"""Progress helpers for Python example runners."""

from __future__ import annotations

import sys
from typing import Any


def weavemark_verbose_event(event_type: str, data: dict[str, Any]) -> None:
    """Print concise WeaveMark controller progress for example runners."""
    message = _format_event(event_type, data)
    if message:
        print(f"[promplet] {message}", file=sys.stderr, flush=True)


def _format_event(event_type: str, data: dict[str, Any]) -> str:
    if event_type == "composing":
        return (
            f"composing round {data.get('compile_effect_round')} "
            f"with {data.get('num_variables')} variable(s), "
            f"model {data.get('model')}"
        )
    if event_type == "tool_call":
        name = data.get("name")
        args = data.get("args") or {}
        target = args.get("file_name") or args.get("question") or ""
        suffix = f" {target}" if target else ""
        return f"tool call: {name}{suffix}"
    if event_type == "tool_result":
        status = "error" if data.get("error") else "ok"
        name = data.get("name")
        file_name = data.get("file")
        size = data.get("size")
        target = f" {file_name}" if file_name else ""
        size_text = f", {size} chars" if size is not None else ""
        return f"tool result: {name}{target} ({status}{size_text})"
    if event_type == "transition":
        text = str(data.get("text") or "").strip()
        return f"transition {data.get('step')}: {text}" if text else "transition"
    if event_type == "compile_effect_round":
        remaining_iterates = data.get("remaining_iterate_count")
        remaining_asks = data.get("remaining_ask_count")
        remaining = remaining_iterates if remaining_iterates is not None else remaining_asks
        return (
            f"completed compile-effect round {data.get('completed_round')}; "
            f"remaining effects: {remaining}"
        )
    if event_type.startswith("iterate_"):
        line = data.get("line")
        turn = data.get("turn") or data.get("turns_used")
        return f"{event_type.replace('_', ' ')} at line {line}, turn {turn}"
    if event_type in {"ask_question", "ask_answer"}:
        return f"{event_type.replace('_', ' ')} round {data.get('round')}"
    if event_type == "issue":
        severity = data.get("severity", "issue")
        message = data.get("message") or data
        return f"{severity}: {message}"
    if event_type == "done":
        return (
            f"done with {data.get('tool_calls_made')} tool call(s), "
            f"{data.get('diagnostics_count')} diagnostic(s), "
            f"{data.get('output_length')} output chars"
        )
    return event_type.replace("_", " ")
