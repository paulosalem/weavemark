from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_home_hero_examples_show_current_artifacts() -> None:
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "processor-strip" not in html

    assert "news-intelligence-board.weavemark.md" not in html
    assert ">News board</button>" not in html

    assert 'data-title="recurring-topic-monitor.weavemark.md"' in html
    assert (
        'data-href="../promplets/catalog/executable/recurring-topic-monitor.weavemark.md"'
        in html
    )
    assert ">Topic monitor</button>" in html

    assert 'data-title="childrens-book.weavemark.md"' in html
    assert 'data-href="../promplets/catalog/executable/childrens-book.weavemark.md"' in html
    assert ">Storybook</button>" in html

    slide_count = html.count("<pre class=\"hero-slide")
    assert slide_count == 5
    for index in range(slide_count):
        assert f'data-carousel-index="{index}"' in html


def test_home_hero_example_selector_stays_single_line() -> None:
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")

    controls_rule = re.search(r"\.carousel-controls\s*\{(?P<body>.*?)\n\s*\}", css, re.S)
    assert controls_rule is not None
    assert "flex-wrap: nowrap;" in controls_rule.group("body")
    assert "overflow-x: auto;" in controls_rule.group("body")
