"""Public Python API for compiling and executing WeaveMark programs."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from ellements.core import LLMClientProtocol
from ellements.execution import OnStepCallback

from weavemark.compilation.ask import AskPrompt
from weavemark.compilation.provenance import ProvenanceOptions
from weavemark.compilation.result import CompositionResult
from weavemark.compile_options import (
    DEFAULT_COMPILE_FORMAT,
    normalize_compile_format,
    supported_compile_formats_text,
)
from weavemark.controller import (
    WeaveMarkConfig,
    WeaveMarkController,
)
from weavemark.defaults import DEFAULT_MODEL
from weavemark.engines import (
    ArtifactCallback,
    Engine,
    ExecutionResult,
    RuntimeConfig,
    call_engine_execute,
    resolve_engine,
)
from weavemark.logging_setup import new_client
from weavemark.protection import ProtectionContext
from weavemark.settings import (
    WeaveMarkSettings,
    builtin_weavemark_settings,
    load_weavemark_settings,
)

PathLike: TypeAlias = str | Path
EventCallback: TypeAlias = Callable[[str, dict[str, Any]], None]
AskCallback: TypeAlias = Callable[[AskPrompt], str | Awaitable[str]]
RuntimeConfigInput: TypeAlias = RuntimeConfig | Mapping[str, Any] | PathLike | None
EngineInput: TypeAlias = str | Engine | None


@dataclass(frozen=True)
class CompileOptions:
    """Options for WeaveMark compilation.

    WeaveMark compilation is async because semantic directives may need an LLM
    reference compiler when deterministic structural helpers cannot resolve the
    full program.
    """

    model: str = DEFAULT_MODEL
    temperature: float = 0.3
    max_iterations: int = 15
    use_structural_helpers: bool = True
    max_effect_rounds: int = 6
    max_effect_questions: int = 20
    max_iterate_turns: int = 6
    max_compilation_steps: int = 64
    max_total_model_calls: int = 100
    max_compile_seconds: float = 300.0

    def to_controller_config(self) -> WeaveMarkConfig:
        """Convert public compile options to controller configuration."""

        return WeaveMarkConfig(
            model=self.model,
            temperature=self.temperature,
            max_iterations=self.max_iterations,
            use_structural_helpers=self.use_structural_helpers,
            max_effect_rounds=self.max_effect_rounds,
            max_effect_questions=self.max_effect_questions,
            max_iterate_turns=self.max_iterate_turns,
            max_compilation_steps=self.max_compilation_steps,
            max_total_model_calls=self.max_total_model_calls,
            max_compile_seconds=self.max_compile_seconds,
        )


@dataclass(frozen=True)
class WeaveMarkRunResult:
    """Result returned by ``execute_text`` and ``execute_file``."""

    compiled: CompositionResult
    execution: ExecutionResult
    engine: str
    runtime_config: RuntimeConfig | None = None

    @property
    def output(self) -> str:
        """Primary text output produced by the execution engine."""

        return str(self.execution.output)


class WeaveMarkError(Exception):
    """Base exception raised by the public WeaveMark library API."""


class WeaveMarkCompilationError(WeaveMarkError):
    """Raised when execution is requested for a spec that did not compile."""

    def __init__(self, result: CompositionResult) -> None:
        self.result = result
        message = "WeaveMark compilation failed"
        if result.errors:
            message += ": " + "; ".join(result.errors)
        super().__init__(message)


async def compile_text(
    spec_text: str,
    variables: Mapping[str, Any] | None = None,
    *,
    base_dir: PathLike | None = None,
    options: CompileOptions | None = None,
    on_event: EventCallback | None = None,
    ask_handler: AskCallback | None = None,
    client: LLMClientProtocol | None = None,
    protection_context: ProtectionContext | None = None,
    provenance: ProvenanceOptions | None = None,
    source_path: PathLike | None = None,
) -> CompositionResult:
    """Compile WeaveMark source text into prompt artifacts.

    Args:
        spec_text: WeaveMark source text.
        variables: Values used for ``@{variable}`` substitution.
        base_dir: Directory used for relative file references, module lookup,
            and project-level ``weavemark.json`` discovery. Defaults to the
            current working directory.
        options: Compiler/model settings. Defaults match the CLI.
        on_event: Optional callback receiving controller events such as
            ``"composing"``, ``"transition"``, ``"issue"``, and ``"done"``.
        ask_handler: Optional callback used by standard-library ``@ask`` to
            collect compile-time answers.
        client: Optional ``ellements`` LLM client for advanced integrations.
        provenance: Optional manifest, run-recording, or strict replay settings.
        source_path: Optional source identity for provenance when compiling text.

    Returns:
        A ``CompositionResult`` containing the composed prompt, named prompts,
        emitted artifacts, tool schemas, bindings, execution metadata, and
        diagnostics.
    """

    resolved_options = options or CompileOptions()
    root = _resolve_base_dir(base_dir)
    controller = WeaveMarkController(
        resolved_options.to_controller_config(),
        client=client,
    )
    return await controller.compose(
        spec_text,
        dict(variables or {}),
        root,
        on_event=on_event,
        ask_handler=ask_handler,
        protection=protection_context,
        provenance=provenance,
        source_path=Path(source_path).expanduser().resolve() if source_path else None,
    )


async def compile_file(
    promplet_file: PathLike,
    variables: Mapping[str, Any] | None = None,
    *,
    options: CompileOptions | None = None,
    on_event: EventCallback | None = None,
    ask_handler: AskCallback | None = None,
    client: LLMClientProtocol | None = None,
    protection_context: ProtectionContext | None = None,
    provenance: ProvenanceOptions | None = None,
) -> CompositionResult:
    """Compile a WeaveMark file from disk.

    The promplet's parent directory becomes the base directory for relative
    ``@refine`` / ``@embed`` paths, effective-library module resolution, and
    project ``weavemark.json`` settings.
    """

    promplet_path = _resolve_file(promplet_file)
    return await compile_text(
        promplet_path.read_text(encoding="utf-8"),
        variables,
        base_dir=promplet_path.parent,
        options=options,
        on_event=on_event,
        ask_handler=ask_handler,
        client=client,
        protection_context=protection_context,
        provenance=provenance,
        source_path=promplet_path,
    )


async def execute_text(
    spec_text: str,
    variables: Mapping[str, Any] | None = None,
    *,
    base_dir: PathLike | None = None,
    options: CompileOptions | None = None,
    runtime_config: RuntimeConfigInput = None,
    engine: EngineInput = None,
    on_event: EventCallback | None = None,
    ask_handler: AskCallback | None = None,
    on_step: OnStepCallback | None = None,
    on_artifact: ArtifactCallback | None = None,
    client: LLMClientProtocol | None = None,
    protection_context: ProtectionContext | None = None,
    provenance: ProvenanceOptions | None = None,
    source_path: PathLike | None = None,
) -> WeaveMarkRunResult:
    """Compile WeaveMark source text, then execute it with an engine.

    Runtime config variables are applied before compilation; explicit
    ``variables`` override runtime config variables, matching the CLI.

    ``on_artifact`` receives each ``@output file:`` artifact record the moment an
    engine produces it (e.g. one per rendered page), enabling streaming
    persistence rather than only writing everything after the whole run finishes.
    """

    resolved_runtime_config = load_runtime_config(runtime_config)
    effective_options = options or CompileOptions()
    if resolved_runtime_config is None:
        resolved_runtime_config = RuntimeConfig(model=effective_options.model)
    elif resolved_runtime_config.model is None:
        resolved_runtime_config.model = effective_options.model
    merged_variables = _merge_runtime_variables(resolved_runtime_config, variables)
    compiled = await compile_text(
        spec_text,
        merged_variables,
        base_dir=base_dir,
        options=effective_options,
        on_event=on_event,
        ask_handler=ask_handler,
        client=client,
        protection_context=protection_context,
        provenance=provenance,
        source_path=source_path,
    )
    if compiled.errors:
        raise WeaveMarkCompilationError(compiled)
    resolved_runtime_config.protection = compiled.protection

    resolved_engine, engine_name = _resolve_execution_engine(
        engine,
        resolved_runtime_config,
        compiled,
        client
        or new_client(
            model=resolved_runtime_config.model or effective_options.model,
            protection=compiled.protection,
            logging_settings=load_weavemark_settings(
                _resolve_base_dir(base_dir)
            ).settings.logging,
        ),
    )
    execution = await call_engine_execute(
        resolved_engine,
        compiled,
        resolved_runtime_config,
        on_step=on_step,
        on_artifact=on_artifact,
    )
    return WeaveMarkRunResult(
        compiled=compiled,
        execution=execution,
        engine=engine_name,
        runtime_config=resolved_runtime_config,
    )


async def execute_file(
    promplet_file: PathLike,
    variables: Mapping[str, Any] | None = None,
    *,
    options: CompileOptions | None = None,
    runtime_config: RuntimeConfigInput = None,
    engine: EngineInput = None,
    on_event: EventCallback | None = None,
    ask_handler: AskCallback | None = None,
    on_step: OnStepCallback | None = None,
    on_artifact: ArtifactCallback | None = None,
    client: LLMClientProtocol | None = None,
    protection_context: ProtectionContext | None = None,
    provenance: ProvenanceOptions | None = None,
) -> WeaveMarkRunResult:
    """Compile a WeaveMark file, then execute it with an engine."""

    promplet_path = _resolve_file(promplet_file)
    return await execute_text(
        promplet_path.read_text(encoding="utf-8"),
        variables,
        base_dir=promplet_path.parent,
        options=options,
        runtime_config=runtime_config,
        engine=engine,
        on_event=on_event,
        ask_handler=ask_handler,
        on_step=on_step,
        on_artifact=on_artifact,
        client=client,
        protection_context=protection_context,
        provenance=provenance,
        source_path=promplet_path,
    )


def load_runtime_config(config: RuntimeConfigInput) -> RuntimeConfig | None:
    """Load runtime engine config from an object, mapping, JSON file, or YAML file."""

    if config is None:
        return None
    if isinstance(config, RuntimeConfig):
        return config
    if isinstance(config, str | Path):
        path = _resolve_file(config)
        if path.suffix in (".yaml", ".yml"):
            return RuntimeConfig.from_yaml(path)
        return RuntimeConfig.from_json(path)
    return _runtime_config_from_mapping(config)


def format_compiled_output(
    result: CompositionResult,
    output_format: str | None = None,
    *,
    base_dir: PathLike | None = None,
    settings: WeaveMarkSettings | None = None,
) -> str:
    """Render a compiled result the same way the CLI renders primary output.

    ``markdown`` returns ``result.composed_prompt`` and ``json`` returns structured
    result JSON. Custom format identifiers and aliases are resolved through
    ``weavemark.json`` settings when ``base_dir`` or ``settings`` is supplied.
    """

    resolved_settings = _resolve_settings(base_dir, settings)
    raw_format = output_format
    if raw_format is None and result.compile:
        compile_format = result.compile.get("format")
        raw_format = str(compile_format) if compile_format is not None else None
    raw_format = raw_format or DEFAULT_COMPILE_FORMAT

    normalized = normalize_compile_format(raw_format, resolved_settings)
    if normalized is None:
        raise ValueError(
            f"Unsupported output format: {raw_format}. "
            f"Supported formats: {supported_compile_formats_text(resolved_settings)}."
        )

    if normalized == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    return str(result.composed_prompt)


def _resolve_base_dir(base_dir: PathLike | None) -> Path:
    if base_dir is None:
        return Path.cwd()
    return Path(base_dir).expanduser().resolve()


def _resolve_file(path: PathLike) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return resolved


def _resolve_settings(
    base_dir: PathLike | None,
    settings: WeaveMarkSettings | None,
) -> WeaveMarkSettings:
    if settings is not None:
        return settings
    if base_dir is None:
        return builtin_weavemark_settings()
    return load_weavemark_settings(Path(base_dir).expanduser().resolve()).settings


def _merge_runtime_variables(
    runtime_config: RuntimeConfig | None,
    variables: Mapping[str, Any] | None,
) -> dict[str, Any]:
    merged = dict(runtime_config.variables) if runtime_config else {}
    merged.update(dict(variables or {}))
    return merged


def _resolve_execution_engine(
    engine: EngineInput,
    runtime_config: RuntimeConfig | None,
    compiled: CompositionResult,
    client: LLMClientProtocol | None,
) -> tuple[Engine, str]:
    if engine is None:
        engine_name = _engine_name_from_result(runtime_config, compiled)
        return (
            resolve_engine(
                engine_name,
                client=client,
                protection=runtime_config.protection if runtime_config else None,
            ),
            engine_name,
        )
    if isinstance(engine, str):
        return (
            resolve_engine(
                engine,
                client=client,
                protection=runtime_config.protection if runtime_config else None,
            ),
            engine,
        )
    return engine, engine.__class__.__name__


def _engine_name_from_result(
    runtime_config: RuntimeConfig | None,
    compiled: CompositionResult,
) -> str:
    if runtime_config is not None and runtime_config.engine:
        return str(runtime_config.engine)
    declared = compiled.execution.get("type") if compiled.execution else None
    if isinstance(declared, str) and declared:
        return declared
    return "single-call"


def _runtime_config_from_mapping(data: Mapping[str, Any]) -> RuntimeConfig:
    return RuntimeConfig.from_mapping(data)


__all__ = [
    "CompileOptions",
    "EngineInput",
    "EventCallback",
    "PathLike",
    "WeaveMarkCompilationError",
    "WeaveMarkError",
    "WeaveMarkRunResult",
    "RuntimeConfigInput",
    "compile_file",
    "compile_text",
    "execute_file",
    "execute_text",
    "format_compiled_output",
    "load_runtime_config",
]
