"""Tests for dotted-path variable navigation (``@{a.b.c}``).

Covers the shared resolver, compile-time substitution / @if / @match, the
runtime engine renderers, and the TUI scanner's root-collapsing behavior.
"""

from __future__ import annotations

import asyncio
from typing import Any

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.variable_paths import (
    MISSING,
    resolve_variable_path,
    variable_is_defined,
)

# ── shared resolver ───────────────────────────────────────────────────


def test_resolver_flat_key_wins_first() -> None:
    # An exact flat key that literally contains a dot still resolves.
    assert resolve_variable_path({"a.b": 7, "a": {"b": 1}}, "a.b") == 7


def test_resolver_nested_dict() -> None:
    assert resolve_variable_path({"x": {"y": {"z": 42}}}, "x.y.z") == 42


def test_resolver_list_index() -> None:
    data = {"panels": [{"beat": "enter"}, {"beat": "sit"}]}
    assert resolve_variable_path(data, "panels.0.beat") == "enter"
    assert resolve_variable_path(data, "panels.1.beat") == "sit"


def test_resolver_negative_index() -> None:
    assert resolve_variable_path({"xs": [10, 20, 30]}, "xs.-1") == 30


def test_resolver_missing_paths() -> None:
    data = {"a": {"b": 1}, "xs": [0]}
    assert resolve_variable_path(data, "a.c") is MISSING
    assert resolve_variable_path(data, "a.b.c") is MISSING  # descend into scalar
    assert resolve_variable_path(data, "xs.5") is MISSING  # out of range
    assert resolve_variable_path(data, "xs.k") is MISSING  # non-int index
    assert resolve_variable_path(data, "nope") is MISSING


def test_variable_is_defined() -> None:
    data = {"a": {"b": 1, "n": None}}
    assert variable_is_defined(data, "a.b") is True
    assert variable_is_defined(data, "a.n") is False  # None counts as undefined
    assert variable_is_defined(data, "a.z") is False


# ── compile-time substitution / @if / @match ──────────────────────────


async def _compose(spec: str, variables: dict[str, Any]):
    controller = WeaveMarkController(WeaveMarkConfig())
    return await controller.compose(spec, variables)


def test_compile_substitutes_dotted_paths() -> None:
    spec = (
        "Title: @{book.title}\n"
        "First beat: @{panels.0.beat}\n"
        "Second line: @{panels.1.dialogue}\n"
        "Unresolved stays: @{panels.9.beat}\n"
    )
    variables = {
        "book": {"title": "Orion"},
        "panels": [
            {"beat": "cat enters"},
            {"beat": "cat sits", "dialogue": "I run this house."},
        ],
    }
    result = asyncio.run(_compose(spec, variables))
    assert result.errors == []
    text = result.composed_prompt
    assert "Title: Orion" in text
    assert "First beat: cat enters" in text
    assert "Second line: I run this house." in text
    # A path that cannot be resolved is left intact (not blanked).
    assert "@{panels.9.beat}" in text


def test_compile_if_and_match_on_dotted_paths() -> None:
    spec = (
        "@if book.subtitle\n  Subtitle present.\n"
        "@if book.missing\n  SHOULD NOT APPEAR\n"
        "@match panels.0.mood\n"
        '  "grumpy" ==>\n    MOOD GRUMPY\n'
        "  _ ==>\n    other\n"
    )
    variables = {
        "book": {"subtitle": "A Tale"},
        "panels": [{"mood": "grumpy"}],
    }
    result = asyncio.run(_compose(spec, variables))
    assert result.errors == []
    text = result.composed_prompt
    assert "Subtitle present." in text
    assert "SHOULD NOT APPEAR" not in text
    assert "MOOD GRUMPY" in text
    assert "other" not in text


# ── runtime engine renderers ──────────────────────────────────────────


def test_chain_render_resolves_dotted_context() -> None:
    from weavemark.engines.chain import _render

    ctx = {"page": {"index": 3, "beat": "the reveal"}}
    assert _render("Page @{page.index}: @{page.beat}", ctx) == "Page 3: the reveal"
    # Unknown dotted paths stay intact.
    assert _render("@{page.missing}", ctx) == "@{page.missing}"


def test_reflection_render_resolves_dotted_context() -> None:
    from weavemark.engines.reflection import _render

    ctx = {"panels": [{"beat": "enter"}]}
    assert _render("Beat: @{panels.0.beat}", ctx) == "Beat: enter"


# ── TUI scanner collapses dotted leaves to a structured root ───────────


def test_scanner_collapses_dotted_to_root() -> None:
    from weavemark.tui.scanner import scan_spec

    spec = (
        "T: @{book.title}\n"
        "P1: @{panels.0.beat} / @{panels.0.dialogue}\n"
        "P2: @{panels.1.beat}\n"
        "Plain: @{premise}\n"
    )
    meta = scan_spec(spec)
    by_name = {i.name: i.input_type for i in meta.inputs}
    assert by_name["book"] == "multiline"
    assert by_name["panels"] == "multiline"
    assert by_name["premise"] == "text"
    # No bogus per-leaf inputs.
    assert not any("." in i.name for i in meta.inputs)
