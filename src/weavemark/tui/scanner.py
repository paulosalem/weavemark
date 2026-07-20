"""Spec scanner — extract structured metadata from a promplet file.

Parses the spec text using **regex only** (no LLM call) to discover:
  - ``@{variables}`` — text / multiline inputs
  - ``@match var`` cases — select dropdowns
  - ``@if var`` flags — boolean toggles
  - ``@compile format: ...`` — compile-time output defaults
  - ``@embed file: @{var}`` and imported ``@refine @{var}`` — file inputs
  - ``@prompt name role: role`` (without ``@execute``) — emitted artifact files
  - ``@emit file: path`` — emitted output files
  - ``@execute`` strategy — execution metadata
  - ``@prompt name`` — named prompts
  - ``@tool name`` — tool declarations
  - ``@bind name`` — companion-program bindings
  - imported ``@assert`` — validation hints
  - ``@note`` near variables — help text

This module is intentionally LLM-free so it can run instantly for TUI form
generation, IDE integration, spec linting, and pre-flight checks.
"""

from __future__ import annotations

import re
import shlex
import textwrap
from contextlib import suppress
from dataclasses import dataclass, field

from weavemark.compilation.prompt_header import (
    parse_prompt_header,
)
from weavemark.compile_options import (
    extension_for_compile_format,
    normalize_compile_format,
)
from weavemark.settings import WeaveMarkSettings

ScanValue = str | int | float | list[str]

# ═══════════════════════════════════════════════════════════════════
# Data classes
# ═══════════════════════════════════════════════════════════════════


@dataclass
class SpecInput:
    """A single user-facing input discovered in a spec."""

    name: str
    input_type: str  # "text", "multiline", "select", "boolean", "file"
    options: list[str] | None = None
    default: str | None = None
    description: str | None = None
    file_hint: str | None = None
    source_directive: str | None = None  # which directive produced this


@dataclass
class SpecMetadata:
    """Structured metadata extracted from a promplet file."""

    title: str = ""
    description: str = ""
    inputs: list[SpecInput] = field(default_factory=list)
    compile: dict[str, str] | None = None
    execution: dict[str, ScanValue] | None = None
    prompt_names: list[str] = field(default_factory=list)
    tool_names: list[str] = field(default_factory=list)
    binding_names: list[str] = field(default_factory=list)
    module_name: str | None = None
    use_modules: list[str] = field(default_factory=list)
    include_modules: list[str] = field(default_factory=list)
    macro_names: list[str] = field(default_factory=list)
    refine_files: list[str] = field(default_factory=list)
    reference_files: list[str] = field(default_factory=list)
    embed_files: list[str] = field(default_factory=list)
    emit_files: list[str] = field(default_factory=list)
    assertions: list[str] = field(default_factory=list)
    has_notes: bool = False


# ═══════════════════════════════════════════════════════════════════
# Regex patterns
# ═══════════════════════════════════════════════════════════════════

