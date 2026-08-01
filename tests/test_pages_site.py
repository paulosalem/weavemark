"""GitHub Pages artifact and link-contract tests."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

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
    assert (
        Path("promplets/catalog/standalone/prompt-refactoring-pipeline.weavemark.md")
        in copied
    )
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
    assert "weavemark_social.png" in root_html
    assert 'rel="canonical" href="https://paulosalem.github.io/weavemark/"' in root_html
    for public_file in ("llms.txt", "robots.txt", "sitemap.xml"):
        assert (destination / public_file).is_file()
    assert (destination / "docs" / "weavemark_social.png").is_file()
    for collection, target in (
        ("executable", "market-snapshot"),
        ("standalone", "ai-kanban-board"),
    ):
        replay = (
            destination
            / "promplets"
            / "replays"
            / "catalog"
            / collection
            / target
        )
        assert (replay / "manifest.json").is_file()
        assert (replay / "calls.jsonl").is_file()
        assert (replay / "result.json").is_file()
    assert not (destination / "demos" / "orbital-drift").exists()
    assert not (destination / "demos" / "transit-city-swarm").exists()
    assert (destination / "demos" / "ai-kanban" / "index.html").is_file()
    assert (destination / "demos" / "ai-kanban" / "src" / "sqlite-worker.js").is_file()
    assert (destination / "demos" / "ai-kanban" / "vendor" / "sql-wasm.wasm").is_file()
    assert (destination / "demos" / "ai-kanban" / "vendor" / "LICENSE-sql.js").is_file()
    for module in (
        "app.js",
        "bootstrap.js",
        "constants.js",
        "coordination.js",
        "file-workspace.js",
        "markdown.js",
        "output-selection.js",
        "packets.js",
        "provider-adapter.js",
        "repository.js",
        "save-queue.js",
        "shell-quote.js",
        "sqlite-client.js",
        "sqlite-worker.js",
        "surfaces.js",
        "validation.js",
    ):
        assert (
            destination / "demos" / "ai-kanban" / "src" / module
        ).is_file(), module
    assert (
        destination / "demos" / "ai-kanban" / "templates" / "root" / "AGENTS.md"
    ).is_file()
    assert (
        destination
        / "demos"
        / "ai-kanban"
        / "templates"
        / "skill"
        / "ai_kanban.py"
    ).is_file()
    assert (
        destination / "demos" / "ai-kanban" / "compiled-spec.md"
    ).is_file()
    demo_html = (
        destination / "demos" / "ai-kanban" / "index.html"
    ).read_text(encoding="utf-8")
    assert 'href="../../promplets/catalog/standalone/ai-kanban-board.weavemark.md"' in demo_html
    assert 'href="../../docs/tutorial-implement.html"' in demo_html
    assert 'href="./compiled-spec.md"' in demo_html
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
    assert (destination / "demos" / "orion-storybook" / "index.html").is_file()
    assert (
        destination / "demos" / "orion-storybook" / "pages" / "page-12.jpg"
    ).is_file()
    assert (destination / "demos" / "arcana" / "index.html").is_file()
    assert (destination / "demos" / "arcana" / "deck-data.js").is_file()
    assert (
        destination / "demos" / "arcana" / "assets" / "cards" / "card-54.png"
    ).is_file()
    assert (
        destination / "demos" / "arcana" / "assets" / "card-back.png"
    ).is_file()
    tutorial_html = (destination / "docs" / "tutorial.html").read_text(
        encoding="utf-8"
    )
    assert (
        "github.com/paulosalem/weavemark/blob/main/promplets/"
        "catalog/executable/financial-independence-goal-plan.weavemark.md?plain=1"
    ) in tutorial_html
    assert 'href="../promplets/' not in tutorial_html
    assert not (destination / "docs" / "tutorial-games.html").exists()
    implement_html = (destination / "docs" / "tutorial-implement.html").read_text(
        encoding="utf-8"
    )
    assert 'href="../demos/ai-kanban/"' in implement_html
    assert (
        "github.com/paulosalem/weavemark/tree/main/outputs/implementations/"
        "ai-kanban-browser"
    ) in implement_html
    home_html = (destination / "docs" / "index.html").read_text(encoding="utf-8")
    assert "Orbital Drift" not in home_html
    assert "Transit City Swarm" not in home_html
    assert 'data-href="../demos/ai-kanban/"' in home_html
    assert 'href="../demos/ai-kanban/" data-live-demo="ai-kanban"' in home_html
    assert (
        'href="../demos/knowledge-cards/" data-live-demo="knowledge-cards"'
        in home_html
    )
    assert 'href="../demos/orion-storybook/" data-live-demo="orion-storybook"' in home_html
    assert 'href="../demos/arcana/" data-live-demo="arcana"' in home_html
    assert "Fifty-five generated illustrated cards" in home_html
    assert "weavemark library market-snapshot --replay --verbose" in home_html
    assert 'data-result-href="../demos/orion-storybook/"' in home_html
    assert 'data-result-href="../demos/ai-kanban/"' in home_html
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

    source_link_pattern = re.compile(
        r"https://github\.com/paulosalem/weavemark/blob/"
        r"""[^"' <>)]+\.weavemark\.md(?:\?[^"' <>)]+)?"""
    )
    invalid_source_links: list[str] = []
    for path in destination.rglob("*"):
        if path.suffix.casefold() not in {".html", ".md"}:
            continue
        for match in source_link_pattern.finditer(path.read_text(encoding="utf-8")):
            if not match.group(0).endswith("?plain=1"):
                invalid_source_links.append(
                    f"{path.relative_to(destination)}: {match.group(0)}"
                )
    assert invalid_source_links == []


