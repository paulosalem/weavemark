"""Deterministic WeaveMark macro and module preprocessing."""

from __future__ import annotations

import re
import shlex
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from weavemark.compilation.args import parse_header_args
from weavemark.compilation.directive_registry import CORE_DIRECTIVES
from weavemark.promplet_library import (
    PrompletLibraryLookupError,
    resolve_module_source,
)
from weavemark.settings import (
    DefaultModuleImport,
    WeaveMarkSettings,
    load_weavemark_settings,
)
from weavemark.source_comments import strip_markdown_comments

_DIRECTIVE_RE = re.compile(
    r"^(?P<indent>[ \t]*)@(?P<name>[A-Za-z_][A-Za-z0-9_.-]*\??)"
    r"(?P<rest>(?:\s+.*)?)$"
)
_DEFINE_RE = re.compile(
    r"^@define\s+(?P<name>[A-Za-z_][A-Za-z0-9_-]*)" r"(?:\((?P<signature>.*)\))?\s*$"
)
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_MODULE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")
_VARIABLE_RE = re.compile(r"@\{\s*([A-Za-z_][\w.-]*)\s*\}")

_CORE_PRIMITIVES = CORE_DIRECTIVES
_SEMANTIC_PHASES = {"compile", "execute"}
_SEMANTIC_SCOPES = {
    "self",
    "body",
    "enclosing_block",
    "prompt",
    "document",
    "metadata",
}
_SEMANTIC_EFFECT_MODES = {"read", "write"}
_PARAM_MODES = {"text", "subspec", "path", "promplet"}
_OPAQUE_BODY_DIRECTIVES = {"execute", "embed", "note", "output", "package", "tool"}


@dataclass
class DefinitionParam:
    """A parameter accepted by a WeaveMark definition."""

    name: str
    description: str = ""
    default: str | None = None
    implicit: bool = False
    mode: str = "text"


@dataclass(frozen=True)
class SemanticEffect:
    """A host-owned capability requested by an effectful definition."""

    name: str
    mode: str


@dataclass
class WeaveMarkDefinition:
    """A reusable WeaveMark directive definition."""

    name: str
    params: list[DefinitionParam]
    body: str
    source: str
    closure: DefinitionEnvironment | None = None
    phase: str | None = None
    scope: str | None = None
    returns: str | None = None
    effects: list[SemanticEffect] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.source}:{self.name}"

    @property
    def is_semantic(self) -> bool:
        """Return True for effectful semantic-function definitions."""

        return bool(self.effects)

    @property
    def implicit_param(self) -> DefinitionParam | None:
        for param in self.params:
            if param.implicit:
                return param
        return None


@dataclass(frozen=True)
class UseDirective:
    """A module import declaration."""

    module_name: str
    alias: str | None = None
    exposing: tuple[str, ...] = ()
    expose_all: bool = False


@dataclass(frozen=True)
class ModuleBinding:
    """One default host binding declared by a reusable module."""

    name: str
    language: str
    source: str
    symbol: str
    module_name: str

    def metadata(self) -> dict[str, str]:
        """Return portable compiled binding metadata."""

        return {
            "name": self.name,
            "language": self.language,
            "from": self.source,
            "symbol": self.symbol,
            "module": self.module_name,
        }


@dataclass
class ParsedDocument:
    """A WeaveMark document split into metadata definitions and body."""

    module_name: str | None
    uses: list[UseDirective]
    definitions: list[WeaveMarkDefinition]
    body: str
    errors: list[str] = field(default_factory=list)


@dataclass
class ModuleDefinition:
    """A loaded WeaveMark module."""

    name: str
    source: str
    base_dir: Path
    macros: dict[str, WeaveMarkDefinition]
    semantics: dict[str, WeaveMarkDefinition]
    body: str
    default_bindings: tuple[ModuleBinding, ...] = ()
    aliases: dict[str, ModuleDefinition] = field(default_factory=dict)

    @property
    def exports(self) -> dict[str, WeaveMarkDefinition]:
        """All definitions exported by the module."""

        return {**self.macros, **self.semantics}


@dataclass
class DefinitionEnvironment:
    """Names available while expanding a WeaveMark document."""

    macros: dict[str, WeaveMarkDefinition] = field(default_factory=dict)
    semantics: dict[str, WeaveMarkDefinition] = field(default_factory=dict)
    modules: dict[str, ModuleDefinition] = field(default_factory=dict)


@dataclass
class PreprocessResult:
    """Result of macro/module preprocessing."""

    text: str
    module_name: str | None = None
    imports: list[str] = field(default_factory=list)
    includes: list[str] = field(default_factory=list)
    macros: list[str] = field(default_factory=list)
    semantic_definitions: dict[str, WeaveMarkDefinition] = field(default_factory=dict)
    bindings: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ModuleBodyResult:
    """Expanded reusable body resolved from a named module promplet."""

    text: str
    source: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class _ExpansionResult:
    text: str
    includes: list[str] = field(default_factory=list)


