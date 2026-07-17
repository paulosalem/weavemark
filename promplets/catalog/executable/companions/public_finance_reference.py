"""Public-reference lookup companion for the financial-independence goal planner."""

from __future__ import annotations

import json
import os
from typing import Any


async def lookup_public_goal_assumptions(
    goal: str,
    domain: str,
    country: str,
    horizon: str,
) -> dict[str, Any]:
    """Return public, non-private assumptions for a personal-finance goal."""

    query_pack = _query_pack(goal=goal, domain=domain, country=country, horizon=horizon)
    if os.environ.get("WEAVEMARK_LIVE_WEB_SEARCH") == "1":
        searches = await _run_live_web_search(query_pack)
        mode = "live-web-search"
    else:
        searches = _curated_public_sources(query_pack)
        mode = "curated-public-reference-pack"

    return {
        "effect": "web_search read",
        "mode": mode,
        "privacy_boundary": (
            "Uses public reference material only. It does not read bank accounts, "
            "transactions, portfolios, credit reports, or identity data."
        ),
        "goal": goal,
        "domain": domain,
        "country": country,
        "horizon": horizon,
        "queries": query_pack,
        "sources": searches,
        "assumptions_to_verify": [
            "current tax-advantaged account contribution limits",
            "current local tax treatment and withdrawal rules",
            "inflation and expected expense assumptions",
            "safe-withdrawal assumptions appropriate to the user's country",
            "health insurance, housing, family, and job-risk constraints",
        ],
        "planning_lenses": [
            "savings-rate leverage",
            "expense-floor realism",
            "income resilience",
            "emergency-fund runway",
            "investment-policy clarity",
            "review cadence and behavior guardrails",
        ],
    }


def _query_pack(
    *,
    goal: str,
    domain: str,
    country: str,
    horizon: str,
) -> list[str]:
    normalized_country = country.strip() or "the user's country"
    return [
        f"{normalized_country} official retirement account contribution limits",
        f"{normalized_country} investor education compound interest calculator",
        f"{normalized_country} consumer finance budgeting emergency fund guidance",
        f"financial independence planning assumptions safe withdrawal rate {horizon}",
        f"personal finance planning {goal} {domain} public reference",
    ]


async def _run_live_web_search(queries: list[str]) -> list[dict[str, Any]]:
    try:
        from ellements.standard_tools.web.search import web_search_tools
    except ImportError as exc:
        raise RuntimeError(
            "Live web search requires the optional Ellements web-search tools. "
            "Install the example extras or run without WEAVEMARK_LIVE_WEB_SEARCH=1."
        ) from exc

    executor = web_search_tools().executor()
    results: list[dict[str, Any]] = []
    for query in queries:
        payload = await executor(
            "search_web",
            {
                "query": query,
                "max_results": 4,
                "time_range": "y",
            },
        )
        parsed = json.loads(payload)
        results.append(
            {
                "query": query,
                "provider": "ellements.standard_tools.web.search",
                "results": parsed.get("results", []),
            }
        )
    return results


def _curated_public_sources(queries: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "query": queries[0],
            "provider": "curated public reference",
            "results": [
                {
                    "title": "IRS retirement plan contribution limits",
                    "url": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-contributions",
                    "why_it_matters": (
                        "Tax-advantaged contribution limits are public facts that "
                        "can change yearly and should be verified before planning."
                    ),
                },
                {
                    "title": "IRS IRA contribution limits",
                    "url": "https://www.irs.gov/retirement-plans/traditional-and-roth-iras",
                    "why_it_matters": (
                        "IRA rules affect which savings vehicles might be relevant "
                        "for a U.S. financial-independence plan."
                    ),
                },
            ],
        },
        {
            "query": queries[1],
            "provider": "curated public reference",
            "results": [
                {
                    "title": "Investor.gov compound interest calculator",
                    "url": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator",
                    "why_it_matters": (
                        "Compounding examples help turn distant goals into "
                        "reviewable savings and investment assumptions."
                    ),
                }
            ],
        },
        {
            "query": queries[2],
            "provider": "curated public reference",
            "results": [
                {
                    "title": "Consumer Financial Protection Bureau budgeting resources",
                    "url": "https://www.consumerfinance.gov/consumer-tools/budgeting/",
                    "why_it_matters": (
                        "Budgeting and cash-flow guidance keeps the first steps "
                        "grounded before any investment assumptions."
                    ),
                }
            ],
        },
        {
            "query": queries[3],
            "provider": "curated public reference",
            "results": [
                {
                    "title": "Bogleheads wiki: Safe withdrawal rates",
                    "url": "https://www.bogleheads.org/wiki/Safe_withdrawal_rates",
                    "why_it_matters": (
                        "Safe-withdrawal-rate discussion is useful context, but it "
                        "is not a guarantee and must be adapted to the user."
                    ),
                }
            ],
        },
    ]
