"""Launch-readiness contracts for first-time repository visitors."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_readme_leads_with_three_complete_proof_paths() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    first_half = "\n".join(readme.splitlines()[:150])

    for artifact in (
        "demos/orion-storybook/",
        "demos/ai-kanban/",
        "vale3-market-dashboard.html",
    ):
        assert artifact in first_half
    for preview in (
        "docs/tutorial-storybook-page.jpg",
        "docs/showcase-ai-kanban.jpg",
        "docs/showcase-market-report.jpg",
    ):
        assert preview in first_half
        assert (ROOT / preview).is_file()

    assert "raw.githubusercontent.com/paulosalem/weavemark/main/docs/showcase-" not in first_half

    assert "Inspect a bundled promplet without an API key" in first_half
    assert "Semantic compilation needs a configured model provider" in first_half
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
        / "vale3-market-dashboard.html"
    ).read_text(encoding="utf-8")

    assert "Storybook provenance" in storybook
    assert "Source promplet" in kanban
    assert "Compiled specification" in kanban
    assert "WeaveMark provenance" in market
    assert "execution trace" in market


def test_home_hero_keeps_autorotation() -> None:
    home = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "window.setInterval(() => showSlide(activeIndex + 1), 6500)" in home