def preprocess_weavemark(
    spec_text: str,
    base_dir: Path,
    *,
    settings: WeaveMarkSettings | None = None,
) -> PreprocessResult:
    """Expand WeaveMark macros/modules before ordinary composition."""

    preprocessor = _WeaveMarkPreprocessor(
        settings=settings,
    )
    return preprocessor.preprocess(spec_text, base_dir)


def resolve_module_body(
    module_name: str,
    base_dir: Path,
    *,
    settings: WeaveMarkSettings | None = None,
) -> ModuleBodyResult:
    """Resolve and expand the reusable body of one module promplet."""
    preprocessor = _WeaveMarkPreprocessor(settings=settings)
    module = preprocessor._load_module(module_name, base_dir.resolve(), module_stack=())
    if module is None:
        return ModuleBodyResult(
            text="",
            warnings=preprocessor.warnings,
            errors=preprocessor.errors,
        )
    if not module.body.strip():
        preprocessor.errors.append(
            f"Module '{module_name}' exports definitions but has no refinable body. "
            "Use @use to import its definitions."
        )
    return ModuleBodyResult(
        text=module.body,
        source=module.source,
        warnings=preprocessor.warnings,
        errors=preprocessor.errors,
    )


class _WeaveMarkPreprocessor:
    """Stateful module resolver and macro expander for one preprocessing run."""

    def __init__(
        self,
        *,
        settings: WeaveMarkSettings | None,
    ) -> None:
        self.warnings: list[str] = []
        self.errors: list[str] = []
        self._module_cache: dict[tuple[str, Path], ModuleDefinition] = {}
        self._imported_bindings: dict[str, dict[str, str]] = {}
        self._local_binding_names: set[str] = set()
        self._settings = settings

    def preprocess(self, spec_text: str, base_dir: Path) -> PreprocessResult:
        parsed = _parse_document(spec_text, "<input>")
        self.errors.extend(parsed.errors)
        self._local_binding_names = _top_level_binding_names(parsed.body)
        env = self._build_environment(
            parsed,
            base_dir.resolve(),
            source="<input>",
            module_stack=(),
        )
        self._validate_macro_cycles(env.macros)

        if self.errors:
            return PreprocessResult(
                text="",
                module_name=parsed.module_name,
                imports=[use.module_name for use in parsed.uses],
                macros=[
                    definition.name
                    for definition in parsed.definitions
                    if not definition.is_semantic
                ],
                semantic_definitions=env.semantics,
                bindings=list(self._imported_bindings.values()),
                warnings=self.warnings,
                errors=self.errors,
            )

        expanded = self._expand_source(
            parsed.body,
            env,
            base_dir.resolve(),
            include_stack=(
                (parsed.module_name,) if parsed.module_name is not None else ()
            ),
            expansion_stack=(),
        )
        return PreprocessResult(
            text=expanded.text,
            module_name=parsed.module_name,
            imports=[use.module_name for use in parsed.uses],
            includes=expanded.includes,
            macros=[
                definition.name
                for definition in parsed.definitions
                if not definition.is_semantic
            ],
            semantic_definitions=env.semantics,
            bindings=list(self._imported_bindings.values()),
            warnings=self.warnings,
            errors=self.errors,
        )

    def _build_environment(
        self,
        parsed: ParsedDocument,
        base_dir: Path,
        *,
        source: str,
        module_stack: tuple[str, ...],
    ) -> DefinitionEnvironment:
        env = DefinitionEnvironment()

        if not module_stack and source == "<input>":
            self._register_default_modules(env, base_dir)

        for use in parsed.uses:
            module = self._load_module(use.module_name, base_dir, module_stack)
            if module is None:
                continue
            self._register_module_use(env, use, module)

        for definition in parsed.definitions:
            if definition.name in _CORE_PRIMITIVES:
                self.errors.append(
                    f"@define cannot override core primitive @{definition.name} in {source}."
                )
                continue
            if definition.name in env.macros or definition.name in env.semantics:
                self.errors.append(
                    f"Definition name collision for @{definition.name} in {source}."
                )
                continue
            if definition.is_semantic:
                env.semantics[definition.name] = definition
            else:
                env.macros[definition.name] = definition

        for definition in parsed.definitions:
            definition.closure = env

        return env

    def _register_default_modules(
        self,
        env: DefinitionEnvironment,
        base_dir: Path,
    ) -> None:
        settings = self._settings or load_weavemark_settings(base_dir).settings
        for default_import in settings.default_module_imports:
            module = self._load_module(default_import.name, base_dir, module_stack=())
            if module is None:
                continue
            self._register_module_use(
                env,
                _default_import_to_use(default_import),
                module,
            )

    def _register_module_use(
        self,
        env: DefinitionEnvironment,
        use: UseDirective,
        module: ModuleDefinition,
    ) -> None:
        namespace = use.alias or use.module_name
        existing_namespace = env.modules.get(namespace)
        if existing_namespace is not None:
            self.errors.append(
                f"Duplicate module namespace {namespace!r}: "
                f"{existing_namespace.name} is already imported."
            )
            return
        env.modules[namespace] = module
        env.modules[module.name] = module

        for export_name, macro in module.macros.items():
            qualified_name = f"{namespace}.{export_name}"
            if qualified_name in env.macros or qualified_name in env.semantics:
                self.errors.append(
                    f"Definition name collision for @{qualified_name}."
                )
                continue
            env.macros[qualified_name] = macro
        for export_name, semantic in module.semantics.items():
            qualified_name = f"{namespace}.{export_name}"
            if qualified_name in env.macros or qualified_name in env.semantics:
                self.errors.append(
                    f"Definition name collision for @{qualified_name}."
                )
                continue
            env.semantics[qualified_name] = semantic

        exposed_names = module.exports if use.expose_all else use.exposing
        for exposed_name in exposed_names:
            if exposed_name in _CORE_PRIMITIVES:
                self.errors.append(
                    f"@use {use.module_name} cannot expose @{exposed_name}; "
                    "that name is a core primitive."
                )
                continue
            exposed_macro = module.exports.get(exposed_name)
            if exposed_macro is None:
                self.errors.append(
                    f"@use {use.module_name} exposes unknown definition @{exposed_name}."
                )
                continue
            if exposed_name in env.macros or exposed_name in env.semantics:
                self.errors.append(
                    f"@use {use.module_name} exposes @{exposed_name}, "
                    "but that name is already available."
                )
                continue
            if exposed_macro.is_semantic:
                env.semantics[exposed_name] = exposed_macro
            else:
                env.macros[exposed_name] = exposed_macro

        for binding in module.default_bindings:
            metadata = binding.metadata()
            existing = self._imported_bindings.get(binding.name)
            if (
                existing is not None
                and existing != metadata
                and binding.name not in self._local_binding_names
            ):
                self.errors.append(
                    "Default binding collision for capability "
                    f"{binding.name!r}: {existing['module']} and "
                    f"{binding.module_name}. Declare a local @bind override to "
                    "select the implementation."
                )
                continue
            self._imported_bindings[binding.name] = metadata

    def _load_module(
        self,
        module_name: str,
        importer_base_dir: Path,
        module_stack: tuple[str, ...],
    ) -> ModuleDefinition | None:
        if module_name in module_stack:
            chain = " -> ".join((*module_stack, module_name))
            self.errors.append(f"Cycle detected in @use module chain: {chain}.")
            return None

        cache_key = (module_name, importer_base_dir.resolve())
        cached = self._module_cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            loaded = _read_module_source(module_name, importer_base_dir)
        except PrompletLibraryLookupError as exc:
            self.errors.append(str(exc))
            return None
        if loaded is None:
            self.errors.append(
                f"Module '{module_name}' was not found in the effective promplet library."
            )
            return None

        source_text, source_label, module_base_dir = loaded
        parsed = _parse_document(source_text, source_label)
        self.errors.extend(parsed.errors)
        if parsed.module_name is None:
            self.errors.append(f"Module file {source_label} is missing @module.")
            return None
        if parsed.module_name != module_name:
            self.errors.append(
                f"Module file {source_label} declares @module {parsed.module_name}, "
                f"but it was imported as {module_name}."
            )
            return None

        env = self._build_environment(
            parsed,
            module_base_dir,
            source=module_name,
            module_stack=(*module_stack, module_name),
        )
        self._validate_macro_cycles(env.macros)
        module_body, default_bindings = _extract_module_default_bindings(
            parsed.body,
            module_name,
            module_base_dir,
            self.errors,
        )
        expanded_body = self._expand_source(
            module_body,
            env,
            module_base_dir,
            include_stack=(module_name,),
            expansion_stack=(),
        )
        module = ModuleDefinition(
            name=module_name,
            source=source_label,
            base_dir=module_base_dir,
            macros={
                definition.name: definition
                for definition in parsed.definitions
                if not definition.is_semantic
            },
            semantics={
                definition.name: definition
                for definition in parsed.definitions
                if definition.is_semantic
            },
            body=_strip_promplet_declaration(expanded_body.text),
            default_bindings=default_bindings,
            aliases=env.modules,
        )
        self._module_cache[cache_key] = module
        return module

    def _expand_source(
        self,
        source: str,
        env: DefinitionEnvironment,
        base_dir: Path,
        *,
        include_stack: tuple[str, ...],
        expansion_stack: tuple[str, ...],
    ) -> _ExpansionResult:
        lines = source.splitlines()
        output_lines: list[str] = []
        includes: list[str] = []
        index = 0

        while index < len(lines):
            line = lines[index]
            match = _DIRECTIVE_RE.match(line)
            if match is None:
                output_lines.append(line)
                index += 1
                continue

            directive_name = match.group("name")
            indent = match.group("indent")
            rest = match.group("rest").strip()

            if directive_name == "include":
                block, index = _collect_indented_block(
                    lines,
                    index + 1,
                    len(indent),
                )
                if block.strip():
                    self.errors.append("@include does not accept an indented body.")
                included = self._expand_include(
                    rest,
                    env,
                    base_dir,
                    indent,
                    include_stack,
                    expansion_stack,
                )
                if included.text:
                    output_lines.extend(included.text.splitlines())
                includes.extend(included.includes)
                continue

            if directive_name in _OPAQUE_BODY_DIRECTIVES:
                block, index = _collect_indented_block(lines, index + 1, len(indent))
                output_lines.append(line)
                if block:
                    output_lines.extend(_indent_text(block, f"{indent}  ").splitlines())
                continue

            semantic = env.semantics.get(directive_name)
            if semantic is not None:
                block, index = _collect_indented_block(lines, index + 1, len(indent))
                implicit = semantic.implicit_param
                if (
                    implicit is not None
                    and implicit.default is None
                    and not block.strip()
                ):
                    self.errors.append(
                        f"@{semantic.name} missing required non-empty implicit "
                        f"body '{implicit.name}'."
                    )
                    continue
                output_lines.append(line)
                if block:
                    if implicit is not None and implicit.mode == "subspec":
                        expanded = self._expand_source(
                            block,
                            env,
                            base_dir,
                            include_stack=include_stack,
                            expansion_stack=expansion_stack,
                        )
                        includes.extend(expanded.includes)
                        block = expanded.text
                    output_lines.extend(_indent_text(block, f"{indent}  ").splitlines())
                continue

            macro = env.macros.get(directive_name)
            if macro is None:
                output_lines.append(line)
                index += 1
                continue

            block, index = _collect_indented_block(lines, index + 1, len(indent))
            expanded = self._expand_macro_call(
                macro,
                rest,
                block,
                indent,
                env,
                base_dir,
                include_stack,
                expansion_stack,
            )
            if expanded.text:
                output_lines.extend(expanded.text.splitlines())
            includes.extend(expanded.includes)

        return _ExpansionResult(
            text="\n".join(output_lines).strip("\n"),
            includes=includes,
        )

    def _expand_include(
        self,
        rest: str,
        env: DefinitionEnvironment,
        base_dir: Path,
        indent: str,
        include_stack: tuple[str, ...],
        expansion_stack: tuple[str, ...],
    ) -> _ExpansionResult:
        parsed_args = parse_header_args(rest)
        positional, options = parsed_args.positional, parsed_args.options
        if parsed_args.errors:
            self.errors.extend(f"@include: {error}" for error in parsed_args.errors)
            return _ExpansionResult(text="")
        if options:
            self.errors.append("@include accepts only a module alias or module name.")
            return _ExpansionResult(text="")
        if len(positional) != 1:
            self.errors.append(
                "@include requires exactly one module alias or module name."
            )
            return _ExpansionResult(text="")

        target = positional[0]
        module = env.modules.get(target)
        if module is None:
            module = self._load_module(target, base_dir, module_stack=())
        if module is None:
            self.errors.append(f"@include target '{target}' is not available.")
            return _ExpansionResult(text="")
        if module.name in include_stack:
            chain = " -> ".join((*include_stack, module.name))
            self.errors.append(f"Cycle detected in @include module chain: {chain}.")
            return _ExpansionResult(text="")

        expanded = self._expand_source(
            module.body,
            DefinitionEnvironment(
                macros={
                    **env.macros,
                    **module.aliases.get(module.name, module).macros,
                },
                semantics={
                    **env.semantics,
                    **module.aliases.get(module.name, module).semantics,
                },
                modules={**env.modules, **module.aliases},
            ),
            module.base_dir,
            include_stack=(*include_stack, module.name),
            expansion_stack=expansion_stack,
        )
        return _ExpansionResult(
            text=_indent_text(expanded.text, indent),
            includes=[target, *expanded.includes],
        )

    def _expand_macro_call(
        self,
        macro: WeaveMarkDefinition,
        rest: str,
        body: str,
        indent: str,
        caller_env: DefinitionEnvironment,
        base_dir: Path,
        include_stack: tuple[str, ...],
        expansion_stack: tuple[str, ...],
    ) -> _ExpansionResult:
        if macro.key in expansion_stack:
            chain = " -> ".join((*expansion_stack, macro.key))
            self.errors.append(f"Cycle detected in @define expansion chain: {chain}.")
            return _ExpansionResult(text="")

        bindings = self._bind_macro_arguments(
            macro,
            rest,
            body,
            caller_env,
            base_dir,
            include_stack,
            expansion_stack,
        )
        if bindings is None:
            return _ExpansionResult(text="")

        protected_bindings, protected_text = _protect_text_bindings(macro, bindings)
        substituted = _substitute_macro_params(macro.body, protected_bindings)
        closure = macro.closure or DefinitionEnvironment()
        expansion_env = DefinitionEnvironment(
            macros={**caller_env.macros, **closure.macros},
            semantics={**caller_env.semantics, **closure.semantics},
            modules={**caller_env.modules, **closure.modules},
        )
        expanded = self._expand_source(
            substituted,
            expansion_env,
            base_dir,
            include_stack=include_stack,
            expansion_stack=(*expansion_stack, macro.key),
        )
        return _ExpansionResult(
            text=_indent_text(
                _restore_text_bindings(expanded.text, protected_text),
                indent,
            ),
            includes=expanded.includes,
        )

    def _bind_macro_arguments(
        self,
        macro: WeaveMarkDefinition,
        rest: str,
        body: str,
        caller_env: DefinitionEnvironment,
        base_dir: Path,
        include_stack: tuple[str, ...] = (),
        expansion_stack: tuple[str, ...] = (),
    ) -> dict[str, str] | None:
        parsed_args = parse_header_args(rest)
        if parsed_args.errors:
            self.errors.extend(f"@{macro.name}: {error}" for error in parsed_args.errors)
            return None
        positional, options = parsed_args.positional, parsed_args.options
        params_by_name = {param.name: param for param in macro.params}
        implicit = macro.implicit_param
        inline_params = [param for param in macro.params if param is not implicit]
        bindings: dict[str, str] = {}

        for key, value in options.items():
            if key not in params_by_name:
                self.errors.append(f"@{macro.name} got unknown argument '{key}'.")
                return None
            if params_by_name[key] is implicit:
                self.errors.append(
                    f"@{macro.name} argument '{key}' is the implicit body parameter; "
                    "pass it as an indented block."
                )
                return None
            bindings[key] = value

        available_positionals = [
            param for param in inline_params if param.name not in bindings
        ]
        if len(positional) > len(available_positionals) and len(
            available_positionals
        ) == 1:
            only_param = available_positionals[0]
            if only_param.mode in {"text", "path"}:
                positional = [" ".join(positional)]
        if len(positional) > len(available_positionals):
            self.errors.append(
                f"@{macro.name} got too many positional arguments "
                f"({len(positional)} for {len(available_positionals)} available)."
            )
            return None
        for param, value in zip(available_positionals, positional, strict=False):
            bindings[param.name] = value

        if implicit is not None and not body.strip():
            if implicit.default is None:
                self.errors.append(
                    f"@{macro.name} missing required non-empty implicit "
                    f"body '{implicit.name}'."
                )
                return None
            bindings[implicit.name] = implicit.default
        elif implicit is not None and implicit.mode == "subspec":
            body_expansion = self._expand_source(
                body,
                caller_env,
                base_dir,
                include_stack=include_stack,
                expansion_stack=expansion_stack,
            )
            bindings[implicit.name] = body_expansion.text
        elif implicit is not None:
            bindings[implicit.name] = body
        elif body.strip():
            self.errors.append(f"@{macro.name} does not accept an indented body.")
            return None

        for param in macro.params:
            if param.name in bindings:
                continue
            if param.default is not None:
                bindings[param.name] = param.default
                continue
            self.errors.append(
                f"@{macro.name} missing required argument '{param.name}'."
            )
            return None

        return bindings

    def _validate_macro_cycles(self, macros: dict[str, WeaveMarkDefinition]) -> None:
        graph: dict[str, set[str]] = {}
        definitions = {macro.key: macro for macro in macros.values()}

        for macro in definitions.values():
            closure_macros = macro.closure.macros if macro.closure else macros
            edges: set[str] = set()
            for directive_name in _directive_names_in_source(macro.body):
                target = closure_macros.get(directive_name)
                if target is not None:
                    edges.add(target.key)
            graph[macro.key] = edges

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str, path: list[str]) -> None:
            if node in visited:
                return
            if node in visiting:
                cycle_start = path.index(node)
                cycle = " -> ".join([*path[cycle_start:], node])
                self.errors.append(f"Cycle detected in @define graph: {cycle}.")
                return
            visiting.add(node)
            for target in graph.get(node, set()):
                visit(target, [*path, target])
            visiting.remove(node)
            visited.add(node)

        for key in graph:
            visit(key, [key])


