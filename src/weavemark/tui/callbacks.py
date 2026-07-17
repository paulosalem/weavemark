"""TUI-based EditCallback for collaborative editing in the Textual app.

When a collaborative strategy calls ``request_edit()``, this callback
pushes an :class:`EditScreen` modal and waits for the user to review,
edit, approve, or abort via the TUI.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from weavemark.tui.screens.edit import EditResult, EditScreen

if TYPE_CHECKING:
    from textual.app import App


class TuiEditCallback:
    """EditCallback that uses the Textual TUI for collaborative editing.

    Compatible with the ``EditCallback`` protocol from
    ``ellements.execution``.  Pass this as ``edit_callback``
    in engine config when running collaborative specs in ``--ui`` mode.
    """

    def __init__(self, app: App, done_signal: str = "DONE") -> None:
        self._app = app
        self._done_signal = done_signal
        self._round = 0

    def _log(self, text: str) -> None:
        """Write a progress message to the StepLog if available."""
        try:
            from weavemark.tui.widgets.step_log import StepLog

            log = self._app.query_one("#step-log", StepLog)
            log.add_info(text)
        except Exception:
            pass

    def _spinner(self, show: bool) -> None:
        """Show or hide the loading spinner."""
        try:
            spinner = self._app.query_one("#llm-spinner")
            if show:
                spinner.add_class("active")
            else:
                spinner.remove_class("active")
        except Exception:
            pass

    async def request_edit(self, content: str, context: str = "") -> str:
        """Push a modal EditScreen and wait for the user's response."""
        self._round += 1
        ctx = (
            context
            or f"Round {self._round} — Review the AI-generated text and edit as needed."
        )

        self._log(f"✏️  Round {self._round} — Opening editor…")
        # Hide spinner while user is editing
        self._spinner(False)

        future: asyncio.Future[EditResult] = asyncio.get_running_loop().create_future()

        def _on_dismiss(result: EditResult | None) -> None:
            if result is None:
                future.set_result(EditResult(text=content, action="approve"))
            else:
                future.set_result(result)

        screen = EditScreen(
            content=content,
            context=ctx,
            done_signal=self._done_signal,
        )
        self._app.push_screen(screen, callback=_on_dismiss)

        result = await future

        # Log what the user chose and what happens next
        action = result.action
        if action == "approve":
            self._log("✓ Approved unchanged")
        elif action == "submit":
            self._log("✏ Edit submitted — waiting for LLM to continue…")
            self._spinner(True)
        elif action == "done":
            self._log("🏁 Done — finishing collaboration")
        elif action == "abort":
            self._log("✗ Aborted")

        # Append user message as an instruction block if provided
        text = result.text
        if result.message:
            self._log(f"💬 Message: {result.message[:80]}")
            text = text.rstrip() + f"\n\n---\nUser instruction: {result.message}\n---"

        return text
