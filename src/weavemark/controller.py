"""WeaveMark controller — orchestrates prompt composition via LLM tool calling."""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
import re
import textwrap
from collections.abc import Awaitable, Callable
from contextlib import suppress
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any

from ellements.core import LLMClientProtocol, MaxToolIterationsError, ToolCallResponse

from weavemark.compilation.ask import (
    AskPrompt,
    ask_history_for_prompt,
    composition_result_to_weavemark_text,
    find_ask_directives,
    format_ask_directives_for_prompt,
)
from weavemark.compilation.directive_registry import (
    CORE_DIRECTIVES,
    validate_directive_names,
)
from weavemark.compilation.iterate import (
    IterateAskPrelude,
    IterateDirective,
    find_iterate_directives,
    find_next_compilation_step,
    replace_applications,
    replace_iterate_directive,
    source_for_applications,
    spec_without_whole_iterate_directive,
    step_key,
)
from weavemark.compilation.macros import preprocess_weavemark, resolve_module_body
from weavemark.compilation.multimodal import (
    OutputContract,
    extract_image_refs,
)
from weavemark.compilation.provenance import (
    ProvenanceOptions,
    create_compilation_client,
    finalize_provenance,
    record_resource,
    validate_replay_context,
)
from weavemark.compilation.reference_artifacts import (
    format_reference_context,
    materialize_reference_appendices,
)
from weavemark.compilation.references import resolve_references
from weavemark.compilation.result import CompositionResult
from weavemark.compilation.result_schema import (
    CompilerProtocolError,
    compiler_response_format,
    parse_wire_result,
)
from weavemark.compilation.state import CompilationBudget, CompositionAccumulator
from weavemark.compilation.structural import (
    StructuralHelperResult,
    try_apply_structural_helpers,
)
from weavemark.compilation.trace import (
    CompilationStep,
    CompilationTrace,
    DirectiveApplication,
    StepJudgment,
    directives_from_json,
    directives_to_json,
)
from weavemark.compile_options import normalize_compile_format
from weavemark.defaults import DEFAULT_MODEL
from weavemark.fragments import (
    has_fragment_alias_prefix,
    is_explicit_file_reference,
    resolve_fragment_reference,
)
from weavemark.logging_setup import new_client
from weavemark.protection import ProtectionContext, ProtectionError
from weavemark.settings import (
    WeaveMarkSettings,
    builtin_weavemark_settings,
    load_weavemark_settings,
)
from weavemark.source_comments import strip_markdown_comments
from weavemark.surfaces import lower_weavemark_surface
from weavemark.version import LANGUAGE_VERSION

logger = logging.getLogger(__name__)

# Path to the system prompt shipped with the package
_SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parent / "prompts" / "weavemark.system.md"
)
_PROMPLET_VERSION_RE = re.compile(
    r"^[ \t]*@promplet\s+version:\s*(?P<version>[0-9]+\.[0-9]+)(?:\s|$)",
    re.MULTILINE,
)
_REFERENCE_LANGUAGE_VERSION = (0, 9)


def _language_version_tuple(value: str) -> tuple[int, int] | None:
    try:
        major, minor = value.split(".", 1)
        return int(major), int(minor)
    except (TypeError, ValueError):
        return None


def _reference_syntax_enabled(source: str) -> bool:
    uncommented = strip_markdown_comments(source).text
    first_line = next(
        (line for line in uncommented.splitlines() if line.strip()),
        "",
    )
    match = _PROMPLET_VERSION_RE.match(first_line)
    version = match.group("version") if match is not None else LANGUAGE_VERSION
    parsed = _language_version_tuple(version)
    return parsed is not None and parsed >= _REFERENCE_LANGUAGE_VERSION


# Tool definitions in OpenAI function-calling format
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the content of a file from the filesystem. You MUST "
                "call this exactly once for every imported `@refine <reference>` "
                "and `@embed file: <path>` directive "
                "that survives selection "
                "(i.e., that is not inside a discarded `@if`/`@match` "
                "branch). This rule holds REGARDLESS of how small or "
                "simple the spec looks. Skipping this call and emitting "
                "a placeholder like `(Content from X will be inserted "
                "here.)` is a composition bug. Rich document formats "
                "(PDF, DOCX, PPTX, XLSX) are automatically converted to "
                "Markdown."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": (
                            "Promplet reference to read. Use module:<dotted.name> for "
                            "a module body; explicit paths start with ./, ../, /, or ~/. "
                            "Fragment references use alias:path, or a bare path when "
                            "exactly one fragment alias is configured."
                        ),
                    },
                    "reference_id": {
                        "type": "string",
                        "description": (
                            "When the requested path appears inside host-supplied "
                            "Referenced Source Context, pass that context's Rn id so "
                            "relative paths resolve against the correct containing file."
                        ),
                    },
                },
                "required": ["file_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_transition",
            "description": (
                "Log a composition transition. You MUST call this "
                "exactly once after each iteration pass to record what "
                "changed and why — including for a tiny spec that "
                "completes in a single pass. Skipping this call "
                "because the spec looks trivial is a composition bug."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": (
                            "Free-form description of what changed and why. "
                            "If nothing changed, use 'no change' with a brief reason."
                        ),
                    }
                },
                "required": ["text"],
            },
        },
    },
]

ASK_USER_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "ask_user",
        "description": (
            "Ask the host user a compile-time question for an active @ask "
            "directive. Use this only when @ask is active and the answer will "
            "materially guide the remaining composition. Ask concrete, "
            "non-redundant questions. You may call this repeatedly before "
            "returning intermediate XML."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The exact question to ask the user.",
                },
                "question_type": {
                    "type": "string",
                    "description": (
                        "Question type requested by @ask, e.g. clarifying "
                        "question, tradeoff question, constraint question."
                    ),
                },
                "detail_level": {
                    "type": "string",
                    "description": "The active @ask detail level percentage.",
                },
                "scope": {
                    "type": "string",
                    "description": "Brief description of the body/scope being clarified.",
                },
                "reason": {
                    "type": "string",
                    "description": "Why this answer is needed before continuing.",
                },
            },
            "required": ["question"],
        },
    },
}

COMPILE_EFFECT_TOOLS: list[dict[str, Any]] = [ASK_USER_TOOL]

AskHandler = Callable[[AskPrompt], str | Awaitable[str]]


def _source_declares_reference(source: str, reference: str) -> bool:
    """Whether a parsed file-reading directive names *reference*."""

    normalized = reference.strip()
    if not normalized:
        return False
    stripped = strip_markdown_comments(source).text
    fence_marker: str | None = None
    opaque_indent: int | None = None
    for line in stripped.splitlines():
        content = line.lstrip()
        indent = len(line) - len(content)
        fence = re.match(r"^(`{3,}|~{3,})", content)
        if fence_marker is not None:
            if (
                fence is not None
                and fence.group(1)[0] == fence_marker[0]
                and len(fence.group(1)) >= len(fence_marker)
            ):
                fence_marker = None
            continue
        if fence is not None:
            fence_marker = fence.group(1)
            continue
        if opaque_indent is not None:
            if not content or indent > opaque_indent:
                continue
            opaque_indent = None

        refine = re.match(r"^@refine\s+(\"[^\"]+\"|'[^']+'|\S+)", content)
        embed = re.match(
            r"^@embed\b[^\n]*\bfile:\s*(\"[^\"]+\"|'[^']+'|\S+)",
            content,
        )
        match = refine or embed
        if match is not None and match.group(1).strip("\"'") == normalized:
            return True
        directive = re.match(r"^@([A-Za-z_][\w.-]*)\b", content)
        if directive is not None and directive.group(1) in {
            "embed",
            "execute",
            "note",
            "output",
            "package",
            "tool",
        }:
            opaque_indent = indent
    return False


def _format_variable_for_prompt(value: Any) -> str:
    """Format variable values clearly for the LLM composition path."""

    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def _format_semantic_definitions_for_prompt(definitions: dict[str, Any]) -> str:
    """Format imported semantic definitions for the LLM composition path."""

    if not definitions:
        return "No semantic definitions imported."
    lines: list[str] = []
    seen: set[tuple[str, str]] = set()
    for call_name, definition in sorted(definitions.items()):
        key = (definition.source, definition.name)
        if key in seen and call_name == definition.name:
            continue
        seen.add(key)
        effects = ", ".join(
            f"{effect.name}:{effect.mode}" for effect in definition.effects
        )
        params = ", ".join(
            f"{param.name}[mode={param.mode}]"
            + (" implicit" if param.implicit else "")
            + (f" default={param.default}" if param.default is not None else "")
            for param in definition.params
        )
        lines.append(
            f"- `@{call_name}` (definition `{definition.name}`, "
            f"phase: {definition.phase}, scope: {definition.scope}, "
            f"returns: {definition.returns}, effects: {effects or 'none'}, "
            f"params: {params or 'none'})\n"
            f"  Policy:\n{textwrap.indent(definition.body.strip(), '    ')}"
        )
    return "\n".join(lines)


