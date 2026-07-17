"""Modal screen for compile-time ``@ask`` questions in the TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from weavemark.compilation.ask import AskPrompt


class AskScreen(ModalScreen[str]):
    """Collect one compile-time ``@ask`` answer."""

    DEFAULT_CSS = """
    AskScreen {
        align: center middle;
    }

    #ask-container {
        width: 72%;
        max-width: 100;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }

    #ask-title {
        text-style: bold;
        color: $warning;
        height: auto;
        margin-bottom: 1;
    }

    #ask-question {
        text-style: bold;
        height: auto;
        margin-bottom: 1;
    }

    #ask-meta,
    #ask-reason,
    #ask-hints {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }

    #ask-answer {
        margin-bottom: 1;
    }

    #ask-buttons {
        height: auto;
        align: center middle;
    }

    #ask-buttons Button {
        min-width: 16;
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def __init__(self, prompt: AskPrompt, **kwargs) -> None:
        super().__init__(**kwargs)
        self._prompt = prompt

    def compose(self) -> ComposeResult:
        prompt = self._prompt
        with Vertical(id="ask-container"):
            yield Static("@ask", id="ask-title")
            yield Static(prompt.question, id="ask-question")
            meta = (
                f"Type: {prompt.question_type}  •  "
                f"Detail level: {prompt.detail_level}  •  "
                f"Round {prompt.round_index}, question {prompt.question_index}"
            )
            if prompt.scope:
                meta += f"  •  Scope: {prompt.scope}"
            yield Static(meta, id="ask-meta")
            if prompt.reason:
                yield Static(f"Why this matters: {prompt.reason}", id="ask-reason")
            yield Input(
                placeholder="Type your answer and press Enter…",
                id="ask-answer",
            )
            yield Static(
                "Enter submits the answer. Escape cancels this question.",
                id="ask-hints",
            )
            with Horizontal(id="ask-buttons"):
                yield Button("Submit Answer", id="btn-ask-submit", variant="primary")
                yield Button("Cancel", id="btn-ask-cancel", variant="default")

    def on_mount(self) -> None:
        self.query_one("#ask-answer", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "ask-answer":
            self.action_submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ask-submit":
            self.action_submit()
        elif event.button.id == "btn-ask-cancel":
            self.action_cancel()

    def action_submit(self) -> None:
        self.dismiss(self.query_one("#ask-answer", Input).value.strip())

    def action_cancel(self) -> None:
        self.dismiss("")
