from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_in_page_anchors_clear_sticky_navigation() -> None:
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")

    assert "--anchor-offset: 112px;" in css
    assert "--anchor-offset: 124px;" in css
    assert "scroll-padding-top" not in css

    anchor_rule = re.search(r"\[id\]\s*\{(?P<body>.*?)\n\s*\}", css, re.S)
    assert anchor_rule is not None
    assert "scroll-margin-top: var(--anchor-offset);" in anchor_rule.group("body")

    target_rule = re.search(
        r"\.article-section:target\s*\{(?P<body>.*?)\n\s*\}",
        css,
        re.S,
    )
    assert target_rule is not None
    assert "rgba(var(--accent-bright-rgb), 0.32)" in target_rule.group("body")


def test_home_hero_selector_has_mobile_grid_fallback() -> None:
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")

    assert "processor-strip" not in css

    controls_rule = re.search(r"\.carousel-controls\s*\{(?P<body>.*?)\n\s*\}", css, re.S)
    assert controls_rule is not None
    assert "flex-wrap: nowrap;" in controls_rule.group("body")
    assert "overflow-x: auto;" in controls_rule.group("body")

    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in css
    assert ".carousel-tab[data-carousel-index=\"4\"]" in css
    assert "grid-column: 1 / -1;" in css


def test_site_navigation_has_constant_width_and_right_links() -> None:
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "home-page" not in html
    assert ".home-page" not in css
    assert "--site-chrome-max: var(--max);" not in css
    assert "--site-chrome-max: var(--home-hero-max);" in css
    assert "width: min(var(--site-chrome-max), calc(100% - 40px));" in css

    brand_hidden_rule = re.search(
        r"\.site-nav\.brand-hidden \.site-nav-inner\s*\{(?P<body>.*?)\n\s*\}",
        css,
        re.S,
    )
    assert brand_hidden_rule is not None
    assert "justify-content: flex-end;" in brand_hidden_rule.group("body")

    brand_hidden_links_rule = re.search(
        r"\.site-nav\.brand-hidden \.nav-links\s*\{(?P<body>.*?)\n\s*\}",
        css,
        re.S,
    )
    assert brand_hidden_links_rule is not None
    assert "justify-content: flex-end;" in brand_hidden_links_rule.group("body")

    base_links_rule = re.search(
        r"^\s{6}\.nav-links\s*\{(?P<body>.*?)\n\s{6}\}",
        css,
        re.S | re.M,
    )
    assert base_links_rule is not None
    assert "justify-content: flex-end;" in base_links_rule.group("body")
    assert "justify-content: center;" not in base_links_rule.group("body")


def test_mobile_navigation_is_compact_sticky_and_horizontally_scrollable() -> None:
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")

    mobile = css[css.index("/* Compact, persistent navigation for touch-sized layouts. */") :]

    assert ".site-nav {" in mobile
    assert "position: sticky;" in mobile
    assert "top: var(--mobile-nav-top);" in mobile
    assert ".nav-links a[aria-current=\"page\"]" in mobile
    assert ".tutorial-nav {" in mobile
    assert "flex-wrap: nowrap;" in mobile
    assert ".tutorial-nav a[aria-current=\"page\"]" in mobile
    assert "order: -1;" in mobile
    assert ".sidebar {" in mobile
    assert "top: calc(var(--mobile-nav-top) + 62px);" in mobile
    assert "overflow-x: auto;" in mobile
    assert ".page-summary {" in mobile
    assert "scroll-snap-type: inline mandatory;" in mobile
    assert ".principle-teaser-link {" in mobile
    assert "min-width: 0;" in mobile
    assert ".mini-hero h1 {" in mobile
    assert "overflow-wrap: break-word;" in mobile