def _parse_document(text: str, source: str) -> ParsedDocument:
    comment_result = strip_markdown_comments(text, source_name=source)
    text = comment_result.text
    lines = text.splitlines()
    body_lines: list[str] = []
    uses: list[UseDirective] = []
    definitions: list[WeaveMarkDefinition] = []
    module_name: str | None = None
    errors = list(comment_result.errors)
    index = 0

    while index < len(lines):
        line = lines[index]
        match = _DIRECTIVE_RE.match(line)
        is_top_level = match is not None and not match.group("indent")
        if not is_top_level:
            body_lines.append(line)
            index += 1
            continue

        assert match is not None
        directive_name = match.group("name")
        rest = match.group("rest").strip()

        if directive_name == "module":
            _remove_trailing_blank_lines(body_lines)
            positional, options = _parse_arg_list(rest)
            if (
                options
                or len(positional) != 1
                or not _MODULE_RE.fullmatch(positional[0])
            ):
                errors.append("@module requires one dotted module name.")
            elif module_name is not None:
                errors.append("A WeaveMark file may declare only one @module.")
            else:
                module_name = positional[0]
            index += 1
            index = _skip_metadata_gap(lines, index, body_lines)
            continue

        if directive_name == "use":
            _remove_trailing_blank_lines(body_lines)
            use = _parse_use_directive(rest)
            if isinstance(use, str):
                errors.append(use)
            else:
                uses.append(use)
            index += 1
            index = _skip_metadata_gap(lines, index, body_lines)
            continue

        if directive_name == "define":
            _remove_trailing_blank_lines(body_lines)
            block, index = _collect_indented_block(lines, index + 1, 0)
            definition = _parse_define_directive(line, block, source)
            if isinstance(definition, str):
                errors.append(definition)
            else:
                definitions.append(definition)
            index = _skip_metadata_gap(lines, index, body_lines)
            continue

        body_lines.append(line)
        index += 1

    return ParsedDocument(
        module_name=module_name,
        uses=uses,
        definitions=definitions,
        body="\n".join(body_lines).strip("\n"),
        errors=errors,
    )