_WEAVEMARK_VAR = re.compile(r"@\{\s*([A-Za-z_][\w.-]*)\s*\}")
_MATCH_DIRECTIVE = re.compile(r"^[ \t]*@match\s+(\w+)", re.MULTILINE)
_MATCH_CASE = re.compile(r'^[ \t]*"([^"]+)"\s*==>', re.MULTILINE)
_IF_DIRECTIVE = re.compile(r"^[ \t]*@if\s+(\w+)", re.MULTILINE)
_COMPILE_DIRECTIVE = re.compile(
    r"^[ \t]*@compile\s+(?P<params>.*)$",
    re.MULTILINE,
)
_EXECUTE_DIRECTIVE = re.compile(
    r"^[ \t]*@execute(?:\s+(?P<header>[^\n]*))?(?P<body>(?:\n(?:[ \t]+\S.*))*)",
    re.MULTILINE,
)
_PROMPT_DIRECTIVE_LINE = re.compile(
    r"^[ \t]*@prompt\s[^\n]*",
    re.MULTILINE,
)
_MODULE_DIRECTIVE = re.compile(
    r"^[ \t]*@module\s+([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*)", re.MULTILINE
)
_USE_DIRECTIVE = re.compile(
    r"^[ \t]*@use\s+([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)*)", re.MULTILINE
)
_INCLUDE_DIRECTIVE = re.compile(r"^[ \t]*@include\s+([A-Za-z_][\w.-]*)", re.MULTILINE)
_DEFINE_DIRECTIVE = re.compile(r"^[ \t]*@define\s+([A-Za-z_][\w-]*)", re.MULTILINE)
_TOOL_DIRECTIVE = re.compile(r"^[ \t]*@tool\s+(\S+)", re.MULTILINE)
_BIND_DIRECTIVE = re.compile(r"^[ \t]*@bind\s+([A-Za-z_][\w.-]*)", re.MULTILINE)
_EXECUTION_RESULT_AS = re.compile(
    r"^[ \t]*@(?!prompt\b)[A-Za-z_][\w.-]*\b[^\n]*\bas:\s*([A-Za-z_][\w.-]*)",
    re.MULTILINE,
)
_REFINE_DIRECTIVE = re.compile(r"^[ \t]*@refine\s+(\S+)", re.MULTILINE)
_REFERENCE_DIRECTIVE = re.compile(
    r"^[ \t]*@reference\s+(\"[^\"]+\"|'[^']+'|\S+)",
    re.MULTILINE,
)
_INLINE_REFERENCE = re.compile(
    r"@reference\(\s*(\"[^\"]+\"|'[^']+'|[A-Za-z0-9_./~+-]+)"
)
_PATH_REFERENCE = re.compile(
    r"(?<![A-Za-z0-9_@])@((?:\.{0,2}/|~/|/)"
    r"[A-Za-z0-9_./~+-]+|[A-Za-z0-9_+-]+\.[A-Za-z0-9_.+-]+)"
)
_EMBED_FILE = re.compile(r"^[ \t]*@embed\s+file:\s*(\S+)", re.MULTILINE)
_EMIT_FILE = re.compile(
    r"^[ \t]*@emit\s+(?:file:\s*|file=)(\"[^\"]+\"|'[^']+'|\S+)",
    re.MULTILINE,
)
_EXECUTE_LINE_RE = re.compile(r"^[ \t]*@execute\b", re.MULTILINE)
_ASSERT_DIRECTIVE = re.compile(r"^[ \t]*@assert\s+(.*)", re.MULTILINE)
_NOTE_BLOCK = re.compile(r"^[ \t]*@note\s*\n((?:[ \t]+.*\n?)*)", re.MULTILINE)
_TOP_LEVEL_H1 = re.compile(r"^#\s+(.+)")
_DIRECTIVE_NAME = re.compile(r"^@([A-Za-z_][\w.-]*)\b")
_PRIVATE_BODY_DIRECTIVES = {
    "assert",
    "bind",
    "compile",
    "define",
    "execute",
    "inspect",
    "module",
    "note",
    "output",
    "package",
    "param",
    "prompt",
    "refine",
    "tool",
    "use",
}
_NON_PRIMARY_TITLE_DIRECTIVES = {"emit"}

# File directives that accept file: @{var} patterns
_FILE_DIRECTIVES = [
    ("@embed", _EMBED_FILE),
]

_RICH_FORMAT_HINT = "Supports: .txt, .md, .pdf, .docx, .pptx, .xlsx, .html"

# Variable names that suggest multiline content
_MULTILINE_HINTS = {
    "description",
    "text",
    "content",
    "body",
    "prompt",
    "instructions",
    "message",
    "context",
    "details",
    "summary",
    "draft",
    "template",
    "text_a",
    "text_b",
    "input_text",
    "output_text",
}

# Strategy-internal variables injected at runtime (not user inputs).
_STRATEGY_INTERNAL_VARS = {
    "collaborative": {"edited_content", "original_content"},
    "reflection": {"response", "issues", "previous"},
    "tree-of-thought": {"state", "best_path"},
    "simplified-tree-of-thought": {"candidates", "best_approach"},
}

