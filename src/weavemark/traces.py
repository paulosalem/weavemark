"""Readable execution traces for WeaveMark runtime strategies."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from ellements.execution import StepRecord

# Image steps carry their payload as a long base64 string (a ``b64_json`` field or
# a bare blob returned as the step response). Rendering that verbatim bloats a
# trace to megabytes and reads as noise, so image payloads are elided.
_B64_ELIDE_THRESHOLD = 256
_B64_CHARS = re.compile(r"[A-Za-z0-9+/=]+")


def _looks_like_base64_image(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < _B64_ELIDE_THRESHOLD:
        return False
    if stripped.startswith("data:image/"):
        return True
    return _B64_CHARS.fullmatch(stripped) is not None


def _elide(text: str) -> str:
    if _looks_like_base64_image(text):
        return f"<base64 image data: {len(text):,} chars elided>"
    return text


def _redact_payloads(value: Any) -> Any:
    """Recursively elide base64 image payloads anywhere in *value*."""

    if isinstance(value, str):
        return _elide(value)
    if isinstance(value, Mapping):
        return {key: _redact_payloads(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact_payloads(item) for item in value]
    return value


def render_execution_trace_markdown(
    *,
    spec: str,
    model: str,
    engine: str,
    output: str,
    steps: Sequence[StepRecord],
    metadata: Mapping[str, Any] | None = None,
) -> str:
    """Render a multi-step execution result as inspectable Markdown."""

    lines = [
        "# WeaveMark Execution Trace",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Spec | `{spec}` |",
        f"| Model | `{model}` |",
        f"| Engine | `{engine}` |",
        f"| Steps | {len(steps)} |",
        "",
    ]
    if metadata:
        lines.extend(
            [
                "## Execution metadata",
                "",
                _fence(_json_dumps(_redact_payloads(metadata)), "json"),
                "",
            ]
        )

    lines.extend(["## Steps", ""])
    if not steps:
        lines.extend(["No intermediate steps were recorded.", ""])
    for index, step in enumerate(steps, start=1):
        lines.extend(
            [
                f"### {index}. {step.name}",
                "",
                f"- Prompt key: `{step.prompt_key}`",
            ]
        )
        if step.metadata:
            lines.extend(
                [
                    "- Metadata:",
                    "",
                    _fence(_json_dumps(_redact_payloads(step.metadata)), "json"),
                ]
            )
        lines.extend(
            [
                "- Response:",
                "",
                _fence(_elide(step.response), "markdown"),
                "",
            ]
        )

    lines.extend(
        [
            "## Final output",
            "",
            _fence(_elide(output), "markdown"),
            "",
        ]
    )
    return "\n".join(lines)


def execution_result_to_dict(
    *,
    output: str,
    steps: Sequence[StepRecord],
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert an execution result into JSON-serializable trace data."""

    return {
        "output": output,
        "steps": [
            {
                "name": step.name,
                "prompt_key": step.prompt_key,
                "response": step.response,
                "metadata": dict(step.metadata),
            }
            for step in steps
        ],
        "metadata": dict(metadata or {}),
    }


def _json_dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, default=str)


def _fence(content: str, language: str) -> str:
    fence = "```"
    while fence in content:
        fence += "`"
    return f"{fence}{language}\n{content}\n{fence}"


__all__ = ["execution_result_to_dict", "render_execution_trace_markdown"]