def _top_level_binding_names(body: str) -> set[str]:
    """Return local capability names that explicitly override module defaults."""

    names: set[str] = set()
    for line in body.splitlines():
        match = _DIRECTIVE_RE.match(line)
        if match is None or match.group("indent") or match.group("name") != "bind":
            continue
        parsed = parse_header_args(match.group("rest").strip(), allow_equals=True)
        if not parsed.errors and len(parsed.positional) == 1:
            names.add(parsed.positional[0])
    return names


def _extract_module_default_bindings(
    body: str,
    module_name: str,
    base_dir: Path,
    errors: list[str],
) -> tuple[str, tuple[ModuleBinding, ...]]:
    """Remove and validate top-level default ``@bind`` declarations."""

    body_lines: list[str] = []
    bindings: dict[str, ModuleBinding] = {}
    required = {"language", "from", "symbol"}
    for line in body.splitlines():
        match = _DIRECTIVE_RE.match(line)
        if match is None or match.group("indent") or match.group("name") != "bind":
            body_lines.append(line)
            continue

        parsed = parse_header_args(match.group("rest").strip(), allow_equals=True)
        if parsed.errors:
            errors.extend(
                f"Module {module_name} @bind: {error}" for error in parsed.errors
            )
            continue
        if len(parsed.positional) != 1:
            errors.append(
                f"Module {module_name} @bind requires exactly one capability name."
            )
            continue
        capability = parsed.positional[0]
        if not _IDENT_RE.fullmatch(capability):
            errors.append(
                f"Module {module_name} @bind capability is invalid: {capability}"
            )
            continue

        missing = sorted(required - set(parsed.options))
        unsupported = sorted(set(parsed.options) - required)
        if missing:
            errors.append(
                f"Module {module_name} @bind missing required parameter(s): "
                + ", ".join(missing)
                + "."
            )
        if unsupported:
            errors.append(
                f"Module {module_name} @bind has unsupported parameter(s): "
                + ", ".join(unsupported)
                + "."
            )
        if missing or unsupported:
            continue

        language = parsed.options["language"].strip()
        source = parsed.options["from"].strip()
        symbol = parsed.options["symbol"].strip()
        if not re.fullmatch(r"[A-Za-z_][\w-]*", language):
            errors.append(
                f"Module {module_name} @bind language is invalid: {language}"
            )
            continue
        if not _IDENT_RE.fullmatch(symbol):
            errors.append(f"Module {module_name} @bind symbol is invalid: {symbol}")
            continue

        source_path = Path(source)
        if (
            not source
            or source == "."
            or source_path.is_absolute()
            or ".." in source_path.parts
            or source.endswith(("/", "\\"))
        ):
            errors.append(
                f"Module {module_name} @bind source must stay inside the module: "
                f"{source}"
            )
            continue
        resolved = (base_dir / source_path).resolve()
        try:
            resolved.relative_to(base_dir.resolve())
        except ValueError:
            errors.append(
                f"Module {module_name} @bind source escapes the module: {source}"
            )
            continue
        if not resolved.is_file():
            errors.append(
                f"Module {module_name} @bind source was not found: {source}"
            )
            continue
        if capability in bindings:
            errors.append(
                f"Module {module_name} has duplicate default @bind for "
                f"capability: {capability}"
            )
            continue
        bindings[capability] = ModuleBinding(
            name=capability,
            language=language,
            source=source,
            symbol=symbol,
            module_name=module_name,
        )

    return "\n".join(body_lines).strip("\n"), tuple(bindings.values())


