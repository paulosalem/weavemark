from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_home_hero_examples_show_current_artifacts() -> None:
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    assert "processor-strip" not in html
    assert 'data-title="Orion storybook — live generated result"' in html
    assert (
        'data-href="../outputs/implementations/orion-storybook/index.html"'
        in html
    )
    assert 'data-live-demo="orion-storybook"' in html
    assert 'data-title="AI Kanban — live browser demo"' in html
    assert (
        'data-href="../outputs/implementations/ai-kanban-browser/index.html"'
        in html
    )
    assert 'data-live-demo="ai-kanban"' in html
    assert '<script src="local-demo-links.js"></script>' in html
    assert "browser_sqlite_file_store" in html
    assert "typescript_nextjs_prisma_sqlite" not in html

    assert "news-intelligence-board.weavemark.md" not in html
    assert ">News board</button>" not in html

    assert 'data-title="recurring-topic-monitor.weavemark.md"' in html
    assert (
        'data-href="../promplets/catalog/executable/recurring-topic-monitor.weavemark.md"'
        in html
    )
    assert ">Topic monitor</button>" in html

    assert ">Storybook</button>" in html
    assert 'data-title="VALE3 market dashboard — live generated report"' in html
    assert (
        'data-href="https://paulosalem.github.io/weavemark/examples/'
        'saved-artifact-workflows/market-snapshot/outputs/'
        'vale3-market-dashboard.html"'
        in html
    )
    assert ">Market report</button>" in html
    assert 'data-title="issue-tree-analysis.weavemark.md"' not in html

    slide_count = html.count("<pre class=\"hero-slide")
    assert slide_count == 5
    for index in range(slide_count):
        assert f'data-carousel-index="{index}"' in html
    assert html.index(">Storybook</button>") < html.index(">Kanban</button>")
    assert html.index(">Kanban</button>") < html.index(">Market report</button>")
    for attribute in (
        "data-example-result",
        "data-example-source",
        "data-example-tutorial",
    ):
        assert attribute in html

    assert "reflection, functional, FSLM" in html
    assert "Nine connected lessons" in html
    assert "reflection, weave, FSLM" not in html


def test_home_hero_example_selector_stays_single_line() -> None:
    css = (ROOT / "docs" / "site.css").read_text(encoding="utf-8")

    controls_rule = re.search(r"\.carousel-controls\s*\{(?P<body>.*?)\n\s*\}", css, re.S)
    assert controls_rule is not None
    assert "flex-wrap: nowrap;" in controls_rule.group("body")
    assert "overflow-x: auto;" in controls_rule.group("body")
