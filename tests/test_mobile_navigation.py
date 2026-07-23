"""Contracts for explicit narrow-screen documentation navigation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs"
SCRIPT_TAG = '<script src="mobile-navigation.js?v=20260723" defer></script>'


def test_every_site_navigation_page_loads_mobile_navigation() -> None:
    pages = []
    for path in sorted(DOCS.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        if '<nav class="site-nav"' not in html:
            continue
        pages.append(path)
        assert SCRIPT_TAG in html, path

    assert len(pages) == 15


def test_mobile_navigation_controller_covers_all_navigation_levels() -> None:
    source = (DOCS / "mobile-navigation.js").read_text(encoding="utf-8")

    for selector in (".site-nav", ".tutorial-nav", ".sidebar"):
        assert f'document.querySelector("{selector}")' in source
    for label in ("Menu", "Tutorials", "On this page"):
        assert f'label: "{label}"' in source

    assert 'button.setAttribute("aria-expanded", "false")' in source
    assert "wrapDirectLinks" in source
    assert 'event.key !== "Escape"' in source
    assert "!item.container.contains(event.target)" in source
    assert 'mobileQuery.addEventListener("change"' in source


def test_tutorials_expose_track_and_section_disclosures() -> None:
    for path in sorted(DOCS.glob("tutorial*.html")):
        html = path.read_text(encoding="utf-8")
        assert '<nav class="tutorial-nav shell"' in html, path
        assert '<aside class="sidebar"' in html, path
