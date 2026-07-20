"""Deterministic helpers for structural pieces of WeaveMark compilation."""

from __future__ import annotations

import json
import re
import shlex
import textwrap
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from weavemark.compilation.args import parse_header_args
from weavemark.compilation.fslm_sugar import (
    is_fslm_machine_directive,
    lower_machine_block,
)
from weavemark.compilation.macros import (
    WeaveMarkDefinition,
    preprocess_weavemark,
    resolve_module_body,
)
from weavemark.compilation.prompt_header import (
    PROMPT_LINE_RE,
    parse_prompt_header,
)
from weavemark.compile_options import (
    extension_for_compile_format,
    normalize_compile_format,
    normalize_context_mode,
    supported_compile_formats_text,
)
from weavemark.fragments import is_explicit_file_reference, resolve_fragment_reference
from weavemark.settings import WeaveMarkSettings, builtin_weavemark_settings
from weavemark.variable_paths import (
    MISSING as _MISSING_VARIABLE,
)
from weavemark.variable_paths import (
    resolve_variable_path,
    variable_is_defined,
)
from weavemark.version import LANGUAGE_VERSION

ReadFile = Callable[[str, Path], str]


@dataclass
class StructuralHelperResult:
    """Result produced when structural helpers can resolve a promplet."""

    composed_prompt: str
    prompts: dict[str, str]
    prompt_roles: dict[str, str] = field(default_factory=dict)
    prompt_outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    seen_compile: bool = False
    seen_execution: bool = False
    seen_tools: set[str] = field(default_factory=set)
    seen_output_scopes: set[str] = field(default_factory=set)
    seen_package_targets: set[str] = field(default_factory=set)
    analysis: str = (
        "Resolved structural WeaveMark directives with deterministic helpers."
    )
    compile: dict[str, Any] = field(default_factory=dict)
    tools: list[dict[str, Any]] = field(default_factory=list)
    bindings: list[dict[str, str]] = field(default_factory=list)
    execution: dict[str, Any] = field(default_factory=dict)
    emits: dict[str, str] = field(default_factory=dict)
    packages: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    tool_calls_made: int = 0


@dataclass
class _StructuralCompileState:
    """Mutable state collected while compiling structural directives."""

    tools: list[dict[str, Any]] = field(default_factory=list)
    bindings: list[dict[str, str]] = field(default_factory=list)
    compile: dict[str, Any] = field(default_factory=dict)
    execution: dict[str, Any] = field(default_factory=dict)
    semantic_definitions: dict[str, WeaveMarkDefinition] = field(default_factory=dict)
    execution_nodes: list[dict[str, Any]] = field(default_factory=list)
    execution_result_names: set[str] = field(default_factory=set)
    assertions: list[_StructuralAssertion] = field(default_factory=list)
    prompt_map: dict[str, str] | None = None
    generated_prompts: dict[str, str] = field(default_factory=dict)
    prompt_roles: dict[str, str] = field(default_factory=dict)
    prompt_outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    current_output_scope: str = "default"
    fslm_machines: dict[str, dict[str, Any]] = field(default_factory=dict)
    emits: dict[str, str] = field(default_factory=dict)
    packages: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    seen_compile: bool = False
    seen_execution: bool = False
    seen_tools: set[str] = field(default_factory=set)
    seen_output_scopes: set[str] = field(default_factory=set)
    seen_package_targets: set[str] = field(default_factory=set)
    file_reads: int = 0
    settings: WeaveMarkSettings = field(default_factory=builtin_weavemark_settings)


@dataclass(frozen=True)
class _NamedPromptBlock:
    """A parsed ``@prompt`` block."""

    name: str
    role: str | None
    format: str | None
    text: str


@dataclass(frozen=True)
class _EmitBlock:
    """A parsed emitted artifact block produced by ``@emit file:``."""

    file_name: str
    text: str


@dataclass(frozen=True)
class _UnifiedSpec:
    """A prompt spec split into shared context, prompts, and emits."""

    prefix: str
    prompts: list[_NamedPromptBlock]
    suffix: str
    emits: list[_EmitBlock]


@dataclass(frozen=True)
class _StructuralAssertion:
    """A standard-library ``@assert`` call checked deterministically."""

    options: dict[str, str]


_DIRECTIVE_RE = re.compile(r"^@(?P<name>[A-Za-z_][\w.-]*\??)(?P<rest>(?:\s+.*)?)$")
_IDENTIFIER_TOKEN_RE = re.compile(r"^[A-Za-z_][\w.-]*$")
_EXECUTION_RESULT_NAME_RE = re.compile(r"^[A-Za-z_]\w*$")
_EMIT_PROMPT_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*(?:\.[A-Za-z0-9_-]+)*$")
_BRANCH_RE = re.compile(
    r"""^\s*(?P<quote>["'])(?P<value>.*?)(?P=quote)\s*==>\s*(?P<tail>.*)$"""
)
_WILDCARD_BRANCH_RE = re.compile(r"""^\s*_\s*==>\s*(?P<tail>.*)$""")
_NO_BRANCH = object()
_TOOL_PARAM_RE = re.compile(
    r"^\s*-\s*(?P<name>[A-Za-z_][\w-]*)\s*:\s*(?P<type>[A-Za-z_][\w-]*)"
    r"(?P<rest>.*)$"
)
_VARIABLE_RE = re.compile(r"@\{\s*([A-Za-z_][\w.-]*)\s*\}")
_ASSERTION_CHECK_OPTIONS = {"contains", "not_contains", "section", "variable"}
_ASSERTION_OPTIONS = _ASSERTION_CHECK_OPTIONS | {"severity"}
_COMPILE_OPTIONS = {"format", "context", "images"}
_WEAVEMARK_VERSION = LANGUAGE_VERSION
_FUNCTIONAL_SCHEDULERS = {"sequential", "graph", "graph-strict"}
_TOOL_PARAMETER_TYPES = {"string", "integer", "number", "boolean", "array", "object"}
_EMBED_VARIABLE_OPEN_SENTINEL = "__WEAVEMARK_EMBED_VARIABLE_OPEN__"


def _directive_match(line: str) -> re.Match[str] | None:
    """Return a directive match for unindented directive lines."""

    if line.startswith((" ", "\t")):
        return None
    return _DIRECTIVE_RE.match(line)


def _is_top_level_prompt(line: str) -> bool:
    return not line.startswith((" ", "\t")) and PROMPT_LINE_RE.match(line) is not None


def _is_top_level_emit(line: str) -> bool:
    match = _directive_match(line)
    return match is not None and match.group("name") == "emit"


def _spec_has_top_level_execute(spec_text: str) -> bool:
    """Return True when the spec text contains a top-level @execute directive."""

    for line in spec_text.splitlines():
        if line.startswith((" ", "\t")):
            continue
        match = _DIRECTIVE_RE.match(line)
        if match is not None and match.group("name") == "execute":
            return True
    return False


def _dedent_block(lines: list[str]) -> str:
    return textwrap.dedent("\n".join(lines)).strip("\n")


def _join_prompt_parts(*parts: str) -> str:
    return "\n\n".join(part.strip() for part in parts if part.strip()).strip()


