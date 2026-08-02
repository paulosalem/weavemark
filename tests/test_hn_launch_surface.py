"""Launch-readiness contracts for first-time repository visitors."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parents[1]


def test_readme_leads_with_three_complete_proof_paths() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    first_half = " ".join(readme.splitlines()[:150])

    for artifact in (
        "demos/orion-storybook/",
        "demos/ai-kanban/",
        "demos/arcana/",
        "market-dashboard.html",
    ):
        assert artifact in first_half
    for preview in (
        "docs/tutorial-storybook-page.jpg",
        "docs/showcase-ai-kanban.jpg",
        "docs/showcase-arcana.jpg",
        "docs/showcase-market-report.jpg",
    ):
        assert preview in first_half
        assert (ROOT / preview).is_file()

    assert "raw.githubusercontent.com/paulosalem/weavemark/main/docs/showcase-" not in first_half

    assert "weavemark library market-snapshot --replay --verbose" in first_half
    assert "weavemark library ai-kanban-board --replay" in first_half
    assert "without an API key or network call" in first_half
    assert "passive-income-planning-dashboard" not in first_half
    assert "Orbital Drift" not in first_half


def test_readme_preserves_playful_faq_and_links_secondary_docs() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in (
        "LLM-based compilation? Are you insane?",
        'As much as a car is a "fuel harness".',
        "Don't you have an actual job and a family to feed?",
    ):
        assert phrase in readme
    assert "docs/agent-usage.md" in readme
    assert "docs/citation.md" in readme
    assert len(readme.splitlines()) < 320


def test_primary_showcases_retain_result_provenance() -> None:
    storybook = (
        ROOT / "outputs" / "implementations" / "orion-storybook" / "index.html"
    ).read_text(encoding="utf-8")
    kanban = (
        ROOT / "outputs" / "implementations" / "ai-kanban-browser" / "index.html"
    ).read_text(encoding="utf-8")
    market = (
        ROOT
        / "examples"
        / "saved-artifact-workflows"
        / "market-snapshot"
        / "outputs"
        / "market-dashboard.html"
    ).read_text(encoding="utf-8")

    assert "Storybook provenance" in storybook
    assert "Source promplet" in kanban
    assert "Compiled specification" in kanban
    assert "WeaveMark provenance" in market
    assert "execution trace" in market


def test_home_hero_keeps_autorotation() -> None:
    home = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "window.setInterval(() => showSlide(activeIndex + 1), 6500)" in home


def test_home_directives_and_artifact_paths_are_visually_scannable() -> None:
    home = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")

    for selector in (
        ".directive-map .syntax-directive",
        ".directive-map .syntax-var",
        ".directive-map .syntax-key",
        ".directive-map .syntax-string",
    ):
        assert selector in css

    assert home.count('class="build-links"') == 3
    for label in (
        "Read the source promplet",
        "Follow the AI Kanban tutorial",
        "Open the live browser app",
        "Read the executable promplet",
    ):
        assert label in home


def test_home_preserves_principles_and_explains_replay_before_claiming_it() -> None:
    home = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    hero = home[: home.index("</header>")]

    assert home.index("Language is a tool for thought.") < home.index("<main>")

    # The hero may invite a replay, but "no API key" reads as a free live run,
    # so that claim belongs only beside the explanation of what replay does.
    assert "no API key" not in hero
    assert "No API key" not in hero
    assert "--replay" in hero
    assert home.index("What it gives you") < home.index("Restore a complete recorded")
    assert home.index("Start here") < home.index("Restore a complete recorded")
    assert "does not call" in home
    assert "A fresh run still needs a model" in home
    assert "market-dashboard.html" in home

    assert "weavemark library market-snapshot --replay --verbose" in home
    assert "Can an LLM sensibly act as a compiler" not in home
    assert 'id="compiler-proof"' not in home
    assert 'class="video-slot" hidden data-video-slot' in home
    assert '<script src="analytics.js?v=20260720" defer></script>' in home


def test_public_replay_metrics_match_recorded_manifests() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    home = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    root = ROOT / "promplets" / "replays" / "catalog" / "standalone"
    kanban = json.loads((root / "ai-kanban-board" / "manifest.json").read_text())
    market = json.loads(
        (
            ROOT
            / "promplets"
            / "replays"
            / "catalog"
            / "executable"
            / "market-snapshot"
            / "manifest.json"
        ).read_text()
    )

    original = market["original_run"]
    assert original["duration_ms"] == 177_200
    assert original["output_chars"] == 24_464
    assert original["usage"] == {
        "prompt_tokens": 11_002,
        "cache_read_input_tokens": 0,
        "completion_tokens": 20_728,
        "total_tokens": 31_730,
        "response_cost": 0.3384,
    }
    assert kanban["call_count"] == 2
    assert kanban["duration_ms"] == 124_269
    assert {
        key: kanban["usage"][key]
        for key in (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "llm_duration_ms",
            "reported_cost_usd",
            "cost_source",
        )
    } == {
        "prompt_tokens": 289_861,
        "completion_tokens": 16_943,
        "total_tokens": 306_804,
        "llm_duration_ms": 124_161,
        "reported_cost_usd": 0.3778454,
        "cost_source": "provider",
    }
    for text in (
        "11,002",
        "0 cached",
        "20,728",
        "$0.3384",
        "289,861",
        "225,107",
        "16,943",
        "$0.3778",
    ):
        assert text in readme
    for text in ("11,002 input", "0 cached", "20,728 output", "$0.3384"):
        assert text in home


def test_social_preview_has_standard_large_card_dimensions() -> None:
    image_path = ROOT / "docs" / "weavemark_social.png"
    with Image.open(image_path) as image:
        assert image.size == (1200, 630)

    home = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    assert "weavemark_social.png" in home
    assert '<meta property="og:image:width" content="1200">' in home
    assert '<meta property="og:image:height" content="630">' in home