def test_pages_artifact_contains_no_private_context(tmp_path: Path) -> None:
    builder = _load_builder()
    destination = tmp_path / "site"
    builder.build_site(destination, ROOT)

    errors = builder.validate_site(destination)

    assert not any("private context" in error for error in errors)
    assert not any("Git LFS pointer" in error for error in errors)


def test_arcana_live_demo_is_published_independently(tmp_path: Path) -> None:
    builder = _load_builder()
    destination = tmp_path / "site"

    builder.build_site(destination)

    demo = destination / "demos" / "arcana"
    assert (demo / "index.html").is_file()
    assert (demo / "deck-data.js").is_file()
    assert (demo / "assets" / "card-back.png").is_file()
    assert (demo / "assets" / "cards" / "prototype.png").is_file()
    assert (demo / "assets" / "cards" / "card-54.png").is_file()
    home = (destination / "docs" / "index.html").read_text(encoding="utf-8")
    assert 'href="../demos/arcana/" data-live-demo="arcana"' in home
    assert (
        "github.com/paulosalem/weavemark/blob/main/"
        "promplets/catalog/arcana/app.weavemark.md?plain=1"
    ) in home
    assert (
        "github.com/paulosalem/weavemark/blob/main/"
        "promplets/catalog/arcana/cards.weavemark.md?plain=1"
    ) in home


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


def test_pages_publisher_allows_only_explicit_regular_assets_and_rejects_ignored_or_symlinked_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    builder = _load_builder()
    root = tmp_path / "repository"
    assets = root / "demo" / "assets"
    assets.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
    tracked = assets / "tracked.js"
    tracked.write_text("console.log('tracked');\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", ".gitignore", "demo/assets/tracked.js"],
        cwd=root,
        check=True,
    )
    monkeypatch.setattr(
        builder,
        "LIVE_DEMOS",
        {"certification": ("demo", ("assets",))},
    )
    monkeypatch.setattr(builder, "EXPLICIT_LIVE_DEMO_FILES", frozenset())

    ignored = assets / "__pycache__" / "secret.pyc"
    ignored.parent.mkdir()
    ignored.write_bytes(b"credential material")
    with pytest.raises(ValueError, match="ignored by Git|forbidden sensitive"):
        builder._publish_live_demos(
            tmp_path / "ignored-site",
            root,
            {tracked},
            set(),
        )

    ignored.unlink()
    ignored.parent.rmdir()
    symlink = assets / "linked.js"
    symlink.symlink_to(tracked)
    with pytest.raises(ValueError, match="symlink"):
        builder._publish_live_demos(
            tmp_path / "symlink-site",
            root,
            {tracked},
            set(),
        )

    symlink.unlink()
    arbitrary = assets / "arbitrary.js"
    arbitrary.write_text("console.log('arbitrary');\n", encoding="utf-8")
    explicit = assets / "explicit.js"
    explicit.write_text("console.log('explicit');\n", encoding="utf-8")
    monkeypatch.setattr(
        builder,
        "EXPLICIT_LIVE_DEMO_FILES",
        frozenset({"demo/assets/explicit.js"}),
    )
    destination = tmp_path / "safe-site"
    builder._publish_live_demos(destination, root, {tracked}, set())
    published = destination / "demos" / "certification" / "assets"
    assert (published / "tracked.js").is_file()
    assert (published / "explicit.js").is_file()
    assert not (published / "arbitrary.js").exists()
    assert not any(
        path.name == "__pycache__" or path.suffix == ".pyc"
        for path in destination.rglob("*")
    )