def _parse_json_object_response(text: str, *, label: str) -> dict[str, Any] | str:
    """Parse a JSON object emitted by a focused LLM sub-call."""

    stripped = text.strip()
    fence = re.fullmatch(
        r"```(?:json)?\s*(?P<body>.*?)\s*```",
        stripped,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fence is not None:
        stripped = fence.group("body").strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        return f"{label} returned invalid JSON: {exc.msg}."
    if not isinstance(parsed, dict):
        return f"{label} returned JSON {type(parsed).__name__}; expected an object."
    return parsed


def _strip_markdown_fence(text: str) -> str:
    """Strip a single enclosing Markdown code fence from model output."""

    stripped = text.strip()
    fence = re.fullmatch(
        r"```(?:[A-Za-z0-9_.+-]+)?\s*(?P<body>.*?)\s*```",
        stripped,
        flags=re.DOTALL,
    )
    if fence is None:
        return stripped
    return fence.group("body").strip()


def _parse_step_judgment_response(response: str) -> StepJudgment | str:
    parsed = _parse_json_object_response(response, label="@iterate step judge")
    if isinstance(parsed, str):
        return parsed
    needs_improvement = parsed.get("needs_improvement")
    if not isinstance(needs_improvement, bool):
        return (
            "@iterate step judge returned invalid JSON: 'needs_improvement' "
            "must be a boolean."
        )
    return StepJudgment.from_dict(parsed)


def _constraint_findings_from_result(result: CompositionResult) -> list[str]:
    findings: list[str] = []
    for message in [*result.errors, *result.warnings, *result.suggestions]:
        if _is_constraint_finding(message):
            findings.append(message)
    return findings


def _is_constraint_finding(message: str) -> bool:
    lowered = message.lower()
    return (
        "@assert" in lowered
        or "@output" in lowered
        or "@structural_constraints" in lowered
        or "output format" in lowered
        or "structural constraint" in lowered
    )


def _has_only_constraint_errors(result: CompositionResult) -> bool:
    return bool(result.errors) and all(_is_constraint_finding(error) for error in result.errors)


def _trace_steps_by_key(trace: CompilationTrace | None) -> dict[str, CompilationStep]:
    if trace is None:
        return {}
    return {step_key(step.applications): step for step in trace.steps if step.applications}


def _merge_traces(
    first: CompilationTrace | None,
    second: CompilationTrace | None,
) -> CompilationTrace:
    merged = CompilationTrace()
    if first is not None:
        merged.extend(list(first.steps))
    if second is not None:
        merged.extend(list(second.steps))
    return merged


def _attach_constraint_findings_to_trace(
    trace: CompilationTrace,
    findings: list[str],
) -> None:
    if not findings:
        return
    for step in trace.steps:
        for finding in findings:
            message = f"Constraint finding: {finding}"
            if message not in step.envelope.suggestions:
                step.envelope.suggestions.append(message)


def _format_bullets(items: list[str]) -> str:
    if not items:
        return "- None."
    return "\n".join(f"- {item}" for item in items)


def _extract_root_text(spec_text: str) -> tuple[str, str]:
    """Extract root prefix and suffix from a spec.

    Prefix = everything from start to first ``@prompt``, with the
    ``@execute`` block (line + indented params) stripped.
    Suffix = everything after the last ``@prompt`` block ends.

    Returns ``(prefix, suffix)`` — both may be empty strings.
    """
    lines = spec_text.split("\n")

    # Find indices of @prompt directives
    prompt_indices: list[int] = []
    for i, line in enumerate(lines):
        if re.match(r"^@prompt\b", line.strip()):
            prompt_indices.append(i)

    if not prompt_indices:
        return ("", "")

    # --- Prefix: lines 0 .. first_prompt-1, minus @execute block ---
    first_prompt = prompt_indices[0]
    prefix_lines: list[str] = []
    i = 0
    while i < first_prompt:
        stripped = lines[i].strip()
        if stripped.startswith("@execute"):
            # Skip the @execute line and any indented continuation lines
            i += 1
            while i < first_prompt and lines[i] and lines[i][0] in (" ", "\t"):
                i += 1
            continue
        prefix_lines.append(lines[i])
        i += 1

    # --- Suffix: lines after the last @prompt block ---
    last_prompt = prompt_indices[-1]
    # The @prompt block extends until next @prompt or EOF.
    # Find where the last @prompt's content ends:
    # it's all indented lines after the @prompt line.
    j = last_prompt + 1
    while j < len(lines):
        line = lines[j]
        # A non-empty, non-indented line that isn't blank means
        # the block ended (new top-level content = suffix).
        if line and not line[0].isspace():
            break
        j += 1
    suffix_lines = lines[j:] if j < len(lines) else []

    prefix = "\n".join(prefix_lines).strip()
    suffix = "\n".join(suffix_lines).strip()
    return (prefix, suffix)


def _cascade_root_context(
    prompts: dict[str, str],
    prefix: str,
    suffix: str,
) -> dict[str, str]:
    """Prepend prefix and append suffix to each named prompt.

    Skips cascading for single-call specs (only ``"default"`` key) and
    does nothing if both prefix and suffix are empty.
    """
    if not prefix and not suffix:
        return prompts
    # Single-call specs: root text is already the entire prompt
    if list(prompts.keys()) == ["default"]:
        return prompts

    result: dict[str, str] = {}
    for name, text in prompts.items():
        parts = []
        if prefix:
            parts.append(prefix)
        parts.append(text)
        if suffix:
            parts.append(suffix)
        result[name] = "\n\n".join(parts)
    return result


def _is_named_prompt_result(prompts: dict[str, str]) -> bool:
    """Return True when parsed prompts represent explicit named prompts."""

    return bool(prompts) and list(prompts.keys()) != ["default"]


def _prompt_starts_with_context(prompt: str, shared_context: str) -> bool:
    """Check whether *prompt* already contains the shared context prefix."""

    prompt_text = prompt.strip()
    context_text = shared_context.strip()
    if not context_text:
        return True
    return prompt_text == context_text or prompt_text.startswith(f"{context_text}\n")


def _ensure_shared_context_in_named_prompts(
    prompts: dict[str, str],
    shared_context: str,
) -> dict[str, str]:
    """Prepend resolved shared context to named prompts when the model omitted it."""

    shared_context = shared_context.strip()
    if not shared_context:
        return prompts

    result: dict[str, str] = {}
    for name, prompt in prompts.items():
        if _prompt_starts_with_context(prompt, shared_context):
            result[name] = prompt
        else:
            result[name] = f"{shared_context}\n\n{prompt.strip()}"
    return result


def _should_cascade_shared_context(result: CompositionResult) -> bool:
    """Decide whether the LLM-fallback path should re-inject shared context.

    Mirrors the disposition + cascade rule applied by the structural compiler:
    pipeline disposition defaults to cascading; emission disposition defaults
    to not cascading. ``@compile context: cascade|local`` overrides the
    inferred default in either direction.
    """

    context_mode = result.compile.get("context", "auto")
    if isinstance(context_mode, str):
        normalized = context_mode.strip().lower()
        if normalized == "cascade":
            return True
        if normalized == "local":
            return False
    # No explicit override: infer disposition. The LLM populates <emits> for
    # the emission disposition; populating it means we should NOT cascade.
    return not bool(result.emits)


def parse_composition_response(
    raw: str,
    settings: WeaveMarkSettings | None = None,
) -> CompositionResult:
    """Parse one strict semantic-compiler JSON response."""
    try:
        wire = parse_wire_result(raw)
        bindings = _canonicalize_bindings(wire.bindings)
    except CompilerProtocolError as exc:
        return CompositionResult(
            composed_prompt="",
            raw_response=raw,
            errors=[f"Compiler response protocol error: {exc}"],
        )

    prompts = {name: payload.text for name, payload in wire.prompts.items()}
    prompt_roles: dict[str, str] = {
        name: payload.role
        for name, payload in wire.prompts.items()
        if payload.role is not None
    }
    if not prompts and wire.prompt:
        prompts = {"default": wire.prompt}
    compile_options = wire.compile.model_dump(exclude_none=True)
    if "format" in compile_options:
        normalized = normalize_compile_format(compile_options["format"], settings)
        if normalized is not None:
            compile_options["format"] = normalized

    return CompositionResult(
        composed_prompt=wire.prompt,
        prompts=prompts,
        prompt_roles=prompt_roles,
        prompt_outputs={
            name: OutputContract.from_dict(payload.contract_dict())
            for name, payload in wire.outputs.items()
        },
        raw_response=raw,
        analysis=wire.analysis,
        compile=compile_options,
        tools=[tool.model_dump() for tool in wire.tools],
        bindings=bindings,
        execution=wire.execution,
        emits=wire.emits,
        packages=[package.package_dict() for package in wire.packages],
        reference_contents=wire.references,
        directives=directives_from_json(
            [directive.model_dump() for directive in wire.directives]
        ),
        warnings=wire.warnings,
        errors=wire.errors,
        suggestions=wire.suggestions,
    )


def _canonicalize_bindings(
    bindings: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Normalize semantic-compiler binding names to the public ``name`` field."""

    canonical: list[dict[str, str]] = []
    for binding in bindings:
        name = next(
            (
                binding[key]
                for key in ("name", "capability", "capability_name", "tool")
                if binding.get(key)
            ),
            None,
        )
        if name is None:
            raise CompilerProtocolError(
                "compiler binding metadata is missing name/capability."
            )
        normalized = {
            key: value
            for key, value in binding.items()
            if key not in {"name", "capability", "capability_name", "tool"}
        }
        canonical.append({"name": name, **normalized})
    return canonical


def _compiler_protocol_errors(result: CompositionResult) -> list[str]:
    """Return semantic compiler protocol failures from a parsed result."""

    prefix = "Compiler response protocol error:"
    return [error for error in result.errors if error.startswith(prefix)]


async def _cleanup_litellm_logging_worker() -> None:
    """Stop LiteLLM's best-effort async logging worker between event loops."""

    with suppress(Exception, asyncio.CancelledError):
        import litellm.litellm_core_utils.logging_worker as logging_worker

        worker = logging_worker.GLOBAL_LOGGING_WORKER
        queue = worker._queue
        if queue is not None:
            while not queue.empty():
                with suppress(Exception):
                    task = queue.get_nowait()
                    coroutine = task.get("coroutine")
                    close = getattr(coroutine, "close", None)
                    if callable(close):
                        close()
                    queue.task_done()
        worker_task = worker._worker_task
        if worker_task is not None:
            worker_task.cancel()
            with suppress(Exception, asyncio.CancelledError, TimeoutError):
                await asyncio.wait_for(worker_task, timeout=1.0)
        worker._queue = None
        worker._worker_task = None


def _composition_from_structural_helper_result(
    result: StructuralHelperResult,
) -> CompositionResult:
    """Convert structural-helper output to the public result type."""

    return CompositionResult(
        composed_prompt=result.composed_prompt,
        prompts=result.prompts,
        prompt_roles=result.prompt_roles,
        prompt_outputs={
            name: OutputContract.from_dict(contract)
            for name, contract in result.prompt_outputs.items()
        },
        analysis=result.analysis,
        compile=result.compile,
        tools=result.tools,
        bindings=result.bindings,
        execution=result.execution,
        emits=result.emits,
        packages=result.packages,
        warnings=result.warnings,
        errors=result.errors,
        suggestions=result.suggestions,
        tool_calls_made=result.tool_calls_made,
    )


def _images_enabled(result: CompositionResult) -> bool:
    """Return whether Markdown image lifting is enabled (``@compile images``)."""

    value = result.compile.get("images", True)
    return bool(value)


def populate_prompt_images(
    result: CompositionResult,
    base_dir: Path,
    protection: ProtectionContext,
) -> None:
    """Lift Markdown image references into ``result.prompt_images`` in place.

    Runs only when ``@compile images`` is on (default). Scans the composed
    prompt and each named prompt; resolved images are attached per prompt name
    and any unresolved references are surfaced as warnings.
    """

    if result.errors or not _images_enabled(result):
        return

    seen_warnings: set[str] = set(result.warnings)
    sources: dict[str, str] = {}
    if result.prompts:
        sources.update(result.prompts)
    elif result.composed_prompt:
        sources["default"] = result.composed_prompt

    for name, text in sources.items():
        if not text:
            continue
        refs, warnings = extract_image_refs(
            text,
            base_dir,
            protection=protection,
        )
        if refs:
            result.prompt_images[name] = refs
        for warning in warnings:
            if warning not in seen_warnings:
                result.warnings.append(warning)
                seen_warnings.add(warning)


@dataclass
class WeaveMarkConfig:
    """Configuration for the WeaveMark controller."""

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


class WeaveMarkController:
    """Orchestrates prompt composition using LLM tool calling.

    Loads the WeaveMark system prompt (``weavemark.system.md``),
    sends the user's spec + variables, and lets the LLM drive the
    composition loop (calling ``read_file`` and ``log_transition``
    as needed).
    """

    def __init__(
        self,
        config: WeaveMarkConfig | None = None,
        *,
        client: LLMClientProtocol | None = None,
    ) -> None:
        self.config = config or WeaveMarkConfig()
        self.client = client
        self._system_prompt = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    async def compose(
        self,
        spec_text: str,
        variables: dict[str, Any] | None = None,
        base_dir: Path | None = None,
        on_event: Callable[[str, dict[str, Any]], None] | None = None,
        ask_handler: AskHandler | None = None,
        protection: ProtectionContext | None = None,
        provenance: ProvenanceOptions | None = None,
        source_path: Path | None = None,
    ) -> CompositionResult:
        """Compose a prompt from *spec_text* and *variables*.

        Args:
            spec_text: The promplet specification (Markdown with directives).
            variables: Variable values to substitute (``@{name}`` → value).
            base_dir: Base directory for resolving imported ``@refine <file>`` paths.
                      Defaults to the current working directory.
            on_event: Optional callback ``(event_type, data)`` for UI updates.
                      Event types: ``"tool_call"``, ``"tool_result"``,
                      ``"transition"``, ``"issue"``, ``"composing"``, ``"done"``.
            ask_handler: Optional host callback used by active standard-library
                ``@ask`` directives to collect compile-time answers.

        Returns:
            A :class:`CompositionResult` with the final prompt and any
            issues logged during processing.
        """
        source_text = spec_text
        started_at = datetime.now(UTC)
        started_monotonic = monotonic()
        resources: dict[str, dict[str, Any]] = {}
        base_dir = Path(base_dir) if base_dir else Path.cwd()
        variables = variables or {}
        settings_result = load_weavemark_settings(base_dir)
        if settings_result.errors:
            result = CompositionResult(
                composed_prompt="",
                analysis="WeaveMark configuration loading failed.",
                warnings=list(settings_result.warnings),
                errors=list(settings_result.errors),
                source_path=str(source_path) if source_path is not None else None,
            )
            if on_event:
                for issue in result.diagnostics:
                    on_event("issue", issue)
                on_event(
                    "done",
                    {
                        "tool_calls_made": 0,
                        "diagnostics_count": len(result.diagnostics),
                        "output_length": 0,
                    },
                )
            return result
        protection = protection or ProtectionContext.create(
            settings_result.settings.protections,
            entrypoint_dir=base_dir,
        )
        compilation_access_root = self._file_access_root(base_dir)
        replaying = provenance is not None and provenance.replay_dir is not None
        live_client = self.client
        if live_client is None and not replaying:
            live_client = new_client(
                model=self.config.model,
                protection=protection,
                logging_settings=settings_result.settings.logging,
            )
        client, recorder = create_compilation_client(live_client, provenance)
        validate_replay_context(
            client,
            source_text=source_text,
            variables=variables,
            system_prompt=self._system_prompt,
            schema=compiler_response_format(),
            compile_config=asdict(self.config),
        )
        settings = settings_result.settings

        # Lower surface syntax to canonical WeaveMark before any preprocessing.
        surface_result = lower_weavemark_surface(spec_text)
        if surface_result.errors:
            result = CompositionResult(
                composed_prompt="",
                analysis="WeaveMark surface lowering failed.",
                warnings=surface_result.warnings,
                errors=surface_result.errors,
                source_path=str(source_path) if source_path is not None else None,
            )
            if on_event:
                for issue in result.diagnostics:
                    on_event("issue", issue)
                on_event(
                    "done",
                    {
                        "tool_calls_made": 0,
                        "diagnostics_count": len(result.diagnostics),
                        "output_length": 0,
                    },
                )
            return result
        spec_text = surface_result.text

        preprocess_result = preprocess_weavemark(
            spec_text,
            base_dir,
            settings=settings,
        )

        def _emit(event: str, data: dict[str, Any]) -> None:
            if on_event:
                on_event(event, data)

        if preprocess_result.errors:
            result = CompositionResult(
                composed_prompt="",
                analysis="WeaveMark macro/module preprocessing failed.",
                warnings=preprocess_result.warnings,
                errors=preprocess_result.errors,
                source_path=str(source_path) if source_path is not None else None,
            )
            for issue in result.diagnostics:
                _emit("issue", issue)
            _emit(
                "done",
                {
                    "tool_calls_made": 0,
                    "diagnostics_count": len(result.diagnostics),
                    "output_length": 0,
                },
            )
            return result

        def _read_reference(reference: str, directory: Path) -> tuple[str, Path] | str:
            path = self._resolve_read_path(
                reference,
                directory,
                settings,
                protection,
                declared=True,
            )
            if isinstance(path, str):
                return f"Error: {path}"
            content = self._read_file(
                reference,
                directory,
                settings,
                protection,
                declared=True,
            )
            if content.startswith("Error:"):
                return content
            resource_key = _resource_key(path)
            record_resource(
                resources,
                reference=resource_key,
                content=content,
            )
            return content, path

        def _resource_key(path: Path) -> str:
            try:
                return path.relative_to(compilation_access_root).as_posix()
            except ValueError:
                path_digest = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:12]
                return f"external:{path.name}:{path_digest}"

        reference_result = resolve_references(
            preprocess_result.text,
            base_dir,
            reader=_read_reference,
            known_directives=frozenset(
                {*CORE_DIRECTIVES, *preprocess_result.semantic_definitions}
            ),
            enabled=_reference_syntax_enabled(preprocess_result.text),
        )
        if reference_result.errors:
            result = CompositionResult(
                composed_prompt="",
                analysis="WeaveMark reference resolution failed.",
                warnings=[
                    *settings_result.warnings,
                    *preprocess_result.warnings,
                    *reference_result.warnings,
                ],
                errors=reference_result.errors,
                references=[
                    reference.metadata() for reference in reference_result.references
                ],
                source_path=str(source_path) if source_path is not None else None,
            )
            if on_event:
                for issue in result.diagnostics:
                    on_event("issue", issue)
                on_event(
                    "done",
                    {
                        "tool_calls_made": 0,
                        "model_calls_made": 0,
                        "diagnostics_count": len(result.diagnostics),
                        "output_length": 0,
                    },
                )
            return result
        directive_errors = validate_directive_names(
            reference_result.text,
            preprocess_result.semantic_definitions,
        )
        if directive_errors:
            result = CompositionResult(
                composed_prompt="",
                analysis="WeaveMark directive validation failed.",
                warnings=[
                    *settings_result.warnings,
                    *preprocess_result.warnings,
                    *reference_result.warnings,
                ],
                errors=directive_errors,
                source_path=str(source_path) if source_path is not None else None,
            )
            if on_event:
                for issue in result.diagnostics:
                    on_event("issue", issue)
                on_event(
                    "done",
                    {
                        "tool_calls_made": 0,
                        "model_calls_made": 0,
                        "diagnostics_count": len(result.diagnostics),
                        "output_length": 0,
                    },
                )
            return result

        references = reference_result.references
        original_spec_text = reference_result.text

        # Collect transitions from log_transition tool calls across compile-effect rounds.
        transitions: list[str] = []
        ask_history: list[dict[str, str]] = []
        ask_tool_errors: list[str] = []
        iteration_history: list[dict[str, Any]] = []
        iterate_warnings: list[str] = []
        compilation_trace = CompilationTrace()
        accumulated_state = CompositionAccumulator()
        budget = CompilationBudget(
            max_steps=self.config.max_compilation_steps,
            max_model_calls=self.config.max_total_model_calls,
            max_seconds=self.config.max_compile_seconds,
        )

        def _emit_done(result: CompositionResult) -> None:
            result.protection = protection
            result.source_path = (
                str(source_path) if source_path is not None else None
            )
            accumulated_state.apply_to(result)
            result.references = [reference.metadata() for reference in references]
            if references and not result.errors:
                composed_prompt, prompts, reference_errors = (
                    materialize_reference_appendices(
                        result.composed_prompt,
                        result.prompts,
                        references,
                        result.reference_contents,
                    )
                )
                result.composed_prompt = composed_prompt
                result.prompts = prompts
                result.errors.extend(reference_errors)
            result.tool_calls_made += len(references)
            result.model_calls_made = budget.model_calls_used
            finalize_provenance(
                options=provenance,
                client=client,
                recorder=recorder,
                result=result,
                source_text=source_text,
                source_path=source_path,
                variables=variables,
                system_prompt=self._system_prompt,
                schema=compiler_response_format(),
                compile_config=asdict(self.config),
                resources=resources,
                started_at=started_at,
                elapsed_ms=int((monotonic() - started_monotonic) * 1000),
                protection=protection,
            )
            for issue in result.diagnostics:
                _emit("issue", issue)
            _emit(
                "done",
                {
                    "tool_calls_made": result.tool_calls_made,
                    "model_calls_made": result.model_calls_made,
                    "diagnostics_count": len(result.diagnostics),
                    "output_length": len(result.composed_prompt),
                },
            )

        def _read_compiler_resource(
            reference: str,
            directory: Path,
            *,
            declared: bool,
        ) -> str:
            content = self._read_file(
                reference,
                directory,
                settings,
                protection,
                declared=declared,
            )
            if not content.startswith("Error:"):
                resolved = self._resolve_read_path(
                    reference,
                    directory,
                    settings,
                    protection,
                    declared=declared,
                )
                record_resource(
                    resources,
                    reference=(
                        _resource_key(resolved)
                        if isinstance(resolved, Path)
                        else reference
                    ),
                    content=content,
                )
            return content

        def _error_result(analysis: str, errors: list[str]) -> CompositionResult:
            result = CompositionResult(
                composed_prompt="",
                analysis=analysis,
                warnings=[
                    *settings_result.warnings,
                    *preprocess_result.warnings,
                    *reference_result.warnings,
                    *iterate_warnings,
                ],
                errors=errors,
                ask_history=list(ask_history),
                iteration_history=list(iteration_history),
                compilation_trace=compilation_trace if compilation_trace.steps else None,
            )
            result.transitions = transitions
            _emit_done(result)
            return result

        def _effect_error_result(analysis: str, errors: list[str]) -> CompositionResult:
            return CompositionResult(
                composed_prompt="",
                analysis=analysis,
                warnings=[
                    *settings_result.warnings,
                    *preprocess_result.warnings,
                    *reference_result.warnings,
                    *iterate_warnings,
                ],
                errors=errors,
                transitions=transitions,
                ask_history=list(ask_history),
                iteration_history=list(iteration_history),
                compilation_trace=compilation_trace if compilation_trace.steps else None,
            )

        def _build_user_message(
            current_spec_text: str,
            active_asks: list[Any],
            *,
            round_index: int,
            iteration_guidance: str = "",
        ) -> str:
            vars_section = ""
            if variables:
                lines = [
                    f"- `{k}`: {_format_variable_for_prompt(v)}"
                    for k, v in variables.items()
                ]
                vars_section = "\n".join(lines)
            else:
                vars_section = "No variables provided."
            semantic_defs_section = _format_semantic_definitions_for_prompt(
                preprocess_result.semantic_definitions,
            )
            references_section = format_reference_context(references)
            ask_directives_section = format_ask_directives_for_prompt(active_asks)
            ask_answers_section = ask_history_for_prompt(ask_history)
            ask_contract = ""
            if active_asks:
                ask_contract = (
                    "## Active Compile Effects\n\n"
                    "The current spec contains active standard-library `@ask` "
                    "compile effects. Treat `@ask` as an unresolved compiler "
                    "directive, not final prompt text. Process innermost active "
                    "`@ask` scopes first. While compiling the target body/scope, "
                    "call `ask_user(question, question_type, detail_level, scope, "
                    "reason)` whenever an answer would materially guide the "
                    "remaining transformations. You may ask multiple questions "
                    "before returning XML. If transformations expose new "
                    "ambiguities, keep the relevant `@ask` directive in the XML "
                    "output so the host compiler can run another composition "
                    "round (`O1 with @ask → O2 with @ask → ... → On without "
                    "@ask`). Only remove an `@ask` once every useful question for "
                    "its requested detail level has been answered. When `@ask` "
                    "remains in an intermediate XML prompt, that is not directive "
                    "leakage; it is an explicit request for another compile-effect "
                    "round. The final accepted output, however, must contain no "
                    "unresolved `@ask`.\n\n"
                    "Active @ask directives, already sorted innermost first:\n"
                    f"{ask_directives_section}\n\n"
                    "Collected @ask answers from previous rounds:\n"
                    f"{ask_answers_section}\n\n"
                )
            guidance_section = ""
            if iteration_guidance.strip():
                guidance_section = (
                    "## Step Iteration Guidance\n\n"
                    f"{iteration_guidance.strip()}\n\n"
                )
            return (
                "# Current State\n\n"
                f"## Compile-Effect Round\n\n{round_index}\n\n"
                "## Current WeaveMark Specification\n\n"
                f"```\n{current_spec_text}\n```\n\n"
                "## Current Variables\n\n"
                f"{vars_section}\n\n"
                "## Imported Semantic Definitions\n\n"
                f"{semantic_defs_section}\n\n"
                "## Referenced Source Context\n\n"
                f"{references_section}\n\n"
                f"{ask_contract}"
                f"{guidance_section}"
                "## Pre-flight Checklist (do this BEFORE writing the output)\n\n"
                "Before producing any XML output, mentally enumerate:\n"
                "1. Every imported `@refine <path>` and `@embed file: <path>` in the "
                "spec above. For each one that survives selection (i.e., "
                "is NOT inside a discarded `@if`/`@match` branch after "
                "evaluating the conditions), you MUST call `read_file` "
                "exactly once with that path. This rule holds even if the "
                "spec is only a few lines long — small specs are NOT exempt.\n"
                "2. The number of iteration passes the composition will need "
                "(typically one or two). You MUST call `log_transition` "
                "exactly once per pass — including for a tiny one-pass "
                "spec. Skipping `log_transition` because the spec looks "
                "trivial is a composition bug.\n\n"
                "If your output ever contains a parenthetical placeholder "
                "such as `(Content from <path> will be inserted here.)`, "
                "you have skipped a required `read_file` call. Stop, call "
                "the tool, and inline the actual content.\n\n"
                "## Task\n\n"
                "Process the promplet specification above by following the Composition Flow exactly:\n"
                "1. Substitute ALL WeaveMark variable placeholders (`@{variable}`) with their values.\n"
                "2. Resolve ALL directives — process innermost nested directives first (inside-out), "
                "then apply outer directives to the result. "
                "This includes core directives such as `@match`, `@if`/`@else`, "
                "`@note`, `@prompt`, `@compile`, `@execute`, `@tool`, `@bind`, "
                "`@emit`, `@embed`, `@output`, `@module`, `@use`, `@include`, "
                "and `@define`, plus imported semantic definitions listed above. "
                "Resolve every referenced source context recursively as WeaveMark "
                "source. For a nested relative `@refine` or `@embed file:` read, "
                "pass its containing `Rn` as `reference_id` to `read_file`. Preserve "
                "each `[Reference Rn]` anchor exactly. Return the "
                "fully resolved body of every listed reference in the required "
                "`references` result object, keyed by its `Rn` identifier. Do not "
                "append reference bodies to prompt text; the host materializes kept "
                "appendices deterministically after compilation. "
                "Pure standard-library macros must have already expanded before "
                "this LLM composition path. "
                "For every imported `@refine` / `@embed file:` in a "
                "non-discarded branch, you MUST call `read_file(path)` to "
                "load the actual content — never substitute a placeholder "
                "or hallucinated content.\n"
                "3. After each iteration pass, call `log_transition(text)` exactly once. "
                "A tiny one-pass composition still requires one `log_transition` call.\n"
                "4. Unescape `@@` → `@`.\n\n"
                "## Semantic Function Contract\n\n"
                "Imported semantic definitions are compiler functions. Execute them and "
                "replace the directive call with the transformed result. Do NOT copy a "
                "semantic definition's policy body into the final prompt as prose. "
                "Definitions with `returns: replacement` replace their selected body or "
                "region; definitions with `returns: diagnostics` emit warnings/errors/"
                "suggestions only and do not contribute prompt text. If a semantic "
                "definition asks you to summarize, compress, extract, expand, revise, "
                "normalize, style, generate examples, enforce output format, apply "
                "structural constraints, or run a compile effect, perform that "
                "operation on the surrounding content and emit the resulting prompt "
                "text only. The final prompt field must never contain unresolved "
                "compiler-operation labels such as `Summarize the relevant content`, "
                "`Compress the relevant content`, `Extract the requested information`, "
                "`Expand the following material`, `Revision instruction`, `Style "
                "constraints`, `Generate N examples`, `Enforcement: strict`, "
                "`Strict: false`, or bracketed `[Assertion: ...]` diagnostics.\n\n"
                "## Refinement Contract\n\n"
                "For every `@refine` whose `mingle` option is absent or true, produce a "
                "true semantic refinement, not an append-only merge: the final artifact "
                "must imply the imported spec's full public semantic content while becoming "
                "more concrete for the local spec. If the `@refine` call has an indented "
                "body, treat that body as compiler-facing guidance for how this specific "
                "semantic mingling should be performed; do not copy it into the final "
                "output as standalone text unless the resulting concrete obligation "
                "requires it. Formally: if S' refines S, then "
                "S' implies S (`S' => S`), but S does not necessarily imply S' (`S => S'`). "
                "Integrate and specialize definitions, "
                "roles, methods, principles, workflows, examples, rationale, quality checks, "
                "constraints, output contracts, data-model rules, and exact literal "
                "identifiers into one coherent result. Do not summarize away refined "
                "method detail: if a refined spec defines MECE, ACH, issue trees, SCAMPER, "
                "or another method, the final prompt must still operationally contain that "
                "method's definition, workflow, failure/quality checks, and examples or "
                "examples-as-rules, adapted to the local domain. Propagate cross-cutting "
                "requirements into concrete sections so detailed tables, fields, routes, "
                "or acceptance criteria do not omit or contradict inherited obligations. "
                "Strip only private authoring material such as `@note`, source-relationship "
                "commentary, duplicate headings, and pure organization scaffolding; do not "
                "treat public method explanation as disposable background. Preserve exact literals in backticks, "
                "quotes, fenced blocks, API paths, event names, enum values, schema fields, "
                "and command flags byte-for-byte. Apply compiler-facing guardrails "
                "without echoing them as standalone output. Strip `@note` wording "
                "entirely; do not paraphrase it as explicit output requirements unless "
                "non-note content independently requires the same result. Never describe "
                "requirements "
                "as inherited from, compatible with, or refined from another spec; state "
                "the final concrete obligation directly. For `mingle: false`, preserve "
                "imported wording and source order as much as possible. A "
                "`mingle: false` call with a non-empty indented `@refine` body is "
                "an authoring error; report it in the errors field instead of ignoring "
                "or copying the body.\n\n"
                "**CRITICAL**: The final accepted prompt field must contain ONLY the "
                "fully-resolved prompt text. It must NOT contain raw directive syntax "
                "(`@directive`, `==>`, `@{...}`), except that an intermediate "
                "compile-effect round may intentionally keep unresolved `@ask` while "
                "more questions remain. It must NOT contain placeholder text like "
                "`(Content from X will be inserted here.)` for files you did not actually load. "
                "These are instructions for you to execute, not content to pass through.\n\n"
                "## Output Format (MANDATORY)\n\n"
                "Return exactly one JSON object matching the enforced response schema. "
                "Every field is required, including empty collections: prompt, prompts, "
                "compile, tools, bindings, execution, emits, outputs, packages, "
                "directives, analysis, warnings, errors, and suggestions. Do not add "
                "a code fence, preamble, trailing commentary, or extra fields. Prompt "
                "values are objects with text and nullable role. Package entries require "
                "file plus exactly one of template or from. The `references` object "
                "must contain every supplied reference id mapped to its fully resolved "
                "content, or be empty when no references were supplied."
            )

        async def _ask_user(args: dict[str, Any], *, round_index: int) -> str:
            def fail(message: str) -> str:
                if message not in ask_tool_errors:
                    ask_tool_errors.append(message)
                return f"Error: {message}"

            if ask_handler is None:
                return fail(
                    "@ask requires a host ask handler, but none is available."
                )
            if len(ask_history) >= self.config.max_effect_questions:
                return fail(
                    "@ask question limit reached "
                    f"({self.config.max_effect_questions})."
                )
            question = str(args.get("question", "")).strip()
            if not question:
                return fail("ask_user requires a non-empty question.")
            normalized_question = " ".join(question.casefold().split())
            if any(
                " ".join(item.get("question", "").casefold().split())
                == normalized_question
                for item in ask_history
            ):
                return fail(
                    "ask_user repeated a question that was already answered: "
                    f"{question}"
                )
            prompt = AskPrompt(
                question=question,
                question_type=str(args.get("question_type") or "clarifying question"),
                detail_level=str(args.get("detail_level") or "20%"),
                scope=str(args.get("scope") or ""),
                reason=str(args.get("reason") or ""),
                round_index=round_index,
                question_index=len(ask_history) + 1,
            )
            _emit(
                "ask_question",
                {
                    "question": prompt.question,
                    "question_type": prompt.question_type,
                    "detail_level": prompt.detail_level,
                    "scope": prompt.scope,
                    "reason": prompt.reason,
                    "round": prompt.round_index,
                    "index": prompt.question_index,
                },
            )
            maybe_answer = ask_handler(prompt)
            if inspect.isawaitable(maybe_answer):
                maybe_answer = await maybe_answer
            answer = str(maybe_answer)
            ask_history.append(
                {
                    "question": prompt.question,
                    "answer": answer,
                    "question_type": prompt.question_type,
                    "detail_level": prompt.detail_level,
                    "scope": prompt.scope,
                    "reason": prompt.reason,
                }
            )
            _emit(
                "ask_answer",
                {
                    "round": prompt.round_index,
                    "index": prompt.question_index,
                    "answer_length": len(answer),
                },
            )
            return f"Answer recorded for @ask:\n{answer}"

        async def _compose_round_raw(
            current_spec_text: str,
            active_asks: list[Any],
            ask_errors: list[str],
            *,
            round_index: int,
            iteration_guidance: str = "",
        ) -> CompositionResult:
            messages = [
                {"role": "system", "content": self._system_prompt},
                {
                    "role": "user",
                    "content": _build_user_message(
                        current_spec_text,
                        active_asks,
                        round_index=round_index,
                        iteration_guidance=iteration_guidance,
                    ),
                },
            ]

            async def tool_executor(name: str, args: dict[str, Any]) -> str:
                _emit("tool_call", {"name": name, "args": args})
                if name == "read_file":
                    file_name = str(args["file_name"])
                    reference_id = str(args.get("reference_id", "")).strip()
                    root_declared = _source_declares_reference(
                        original_spec_text,
                        file_name,
                    )
                    declaring_references = [
                        reference
                        for reference in references
                        if _source_declares_reference(reference.content, file_name)
                    ]
                    nested_reference = next(
                        (
                            reference
                            for reference in declaring_references
                            if reference.id == reference_id
                        ),
                        None,
                    )
                    if reference_id and nested_reference is None:
                        return (
                            f"Error: reference_id {reference_id!r} does not declare "
                            f"{file_name!r}."
                        )
                    if (
                        not reference_id
                        and not root_declared
                        and len(declaring_references) == 1
                    ):
                        nested_reference = declaring_references[0]
                    if (
                        not reference_id
                        and not root_declared
                        and len(declaring_references) > 1
                    ):
                        choices = ", ".join(
                            reference.id for reference in declaring_references
                        )
                        return (
                            f"Error: {file_name!r} is declared by multiple referenced "
                            f"sources ({choices}); retry read_file with reference_id."
                        )
                    resource_dir = (
                        nested_reference.resolved_path.parent
                        if nested_reference is not None
                        else base_dir
                    )
                    result_str = _read_compiler_resource(
                        file_name,
                        resource_dir,
                        declared=(
                            root_declared
                            or nested_reference is not None
                        ),
                    )
                    _emit(
                        "tool_result",
                        {
                            "name": name,
                            "file": args["file_name"],
                            "size": len(result_str),
                            "error": result_str.startswith("Error:"),
                        },
                    )
                    return result_str
                if name == "log_transition":
                    text = args.get("text", "")
                    transitions.append(text)
                    _emit("transition", {"text": text, "step": len(transitions)})
                    return "Transition logged."
                if name == "ask_user":
                    result_str = await _ask_user(args, round_index=round_index)
                    _emit(
                        "tool_result",
                        {
                            "name": name,
                            "size": len(result_str),
                            "error": result_str.startswith("Error:"),
                        },
                    )
                    return result_str
                return f"Unknown tool: {name}"

            _emit(
                "composing",
                {
                    "model": self.config.model,
                    "num_variables": len(variables),
                    "spec_length": len(current_spec_text),
                    "compile_effect_round": round_index,
                    "active_ask_count": len(active_asks),
                },
            )

            if self.config.use_structural_helpers and not references:
                structural_helper_result = try_apply_structural_helpers(
                    current_spec_text,
                    variables,
                    base_dir,
                    lambda file_name, directory: _read_compiler_resource(
                        file_name,
                        directory,
                        declared=True,
                    ),
                    preprocess_result.semantic_definitions,
                    settings=settings,
                )
            else:
                structural_helper_result = None
            if structural_helper_result is not None:
                result = _composition_from_structural_helper_result(
                    structural_helper_result
                )
                result.warnings = [
                    *settings_result.warnings,
                    *preprocess_result.warnings,
                    *reference_result.warnings,
                    *iterate_warnings,
                    *result.warnings,
                ]
                result.transitions = transitions
                result.ask_history = list(ask_history)
                result.iteration_history = list(iteration_history)
                result.compilation_trace = (
                    compilation_trace if compilation_trace.steps else None
                )
                populate_prompt_images(result, base_dir, protection)
                return result

            if ask_errors:
                return CompositionResult(
                    composed_prompt="",
                    analysis="WeaveMark @ask validation failed.",
                    warnings=[
                        *settings_result.warnings,
                        *preprocess_result.warnings,
                        *iterate_warnings,
                    ],
                    errors=ask_errors,
                    transitions=transitions,
                    ask_history=list(ask_history),
                    iteration_history=list(iteration_history),
                )

            if active_asks and ask_handler is None:
                return CompositionResult(
                    composed_prompt="",
                    analysis="WeaveMark @ask requires host interaction.",
                    warnings=[
                        *settings_result.warnings,
                        *preprocess_result.warnings,
                        *iterate_warnings,
                    ],
                    errors=[
                        "@ask requires an interactive host ask handler. "
                        "Run without --batch-only in the CLI or provide "
                        "ask_handler when using the Python API."
                    ],
                    transitions=transitions,
                    ask_history=list(ask_history),
                    iteration_history=list(iteration_history),
                )

            tools = TOOLS + (COMPILE_EFFECT_TOOLS if active_asks else [])
            max_iterations = self.config.max_iterations
            if active_asks:
                max_iterations = max(
                    max_iterations,
                    self.config.max_effect_questions + 5,
                )
            budget_error = budget.consume_model_call("semantic composition")
            if budget_error is not None:
                return CompositionResult(
                    composed_prompt="",
                    analysis="WeaveMark compilation budget exhausted.",
                    errors=[budget_error],
                )
            try:
                response: ToolCallResponse = await client.complete_with_tools(
                    messages=messages,
                    tools=tools,
                    tool_executor=tool_executor,
                    model=self.config.model,
                    temperature=self.config.temperature,
                    max_iterations=max_iterations,
                    response_format=compiler_response_format(),
                )
            except MaxToolIterationsError as exc:
                result = CompositionResult(
                    composed_prompt="",
                    analysis="WeaveMark compiler tool loop did not converge.",
                    warnings=[
                        *settings_result.warnings,
                        *preprocess_result.warnings,
                        *iterate_warnings,
                    ],
                    errors=[str(exc)],
                    transitions=transitions,
                    ask_history=list(ask_history),
                    iteration_history=list(iteration_history),
                    tool_calls_made=len(exc.tool_calls_made),
                    partial_messages=list(exc.messages),
                    unresolved_tool_calls=list(exc.unresolved_tool_calls),
                )
                return result
            finally:
                await _cleanup_litellm_logging_worker()

            result = parse_composition_response(response.content, settings)
            compiler_tool_calls = len(response.tool_calls)
            protocol_errors = _compiler_protocol_errors(result)
            if protocol_errors:
                repair_budget_error = budget.consume_model_call(
                    "semantic compiler protocol repair"
                )
                if repair_budget_error is not None:
                    result.errors.append(repair_budget_error)
                else:
                    repair_messages = [
                        *messages,
                        {"role": "assistant", "content": response.content},
                        {
                            "role": "user",
                            "content": (
                                "Your previous final compiler response violated the "
                                "required JSON protocol:\n- "
                                + "\n- ".join(protocol_errors)
                                + "\n\nReturn one corrected compiler response now. "
                                "It must match the response schema exactly, contain "
                                "no duplicate keys, and preserve the intended prompt "
                                "and metadata. You may call the available tools again "
                                "if needed."
                            ),
                        },
                    ]
                    try:
                        repaired_response: ToolCallResponse = (
                            await client.complete_with_tools(
                                messages=repair_messages,
                                tools=tools,
                                tool_executor=tool_executor,
                                model=self.config.model,
                                temperature=self.config.temperature,
                                max_iterations=max_iterations,
                                response_format=compiler_response_format(),
                            )
                        )
                    except MaxToolIterationsError as exc:
                        result.errors.append(
                            "Compiler protocol repair did not converge: " + str(exc)
                        )
                        compiler_tool_calls += len(exc.tool_calls_made)
                    else:
                        compiler_tool_calls += len(repaired_response.tool_calls)
                        repaired = parse_composition_response(
                            repaired_response.content,
                            settings,
                        )
                        if not _compiler_protocol_errors(repaired):
                            repaired.warnings.append(
                                "The semantic compiler required one protocol-repair "
                                "retry."
                            )
                        result = repaired
                    finally:
                        await _cleanup_litellm_logging_worker()
            result.errors = [*ask_tool_errors, *result.errors]
            result.tool_calls_made = compiler_tool_calls
            result.transitions = transitions
            result.ask_history = list(ask_history)
            result.iteration_history = list(iteration_history)
            result.compilation_trace = compilation_trace if compilation_trace.steps else None
            result.warnings = [
                *settings_result.warnings,
                *preprocess_result.warnings,
                *iterate_warnings,
                *result.warnings,
            ]

            if _is_named_prompt_result(
                result.prompts
            ) and _should_cascade_shared_context(result):
                result.prompts = _ensure_shared_context_in_named_prompts(
                    result.prompts,
                    result.composed_prompt,
                )
            populate_prompt_images(result, base_dir, protection)
            return result

        async def _compose_round(
            current_spec_text: str,
            active_asks: list[Any],
            ask_errors: list[str],
            *,
            round_index: int,
            iteration_guidance: str = "",
        ) -> CompositionResult:
            result = await _compose_round_raw(
                current_spec_text,
                active_asks,
                ask_errors,
                round_index=round_index,
                iteration_guidance=iteration_guidance,
            )
            accumulated_state.absorb(result)
            return result

        async def _compile_iteration_target(
            target_source: str,
            ask_prelude: IterateAskPrelude | None,
            *,
            iteration_index: int,
            previous_trace: CompilationTrace | None = None,
        ) -> CompositionResult:
            current_target_text = target_source
            if ask_prelude is not None:
                ask_result = await _compile_ask_prelude_target(
                    target_source,
                    ask_prelude,
                )
                if ask_result.errors and not _has_only_constraint_errors(ask_result):
                    return ask_result
                current_target_text = composition_result_to_weavemark_text(ask_result)
                if not current_target_text.strip():
                    current_target_text = ask_result.composed_prompt

            trace = CompilationTrace()
            previous_steps = _trace_steps_by_key(previous_trace)

            while True:
                budget_error = budget.consume_step(
                    f"iterate-{iteration_index}-compilation-steps",
                    current_target_text,
                )
                if budget_error is not None:
                    return _effect_error_result(
                        "WeaveMark compilation step budget exhausted.",
                        [budget_error],
                    )
                applications = find_next_compilation_step(
                    current_target_text,
                    preprocess_result.semantic_definitions,
                )
                if not applications:
                    root_result = await _compose_iteration_root(
                        current_target_text,
                        iteration_index=iteration_index,
                    )
                    if root_result.errors and not _has_only_constraint_errors(
                        root_result
                    ):
                        return root_result
                    _attach_constraint_findings_to_trace(
                        trace,
                        _constraint_findings_from_result(root_result),
                    )
                    root_result.compilation_trace = trace
                    return root_result

                previous_step = previous_steps.get(step_key(applications))
                judgment: StepJudgment | None = None
                guidance = ""
                if previous_step is not None:
                    constraint_findings = _constraint_findings_from_result(
                        previous_step.envelope
                    )
                    judgment_result = await _judge_compilation_step(
                        applications,
                        previous_step,
                        constraint_findings=constraint_findings,
                    )
                    if isinstance(judgment_result, str):
                        return _effect_error_result(
                            "WeaveMark @iterate step judgment failed.",
                            [judgment_result],
                        )
                    judgment = judgment_result
                    if not judgment.needs_improvement:
                        replacement = previous_step.envelope.composed_prompt
                        envelope = previous_step.envelope
                        envelope.compilation_trace = None
                    else:
                        guidance = _format_step_iteration_guidance(
                            previous_step,
                            judgment,
                        )
                        step_source = source_for_applications(
                            current_target_text,
                            applications,
                        )
                        envelope = await _compose_iteration_step(
                            step_source,
                            applications,
                            iteration_guidance=guidance,
                            iteration_index=iteration_index,
                        )
                        if envelope.errors and not _has_only_constraint_errors(
                            envelope
                        ):
                            return envelope
                        replacement = envelope.composed_prompt
                else:
                    step_source = source_for_applications(
                        current_target_text,
                        applications,
                    )
                    envelope = await _compose_iteration_step(
                        step_source,
                        applications,
                        iteration_guidance="",
                        iteration_index=iteration_index,
                    )
                    if envelope.errors and not _has_only_constraint_errors(envelope):
                        return envelope
                    replacement = envelope.composed_prompt

                step = CompilationStep(
                    id=f"iter{iteration_index}.step{len(trace.steps) + 1:03d}",
                    iteration=iteration_index,
                    applications=applications,
                    envelope=envelope,
                    previous_step_id=previous_step.id if previous_step else None,
                    judgment=judgment,
                )
                trace.steps.append(step)
                iteration_history.append(
                    {
                        "phase": "step",
                        "iteration": iteration_index,
                        "step_id": step.id,
                        "previous_step_id": step.previous_step_id,
                        "applications": [
                            application.to_dict() for application in applications
                        ],
                        "needs_improvement": bool(
                            judgment and judgment.needs_improvement
                        ),
                    }
                )
                current_target_text = replace_applications(
                    current_target_text,
                    applications,
                    replacement,
                )

        async def _compile_ask_prelude_target(
            target_source: str,
            ask_prelude: IterateAskPrelude,
        ) -> CompositionResult:
            current_target_text = ask_prelude.wrap(target_source)
            for effect_round_index in range(1, self.config.max_effect_rounds + 1):
                budget_error = budget.consume_step(
                    "iterate-ask-prelude",
                    current_target_text
                    + "\n\nCollected answers:\n"
                    + json.dumps(ask_history, sort_keys=True),
                )
                if budget_error is not None:
                    return _effect_error_result(
                        "WeaveMark @ask did not make progress inside @iterate.",
                        [budget_error],
                    )
                active_asks, ask_errors = find_ask_directives(
                    current_target_text,
                    preprocess_result.semantic_definitions,
                )
                result = await _compose_round(
                    current_target_text,
                    active_asks,
                    ask_errors,
                    round_index=effect_round_index,
                )
                if result.errors and not _has_only_constraint_errors(result):
                    return result

                next_target_text = composition_result_to_weavemark_text(result)
                remaining_asks, ask_errors = find_ask_directives(
                    next_target_text,
                    preprocess_result.semantic_definitions,
                )
                if ask_errors:
                    result.errors.extend(ask_errors)
                    return result
                if not remaining_asks:
                    return result
                if effect_round_index == self.config.max_effect_rounds:
                    result.errors.append(
                        "@ask did not converge inside @iterate: unresolved @ask "
                        "directives remain after "
                        f"{self.config.max_effect_rounds} compile-effect rounds."
                    )
                    return result

                _emit(
                    "compile_effect_round",
                    {
                        "completed_round": effect_round_index,
                        "remaining_ask_count": len(remaining_asks),
                        "inside_iterate": True,
                    },
                )
                current_target_text = next_target_text

            return _effect_error_result(
                "WeaveMark @iterate target compile-effect loop exited unexpectedly.",
                ["WeaveMark @iterate target compile-effect loop exited unexpectedly."],
            )

        async def _compose_iteration_step(
            step_source: str,
            applications: list[DirectiveApplication],
            *,
            iteration_guidance: str,
            iteration_index: int,
        ) -> CompositionResult:
            active_asks, ask_errors = find_ask_directives(
                step_source,
                preprocess_result.semantic_definitions,
            )
            result = await _compose_round(
                step_source,
                active_asks,
                ask_errors,
                round_index=iteration_index + 1,
                iteration_guidance=iteration_guidance,
            )
            result.directives = applications
            return result

        async def _compose_iteration_root(
            root_source: str,
            *,
            iteration_index: int,
        ) -> CompositionResult:
            active_asks, ask_errors = find_ask_directives(
                root_source,
                preprocess_result.semantic_definitions,
            )
            return await _compose_round(
                root_source,
                active_asks,
                ask_errors,
                round_index=iteration_index + 1,
            )

        async def _judge_compilation_step(
            applications: list[DirectiveApplication],
            previous_step: CompilationStep,
            *,
            constraint_findings: list[str],
        ) -> StepJudgment | str:
            budget_error = budget.consume_model_call("@iterate step judgment")
            if budget_error is not None:
                return budget_error
            applications_json = json.dumps(
                directives_to_json(applications),
                ensure_ascii=False,
                indent=2,
            )
            response = await client.complete(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are the dedicated WeaveMark @iterate step judge. "
                            "Judge only; do not rewrite or improve. Evaluate whether "
                            "the previous compilation step can be materially improved "
                            "while fully preserving each original directive's meaning, "
                            "parameters, body, and local role. Treat constraint "
                            "findings as important improvement evidence, but do not "
                            "recommend violating directive parameters. "
                            "Return JSON only with this shape: "
                            '{"needs_improvement": boolean, "good_points": string[], '
                            '"bad_points": string[], "suggestions": string[], '
                            '"compliance_notes": string[], '
                            '"constraint_findings": string[], '
                            '"directive_feedback": {"<directive-id>": string[]}}.'
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Original directive application(s):\n"
                            f"```json\n{applications_json}\n```\n\n"
                            "Previous step envelope/result:\n"
                            f"```json\n{previous_step.envelope.raw_response or previous_step.envelope.composed_prompt}\n```\n\n"
                            "Constraint findings from the previous result:\n"
                            + (
                                "\n".join(f"- {finding}" for finding in constraint_findings)
                                if constraint_findings
                                else "No constraint findings."
                            )
                        ),
                    },
                ],
                model=self.config.model,
                temperature=0.0,
            )
            return _parse_step_judgment_response(response)

        def _format_step_iteration_guidance(
            previous_step: CompilationStep,
            judgment: StepJudgment,
        ) -> str:
            return (
                "You are rerunning the exact same directive application(s) as a "
                "WeaveMark @iterate improvement step. Fully comply with the "
                "original directive headers, parameters, bodies, and semantics. "
                "Do not perform a generic edit; re-execute the original directive "
                "contract better.\n\n"
                "Original directive application(s):\n"
                f"```json\n{json.dumps(directives_to_json(previous_step.applications), ensure_ascii=False, indent=2)}\n```\n\n"
                "Previous step output/envelope:\n"
                f"```json\n{previous_step.envelope.raw_response or previous_step.envelope.composed_prompt}\n```\n\n"
                "Judge good points to preserve:\n"
                f"{_format_bullets(judgment.good_points)}\n\n"
                "Judge bad points to fix:\n"
                f"{_format_bullets(judgment.bad_points)}\n\n"
                "Judge suggestions to apply:\n"
                f"{_format_bullets(judgment.suggestions)}\n\n"
                "Compliance notes:\n"
                f"{_format_bullets(judgment.compliance_notes)}\n\n"
                "Constraint findings:\n"
                f"{_format_bullets(judgment.constraint_findings)}"
            )

        async def _resolve_iterate_directive(
            current_spec_text: str,
            directive: IterateDirective,
        ) -> tuple[str | None, CompositionResult | None]:
            if self.config.max_iterate_turns <= 0:
                return None, _effect_error_result(
                    "WeaveMark @iterate configuration is invalid.",
                    ["WeaveMarkConfig.max_iterate_turns must be greater than 0."],
                )

            requested_turns = directive.turns
            effective_turns = min(
                requested_turns
                if requested_turns is not None
                else self.config.max_iterate_turns,
                self.config.max_iterate_turns,
            )
            target_source = (
                spec_without_whole_iterate_directive(current_spec_text, directive)
                if directive.applies_to_whole_spec
                else directive.target_body
            )
            if not target_source.strip():
                return None, _effect_error_result(
                    "WeaveMark @iterate has no target body.",
                    [
                        f"@iterate at line {directive.line_number} has no body and "
                        "the surrounding spec is empty."
                    ],
                )

            _emit(
                "iterate_start",
                {
                    "line": directive.line_number,
                    "requested_turns": requested_turns,
                    "effective_turns": effective_turns,
                    "config_max_turns": self.config.max_iterate_turns,
                    "ask_wrapper": directive.ask_prelude is not None,
                    "whole_spec": directive.applies_to_whole_spec,
                },
            )

            compiled_result = await _compile_iteration_target(
                target_source,
                directive.ask_prelude,
                iteration_index=0,
            )
            if compiled_result.errors and not _has_only_constraint_errors(
                compiled_result
            ):
                return None, compiled_result
            compiled_target = composition_result_to_weavemark_text(compiled_result)
            if not compiled_target.strip():
                compiled_target = compiled_result.composed_prompt

            for turn_index in range(1, effective_turns + 1):
                improved_result = await _compile_iteration_target(
                    target_source,
                    directive.ask_prelude,
                    iteration_index=turn_index,
                    previous_trace=compiled_result.compilation_trace,
                )
                if improved_result.errors and not _has_only_constraint_errors(
                    improved_result
                ):
                    return None, improved_result
                needs_improvement = any(
                    step.needs_improvement
                    for step in (improved_result.compilation_trace or CompilationTrace()).steps
                ) or bool(_constraint_findings_from_result(improved_result))
                unmet_points: list[str] = list(
                    _constraint_findings_from_result(improved_result)
                )
                for step in (
                    improved_result.compilation_trace or CompilationTrace()
                ).steps:
                    if step.judgment is None:
                        continue
                    for point in (
                        *step.judgment.bad_points,
                        *step.judgment.constraint_findings,
                    ):
                        if point not in unmet_points:
                            unmet_points.append(point)
                _emit(
                    "iterate_judge",
                    {
                        "line": directive.line_number,
                        "turn": turn_index,
                        "satisfied": not needs_improvement,
                        "why": (
                            "No step needed material improvement."
                            if not needs_improvement
                            else "At least one step needed improvement and was rerun."
                        ),
                        "unmet_points": unmet_points,
                    },
                )
                if needs_improvement:
                    _emit(
                        "iterate_improve",
                        {
                            "line": directive.line_number,
                            "turn": turn_index,
                            "unmet_points": unmet_points,
                        },
                    )
                improved_target = composition_result_to_weavemark_text(improved_result)
                if not improved_target.strip():
                    improved_target = improved_result.composed_prompt
                if not needs_improvement:
                    improved_result.compilation_trace = _merge_traces(
                        compiled_result.compilation_trace,
                        improved_result.compilation_trace,
                    )
                    compilation_trace.extend(
                        list(improved_result.compilation_trace.steps)
                        if improved_result.compilation_trace is not None
                        else []
                    )
                    _emit(
                        "iterate_complete",
                        {
                            "line": directive.line_number,
                            "turns_used": turn_index,
                            "reason": "No step needed material improvement.",
                        },
                    )
                    return replace_iterate_directive(
                        current_spec_text,
                        directive,
                        improved_target,
                    ), None
                improved_result.compilation_trace = _merge_traces(
                    compiled_result.compilation_trace,
                    improved_result.compilation_trace,
                )
                compiled_result = improved_result
                compiled_target = improved_target

            compilation_trace.extend(
                list(compiled_result.compilation_trace.steps)
                if compiled_result.compilation_trace is not None
                else []
            )
            warning = (
                f"@iterate at line {directive.line_number} reached its improvement "
                f"budget after {effective_turns} iteration(s); returning the best "
                "available result even though at least one compilation step still "
                "had material improvement opportunities."
            )
            iterate_warnings.append(warning)
            _emit(
                "iterate_exhausted",
                {
                    "line": directive.line_number,
                    "turns_used": effective_turns,
                    "why_not_yet": "At least one compilation step still needed improvement.",
                    "unmet_points": unmet_points,
                },
            )
            return replace_iterate_directive(
                current_spec_text,
                directive,
                compiled_target,
            ), None

        current_spec_text = original_spec_text
        for round_index in range(1, self.config.max_effect_rounds + 1):
            budget_error = budget.consume_step(
                "compile-effect-rounds",
                current_spec_text
                + "\n\nCollected answers:\n"
                + json.dumps(ask_history, sort_keys=True),
            )
            if budget_error is not None:
                return _error_result(
                    "WeaveMark compile-effect loop did not make progress.",
                    [budget_error],
                )
            active_iterates, iterate_errors = find_iterate_directives(
                current_spec_text,
                preprocess_result.semantic_definitions,
            )
            if iterate_errors:
                result = _effect_error_result(
                    "WeaveMark @iterate validation failed.",
                    iterate_errors,
                )
                _emit_done(result)
                return result
            if active_iterates:
                next_spec_text, error_result = await _resolve_iterate_directive(
                    current_spec_text,
                    active_iterates[0],
                )
                if error_result is not None:
                    _emit_done(error_result)
                    return error_result
                if next_spec_text is None:
                    result = _effect_error_result(
                        "WeaveMark @iterate failed unexpectedly.",
                        ["WeaveMark @iterate failed unexpectedly."],
                    )
                    _emit_done(result)
                    return result
                remaining_iterates, iterate_errors = find_iterate_directives(
                    next_spec_text,
                    preprocess_result.semantic_definitions,
                )
                if iterate_errors:
                    result = _effect_error_result(
                        "WeaveMark @iterate validation failed.",
                        iterate_errors,
                    )
                    _emit_done(result)
                    return result
                current_spec_text = next_spec_text
                if remaining_iterates:
                    if round_index == self.config.max_effect_rounds:
                        result = _effect_error_result(
                            "WeaveMark @iterate did not converge.",
                            [
                                "@iterate did not converge: unresolved @iterate "
                                "directives remain after "
                                f"{self.config.max_effect_rounds} compile-effect rounds."
                            ],
                        )
                        _emit_done(result)
                        return result
                    _emit(
                        "compile_effect_round",
                        {
                            "completed_round": round_index,
                            "remaining_iterate_count": len(remaining_iterates),
                        },
                    )
                    continue

            active_asks, ask_errors = find_ask_directives(
                current_spec_text,
                preprocess_result.semantic_definitions,
            )

            result = await _compose_round(
                current_spec_text,
                active_asks,
                ask_errors,
                round_index=round_index,
            )
            if result.errors:
                _emit_done(result)
                return result

            next_spec_text = composition_result_to_weavemark_text(result)
            remaining_iterates, iterate_errors = find_iterate_directives(
                next_spec_text,
                preprocess_result.semantic_definitions,
            )
            if iterate_errors:
                result.errors.extend(iterate_errors)
                _emit_done(result)
                return result
            if remaining_iterates:
                if round_index == self.config.max_effect_rounds:
                    result.errors.append(
                        "@iterate did not converge: unresolved @iterate directives "
                        f"remain after {self.config.max_effect_rounds} compile-effect "
                        "rounds."
                    )
                    _emit_done(result)
                    return result
                _emit(
                    "compile_effect_round",
                    {
                        "completed_round": round_index,
                        "remaining_iterate_count": len(remaining_iterates),
                    },
                )
                current_spec_text = next_spec_text
                continue

            remaining_asks, ask_errors = find_ask_directives(
                next_spec_text,
                preprocess_result.semantic_definitions,
            )
            if ask_errors:
                result.errors.extend(ask_errors)
                _emit_done(result)
                return result
            if not remaining_asks:
                _emit_done(result)
                return result
            if round_index == self.config.max_effect_rounds:
                result.errors.append(
                    "@ask did not converge: unresolved @ask directives remain "
                    f"after {self.config.max_effect_rounds} compile-effect rounds."
                )
                _emit_done(result)
                return result

            _emit(
                "compile_effect_round",
                {
                    "completed_round": round_index,
                    "remaining_ask_count": len(remaining_asks),
                },
            )
            current_spec_text = next_spec_text

        return _error_result(
            "WeaveMark compile-effect loop exited unexpectedly.",
            ["WeaveMark compile-effect loop exited unexpectedly."],
        )

    # ------------------------------------------------------------------
    # Primitive helpers
    # ------------------------------------------------------------------

    # Rich document extensions that markitdown can convert to Markdown
    _RICH_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".pptx",
        ".xlsx",
        ".xls",
        ".doc",
        ".ppt",
        ".html",
        ".htm",
    }
    _PROJECT_ROOT_MARKERS = (
        ".weavemark-root",
        "weavemark.json",
        ".git",
        "pyproject.toml",
    )

    @staticmethod
    def _file_access_root(base_dir: Path) -> Path:
        """Return the outer boundary for file references from *base_dir*."""

        resolved = base_dir.resolve()
        for candidate in (resolved, *resolved.parents):
            if any(
                (candidate / marker).exists()
                for marker in WeaveMarkController._PROJECT_ROOT_MARKERS
            ):
                return candidate
        return resolved

    @staticmethod
    def _read_file(
        file_name: str,
        base_dir: Path,
        settings: WeaveMarkSettings | None = None,
        protection: ProtectionContext | None = None,
        *,
        declared: bool = True,
    ) -> str:
        """Read a file relative to *base_dir*.

        For rich document formats (.pdf, .docx, .pptx, .xlsx, etc.),
        automatically converts to Markdown using ``markitdown`` if
        installed.  Falls back to a helpful error otherwise.
        """
        settings = settings or builtin_weavemark_settings()
        if file_name.startswith("directory:"):
            folder_name = file_name.removeprefix("directory:").strip()
            return WeaveMarkController._read_markdown_directory(
                folder_name,
                base_dir,
                settings,
                protection,
                declared=declared,
            )
        if file_name.startswith("module:"):
            module_name = file_name.removeprefix("module:").strip()
            result = resolve_module_body(module_name, base_dir, settings=settings)
            if result.errors:
                return "Error: " + "\n".join(result.errors)
            return result.text
        protection = protection or ProtectionContext.create(
            settings.protections,
            entrypoint_dir=base_dir,
        )
        path = WeaveMarkController._resolve_read_path(
            file_name,
            base_dir,
            settings,
            protection,
            declared=declared,
        )
        if isinstance(path, str):
            return f"Error: {path}"

        # Check if this is a rich format that needs conversion
        if path.suffix.lower() in WeaveMarkController._RICH_EXTENSIONS:
            return WeaveMarkController._convert_rich_file(path, file_name)

        try:
            return path.read_text(encoding="utf-8")
        except ProtectionError:
            raise
        except Exception as exc:
            return f"Error reading '{file_name}': {exc}"

    @staticmethod
    def _read_markdown_directory(
        folder_name: str,
        base_dir: Path,
        settings: WeaveMarkSettings,
        protection: ProtectionContext | None,
        *,
        declared: bool,
    ) -> str:
        """Read a bounded, deterministic set of Markdown reports from a directory."""

        protection = protection or ProtectionContext.create(
            settings.protections,
            entrypoint_dir=base_dir,
        )
        access_root = WeaveMarkController._file_access_root(base_dir)
        candidates = [
            (base_dir / folder_name).resolve(),
            (access_root / folder_name).resolve(),
        ]
        directory = next((path for path in candidates if path.is_dir()), None)
        if directory is None:
            return f"Error: directory '{folder_name}' not found."

        reports = sorted(directory.rglob("*.md"))
        if not reports:
            return f"Error: directory '{folder_name}' contains no Markdown reports."
        if len(reports) > 20:
            return (
                f"Error: directory '{folder_name}' contains {len(reports)} Markdown "
                "reports; the maximum is 20."
            )

        sections: list[str] = []
        total_chars = 0
        for path in reports:
            authorized = protection.authorize_read(
                path,
                reason=f"Markdown report folder {folder_name!r}",
                declared=declared,
            )
            text = authorized.read_text(encoding="utf-8")
            total_chars += len(text)
            if total_chars > 120_000:
                return (
                    f"Error: Markdown reports in '{folder_name}' exceed the "
                    "120000-character limit."
                )
            relative = path.relative_to(directory)
            sections.append(f"## {relative.as_posix()}\n\n{text.strip()}")
        return "\n\n".join(sections)

    @staticmethod
    def _resolve_read_path(
        file_name: str,
        base_dir: Path,
        settings: WeaveMarkSettings,
        protection: ProtectionContext,
        *,
        declared: bool,
    ) -> Path | str:
        if not is_explicit_file_reference(file_name) and (
            settings.fragment_aliases or has_fragment_alias_prefix(file_name)
        ):
            fragment = resolve_fragment_reference(file_name, settings)
            if fragment.error is not None:
                return fragment.error
            if fragment.path is not None:
                return protection.authorize_read(
                    fragment.path,
                    reason=f"Promplet fragment reference {file_name!r}",
                    declared=declared,
                )

        access_root = WeaveMarkController._file_access_root(base_dir)
        expanded_path = Path(file_name).expanduser()
        candidate_paths = (
            [expanded_path.resolve()]
            if expanded_path.is_absolute()
            else [
                (base_dir / expanded_path).resolve(),
                (access_root / "promplets" / expanded_path).resolve(),
                (access_root / expanded_path).resolve(),
            ]
        )
        for candidate in candidate_paths:
            if candidate.is_file():
                return protection.authorize_read(
                    candidate,
                    reason=f"Promplet file reference {file_name!r}",
                    declared=declared,
                )
        if protection.enabled:
            protection.authorize_read(
                candidate_paths[0],
                reason=f"Promplet file reference {file_name!r}",
                declared=declared,
            )
        return f"file '{file_name}' not found."

    @staticmethod
    def _convert_rich_file(path: Path, file_name: str) -> str:
        """Convert a rich document to Markdown via markitdown."""
        try:
            from markitdown import MarkItDown
        except ImportError:
            return (
                f"Error: file '{file_name}' is a rich document format "
                f"({path.suffix}) that requires the 'markitdown' package "
                f"for conversion. Install it with: pip install weavemark[convert]"
            )
        try:
            md = MarkItDown()
            result = md.convert(str(path))
            return result.text_content
        except Exception as exc:
            return f"Error converting '{file_name}' to Markdown: {exc}"
