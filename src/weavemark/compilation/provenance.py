"""Optional compilation provenance, run recording, and strict replay."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, cast

from ellements.core import (
    LLMClientProtocol,
    ToolCallRecord,
    ToolCallResponse,
)
from ellements.core.observability import (
    LLMErrorEvent,
    LLMRequestEvent,
    LLMResponseEvent,
)

from weavemark.protection import ProtectionContext
from weavemark.version import LANGUAGE_VERSION, PROCESSOR_VERSION

if TYPE_CHECKING:
    from weavemark.compilation.result import CompositionResult

_FORMAT_VERSION = 1
_CALLS_FILE = "calls.jsonl"
_MANIFEST_FILE = "manifest.json"
_RESULT_FILE = "result.json"

ToolExecutor = Callable[[str, dict[str, Any]], Awaitable[str]]


class CompilationClient(Protocol):
    """Narrow LLM surface used by semantic WeaveMark compilation."""

    model: str

    async def complete(
        self,
        messages: Any,
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str: ...

    async def complete_with_tools(
        self,
        messages: Any,
        tools: Any,
        *,
        tool_executor: ToolExecutor | None = None,
        dialect: Any = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        max_iterations: int = 10,
        **kwargs: Any,
    ) -> ToolCallResponse: ...


@dataclass(frozen=True, slots=True)
class ProvenanceOptions:
    """Optional artifact destinations for one compilation."""

    manifest_path: Path | None = None
    record_dir: Path | None = None
    replay_dir: Path | None = None

    def __post_init__(self) -> None:
        if self.record_dir is not None and self.replay_dir is not None:
            raise ValueError("record_dir and replay_dir are mutually exclusive")

    @property
    def enabled(self) -> bool:
        """Whether this compilation should emit or replay provenance."""

        return any((self.manifest_path, self.record_dir, self.replay_dir))


@dataclass(slots=True)
class LLMCallRecord:
    """One canonical compilation LLM request and its exact outcome."""

    index: int
    request_hash: str
    request: dict[str, Any]
    response: str | None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    duration_ms: int = 0
    usage: dict[str, Any] | None = None
    cost_usd: float | None = None
    error: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable call record."""

        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> LLMCallRecord:
        """Load one validated-enough call record from a run bundle."""

        request = data.get("request")
        if not isinstance(request, dict):
            raise ReplayMismatchError("A recorded call has no request object.")
        tool_calls = data.get("tool_calls", [])
        if not isinstance(tool_calls, list):
            raise ReplayMismatchError("A recorded call has invalid tool calls.")
        usage = data.get("usage")
        return cls(
            index=int(data["index"]),
            request_hash=str(data["request_hash"]),
            request=dict(request),
            response=(
                str(data["response"]) if data.get("response") is not None else None
            ),
            tool_calls=[dict(item) for item in tool_calls if isinstance(item, Mapping)],
            duration_ms=int(data.get("duration_ms", 0)),
            usage=dict(usage) if isinstance(usage, Mapping) else None,
            cost_usd=(
                float(data["cost_usd"])
                if isinstance(data.get("cost_usd"), int | float)
                else None
            ),
            error=(
                {str(key): str(value) for key, value in data["error"].items()}
                if isinstance(data.get("error"), Mapping)
                else None
            ),
        )