def _strip_promplet_declaration(text: str) -> str:
    """Remove a module file's leading ``@promplet`` metadata from its body."""
    lines = text.splitlines()
    if not lines or not lines[0].startswith("@promplet "):
        return text
    index = 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    return "\n".join(lines[index:])


def _parse_use_directive(rest: str) -> UseDirective | str:
    tokens = _split_tokens(rest)
    if not tokens:
        return "@use requires a module name."
    module_name = tokens[0]
    if not _MODULE_RE.fullmatch(module_name):
        return f"@use module name is invalid: {module_name}"

    alias: str | None = None
    exposing: list[str] = []
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "as":
            if alias is not None:
                return "@use may declare only one alias."
            if index + 1 >= len(tokens):
                return "@use as requires an alias."
            alias = tokens[index + 1]
            if not _IDENT_RE.fullmatch(alias):
                return f"@use alias is invalid: {alias}"
            index += 2
            continue
        if token == "exposing":
            if exposing:
                return "@use may declare only one exposing clause."
            index += 1
            exposed_tokens: list[str] = []
            while index < len(tokens) and tokens[index] not in {
                "as",
                "exposing",
                "bindings:",
            }:
                exposed_tokens.append(tokens[index])
                index += 1
            exposing = [
                item.strip()
                for item in " ".join(exposed_tokens).replace(",", " ").split()
                if item.strip()
            ]
            if not exposing:
                return "@use exposing requires at least one macro name."
            invalid = [name for name in exposing if not _IDENT_RE.fullmatch(name)]
            if invalid:
                return f"@use exposing has invalid macro name(s): {', '.join(invalid)}"
            continue
        if token == "bindings:":
            return (
                "@use bindings: is not supported; module default bindings are "
                "selected automatically."
            )
        return f"Unexpected @use token: {token}"

    return UseDirective(
        module_name=module_name,
        alias=alias,
        exposing=tuple(exposing),
    )


