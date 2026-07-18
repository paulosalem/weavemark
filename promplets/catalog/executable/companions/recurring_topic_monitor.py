"""Thin Ellements web-tool bindings for the recurring topic monitor."""

from __future__ import annotations


async def search_web(
    query: str,
    max_results: int = 7,
    time_range: str = "w",
) -> str:
    """Execute one web search exactly as requested by the promplet."""

    from ellements.standard_tools.web.search import web_search_tools

    return await web_search_tools().executor()(
        "search_web",
        {
            "query": query,
            "max_results": max_results,
            "time_range": time_range,
        },
    )


async def search_news(
    query: str,
    max_results: int = 7,
    time_range: str = "w",
) -> str:
    """Execute one news search exactly as requested by the promplet."""

    from ellements.standard_tools.web.search import web_search_tools

    return await web_search_tools().executor()(
        "search_news",
        {
            "query": query,
            "max_results": max_results,
            "time_range": time_range,
        },
    )


async def crawl_url(url: str) -> str:
    """Crawl one URL exactly as requested by the promplet."""

    from ellements.standard_tools.web.crawler import web_crawler_tools

    return await web_crawler_tools(max_content_tokens=3500).executor()(
        "crawl_url",
        {"url": url},
    )


__all__ = ["crawl_url", "search_news", "search_web"]