def _collect_indented_block(lines: list[str], start: int) -> tuple[str, int]:
    """Collect the indented block following a top-level directive."""

    block: list[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            next_nonblank = next(
                (
                    future
                    for future in range(index + 1, len(lines))
                    if lines[future].strip()
                ),
                None,
            )
            if next_nonblank is None or not lines[next_nonblank].startswith(
                (" ", "\t")
            ):
                break
            block.append(line)
            index += 1
            continue
        if line.startswith((" ", "\t")):
            block.append(line)
            index += 1
            continue
        break
    return _dedent_block(block), index


def _parse_directive_options(rest: str) -> tuple[list[str], dict[str, str]]:
    parsed = parse_header_args(rest, allow_equals=True)
    return parsed.positional, parsed.options


def _parse_directive_options_with_errors(
    rest: str,
) -> tuple[list[str], dict[str, str], list[str]]:
    parsed = parse_header_args(rest, allow_equals=True)
    return parsed.positional, parsed.options, parsed.errors


def _parse_refine_header(rest: str) -> tuple[str | None, dict[str, str]]:
    tokens = _split_directive_tokens(rest)
    if not tokens:
        return None, {}
    option_text = shlex.join(tokens[1:]) if len(tokens) > 1 else ""
    _, options = _parse_directive_options(option_text)
    return tokens[0], options


def _parse_refine_bindings(
    block: str,
    variables: dict[str, Any],
    state: _StructuralCompileState,
) -> tuple[dict[str, Any], bool]:
    """Parse a ``@refine`` binding block of ``with <name>: <value>`` lines.

    Returns ``(bindings, is_binding_block)``. A block is treated as bindings only
    when every non-blank line starts with ``with`` — otherwise it is ordinary
    refine guidance and ``is_binding_block`` is ``False``. Values may be scalars,
    quoted strings, or ``@{parent_var}`` forwards (substituted from *variables*).
    """

    lines = [line for line in block.splitlines() if line.strip()]
    if not lines:
        return {}, False
    if not all(line.strip().split(maxsplit=1)[0] == "with" for line in lines):
        return {}, False

    bindings: dict[str, Any] = {}
    for raw in lines:
        body = raw.strip()[len("with") :].strip()
        match = re.match(r"([A-Za-z_][\w.-]*)\s*[:=]\s*(.*)$", body)
        if not match:
            state.errors.append(
                "@refine binding must be 'with <name>: <value>'; got: "
                f"{raw.strip()}"
            )
            continue
        name = match.group(1)
        value = _substitute_variables(match.group(2).strip(), variables).strip()
        if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
            bindings[name] = value[1:-1]
        else:
            bindings[name] = _parse_scalar(value)
    return bindings, True


def _split_directive_tokens(rest: str) -> list[str]:
    try:
        raw_tokens = shlex.split(rest.strip())
    except ValueError:
        raw_tokens = rest.strip().split()

    tokens: list[str] = []
    index = 0
    while index < len(raw_tokens):
        token = raw_tokens[index]
        if token.startswith("[") and not token.endswith("]"):
            parts = [token]
            index += 1
            while index < len(raw_tokens):
                parts.append(raw_tokens[index])
                if raw_tokens[index].endswith("]"):
                    break
                index += 1
            tokens.append(" ".join(parts))
            index += 1
            continue
        tokens.append(token)
        index += 1
    return tokens


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text not in {"", "0", "false", "no", "off", "none", "null"}


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        return value


def _version_tuple(version: str) -> tuple[int, ...] | None:
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", version):
        return None
    return tuple(int(part) for part in version.split("."))


def _collect_weavemark_pragma(
    spec_text: str,
    state: _StructuralCompileState,
) -> None:
    """Validate and record the optional top-level ``@promplet`` pragma."""

    pragma_lines: list[tuple[int, str]] = []
    first_nonblank: int | None = None
    for line_number, line in enumerate(spec_text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if first_nonblank is None:
            first_nonblank = line_number
        if stripped.startswith("@promplet"):
            pragma_lines.append((line_number, stripped))

    if not pragma_lines:
        return

    if len(pragma_lines) > 1:
        state.errors.append(
            "A WeaveMark file may declare only one @promplet directive."
        )

    line_number, pragma = pragma_lines[0]
    if first_nonblank != line_number:
        state.errors.append("@promplet must be the first non-blank line in the spec.")

    positional, options = _parse_directive_options(
        pragma.removeprefix("@promplet").strip()
    )
    version = options.get("version")
    allowed_keys = {"version", "surface"}
    if positional or not (set(options) <= allowed_keys) or version is None:
        state.errors.append(
            "@promplet requires version: <major.minor> and optional surface: <name>."
        )
        return

    surface = options.get("surface")
    if surface is not None:
        _SUPPORTED_PRAGMA_SURFACES = {"canonical", "markdown"}
        if surface.lower() not in _SUPPORTED_PRAGMA_SURFACES:
            state.errors.append(
                f"@promplet surface '{surface}' is not supported. "
                f"Supported surfaces: {sorted(_SUPPORTED_PRAGMA_SURFACES)}."
            )

    parsed_version = _version_tuple(version)
    supported_version = _version_tuple(_WEAVEMARK_VERSION)
    if parsed_version is None:
        state.errors.append(f"@promplet version is invalid: {version}")
        return

    state.compile["weavemark_version"] = version
    if surface is not None:
        state.compile["weavemark_surface"] = surface.lower()
    if supported_version is not None and parsed_version > supported_version:
        state.warnings.append(
            f"Declared WeaveMark version {version} is newer than supported "
            f"{_WEAVEMARK_VERSION}; behaviour may differ."
        )


def _resolve_variable_path(variables: dict[str, Any], name: str) -> Any:
    """Resolve a possibly-dotted variable *name* (see ``variable_paths``)."""

    return resolve_variable_path(variables, name)


def _variable_is_defined(variables: dict[str, Any], name: str) -> bool:
    """Whether *name* (flat key or dotted path) resolves to a non-None value."""

    return variable_is_defined(variables, name)


def _substitute_variables(
    text: str,
    variables: dict[str, Any],
    protected_names: set[str] | None = None,
) -> str:
    def replace_variable(match: re.Match[str]) -> str:
        name = match.group(1)
        if protected_names is not None and name in protected_names:
            return match.group(0)
        value = resolve_variable_path(variables, name)
        if value is _MISSING_VARIABLE:
            return match.group(0)
        return _format_variable_value(value)

    return _VARIABLE_RE.sub(replace_variable, text)


def _format_variable_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        if all(not isinstance(item, (dict, list, tuple)) for item in value):
            return "\n".join(f"- {item}" for item in value)
        return json.dumps(value, ensure_ascii=False, indent=2)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _parse_match_block(block: str, variable_value: Any) -> str | None:
    """Parse a `@match` body and return the winning branch's effect.

    Supports both quoted-value branches (`"foo" ==> ...`) and the wildcard
    default branch (`_ ==> ...`). The wildcard, if present, MUST be the
    last branch — it wins only when no earlier named branch matches.

    Branch detection is indentation-aware: only branch headers at this match's
    base indentation open a new branch. Branch headers indented more deeply
    belong to a *nested* ``@match`` and are kept verbatim as the current
    branch's content, so ``@match`` blocks may be nested inside one another.

    Returns the deduped/dedented effect text of the winning branch, or
    ``None`` if no branch matched and no wildcard was provided.
    """
    branches: list[tuple[str | None, str]] = []
    current_value: str | None | object = _NO_BRANCH
    current_lines: list[str] = []
    base_indent: int | None = None

    def flush() -> None:
        nonlocal current_value, current_lines
        if current_value is not _NO_BRANCH:
            assert current_value is None or isinstance(current_value, str)
            branches.append((current_value, _dedent_block(current_lines).strip()))
        current_value = _NO_BRANCH
        current_lines = []

    for line in block.splitlines():
        named_match = _BRANCH_RE.match(line)
        wildcard_match = _WILDCARD_BRANCH_RE.match(line)
        if named_match or wildcard_match:
            indent = len(line) - len(line.lstrip())
            if base_indent is None:
                base_indent = indent
            if indent == base_indent:
                flush()
                if named_match:
                    current_value = named_match.group("value")
                    tail = named_match.group("tail")
                else:
                    assert wildcard_match is not None
                    current_value = None  # sentinel for wildcard
                    tail = wildcard_match.group("tail")
                if tail:
                    current_lines.append(tail)
                continue
        current_lines.append(line)
    flush()

    expected = str(variable_value)
    wildcard_content: str | None = None
    for value, content in branches:
        if value is None:
            wildcard_content = content
        elif value == expected:
            return content
    return wildcard_content


def _parse_tool_directive(
    name: str,
    block: str,
    state: _StructuralCompileState,
) -> dict[str, Any]:
    description_lines: list[str] = []
    properties: dict[str, dict[str, Any]] = {}
    required: list[str] = []

    for line in block.splitlines():
        if not line.strip():
            continue
        param_match = _TOOL_PARAM_RE.match(line)
        if param_match:
            param_name = param_match.group("name")
            param_type = param_match.group("type").lower()
            rest = param_match.group("rest").rstrip()
            if param_type not in _TOOL_PARAMETER_TYPES:
                state.errors.append(
                    f"Unsupported type {param_type!r} for parameter {param_name!r} "
                    f"in @tool {name}."
                )
                continue
            modifiers, separator, description = rest.partition(" - ")
            if not separator:
                state.errors.append(
                    f"Malformed parameter {param_name!r} in @tool {name}: use the "
                    "ASCII ' - ' separator before its description."
                )
                continue
            if param_name in properties:
                state.errors.append(
                    f"Duplicate parameter {param_name!r} in @tool {name}."
                )
                continue
            parsed_modifiers = _parse_tool_parameter_modifiers(
                modifiers,
                parameter_name=param_name,
                parameter_type=param_type,
                tool_name=name,
                state=state,
            )
            if parsed_modifiers is None:
                continue
            is_required = parsed_modifiers.pop("required", False)
            properties[param_name] = {
                "type": param_type,
                "description": description.strip(),
                **parsed_modifiers,
            }
            if is_required:
                required.append(param_name)
        elif line.lstrip().startswith("-"):
            state.errors.append(
                f"Malformed parameter declaration in @tool {name}: {line.strip()}"
            )
        else:
            description_lines.append(line.strip())

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": " ".join(description_lines).strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def _parse_tool_parameter_modifiers(
    text: str,
    *,
    parameter_name: str,
    parameter_type: str,
    tool_name: str,
    state: _StructuralCompileState,
) -> dict[str, Any] | None:
    modifiers: dict[str, Any] = {}
    position = 0

    def reject(message: str) -> None:
        state.errors.append(
            f"Malformed modifiers for parameter {parameter_name!r} in "
            f"@tool {tool_name}: {message}"
        )

    while position < len(text):
        while position < len(text) and text[position].isspace():
            position += 1
        if position >= len(text):
            break

        if text[position] == "(":
            close = text.find(")", position + 1)
            if close < 0:
                reject("unterminated parenthesized modifier.")
                return None
            marker = text[position + 1 : close].strip().lower()
            if marker == "optional":
                state.errors.append(
                    f"Unsupported (optional) modifier for parameter "
                    f"{parameter_name!r} in @tool {tool_name}; parameters are "
                    "optional unless marked (required)."
                )
                return None
            if marker != "required":
                reject(f"unsupported modifier ({marker}).")
                return None
            if "required" in modifiers:
                reject("duplicate modifier 'required'.")
                return None
            modifiers["required"] = True
            position = close + 1
            continue

        key_match = re.match(r"([A-Za-z_][\w-]*)\s*:", text[position:])
        if key_match is None:
            reject(f"unexpected text {text[position:]!r}.")
            return None
        key = key_match.group(1).lower()
        if key not in {"enum", "default"}:
            reject(f"unsupported modifier {key!r}.")
            return None
        if key in modifiers:
            reject(f"duplicate modifier {key!r}.")
            return None

        position += key_match.end()
        while position < len(text) and text[position].isspace():
            position += 1
        raw_value, position = _consume_tool_modifier_value(text, position)
        if raw_value is None:
            reject(f"{key}: requires a value.")
            return None
        try:
            modifiers[key] = _parse_tool_modifier_value(
                raw_value,
                parameter_type=parameter_type,
                require_list=key == "enum",
            )
        except ValueError as exc:
            reject(f"{key}: {exc}")
            return None

    return modifiers


def _consume_tool_modifier_value(
    text: str,
    position: int,
) -> tuple[str | None, int]:
    if position >= len(text):
        return None, position
    opener = text[position]
    if opener == "[":
        close = text.find("]", position + 1)
        if close < 0:
            return text[position:], len(text)
        return text[position : close + 1], close + 1
    if opener in {'"', "'"}:
        escaped = False
        for index in range(position + 1, len(text)):
            char = text[index]
            if char == opener and not escaped:
                return text[position : index + 1], index + 1
            escaped = char == "\\" and not escaped
            if char != "\\":
                escaped = False
        return text[position:], len(text)
    end = position
    while end < len(text) and not text[end].isspace():
        end += 1
    return text[position:end], end


def _parse_tool_modifier_value(
    raw_value: str,
    *,
    parameter_type: str,
    require_list: bool,
) -> Any:
    try:
        value = yaml.safe_load(raw_value)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid value {raw_value!r}.") from exc

    if require_list:
        if not raw_value.startswith("[") or not raw_value.endswith("]"):
            raise ValueError("must be a bracketed list.")
        if not isinstance(value, list) or not value:
            raise ValueError("must be a non-empty bracketed list.")
        for item in value:
            _validate_tool_modifier_type(item, parameter_type)
        return value

    if parameter_type == "string":
        if raw_value.startswith(('"', "'")):
            if not isinstance(value, str):
                raise ValueError("must be a string.")
            return value
        return raw_value

    _validate_tool_modifier_type(value, parameter_type)
    return value


def _validate_tool_modifier_type(value: Any, parameter_type: str) -> None:
    valid = {
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }[parameter_type]
    if not valid:
        raise ValueError(f"value {value!r} does not match type {parameter_type!r}.")


def _parse_tool_header(
    rest: str,
    state: _StructuralCompileState,
) -> str | None:
    positional, options, parse_errors = _parse_directive_options_with_errors(rest)
    if parse_errors:
        state.errors.extend(f"@tool: {error}" for error in parse_errors)
        return None
    if options:
        state.errors.append(
            "@tool declares only the LLM-facing schema; use @bind for helper "
            "implementations. Unsupported parameter(s): "
            + ", ".join(sorted(options))
            + "."
        )
        return None
    if len(positional) != 1:
        state.errors.append("@tool requires exactly one tool name.")
        return None
    name = positional[0]
    if not _IDENTIFIER_TOKEN_RE.fullmatch(name):
        state.errors.append(f"@tool name is invalid: {name}")
        return None
    return name


def _parse_bind_directive(
    rest: str,
    variables: dict[str, Any],
    base_dir: Path,
    state: _StructuralCompileState,
) -> dict[str, str] | None:
    positional, options, parse_errors = _parse_directive_options_with_errors(rest)
    if parse_errors:
        state.errors.extend(f"@bind: {error}" for error in parse_errors)
        return None
    if len(positional) != 1:
        state.errors.append("@bind requires exactly one capability name.")
        return None
    capability = positional[0]
    if not _IDENTIFIER_TOKEN_RE.fullmatch(capability):
        state.errors.append(f"@bind capability name is invalid: {capability}")
        return None

    required = {"language", "from", "symbol"}
    missing = sorted(required - set(options))
    unsupported = sorted(set(options) - required)
    if missing or unsupported:
        if missing:
            state.errors.append(
                "@bind missing required parameter(s): " + ", ".join(missing) + "."
            )
        if unsupported:
            state.errors.append(
                "@bind has unsupported parameter(s): " + ", ".join(unsupported) + "."
            )
        return None

    language = _substitute_variables(options["language"], variables).strip()
    source = _substitute_variables(options["from"], variables).strip()
    symbol = _substitute_variables(options["symbol"], variables).strip()

    if not re.fullmatch(r"[A-Za-z_][\w-]*", language):
        state.errors.append(f"@bind language is invalid: {language}")
        return None
    if not _IDENTIFIER_TOKEN_RE.fullmatch(symbol):
        state.errors.append(f"@bind symbol is invalid: {symbol}")
        return None
    if _VARIABLE_RE.search(source):
        state.errors.append(f"@bind source has unresolved variable(s): {source}")
        return None
    source_path = Path(source)
    if source_path.is_absolute() or ".." in source_path.parts:
        state.errors.append(f"@bind source must stay inside the project: {source}")
        return None
    if source in {"", "."} or source.endswith(("/", "\\")):
        state.errors.append(f"@bind source must name a helper file: {source}")
        return None
    resolved = (base_dir / source_path).resolve()
    try:
        resolved.relative_to(base_dir.resolve())
    except ValueError:
        state.errors.append(f"@bind source escapes the spec directory: {source}")
        return None

    binding = {
        "name": capability,
        "language": language,
        "from": source,
        "symbol": symbol,
    }
    if any(existing["name"] == capability for existing in state.bindings):
        state.errors.append(f"Duplicate @bind for capability: {capability}")
        return None
    return binding


def _parse_uses(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    text = str(value).strip()
    if not text:
        return []
    parsed = _parse_scalar(text)
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return [item.strip() for item in text.replace(",", " ").split() if item.strip()]


def _collect_execution_node(
    definition: WeaveMarkDefinition,
    directive: str,
    rest: str,
    body: str,
    state: _StructuralCompileState,
) -> None:
    positional, options = _parse_directive_options(rest)
    result_name = options.pop("as", None)
    uses = _parse_uses(options.pop("uses", "")) if "uses" in options else []

    node_id = f"{directive}_{len(state.execution_nodes) + 1}"
    if result_name is not None:
        if not _EXECUTION_RESULT_NAME_RE.fullmatch(result_name):
            state.errors.append(f"Execution result name is invalid: {result_name}")
            return
        if result_name in state.execution_result_names:
            state.errors.append(f"Duplicate execution result name: {result_name}")
            return
        node_id = result_name
    invalid_uses = [
        name for name in uses if not _EXECUTION_RESULT_NAME_RE.fullmatch(name)
    ]
    if invalid_uses:
        state.errors.append(
            "Execution uses: has invalid result name(s): "
            + ", ".join(invalid_uses)
            + "."
        )
        return

    state.execution_nodes.append(
        {
            "id": node_id,
            "directive": directive,
            "definition": definition.name,
            "phase": definition.phase,
            "scope": definition.scope,
            "returns": definition.returns,
            "effects": [
                {"name": effect.name, "mode": effect.mode}
                for effect in definition.effects
            ],
            "args": {
                "positional": positional,
                "options": options,
            },
            "params": [
                {
                    "name": param.name,
                    "implicit": param.implicit,
                    "mode": param.mode,
                    **({"default": param.default} if param.default is not None else {}),
                }
                for param in definition.params
            ],
            "body": body,
            **({"as": result_name} if result_name else {}),
            **({"uses": uses} if uses else {}),
        }
    )
    if result_name is not None:
        state.execution_result_names.add(result_name)


def _functional_node_id(node: dict[str, Any]) -> str:
    return str(node.get("id") or node.get("as") or node["directive"])


def _functional_result_references(
    node: dict[str, Any],
    produced_results: set[str],
) -> set[str]:
    references: set[str] = set()
    args = node.get("args", {})
    values = [
        args.get("positional", []) if isinstance(args, dict) else [],
        args.get("options", {}) if isinstance(args, dict) else {},
        node.get("body", ""),
    ]

    def collect(value: Any) -> None:
        if isinstance(value, str):
            references.update(
                match.group(1).split(".", 1)[0]
                for match in _VARIABLE_RE.finditer(value)
                if match.group(1).split(".", 1)[0] in produced_results
            )
        elif isinstance(value, dict):
            for nested in value.values():
                collect(nested)
        elif isinstance(value, (list, tuple)):
            for nested in value:
                collect(nested)

    for value in values:
        collect(value)
    return references


def _validate_graph_strict_uses(
    nodes: list[dict[str, Any]],
    state: _StructuralCompileState,
) -> None:
    produced_results = {str(node["as"]) for node in nodes if node.get("as")}
    for node in nodes:
        referenced = _functional_result_references(node, produced_results)
        declared = {str(name) for name in node.get("uses", [])}
        missing = sorted(referenced - declared)
        if missing:
            state.errors.append(
                f"@execute functional graph-strict node {_functional_node_id(node)} "
                "references result(s) without explicit uses: "
                + ", ".join(missing)
                + "."
            )


def _topological_functional_levels(
    nodes: list[dict[str, Any]],
    state: _StructuralCompileState,
) -> list[list[str]] | None:
    produced: dict[str, str] = {
        str(node["as"]): _functional_node_id(node) for node in nodes if node.get("as")
    }
    node_ids = [_functional_node_id(node) for node in nodes]
    dependencies: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
    dependents: dict[str, set[str]] = {node_id: set() for node_id in node_ids}

    for node in nodes:
        node_id = _functional_node_id(node)
        for dependency_name in node.get("uses", []):
            dependency_id = produced.get(str(dependency_name))
            if dependency_id is None:
                state.errors.append(
                    f"@execute functional node {node_id} uses unknown result: "
                    f"{dependency_name}"
                )
                continue
            dependencies[node_id].add(dependency_id)
            dependents[dependency_id].add(node_id)

    if state.errors:
        return None

    levels: list[list[str]] = []
    processed: set[str] = set()
    ready = [node_id for node_id in node_ids if not dependencies[node_id]]
    while ready:
        ready_set = set(ready)
        level = [node_id for node_id in node_ids if node_id in ready_set]
        levels.append(level)
        ready = []
        for node_id in level:
            processed.add(node_id)
            for dependent in sorted(dependents[node_id]):
                dependencies[dependent].discard(node_id)
                if not dependencies[dependent] and dependent not in processed:
                    ready.append(dependent)

    if len(processed) != len(node_ids):
        cyclic = [node_id for node_id in node_ids if node_id not in processed]
        state.errors.append(
            "@execute functional dependency cycle detected: "
            + " -> ".join(cyclic)
            + "."
        )
        return None

    return levels


def _validate_functional_execution_plan(state: _StructuralCompileState) -> None:
    nodes = state.execution_nodes
    scheduler = state.execution.get("scheduler", "sequential")
    allowed_effects = state.execution.get("allow_effects")
    if allowed_effects is not None:
        allowed = {str(effect) for effect in _parse_uses(allowed_effects)}
        for node in nodes:
            requested = {
                str(effect["name"])
                for effect in node.get("effects", [])
                if isinstance(effect, dict) and effect.get("name")
            }
            disallowed = sorted(requested - allowed)
            if disallowed:
                state.errors.append(
                    f"@execute functional node {_functional_node_id(node)} requests "
                    "effect(s) not listed in allow_effects: "
                    + ", ".join(disallowed)
                    + "."
                )

    if scheduler == "graph-strict":
        _validate_graph_strict_uses(nodes, state)

    levels = _topological_functional_levels(nodes, state)
    if levels is None:
        return
    if scheduler == "sequential":
        levels = [[_functional_node_id(node)] for node in nodes]
    state.execution["plan"] = {
        "scheduler": scheduler,
        "order": [node_id for level in levels for node_id in level],
        "levels": levels,
    }


def _attach_fslm_machine_spec(state: _StructuralCompileState) -> None:
    if not state.fslm_machines:
        return
    if state.execution.get("type") != "fslm":
        state.warnings.append(
            "Inline FSLM @machine declaration ignored because @execute fslm "
            "is not active."
        )
        return
    selected = state.execution.get("machine")
    if isinstance(selected, str) and selected in state.fslm_machines:
        state.execution["machine_spec"] = state.fslm_machines[selected]
        return
    if selected is None and len(state.fslm_machines) == 1:
        selected_name, machine_spec = next(iter(state.fslm_machines.items()))
        state.execution["machine"] = selected_name
        state.execution["machine_spec"] = machine_spec
        return
    available = ", ".join(sorted(state.fslm_machines))
    if isinstance(selected, str):
        state.errors.append(
            f"@execute fslm selects machine {selected!r}, but no inline "
            f"@machine with that name exists. Available inline machines: {available}."
        )
    else:
        state.errors.append(
            "@execute fslm must declare machine: <name> when multiple inline "
            f"machines are present. Available inline machines: {available}."
        )


def _parse_execute_directive(
    rest: str,
    block: str,
    state: _StructuralCompileState,
    base_dir: Path,
    variables: dict[str, Any],
) -> dict[str, Any]:
    positional, options = _parse_directive_options(rest)
    execution: dict[str, Any] = {}
    if positional:
        execution["type"] = positional[0]
    for key, value in options.items():
        execution[key] = _parse_scalar(_substitute_variables(value, variables))
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        execution[key.strip()] = _parse_scalar(
            _substitute_variables(value, variables)
        )
    if execution.get("type") == "functional":
        scheduler = execution.get("scheduler", "sequential")
        if scheduler not in _FUNCTIONAL_SCHEDULERS:
            state.errors.append(
                "@execute functional scheduler must be sequential, graph, or "
                f"graph-strict; got {scheduler}."
            )
        execution["scheduler"] = scheduler
        if "bindings" not in execution and state.bindings:
            execution["bindings"] = list(state.bindings)
    if execution.get("type") == "fslm" and "base_dir" not in execution:
        execution["base_dir"] = str(base_dir.resolve())
    return execution


def _parse_output_directive(
    rest: str,
    block: str,
    state: _StructuralCompileState,
    variables: dict[str, Any],
) -> dict[str, Any]:
    """Parse an ``@output`` directive into an output contract dict.

    Shape: ``{"type": "text"|"image", **params}``. A positional string is
    treated as a text ``format`` (preserving the old ``@output_format "x"``
    form). For ``type: text`` the indented body is a free-text format
    description; for ``type: image`` the indented body is ``key: value`` params.

    Parameter values are variable-substituted (``@{var}``) at compile time, so
    an image contract may read ``size: @{image_size}`` from companion vars — the
    same convention ``@execute`` config already follows. The free-text ``text``
    body is left untouched.
    """

    positional, options = _parse_directive_options(rest)
    contract: dict[str, Any] = {}

    raw_type = str(options.pop("type", "text")).strip().lower()
    if raw_type not in {"text", "image"}:
        state.errors.append(
            f"@output type must be text or image; got: {raw_type}."
        )
        raw_type = "text"
    contract["type"] = raw_type

    for key, value in options.items():
        contract[key] = _parse_scalar(_substitute_variables(value, variables))

    if raw_type == "image":
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            contract[key.strip()] = _parse_scalar(
                _substitute_variables(value, variables)
            )
        if positional:
            state.errors.append(
                "@output type: image does not accept a positional format string."
            )
        return contract

    if positional and "format" not in contract:
        contract["format"] = positional[0]
    body = textwrap.dedent(block).strip() if block else ""
    if body:
        contract["body"] = body
    return contract


def _output_text_obligation(contract: dict[str, Any]) -> str | None:
    """Render the prompt-text obligation for a ``type: text`` output contract.

    Returns ``None`` when there is nothing to inject (image contracts, or text
    contracts with no format/body/enforcement requirement).
    """

    if contract.get("type") != "text":
        return None
    fmt = str(contract.get("format", "")).strip()
    body = str(contract.get("body", "")).strip()
    enforce = str(contract.get("enforce", "")).strip()
    if not fmt and not body and not enforce:
        return None
    parts = ["## Output format"]
    if fmt:
        parts.append(fmt)
    if body:
        parts.append(body)
    if enforce:
        parts.append(f"Enforcement level: {enforce}.")
    return "\n\n".join(parts)


def _parse_compile_directive(
    rest: str,
    variables: dict[str, Any],
    state: _StructuralCompileState,
) -> None:
    positional, options = _parse_directive_options(rest)
    unsupported = sorted(key for key in options if key not in _COMPILE_OPTIONS)
    if unsupported:
        state.errors.append(
            "@compile only supports the format and context "
            "parameters. Unsupported parameter(s): " + ", ".join(unsupported) + "."
        )
        return
    if positional:
        state.errors.append(
            "@compile requires key-value parameters such as format: markdown; "
            "positional arguments are not supported."
        )
        return
    if not options:
        state.errors.append(
            "@compile requires at least one parameter such as format: markdown or "
            "context: cascade."
        )
        return

    raw_format = options.get("format")
    if raw_format is not None:
        format_name = _substitute_variables(raw_format, variables).strip()
        if _VARIABLE_RE.search(format_name):
            state.errors.append(
                f"@compile format has unresolved variable(s): {format_name}"
            )
        else:
            normalized = normalize_compile_format(format_name, state.settings)
            if normalized is None:
                state.errors.append(
                    f"Unsupported @compile format: {format_name}. Supported formats: "
                    f"{supported_compile_formats_text(state.settings)}."
                )
            else:
                previous = state.compile.get("format")
                if previous and previous != normalized:
                    state.warnings.append(
                        f"Duplicate @compile format overrides earlier value: {previous} -> {normalized}."
                    )
                state.compile["format"] = normalized

    raw_context = options.get("context")
    if raw_context is not None:
        context_text = _substitute_variables(raw_context, variables).strip()
        if _VARIABLE_RE.search(context_text):
            state.errors.append(
                f"@compile context has unresolved variable(s): {context_text}"
            )
        else:
            context_mode = normalize_context_mode(context_text)
            if context_mode is None:
                state.errors.append(
                    "@compile context must be auto, cascade, or local; "
                    f"got: {context_text}"
                )
            else:
                previous_context = state.compile.get("context")
                if previous_context is not None and previous_context != context_mode:
                    state.warnings.append(
                        "Duplicate @compile context overrides earlier value: "
                        f"{previous_context} -> {context_mode}."
                    )
                state.compile["context"] = context_mode

    raw_images = options.get("images")
    if raw_images is not None:
        images_text = _substitute_variables(raw_images, variables).strip().lower()
        if images_text in {"on", "true", "yes"}:
            state.compile["images"] = True
        elif images_text in {"off", "false", "no"}:
            state.compile["images"] = False
        else:
            state.errors.append(
                "@compile images must be on or off; " f"got: {images_text}"
            )


def _parse_structural_assertion(rest: str, block: str) -> _StructuralAssertion | str:
    positional, options, parse_errors = _parse_directive_options_with_errors(rest)
    if parse_errors:
        return "@assert: " + " ".join(parse_errors)
    if positional:
        return (
            "@assert does not accept positional or free-text assertions; "
            "use contains:, not_contains:, section:, or variable:."
        )
    if block.strip():
        return (
            "@assert does not accept a body; use contains:, not_contains:, "
            "section:, or variable:."
        )
    unsupported = sorted(set(options) - _ASSERTION_OPTIONS)
    if unsupported:
        return (
            "@assert has unknown structural parameter(s): "
            + ", ".join(unsupported)
            + "."
        )
    severity = options.get("severity")
    if severity is not None and severity.lower() not in {"error", "warning"}:
        return "@assert severity must be error or warning."
    if not any(options.get(option, "").strip() for option in _ASSERTION_CHECK_OPTIONS):
        return (
            "@assert requires at least one nonempty canonical check: "
            "contains:, not_contains:, section:, or variable:."
        )
    return _StructuralAssertion(options=options)


def _assertion_checks(
    assertion: _StructuralAssertion,
) -> list[tuple[str, str]] | None:
    checks: list[tuple[str, str]] = []

    for option in _ASSERTION_CHECK_OPTIONS:
        value = assertion.options.get(option)
        if value:
            checks.append((option, value))

    return checks or None


def _has_markdown_section(text: str, section: str) -> bool:
    pattern = re.compile(rf"(?im)^#{{1,6}}\s+{re.escape(section.strip())}\s*$")
    return pattern.search(text) is not None


def _assertion_check_passed(
    check: tuple[str, str],
    composed_prompt: str,
    variables: dict[str, Any],
) -> bool:
    kind, value = check
    if kind == "contains":
        return value in composed_prompt
    if kind == "not_contains":
        return value not in composed_prompt
    if kind == "section":
        return _has_markdown_section(composed_prompt, value)
    if kind == "variable":
        return _variable_is_defined(variables, value)
    return False


def _format_embed_block(content: str, *, lang: str = "", label: str = "") -> str:
    content = content.replace("@{", _EMBED_VARIABLE_OPEN_SENTINEL)
    fence = f"```{lang}".rstrip()
    block = f"{fence}\n{content.rstrip()}\n```"
    if label:
        return f"{label}\n\n{block}"
    return block


def _extract_heading_titles(text: str) -> list[str]:
    return [
        match.group("title").strip()
        for match in re.finditer(
            r"(?m)^\s{0,3}#{1,6}\s+(?P<title>.+?)\s*$",
            text,
        )
    ]


def _describe_assertion(assertion: _StructuralAssertion) -> str:
    parts = [
        f"{key}: {assertion.options[key]}"
        for key in sorted(_ASSERTION_CHECK_OPTIONS)
        if assertion.options.get(key)
    ]
    return ", ".join(parts) or "assertion"


def _evaluate_assertions(
    state: _StructuralCompileState,
    composed_prompt: str,
    variables: dict[str, Any],
) -> None:
    for assertion in state.assertions:
        checks = _assertion_checks(assertion)
        if checks is None:
            state.errors.append(
                f"Unsupported structural @assert semantic check: {_describe_assertion(assertion)}"
            )
            continue
        if all(
            _assertion_check_passed(check, composed_prompt, variables)
            for check in checks
        ):
            continue

        severity = assertion.options.get("severity", "error").lower()
        message = f"@assert failed: {_describe_assertion(assertion)}"
        if severity == "warning":
            state.warnings.append(message)
        else:
            state.errors.append(message)


def _semantic_definition(
    state: _StructuralCompileState,
    directive: str,
    *,
    phase: str,
) -> WeaveMarkDefinition | None:
    definition = state.semantic_definitions.get(directive)
    if definition is None or definition.phase != phase:
        return None
    return definition


def _fslm_machine_semantic_names(state: _StructuralCompileState) -> set[str]:
    return {
        name
        for name, definition in state.semantic_definitions.items()
        if definition.name == "machine"
        and any(effect.name == "fslm_sugar" for effect in definition.effects)
    }


def _semantic_effect_names(definition: WeaveMarkDefinition) -> set[str]:
    return {effect.name for effect in definition.effects}


def _validate_compile_semantic_contract(
    definition: WeaveMarkDefinition,
    required_effects: set[str],
    state: _StructuralCompileState,
) -> bool:
    effect_names = _semantic_effect_names(definition)
    missing = sorted(required_effects - effect_names)
    if missing:
        state.errors.append(
            f"Semantic @{definition.name} definition is missing required effect(s): "
            + ", ".join(missing)
            + "."
        )
        return False
    return True


def _validate_relative_file(
    file_name: str, directive: str, state: _StructuralCompileState
) -> str | None:
    """Validate that *file_name* is a safe relative path under the output dir."""

    if not file_name:
        return None
    if _VARIABLE_RE.search(file_name):
        state.errors.append(
            f"{directive} file path has unresolved variable(s): {file_name}"
        )
        return None
    path = Path(file_name)
    if path.is_absolute() or ".." in path.parts:
        state.errors.append(
            f"{directive} file path must stay relative to the output directory: "
            f"{file_name}"
        )
        return None
    if file_name in {".", ""} or file_name.endswith(("/", "\\")):
        state.errors.append(f"{directive} file path must name a file: {file_name}")
        return None
    return file_name


def _parse_package_directive(
    rest: str,
    block: str,
    variables: dict[str, Any],
    state: _StructuralCompileState,
) -> dict[str, str] | None:
    """Parse a ``@package`` directive into a packaging step.

    Two forms:

    - Apply: ``@package instructions: <promplet> file: <out>`` and/or an indented
      instruction body. Referenced and inline instructions are compiled with the
      execution context and applied in one semantic call.
    - Convert: ``@package from: <src> file: <out>`` — deterministically convert
      an already-produced deliverable (e.g. HTML ``from:`` -> PDF ``file:``).

    ``file:`` is required. Conversion cannot be combined with semantic instructions.
    """

    _positional, options = _parse_directive_options(rest)

    allowed = {"instructions", "file", "from"}
    unsupported = sorted(key for key in options if key not in allowed)
    if unsupported:
        state.errors.append(
            "@package supports instructions:, file:, and from:. Unsupported "
            "parameter(s): " + ", ".join(unsupported) + "."
        )
        return None

    file_name = _validate_relative_file(
        _substitute_variables(options.get("file", ""), variables).strip(),
        "@package",
        state,
    )
    if not file_name:
        state.errors.append("@package requires file: <path>.")
        return None

    instructions = _substitute_variables(
        options.get("instructions", ""), variables
    ).strip()
    source = _substitute_variables(options.get("from", ""), variables).strip()
    body = block.strip()
    has_semantic_source = bool(instructions or body)
    if has_semantic_source == bool(source):
        state.errors.append(
            "@package requires instructions: <promplet>, a non-empty body, or both; "
            "from: <path> is the mutually exclusive conversion form."
        )
        return None

    package: dict[str, str] = {"file": file_name}
    if has_semantic_source:
        if instructions:
            package["instructions"] = instructions
        if body:
            package["body"] = body
    else:
        validated_source = _validate_relative_file(
            source,
            "@package from:",
            state,
        )
        if not validated_source:
            return None
        package["from"] = validated_source
    return package


def _parse_emit_file(
    rest: str,
    variables: dict[str, Any],
    state: _StructuralCompileState,
) -> str | None:
    positional, options = _parse_directive_options(rest)
    unsupported = sorted(key for key in options if key != "file")
    if unsupported:
        state.errors.append(
            "@emit only supports the file parameter. Unsupported parameter(s): "
            + ", ".join(unsupported)
            + "."
        )
        return None
    if positional:
        state.errors.append(
            "@emit requires file: <path>; positional arguments are not supported."
        )
        return None

    file_name = _substitute_variables(options.get("file", ""), variables).strip()
    if not file_name:
        state.errors.append("@emit requires file: <path>.")
        return None
    if _VARIABLE_RE.search(file_name):
        state.errors.append(f"@emit file path has unresolved variable(s): {file_name}")
        return None
    path = Path(file_name)
    if path.is_absolute() or ".." in path.parts:
        state.errors.append(
            f"@emit file path must stay relative to the output directory: {file_name}"
        )
        return None
    if file_name in {".", ""} or file_name.endswith(("/", "\\")):
        state.errors.append(f"@emit file path must name a file: {file_name}")
        return None
    return file_name


def _split_unified_spec(
    spec_text: str,
    variables: dict[str, Any],
    state: _StructuralCompileState,
) -> _UnifiedSpec | None:
    """Split a spec into prefix + named ``@prompt`` blocks + ``@emit`` blocks + suffix.

    Returns ``None`` when the spec has neither top-level ``@prompt`` nor
    ``@emit`` directives, signaling that the caller should fall back to plain
    line-by-line directive processing.

    Body parsing supports two styles, decided per block by inspecting the
    first non-blank line after the directive header:

    - **Indented body**: lines are collected until the first non-indented
      non-blank content. That non-indented content becomes the spec's
      *suffix* and terminates block collection (matching the historical
      ``@prompt`` behavior with a shared cascading suffix).
    - **Non-indented body**: lines are collected until the next top-level
      ``@prompt`` / ``@emit`` / ``@compile`` directive (matching the
      historical ``@message`` behavior).

    Both styles compose cleanly in the same spec.
    """

    lines = spec_text.splitlines()
    first_boundary = next(
        (
            i
            for i, line in enumerate(lines)
            if _is_top_level_prompt(line) or _is_top_level_emit(line)
        ),
        None,
    )
    if first_boundary is None:
        return None

    prefix_lines = lines[:first_boundary]
    prompt_blocks: list[_NamedPromptBlock] = []
    emit_blocks: list[_EmitBlock] = []
    suffix_lines: list[str] = []
    index = first_boundary
    in_suffix = False

    while index < len(lines):
        if in_suffix:
            suffix_lines.append(lines[index])
            index += 1
            continue

        line = lines[index]
        match = _directive_match(line)
        if match is not None and match.group("name") == "compile":
            # @compile between/around blocks belongs to the spec proper —
            # leave for the directive-processing pass via the suffix.
            suffix_lines.append(line)
            in_suffix = True
            index += 1
            continue

        if _is_top_level_prompt(line):
            parsed = parse_prompt_header(line)
            assert parsed is not None  # narrowed by _is_top_level_prompt
            for err in parsed.errors:
                state.errors.append(err)
            body, index, hit_suffix = _consume_block_body(lines, index + 1)
            prompt_blocks.append(
                _NamedPromptBlock(
                    name=parsed.name,
                    role=parsed.role,
                    format=parsed.format,
                    text=body,
                )
            )
            if hit_suffix:
                in_suffix = True
            continue

        if _is_top_level_emit(line):
            match = _directive_match(line)
            assert match is not None
            rest = match.group("rest").strip()
            file_name = _parse_emit_file(rest, variables, state)
            body, index, hit_suffix = _consume_block_body(lines, index + 1)
            if file_name:
                emit_blocks.append(_EmitBlock(file_name=file_name, text=body))
            if hit_suffix:
                in_suffix = True
            continue

        # Blank line between blocks (or other top-level content slipping
        # through). Skip when blank; otherwise treat as suffix.
        if not line.strip():
            index += 1
            continue
        # Non-blank, non-block top-level line outside any block — this is
        # suffix territory.
        suffix_lines.append(line)
        in_suffix = True
        index += 1

    return _UnifiedSpec(
        prefix=_dedent_block(prefix_lines).strip(),
        prompts=prompt_blocks,
        suffix=_dedent_block(suffix_lines).strip(),
        emits=emit_blocks,
    )


def _consume_block_body(lines: list[str], start: int) -> tuple[str, int, bool]:
    """Consume the body of a ``@prompt`` / ``@emit`` block.

    Returns ``(body_text, new_index, hit_suffix)``.

    ``hit_suffix`` is ``True`` when the body terminated because we hit a
    non-indented, non-directive line — meaning the rest of the spec is a
    cascading suffix in @prompt-style specs. Callers should accumulate
    everything from ``new_index`` onward into the spec's suffix.
    """

    block_lines: list[str] = []
    index = start

    # Skip leading blank lines.
    while index < len(lines) and not lines[index].strip():
        block_lines.append(lines[index])
        index += 1

    if index >= len(lines):
        return _dedent_block(block_lines).strip(), index, False

    first_content_line = lines[index]
    if _is_top_level_prompt(first_content_line) or _is_top_level_emit(
        first_content_line
    ):
        return _dedent_block(block_lines).strip(), index, False

    indented_mode = first_content_line.startswith((" ", "\t"))

    while index < len(lines):
        line = lines[index]
        if _is_top_level_prompt(line) or _is_top_level_emit(line):
            break
        if indented_mode and line.strip() and not line.startswith((" ", "\t")):
            # Non-indented content after an indented-mode body marks the
            # start of the cascading suffix.
            return _dedent_block(block_lines).strip(), index, True
        block_lines.append(line)
        index += 1

    return _dedent_block(block_lines).strip(), index, False


def _compile_structural_text(
    spec_text: str,
    variables: dict[str, Any],
    base_dir: Path,
    state: _StructuralCompileState,
    read_file: ReadFile,
    stack: tuple[Path, ...] = (),
) -> str | None:
    """Resolve directives covered by deterministic structural helpers."""

    unified_spec = _split_unified_spec(spec_text, variables, state)
    if unified_spec is not None:
        return _compile_unified_spec(
            spec_text,
            unified_spec,
            variables,
            base_dir,
            state,
            read_file,
            stack,
        )

    lines = spec_text.splitlines()
    output_lines: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        match = _directive_match(line)
        if match is None:
            output_lines.append(line)
            index += 1
            continue

        directive = match.group("name")
        rest = match.group("rest").strip()

        if directive == "note":
            _, index = _collect_indented_block(lines, index + 1)
            continue

        if directive == "promplet":
            # Version pragma — emits compile-time metadata in the
            # controller, but contributes no prompt text.
            index += 1
            continue

        if directive == "directives?":
            found = sorted(
                {
                    m.group("name")
                    for source_line in lines
                    if (m := _directive_match(source_line)) is not None
                    and m.group("name") != "directives?"
                }
            )
            state.suggestions.append(
                "Directives used: "
                + (", ".join(f"@{name}" for name in found) or "none")
            )
            index += 1
            continue

        if directive == "vars?":
            referenced = sorted(
                set(_VARIABLE_RE.findall("\n".join(output_lines + lines[index + 1 :])))
            )
            missing = [
                name for name in referenced if not _variable_is_defined(variables, name)
            ]
            detail = "Variables referenced: " + (", ".join(referenced) or "none")
            if missing:
                detail += ". Missing variables: " + ", ".join(missing)
            state.suggestions.append(detail)
            index += 1
            continue

        if directive == "structure?":
            headings = _extract_heading_titles("\n".join(output_lines))
            state.suggestions.append(
                "Prompt structure headings: "
                + (", ".join(headings) if headings else "no Markdown headings detected")
            )
            index += 1
            continue

        if directive == "compile":
            if state.seen_compile:
                state.errors.append("Duplicate @compile directive.")
                index += 1
                continue
            state.seen_compile = True
            _parse_compile_directive(rest, variables, state)
            index += 1
            continue

        if directive == "embed":
            positional, options = _parse_directive_options(rest)
            lang = options.get("lang", "")
            label = options.get("label", "")
            optional = str(options.get("optional", "")).casefold() in {
                "1",
                "on",
                "true",
                "yes",
            }
            file_name = options.get("file")
            folder_name = options.get("folder")
            if file_name and folder_name:
                state.errors.append("@embed accepts either file: or folder:, not both.")
                index += 1
                continue
            if folder_name:
                folder_name = _substitute_variables(folder_name, variables).strip()
                if not folder_name and optional:
                    index += 1
                    continue
                if _VARIABLE_RE.search(folder_name):
                    state.errors.append(
                        f"@embed folder path has unresolved variable(s): {folder_name}"
                    )
                    index += 1
                    continue
                content = read_file(f"directory:{folder_name}", base_dir)
                state.file_reads += 1
                if content.startswith("Error:"):
                    state.errors.append(content)
                    index += 1
                    continue
                output_lines.append(
                    _format_embed_block(
                        content,
                        lang=lang or "markdown",
                        label=label or "Previous reports",
                    )
                )
                index += 1
                continue
            if file_name:
                file_name = _substitute_variables(file_name, variables).strip()
                if _VARIABLE_RE.search(file_name):
                    state.errors.append(
                        f"@embed file path has unresolved variable(s): {file_name}"
                    )
                    index += 1
                    continue
                content = read_file(file_name, base_dir)
                state.file_reads += 1
                if content.startswith("Error:"):
                    state.errors.append(content)
                    index += 1
                    continue
                output_lines.append(
                    _format_embed_block(content, lang=lang, label=label)
                )
                index += 1
                continue

            block, index = _collect_indented_block(lines, index + 1)
            if positional and not lang and positional[0] not in {"file"}:
                lang = positional[0]
            output_lines.append(_format_embed_block(block, lang=lang, label=label))
            continue

        compile_semantic = _semantic_definition(state, directive, phase="compile")
        execute_semantic = _semantic_definition(state, directive, phase="execute")

        if compile_semantic is not None and compile_semantic.name == "refine":
            if not _validate_compile_semantic_contract(
                compile_semantic,
                {"read_file", "compose_spec", "transform_text", "diagnostics"},
                state,
            ):
                index += 1
                continue
            file_name, options = _parse_refine_header(rest)
            if file_name is None:
                state.errors.append("@refine requires a promplet reference.")
                index += 1
                continue
            refine_block, next_index = _collect_indented_block(lines, index + 1)
            bindings, is_bound = _parse_refine_bindings(
                refine_block, variables, state
            )
            if not is_bound:
                # No bindings: preserve existing behavior. mingle:true refinement
                # is semantic (LLM); only mingle:false composes structurally.
                if options.get("mingle", "true").lower() != "false":
                    return None
                if refine_block.strip():
                    state.errors.append(
                        "@refine with mingle: false cannot have an indented body. "
                        "Use `with <name>: <value>` binding lines, or remove the "
                        "body."
                    )
                    index = next_index
                    continue
            child_variables = {**variables, **bindings} if is_bound else variables

            file_name = _substitute_variables(file_name, variables).strip()
            if _VARIABLE_RE.search(file_name):
                state.errors.append(
                    f"@refine path has unresolved variable(s): {file_name}"
                )
                index = next_index
                continue
            if file_name.startswith("module:"):
                module_name = file_name.removeprefix("module:").strip()
                module_body = resolve_module_body(
                    module_name,
                    base_dir,
                    settings=state.settings,
                )
                state.warnings.extend(module_body.warnings)
                if module_body.errors:
                    state.errors.extend(module_body.errors)
                    index = next_index
                    continue
                assert module_body.source is not None
                path = Path(module_body.source).resolve()
                file_text = module_body.text
                state.file_reads += 1
            else:
                fragment = resolve_fragment_reference(file_name, state.settings)
                if fragment.error is not None:
                    state.errors.append(fragment.error)
                    index = next_index
                    continue
                path = (
                    fragment.path
                    if fragment.path is not None
                    else (base_dir / file_name).resolve()
                )
                if fragment.path is None and not is_explicit_file_reference(file_name):
                    state.errors.append(
                        f"Bare @refine path '{file_name}' must resolve as a fragment "
                        "or start with ./, ../, /, or ~/."
                    )
                    index = next_index
                    continue
                file_text = read_file(file_name, base_dir)
                state.file_reads += 1
                if file_text.startswith("Error:"):
                    state.errors.append(file_text)
                    index = next_index
                    continue
            if path in stack:
                state.errors.append(f"Cyclic @refine detected for '{file_name}'.")
                index = next_index
                continue
            preprocessed = preprocess_weavemark(
                file_text,
                path.parent,
                settings=state.settings,
            )
            state.warnings.extend(preprocessed.warnings)
            state.errors.extend(preprocessed.errors)
            if preprocessed.errors:
                index = next_index
                continue
            compiled = _compile_structural_text(
                preprocessed.text,
                child_variables,
                path.parent,
                state,
                read_file,
                (*stack, path),
            )
            if compiled is None:
                return None
            output_lines.append(compiled)
            index = next_index
            continue

        if directive == "if":
            block, index = _collect_indented_block(lines, index + 1)
            else_block = ""
            else_index = index
            while else_index < len(lines) and not lines[else_index].strip():
                else_index += 1
            if else_index < len(lines):
                else_match = _directive_match(lines[else_index])
                if else_match is not None and else_match.group("name") == "else":
                    else_block, index = _collect_indented_block(
                        lines, else_index + 1
                    )
            condition = rest.split()[0] if rest else ""
            resolved = _resolve_variable_path(variables, condition)
            if resolved is _MISSING_VARIABLE:
                resolved = None
            selected = block if _coerce_bool(resolved) else else_block
            if selected:
                compiled = _compile_structural_text(
                    selected,
                    variables,
                    base_dir,
                    state,
                    read_file,
                    stack,
                )
                if compiled is None:
                    return None
                output_lines.append(compiled)
            continue

        if directive == "else":
            state.errors.append("@else must immediately follow @if.")
            _, index = _collect_indented_block(lines, index + 1)
            continue

        if directive == "match":
            block, index = _collect_indented_block(lines, index + 1)
            variable = rest.split()[0] if rest else ""
            resolved = _resolve_variable_path(variables, variable)
            if resolved is _MISSING_VARIABLE:
                resolved = None
            selected = _parse_match_block(block, resolved)
            if selected is None:
                state.warnings.append(f"No @match branch matched '{variable}'.")
                continue
            compiled = _compile_structural_text(
                selected,
                variables,
                base_dir,
                state,
                read_file,
                stack,
            )
            if compiled is None:
                return None
            output_lines.append(compiled)
            continue

        if directive == "bind":
            binding = _parse_bind_directive(rest, variables, base_dir, state)
            if binding is not None:
                state.bindings.append(binding)
            index += 1
            continue

        if directive == "tool":
            block, index = _collect_indented_block(lines, index + 1)
            tool_name = _parse_tool_header(rest, state)
            if tool_name is not None:
                normalized_tool_name = tool_name.casefold()
                if normalized_tool_name in state.seen_tools:
                    state.errors.append(f"Duplicate @tool declaration: {tool_name}")
                else:
                    state.seen_tools.add(normalized_tool_name)
                    state.tools.append(
                        _parse_tool_directive(tool_name, block, state)
                    )
            continue

        if directive == "execute":
            block, index = _collect_indented_block(lines, index + 1)
            if state.seen_execution:
                state.errors.append("Duplicate @execute directive.")
                continue
            state.seen_execution = True
            state.execution = _parse_execute_directive(
                rest, block, state, base_dir, variables
            )
            continue

        if directive == "output":
            block, index = _collect_indented_block(lines, index + 1)
            if state.current_output_scope in state.seen_output_scopes:
                state.errors.append(
                    f"Duplicate @output contract for scope "
                    f"{state.current_output_scope!r}."
                )
                continue
            state.seen_output_scopes.add(state.current_output_scope)
            contract = _parse_output_directive(rest, block, state, variables)
            state.prompt_outputs[state.current_output_scope] = contract
            obligation = _output_text_obligation(contract)
            if obligation is not None:
                output_lines.append(obligation)
            continue

        if directive == "package":
            block, index = _collect_indented_block(lines, index + 1)
            package = _parse_package_directive(rest, block, variables, state)
            if package is not None:
                target = package["file"].casefold()
                if target in state.seen_package_targets:
                    state.errors.append(
                        f"Duplicate @package output target: {package['file']}"
                    )
                else:
                    state.seen_package_targets.add(target)
                    state.packages.append(package)
            continue

        if is_fslm_machine_directive(directive, _fslm_machine_semantic_names(state)):
            block, index = _collect_indented_block(lines, index + 1)
            lowered = lower_machine_block(rest, block)
            state.warnings.extend(lowered.warnings)
            state.errors.extend(lowered.errors)
            if lowered.machine_name and lowered.machine_spec:
                if lowered.machine_name in state.fslm_machines:
                    state.errors.append(
                        f"Duplicate FSLM @machine declaration: {lowered.machine_name}"
                    )
                else:
                    state.fslm_machines[lowered.machine_name] = lowered.machine_spec
                for prompt_name, prompt_text in lowered.prompts.items():
                    if prompt_name in state.generated_prompts:
                        state.errors.append(
                            f"Duplicate generated FSLM prompt: {prompt_name}"
                        )
                    else:
                        state.generated_prompts[prompt_name] = prompt_text
            continue

        if compile_semantic is not None and compile_semantic.name == "assert":
            if not _validate_compile_semantic_contract(
                compile_semantic,
                {"inspect_text", "diagnostics"},
                state,
            ):
                index += 1
                continue
            block, index = _collect_indented_block(lines, index + 1)
            assertion = _parse_structural_assertion(rest, block)
            if isinstance(assertion, str):
                state.errors.append(assertion)
                continue
            state.assertions.append(assertion)
            continue

        if compile_semantic is not None and compile_semantic.name == "inspect":
            return None

        if compile_semantic is not None and compile_semantic.name in {"ask", "iterate"}:
            return None

        if execute_semantic is not None:
            block, index = _collect_indented_block(lines, index + 1)
            _collect_execution_node(execute_semantic, directive, rest, block, state)
            positional, options = _parse_directive_options(rest)
            result_name = options.get("as")
            if result_name:
                output_lines.append(f"@{{{result_name}}}")
            continue

        return None

    return (
        _substitute_variables(
            "\n".join(output_lines).strip("\n"),
            variables,
            protected_names=state.execution_result_names,
        )
        .replace(
            _EMBED_VARIABLE_OPEN_SENTINEL,
            "@{",
        )
        .replace(
            "@@",
            "@",
        )
    )


def _normalize_prompt_format(
    prompt_block: _NamedPromptBlock,
    compile_format: str,
    state: _StructuralCompileState,
) -> str | None:
    raw_format = prompt_block.format
    if raw_format is None:
        return compile_format
    normalized: str | None = normalize_compile_format(raw_format, state.settings)
    if normalized is None:
        state.errors.append(
            f"@prompt {prompt_block.name} format is unsupported: {raw_format}. "
            f"Supported formats: {supported_compile_formats_text(state.settings)}."
        )
        return None
    return normalized


def _compile_unified_spec(
    spec_text: str,
    unified_spec: _UnifiedSpec,
    variables: dict[str, Any],
    base_dir: Path,
    state: _StructuralCompileState,
    read_file: ReadFile,
    stack: tuple[Path, ...],
) -> str | None:
    """Compile a spec that contains top-level ``@prompt`` and/or ``@emit`` blocks."""

    # Pre-scan for @execute *in this spec's own text* (lexical, not via
    # refined children). This is the basis for the disposition rule.
    has_execute = _spec_has_top_level_execute(spec_text)

    # format: is emission-only metadata; on a pipeline (`@execute`) spec it
    # would otherwise be silently ignored, which confuses users. Reject it.
    if has_execute:
        for block in unified_spec.prompts:
            if block.format:
                state.errors.append(
                    f"@prompt {block.name}: format: is an emission-only parameter "
                    f"and cannot be used in a "
                    f"pipeline spec (one with top-level @execute). Remove "
                    f"it or drop @execute."
                )

    # Determine role usage among @prompt blocks.
    roles_present = [bool(block.role) for block in unified_spec.prompts]
    all_have_roles = bool(roles_present) and all(roles_present)
    none_have_roles = not any(roles_present)

    # Disposition rule.
    # If @execute is present in the spec text, blocks always land in <prompts>
    # (pipeline). If not, all-roles → <emits>; no-roles → <prompts> (refine
    # target); mixed roles → error.
    if has_execute:
        disposition = "prompts"
    elif unified_spec.prompts and all_have_roles:
        disposition = "emits"
    elif not unified_spec.prompts or none_have_roles:
        disposition = "prompts"
    else:
        state.errors.append(
            "@prompt blocks without @execute must either all declare role: "
            "<role> (to be emitted as artifact files) or none of them must "
            "(to serve as @refine targets). Mixing role-tagged and role-less "
            "@prompt blocks in the same spec is ambiguous; either add "
            "@execute to make this a pipeline, or split the spec."
        )
        # Ambiguous spec: surface the error but keep a sensible composed
        # output (prefix + suffix only) so the controller still produces a
        # CompositionResult instead of falling back to the LLM.
        prefix_only = _compile_structural_text(
            unified_spec.prefix,
            variables,
            base_dir,
            state,
            read_file,
            stack,
        )
        suffix_only = _compile_structural_text(
            unified_spec.suffix,
            variables,
            base_dir,
            state,
            read_file,
            stack,
        )
        if prefix_only is None or suffix_only is None:
            return ""
        return _join_prompt_parts(prefix_only, suffix_only)

    # Compile prefix / suffix shared context.
    prefix = _compile_structural_text(
        unified_spec.prefix,
        variables,
        base_dir,
        state,
        read_file,
        stack,
    )
    suffix = _compile_structural_text(
        unified_spec.suffix,
        variables,
        base_dir,
        state,
        read_file,
        stack,
    )
    if prefix is None or suffix is None:
        return None
    shared_context = _join_prompt_parts(prefix, suffix)

    # Resolve the cascade setting.
    cascade_default = disposition == "prompts"
    context_mode = state.compile.get("context", "auto")
    cascade = cascade_default if context_mode == "auto" else context_mode == "cascade"

    # Resolve the artifact extension.
    compile_format = str(state.compile.get("format") or "markdown")
    extension = extension_for_compile_format(compile_format, state.settings)

    # Compile each @prompt block.
    prompt_map: dict[str, str] = {}
    roles: dict[str, str] = {}
    emit_targets: list[tuple[str, str]] = []
    seen_prompt_names: set[str] = set()
    for prompt_block in unified_spec.prompts:
        normalized_prompt_name = prompt_block.name.casefold()
        if normalized_prompt_name in seen_prompt_names:
            state.errors.append(
                "Duplicate @prompt declaration (names are case-insensitive): "
                f"{prompt_block.name}"
            )
            continue
        seen_prompt_names.add(normalized_prompt_name)
        state.current_output_scope = prompt_block.name
        prompt_text = _compile_structural_text(
            prompt_block.text,
            variables,
            base_dir,
            state,
            read_file,
            stack,
        )
        state.current_output_scope = "default"
        if prompt_text is None:
            return None

        if disposition == "prompts":
            if cascade:
                prompt_map[prompt_block.name] = _join_prompt_parts(
                    prefix, prompt_text, suffix
                )
            else:
                prompt_map[prompt_block.name] = prompt_text
            if prompt_block.role:
                roles[prompt_block.name] = prompt_block.role
        else:
            # emission disposition
            if not _EMIT_PROMPT_NAME_RE.fullmatch(prompt_block.name):
                state.errors.append(
                    "@prompt name used for emission must be a safe dotted "
                    f"identifier without path separators: {prompt_block.name}"
                )
                continue
            role = prompt_block.role or ""
            if not _IDENTIFIER_TOKEN_RE.fullmatch(role):
                state.errors.append(
                    "@prompt role must be a safe identifier without path "
                    f"separators: {role}"
                )
                continue
            parts: list[str] = [prompt_block.name, role]
            if prompt_block.format:
                prompt_format = _normalize_prompt_format(
                    prompt_block,
                    compile_format,
                    state,
                )
                if prompt_format is None:
                    continue
                if prompt_format != compile_format:
                    parts.append(
                        extension_for_compile_format(prompt_format, state.settings)
                    )
            file_name = ".".join(parts) + "." + extension
            if cascade:
                composed = _join_prompt_parts(prefix, prompt_text, suffix)
            else:
                composed = prompt_text
            emit_targets.append((file_name, composed))

    # Compile @emit (literal file path) blocks. These are always artifact
    # emissions and apply the cascade setting like other emit-disposition
    # blocks.
    literal_emit_targets: list[tuple[str, str]] = []
    for emit in unified_spec.emits:
        compiled = _compile_structural_text(
            emit.text,
            variables,
            base_dir,
            state,
            read_file,
            stack,
        )
        if compiled is None:
            return None
        if cascade and disposition == "emits":
            content = _join_prompt_parts(prefix, compiled, suffix)
        else:
            content = compiled
        literal_emit_targets.append((emit.file_name, content))

    # Commit prompt_map (pipeline disposition).
    if disposition == "prompts" and prompt_map:
        if state.prompt_map is None:
            state.prompt_map = {}
        for name, prompt_text in prompt_map.items():
            if name in state.prompt_map:
                state.errors.append(f"Duplicate compiled prompt name: {name}")
                continue
            state.prompt_map[name] = prompt_text
        for name, role in roles.items():
            if name not in state.prompt_roles:
                state.prompt_roles[name] = role

    # Commit emits. Detect duplicates both exactly and case-insensitively
    # (the latter matters on case-insensitive filesystems like macOS HFS+
    # / APFS in default config and most Windows volumes).
    seen_lower: dict[str, str] = {}
    for file_name, content in emit_targets + literal_emit_targets:
        if file_name in state.emits:
            state.errors.append(f"Duplicate emitted artifact target: {file_name}")
            continue
        lower_name = file_name.lower()
        if lower_name in seen_lower and seen_lower[lower_name] != file_name:
            state.errors.append(
                f"Emitted artifact targets collide on case-insensitive "
                f"filesystems: {seen_lower[lower_name]!r} vs {file_name!r}"
            )
            continue
        seen_lower[lower_name] = file_name
        state.emits[file_name] = content

    # Disposition-was-emission-but-refined-child-declared-@execute warning.
    if disposition == "emits" and state.execution:
        state.warnings.append(
            "@prompt blocks were emitted as artifacts, but a refined child "
            "declared @execute. To run these as a pipeline, declare @execute "
            "at the top level of this spec."
        )

    return shared_context


def try_apply_structural_helpers(
    spec_text: str,
    variables: dict[str, Any],
    base_dir: Path,
    read_file: ReadFile,
    semantic_definitions: dict[str, WeaveMarkDefinition] | None = None,
    settings: WeaveMarkSettings | None = None,
) -> StructuralHelperResult | None:
    """Try structural helpers, returning ``None`` for LLM-only directives."""

    state = _StructuralCompileState(
        semantic_definitions=semantic_definitions or {},
        settings=settings or builtin_weavemark_settings(),
    )
    _collect_weavemark_pragma(spec_text, state)
    composed_prompt = _compile_structural_text(
        spec_text,
        variables,
        base_dir,
        state,
        read_file,
    )
    if composed_prompt is None:
        return None

    if state.execution_nodes:
        if state.execution.get("type") != "functional":
            state.errors.append(
                "Execution semantic functions require @execute functional."
            )
        else:
            _validate_functional_execution_plan(state)
            state.execution["nodes"] = state.execution_nodes
            state.execution["bindings"] = list(state.bindings)
    _attach_fslm_machine_spec(state)

    _evaluate_assertions(state, composed_prompt, variables)
    generated_prompts = state.generated_prompts
    if generated_prompts and composed_prompt:
        generated_prompts = {
            name: _join_prompt_parts(composed_prompt, prompt)
            for name, prompt in generated_prompts.items()
        }
    prompts = dict(generated_prompts)
    if state.prompt_map:
        duplicates = sorted(set(prompts) & set(state.prompt_map))
        for duplicate in duplicates:
            state.errors.append(f"Duplicate prompt name: {duplicate}")
        prompts.update(state.prompt_map)
    if not prompts:
        prompts = {"default": composed_prompt}

    return StructuralHelperResult(
        composed_prompt=composed_prompt,
        prompts=prompts,
        prompt_roles=state.prompt_roles,
        prompt_outputs=state.prompt_outputs,
        compile=state.compile,
        tools=state.tools,
        bindings=state.bindings,
        execution=state.execution,
        emits=state.emits,
        packages=state.packages,
        warnings=state.warnings,
        errors=state.errors,
        suggestions=state.suggestions,
        tool_calls_made=state.file_reads,
    )
