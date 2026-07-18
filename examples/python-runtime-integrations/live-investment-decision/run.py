#!/usr/bin/env python3
# ruff: noqa: E402
"""Compile and run the live investment-decision companion-runtime example."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import json
import logging
import os
import sys
from collections.abc import Awaitable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = (
    REPO_ROOT / "examples" / "python-runtime-integrations" / "live-investment-decision"
)
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

logging.getLogger("promplet.controller").setLevel(logging.ERROR)

SPEC_PATH = (
    REPO_ROOT
    / "promplets"
    / "catalog"
    / "standalone"
    / "live-investment-decision-brief.weavemark.md"
)
COMPANION_PATH = (
    REPO_ROOT
    / "promplets"
    / "experimental"
    / "weave"
    / "companions"
    / "market_data.py"
)
VARS_PATH = EXAMPLE_ROOT / "inputs" / "vars.json"
OUTPUT_DIR = EXAMPLE_ROOT / "outputs"


def _section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


async def main() -> None:
    variables = json.loads(VARS_PATH.read_text(encoding="utf-8"))
    assets = _load_assets(variables)
    compile_variables = {
        **variables,
        "candidate_assets": _format_candidate_assets(assets),
        "companion_runtime_results": (
            "Injected after compilation by "
            "`examples/python-runtime-integrations/live-investment-decision/run.py` "
            "using Ellements finance, web-search, and crawl tools."
        ),
    }

    controller = WeaveMarkController(WeaveMarkConfig(model=DEFAULT_MODEL))
    result = await controller.compose(
        SPEC_PATH.read_text(encoding="utf-8"),
        variables=compile_variables,
        base_dir=SPEC_PATH.parent,
        on_event=weavemark_verbose_event,
    )
    if result.errors:
        raise RuntimeError("\n".join(result.errors))

    _section("WeaveMark compiled investment-decision brief")
    print(result.composed_prompt)

    _section("Companion runtime execution with Ellements tools")
    companion = _load_companion()
    companion_results = await _collect_companion_results(companion, variables, assets)

    model_label = DEFAULT_MODEL
    if os.environ.get("OPENAI_API_KEY"):
        _section(f"Synthesizing final decision brief with {DEFAULT_MODEL}")
        synthesis_prompt = _synthesis_prompt(result.composed_prompt, companion_results)
        response = await LLMClient(model=DEFAULT_MODEL).complete(synthesis_prompt)
    else:
        _section("Synthesizing final decision brief without an LLM")
        model_label = f"{DEFAULT_MODEL} (not invoked; OPENAI_API_KEY unavailable)"
        response = _fallback_companion_summary(variables, companion_results)

    response = normalize_generated_markdown(response)
    composed_prompt = normalize_generated_markdown(result.composed_prompt)

    _section("Final response")
    print(response)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    compiled_prompt_path = OUTPUT_DIR / "compiled-prompt.md"
    data_path = OUTPUT_DIR / "tool-results.json"
    output_path = OUTPUT_DIR / "execution-output.md"
    trace_path = OUTPUT_DIR / "execution-trace.md"

    compiled_prompt_path.write_text(composed_prompt, encoding="utf-8")
    data_path.write_text(
        json.dumps(companion_results, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    output_path.write_text(response, encoding="utf-8")
    trace_path.write_text(
        _render_trace(
            model_label=model_label,
            composed_prompt=composed_prompt,
            companion_results=companion_results,
            output=response,
        ),
        encoding="utf-8",
    )

    _section("Artifacts written")
    print(f"Wrote {compiled_prompt_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {data_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {trace_path.relative_to(REPO_ROOT)}")


async def _collect_companion_results(
    companion: Any,
    variables: dict[str, Any],
    assets: list[dict[str, str]],
) -> dict[str, Any]:
    max_sources = int(variables.get("max_crawl_sources_per_asset", 1))
    asset_results: list[dict[str, Any]] = []
    for index, asset in enumerate(assets, start=1):
        ticker = asset["ticker"]
        company_name = asset["company_name"]
        print(f"{index}. Fetching finance snapshot for {company_name} ({ticker})...")
        asset_snapshot = await _maybe_await(companion.fetch_asset_snapshot(ticker))
        print(f"   Finance fields: {', '.join(sorted(asset_snapshot))}")

        print("   Searching news, analyst opinion, official context, and risks...")
        web_context = await _maybe_await(
            companion.search_asset_context(
                ticker,
                company_name,
                variables["research_focus"],
            )
        )
        searches = (
            web_context.get("searches", {}) if isinstance(web_context, dict) else {}
        )
        print(f"   Search groups: {', '.join(sorted(searches)) or '(none)'}")

        print(f"   Crawling {max_sources} selected source(s)...")
        source_readings = await _maybe_await(
            companion.crawl_asset_sources(
                web_context,
                instructions=(
                    "Prioritize source-rich evidence about recent earnings, AI "
                    "exposure, valuation, competitive position, and downside risks."
                ),
                max_sources=max_sources,
            )
        )
        sources = (
            source_readings.get("sources", [])
            if isinstance(source_readings, dict)
            else []
        )
        print(f"   Crawled sources: {len(sources)}")

        asset_results.append(
            {
                "asset": asset,
                "asset_snapshot": asset_snapshot,
                "web_context": web_context,
                "source_readings": source_readings,
            }
        )

    return {
        "decision_question": variables["decision_question"],
        "risk_free_benchmark": variables["risk_free_benchmark"],
        "decision_horizon": variables["decision_horizon"],
        "comparison_principal": variables["comparison_principal"],
        "materiality_band": variables["materiality_band"],
        "research_focus": variables["research_focus"],
        "assets": asset_results,
        "tool_providers": [
            "ellements.domain_specific.finance.yahoo_finance",
            "ellements.standard_tools.web.search",
            "ellements.standard_tools.web.crawler",
        ],
    }


def _load_assets(variables: dict[str, Any]) -> list[dict[str, str]]:
    raw_assets = variables.get("assets")
    if not isinstance(raw_assets, list) or not raw_assets:
        raise ValueError("inputs/vars.json must define a non-empty assets list")
    assets: list[dict[str, str]] = []
    for raw_asset in raw_assets:
        if not isinstance(raw_asset, dict):
            raise ValueError("each asset must be an object")
        ticker = str(raw_asset.get("ticker", "")).strip().upper()
        company_name = str(raw_asset.get("company_name", "")).strip()
        if not ticker or not company_name:
            raise ValueError("each asset must include ticker and company_name")
        assets.append({"ticker": ticker, "company_name": company_name})
    return assets


def _format_candidate_assets(assets: list[dict[str, str]]) -> str:
    return "\n".join(
        f"- {asset['company_name']} ({asset['ticker']})" for asset in assets
    )


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


def _synthesis_prompt(
    composed_prompt: str,
    companion_results: dict[str, Any],
) -> str:
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
                "Write the final investment-learning brief now. Use the "
                "companion runtime results as the concrete values for the "
                "WeaveMark specification. Cite crawled or searched URLs when "
                "making news, risk, valuation, or analyst-context claims. Do "
                "not make a buy, sell, or hold recommendation."
            ),
        ]
    )


def _render_trace(
    *,
    model_label: str,
    composed_prompt: str,
    companion_results: dict[str, Any],
    output: str,
) -> str:
    return "\n".join(
        [
            "# WeaveMark Live Investment Decision Trace",
            "",
            f"- Model: `{model_label}`",
            f"- Spec: `{SPEC_PATH.relative_to(REPO_ROOT)}`",
            "- Companion runtime: "
            "`examples/python-runtime-integrations/live-investment-decision/run.py`",
            "- Tool providers:",
            "  - `ellements.domain_specific.finance.yahoo_finance`",
            "  - `ellements.standard_tools.web.search`",
            "  - `ellements.standard_tools.web.crawler`",
            "",
            "## Compiled prompt",
            "",
            _fence(composed_prompt, "markdown"),
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
    summaries: list[dict[str, Any]] = []
    for asset_result in companion_results.get("assets", []):
        if not isinstance(asset_result, dict):
            continue
        asset = asset_result.get("asset", {})
        source_readings = asset_result.get("source_readings", {})
        sources = (
            source_readings.get("sources", [])
            if isinstance(source_readings, dict)
            else []
        )
        summaries.append(
            {
                "ticker": asset.get("ticker"),
                "company_name": asset.get("company_name"),
                "crawled_urls": [
                    source.get("url", "")
                    for source in sources
                    if isinstance(source, dict)
                ],
            }
        )
    return {
        "decision_question": companion_results.get("decision_question"),
        "risk_free_benchmark": companion_results.get("risk_free_benchmark"),
        "assets": summaries,
    }


def _fallback_companion_summary(
    variables: dict[str, Any],
    companion_results: dict[str, Any],
) -> str:
    lines = [
        "# Live Investment Decision Brief",
        "",
        (
            "> Generated from Ellements-backed companion runtime tool results. "
            "`gpt-5.5` synthesis was skipped because `OPENAI_API_KEY` was not set."
        ),
        "",
        f"Question: {variables['decision_question']}",
        "",
        "## Companion evidence collected",
    ]
    for asset_result in companion_results.get("assets", []):
        if not isinstance(asset_result, dict):
            continue
        asset = asset_result.get("asset", {})
        snapshot = asset_result.get("asset_snapshot", {})
        tools = snapshot.get("tools", {}) if isinstance(snapshot, dict) else {}
        quote = _json_object(tools.get("quote"))
        metrics = _json_object(tools.get("financial_metrics"))
        source_readings = asset_result.get("source_readings", {})
        sources = (
            source_readings.get("sources", [])
            if isinstance(source_readings, dict)
            else []
        )
        lines.extend(
            [
                "",
                f"### {asset.get('company_name')} ({asset.get('ticker')})",
                f"- Current price: {_format_money(quote.get('current_price'))}",
                f"- Market cap: {_format_money(quote.get('market_cap'))}",
                f"- P/E: {_format_number(metrics.get('pe_ratio'))}",
                f"- Forward P/E: {_format_number(metrics.get('forward_pe'))}",
                f"- Revenue growth: {_format_percent(metrics.get('revenue_growth'))}",
                f"- Crawled sources: {', '.join(_source_urls(sources)) or 'none'}",
            ]
        )
    lines.extend(
        [
            "",
            "## Next step",
            (
                "Run with `OPENAI_API_KEY` to synthesize the full probability, "
                "delta, evidence-grade, and ranking analysis. This fallback is "
                "an evidence collection summary, not an investment recommendation."
            ),
        ]
    )
    return "\n".join(lines)


def _source_urls(sources: list[Any]) -> list[str]:
    return [
        str(source.get("url", "")).strip()
        for source in sources
        if isinstance(source, dict) and str(source.get("url", "")).strip()
    ]


def _json_object(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str) and payload.strip():
        parsed = json.loads(payload)
        if isinstance(parsed, dict):
            return parsed
    return {}


def _format_money(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if abs(number) >= 1_000_000_000:
        return f"${number / 1_000_000_000:.2f}B"
    if abs(number) >= 1_000_000:
        return f"${number / 1_000_000:.2f}M"
    return f"${number:,.2f}"


def _format_number(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "unknown"


def _format_percent(value: Any) -> str:
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "unknown"


def _fence(content: str, language: str) -> str:
    return f"```{language}\n{content.rstrip()}\n```"


if __name__ == "__main__":
    asyncio.run(main())
