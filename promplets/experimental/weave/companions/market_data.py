"""Ellements-backed host functions for the stock-learning Weave example."""

from __future__ import annotations

import json
import warnings
from typing import Any

from ellements.domain_specific.finance.yahoo_finance import finance_tools
from ellements.standard_tools.web.search import web_search_tools

warnings.filterwarnings(
    "ignore",
    message=r"Timestamp\.utcnow is deprecated.*",
    module=r"yfinance\..*",
)


async def fetch_asset_snapshot(ticker: str) -> dict[str, Any]:
    """Fetch a finance snapshot for one public ticker through Ellements tools."""

    symbol = _normalize_ticker(ticker)
    executor = finance_tools().executor()
    calls = {
        "quote": ("get_asset_quote", {"symbol": symbol}),
        "profile": ("get_asset_profile", {"symbol": symbol}),
        "financial_metrics": ("get_financial_metrics", {"symbol": symbol}),
        "analyst_recommendations": (
            "get_analyst_recommendations",
            {"symbol": symbol},
        ),
    }
    return {
        "ticker": symbol,
        "provider": "ellements.domain_specific.finance.yahoo_finance",
        "tools": {
            label: await executor(tool_name, arguments)
            for label, (tool_name, arguments) in calls.items()
        },
    }


async def search_asset_context(
    ticker: str,
    company_name: str,
    focus: str,
) -> dict[str, Any]:
    """Search web/news context for one stock through Ellements tools."""

    symbol = _normalize_ticker(ticker)
    company = company_name.strip() or symbol
    focus_text = focus.strip() or "recent business performance and stock outlook"
    executor = web_search_tools().executor()
    queries = {
        "recent_news": (
            "search_news",
            {
                "query": f"{company} {symbol} stock recent news",
                "max_results": 5,
                "time_range": "m",
            },
        ),
        "analyst_opinion": (
            "search_web",
            {
                "query": f"{company} {symbol} analyst opinion {focus_text}",
                "max_results": 5,
                "time_range": "m",
            },
        ),
        "official_context": (
            "search_web",
            {
                "query": f"{company} investor relations quarterly results {symbol}",
                "max_results": 5,
                "time_range": "y",
            },
        ),
        "skeptical_view": (
            "search_web",
            {
                "query": f"{company} {symbol} risks bear case competition",
                "max_results": 5,
                "time_range": "y",
            },
        ),
    }
    searches: dict[str, str] = {}
    for label, (tool_name, arguments) in queries.items():
        searches[label] = _filter_search_results(await executor(tool_name, arguments))
    return {
        "ticker": symbol,
        "company_name": company,
        "focus": focus_text,
        "provider": "ellements.standard_tools.web.search",
        "searches": searches,
    }


def _normalize_ticker(ticker: str) -> str:
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("ticker must not be empty")
    return symbol


def _filter_search_results(payload: str) -> str:
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("search tool returned a non-object payload")
    results = parsed.get("results", [])
    if isinstance(results, list):
        parsed["results"] = [
            result
            for result in results
            if isinstance(result, dict) and not _has_portfolio_term(result)
        ]
        parsed["total_results"] = len(parsed["results"])
    return json.dumps(parsed, ensure_ascii=False)


def _has_portfolio_term(result: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(result.get(field, "")) for field in ("title", "url", "snippet", "body")
    ).lower()
    return "portfolio" in haystack