def _default_import_to_use(default_import: DefaultModuleImport) -> UseDirective:
    exposing = default_import.exposing or ()
    return UseDirective(
        module_name=default_import.name,
        alias=default_import.alias,
        exposing=exposing,
        expose_all=default_import.exposing is None,
    )


def _remove_trailing_blank_lines(lines: list[str]) -> None:
    while lines and not lines[-1].strip():
        lines.pop()


def _skip_metadata_gap(lines: list[str], index: int, body_lines: list[str]) -> int:
    while index < len(lines) and not lines[index].strip():
        index += 1
    if body_lines and index < len(lines):
        body_lines.append("")
    return index


def _parse_define_directive(
    line: str,
    block: str,
    source: str,
) -> WeaveMarkDefinition | str:
    match = _DEFINE_RE.match(line)
    if match is None:
        return "@define syntax must be @define name(...) or @define name."
    name = match.group("name")
    signature = match.group("signature")
    if name in _CORE_PRIMITIVES:
        return f"@define cannot override core primitive @{name}."

    if signature is not None:
        params = _parse_compact_signature(signature)
        if isinstance(params, str):
            return params
        return WeaveMarkDefinition(name=name, params=params, body=block, source=source)

    parsed = _parse_long_define_body(name, block, source)
    return parsed


