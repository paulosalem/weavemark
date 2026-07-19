from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_in_page_anchors_clear_sticky_navigation() -> None:
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")

    assert "--anchor-offset: 112px;" in css
    assert "--anchor-offset: 28px;" in css
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
