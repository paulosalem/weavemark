"""Collaborative editing engine — wraps WeaveMark CollaborativeEditingStrategy."""

from __future__ import annotations

import asyncio
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ellements.execution import (
    CollaborativeEditingStrategy,
    OnStepCallback,
    PassthroughEditCallback,
)

from ..compilation.result import CompositionResult
from .base import ArtifactCallback, BaseEngine, ExecutionResult, RuntimeConfig


class AgentHandoffEditCallback:
    """Edit callback that asks an external AI agent to author each edit turn."""

    def __init__(
        self,
        handoff_dir: str | Path,
        *,
        done_signal: str = "DONE",
        timeout_seconds: float = 900.0,
        poll_seconds: float = 1.0,
        label: str = "WeaveMark collaborative example",
        announce: bool = True,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("agent_handoff_timeout_seconds must be greater than 0.")
        if poll_seconds <= 0:
            raise ValueError("agent_handoff_poll_seconds must be greater than 0.")
        self._handoff_dir = Path(handoff_dir)
        self._done_signal = done_signal
        self._timeout_seconds = timeout_seconds
        self._poll_seconds = poll_seconds
        self._label = label
        self._announce = announce
        self._index = 0

    async def request_edit(self, content: str, context: str = "") -> str:
        self._index += 1
        turn = self._prepare_turn(content, context)
        if self._announce:
            self._announce_turn(turn)
        await self._wait_for_response(turn.response_path)
        return turn.response_path.read_text(encoding="utf-8")

    def _prepare_turn(self, content: str, context: str) -> AgentHandoffTurn:
        self._handoff_dir.mkdir(parents=True, exist_ok=True)
        stem = f"turn-{self._index:03d}"
        request_path = self._handoff_dir / f"{stem}-request.md"
        response_path = self._handoff_dir / f"{stem}-response.md"
        if response_path.exists():
            response_path.unlink()
        request_path.write_text(
            self._render_request(content, context, response_path),
            encoding="utf-8",
        )
        return AgentHandoffTurn(
            index=self._index,
            request_path=request_path,
            response_path=response_path,
        )

    def _render_request(
        self,
        content: str,
        context: str,
        response_path: Path,
    ) -> str:
        return (
            f"# Agent collaboration turn {self._index}\n\n"
            f"**Example:** {self._label}\n\n"
            f"**Context:** {context or 'Collaborative edit turn'}\n\n"
            "You are the AI agent collaborating as the human/editor side of this "
            "WeaveMark example. Review the current draft and write the complete "
            "edited document to the response file below.\n\n"
            f"**Response file:** `{response_path}`\n\n"
            "## Response contract\n\n"
            "- Write the full edited document, not a diff or commentary.\n"
            "- To approve the draft unchanged, copy it exactly.\n"
            f"- To finish the collaboration, write the full document and add a "
            f"final line containing only `{self._done_signal}`.\n"
            "- To abort, create an empty response file.\n\n"
            "## Current draft\n\n"
            "```markdown\n"
            f"{content.rstrip()}\n"
            "```\n"
        )

    def _announce_turn(self, turn: AgentHandoffTurn) -> None:
        print(
            "\nWEAVEMARK_AGENT_TURN_REQUEST\n"
            f"request_path={turn.request_path}\n"
            f"response_path={turn.response_path}\n"
            "Write the complete edited document to response_path.\n"
            "WEAVEMARK_AGENT_TURN_WAITING\n",
            file=sys.stderr,
            flush=True,
        )

    async def _wait_for_response(self, response_path: Path) -> None:
        deadline = time.monotonic() + self._timeout_seconds
        while not response_path.exists():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    "Timed out waiting for agent collaboration response: "
                    f"{response_path}"
                )
            await asyncio.sleep(min(self._poll_seconds, remaining))
        await asyncio.sleep(self._poll_seconds)


