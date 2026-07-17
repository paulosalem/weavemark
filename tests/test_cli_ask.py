"""Tests for regular CLI compile-time ``@ask`` prompting."""

from __future__ import annotations

import pytest
from ellements.cli import CliPrinter

from weavemark.app import _prompt_for_compile_ask
from weavemark.compilation.ask import AskPrompt


def _ask_prompt() -> AskPrompt:
    return AskPrompt(
        question="What kind of city should the racing game use?",
        question_type="clarifying question",
        detail_level="20%",
        scope="racing game",
        reason="The answer changes the track design.",
        round_index=2,
        question_index=3,
    )


class TestCliAskPrompt:
    @pytest.mark.asyncio
    async def test_enter_submitting_reader_collects_answer(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        printer = CliPrinter("WeaveMark", verbose=False)
        prompts: list[str] = []

        def fake_input(prompt: str) -> str:
            prompts.append(prompt)
            return "Dense downtown grid with parks and tunnels."

        monkeypatch.setattr(printer.console, "input", fake_input)

        answer = await _prompt_for_compile_ask(printer, _ask_prompt())

        assert answer == "Dense downtown grid with parks and tunnels."
        assert prompts == [
            "[bold bright_cyan]Answer[/] [dim](Enter submits)[/]: ",
        ]
        assert "Answer received" in capsys.readouterr().err