# Loop built-ins the `chain` engine injects per repeated iteration.
_CHAIN_LOOP_VARS = {"previous", "index", "count"}


# ═══════════════════════════════════════════════════════════════════
# Scanner
# ═══════════════════════════════════════════════════════════════════


def scan_spec(
    spec_text: str,
    settings: WeaveMarkSettings | None = None,
) -> SpecMetadata:
    """Scan a spec and extract structured metadata.

    This is a fast, regex-only pass — no LLM call.  It discovers all
    user-facing inputs and structural metadata needed to build a TUI
    form or perform pre-flight validation.
    """
    meta = SpecMetadata()
    input_scan_text = _strip_define_blocks(spec_text)
    internal_vars: set[str] = set()
    internal_vars.update(_EXECUTION_RESULT_AS.findall(spec_text))

    # ── Title (first top-level # heading) ────────────────────────
    title_line_index, meta.title = _extract_title(spec_text)

    # ── Description (text after title, before next top-level block)
    meta.description = _extract_description(spec_text, title_line_index)

    # ── Notes ────────────────────────────────────────────────────
    note_blocks = _NOTE_BLOCK.findall(spec_text)
    meta.has_notes = len(note_blocks) > 0
    # Build a map of variable → nearby note text for help descriptions
    note_hints = _extract_note_hints(spec_text)

    # ── @compile ─────────────────────────────────────────────────
    compile_match = _COMPILE_DIRECTIVE.search(spec_text)
    if compile_match:
        params = _parse_inline_params(compile_match.group("params"))
        raw_format = params.get("format")
        if raw_format and not _is_variable(raw_format):
            normalized_format = normalize_compile_format(raw_format, settings)
            if normalized_format is not None:
                meta.compile = {"format": normalized_format}

    # ── @execute ─────────────────────────────────────────────────
    exec_match = _EXECUTE_DIRECTIVE.search(spec_text)
    if exec_match:
        header = (exec_match.group("header") or "").strip()
        try:
            header_tokens = shlex.split(header)
        except ValueError:
            header_tokens = header.split()
        strategy = header_tokens[0] if header_tokens else ""
        config_block = exec_match.group("body").strip()
        config: dict[str, ScanValue] = {"type": strategy} if strategy else {}
        if len(header_tokens) > 1:
            config.update(
                {
                    key: _parse_scan_value(value)
                    for key, value in _parse_inline_params(
                        " ".join(header_tokens[1:])
                    ).items()
                }
            )
        for line in config_block.splitlines():
            line = line.strip()
            if ":" in line:
                k, _, v = line.partition(":")
                config[k.strip()] = _parse_scan_value(v.strip())
        meta.execution = config

    # ── @prompt ──────────────────────────────────────────────────
    parsed_prompts = []
    for match in _PROMPT_DIRECTIVE_LINE.finditer(spec_text):
        parsed = parse_prompt_header(match.group(0))
        if parsed is not None and parsed.name:
            parsed_prompts.append(parsed)
    meta.prompt_names = list(dict.fromkeys(p.name for p in parsed_prompts if p.name))

    # Pipeline stages thread each other's outputs at runtime as @{<stage>}, so a
    # @prompt name is never a user input. A `chain` also injects the loop
    # built-ins @{previous}/@{index}/@{count} per iteration; `reflection` threads
    # each production stage's output forward as @{previous}.
    internal_vars.update(meta.prompt_names)
    engine_type = str((meta.execution or {}).get("type", ""))
    internal_vars.update(_STRATEGY_INTERNAL_VARS.get(engine_type, set()))
    if engine_type == "chain":
        internal_vars.update(_CHAIN_LOOP_VARS)

    # ── @module / @use / @include / @define ─────────────────────
    module_match = _MODULE_DIRECTIVE.search(spec_text)
    if module_match:
        meta.module_name = module_match.group(1)
    meta.use_modules = list(dict.fromkeys(_USE_DIRECTIVE.findall(spec_text)))
    meta.include_modules = list(dict.fromkeys(_INCLUDE_DIRECTIVE.findall(spec_text)))
    meta.macro_names = list(dict.fromkeys(_DEFINE_DIRECTIVE.findall(spec_text)))

    # ── @tool ────────────────────────────────────────────────────
    meta.tool_names = list(dict.fromkeys(_TOOL_DIRECTIVE.findall(spec_text)))

    # ── @bind ────────────────────────────────────────────────────
    meta.binding_names = list(dict.fromkeys(_BIND_DIRECTIVE.findall(spec_text)))

    # ── @assert ──────────────────────────────────────────────────
    meta.assertions = _ASSERT_DIRECTIVE.findall(spec_text)

    # ── @refine (static file deps) ──────────────────────────────
    for path in _REFINE_DIRECTIVE.findall(spec_text):
        if not _is_variable(path):
            meta.refine_files.append(path)

    # ── @reference and Claude-style source references ──────────
    for pattern in (_REFERENCE_DIRECTIVE, _INLINE_REFERENCE, _PATH_REFERENCE):
        for path in pattern.findall(spec_text):
            cleaned = path.strip("\"'").rstrip(".,;:!?")
            if cleaned not in meta.reference_files:
                meta.reference_files.append(cleaned)

    # ── @emit (static output files) ─────────────────────────────
    for path in _EMIT_FILE.findall(spec_text):
        cleaned_path = path.strip("\"'")
        if not _is_variable(cleaned_path):
            meta.emit_files.append(cleaned_path)

    # ── role-tagged @prompt blocks → emitted artifacts when no @execute ─
    has_execute = bool(_EXECUTE_LINE_RE.search(spec_text))
    if not has_execute:
        compile_format = (meta.compile or {}).get("format") if meta.compile else None
        extension = extension_for_compile_format(compile_format, settings)
        normalized_compile_format = normalize_compile_format(
            compile_format or "markdown",
            settings,
        )
        for parsed in parsed_prompts:
            prompt_format_extension = None
            if parsed.format:
                normalized_prompt_format = normalize_compile_format(
                    parsed.format,
                    settings,
                )
                if (
                    normalized_prompt_format is not None
                    and normalized_prompt_format != normalized_compile_format
                ):
                    prompt_format_extension = extension_for_compile_format(
                        normalized_prompt_format,
                        settings,
                    )
            predicted = parsed.emit_filename(
                extension,
                prompt_format_extension=prompt_format_extension,
            )
            if predicted and not _is_variable(parsed.name):
                meta.emit_files.append(predicted)

    # ── Collect all inputs ───────────────────────────────────────
    seen_names: set[str] = set()
    inputs: list[SpecInput] = []
    interpolated_roots = {
        match.group(1).split(".", 1)[0]
        for match in _WEAVEMARK_VAR.finditer(input_scan_text)
    }

    # 1. @match variables → select dropdowns
    for m in _MATCH_DIRECTIVE.finditer(input_scan_text):
        var_name = m.group(1)
        if var_name in seen_names:
            continue
        seen_names.add(var_name)
        # Extract case values from the block following the @match
        cases = _extract_match_cases(input_scan_text, m)
        inputs.append(
            SpecInput(
                name=var_name,
                input_type="select",
                options=cases,
                description=note_hints.get(var_name),
                source_directive="@match",
            )
        )

    # 2. @if variables → boolean toggles
    for m in _IF_DIRECTIVE.finditer(input_scan_text):
        var_name = m.group(1)
        if var_name in seen_names or var_name in interpolated_roots:
            continue
        seen_names.add(var_name)
        inputs.append(
            SpecInput(
                name=var_name,
                input_type="boolean",
                default="false",
                description=note_hints.get(var_name),
                source_directive="@if",
            )
        )

    # 3. File directives with @{var} → file pickers
    for directive_name, pattern in _FILE_DIRECTIVES:
        for m in pattern.finditer(input_scan_text):
            path = m.group(1)
            if _is_variable(path):
                var_name = _extract_var_name(path)
                if var_name and var_name not in seen_names:
                    seen_names.add(var_name)
                    inputs.append(
                        SpecInput(
                            name=var_name,
                            input_type="file",
                            file_hint=_RICH_FORMAT_HINT,
                            description=note_hints.get(var_name),
                            source_directive=directive_name,
                        )
                    )
            else:
                # Static file ref → informational
                meta.embed_files.append(path)

    # 4. @refine with @{var} → file picker
    for m in _REFINE_DIRECTIVE.finditer(input_scan_text):
        path = m.group(1)
        if _is_variable(path):
            var_name = _extract_var_name(path)
            if var_name and var_name not in seen_names:
                seen_names.add(var_name)
                inputs.append(
                    SpecInput(
                        name=var_name,
                        input_type="file",
                        file_hint="WeaveMark file (.weavemark.md)",
                        description=note_hints.get(var_name),
                        source_directive="@refine",
                    )
                )

    # 5. Remaining @{variables} → text / multiline inputs. A dotted reference
    # like @{panels.0.beat} navigates a nested structure, so its ROOT (`panels`)
    # is the single structured input — collapse all dotted leaves to that root.
    for m in _WEAVEMARK_VAR.finditer(input_scan_text):
        var_name = m.group(1)
        is_dotted = "." in var_name
        root_name = var_name.split(".", 1)[0] if is_dotted else var_name
        if root_name in seen_names or root_name in internal_vars:
            continue
        seen_names.add(root_name)
        is_multiline = is_dotted or _is_multiline_hint(root_name)
        inputs.append(
            SpecInput(
                name=root_name,
                input_type="multiline" if is_multiline else "text",
                description=note_hints.get(root_name) or note_hints.get(var_name),
                source_directive="@{variable}",
            )
        )

    meta.inputs = inputs
    return meta


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def _strip_define_blocks(spec_text: str) -> str:
    """Remove top-level @define bodies before scanning user-facing inputs."""

    lines = spec_text.splitlines()
    kept: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^[ \t]*@define\b", line):
            define_indent = len(line) - len(line.lstrip(" \t"))
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if not candidate.strip():
                    index += 1
                    continue
                candidate_indent = len(candidate) - len(candidate.lstrip(" \t"))
                if candidate_indent <= define_indent:
                    break
                index += 1
            continue
        kept.append(line)
        index += 1
    return "\n".join(kept)


