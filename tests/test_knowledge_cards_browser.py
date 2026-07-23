"""Contracts for the static Knowledge Cards browser implementation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
APP = ROOT / "outputs" / "implementations" / "knowledge-cards"


def test_knowledge_cards_static_delivery_is_complete() -> None:
    required = (
        "index.html",
        "favicon.svg",
        "manifest.webmanifest",
        "sw.js",
        "styles/site.css",
        "src/main.js",
        "src/domain/feedOrdering.js",
        "src/domain/repositories.js",
        "src/ui/feed.js",
        "content/packs/index.json",
        "schemas/cards.schema.json",
        "tools/generate-content.mjs",
        "tools/validate-packs.mjs",
        "README.md",
    )
    assert all((APP / relative).is_file() for relative in required)

    package = json.loads((APP / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["validate:packs"]
    assert package["scripts"]["test"]
    assert package.get("dependencies") in (None, {})


def test_knowledge_cards_ships_four_complete_authored_packs() -> None:
    index = json.loads(
        (APP / "content/packs/index.json").read_text(encoding="utf-8")
    )
    assert len(index["packs"]) == 4
    assert sum(pack["card_count"] for pack in index["packs"]) == 200

    forbidden = (
        "The learner should use this idea to organize later details",
        "The beginner-level limitation is that real cases include",
        "Use the example to point out where",
        "https://www.cdc.gov/safechild/",
    )
    for pack in index["packs"]:
        pack_dir = APP / "content" / "packs" / pack["id"]
        manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
        document = json.loads(
            (pack_dir / manifest["ordered_content_files"][0]).read_text(
                encoding="utf-8"
            )
        )
        assert len(document["cards"]) == 50
        assert len({card["id"] for card in document["cards"]}) == 50
        assert len(
            {tuple(sorted(card["source_refs"])) for card in document["cards"]}
        ) > 1
        source = json.dumps(document)
        assert all(item not in source for item in forbidden)


def test_knowledge_cards_has_no_backend_or_runtime_model() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((APP / "src").rglob("*.js"))
    )
    for forbidden in ("new WebSocket(", "/api/", "localhost:", "OpenAI", "Anthropic"):
        assert forbidden not in source

    assert "indexedDB.open" in source
    assert "serviceWorker.register" in source
    assert "mutationChain" in source
    assert "shouldOfferStoppingPoint" in source
    assert "session_viewed_card_ids" in source


def test_knowledge_cards_uses_the_document_as_its_only_scroll_surface() -> None:
    css = (APP / "styles/site.css").read_text(encoding="utf-8")
    feed = (APP / "src/ui/feed.js").read_text(encoding="utf-8")

    assert "overflow-y: auto" not in css
    assert "max-block-size:" not in _css_rule(css, ".knowledge-card")
    assert 'window.addEventListener("scroll", activateIfReady' in feed
    assert 'feed.addEventListener("scroll"' not in feed


def _css_rule(css: str, selector: str) -> str:
    start = css.index(f"{selector} {{")
    end = css.index("}", start)
    return css[start:end]
