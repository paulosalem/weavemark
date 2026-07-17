"""Pilot tests for compile-time ``@ask`` TUI prompts."""

from __future__ import annotations

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Static

from weavemark.compilation.ask import AskPrompt
from weavemark.tui.screens.ask import AskScreen


def _ask_prompt() -> AskPrompt:
    return AskPrompt(
        question="What kind of city should the racing game use?",
        question_type="clarifying question",
        detail_level="20%",
        scope="racing game",
        reason="The answer changes the track design.",
    )


class _AskApp(App):
    def __init__(self, prompt: AskPrompt | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._prompt = prompt or _ask_prompt()
        self.answer: str | None = None

    def compose(self) -> ComposeResult:
        yield Static("host")

    def on_mount(self) -> None:
        self.push_screen(AskScreen(self._prompt), callback=self._on_answer)

    def _on_answer(self, answer: str | None) -> None:
        self.answer = answer
        self.exit()


class TestAskScreen:
    @pytest.mark.asyncio
    async def test_enter_submits_answer(self) -> None:
        app = _AskApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            answer = app.screen.query_one("#ask-answer", Input)
            answer.value = "Dense downtown grid with parks and tunnels."
            await pilot.press("enter")
            await pilot.pause()

        assert app.answer == "Dense downtown grid with parks and tunnels."

    @pytest.mark.asyncio
    async def test_submit_button_submits_answer(self) -> None:
        app = _AskApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app.screen.query_one("#ask-answer", Input).value = "Coastal city."
            app.screen.query_one("#btn-ask-submit", Button).press()
            await pilot.pause()

        assert app.answer == "Coastal city."

    @pytest.mark.asyncio
    async def test_escape_cancels_with_empty_answer(self) -> None:
        app = _AskApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            app.screen.query_one("#ask-answer", Input).value = "Ignored."
            await pilot.press("escape")
            await pilot.pause()

        assert app.answer == ""
