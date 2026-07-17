"""Deterministic directive-name and duplicate-declaration validation."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

import pytest

from weavemark.compilation.args import parse_header_args
from weavemark.compilation.directive_registry import validate_directive_names
from weavemark.controller import WeaveMarkConfig, WeaveMarkController


class _NeverClient:
    async def complete_with_tools(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Invalid directives must fail before an LLM call.")


def test_unknown_directives_report_lines_and_nearest_name() -> None:
    source = "@refien target.md\n@if enabled\n  @mystery value\n"

    assert validate_directive_names(source, {"refine": object()}) == [
        "Unknown directive '@refien' at line 1. Did you mean '@refine'?",
        "Unknown directive '@mystery' at line 3.",
    ]


def test_validator_ignores_literal_and_opaque_regions() -> None:
    source = textwrap.dedent(
        """
        Contact dev@example.com.
        @@literal directive
        ```weavemark
        @typo in a fence
        ```
        @tool lookup
          Example payload:
          @typo inside tool documentation
        @note
          @typo inside a note
        @if enabled
          Valid branch.
        """
    ).strip()

    assert validate_directive_names(source, {}) == []


def test_local_semantic_definition_is_a_known_directive() -> None:
    source = "@custom value"

    assert validate_directive_names(source, {"custom": object()}) == []


def test_duplicate_named_parameters_are_rejected_without_overwriting() -> None:
    parsed = parse_header_args("format: json format: markdown")

    assert parsed.options == {"format": "json"}
    assert parsed.errors == ["Duplicate named parameter 'format'."]


@pytest.mark.asyncio
async def test_unknown_nested_directive_fails_before_llm(tmp_path: Path) -> None:
    controller = WeaveMarkController(
        WeaveMarkConfig(),
        client=_NeverClient(),
    )

    result = await controller.compose(
        "@if enabled\n  @refien ./base.weavemark.md",
        variables={"enabled": True},
        base_dir=tmp_path,
    )

    assert result.composed_prompt == ""
    assert result.errors == [
        "Unknown directive '@refien' at line 2. Did you mean '@refine'?"
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("source", "message"),
    (
        (
            "@compile format: json\n@compile format: markdown",
            "Duplicate @compile directive.",
        ),
        (
            "@tool lookup\n  First.\n@tool Lookup\n  Second.",
            "Duplicate @tool declaration: Lookup",
        ),
        (
            "@execute single-call\n@execute chain",
            "Duplicate @execute directive.",
        ),
        (
            '@output "First."\n@output "Second."',
            "Duplicate @output contract for scope 'default'.",
        ),
        (
            "@package template: one.md file: out.html\n"
            "@package template: two.md file: out.html",
            "Duplicate @package output target: out.html",
        ),
        (
            "@prompt Intro\n  First.\n@prompt intro\n  Second.",
            "Duplicate @prompt declaration (names are case-insensitive): intro",
        ),
    ),
)
async def test_duplicate_structural_declarations_are_errors(
    tmp_path: Path,
    source: str,
    message: str,
) -> None:
    result = await WeaveMarkController(WeaveMarkConfig()).compose(
        source,
        base_dir=tmp_path,
    )

    assert message in result.errors
