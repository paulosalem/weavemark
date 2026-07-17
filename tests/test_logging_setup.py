"""Tests for WeaveMark LLM call logging wiring (``weavemark.logging_setup``).

Covers the deterministic pieces (no LLM required):
- the on-by-default toggle and its ``WEAVEMARK_LOG`` opt-out values
- the log directory default (``~/.weavemark/logs``) and ``WEAVEMARK_LOG_DIR`` override
- ``new_client`` attaching a JSONL logging observer only when logging is enabled
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ellements.core.observability import LLMRequestEvent, LLMResponseEvent

from weavemark.discovery.config import GLOBAL_DIR
from weavemark.logging_policy import LoggingSettings
from weavemark.logging_setup import (
    PolicyPromptLogger,
    default_log_dir,
    logging_enabled,
    new_client,
)
from weavemark.protection import ProtectionContext, ProtectionSettings

_MODEL = "openai/gpt-5.5"


def test_logging_enabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    assert logging_enabled() is True


@pytest.mark.parametrize("value", ["0", "off", "false", "no", "OFF", "False"])
def test_logging_disabled_by_opt_out_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG", value)
    assert logging_enabled() is False


@pytest.mark.parametrize("value", ["1", "on", "true", "yes", ""])
def test_logging_enabled_for_other_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG", value)
    assert logging_enabled() is True


def test_default_log_dir_uses_global_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    monkeypatch.delenv("WEAVEMARK_LOG_DIR", raising=False)
    assert default_log_dir() == GLOBAL_DIR / "logs"


def test_default_log_dir_honors_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path / "custom"))
    assert default_log_dir() == tmp_path / "custom"


def test_default_log_dir_none_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG", "0")
    assert default_log_dir() is None


def test_new_client_attaches_logger_when_enabled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path / "logs"))
    client = new_client(model=_MODEL)
    observer_names = {type(o).__name__ for o in client.observers}
    assert "PolicyPromptLogger" in observer_names
    # The logger creates its directory eagerly so the first call can write.
    assert (tmp_path / "logs").is_dir()


def test_new_client_has_no_logger_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG", "0")
    client = new_client(model=_MODEL)
    assert client.observers == []


def test_protected_client_uses_the_same_explicit_logging_policy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path / "logs"))
    protection = ProtectionContext.create(
        ProtectionSettings(),
        entrypoint_dir=tmp_path,
        invocation_dir=tmp_path,
        approvals_path=tmp_path / "approvals.json",
    )

    client = new_client(model=_MODEL, protection=protection)

    assert {type(observer).__name__ for observer in client.observers} == {
        "PolicyPromptLogger"
    }
    assert (tmp_path / "logs").is_dir()


def test_llm_call_logging_can_be_disabled_independently(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path / "logs"))
    client = new_client(
        model=_MODEL,
        logging_settings=LoggingSettings(llm_calls=False),
    )

    assert client.observers == []


@pytest.mark.asyncio
async def test_default_policy_keeps_text_and_omits_binary(
    tmp_path: Path,
) -> None:
    logger = PolicyPromptLogger(tmp_path, LoggingSettings())
    await logger.on_request(
        LLMRequestEvent(
            call_id="call-1",
            method="complete",
            model=_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "ticker=MSFT"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64,AAAA",
                            },
                        },
                    ],
                }
            ],
            temperature=0.3,
            max_tokens=None,
        )
    )
    await logger.on_response(
        LLMResponseEvent(
            call_id="call-1",
            method="complete",
            model=_MODEL,
            response="The textual answer.",
            duration_ms=12,
            usage={"total_tokens": 42},
            metadata={"b64_json": "BBBB"},
        )
    )

    record = next(tmp_path.glob("llm-log-*.jsonl")).read_text(encoding="utf-8")
    assert "ticker=MSFT" in record
    assert "The textual answer." in record
    assert '"total_tokens":42' in record
    assert "AAAA" not in record
    assert "BBBB" not in record
    assert "binary" in record


@pytest.mark.asyncio
async def test_policy_can_disable_request_response_tools_and_usage(
    tmp_path: Path,
) -> None:
    logger = PolicyPromptLogger(
        tmp_path,
        LoggingSettings(
            llm_requests=False,
            llm_responses=False,
            tool_data=False,
            usage=False,
        ),
    )
    await logger.on_request(
        LLMRequestEvent(
            call_id="call-2",
            method="complete_with_tools",
            model=_MODEL,
            messages=[{"role": "user", "content": "secret prompt"}],
            temperature=0.3,
            max_tokens=None,
            tools=[{"type": "function", "function": {"name": "read_file"}}],
        )
    )
    await logger.on_response(
        LLMResponseEvent(
            call_id="call-2",
            method="complete_with_tools",
            model=_MODEL,
            response="secret response",
            duration_ms=12,
            tool_calls=[{"name": "read_file", "result": "secret tool result"}],
            usage={"total_tokens": 42},
        )
    )

    record = next(tmp_path.glob("llm-log-*.jsonl")).read_text(encoding="utf-8")
    assert "secret prompt" not in record
    assert "secret response" not in record
    assert "secret tool result" not in record
    assert '"usage":null' in record