@dataclass(frozen=True)
class AgentHandoffTurn:
    """Filesystem handoff paths for one collaborative edit turn."""

    index: int
    request_path: Path
    response_path: Path


class CollaborativeEngine(BaseEngine):
    """Human-in-the-loop collaborative editing engine.

    Requires named prompts: ``generate``, ``continue``.

    Accepts an optional ``edit_callback`` in the runtime config (or
    ``config`` block of the spec).  Runtime config can also provide
    ``agent_handoff_dir`` to ask an external AI agent for each edit turn.
    Defaults to
    :class:`ellements.execution.PassthroughEditCallback`
    so that specs can be executed non-interactively (e.g. in tests).
    """

    async def execute(
        self,
        result: CompositionResult,
        config: RuntimeConfig | None = None,
        on_step: OnStepCallback | None = None,
        on_artifact: ArtifactCallback | None = None,
    ) -> ExecutionResult:
        self._require_text_only(result, "collaborative")
        strategy = CollaborativeEditingStrategy()
        strategy_config = self._build_strategy_config(result, config, on_step)
        _materialize_agent_handoff_callback(strategy_config)
        # Ensure a callback is present; callers may inject their own via config
        strategy_config.setdefault("edit_callback", PassthroughEditCallback())
        sr = await strategy.execute(
            result.prompts or {"default": result.composed_prompt},
            self.client,
            tools=result.tools or None,
            config=strategy_config,
        )
        return self._wrap_result(sr, result, config)


def _materialize_agent_handoff_callback(strategy_config: dict[str, Any]) -> None:
    raw_handoff_dir = strategy_config.pop("agent_handoff_dir", None)
    if raw_handoff_dir is None or "edit_callback" in strategy_config:
        return
    if not isinstance(raw_handoff_dir, str | Path):
        raise ValueError("engine_config.agent_handoff_dir must be a path string.")
    done_signal = _read_optional_string(
        strategy_config,
        "done_signal",
        default="DONE",
    )
    timeout_seconds = _pop_optional_number(
        strategy_config,
        "agent_handoff_timeout_seconds",
        default=900.0,
    )
    poll_seconds = _pop_optional_number(
        strategy_config,
        "agent_handoff_poll_seconds",
        default=1.0,
    )
    label = _pop_optional_string(
        strategy_config,
        "agent_handoff_label",
        default="WeaveMark collaborative example",
    )
    announce = _pop_optional_bool(
        strategy_config,
        "agent_handoff_announce",
        default=True,
    )
    strategy_config["edit_callback"] = AgentHandoffEditCallback(
        raw_handoff_dir,
        done_signal=done_signal,
        timeout_seconds=timeout_seconds,
        poll_seconds=poll_seconds,
        label=label,
        announce=announce,
    )


def _pop_optional_string(
    strategy_config: dict[str, Any],
    key: str,
    *,
    default: str,
) -> str:
    raw_value = strategy_config.pop(key, default)
    if not isinstance(raw_value, str):
        raise ValueError(f"engine_config.{key} must be a string.")
    return raw_value


def _pop_optional_number(
    strategy_config: dict[str, Any],
    key: str,
    *,
    default: float,
) -> float:
    raw_value = strategy_config.pop(key, default)
    if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
        raise ValueError(f"engine_config.{key} must be a number.")
    return float(raw_value)


def _pop_optional_bool(
    strategy_config: dict[str, Any],
    key: str,
    *,
    default: bool,
) -> bool:
    raw_value = strategy_config.pop(key, default)
    if not isinstance(raw_value, bool):
        raise ValueError(f"engine_config.{key} must be a boolean.")
    return raw_value


def _read_optional_string(
    strategy_config: Mapping[str, Any],
    key: str,
    *,
    default: str,
) -> str:
    raw_value = strategy_config.get(key, default)
    if not isinstance(raw_value, str):
        raise ValueError(f"engine_config.{key} must be a string.")
    return raw_value
