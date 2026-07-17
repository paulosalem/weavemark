"""Ellements-backed companion functions for recurring topic monitoring."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse, urlunparse


@dataclass(frozen=True)
class MonitorSettings:
    """Concrete settings for one recurring monitor run."""

    topic: str
    monitor_mode: str
    cadence: str
    lookback_window: str
    region: str
    audience: str
    research_depth: str
    max_results_per_query: int
    max_first_level_sources: int
    max_second_level_sources: int
    age: str
    user_constraints: str
    seed_urls: tuple[str, ...]


async def collect_monitor_context(variables: dict[str, Any]) -> dict[str, Any]:
    """Search and crawl sources for one recurring monitor run."""

    from ellements.core.exceptions import LLMError
    from ellements.standard_tools.web.crawler import web_crawler_tools
    from ellements.standard_tools.web.search import web_search_tools

    settings = _settings_from_variables(variables)
    query_plan = _build_query_plan(settings)
    search_executor = web_search_tools().executor()
    crawler_executor = web_crawler_tools(max_content_tokens=3500).executor()

    search_results: dict[str, dict[str, Any]] = {}
    for query in query_plan:
        payload = await _run_search_query(
            search_executor,
            query,
            max_results=settings.max_results_per_query,
            llm_error_type=LLMError,
        )
        payload["query_family"] = query["label"]
        payload["query_tool"] = query["tool"]
        search_results[query["label"]] = payload

    seed_urls = _seed_urls(settings)
    first_level_urls = _merge_urls(
        seed_urls,
        _select_urls(
            search_results.values(),
            limit=settings.max_first_level_sources,
            mode=settings.monitor_mode,
        ),
        limit=settings.max_first_level_sources,
        mode=settings.monitor_mode,
    )
    first_level_sources = await _crawl_urls(
        crawler_executor,
        first_level_urls,
        level=1,
    )

    second_level_urls = _select_second_level_urls(
        first_level_sources,
        already_seen=set(first_level_urls),
        limit=settings.max_second_level_sources,
        mode=settings.monitor_mode,
    )
    second_level_sources = await _crawl_urls(
        crawler_executor,
        second_level_urls,
        level=2,
    )

    return {
        "run_timestamp": datetime.now(UTC).isoformat(),
        "settings": settings.__dict__,
        "query_plan": query_plan,
        "seed_urls": seed_urls,
        "search_results": search_results,
        "crawl_rounds": {
            "first_level": first_level_sources,
            "second_level": second_level_sources,
        },
        "source_counts": {
            "queries": len(query_plan),
            "search_results": sum(
                len(payload.get("results", [])) for payload in search_results.values()
            ),
            "first_level_crawled": len(first_level_sources),
            "second_level_crawled": len(second_level_sources),
        },
        "tool_providers": [
            "ellements.standard_tools.web.search",
            "ellements.standard_tools.web.crawler",
        ],
    }


def compile_variables(raw_variables: dict[str, Any]) -> dict[str, Any]:
    """Return variables with derived topic/run fields filled in."""

    variables = dict(raw_variables)
    topic = str(variables.get("topic", "")).strip()
    if "@{age}" in topic:
        age = str(variables.get("age", "")).strip()
        if not age:
            raise ValueError("topic uses @{age}, so inputs must include age")
        topic = topic.replace("@{age}", age)
    if not topic:
        raise ValueError("topic must not be empty")
    variables["topic"] = topic
    variables.setdefault("run_date", datetime.now(UTC).date().isoformat())
    variables.setdefault(
        "companion_runtime_results",
        "Injected by the companion runtime after Ellements web search and crawl passes.",
    )
    variables.setdefault("previous_run_context", "No previous run context supplied.")
    variables.setdefault("user_constraints", "No additional constraints supplied.")
    variables.setdefault("region", "global")
    variables.setdefault("audience", "the user")
    seed_urls = _coerce_seed_urls(variables.get("seed_urls", []))
    variables["seed_urls"] = list(seed_urls)
    variables["seed_urls_summary"] = _format_seed_urls(seed_urls)
    return variables


def _settings_from_variables(variables: dict[str, Any]) -> MonitorSettings:
    prepared = compile_variables(variables)
    mode = str(prepared.get("monitor_mode", "news")).strip().lower()
    if mode not in {"news", "events"}:
        raise ValueError("monitor_mode must be 'news' or 'events'")
    depth = str(prepared.get("research_depth", "deep")).strip().lower()
    if depth not in {"quick", "standard", "deep"}:
        raise ValueError("research_depth must be quick, standard, or deep")
    defaults = {
        "quick": (3, 2, 0),
        "standard": (5, 4, 2),
        "deep": (7, 6, 4),
    }
    max_results, first_level, second_level = defaults[depth]
    return MonitorSettings(
        topic=str(prepared["topic"]),
        monitor_mode=mode,
        cadence=str(prepared.get("cadence", "weekly")),
        lookback_window=str(prepared.get("lookback_window", "past week")),
        region=str(prepared.get("region", "global")),
        audience=str(prepared.get("audience", "the user")),
        research_depth=depth,
        max_results_per_query=int(prepared.get("max_results_per_query", max_results)),
        max_first_level_sources=int(
            prepared.get("max_first_level_sources", first_level)
        ),
        max_second_level_sources=int(
            prepared.get("max_second_level_sources", second_level)
        ),
        age=str(prepared.get("age", "")).strip(),
        user_constraints=str(prepared.get("user_constraints", "")).strip(),
        seed_urls=_coerce_seed_urls(prepared.get("seed_urls", [])),
    )


def _coerce_seed_urls(value: object) -> tuple[str, ...]:
    if value in (None, ""):
        return ()
    if isinstance(value, str):
        candidates = re.split(r"[\n,]+", value)
    elif isinstance(value, (list, tuple)):
        candidates = [str(item) for item in value]
    else:
        raise ValueError("seed_urls must be a list of URLs or a newline/comma string")
    urls: list[str] = []
    for candidate in candidates:
        url = _normalize_url(candidate)
        if url and url not in urls:
            urls.append(url)
    return tuple(urls)


def _format_seed_urls(seed_urls: tuple[str, ...]) -> str:
    if not seed_urls:
        return "No user-supplied source seeds."
    return "\n".join(f"- {url}" for url in seed_urls)


def _build_query_plan(settings: MonitorSettings) -> list[dict[str, str]]:
    time_range = _time_range(settings.lookback_window, settings.cadence)
    topic = settings.topic
    region_clause = "" if settings.region.lower() == "global" else f" {settings.region}"
    if settings.monitor_mode == "events":
        if _is_sao_paulo_child_activity(settings):
            localized_age = f" {settings.age} anos" if settings.age else ""
            return [
                {
                    "label": "upcoming_events",
                    "tool": "search_web",
                    "query": (
                        "programação infantil crianças"
                        f"{localized_age} São Paulo próximos 7 dias fim de semana"
                    ),
                    "time_range": time_range,
                },
                {
                    "label": "official_calendars",
                    "tool": "search_web",
                    "query": (
                        "site:sescsp.org.br/programacao programação infantil "
                        "crianças São Paulo"
                    ),
                    "time_range": time_range,
                },
                {
                    "label": "venue_calendars",
                    "tool": "search_web",
                    "query": (
                        "site:cataventocultural.org.br programação férias "
                        "crianças São Paulo"
                    ),
                    "time_range": time_range,
                },
                {
                    "label": "city_culture_calendar",
                    "tool": "search_web",
                    "query": (
                        "site:capital.sp.gov.br cultura programação infantil "
                        "crianças São Paulo"
                    ),
                    "time_range": time_range,
                },
                {
                    "label": "local_roundups",
                    "tool": "search_web",
                    "query": (
                        "São Paulo para crianças programação infantil fim de semana "
                        "férias museu teatro"
                    ),
                    "time_range": time_range,
                },
                {
                    "label": "age_fit_safety",
                    "tool": "search_web",
                    "query": (
                        "crianças"
                        f"{localized_age} São Paulo gratuito ingresso "
                        "atividade infantil segura"
                    ),
                    "time_range": time_range,
                },
                {
                    "label": "cancellations_changes",
                    "tool": "search_news",
                    "query": (
                        "programação infantil São Paulo cancelamento alteração "
                        "chuva crianças"
                    ),
                    "time_range": time_range,
                },
            ]
        event_terms = _event_search_terms(settings)
        return [
            {
                "label": "upcoming_events",
                "tool": "search_web",
                "query": f"{event_terms}{region_clause} upcoming events this {settings.cadence}",
                "time_range": time_range,
            },
            {
                "label": "official_calendars",
                "tool": "search_web",
                "query": f"{event_terms}{region_clause} official calendar venue organizer",
                "time_range": time_range,
            },
            {
                "label": "local_roundups",
                "tool": "search_web",
                "query": f"{event_terms}{region_clause} best events activities guide",
                "time_range": time_range,
            },
            {
                "label": "age_fit_safety",
                "tool": "search_web",
                "query": f"{event_terms}{region_clause} age appropriate safety cost booking",
                "time_range": time_range,
            },
            {
                "label": "local_language_events",
                "tool": "search_web",
                "query": _localized_event_query(settings),
                "time_range": time_range,
            },
            {
                "label": "cancellations_changes",
                "tool": "search_news",
                "query": f"{event_terms}{region_clause} cancelled changed announced",
                "time_range": time_range,
            },
        ]
    return [
        {
            "label": "recent_news",
            "tool": "search_news",
            "query": f"{topic} latest news",
            "time_range": time_range,
        },
        {
            "label": "primary_sources",
            "tool": "search_web",
            "query": f"{topic} official announcement primary source",
            "time_range": time_range,
        },
        {
            "label": "expert_analysis",
            "tool": "search_web",
            "query": f"{topic} expert analysis implications",
            "time_range": time_range,
        },
        {
            "label": "skeptical_context",
            "tool": "search_web",
            "query": f"{topic} criticism risks concerns",
            "time_range": time_range,
        },
        {
            "label": "source_roundup",
            "tool": "search_web",
            "query": f"{topic} weekly roundup sources",
            "time_range": time_range,
        },
    ]


def _event_search_terms(settings: MonitorSettings) -> str:
    age_phrase = f" age {settings.age}" if settings.age else ""
    if _looks_like_child_activity_topic(settings.topic):
        return f"children kids family activities events{age_phrase}"
    return settings.topic


def _localized_event_query(settings: MonitorSettings) -> str:
    if "são paulo" in settings.region.lower() and _looks_like_child_activity_topic(
        settings.topic
    ):
        age_phrase = f" {settings.age} anos" if settings.age else ""
        return (
            f"programação infantil crianças{age_phrase} São Paulo próximos 7 dias "
            "Sesc Catavento Prefeitura museu"
        )
    return f"{_event_search_terms(settings)} {settings.region} local events calendar"


def _looks_like_child_activity_topic(topic: str) -> bool:
    lowered = topic.lower()
    return any(term in lowered for term in ("child", "children", "kid", "kids", "y.o."))


def _looks_like_ai_news_topic(topic: str) -> bool:
    lowered = topic.lower()
    return any(
        term in lowered
        for term in ("llm", "generative ai", "genai", "large language model")
    )


def _is_sao_paulo_child_activity(settings: MonitorSettings) -> bool:
    return "são paulo" in settings.region.lower() and _looks_like_child_activity_topic(
        settings.topic
    )


def _time_range(lookback_window: str, cadence: str) -> str:
    text = f"{lookback_window} {cadence}".lower()
    if "day" in text or "24" in text:
        return "d"
    if "month" in text:
        return "m"
    if "year" in text:
        return "y"
    return "w"


def _coerce_search_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, str):
        parsed = json.loads(payload)
    elif hasattr(payload, "model_dump"):
        parsed = payload.model_dump()
    else:
        parsed = payload
    if not isinstance(parsed, dict):
        raise ValueError("web search tool returned a non-object payload")
    results = parsed.get("results", [])
    if isinstance(results, list):
        parsed["results"] = [
            result
            for result in results
            if isinstance(result, dict) and _result_url(result)
        ]
        parsed["total_results"] = len(parsed["results"])
    return parsed


async def _run_search_query(
    executor: Any,
    query: dict[str, str],
    *,
    max_results: int,
    llm_error_type: type[Exception],
) -> dict[str, Any]:
    arguments = {
        "query": query["query"],
        "max_results": max_results,
        "time_range": query["time_range"],
    }
    try:
        payload = await executor(query["tool"], arguments)
    except llm_error_type as exc:
        if query["tool"] != "search_news":
            return _search_error_payload(query, str(exc))
        try:
            payload = await executor("search_web", arguments)
        except llm_error_type as fallback_exc:
            return _search_error_payload(
                query,
                f"{exc}; fallback search_web also failed: {fallback_exc}",
            )
        parsed = _coerce_search_payload(payload)
        parsed["fallback_from"] = "search_news"
        parsed["fallback_reason"] = str(exc)
        return parsed
    return _coerce_search_payload(payload)


def _search_error_payload(query: dict[str, str], error: str) -> dict[str, Any]:
    return {
        "query": query["query"],
        "tool": query["tool"],
        "time_range": query["time_range"],
        "error": error,
        "results": [],
        "total_results": 0,
    }


def _select_urls(
    payloads: Iterable[dict[str, Any]],
    *,
    limit: int,
    mode: str,
) -> list[str]:
    urls: list[str] = []
    candidates = sorted(
        _iter_search_results(payloads),
        key=lambda item: _result_priority(item, mode),
    )
    for result in candidates:
        url = _normalize_url(_result_url(result))
        if url and _is_crawl_candidate(url) and url not in urls:
            urls.append(url)
        if len(urls) >= limit:
            return urls
    return urls


def _seed_urls(settings: MonitorSettings) -> list[str]:
    urls = list(settings.seed_urls)
    if settings.monitor_mode == "news" and _looks_like_ai_news_topic(settings.topic):
        urls.extend(
            [
                "https://openai.com/news/",
                "https://www.anthropic.com/news",
                "https://deepmind.google/discover/blog/",
                "https://huggingface.co/blog",
                "https://nvidianews.nvidia.com/news/latest",
            ]
        )
    if settings.monitor_mode == "events" and _is_sao_paulo_child_activity(settings):
        urls.extend(
            [
                "https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis/",
                "https://www.sescsp.org.br/programacao/territorio-do-brincar-3/",
                "https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho/",
                "https://saopauloparacriancas.com.br/",
            ]
        )
    deduped: list[str] = []
    for candidate in urls:
        url = _normalize_url(candidate)
        if url and url not in deduped:
            deduped.append(url)
    return deduped


def _merge_urls(*groups: list[str], limit: int, mode: str) -> list[str]:
    urls: list[str] = []
    for group in groups:
        for candidate in group:
            url = _normalize_url(candidate)
            if url and _is_crawl_candidate(url) and url not in urls:
                urls.append(url)
            if len(urls) >= limit:
                return urls
    return sorted(urls, key=lambda candidate: _link_priority(candidate, mode))[:limit]


def _iter_search_results(payloads: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for payload in payloads:
        family = str(payload.get("query_family", ""))
        tool = str(payload.get("query_tool", ""))
        results = payload.get("results", [])
        if not isinstance(results, list):
            continue
        for result in results:
            if not isinstance(result, dict):
                continue
            enriched = dict(result)
            enriched["_query_family"] = family
            enriched["_query_tool"] = tool
            items.append(enriched)
    return items


async def _crawl_urls(
    executor: Any,
    urls: list[str],
    *,
    level: int,
) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for url in urls:
        markdown = await executor("crawl_url", {"url": url})
        sources.append(
            {
                "level": str(level),
                "url": url,
                "markdown": _trim_markdown(str(markdown)),
                "links": json.dumps(_extract_markdown_links(str(markdown))[:12]),
            }
        )
    return sources


def _select_second_level_urls(
    sources: list[dict[str, str]],
    *,
    already_seen: set[str],
    limit: int,
    mode: str,
) -> list[str]:
    urls: list[str] = []
    normalized_seen = {_normalize_url(url) for url in already_seen}
    candidates: list[str] = []
    for source in sources:
        links = json.loads(source.get("links", "[]"))
        if not isinstance(links, list):
            continue
        for url in links:
            if not isinstance(url, str):
                continue
            normalized = _normalize_url(url)
            if (
                normalized
                and normalized not in normalized_seen
                and normalized not in candidates
                and _is_crawl_candidate(normalized)
                and _link_matches_mode(normalized, mode)
            ):
                candidates.append(normalized)
    for url in sorted(
        candidates, key=lambda candidate: _link_priority(candidate, mode)
    ):
        urls.append(url)
        if len(urls) >= limit:
            return urls
    return urls


def _result_url(result: dict[str, Any]) -> str:
    return str(result.get("url") or result.get("href") or "").strip()


def _result_priority(result: object, mode: str) -> int:
    if not isinstance(result, dict):
        return 100
    family = str(result.get("_query_family", "")).lower()
    url = _result_url(result)
    path = urlparse(url).path.lower()
    haystack = " ".join(
        str(result.get(field, "")) for field in ("title", "url", "snippet", "body")
    ).lower()
    penalty = _domain_penalty(url, mode)
    family_bonus = 0
    if mode == "events":
        if family in {"official_calendars", "local_language_events"}:
            family_bonus = -3
        elif family == "local_roundups":
            family_bonus = -2
        if "/programacao/" in path:
            family_bonus -= 4
        if "/editorial/" in path:
            penalty += 7
    elif family in {"primary_sources", "recent_news"}:
        family_bonus = -3
    primary_terms = (
        "official",
        "calendar",
        "events",
        "venue",
        "tickets",
        "register",
        "programação",
        "infantil",
        "crianças",
        "sesc",
        "museu",
        "catavento",
        "prefeitura",
    )
    news_terms = ("news", "announced", "release", "blog", "report", "research")
    terms = primary_terms if mode == "events" else news_terms
    if any(term in haystack for term in terms):
        return family_bonus + penalty
    return family_bonus + penalty + 5


def _domain_penalty(url: str, mode: str) -> int:
    hostname = (urlparse(url).hostname or "").removeprefix("www.").lower()
    if mode == "events":
        favored = (
            "sescsp.org.br",
            "prefeitura.sp.gov.br",
            "capital.sp.gov.br",
            "cataventocultural.org.br",
            "museudaimaginacao.com.br",
            "saopaulosecreto.com",
            "saopauloparacriancas.com.br",
            "sympla.com.br",
            "ingresse.com",
        )
        weak = (
            "allevents.",
            "seatgeek.",
            "bandsintown.",
            "wheresthematch.",
            "challengefamily.",
            "tripadvisor.",
            "getyourguide.",
            "wikipedia.org",
            "pinterest.",
            "youtube.",
            "mdpi.",
            "children.org",
            "savethechildren.",
            "fedex.",
            "17track.",
            "ordertracker.",
        )
    else:
        favored = (
            "openai.com",
            "anthropic.com",
            "deepmind.google",
            "ai.google",
            "microsoft.com",
            "nvidia.com",
            "huggingface.co",
            "github.com",
            "arxiv.org",
        )
        weak = ("msn.com", "forbes.com", "finance.yahoo.com")
    if any(hostname == domain or hostname.endswith(f".{domain}") for domain in favored):
        return -5
    if any(term in hostname for term in weak):
        return 8
    return 0


def _is_crawl_candidate(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = (parsed.hostname or "").removeprefix("www.").lower()
    path = parsed.path.lower()
    blocked_domains = {
        "allevents.in",
        "bandsintown.com",
        "facebook.com",
        "instagram.com",
        "linkedin.com",
        "pinterest.com",
        "reddit.com",
        "seatgeek.com",
        "tiktok.com",
        "x.com",
        "twitter.com",
        "youtube.com",
    }
    blocked_extensions = (
        ".avif",
        ".css",
        ".gif",
        ".ico",
        ".jpeg",
        ".jpg",
        ".js",
        ".png",
        ".svg",
        ".webp",
        ".woff",
        ".woff2",
    )
    if path.endswith(blocked_extensions):
        return False
    return not any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in blocked_domains
    )


def _link_matches_mode(url: str, mode: str) -> bool:
    parsed = urlparse(url)
    lowered = f"{parsed.path} {parsed.query}".lower()
    if mode == "events":
        return any(
            term in lowered
            for term in (
                "agenda",
                "atividade",
                "brincar",
                "calendar",
                "crianca",
                "criancas",
                "criança",
                "crianças",
                "event",
                "evento",
                "ferias",
                "férias",
                "infantil",
                "ingresso",
                "program",
                "programacao",
                "programação",
                "ticket",
            )
        )
    return any(
        term in lowered
        for term in (
            "announcement",
            "blog",
            "index",
            "news",
            "press",
            "release",
            "report",
            "research",
        )
    )


def _link_priority(url: str, mode: str) -> int:
    parsed = urlparse(url)
    text = f"{parsed.netloc} {parsed.path} {parsed.query}".lower()
    score = _domain_penalty(url, mode)
    if mode == "events":
        if any(
            term in text
            for term in (
                "programacao",
                "programação",
                "infantil",
                "crianca",
                "criança",
                "evento",
                "agenda",
            )
        ):
            score -= 4
    elif any(
        term in text
        for term in (
            "/news/",
            "/index/",
            "/research/",
            "announcement",
            "release",
            "system-card",
        )
    ):
        score -= 4
    return score


def _normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    normalized = parsed._replace(fragment="")
    return urlunparse(normalized).rstrip("/")


def _extract_markdown_links(markdown: str) -> list[str]:
    urls: list[str] = []
    for match in re.finditer(r"\[[^\]]+\]\((https?://[^)\s]+)\)", markdown):
        url = _normalize_url(match.group(1))
        if url and url not in urls:
            urls.append(url)
    for match in re.finditer(r"https?://[^\s)>\"]+", markdown):
        url = _normalize_url(match.group(0).strip().rstrip(".,;]"))
        if url and url not in urls:
            urls.append(url)
    return urls


def _trim_markdown(markdown: str, limit: int = 5000) -> str:
    lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.lower().startswith(("cookie", "subscribe", "advertisement")):
            continue
        lines.append(line)
        if len("\n".join(lines)) >= limit:
            break
    return "\n".join(lines)