def _parse_compact_signature(signature: str) -> list[DefinitionParam] | str:
    if not signature.strip():
        return []
    params: list[DefinitionParam] = []
    seen: set[str] = set()
    for part in _split_signature_params(signature):
        name, sep, description = part.partition(":")
        name = name.strip()
        if sep != ":" or not name or not _IDENT_RE.fullmatch(name):
            return f"Invalid @define parameter signature: {part!r}"
        if name in seen:
            return f"Duplicate @define parameter: {name}"
        seen.add(name)
        params.append(
            DefinitionParam(
                name=name,
                description=description.strip(),
                implicit=name == "body",
                mode="subspec" if name == "body" else "text",
            )
        )
    return params


def _parse_long_define_body(
    macro_name: str,
    block: str,
    source: str,
) -> WeaveMarkDefinition | str:
    lines = block.splitlines()
    params: list[DefinitionParam] = []
    effects: list[SemanticEffect] = []
    body: str | None = None
    phase: str | None = None
    scope: str | None = None
    returns: str | None = None
    seen: set[str] = set()
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        match = _DIRECTIVE_RE.match(line)
        if match is None or match.group("indent"):
            return f"Unexpected content in long @define {macro_name}; expected @param or @body."

        directive_name = match.group("name")
        rest = match.group("rest").strip()
        if directive_name == "param":
            description, index = _collect_indented_block(lines, index + 1, 0)
            param = _parse_param_directive(rest, description)
            if isinstance(param, str):
                return param
            if param.name in seen:
                return f"Duplicate @param in @define {macro_name}: {param.name}"
            seen.add(param.name)
            params.append(param)
            continue

        if directive_name == "phase":
            if phase is not None:
                return f"@define {macro_name} may contain only one @phase."
            positional, options = _parse_arg_list(rest)
            if options or len(positional) != 1:
                return f"@phase in @define {macro_name} requires compile or execute."
            phase = positional[0]
            if phase not in _SEMANTIC_PHASES:
                return (
                    f"@phase in @define {macro_name} must be compile or execute; "
                    f"got {phase}."
                )
            index += 1
            continue

        if directive_name == "scope":
            if scope is not None:
                return f"@define {macro_name} may contain only one @scope."
            positional, options = _parse_arg_list(rest)
            if options or len(positional) != 1:
                return f"@scope in @define {macro_name} requires one scope name."
            scope = positional[0]
            if scope not in _SEMANTIC_SCOPES:
                return (
                    f"@scope in @define {macro_name} must be one of "
                    f"{', '.join(sorted(_SEMANTIC_SCOPES))}; got {scope}."
                )
            index += 1
            continue

        if directive_name == "returns":
            if returns is not None:
                return f"@define {macro_name} may contain only one @returns."
            positional, options = _parse_arg_list(rest)
            if options or len(positional) != 1:
                return f"@returns in @define {macro_name} requires one return kind."
            returns = positional[0]
            if not _IDENT_RE.fullmatch(returns):
                return f"@returns in @define {macro_name} is invalid: {returns}"
            index += 1
            continue

        if directive_name == "effect":
            effect = _parse_effect_directive(rest)
            if isinstance(effect, str):
                return effect
            effects.append(effect)
            index += 1
            continue

        if directive_name == "body":
            if body is not None:
                return f"@define {macro_name} may contain only one @body block."
            body, index = _collect_indented_block(lines, index + 1, 0)
            continue

        return f"Unexpected @{directive_name} in long @define {macro_name}."

    if body is None:
        return f"Long-form @define {macro_name} requires an @body block."

    implicit_params = [param.name for param in params if param.implicit]
    if len(implicit_params) > 1:
        return (
            f"@define {macro_name} may have only one implicit body parameter; "
            f"got {', '.join(implicit_params)}."
        )

    has_semantic_metadata = bool(effects) or any(
        item is not None for item in (phase, scope, returns)
    )
    if has_semantic_metadata and not effects:
        return f"Semantic @define {macro_name} requires at least one @effect."
    if effects and phase is None:
        return (
            f"Semantic @define {macro_name} requires @phase compile or @phase execute."
        )
    if effects and returns is None:
        return f"Semantic @define {macro_name} requires @returns."

    return WeaveMarkDefinition(
        name=macro_name,
        params=params,
        body=body,
        source=source,
        phase=phase,
        scope=scope or ("self" if effects else None),
        returns=returns,
        effects=effects,
    )


