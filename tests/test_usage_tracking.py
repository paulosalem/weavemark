"""Contracts for run-scoped token usage and cost reporting."""

from __future__ import annotations

import asyncio

import pytest

from weavemark.logging_setup import (
    new_client,
    requires_responses_api,
    responses_tool_schema,
)
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


def test_openai_nested_cached_tokens_are_accumulated() -> None:
    """OpenAI reports cache reads under ``prompt_tokens_details``."""

    accumulator = UsageAccumulator()

    accumulator.record(
        {
            "prompt_tokens": 115548,
            "completion_tokens": 5380,
            "prompt_tokens_details": {"cached_tokens": 113536},
            "response_cost": 0.228228,
        }
    )

    totals = accumulator.totals()
    assert totals.cached_prompt_tokens == 113536
    assert totals.cache_hit_rate == pytest.approx(0.98259, rel=1e-4)


def test_anthropic_top_level_cache_reads_are_accumulated() -> None:
    """Anthropic reports cache reads as a sibling of the prompt token count."""

    accumulator = UsageAccumulator()

    accumulator.record(
        {
            "prompt_tokens": 400,
            "completion_tokens": 10,
            "cache_read_input_tokens": 300,
        }
    )

    assert accumulator.totals().cached_prompt_tokens == 300


def test_cached_tokens_survive_non_mapping_usage_details() -> None:
    """LiteLLM may hand back a model object rather than a plain mapping."""

    class Details:
        cached_tokens = 64

    accumulator = UsageAccumulator()
    accumulator.record(
        {
            "prompt_tokens": 128,
            "completion_tokens": 8,
            "prompt_tokens_details": Details(),
        }
    )

    assert accumulator.totals().cached_prompt_tokens == 64


def test_footer_reports_the_cache_share_of_prompt_tokens() -> None:
    stats = usage_stats(
        UsageTotals(
            prompt_tokens=115548,
            completion_tokens=5380,
            cached_prompt_tokens=113536,
            cost_usd=0.228228,
        )
    )

    assert stats["Tokens in"] == "115,548"
    assert stats["Tokens cached"] == "113,536 (98%)"
    assert stats["Tokens out"] == "5,380"
    assert list(stats) == ["Tokens in", "Tokens cached", "Tokens out", "Cost"]


def test_footer_omits_the_cache_share_when_nothing_was_cached() -> None:
    """A cold or uncacheable run must not display a distracting 0%."""

    stats = usage_stats(UsageTotals(prompt_tokens=13133, completion_tokens=22342))

    assert stats["Tokens in"] == "13,133"
    assert "Tokens cached" not in stats


def test_cache_hit_rate_is_unknown_without_prompt_tokens() -> None:
    assert UsageTotals(completion_tokens=5).cache_hit_rate is None


def test_gpt_5_6_models_route_through_the_responses_api() -> None:
    """The GPT-5.6 family rejects tools plus reasoning on chat completions."""

    for model in ("gpt-5.6-sol", "gpt-5.6-terra", "openai/gpt-5.6", "GPT-5.6-Luna"):
        assert requires_responses_api(model), model


def test_earlier_models_keep_using_chat_completions() -> None:
    for model in ("gpt-5.5", "gpt-5.4-mini", "claude-opus-4.6", "gemini-3.1-pro"):
        assert not requires_responses_api(model), model


def test_new_client_selects_the_api_its_model_requires() -> None:
    assert new_client(model="gpt-5.6-terra").use_responses_api is True
    assert new_client(model="gpt-5.5").use_responses_api is False


def test_an_explicit_api_choice_is_never_overridden() -> None:
    client = new_client(model="gpt-5.6-terra", use_responses_api=False)

    assert client.use_responses_api is False


def test_chat_tool_definitions_are_flattened_for_the_responses_api() -> None:
    """Responses expects the callable's fields at the top level."""

    chat_tool = {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file.",
            "parameters": {"type": "object", "properties": {}},
        },
    }

    assert responses_tool_schema(chat_tool) == {
        "type": "function",
        "name": "read_file",
        "description": "Read a file.",
        "parameters": {"type": "object", "properties": {}},
    }


def test_already_flat_and_unrecognised_tools_pass_through_untouched() -> None:
    flat = {"type": "function", "name": "ping", "parameters": {}}
    hosted = {"type": "web_search"}

    assert responses_tool_schema(flat) == flat
    assert responses_tool_schema(hosted) == hosted
    assert responses_tool_schema("not a tool") == "not a tool"


def test_the_environment_can_force_a_model_onto_the_responses_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A future model with the same constraint must not need a release."""

    monkeypatch.setenv("WEAVEMARK_RESPONSES_API", "1")

    assert requires_responses_api("gpt-5.7-hypothetical")
    assert new_client(model="gpt-5.7-hypothetical").use_responses_api is True


def test_the_environment_can_force_a_model_back_onto_chat_completions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVEMARK_RESPONSES_API", "0")

    assert not requires_responses_api("gpt-5.6-terra")
    assert new_client(model="gpt-5.6-terra").use_responses_api is False


def test_a_blank_override_leaves_detection_alone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVEMARK_RESPONSES_API", "   ")

    assert requires_responses_api("gpt-5.6-terra")
    assert not requires_responses_api("gpt-5.5")
