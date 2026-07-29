"""Contracts for run-scoped token usage and cost reporting."""

from __future__ import annotations

import asyncio

import pytest

from weavemark.logging_setup import new_client
from weavemark.usage_tracking import (
    UsageAccumulator,
    UsageTotals,
    active_accumulator,
    active_totals,
    format_cost,
    track_usage,
    usage_stats,
)

OPENAI_USAGE = {
    "prompt_tokens": 123480,
    "completion_tokens": 15257,
    "total_tokens": 138737,
    "response_cost": 0.714534,
}


def test_accumulator_sums_tokens_and_cost_across_calls() -> None:
    accumulator = UsageAccumulator()

    accumulator.record(OPENAI_USAGE)
    accumulator.record({"prompt_tokens": 20, "completion_tokens": 5, "cost": 0.25})

    totals = accumulator.totals()
    assert totals.prompt_tokens == 123500
    assert totals.completion_tokens == 15262
    assert totals.cost_usd == pytest.approx(0.964534)


def test_accumulator_accepts_alternate_provider_key_spellings() -> None:
    accumulator = UsageAccumulator()

    accumulator.record({"input_tokens": 11, "output_tokens": 3, "total_cost": 0.5})

    totals = accumulator.totals()
    assert totals.prompt_tokens == 11
    assert totals.completion_tokens == 3
    assert totals.cost_usd == pytest.approx(0.5)


def test_accumulator_ignores_missing_and_empty_usage_reports() -> None:
    accumulator = UsageAccumulator()

    accumulator.record(None)
    accumulator.record({})

    assert accumulator.totals() == UsageTotals()


def test_cost_stays_none_when_no_provider_prices_a_call() -> None:
    accumulator = UsageAccumulator()

    accumulator.record({"prompt_tokens": 7, "completion_tokens": 2})

    totals = accumulator.totals()
    assert totals.has_tokens
    assert totals.cost_usd is None


def test_usage_stats_renders_tokens_and_cost() -> None:
    stats = usage_stats(
        UsageTotals(prompt_tokens=123480, completion_tokens=15257, cost_usd=0.714534)
    )

    assert stats == {
        "Tokens in": "123,480",
        "Tokens out": "15,257",
        "Cost": "$0.7145",
    }


def test_usage_stats_omits_cost_when_unpriced() -> None:
    stats = usage_stats(UsageTotals(prompt_tokens=7, completion_tokens=2))

    assert stats == {"Tokens in": "7", "Tokens out": "2"}


@pytest.mark.parametrize(
    ("totals", "reason"),
    [
        (None, "no tracking scope"),
        (UsageTotals(), "no provider telemetry"),
    ],
)
def test_usage_stats_stays_empty_without_usable_telemetry(
    totals: UsageTotals | None,
    reason: str,
) -> None:
    assert usage_stats(totals) == {}, reason


@pytest.mark.parametrize(
    ("cost", "expected"),
    [
        (0.0591, "$0.0591"),
        (0.714534, "$0.7145"),
        (1.5, "$1.50"),
        (1234.5, "$1,234.50"),
    ],
)
def test_format_cost_keeps_inexpensive_runs_legible(
    cost: float,
    expected: str,
) -> None:
    assert format_cost(cost) == expected


def test_scope_isolates_totals_and_restores_previous_state() -> None:
    assert active_accumulator() is None

    with track_usage() as accumulator:
        accumulator.record({"prompt_tokens": 4, "completion_tokens": 1})
        assert active_totals() == UsageTotals(prompt_tokens=4, completion_tokens=1)

    assert active_accumulator() is None
    assert active_totals() is None


def test_scope_reaches_clients_created_inside_asyncio_run() -> None:
    """The CLI installs the scope around ``asyncio.run``; totals must survive."""

    async def compile_like_work() -> None:
        accumulator = active_accumulator()
        assert accumulator is not None
        accumulator.record(OPENAI_USAGE)

    with track_usage() as accumulator:
        asyncio.run(compile_like_work())

    assert accumulator.totals().prompt_tokens == 123480


def test_new_client_observes_usage_only_inside_a_tracking_scope() -> None:
    untracked = new_client(model="gpt-5.5")
    assert not any(
        isinstance(observer, UsageAccumulator) for observer in untracked.observers
    )

    with track_usage() as accumulator:
        tracked = new_client(model="gpt-5.5")

    assert accumulator in tracked.observers
