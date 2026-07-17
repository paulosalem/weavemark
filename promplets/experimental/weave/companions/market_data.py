"""Ellements-backed host functions for the stock-learning Weave example."""

from __future__ import annotations

import json
import warnings
from typing import Any
from urllib.parse import urlparse

from ellements.domain_specific.finance.yahoo_finance import finance_tools
from ellements.standard_tools.web.crawler import web_crawler_tools
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


async def crawl_asset_sources(
    web_context: dict[str, Any] | str,
    instructions: str = "",
    max_sources: int = 3,
) -> dict[str, Any]:
    """Crawl selected source URLs through Ellements crawl tools."""

    parsed_context = _coerce_mapping(web_context)
    urls = _extract_urls(parsed_context)
    executor = web_crawler_tools().executor()
    readings: list[dict[str, str]] = []
    for url in urls[:max_sources]:
        markdown = _relevant_markdown(
            _remove_portfolio_lines(await executor("crawl_url", {"url": url}))
        )
        readings.append(
            {
                "url": url,
                "markdown": _remove_portfolio_lines(markdown),
            }
        )
    return {
        "provider": "ellements.standard_tools.web.crawler",
        "instructions": instructions,
        "source_count": len(readings),
        "sources": readings,
    }


def _normalize_ticker(ticker: str) -> str:
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("ticker must not be empty")
    return symbol


def _coerce_mapping(value: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("web_context must be a JSON object or mapping")
    return parsed


def _extract_urls(web_context: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    searches = web_context.get("searches", {})
    if not isinstance(searches, dict):
        raise ValueError("web_context searches must be a mapping")
    for payload in _prioritized_search_payloads(searches):
        parsed = json.loads(payload) if isinstance(payload, str) else payload
        if not isinstance(parsed, dict):
            continue
        results = parsed.get("results", [])
        if not isinstance(results, list):
            continue
        for result in sorted(results, key=_crawl_priority):
            if not isinstance(result, dict):
                continue
            url = str(result.get("url", "")).strip()
            if (
                url
                and _is_crawl_candidate(url)
                and not _has_portfolio_term(result)
                and url not in urls
            ):
                urls.append(url)
    return urls


def _prioritized_search_payloads(searches: dict[str, Any]) -> list[Any]:
    priority = ["official_context", "recent_news", "analyst_opinion", "skeptical_view"]
    return [searches[key] for key in priority if key in searches] + [
        payload for key, payload in searches.items() if key not in priority
    ]


def _is_crawl_candidate(url: str) -> bool:
    blocked_or_low_signal_domains = {
        "barrons.com",
        "bloomberg.com",
        "finance.yahoo.com",
        "seekingalpha.com",
        "valuesense.io",
        "wsj.com",
    }
    hostname = urlparse(url).hostname or ""
    hostname = hostname.removeprefix("www.")
    return "portfolio" not in url.lower() and not any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in blocked_or_low_signal_domains
    )


def _crawl_priority(result: object) -> int:
    if not isinstance(result, dict):
        return 100
    url = str(result.get("url", "")).lower()
    title = str(result.get("title", "")).lower()
    if "newsroom" in url or "press-release" in url or "results" in title:
        return 0
    if "investor" in url or "investor" in title:
        return 1
    return 2


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


def _remove_portfolio_lines(markdown: str) -> str:
    return "\n".join(
        line for line in markdown.splitlines() if "portfolio" not in line.lower()
    )


def _relevant_markdown(markdown: str, limit: int = 4000) -> str:
    keywords = (
        "analyst",
        "announced",
        "aapl",
        "apple",
        "earnings",
        "financial",
        "quarter",
        "revenue",
        "services",
        "stock",
    )
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if lowered.startswith("* [") or lowered.startswith("## shop"):
            continue
        if any(keyword in lowered for keyword in keywords):
            lines.append(line)
        if len("\n".join(lines)) >= limit:
            break
    excerpt = "\n".join(lines).strip()
    return excerpt[:limit] if excerpt else markdown[:limit].strip()