def _parse_scan_value(value: str) -> str | int | float | list[str]:
    """Parse simple scalar values used by scan metadata."""

    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
    try:
        return int(value)
    except (ValueError, TypeError):
        with suppress(ValueError, TypeError):
            return float(value)
    return value


def _parse_inline_params(text: str) -> dict[str, str]:
    """Parse simple directive parameters from one source line."""

    try:
        tokens = shlex.split(text.strip())
    except ValueError:
        return {}
    params: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.endswith(":") and index + 1 < len(tokens):
            params[token[:-1]] = tokens[index + 1]
            index += 2
        elif ":" in token:
            key, value = token.split(":", 1)
            if value:
                params[key] = value
                index += 1
            elif index + 1 < len(tokens):
                params[key] = tokens[index + 1]
                index += 2
            else:
                index += 1
        elif "=" in token:
            key, value = token.split("=", 1)
            if value:
                params[key] = value
                index += 1
            elif index + 1 < len(tokens):
                params[key] = tokens[index + 1]
                index += 2
            else:
                index += 1
        else:
            index += 1
    return params


def find_authored_title(spec_text: str) -> tuple[int | None, str]:
    """Find the first document H1, including one wrapped by a public body."""

    containers: list[tuple[int, bool, bool]] = []
    fallback: tuple[int | None, str] = (None, "")
    fenced = False
    for index, line in enumerate(spec_text.splitlines()):
        stripped = line.lstrip(" \t")
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced or not stripped:
            continue

        indent = len(line) - len(stripped)
        while containers and indent <= containers[-1][0]:
            containers.pop()

        directive = _DIRECTIVE_NAME.match(stripped)
        if directive:
            name = directive.group(1).casefold()
            is_public = name not in _PRIVATE_BODY_DIRECTIVES
            is_primary = name not in _NON_PRIMARY_TITLE_DIRECTIVES
            containers.append((indent, is_public, is_primary))
            continue

        heading = _TOP_LEVEL_H1.match(stripped)
        if heading and (
            (indent == 0 and not containers)
            or (
                containers
                and containers[0][0] == 0
                and all(container[1] for container in containers)
            )
        ):
            title = heading.group(1).strip()
            if containers and not all(container[2] for container in containers):
                if fallback[0] is None:
                    fallback = (index, title)
                continue
            return index, title
    return fallback


