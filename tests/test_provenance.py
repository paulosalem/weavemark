"""Compilation provenance, recording, replay, and version-contract tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallRecord, ToolCallResponse
from ellements.core.observability import LLMResponseEvent

import weavemark
from tests.wire_helpers import compiler_response
from weavemark.api import CompileOptions, compile_text
from weavemark.app import create_parser
from weavemark.compilation.provenance import (
    ProvenanceOptions,
    ReplayMismatchError,
)
from weavemark.protection import ProtectionContext, ProtectionSettings


class RecordingFakeClient:
    """Deterministic compiler client with provider-like telemetry."""

    def __init__(self) -> None:
        self.model = "test/provider-model"
        self.observers: list[Any] = []
        self.calls = 0

    def add_observer(self, observer: Any) -> None:
        self.observers.append(observer)

    async def complete_with_tools(
        self,
        messages: Any,
        tools: Any,
        *,
        tool_executor=None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        max_iterations: int = 10,
        **kwargs: Any,
    ) -> ToolCallResponse:
        del messages, tools, temperature, max_tokens, max_iterations, kwargs
        self.calls += 1
        assert tool_executor is not None
        arguments = {"text": "Applied @style and completed compilation."}
        tool_result = await tool_executor("log_transition", arguments)
        response = ToolCallResponse(
            content=compiler_response("A concise explanation of caching."),
            tool_calls=[
                ToolCallRecord(
                    name="log_transition",
                    arguments=arguments,
                    result=tool_result,
                )
            ],
        )
        event = LLMResponseEvent(
            call_id=f"call-{self.calls}",
            method="complete_with_tools",
            model=f"provider-resolved/{model or self.model}",
            response=response.content,
            duration_ms=123,
            tool_calls=[
                record.model_dump(mode="json") for record in response.tool_calls
            ],
            usage={
                "prompt_tokens": 100,
                "completion_tokens": 25,
                "total_tokens": 125,
                "cost_usd": 0.0042,
            },
        )
        for observer in list(self.observers):
            await observer.on_response(event)
        return response

    async def complete(self, *args: Any, **kwargs: Any) -> str:
        raise AssertionError("This test does not expect a plain completion.")


def _protection(tmp_path: Path) -> ProtectionContext:
    return ProtectionContext.create(
        ProtectionSettings(),
        entrypoint_dir=tmp_path,
        invocation_dir=tmp_path,
        approvals_path=tmp_path / "approvals.json",
    )


@pytest.mark.asyncio
async def test_recorded_run_reports_usage_cost_and_replays_offline(
    tmp_path: Path,
) -> None:
    source = '@style "concise"\n  Explain caching.\n'
    recording = tmp_path / "recording"
    client = RecordingFakeClient()
    options = CompileOptions(model=client.model)

    recorded = await compile_text(
        source,
        {"audience": "developers"},
        base_dir=tmp_path,
        options=options,
        client=client,
        protection_context=_protection(tmp_path),
        provenance=ProvenanceOptions(record_dir=recording),
        source_path=tmp_path / "example.weavemark.md",
    )

    assert recorded.errors == []
    assert client.calls == 1
    assert recorded.provenance is not None
    usage = recorded.provenance.to_dict()["usage"]
    assert usage["prompt_tokens"] == 100
    assert usage["completion_tokens"] == 25
    assert usage["total_tokens"] == 125
    assert usage["llm_duration_ms"] == 123
    assert usage["reported_cost_usd"] == pytest.approx(0.0042)
    assert usage["cost_source"] == "provider"
    assert (recording / "manifest.json").is_file()
    assert (recording / "calls.jsonl").is_file()
    assert (recording / "result.json").is_file()
    if os.name != "nt":
        assert recording.stat().st_mode & 0o777 == 0o700
        assert (recording / "calls.jsonl").stat().st_mode & 0o777 == 0o600

    offline_client = RecordingFakeClient()
    replayed = await compile_text(
        source,
        {"audience": "developers"},
        base_dir=tmp_path,
        options=options,
        client=offline_client,
        protection_context=_protection(tmp_path),
        provenance=ProvenanceOptions(replay_dir=recording),
        source_path=tmp_path / "example.weavemark.md",
    )

    assert offline_client.calls == 0
    assert replayed.composed_prompt == recorded.composed_prompt
    assert replayed.transitions == recorded.transitions
    assert replayed.provenance is not None
    assert replayed.provenance.to_dict()["mode"] == "replay"


@pytest.mark.asyncio
async def test_replay_fails_on_source_mismatch(tmp_path: Path) -> None:
    recording = tmp_path / "recording"
    client = RecordingFakeClient()
    options = CompileOptions(model=client.model)
    await compile_text(
        '@style "concise"\n  Explain caching.\n',
        base_dir=tmp_path,
        options=options,
        client=client,
        protection_context=_protection(tmp_path),
        provenance=ProvenanceOptions(record_dir=recording),
    )

    with pytest.raises(ReplayMismatchError, match="does not match"):
        await compile_text(
            '@style "detailed"\n  Explain caching.\n',
            base_dir=tmp_path,
            options=options,
            client=RecordingFakeClient(),
            protection_context=_protection(tmp_path),
            provenance=ProvenanceOptions(replay_dir=recording),
        )


@pytest.mark.asyncio
async def test_manifest_only_is_optional_and_omits_variable_values(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "provenance.json"
    result = await compile_text(
        "Hello @{name}.",
        {"name": "sensitive value"},
        base_dir=tmp_path,
        protection_context=_protection(tmp_path),
        provenance=ProvenanceOptions(manifest_path=manifest_path),
    )

    assert result.errors == []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["mode"] == "manifest"
    assert manifest["call_count"] == 0
    assert manifest["variables"]["names"] == ["name"]
    assert manifest["variables"]["values_in_manifest"] is False
    assert "sensitive value" not in manifest_path.read_text(encoding="utf-8")


def test_version_contract_and_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert weavemark.__version__ == "0.9.0"
    assert weavemark.LANGUAGE_VERSION == "0.9"
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])

    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == (
        "weavemark 0.9.0 (WeaveMark language 0.9)"
    )
