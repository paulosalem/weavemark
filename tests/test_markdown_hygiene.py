"""Tests for repository Markdown rendering hygiene."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).parents[1]


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "markdown_hygiene",
        ROOT / "scripts" / "check_markdown_hygiene.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_tracked_markdown_is_renderable() -> None:
    checker = _load_checker()

    assert checker.check_repository(ROOT) == []


def test_checker_rejects_unclosed_and_untyped_fences() -> None:
    checker = _load_checker()
    path = Path("README.md")

    assert checker._check_fences(path, "```bash\necho ok", True) == [
        "README.md:1: unclosed fenced code block"
    ]
    assert checker._check_fences(path, "```\nplain\n```\n", True) == [
        "README.md:1: fenced block needs a language"
    ]
    assert checker._check_fences(path, "```bash\necho ok\n```\n", True) == []


def test_checker_rejects_missing_and_escaped_local_links(tmp_path: Path) -> None:
    checker = _load_checker()
    docs = tmp_path / "docs"
    docs.mkdir()
    path = docs / "guide.md"
    text = "[missing](missing.md)\n\n[escaped](../../outside.md)\n"
    path.write_text(text, encoding="utf-8")
    tokens = MarkdownIt("commonmark").parse(text)

    assert checker._check_local_links(
        tmp_path,
        path,
        Path("docs/guide.md"),
        tokens,
    ) == [
        "docs/guide.md:1: missing local target 'missing.md'",
        "docs/guide.md:3: local target escapes repository '../../outside.md'",
    ]