def _extract_title(spec_text: str) -> tuple[int | None, str]:
    """Return the authored title location and text."""

    return find_authored_title(spec_text)


def _extract_description(spec_text: str, title_line_index: int | None) -> str:
    """Extract free text owned by the authored title's indentation scope."""
    if title_line_index is None:
        return ""

    lines = spec_text.splitlines()
    title_line = lines[title_line_index]
    title_indent = len(title_line) - len(title_line.lstrip(" \t"))
    desc_lines: list[str] = []
    fenced = False
    for line in lines[title_line_index + 1 :]:
        stripped = line.lstrip(" \t")
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
            desc_lines.append(line)
            continue
        indent = len(line) - len(stripped)
        if not fenced and stripped:
            if indent < title_indent:
                break
            if indent == title_indent and (
                _DIRECTIVE_NAME.match(stripped) or stripped.startswith("#")
            ):
                break
        desc_lines.append(line)
    return textwrap.dedent("\n".join(desc_lines)).strip()


def _extract_match_cases(
    spec_text: str,
    directive_match: re.Match[str],
) -> list[str]:
    """Extract only named cases owned by one ``@match`` directive."""

    line_start = spec_text.rfind("\n", 0, directive_match.start()) + 1
    line_end = spec_text.find("\n", line_start)
    if line_end < 0:
        line_end = len(spec_text)
    directive_line = spec_text[line_start:line_end]
    directive_indent = len(directive_line) - len(directive_line.lstrip(" \t"))
    remaining = spec_text[directive_match.end() :]
    cases: list[str] = []
    case_indent: int | None = None
    for line in remaining.splitlines()[1:]:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" \t"))
        if indent <= directive_indent:
            break
        match = _MATCH_CASE.match(line)
        if match:
            if case_indent is None:
                case_indent = indent
            if indent == case_indent:
                cases.append(match.group(1))
    return cases