def _parse_effect_directive(rest: str) -> SemanticEffect | str:
    positional, options = _parse_arg_list(rest)
    if options or not 1 <= len(positional) <= 2:
        return "@effect requires an effect name and optional read/write mode."
    name = positional[0]
    if not _IDENT_RE.fullmatch(name):
        return f"@effect name is invalid: {name}"
    mode = positional[1] if len(positional) == 2 else "read"
    if mode not in _SEMANTIC_EFFECT_MODES:
        return f"@effect {name} mode must be read or write; got {mode}."
    return SemanticEffect(name=name, mode=mode)


def _parse_param_directive(rest: str, description: str) -> DefinitionParam | str:
    positional, options = _parse_arg_list(rest)
    if len(positional) != 1:
        return "@param requires exactly one parameter name."
    name = positional[0]
    if not _IDENT_RE.fullmatch(name):
        return f"@param name is invalid: {name}"

    implicit = options.get("implicit", "false").lower() in {"true", "yes", "1", "on"}
    mode = options.get("mode", "text")
    default = options.get("default")
    allowed = {"default", "implicit", "mode"}
    unsupported = sorted(set(options) - allowed)
    if unsupported:
        return f"@param {name} has unsupported option(s): {', '.join(unsupported)}"
    if mode not in _PARAM_MODES:
        return f"@param {name} mode must be text, subspec, path, or promplet."

    return DefinitionParam(
        name=name,
        description=description,
        default=default,
        implicit=implicit,
        mode=mode,
    )


def _parse_arg_list(rest: str) -> tuple[list[str], dict[str, str]]:
    parsed = parse_header_args(rest, allow_equals=True)
    return parsed.positional, parsed.options


def _split_tokens(text: str) -> list[str]:
    try:
        return shlex.split(text.strip())
    except ValueError:
        return text.strip().split()


def _split_signature_params(signature: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_string = False
    escape = False
    for char in signature:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\" and in_string:
            current.append(char)
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            current.append(char)
            continue
        if char == "," and not in_string:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(char)
    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


def _collect_indented_block(
    lines: list[str],
    start: int,
    parent_indent: int,
) -> tuple[str, int]:
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
            if (
                next_nonblank is None
                or _indent_width(lines[next_nonblank]) <= parent_indent
            ):
                break
            block.append(line)
            index += 1
            continue
        if _indent_width(line) <= parent_indent:
            break
        block.append(line)
        index += 1
    return _dedent_block(block), index


def _dedent_block(lines: list[str]) -> str:
    return textwrap.dedent("\n".join(lines)).strip("\n")


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _indent_text(text: str, indent: str) -> str:
    if not indent or not text:
        return text
    return "\n".join(f"{indent}{line}" if line else line for line in text.splitlines())


def _substitute_macro_params(text: str, bindings: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in bindings:
            return match.group(0)
        return bindings[name]

    return _VARIABLE_RE.sub(replace, text)


def _protect_text_bindings(
    macro: WeaveMarkDefinition,
    bindings: dict[str, str],
) -> tuple[dict[str, str], dict[str, str]]:
    protected: dict[str, str] = {}
    text_bindings: dict[str, str] = {}
    params_by_name = {param.name: param for param in macro.params}

    for name, value in bindings.items():
        param = params_by_name[name]
        if param.mode not in {"text", "path", "promplet"}:
            protected[name] = value
            continue
        token = f"\x00WEAVEMARK_TEXT_BINDING_{len(text_bindings)}\x00"
        protected[name] = token
        text_bindings[token] = value

    return protected, text_bindings


def _restore_text_bindings(text: str, bindings: dict[str, str]) -> str:
    for token, value in bindings.items():
        text = text.replace(token, value)
    return text


def _directive_names_in_source(source: str) -> list[str]:
    names: list[str] = []
    for line in source.splitlines():
        match = _DIRECTIVE_RE.match(line)
        if match is not None:
            names.append(match.group("name"))
    return names


def _read_module_source(
    module_name: str,
    importer_base_dir: Path,
) -> tuple[str, str, Path] | None:
    source = resolve_module_source(module_name, cwd=importer_base_dir)
    return source.text, str(source.path), source.path.parent
