"""WeaveMark public Python library API."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

from weavemark.version import LANGUAGE_VERSION, __version__

if TYPE_CHECKING:
    from weavemark.api import (
        AskCallback,
        CompileOptions,
        EngineInput,
        EventCallback,
        PathLike,
        RuntimeConfigInput,
        WeaveMarkCompilationError,
        WeaveMarkError,
        WeaveMarkRunResult,
        compile_file,
        compile_text,
        execute_file,
        execute_text,
        format_compiled_output,
        load_runtime_config,
    )
    from weavemark.compilation.ask import AskPrompt
    from weavemark.compilation.diagnostics import Diagnostic
    from weavemark.compilation.provenance import (
        ProvenanceManifest,
        ProvenanceOptions,
        ReplayMismatchError,
    )
    from weavemark.compilation.result import CompositionResult
    from weavemark.compilation.trace import (
        CompilationStep,
        CompilationTrace,
        DirectiveApplication,
        SourceSpan,
        StepJudgment,
    )
    from weavemark.engines import Engine, ExecutionResult, PromptConfig, RuntimeConfig
    from weavemark.promplet_library import (
        bundled_promplet,
        bundled_promplet_path,
        bundled_promplets,
        bundled_promplets_path,
        iter_bundled_promplets,
        read_bundled_promplet,
    )

_LAZY_EXPORTS = {
    "AskCallback": ("weavemark.api", "AskCallback"),
    "AskPrompt": ("weavemark.compilation.ask", "AskPrompt"),
    "CompilationStep": ("weavemark.compilation.trace", "CompilationStep"),
    "CompilationTrace": ("weavemark.compilation.trace", "CompilationTrace"),
    "CompileOptions": ("weavemark.api", "CompileOptions"),
    "CompositionResult": ("weavemark.compilation.result", "CompositionResult"),
    "Diagnostic": ("weavemark.compilation.diagnostics", "Diagnostic"),
    "DirectiveApplication": (
        "weavemark.compilation.trace",
        "DirectiveApplication",
    ),
    "Engine": ("weavemark.engines", "Engine"),
    "EngineInput": ("weavemark.api", "EngineInput"),
    "EventCallback": ("weavemark.api", "EventCallback"),
    "ExecutionResult": ("weavemark.engines", "ExecutionResult"),
    "PathLike": ("weavemark.api", "PathLike"),
    "PromptConfig": ("weavemark.engines", "PromptConfig"),
    "ProvenanceManifest": (
        "weavemark.compilation.provenance",
        "ProvenanceManifest",
    ),
    "ProvenanceOptions": ("weavemark.compilation.provenance", "ProvenanceOptions"),
    "ReplayMismatchError": (
        "weavemark.compilation.provenance",
        "ReplayMismatchError",
    ),
    "RuntimeConfig": ("weavemark.engines", "RuntimeConfig"),
    "RuntimeConfigInput": ("weavemark.api", "RuntimeConfigInput"),
    "SourceSpan": ("weavemark.compilation.trace", "SourceSpan"),
    "StepJudgment": ("weavemark.compilation.trace", "StepJudgment"),
    "WeaveMarkCompilationError": (
        "weavemark.exceptions",
        "WeaveMarkCompilationError",
    ),
    "WeaveMarkError": ("weavemark.exceptions", "WeaveMarkError"),
    "WeaveMarkRunResult": ("weavemark.api", "WeaveMarkRunResult"),
    "bundled_promplet": ("weavemark.promplet_library", "bundled_promplet"),
    "bundled_promplet_path": (
        "weavemark.promplet_library",
        "bundled_promplet_path",
    ),
    "bundled_promplets": ("weavemark.promplet_library", "bundled_promplets"),
    "bundled_promplets_path": (
        "weavemark.promplet_library",
        "bundled_promplets_path",
    ),
    "compile_file": ("weavemark.api", "compile_file"),
    "compile_text": ("weavemark.api", "compile_text"),
    "execute_file": ("weavemark.api", "execute_file"),
    "execute_text": ("weavemark.api", "execute_text"),
    "format_compiled_output": ("weavemark.api", "format_compiled_output"),
    "iter_bundled_promplets": (
        "weavemark.promplet_library",
        "iter_bundled_promplets",
    ),
    "load_runtime_config": ("weavemark.api", "load_runtime_config"),
    "read_bundled_promplet": (
        "weavemark.promplet_library",
        "read_bundled_promplet",
    ),
}


def __getattr__(name: str) -> Any:
    """Load an explicitly exported API symbol on first use."""

    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = target
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return eager and lazy public names for interactive discovery."""

    return sorted({*globals(), *_LAZY_EXPORTS})


__all__ = [
    "CompileOptions",
    "AskCallback",
    "AskPrompt",
    "CompilationStep",
    "CompilationTrace",
    "CompositionResult",
    "Diagnostic",
    "DirectiveApplication",
    "Engine",
    "EngineInput",
    "EventCallback",
    "ExecutionResult",
    "PathLike",
    "PromptConfig",
    "ProvenanceManifest",
    "ProvenanceOptions",
    "ReplayMismatchError",
    "WeaveMarkCompilationError",
    "WeaveMarkError",
    "WeaveMarkRunResult",
    "RuntimeConfig",
    "RuntimeConfigInput",
    "LANGUAGE_VERSION",
    "SourceSpan",
    "StepJudgment",
    "compile_file",
    "compile_text",
    "bundled_promplet",
    "bundled_promplet_path",
    "bundled_promplets",
    "bundled_promplets_path",
    "execute_file",
    "execute_text",
    "format_compiled_output",
    "iter_bundled_promplets",
    "load_runtime_config",
    "read_bundled_promplet",
    "__version__",
]
