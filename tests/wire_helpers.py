"""Helpers for constructing strict semantic compiler responses in tests."""

from __future__ import annotations

import json
from typing import Any


def compiler_response(
    prompt: str = "",
    *,
    prompts: dict[str, str | dict[str, Any]] | None = None,
    compile: dict[str, Any] | None = None,
    tools: list[dict[str, Any]] | None = None,
    bindings: list[dict[str, str]] | None = None,
    execution: dict[str, Any] | None = None,
    emits: dict[str, str] | None = None,
    outputs: dict[str, dict[str, Any]] | None = None,
    packages: list[dict[str, str]] | None = None,
    references: dict[str, str] | None = None,
    directives: list[dict[str, Any]] | None = None,
    analysis: str = "",
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    suggestions: list[str] | None = None,
) -> str:
    """Return one complete strict compiler-result JSON object."""
    if prompts is None:
        prompt_payloads = (
            {"default": {"text": prompt, "role": None}}
            if prompt
            else {}
        )
    else:
        prompt_payloads = {
            name: (
                {"text": value, "role": None}
                if isinstance(value, str)
                else value
            )
            for name, value in prompts.items()
        }
    return json.dumps(
        {
            "prompt": prompt,
            "prompts": prompt_payloads,
            "compile": compile or {},
            "tools": tools or [],
            "bindings": bindings or [],
            "execution": execution or {},
            "emits": emits or {},
            "outputs": outputs or {},
            "packages": packages or [],
            "references": references or {},
            "directives": directives or [],
            "analysis": analysis,
            "warnings": warnings or [],
            "errors": errors or [],
            "suggestions": suggestions or [],
        },
        ensure_ascii=False,
    )


__all__ = ["compiler_response"]