@dataclass(frozen=True, slots=True)
class ProvenanceManifest:
    """Durable traceability metadata for one compilation."""

    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a defensive copy suitable for JSON serialization."""

        return cast(
            dict[str, Any],
            json.loads(json.dumps(self.data, ensure_ascii=False)),
        )


class ReplayMismatchError(RuntimeError):
    """Raised when a replay bundle cannot exactly satisfy the current run."""


@dataclass(slots=True)
class _ObservedMetrics:
    method: str
    duration_ms: int
    usage: dict[str, Any] | None


class CompilationRecorder:
    """Record exact compiler calls while collecting provider telemetry."""

    def __init__(self) -> None:
        self.calls: list[LLMCallRecord] = []
        self._metrics: list[_ObservedMetrics] = []

    async def on_request(self, event: LLMRequestEvent) -> None:
        """Observe requests through the recording wrapper instead."""

    async def on_response(self, event: LLMResponseEvent) -> None:
        """Capture provider-reported usage and native latency."""

        self._metrics.append(
            _ObservedMetrics(
                method=event.method,
                duration_ms=event.duration_ms,
                usage=dict(event.usage) if event.usage is not None else None,
            )
        )

    async def on_error(self, event: LLMErrorEvent) -> None:
        """The wrapper records the final exception with request context."""

    def consume_metrics(
        self,
        *,
        method: str,
        fallback_duration_ms: int,
    ) -> _ObservedMetrics:
        """Consume matching provider telemetry or synthesize local timing."""

        for index, metrics in enumerate(self._metrics):
            if metrics.method == method:
                return self._metrics.pop(index)
        return _ObservedMetrics(
            method=method,
            duration_ms=fallback_duration_ms,
            usage=None,
        )

    def append(
        self,
        *,
        request: dict[str, Any],
        response: str | None,
        tool_calls: list[dict[str, Any]],
        duration_ms: int,
        usage: dict[str, Any] | None,
        error: BaseException | None = None,
    ) -> None:
        """Append one immutable-in-practice call record."""

        self.calls.append(
            LLMCallRecord(
                index=len(self.calls) + 1,
                request_hash=_hash_json(request),
                request=request,
                response=response,
                tool_calls=tool_calls,
                duration_ms=duration_ms,
                usage=usage,
                cost_usd=_reported_cost(usage),
                error=(
                    {"type": type(error).__name__, "message": str(error)}
                    if error is not None
                    else None
                ),
            )
        )


class RecordingCompilationClient:
    """Transparent compiler client that records exact calls and results."""

    def __init__(
        self,
        inner: LLMClientProtocol,
        recorder: CompilationRecorder,
    ) -> None:
        self.inner = inner
        self.recorder = recorder
        self.model = inner.model
        self._observer_attached = False
        add_observer = getattr(inner, "add_observer", None)
        if callable(add_observer):
            add_observer(recorder)
            self._observer_attached = True

    def close(self) -> None:
        """Detach the metrics observer from a reusable concrete client."""

        if not self._observer_attached:
            return
        observers = getattr(self.inner, "observers", None)
        if isinstance(observers, list) and self.recorder in observers:
            observers.remove(self.recorder)
        self._observer_attached = False

    async def complete(
        self,
        messages: Any,
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Record one text completion."""

        resolved_model = model or self.model
        request = _canonical_request(
            method="complete",
            model=resolved_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra=kwargs,
        )
        started = time.monotonic()
        try:
            response = await self.inner.complete(
                messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except Exception as exc:
            duration_ms = int((time.monotonic() - started) * 1000)
            self.recorder.append(
                request=request,
                response=None,
                tool_calls=[],
                duration_ms=duration_ms,
                usage=None,
                error=exc,
            )
            raise
        if not isinstance(response, str):
            raise TypeError("Compilation client complete() must return a string.")
        elapsed_ms = int((time.monotonic() - started) * 1000)
        metrics = self.recorder.consume_metrics(
            method="complete",
            fallback_duration_ms=elapsed_ms,
        )
        self.recorder.append(
            request=request,
            response=response,
            tool_calls=[],
            duration_ms=metrics.duration_ms,
            usage=metrics.usage,
        )
        return response

    async def complete_with_tools(
        self,
        messages: Any,
        tools: Any,
        *,
        tool_executor: ToolExecutor | None = None,
        dialect: Any = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        max_iterations: int = 10,
        **kwargs: Any,
    ) -> ToolCallResponse:
        """Record one complete tool-using compilation call."""

        resolved_model = model or self.model
        request = _canonical_request(
            method="complete_with_tools",
            model=resolved_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            max_iterations=max_iterations,
            extra=kwargs,
        )
        started = time.monotonic()
        try:
            response = await self.inner.complete_with_tools(
                messages,
                tools,
                tool_executor=tool_executor,
                dialect=dialect,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_iterations=max_iterations,
                **kwargs,
            )
        except Exception as exc:
            duration_ms = int((time.monotonic() - started) * 1000)
            self.recorder.append(
                request=request,
                response=None,
                tool_calls=[],
                duration_ms=duration_ms,
                usage=None,
                error=exc,
            )
            raise
        elapsed_ms = int((time.monotonic() - started) * 1000)
        metrics = self.recorder.consume_metrics(
            method="complete_with_tools",
            fallback_duration_ms=elapsed_ms,
        )
        tool_calls = [record.model_dump(mode="json") for record in response.tool_calls]
        self.recorder.append(
            request=request,
            response=response.content,
            tool_calls=tool_calls,
            duration_ms=metrics.duration_ms,
            usage=metrics.usage,
        )
        return response


class ReplayCompilationClient:
    """Strict offline compiler client backed by one recorded run."""

    def __init__(
        self,
        calls: list[LLMCallRecord],
        *,
        model: str,
        manifest: Mapping[str, Any],
    ) -> None:
        self.model = model
        self.calls = calls
        self.manifest = dict(manifest)
        self._cursor = 0

    @classmethod
    def from_directory(cls, directory: Path) -> ReplayCompilationClient:
        """Load and validate a run recording directory."""

        manifest = _load_json_object(directory / _MANIFEST_FILE)
        calls = _load_calls(directory / _CALLS_FILE)
        models = manifest.get("models")
        model = ""
        if isinstance(models, list) and models:
            model = str(models[0])
        if not model and calls:
            model = str(calls[0].request.get("model", ""))
        if not model:
            raise ReplayMismatchError("The replay bundle does not identify a model.")
        recording = manifest.get("recording")
        if not isinstance(recording, Mapping):
            raise ReplayMismatchError("The replay manifest has no recording metadata.")
        expected_calls_hash = recording.get("calls_sha256")
        actual_calls_hash = _hash_json([call.to_dict() for call in calls])
        if expected_calls_hash != actual_calls_hash:
            raise ReplayMismatchError(
                "The replay call recording does not match its manifest hash."
            )
        return cls(calls, model=model, manifest=manifest)

    def validate_context(
        self,
        *,
        source_text: str,
        variables: Mapping[str, Any],
        system_prompt: str,
        schema: Mapping[str, Any],
        compile_config: Mapping[str, Any],
    ) -> None:
        """Validate all non-resource inputs before replay begins."""

        source_record = self.manifest.get("source")
        variable_record = self.manifest.get("variables")
        if not isinstance(source_record, Mapping) or not isinstance(
            variable_record, Mapping
        ):
            raise ReplayMismatchError(
                "The replay manifest has invalid source or variable metadata."
            )
        expected = {
            "source": source_record.get("sha256"),
            "variables": variable_record.get("sha256"),
            "system prompt": self.manifest.get("system_prompt_sha256"),
            "response schema": self.manifest.get("response_schema_sha256"),
            "compile config": _hash_json(self.manifest.get("compile_config", {})),
        }
        actual = {
            "source": _hash_text(source_text),
            "variables": _hash_json(dict(variables)),
            "system prompt": _hash_text(system_prompt),
            "response schema": _hash_json(schema),
            "compile config": _hash_json(dict(compile_config)),
        }
        mismatches = [
            label
            for label, expected_hash in expected.items()
            if expected_hash != actual[label]
        ]
        if mismatches:
            raise ReplayMismatchError(
                "Replay context does not match the recording: "
                + ", ".join(mismatches)
                + "."
            )

    async def complete(
        self,
        messages: Any,
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Replay one recorded text completion."""

        record = self._consume(
            _canonical_request(
                method="complete",
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra=kwargs,
            )
        )
        if record.response is None or record.error is not None:
            raise ReplayMismatchError(
                f"Recorded call {record.index} did not complete successfully."
            )
        return record.response

    async def complete_with_tools(
        self,
        messages: Any,
        tools: Any,
        *,
        tool_executor: ToolExecutor | None = None,
        dialect: Any = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        max_iterations: int = 10,
        **kwargs: Any,
    ) -> ToolCallResponse:
        """Replay one recorded tool call, validating deterministic tool results."""

        del dialect
        record = self._consume(
            _canonical_request(
                method="complete_with_tools",
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                max_iterations=max_iterations,
                extra=kwargs,
            )
        )
        if record.response is None or record.error is not None:
            raise ReplayMismatchError(
                f"Recorded call {record.index} did not complete successfully."
            )
        tool_records = [
            ToolCallRecord.model_validate(item) for item in record.tool_calls
        ]
        if tool_records and tool_executor is None:
            raise ReplayMismatchError(
                f"Recorded call {record.index} requires a tool executor."
            )
        for tool_record in tool_records:
            if tool_record.name == "ask_user":
                raise ReplayMismatchError(
                    "Run replay does not repeat interactive @ask answers. "
                    "Record non-interactive inputs as variables before replay."
                )
            assert tool_executor is not None
            actual = await tool_executor(tool_record.name, tool_record.arguments)
            if actual != tool_record.result:
                raise ReplayMismatchError(
                    f"Tool result mismatch in call {record.index} for "
                    f"{tool_record.name!r}: local resources changed."
                )
        return ToolCallResponse(
            content=record.response,
            tool_calls=tool_records,
        )

    def assert_consumed(self) -> None:
        """Ensure the current compiler used every recorded call exactly once."""

        if self._cursor != len(self.calls):
            raise ReplayMismatchError(
                f"Replay consumed {self._cursor} of {len(self.calls)} recorded calls."
            )

    def _consume(self, request: dict[str, Any]) -> LLMCallRecord:
        if self._cursor >= len(self.calls):
            raise ReplayMismatchError("Replay requested an unrecorded LLM call.")
        record = self.calls[self._cursor]
        current_hash = _hash_json(request)
        if current_hash != record.request_hash:
            raise ReplayMismatchError(
                f"Replay request {self._cursor + 1} does not match the recording "
                f"(expected {record.request_hash}, got {current_hash})."
            )
        self._cursor += 1
        return record


def create_compilation_client(
    client: LLMClientProtocol | None,
    options: ProvenanceOptions | None,
) -> tuple[CompilationClient, CompilationRecorder | None]:
    """Wrap a live client for recording or load a strict replay client."""

    if options is not None and options.replay_dir is not None:
        return ReplayCompilationClient.from_directory(options.replay_dir), None
    if client is None:
        raise ValueError("A live compilation client is required outside replay mode.")
    if options is not None and (options.record_dir or options.manifest_path):
        recorder = CompilationRecorder()
        return RecordingCompilationClient(client, recorder), recorder
    return client, None


def validate_replay_context(
    client: CompilationClient,
    *,
    source_text: str,
    variables: Mapping[str, Any],
    system_prompt: str,
    schema: Mapping[str, Any],
    compile_config: Mapping[str, Any],
) -> None:
    """Validate manifest-level replay inputs when the client is a replay."""

    if isinstance(client, ReplayCompilationClient):
        client.validate_context(
            source_text=source_text,
            variables=variables,
            system_prompt=system_prompt,
            schema=schema,
            compile_config=compile_config,
        )


def finalize_provenance(
    *,
    options: ProvenanceOptions | None,
    client: CompilationClient,
    recorder: CompilationRecorder | None,
    result: CompositionResult,
    source_text: str,
    source_path: Path | None,
    variables: Mapping[str, Any],
    system_prompt: str,
    schema: Mapping[str, Any],
    compile_config: Mapping[str, Any],
    resources: Mapping[str, Mapping[str, Any]],
    started_at: datetime,
    elapsed_ms: int,
    protection: ProtectionContext,
) -> ProvenanceManifest | None:
    """Build and persist optional provenance artifacts for a compilation."""

    if options is None or not options.enabled:
        return None
    if isinstance(client, ReplayCompilationClient):
        client.assert_consumed()
        calls = client.calls
        mode = "replay"
    else:
        calls = recorder.calls if recorder is not None else []
        mode = "record" if options.record_dir is not None else "manifest"
    if isinstance(client, RecordingCompilationClient):
        client.close()

    usage = _usage_summary(calls)
    artifacts = _artifact_hashes(result)
    manifest_data: dict[str, Any] = {
        "format_version": _FORMAT_VERSION,
        "mode": mode,
        "processor_version": PROCESSOR_VERSION,
        "language_version": LANGUAGE_VERSION,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "duration_ms": elapsed_ms,
        "models": sorted(
            {
                str(call.request.get("model"))
                for call in calls
                if call.request.get("model")
            }
            or {str(compile_config.get("model", ""))}
        ),
        "compile_config": _json_safe(dict(compile_config)),
        "system_prompt_sha256": _hash_text(system_prompt),
        "response_schema_sha256": _hash_json(schema),
        "source": {
            "path": str(source_path) if source_path is not None else None,
            "sha256": _hash_text(source_text),
        },
        "variables": {
            "names": sorted(str(key) for key in variables),
            "sha256": _hash_json(dict(variables)),
            "values_in_manifest": False,
        },
        "resources": {
            str(reference): _json_safe(dict(details))
            for reference, details in sorted(resources.items())
        },
        "lineage": [
            {"stage": "surface lowering", "kind": "structural"},
            {"stage": "macro/module preprocessing", "kind": "structural"},
            {"stage": "directive validation", "kind": "structural"},
            {
                "stage": "composition",
                "kind": "semantic" if calls else "structural",
                "model_calls": len(calls),
            },
            {"stage": "artifact materialization", "kind": "structural"},
        ],
        "usage": usage,
        "artifacts": artifacts,
        "call_count": len(calls),
        "recording_contains_sensitive_content": options.record_dir is not None,
    }
    if calls or options.record_dir is not None or options.replay_dir is not None:
        manifest_data["recording"] = {
            "calls_sha256": _hash_json([call.to_dict() for call in calls]),
            "replay_policy": "strict-no-live-fallback",
        }
    if options.replay_dir is not None:
        manifest_data["replayed_from"] = str(options.replay_dir.resolve())
    manifest = ProvenanceManifest(manifest_data)
    result.provenance = manifest

    if options.record_dir is not None:
        _write_run_bundle(
            options.record_dir,
            manifest,
            calls,
            result,
            protection,
        )
    if options.manifest_path is not None:
        path = protection.authorize_write(
            options.manifest_path,
            reason="Writing the requested compilation provenance manifest",
        )
        _write_json(path, manifest.to_dict())
    return manifest


def record_resource(
    resources: dict[str, dict[str, Any]],
    *,
    reference: str,
    content: str,
) -> None:
    """Record a local compiler resource without persisting its content."""

    resources[reference] = {
        "sha256": _hash_text(content),
        "bytes": len(content.encode("utf-8")),
    }


def _canonical_request(
    *,
    method: str,
    model: str,
    messages: Any,
    temperature: float,
    max_tokens: int | None,
    tools: Any = None,
    max_iterations: int | None = None,
    extra: Mapping[str, Any],
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "method": method,
        "model": model,
        "messages": _json_safe(messages),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "extra": _json_safe(dict(extra)),
    }
    if tools is not None:
        request["tools"] = _json_safe(tools)
    if max_iterations is not None:
        request["max_iterations"] = max_iterations
    return request


def _usage_summary(calls: Iterable[LLMCallRecord]) -> dict[str, Any]:
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    duration_ms = 0
    reported_cost_usd = 0.0
    has_cost = False
    provider_usage: list[dict[str, Any]] = []
    for call in calls:
        duration_ms += call.duration_ms
        usage = call.usage or {}
        prompt_tokens += _numeric_usage(
            usage,
            "prompt_tokens",
            "input_tokens",
        )
        completion_tokens += _numeric_usage(
            usage,
            "completion_tokens",
            "output_tokens",
        )
        total_tokens += _numeric_usage(usage, "total_tokens")
        if call.cost_usd is not None:
            reported_cost_usd += call.cost_usd
            has_cost = True
        if usage:
            provider_usage.append(_json_safe(usage))
    if total_tokens == 0:
        total_tokens = prompt_tokens + completion_tokens
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "llm_duration_ms": duration_ms,
        "reported_cost_usd": reported_cost_usd if has_cost else None,
        "cost_source": "provider" if has_cost else "unavailable",
        "provider_usage": provider_usage,
    }


def _artifact_hashes(result: CompositionResult) -> list[dict[str, Any]]:
    artifacts = [
        {
            "name": "composed_prompt",
            "kind": "primary",
            "sha256": _hash_text(result.composed_prompt),
            "bytes": len(result.composed_prompt.encode("utf-8")),
        }
    ]
    for name, content in sorted(result.prompts.items()):
        artifacts.append(
            {
                "name": name,
                "kind": "prompt",
                "sha256": _hash_text(content),
                "bytes": len(content.encode("utf-8")),
            }
        )
    for name, content in sorted(result.emits.items()):
        artifacts.append(
            {
                "name": name,
                "kind": "emit",
                "sha256": _hash_text(content),
                "bytes": len(content.encode("utf-8")),
            }
        )
    return artifacts


def _write_run_bundle(
    directory: Path,
    manifest: ProvenanceManifest,
    calls: list[LLMCallRecord],
    result: CompositionResult,
    protection: ProtectionContext,
) -> None:
    resolved = protection.authorize_write(
        directory,
        reason="Writing the requested compilation run recording",
    )
    resolved.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        resolved.chmod(0o700)
    _write_json(resolved / _MANIFEST_FILE, manifest.to_dict())
    _write_json(
        resolved / _RESULT_FILE,
        result.to_dict(include_provenance=False),
    )
    _write_jsonl(
        resolved / _CALLS_FILE,
        [call.to_dict() for call in calls],
    )


def _write_json(path: Path, data: Mapping[str, Any]) -> None:
    _write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _write_jsonl(path: Path, records: Iterable[Mapping[str, Any]]) -> None:
    text = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
        for record in records
    )
    _write_text(path, text)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        if os.name != "nt":
            temporary.chmod(0o600)
        temporary.replace(path)
        if os.name != "nt":
            path.chmod(0o600)
    finally:
        temporary.unlink(missing_ok=True)


def _load_calls(path: Path) -> list[LLMCallRecord]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ReplayMismatchError(f"Cannot read replay calls {path}: {exc}") from exc
    calls: list[LLMCallRecord] = []
    for line_number, line in enumerate(lines, start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReplayMismatchError(
                f"Invalid replay call JSON at {path}:{line_number}: {exc}"
            ) from exc
        if not isinstance(value, Mapping):
            raise ReplayMismatchError(
                f"Replay call at {path}:{line_number} is not an object."
            )
        calls.append(LLMCallRecord.from_dict(value))
    return calls


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayMismatchError(f"Cannot read replay manifest {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReplayMismatchError(f"Replay manifest {path} is not a JSON object.")
    if value.get("format_version") != _FORMAT_VERSION:
        raise ReplayMismatchError(
            f"Unsupported replay format version: {value.get('format_version')!r}."
        )
    return value


def _reported_cost(usage: Mapping[str, Any] | None) -> float | None:
    if not usage:
        return None
    for key in ("cost_usd", "response_cost", "total_cost", "cost"):
        value = usage.get(key)
        if isinstance(value, int | float):
            return float(value)
    return None


def _numeric_usage(usage: Mapping[str, Any], *keys: str) -> int:
    for key in keys:
        value = usage.get(key)
        if isinstance(value, int | float):
            return int(value)
    return 0


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_json(value: Any) -> str:
    encoded = json.dumps(
        _json_safe(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return _hash_text(encoded)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, bytes):
        return {"bytes_sha256": hashlib.sha256(value).hexdigest(), "length": len(value)}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, type):
        return f"{value.__module__}.{value.__qualname__}"
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    if isinstance(value, set | frozenset):
        return sorted((_json_safe(item) for item in value), key=repr)
    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe(asdict(value))
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return _json_safe(model_dump(mode="json"))
    return repr(value)


__all__ = [
    "CompilationClient",
    "CompilationRecorder",
    "LLMCallRecord",
    "ProvenanceManifest",
    "ProvenanceOptions",
    "RecordingCompilationClient",
    "ReplayCompilationClient",
    "ReplayMismatchError",
    "create_compilation_client",
    "finalize_provenance",
    "record_resource",
    "validate_replay_context",
]
