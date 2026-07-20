#!/usr/bin/env python3
# ruff: noqa: E402
"""Compile and execute the stock-learning functional market snapshot example."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import json
import os
import sys
from collections.abc import Awaitable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "python-runtime-integrations" / "market-snapshot"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

for path in [
    REPO_ROOT / "src",
    REPO_ROOT / "examples" / "_lib",
]:
    sys.path.insert(0, str(path))

from ellements.core import LLMClient
from weavemark_example_progress import (
    normalize_generated_markdown,
    weavemark_verbose_event,
)

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.defaults import DEFAULT_MODEL

SPEC_PATH = (
    REPO_ROOT
    / "promplets"
    / "experimental"
    / "weave"
    / "weave-market-snapshot.weavemark.md"
)
COMPANION_PATH = SPEC_PATH.parent / "companions" / "market_data.py"
VARS_PATH = EXAMPLE_ROOT / "inputs" / "vars.json"
OUTPUT_DIR = EXAMPLE_ROOT / "outputs"


def _section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


async def main() -> None:
    variables = json.loads(VARS_PATH.read_text(encoding="utf-8"))
    controller = WeaveMarkController(WeaveMarkConfig(model=DEFAULT_MODEL))
    result = await controller.compose(
        SPEC_PATH.read_text(encoding="utf-8"),
        variables=variables,
        base_dir=SPEC_PATH.parent,
        on_event=weavemark_verbose_event,
    )
    if result.errors:
        raise RuntimeError("\n".join(result.errors))

    _section("WeaveMark compiled functional prompt")
    print(result.composed_prompt)

    _section("Functional execution plan emitted by WeaveMark")
    print(
        json.dumps(
            {"execution": result.execution, "bindings": result.bindings},
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )

    _section("Companion runtime execution with Ellements tools")
    companion = _load_companion()
    print(f"1. Fetching finance snapshot for {variables['ticker']}...")
    asset_snapshot = await _maybe_await(
        companion.fetch_asset_snapshot(variables["ticker"])
    )
    asset_snapshot_fields = (
        sorted(asset_snapshot) if isinstance(asset_snapshot, dict) else []
    )
    print(f"   Snapshot fields: {', '.join(asset_snapshot_fields) or '(none)'}")

    print(
        "2. Searching recent news, opinions, official context, and skeptical views..."
    )
    web_context = await _maybe_await(
        companion.search_asset_context(
            variables["ticker"],
            variables["company_name"],
            variables["research_focus"],
        )
    )
    searches = web_context.get("searches", {}) if isinstance(web_context, dict) else {}
    search_groups = sorted(searches) if isinstance(searches, dict) else []
    print(f"   Search groups: {', '.join(search_groups) or '(none)'}")

    companion_results = {
        "asset_snapshot": asset_snapshot,
        "web_context": web_context,
    }
    model_label = DEFAULT_MODEL
    if os.environ.get("OPENAI_API_KEY"):
        _section(f"Synthesizing final learning brief with {DEFAULT_MODEL}")
        synthesis_prompt = _synthesis_prompt(result.composed_prompt, companion_results)
        response = await LLMClient(model=DEFAULT_MODEL).complete(synthesis_prompt)
    else:
        _section("Synthesizing final learning brief without an LLM")
        model_label = f"{DEFAULT_MODEL} (not invoked; OPENAI_API_KEY unavailable)"
        response = _fallback_companion_summary(variables, companion_results)

    response = normalize_generated_markdown(response)
    composed_prompt = normalize_generated_markdown(result.composed_prompt)

    _section("Final response")
    print(response)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    compiled_prompt_path = OUTPUT_DIR / "compiled-prompt.md"
    compiled_plan_path = OUTPUT_DIR / "compiled-plan.json"
    data_path = OUTPUT_DIR / "tool-results.json"
    output_path = OUTPUT_DIR / "execution-output.md"
    trace_path = OUTPUT_DIR / "execution-trace.md"

    compiled_prompt_path.write_text(composed_prompt, encoding="utf-8")
    compiled_plan_path.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    data_path.write_text(
        json.dumps(companion_results, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    output_path.write_text(response, encoding="utf-8")
    trace_path.write_text(
        _render_trace(
            model_label=model_label,
            composed_prompt=composed_prompt,
            execution_plan=result.execution,
            bindings=result.bindings,
            companion_results=companion_results,
            output=response,
        ),
        encoding="utf-8",
    )

    _section("Artifacts written")
    print(f"Wrote {compiled_prompt_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {compiled_plan_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {data_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {trace_path.relative_to(REPO_ROOT)}")


def _load_companion() -> Any:
    spec = importlib.util.spec_from_file_location(
        "market_data_companion", COMPANION_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load companion module from {COMPANION_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _maybe_await(value: Awaitable[Any] | Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _synthesis_prompt(composed_prompt: str, companion_results: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            composed_prompt,
            "# Companion runtime results",
            _fence(
                json.dumps(
                    companion_results, indent=2, ensure_ascii=False, default=str
                ),
                "json",
            ),
            (
                "Write the final learning brief now. Use the companion runtime "
                "results as the concrete values for the WeaveMark placeholders. "
                "Cite URLs from web-search results when making news or opinion "
                "claims, and label snippets as search-result evidence."
            ),
        ]
    )


def _render_trace(
    *,
    model_label: str,
    composed_prompt: str,
    execution_plan: dict[str, Any],
    bindings: list[dict[str, Any]],
    companion_results: dict[str, Any],
    output: str,
) -> str:
    return "\n".join(
        [
            "# WeaveMark Weave Stock Snapshot Trace",
            "",
            f"- Model: `{model_label}`",
            f"- Spec: `{SPEC_PATH.relative_to(REPO_ROOT)}`",
            "- Companion runtime: `examples/python-runtime-integrations/market-snapshot/run.py`",
            "- Tool providers:",
            "  - `ellements.domain_specific.finance.yahoo_finance`",
            "  - `ellements.standard_tools.web.search`",
            "",
            "## Compiled prompt",
            "",
            _fence(composed_prompt, "markdown"),
            "",
            "## Functional execution plan",
            "",
            _fence(
                json.dumps(
                    {"execution": execution_plan, "bindings": bindings},
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                ),
                "json",
            ),
            "",
            "## Companion runtime result summary",
            "",
            _fence(
                json.dumps(
                    _summarize_companion_results(companion_results),
                    indent=2,
                    ensure_ascii=False,
                ),
                "json",
            ),
            "",
            "## Final response",
            "",
            _fence(output, "markdown"),
            "",
        ]
    )


def _summarize_companion_results(companion_results: dict[str, Any]) -> dict[str, Any]:
    return {
        "asset_snapshot_keys": sorted(
            companion_results.get("asset_snapshot", {}).keys()
        ),
        "web_search_groups": sorted(
            companion_results.get("web_context", {}).get("searches", {})
        ),
        "search_result_sources": _search_result_sources(
            companion_results.get("web_context")
        ),
    }


def _fallback_companion_summary(
    variables: dict[str, Any],
    companion_results: dict[str, Any],
) -> str:
    asset_snapshot = companion_results.get("asset_snapshot", {})
    tools = asset_snapshot.get("tools", {}) if isinstance(asset_snapshot, dict) else {}
    quote = _json_object(tools.get("quote"))
    profile = _json_object(tools.get("profile"))
    metrics = _json_object(tools.get("financial_metrics"))
    analyst_recommendations = str(tools.get("analyst_recommendations", "")).strip()
    web_context = companion_results.get("web_context", {})
    return "\n\n".join(
        [
            f"# Stock Learning Snapshot: {variables['company_name']} ({variables['ticker']})",
            (
                "> Generated from the Ellements-backed companion runtime tool results. "
                "`gpt-5.5` synthesis was skipped because `OPENAI_API_KEY` was not set."
            ),
            "## Finance data from Ellements Yahoo Finance tools",
            "\n".join(
                [
                    f"- Price: {_format_money(quote.get('current_price'))}",
                    f"- Market cap: {_format_money(quote.get('market_cap'))}",
                    f"- Sector / industry: {profile.get('sector', 'unknown')} / {profile.get('industry', 'unknown')}",
                    f"- P/E: {_format_number(metrics.get('pe_ratio'))}; forward P/E: {_format_number(metrics.get('forward_pe'))}",
                    f"- Revenue growth: {_format_percent(metrics.get('revenue_growth'))}; earnings growth: {_format_percent(metrics.get('earnings_growth'))}",
                    f"- Profit margin: {_format_percent(metrics.get('profit_margin'))}; gross margin: {_format_percent(metrics.get('gross_margin'))}",
                    f"- 52-week range: {_format_money(quote.get('fifty_two_week_low'))} - {_format_money(quote.get('fifty_two_week_high'))}",
                ]
            ),
            "## Analyst context",
            analyst_recommendations
            or "No analyst recommendation payload was returned.",
            "## Source-grounded search-result evidence",
            _search_result_summary(web_context),
            "## Next questions for a learner",
            "\n".join(
                [
                    "- Which revenue lines are driving the latest market reaction?",
                    "- Which parts of the bullish or bearish commentary are evidence-backed?",
                    "- What changed recently in margins, demand, competition, or regulation?",
                    "- Which claims should be verified against company filings or investor materials?",
                ]
            ),
            (
                "This is an educational stock snapshot, not a buy/sell "
                "recommendation or personal financial advice."
            ),
        ]
    )


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    parsed = json.loads(value)
    return parsed if isinstance(parsed, dict) else {}


def _search_result_summary(web_context: Any) -> str:
    if not isinstance(web_context, dict):
        return "No web context was returned."
    searches = web_context.get("searches", {})
    if not isinstance(searches, dict):
        return "No web searches were returned."
    labels = {
        "recent_news": "Recent news",
        "analyst_opinion": "Analyst opinion",
        "official_context": "Official/company context",
        "skeptical_view": "Skeptical view",
    }
    sections: list[str] = []
    for key, heading in labels.items():
        payload = searches.get(key)
        if payload is None:
            continue
        parsed = _json_object(payload)
        results = parsed.get("results", [])
        if not isinstance(results, list):
            continue
        bullets = []
        for result in results[:2]:
            if not isinstance(result, dict):
                continue
            bullets.append(
                f"- [{result.get('title', 'Untitled')}]({result.get('url', '')}) — {result.get('snippet', '')}"
            )
        if bullets:
            sections.append(f"### {heading}\n\n" + "\n".join(bullets))
    return "\n\n".join(sections) if sections else "No search results were returned."


def _search_result_sources(web_context: Any) -> list[dict[str, str]]:
    if not isinstance(web_context, dict):
        return []
    searches = web_context.get("searches", {})
    if not isinstance(searches, dict):
        return []
    sources: list[dict[str, str]] = []
    for label, payload in searches.items():
        parsed = _json_object(payload)
        results = parsed.get("results", [])
        if not isinstance(results, list):
            continue
        for result in results:
            if not isinstance(result, dict):
                continue
            sources.append(
                {
                    "group": str(label),
                    "title": str(result.get("title", "")),
                    "url": str(result.get("url", "")),
                    "snippet": str(result.get("snippet", ""))[:500],
                }
            )
    return sources


def _format_money(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "unknown"
    if abs(number) >= 1_000_000_000_000:
        return f"${number / 1_000_000_000_000:.2f}T"
    if abs(number) >= 1_000_000_000:
        return f"${number / 1_000_000_000:.2f}B"
    if abs(number) >= 1_000_000:
        return f"${number / 1_000_000:.2f}M"
    return f"${number:,.2f}"


def _format_percent(value: Any) -> str:
    number = _to_float(value)
    return "unknown" if number is None else f"{number * 100:.1f}%"


def _format_number(value: Any) -> str:
    number = _to_float(value)
    return "unknown" if number is None else f"{number:.2f}"


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fence(content: str, language: str) -> str:
    fence = "```"
    while fence in content:
        fence += "`"
    return f"{fence}{language}\n{content}\n{fence}"


if __name__ == "__main__":
    asyncio.run(main())