def _extract_note_hints(spec_text: str) -> dict[str, str]:
    """Map variable names to nearby @note descriptions.

    If a @note block appears within 5 lines before a @{variable},
    use its text as the variable's description.
    """
    hints: dict[str, str] = {}
    lines = spec_text.splitlines()

    # Find all @note block ranges
    note_ranges: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("@note"):
            start = i
            content_lines: list[str] = []
            i += 1
            while i < len(lines) and (
                lines[i].startswith("  ") or lines[i].strip() == ""
            ):
                if lines[i].strip():
                    content_lines.append(lines[i].strip())
                i += 1
            note_text = " ".join(content_lines)
            note_ranges.append((start, i, note_text))
        else:
            i += 1

    # For each variable, check if a @note ends within 5 lines before it
    for line_idx, line in enumerate(lines):
        for m in _WEAVEMARK_VAR.finditer(line):
            var_name = m.group(1)
            if var_name in hints:
                continue
            for _note_start, note_end, note_text in note_ranges:
                if 0 <= line_idx - note_end <= 5:
                    hints[var_name] = note_text[:200]  # cap length
                    break

    return hints


def _is_variable(path: str) -> bool:
    """Check if a file path is a @{variable} reference."""
    return _WEAVEMARK_VAR.fullmatch(path) is not None


def _extract_var_name(path: str) -> str | None:
    """Extract variable name from a @{var} path."""
    m = _WEAVEMARK_VAR.fullmatch(path)
    return m.group(1) if m else None


def _is_multiline_hint(var_name: str) -> bool:
    """Heuristic: does the variable name suggest multiline content?"""
    lower = var_name.lower()
    return any(hint in lower for hint in _MULTILINE_HINTS)
