"""GitHub Pages artifact and link-contract tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "pages_builder",
        ROOT / "scripts" / "build_pages_site.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pages_artifact_is_complete_and_excludes_lfs(tmp_path: Path) -> None:
    builder = _load_builder()
    destination = tmp_path / "site"

    copied = builder.build_site(destination, ROOT)

    assert builder.validate_site(destination) == []
    assert Path("docs/index.html") in copied
    assert Path("promplets/catalog/standalone/program-review-checklist.weavemark.md") in copied
    assert (destination / ".nojekyll").is_file()
    assert 'url=docs/index.html' in (destination / "index.html").read_text(
        encoding="utf-8"
    )
    assert (destination / "docs" / "tutorial-comic.jpg").is_file()
    favicon = destination / "docs" / "weavemark_favicon.png"
    assert favicon.is_file()
    source_favicon = ROOT / "docs" / "weavemark_favicon.png"
    assert favicon.read_bytes() == source_favicon.read_bytes()
    for html_path in (destination / "docs").glob("*.html"):
        html = html_path.read_text(encoding="utf-8")
        assert 'rel="icon" href="weavemark_favicon.png"' in html
        assert 'rel="icon" href="weavemark_logo.png"' not in html
    root_html = (destination / "index.html").read_text(encoding="utf-8")
    assert 'rel="icon" href="docs/weavemark_favicon.png"' in root_html
    assert not (
        destination
        / "examples"
        / "saved-artifact-workflows"
        / "comic-strip-en"
        / "outputs"
        / "comic-strip.png"
    ).exists()
    assert not (
        destination
        / "examples"
        / "saved-artifact-workflows"
        / "childrens-book-orion-en"
        / "outputs"
        / "book.html"
    ).exists()


def test_pages_artifact_contains_no_private_context(tmp_path: Path) -> None:
    builder = _load_builder()
    destination = tmp_path / "site"
    builder.build_site(destination, ROOT)

    errors = builder.validate_site(destination)

    assert not any("private context" in error for error in errors)
    assert not any("Git LFS pointer" in error for error in errors)
