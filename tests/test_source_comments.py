"""Tests for Markdown-native comments in WeaveMark source."""

from __future__ import annotations

from pathlib import Path

import pytest

from weavemark.api import compile_text
from weavemark.compilation.macros import preprocess_weavemark
from weavemark.source_comments import strip_markdown_comments


def test_strips_block_and_inline_html_comments() -> None:
    source = (
        "<!-- Save as example.weavemark.md -->\n"
        "# Brief\n"
        "Keep <!-- author-only rationale -->this instruction.\n"
        "Join<!-- without merging -->words.\n"
    )

    result = strip_markdown_comments(source)

    assert not result.errors
    assert result.text == "\n# Brief\nKeep this instruction.\nJoin words.\n"


def test_preserves_html_comment_text_inside_code() -> None:
    source = (
        "Use `<!-- literal inline code -->` exactly.\n\n"
        "```html\n"
        "<!-- literal fenced code -->\n"
        "```\n"
        "~~~html\n"
        "<!-- literal tilde-fenced code -->\n"
        "~~~\n"
    )

    result = strip_markdown_comments(source)

    assert not result.errors
    assert result.text == source


def test_unmatched_backtick_does_not_hide_a_comment() -> None:
    result = strip_markdown_comments("Unmatched ` marker <!-- private -->\n")

    assert not result.errors
    assert result.text == "Unmatched ` marker \n"


def test_preprocessor_strips_comments_but_preserves_markdown_headings(
    tmp_path: Path,
) -> None:
    result = preprocess_weavemark(
        "<!-- private -->\n# Public heading\n\nPrompt body.",
        tmp_path,
    )

    assert not result.errors
    assert result.text == "# Public heading\n\nPrompt body."


@pytest.mark.asyncio
async def test_public_compile_api_never_emits_html_comments() -> None:
    result = await compile_text(
        "<!-- private -->\n# Public heading\nKeep <!-- hidden -->this."
    )

    assert not result.errors
    assert result.composed_prompt == "# Public heading\nKeep this."
