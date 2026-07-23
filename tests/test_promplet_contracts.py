"""Focused regressions for maintained non-domain promplet contracts."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import pytest

from weavemark.api import compile_file
from weavemark.compilation.args import parse_header_args
from weavemark.compilation.macros import preprocess_weavemark
from weavemark.engines import functional as functional_module
from weavemark.engines.base import RuntimeConfig
from weavemark.engines.functional import FunctionalEngine
from weavemark.tui.scanner import scan_spec

ROOT = Path(__file__).resolve().parents[1]
PROMPLETS = ROOT / "promplets"
CATALOG = PROMPLETS / "catalog"


def _all_promplets() -> list[Path]:
    return sorted(PROMPLETS.rglob("*.weavemark.md"))


def _tool_parameter_lines(source: str) -> list[str]:
    lines = source.splitlines()
    parameters: list[str] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(?P<indent>\s*)@tool\s+\S+", line)
        if match is None:
            continue
        base_indent = len(match.group("indent").expandtabs(2))
        for candidate in lines[index + 1 :]:
            if not candidate.strip():
                continue
            indent = len(candidate) - len(candidate.lstrip(" "))
            if indent <= base_indent:
                break
            if re.match(r"^\s*-\s+[A-Za-z_][\w-]*\s*:", candidate):
                parameters.append(candidate)
    return parameters


def _bodyless_calls(source: str, names: set[str]) -> list[str]:
    lines = source.splitlines()
    bodyless: list[str] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(?P<indent>\s*)@(?P<name>[\w.-]+)\b", line)
        if match is None or match.group("name") not in names:
            continue
        base_indent = len(match.group("indent").expandtabs(2))
        next_content = next(
            (candidate for candidate in lines[index + 1 :] if candidate.strip()),
            "",
        )
        if not next_content:
            bodyless.append(line.strip())
            continue
        next_indent = len(next_content) - len(next_content.lstrip(" "))
        if next_indent <= base_indent:
            bodyless.append(line.strip())
    return bodyless


def test_all_149_promplets_use_canonical_assert_and_tool_syntax() -> None:
    promplets = _all_promplets()
    assert len(promplets) == 149

    invalid_assertions: list[str] = []
    invalid_parameters: list[str] = []
    assertion_options = {
        "contains",
        "not_contains",
        "section",
        "severity",
        "variable",
    }
    assertion_checks = {"contains", "not_contains", "section", "variable"}
    for path in promplets:
        source = path.read_text(encoding="utf-8")
        for line in source.splitlines():
            match = re.match(r"^\s*@assert\b(?P<rest>.*)$", line)
            if match is None:
                continue
            parsed = parse_header_args(match.group("rest").strip())
            if (
                parsed.errors
                or parsed.positional
                or not assertion_checks.intersection(parsed.options)
                or set(parsed.options) - assertion_options
            ):
                invalid_assertions.append(f"{path.relative_to(ROOT)}: {line.strip()}")
        for line in _tool_parameter_lines(source):
            if "—" in line or "(optional)" in line or " - " not in line:
                invalid_parameters.append(f"{path.relative_to(ROOT)}: {line.strip()}")

    assert invalid_assertions == []
    assert invalid_parameters == []


def test_structural_assertions_name_real_prompt_obligations() -> None:
    missing: list[str] = []
    assertion_pattern = re.compile(r'^\s*@assert\s+contains:\s*"([^"]+)"')
    for path in _all_promplets():
        lines = path.read_text(encoding="utf-8").splitlines()
        source_without_assertions = "\n".join(
            line for line in lines if not line.lstrip().startswith("@assert")
        )
        for line in lines:
            match = assertion_pattern.match(line)
            if match is not None and match.group(1) not in source_without_assertions:
                missing.append(f"{path.relative_to(ROOT)}: {match.group(1)}")

    assert missing == []


def test_required_transform_calls_all_have_explicit_targets() -> None:
    required = {"compress", "normalize", "polish", "revise", "style"}
    bodyless: list[str] = []
    for path in _all_promplets():
        if "domains" in path.parts:
            continue
        for call in _bodyless_calls(path.read_text(encoding="utf-8"), required):
            bodyless.append(f"{path.relative_to(ROOT)}: {call}")

    assert bodyless == []


@pytest.mark.asyncio
async def test_dynamic_story_beat_sheets_ground_every_supplied_entry() -> None:
    book_path = CATALOG / "executable/childrens-book.weavemark.md"
    book_source = book_path.read_text(encoding="utf-8")
    assert re.search(r"pages\.\d+", book_source) is None
    book_beats = [
        {"scene": "Mia waits beside the exact blue gate.", "text": "Wait for me."},
        {"scene": "Mia and Pip meet beneath the exact moon.", "text": "Home at last."},
    ]
    book = await compile_file(
        book_path,
        {
            "title": "Moon Gate",
            "audience": "children aged 3 to 5",
            "page_count": len(book_beats),
            "text_in_image": "on",
            "image_size": "1024x1024",
            "image_quality": "high",
            "image_model": "gpt-image-2",
            "tone": "warm",
            "art_style": "paper cut",
            "premise": "A moth finds her friend.",
            "characters": "Mia: a small silver moth; Pip: a blue firefly.",
            "setting": "A moonlit garden.",
            "lessons": "asking for help",
            "pages": book_beats,
        },
    )
    assert book.errors == []
    assert book.execution["count"] == len(book_beats)
    author = book.prompts["author"]
    for beat in book_beats:
        assert beat["scene"] in author
        assert beat["text"] in author
    assert book.prompt_outputs["author"].params["enforce"] == "strict"
    assert "top-level keys `title`" in book.prompt_outputs["author"].params["body"]
    assert "and `pages` (array)" in book.prompt_outputs["author"].params["body"]
    assert book.packages[0]["instructions"] == (
        "module:weavemark.domains.creative.picture_book_html"
    )

    comic_path = CATALOG / "executable/comic-strip.weavemark.md"
    comic_source = comic_path.read_text(encoding="utf-8")
    assert re.search(r"panels\.\d+", comic_source) is None
    panel_beats = [
        {"staging": "Ada enters carrying the exact red box.", "dialogue": "Delivery!"},
        {"staging": "Bo points at the exact open hatch.", "dialogue": "Wrong door."},
        {"staging": "Ada grins beside the hatch.", "dialogue": "Express route."},
    ]
    comic = await compile_file(
        comic_path,
        {
            "title": "Express Route",
            "premise": "A delivery takes an unexpected shortcut.",
            "panel_count": len(panel_beats),
            "layout": "one row",
            "tone": "dry",
            "art_style": "clean ink",
            "setting": "a quiet workshop",
            "characters": "Ada: red coat; Bo: blue overalls.",
            "panels": panel_beats,
            "character_sheet_1": "",
            "character_sheet_2": "",
            "character_sheet_3": "",
            "character_sheet_4": "",
            "style_reference": "",
        },
    )
    assert comic.errors == []
    comic_author = comic.prompts["author"]
    for beat in panel_beats:
        assert beat["staging"] in comic_author
        assert beat["dialogue"] in comic_author


class _ReportClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def complete(self, prompt: str, **_: Any) -> str:
        self.prompts.append(prompt)
        return "FINAL MARKET REPORT"


@pytest.mark.asyncio
async def test_market_functional_metadata_and_two_node_execution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = PROMPLETS / "catalog/executable/market-snapshot.weavemark.md"
    variables = {
        "provider_ticker": "ACME",
        "display_ticker": "ACME",
        "company_name": "Acme Corp",
        "research_focus": "cash-flow durability",
    }
    compiled = await compile_file(path, variables)
    assert compiled.errors == []
    assert compiled.execution["plan"] == {
        "scheduler": "graph-strict",
        "order": ["asset_snapshot", "web_context"],
        "levels": [["asset_snapshot"], ["web_context"]],
    }
    assert compiled.execution["allow_effects"] == ["finance_data", "web_search"]
    assert compiled.bindings == [
        {
            "name": "finance_data",
            "language": "python",
            "from": "./companions/market_data.py",
            "symbol": "fetch_asset_snapshot",
            "module": "weavemark.domains.finance.market_research",
        },
        {
            "name": "web_search",
            "language": "python",
            "from": "./companions/market_data.py",
            "symbol": "search_asset_context",
            "module": "weavemark.domains.finance.market_research",
        },
    ]
    assert compiled.packages == [
        {
            "file": "vale3-market-dashboard.html",
            "instructions": (
                "module:weavemark.std.presentation.information_dashboard_html"
            ),
            "body": (
                "Title the deliverable \"VALE3 Market Learning Dashboard\" and "
                "identify the\nanalyzed security as Vale S.A. on B3 under ticker "
                "VALE3. The finance provider\nmay label the instrument VALE3.SA; "
                "explain that notation once, compactly.\n\nGive the dashboard an "
                "extractive-industry research character without adding\n"
                "decorative imagery: make commodity exposure, operational drivers, "
                "balance\nsheet signals, evidence quality, cyclical risks, and "
                "watchlist items easy to\nscan. Use the current company name, Vale "
                "S.A.; mention the historical\nCompanhia Vale do Rio Doce name only "
                "if useful for identification.\n\nRetain Portuguese-real amounts "
                "and Brazilian-market terminology exactly when\nsupplied. Never "
                "convert currencies or infer missing values. Keep the final\n"
                "educational, non-recommendation disclaimer visible but quiet."
            ),
        }
    ]

    calls: list[tuple[str, dict[str, Any]]] = []

    async def fetch_asset_snapshot(ticker: str) -> dict[str, Any]:
        calls.append(("finance_data", {"ticker": ticker}))
        return {"ticker": ticker, "price": "42.00"}

    async def search_asset_context(
        ticker: str,
        company_name: str,
        focus: str,
    ) -> dict[str, Any]:
        payload = {
            "ticker": ticker,
            "company_name": company_name,
            "focus": focus,
            "searches": {"official_context": {"results": []}},
        }
        calls.append(("web_search", payload))
        return payload

    implementations = {
        "finance_data": fetch_asset_snapshot,
        "web_search": search_asset_context,
    }

    def load_callables(_: Any, names: list[str]) -> dict[str, Any]:
        assert names == ["finance_data", "web_search"]
        return implementations

    monkeypatch.setattr(
        functional_module,
        "load_binding_callables",
        load_callables,
    )
    client = _ReportClient()
    execution = await FunctionalEngine(client=client).execute(
        compiled,
        RuntimeConfig(execution_variables=variables),
    )

    assert [name for name, _ in calls] == [
        "finance_data",
        "web_search",
    ]
    assert [step.name for step in execution.steps] == [
        "asset_snapshot",
        "web_context",
        "document",
    ]
    assert execution.output == "FINAL MARKET REPORT"
    assert client.prompts and "Acme Corp (ACME)" in client.prompts[0]


def test_information_dashboard_packaging_contract_is_standalone_and_grounded() -> None:
    source = (
        PROMPLETS
        / "stdlib/fragments/presentation/information-dashboard-html.weavemark.md"
    ).read_text(encoding="utf-8")

    assert "@{output}" in source
    assert "@output enforce: strict" in source
    assert "Do not add facts, metrics, dates" in source
    assert "Use no scripts, frameworks" in source
    assert "restrictive Content Security Policy" in source
    assert "approximately 900px and 640px" in source
    assert "Add print styles" in source
    assert "WCAG AA" in source


def test_market_companion_filters_unrelated_results() -> None:
    companion_path = (
        PROMPLETS
        / "domains/finance/definitions/companions/market_data.py"
    )
    spec = importlib.util.spec_from_file_location(
        "market_data_companion_for_tests",
        companion_path,
    )
    assert spec is not None and spec.loader is not None
    companion = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(companion)

    payload = json.dumps(
        {
            "results": [
                {
                    "title": "Vale expands an iron-ore operation",
                    "url": "https://example.com/vale",
                    "snippet": "VALE3 production update",
                },
                {
                    "title": "Unrelated restaurant stock",
                    "url": "https://example.com/restaurant",
                    "snippet": "A meme-stock rally",
                },
            ]
        }
    )
    filtered = json.loads(
        companion._filter_search_results(
            payload,
            symbol="VALE3",
            company_name="Vale S.A.",
            category="recent_news",
        )
    )

    assert [result["title"] for result in filtered["results"]] == [
        "Vale expands an iron-ore operation"
    ]
    assert filtered["total_results"] == 1
    assert companion._matches_category(
        {"url": "https://www.vale.com/investors"},
        "official_context",
    )
    assert not companion._matches_category(
        {"url": "https://example.com/vale-earnings"},
        "official_context",
    )


def test_executable_tool_bindings_are_explicit_and_safe() -> None:
    expected = {
        "react-agent.weavemark.md": {"calculate", "search_web"},
        "crisis-strategy-analyzer.weavemark.md": {"search_web"},
    }
    for filename, binding_names in expected.items():
        source = (CATALOG / "executable" / filename).read_text(encoding="utf-8")
        metadata = scan_spec(source)
        assert set(metadata.binding_names) == binding_names
        assert "run_python" not in source
        assert "recurring_topic_monitor.py" in source

    react = (CATALOG / "executable/react-agent.weavemark.md").read_text(
        encoding="utf-8"
    )
    crisis = (CATALOG / "executable/crisis-strategy-analyzer.weavemark.md").read_text(
        encoding="utf-8"
    )
    assert 'with problem: "@{research_topic}"' in react
    assert 'with problem: "@{situation}"' in crisis
    assert "read_url" not in react
    assert "read_url" not in crisis

    calculator_path = CATALOG / "executable/companions/safe_calculator.py"
    spec = importlib.util.spec_from_file_location(
        "safe_calculator_for_tests", calculator_path
    )
    assert spec is not None and spec.loader is not None
    calculator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(calculator)
    assert calculator.calculate("(2 + 3) ^ 2") == "25"
    assert calculator.calculate("12.5", format="currency") == "$12.50"
    with pytest.raises(ValueError, match="Unsupported expression element"):
        calculator.calculate("__import__('os').getcwd()")


def test_api_docs_revises_the_real_assembled_subspec() -> None:
    source = (CATALOG / "standalone/api-docs-generator.weavemark.md").read_text(
        encoding="utf-8"
    )
    revise_index = source.index("@revise ")
    target = source[revise_index:]
    assert "## API documentation draft" not in source
    assert "@{endpoints}" in target
    assert "@generate_examples count: 2" in target
    assert '@output "markdown"' in target


def test_financial_zero_rate_and_sqlite_contracts_are_explicit() -> None:
    compound = (
        CATALOG / "standalone/compoundvision-investment-simulator.weavemark.md"
    ).read_text(encoding="utf-8")
    for formula in (
        "FV = PV + PMT × N",
        "ordinary annuity",
        "Annuity due",
        "FV = PV × exp(r × t)",
        "FV = PV + C × t",
    ):
        assert formula in compound
    for invalid_type in ("SERIAL", "VARCHAR", "DECIMAL(", "JSONB", "| UUID |"):
        assert invalid_type not in compound
    assert "Never use SQLite `REAL`" in compound
    assert "canonical decimal `TEXT`" in compound

    portfolio = (
        CATALOG / "executable/portfolio-calculator-agent.weavemark.md"
    ).read_text(encoding="utf-8")
    assert "If monthly rate is zero" in portfolio
    assert "initial capital + (monthly contribution * months)" in portfolio
    assert "custom Python host" in portfolio


def test_story_output_contracts_and_cli_titles_are_explicit() -> None:
    book_path = CATALOG / "executable/childrens-book.weavemark.md"
    book_source = book_path.read_text(encoding="utf-8")
    template_path = (
        PROMPLETS / "domains/creative/fragments/picture-book-html.weavemark.md"
    )
    template = template_path.read_text(encoding="utf-8")
    assert "@module weavemark.domains.creative.picture_book_html" in template
    assert "@output enforce: strict" in template
    assert "`<!doctype html>`" in template
    assert "`</html>`" in template
    assert (
        "instructions: module:weavemark.domains.creative.picture_book_html"
        in book_source
    )
    assert not (
        CATALOG / "executable/companions/picture-book-html.template.md"
    ).exists()
    preprocessed = preprocess_weavemark(template, template_path.parent)
    assert preprocessed.errors == []
    assert "You assemble a COMPLETE, print-ready HTML document" in preprocessed.text
    assert "@output enforce: strict" in preprocessed.text

    expected_titles = {
        "childrens-book.weavemark.md": "Children's Picture Book",
        "comic-strip.weavemark.md": "Comic Strip",
        "storyboard-chain.weavemark.md": "Storyboard Chain",
    }
    for filename, title in expected_titles.items():
        source = (CATALOG / "executable" / filename).read_text(encoding="utf-8")
        assert scan_spec(source).title == title


def test_strategy_contract_corrections_are_preserved() -> None:
    contrastive = (CATALOG / "executable/contrastive-mining.weavemark.md").read_text(
        encoding="utf-8"
    )
    assert "max_rounds: 2" in contrastive
    assert "\n  rounds:" not in contrastive
    assert "max_iterations:" not in contrastive
    assert (
        contrastive.count(
            "@embed file: ./samples/contrastive-mining/"
            "corporate-memo-pro-office.txt"
        )
        == 2
    )
    assert (
        contrastive.count(
            "@embed file: ./samples/contrastive-mining/"
            "employee-blog-pro-remote.txt"
        )
        == 2
    )
    assert "../../../examples/" not in contrastive

    tree = (CATALOG / "executable/tree-of-thought-solver.weavemark.md").read_text(
        encoding="utf-8"
    )
    assert "~43 LLM calls vs ~5" in tree
    assert "ANSWER: [final numeric value, text answer, or labeled choice]" in tree


def test_ai_kanban_uses_concise_browser_architecture_modules() -> None:
    source = (CATALOG / "standalone/ai-kanban-board.weavemark.md").read_text(
        encoding="utf-8"
    )
    for module in (
        "stacks.browser_static_esmodules",
        "types.browser_file_backed_webapp",
        "modules.browser_sqlite_file_store",
        "modules.browser_ai_handoff",
    ):
        assert f"module:weavemark.domains.programming.{module}" in source
    assert "@output enforce: strict" in source
    assert "outputs/implementations/ai-kanban-browser/" in source
    assert "Next.js" not in source
    assert "Prisma" not in source
    assert "WebSocket" not in source
    assert len(source.splitlines()) < 120


def test_knowledge_cards_uses_concise_reusable_mobile_architecture() -> None:
    source = (CATALOG / "standalone/knowledge-cards.weavemark.md").read_text(
        encoding="utf-8"
    )
    for module in (
        "programming.stacks.browser_static_esmodules",
        "programming.types.mobile_first_webapp",
        "programming.modules.card",
        "programming.modules.snap_card_feed",
        "programming.modules.static_content_packs",
        "education.knowledge_card_curriculum",
    ):
        assert f"module:weavemark.domains.{module}" in source
    assert "@{topics}" in source
    assert "@{cards_per_pack}" in source
    assert "exactly @{cards_per_pack} cards" in source
    assert "no runtime LLM calls" in source
    assert "content/packs/<pack-id>/" in source
    assert "IndexedDB" in source
    assert "@output enforce: strict" in source
    assert len(source.splitlines()) < 110
