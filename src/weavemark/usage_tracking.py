"""Scoped accumulation of provider-reported token usage and cost.

The Processor issues LLM calls from several places within one invocation:
semantic compilation, execution engines, and companion-driven steps. This module
collects the token and cost telemetry those calls report so the CLI can
summarize a whole run in its statistics footer.

Providers vary in what they report. Token counts are summed defensively across
the common key spellings, and cost is surfaced only when at least one provider
actually priced a call.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from ellements.core.observability import (
    LLMErrorEvent,
    LLMRequestEvent,
    LLMResponseEvent,
)

_PROMPT_TOKEN_KEYS = ("prompt_tokens", "input_tokens")
_COMPLETION_TOKEN_KEYS = ("completion_tokens", "output_tokens")
_COST_KEYS = ("cost_usd", "response_cost", "total_cost", "cost")
_CACHED_TOKEN_KEYS = ("cache_read_input_tokens", "cached_tokens")


@dataclass(frozen=True, slots=True)
class UsageTotals:
    """Provider-reported tokens and cost aggregated over one scope."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_prompt_tokens: int = 0
    cost_usd: float | None = None

    @property
    def has_tokens(self) -> bool:
        """Return whether any provider reported usable token counts."""

        return self.prompt_tokens > 0 or self.completion_tokens > 0

    @property
    def cache_hit_rate(self) -> float | None:
        """Return the share of prompt tokens served from the provider cache.

        ``None`` when no prompt tokens were reported, so callers can tell
        "nothing to cache" apart from "cached nothing".
        """

        if self.prompt_tokens <= 0:
            return None
        return self.cached_prompt_tokens / self.prompt_tokens


class UsageAccumulator:
    """LLM observer that sums provider-reported tokens and cost."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._cached_prompt_tokens = 0
        self._cost_usd = 0.0
        self._cost_reported = False

    async def on_request(self, event: LLMRequestEvent) -> None:
        """Ignore requests; usage is only known once a response returns."""

    async def on_response(self, event: LLMResponseEvent) -> None:
        """Accumulate the telemetry reported for one successful call."""

        self.record(event.usage)

    async def on_error(self, event: LLMErrorEvent) -> None:
        """Ignore failed calls, which carry no provider usage report."""

    def record(self, usage: Mapping[str, Any] | None) -> None:
        """Accumulate one usage mapping, tolerating partial provider data."""

        if not usage:
            return
        prompt = _numeric(usage, *_PROMPT_TOKEN_KEYS)
        completion = _numeric(usage, *_COMPLETION_TOKEN_KEYS)
        cached = _cached_prompt_tokens(usage)
        cost = _reported_cost(usage)
        with self._lock:
            self._prompt_tokens += prompt
            self._completion_tokens += completion
            self._cached_prompt_tokens += cached
            if cost is not None:
                self._cost_usd += cost
                self._cost_reported = True

    def totals(self) -> UsageTotals:
        """Return an immutable snapshot of everything accumulated so far."""

        with self._lock:
            return UsageTotals(
                prompt_tokens=self._prompt_tokens,
                completion_tokens=self._completion_tokens,
                cached_prompt_tokens=self._cached_prompt_tokens,
                cost_usd=self._cost_usd if self._cost_reported else None,
            )


_ACTIVE: ContextVar[UsageAccumulator | None] = ContextVar(
    "weavemark_usage_accumulator",
    default=None,
)


@contextmanager
def track_usage() -> Iterator[UsageAccumulator]:
    """Accumulate usage for every client created within this scope."""

    accumulator = UsageAccumulator()
    token = _ACTIVE.set(accumulator)
    try:
        yield accumulator
    finally:
        _ACTIVE.reset(token)


def active_accumulator() -> UsageAccumulator | None:
    """Return the accumulator installed by the surrounding scope, if any."""

    return _ACTIVE.get()


def active_totals() -> UsageTotals | None:
    """Return the surrounding scope's totals, or ``None`` when untracked."""

    accumulator = _ACTIVE.get()
    return accumulator.totals() if accumulator is not None else None


def usage_stats(totals: UsageTotals | None) -> dict[str, str]:
    """Render token and cost entries for a CLI statistics footer.

    Returns an empty mapping when no provider reported usable telemetry, so
    callers can merge unconditionally without displaying misleading zeros.
    """

    if totals is None or not totals.has_tokens:
        return {}
    stats = {"Tokens in": f"{totals.prompt_tokens:,}"}
    hit_rate = totals.cache_hit_rate
    if totals.cached_prompt_tokens and hit_rate is not None:
        stats["Tokens cached"] = f"{totals.cached_prompt_tokens:,} ({hit_rate:.0%})"
    stats["Tokens out"] = f"{totals.completion_tokens:,}"
    if totals.cost_usd is not None:
        stats["Cost"] = format_cost(totals.cost_usd)
    return stats


def format_cost(cost_usd: float) -> str:
    """Format a USD cost, keeping inexpensive runs legible."""

    precision = 2 if cost_usd >= 1 else 4
    return f"${cost_usd:,.{precision}f}"


def _numeric(usage: Mapping[str, Any], *keys: str) -> int:
    for key in keys:
        value = usage.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            return int(value)
    return 0


def _cached_prompt_tokens(usage: Mapping[str, Any]) -> int:
    """Extract cache-read prompt tokens across provider reporting shapes.

    Anthropic reports ``cache_read_input_tokens`` at the top level; OpenAI
    nests ``cached_tokens`` under ``prompt_tokens_details``.
    """

    cached = _numeric(usage, *_CACHED_TOKEN_KEYS)
    if cached:
        return cached
    details = usage.get("prompt_tokens_details")
    if isinstance(details, Mapping):
        return _numeric(details, *_CACHED_TOKEN_KEYS)
    if details is not None:
        for key in _CACHED_TOKEN_KEYS:
            value = getattr(details, key, None)
            if isinstance(value, bool):
                continue
            if isinstance(value, int | float):
                return int(value)
    return 0


def _reported_cost(usage: Mapping[str, Any]) -> float | None:
    for key in _COST_KEYS:
        value = usage.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            return float(value)
    return None


__all__ = [
    "UsageAccumulator",
    "UsageTotals",
    "active_accumulator",
    "active_totals",
    "format_cost",
    "track_usage",
    "usage_stats",
]
