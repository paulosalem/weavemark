"""Bidirectional JSONL interaction protocol tests."""

from __future__ import annotations

import io

from weavemark.interactions import JsonlStdinInteraction
from weavemark.protection import ProtectionRequest


def _request() -> ProtectionRequest:
    return ProtectionRequest(
        capability="Python code execution",
        subject="/tmp/market_data.py",
        fingerprint="sha256:example",
        reason="Executing bound capability 'finance_data'",
        danger="Python executes with the user's operating-system permissions.",
        config_key="protections.pythonCode",
    )


def test_jsonl_interaction_emits_request_and_accepts_scoped_response() -> None:
    events: list[tuple[str, dict[str, object], str | None]] = []
    stream = io.StringIO(
        '{"version":1,"type":"protection_response","request_id":"request-1",'
        '"decision":"allow_once"}\n'
    )
    interaction = JsonlStdinInteraction(
        lambda event_type, data, phase: events.append((event_type, data, phase)),
        stream=stream,
        id_factory=lambda: "request-1",
    )

    assert interaction.request_protection(_request()) == "allow_once"
    assert [event[0] for event in events] == [
        "protection_request",
        "interaction_resolved",
    ]
    assert events[0][1]["request_id"] == "request-1"
    assert events[0][1]["fingerprint"] == "sha256:example"
    assert events[0][2] == "interaction"


def test_jsonl_interaction_fails_closed_on_mismatched_response() -> None:
    events: list[tuple[str, dict[str, object], str | None]] = []
    interaction = JsonlStdinInteraction(
        lambda event_type, data, phase: events.append((event_type, data, phase)),
        stream=io.StringIO(
            '{"version":1,"type":"protection_response","request_id":"wrong",'
            '"decision":"allow_remember"}\n'
        ),
        id_factory=lambda: "request-1",
    )

    assert interaction.request_protection(_request()) == "deny_once"
    assert events[-1][0] == "interaction_failed"
    assert "request ID" in str(events[-1][1]["error"])


def test_jsonl_interaction_fails_closed_on_eof() -> None:
    events: list[tuple[str, dict[str, object], str | None]] = []
    interaction = JsonlStdinInteraction(
        lambda event_type, data, phase: events.append((event_type, data, phase)),
        stream=io.StringIO(""),
        id_factory=lambda: "request-1",
    )

    assert interaction.request_protection(_request()) == "deny_once"
    assert events[-1][0] == "interaction_failed"
    assert "closed" in str(events[-1][1]["error"])
