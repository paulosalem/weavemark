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
    assert (destination / "demos" / "orbital-drift" / "index.html").is_file()
    assert (destination / "demos" / "orbital-drift" / "src" / "main.js").is_file()
    assert (destination / "demos" / "transit-city-swarm" / "index.html").is_file()
    assert (
        destination / "demos" / "transit-city-swarm" / "src" / "simulation.js"
    ).is_file()
    assert (destination / "demos" / "ai-kanban" / "index.html").is_file()
    assert (destination / "demos" / "ai-kanban" / "src" / "sqlite-worker.js").is_file()
    assert (destination / "demos" / "ai-kanban" / "vendor" / "sql-wasm.wasm").is_file()
    assert (destination / "demos" / "ai-kanban" / "vendor" / "LICENSE-sql.js").is_file()
    assert (destination / "demos" / "knowledge-cards" / "index.html").is_file()
    assert (
        destination / "demos" / "knowledge-cards" / "manifest.webmanifest"
    ).is_file()
    assert (destination / "demos" / "knowledge-cards" / "sw.js").is_file()
    assert (
        destination / "demos" / "knowledge-cards" / "content" / "packs" / "index.json"
    ).is_file()
    assert (
        destination
        / "demos"
        / "knowledge-cards"
        / "content"
        / "packs"
        / "economics"
        / "cards"
        / "cards.json"
    ).is_file()
    tutorial_html = (destination / "docs" / "tutorial.html").read_text(
        encoding="utf-8"
    )
    assert "github.com/paulosalem/weavemark/blob/main/promplets/" in tutorial_html
    assert "github.com/paulosalem/weavemark/tree/main/examples/" in tutorial_html
    assert 'href="../promplets/' not in tutorial_html
    games_html = (destination / "docs" / "tutorial-games.html").read_text(
        encoding="utf-8"
    )
    assert 'href="../demos/transit-city-swarm/"' in games_html
    assert (
        "github.com/paulosalem/weavemark/tree/main/outputs/implementations/"
        "transit-city-swarm"
    ) in games_html
    implement_html = (destination / "docs" / "tutorial-implement.html").read_text(
        encoding="utf-8"
    )
    assert 'href="../demos/ai-kanban/"' in implement_html
    assert (
        "github.com/paulosalem/weavemark/tree/main/outputs/implementations/"
        "ai-kanban-browser"
    ) in implement_html
    home_html = (destination / "docs" / "index.html").read_text(encoding="utf-8")
    assert 'data-href="../demos/ai-kanban/"' in home_html
    assert 'href="../demos/ai-kanban/" data-live-demo="ai-kanban"' in home_html
    assert (
        'href="../demos/knowledge-cards/" data-live-demo="knowledge-cards"'
        in home_html
    )
    assert (destination / "docs" / "local-demo-links.js").is_file()
    assert (destination / "docs" / "mobile-navigation.js").is_file()
    assert '<script src="mobile-navigation.js?v=20260723" defer></script>' in home_html
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


def test_all_tutorial_source_links_resolve_to_github(tmp_path: Path) -> None:
    builder = _load_builder()
    destination = tmp_path / "site"
    builder.build_site(destination, ROOT)

    for tutorial_path in (destination / "docs").glob("tutorial*.html"):
        html = tutorial_path.read_text(encoding="utf-8")
        for root_name in (
            "examples",
            "outputs",
            "promplets",
            "src",
            "studies",
            "vscode-extension",
        ):
            assert f'href="../{root_name}/' not in html
