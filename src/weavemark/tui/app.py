"""WeaveMark TUI — main Textual application.

Launch with:
    weavemark spec.md --ui
    weavemark spec.md --ui --vars vars.json
"""

from __future__ import annotations

import asyncio
from contextlib import suppress
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.theme import Theme
from textual.widgets import (
    Button,
    Footer,
    Header,
    LoadingIndicator,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from weavemark.protection import ProtectionContext
from weavemark.settings import load_weavemark_settings
from weavemark.tui.scanner import scan_spec
from weavemark.tui.screens.ask import AskScreen
from weavemark.tui.screens.input import InputForm
from weavemark.tui.widgets.preview import PreviewPane
from weavemark.tui.widgets.spec_info import SpecInfoPanel
from weavemark.tui.widgets.step_log import StepLog
from weavemark.variable_files import load_variables_file

# Golden theme inspired by the @execute directive color (#FFD700)
WEAVEMARK_THEME = Theme(
    name="weavemark-gold",
    primary="#FFD700",  # gold
    secondary="#FFA500",  # orange (prompt directive)
    accent="#E6BE00",  # darker gold
    warning="#FFA500",
    error="#FF6B6B",
    success="#50C878",  # emerald green
    foreground="#F5F0E1",  # warm white
    background="#1A1612",  # very dark warm brown
    surface="#241E18",  # dark brown
    panel="#2E2720",  # slightly lighter brown
    dark=True,
)


class WeaveMarkApp(App):
    """Interactive TUI for WeaveMark files."""

    TITLE = "WeaveMark Runner"
    CSS_PATH = "theme.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+r", "run_spec", "Run", show=False),
        Binding("ctrl+p", "compose_spec", "Compose", show=True),
        Binding("ctrl+l", "toggle_left_panel", "Toggle Inputs", show=True),
        Binding("ctrl+o", "toggle_status_panel", "Toggle Status", show=True),
    ]

    def __init__(
        self,
        spec_path: Path,
        vars_path: Path | None = None,
        config_path: Path | None = None,
        protection: ProtectionContext | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.register_theme(WEAVEMARK_THEME)
        self.theme = "weavemark-gold"
        self._spec_path = spec_path
        self._vars_path = vars_path
        self._config_path = config_path
        self._protection = protection
        self._spec_text = spec_path.read_text()
        self._metadata = scan_spec(self._spec_text)
        self._initial_vars = self._load_vars(vars_path)

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main-container"):
            # Left: spec info + input form
            with Vertical(id="left-panel"):
                with ScrollableContainer(id="left-scroll"):
                    yield SpecInfoPanel(self._metadata, id="spec-info")
                    yield Static("[bold]Inputs[/bold]", markup=True)
                    yield InputForm(self._metadata.inputs, id="input-form")

                # Action buttons (outside scroll, fixed at bottom)
                with Horizontal(id="action-bar"):
                    yield Button("Compose", id="btn-compose", variant="primary")
                    yield Button("▶ Run", id="btn-run", variant="success")

            # Right: tabbed preview/current-text + output
            with Vertical(id="right-panel"):
                with TabbedContent(id="right-tabs"):
                    with TabPane("Current Text", id="tab-current"):
                        yield Static(
                            "[bold]Current Text[/bold] — updated after each round",
                            markup=True,
                            id="current-title",
                        )
                        yield TextArea(
                            "No text yet — run the spec to see output here.",
                            id="current-text-pane",
                            read_only=True,
                        )
                    with TabPane("Prompt Preview", id="tab-preview"):
                        yield Static(
                            f"[bold]Prompt Preview[/bold] — {self._spec_path.name}",
                            markup=True,
                            id="preview-title",
                        )
                        yield PreviewPane(self._spec_text, id="preview-pane")
                yield LoadingIndicator(id="llm-spinner")
                yield Static("[bold]Status[/bold]", markup=True, id="output-title")
                with Vertical(id="status-panel"):
                    yield StepLog(id="step-log")

        yield Footer()

    def on_mount(self) -> None:
        """Pre-fill form if vars were provided, then refresh preview."""
        if self._initial_vars:
            form = self.query_one("#input-form", InputForm)
            form.set_values(self._initial_vars)
        self._refresh_preview()

    # ── Event handlers ────────────────────────────────────────────

    def on_input_changed(self, event) -> None:
        self._request_preview_refresh()

    def on_text_area_changed(self, event) -> None:
        self._request_preview_refresh()

    def on_select_changed(self, event) -> None:
        self._request_preview_refresh()

    def on_switch_changed(self, event) -> None:
        self._request_preview_refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-compose":
            self.action_compose_spec()
        elif event.button.id == "btn-run":
            self.action_run_spec()

    # ── Actions ───────────────────────────────────────────────────

    def action_compose_spec(self) -> None:
        """Compose the spec with current form values."""
        self.run_worker(self._do_compose(), exclusive=True, thread=False)

    def action_run_spec(self) -> None:
        """Compose and execute the spec."""
        self.run_worker(self._do_run(), exclusive=True, thread=False)

    def action_toggle_left_panel(self) -> None:
        """Show or hide the left input panel (Ctrl+L)."""
        panel = self.query_one("#left-panel")
        panel.display = not panel.display

    def action_toggle_status_panel(self) -> None:
        """Show or hide the status/output panel (Ctrl+O)."""
        try:
            title = self.query_one("#output-title")
            panel = self.query_one("#status-panel")
            vis = not panel.display
            title.display = vis
            panel.display = vis
        except Exception:
            pass

    async def _do_compose(self) -> None:
        """Compose the spec using the controller."""
        log = self.query_one("#step-log", StepLog)
        log.clear()
        log.add_info("Composing…")
        self._show_spinner()

        values = self._get_form_values()
        try:
            from weavemark.controller import WeaveMarkController

            runtime_config = self._load_runtime_config()
            config = self._build_config(runtime_config)
            controller = WeaveMarkController(config)
            result = await controller.compose(
                self._spec_text,
                variables=values,
                base_dir=self._spec_path.parent,
                ask_handler=self._prompt_for_compile_ask,
                protection=self._protection,
            )
            # Show result in the preview
            prompt_text = result.composed_prompt
            preview = self.query_one("#preview-pane", PreviewPane)
            preview.update(
                f"[bold green]Composed prompt:[/bold green]\n\n{prompt_text}"
            )
            log.add_step("done", f"Composed ({len(prompt_text)} chars)")
        except Exception as exc:
            log.add_error(str(exc))
        finally:
            self._hide_spinner()

    async def _do_run(self) -> None:
        """Compose and execute the spec with the engine."""
        log = self.query_one("#step-log", StepLog)
        log.clear()
        log.add_info("Running…")
        self._show_spinner()

        values = self._get_form_values()
        try:
            from weavemark.controller import WeaveMarkController
            from weavemark.engines import resolve_engine
            from weavemark.logging_setup import new_client

            runtime_config = self._load_runtime_config()
            config = self._build_config(runtime_config)
            controller = WeaveMarkController(config)

            # Compose
            log.add_step("generate", "Composing prompt…")
            composed = await controller.compose(
                self._spec_text,
                variables=values,
                base_dir=self._spec_path.parent,
                ask_handler=self._prompt_for_compile_ask,
                protection=self._protection,
            )

            # Determine engine
            strategy = runtime_config.engine or "single-call"
            if runtime_config.engine is None and self._metadata.execution:
                strategy = self._metadata.execution.get("type", "single-call")

            engine = resolve_engine(
                strategy,
                client=new_client(
                    model=config.model,
                    protection=self._protection,
                    logging_settings=load_weavemark_settings(
                        self._spec_path.parent
                    ).settings.logging,
                ),
                protection=self._protection,
            )

            runtime_config.model = config.model
            runtime_config.protection = self._protection
            runtime_config.execution_variables = dict(values)
            if strategy == "collaborative":
                from weavemark.tui.callbacks import TuiEditCallback

                done_signal = "DONE"
                if self._metadata.execution:
                    done_signal = self._metadata.execution.get("done_signal", "DONE")
                runtime_config.engine_config["edit_callback"] = TuiEditCallback(
                    self,
                    done_signal=done_signal,
                )
                log.add_info("Collaborative mode — edit in the pop-up editor")
                # Hide left panel to give full width to collaboration
                self.query_one("#left-panel").display = False
                # Switch to Current Text tab and collapse status panel
                with suppress(Exception):
                    self.query_one("#right-tabs", TabbedContent).active = "tab-current"
                with suppress(Exception):
                    self.query_one("#output-title").display = False
                    self.query_one("#status-panel").display = False

            # Execute with step callback
            def on_step(step):
                step_name = getattr(step, "name", "step")
                step_text = getattr(step, "response", str(step))[:150]
                step_meta = getattr(step, "metadata", None)
                log.add_step(step_name, step_text, step_meta)
                # Update the "Current Text" pane with latest content
                full_response = getattr(step, "response", "")
                if full_response:
                    self._update_current_text(full_response)

            exec_result = await engine.execute(
                composed,
                config=runtime_config,
                on_step=on_step,
            )

            # Show final result
            final_text = exec_result.output
            self._update_current_text(final_text)
            # Auto-switch to Current Text tab
            with suppress(Exception):
                self.query_one("#right-tabs", TabbedContent).active = "tab-current"
            log.add_step("done", f"Finished ({len(final_text)} chars)")

        except Exception as exc:
            log.add_error(str(exc))
        finally:
            self._hide_spinner()

    def _update_current_text(self, text: str) -> None:
        """Update the 'Current Text' tab pane with new content."""
        try:
            pane = self.query_one("#current-text-pane", TextArea)
            pane.load_text(text)
        except Exception:
            pass

    async def _prompt_for_compile_ask(self, prompt) -> str:
        """Collect one compile-time ``@ask`` answer from the TUI."""

        log = self.query_one("#step-log", StepLog)
        log.add_step("ask", prompt.question)
        self._hide_spinner()

        future: asyncio.Future[str] = asyncio.get_running_loop().create_future()

        def _on_dismiss(answer: str | None) -> None:
            future.set_result(answer or "")

        self.push_screen(AskScreen(prompt), callback=_on_dismiss)
        try:
            return await future
        finally:
            self._show_spinner()

    def _show_spinner(self) -> None:
        """Show the animated loading indicator."""
        with suppress(Exception):
            self.query_one("#llm-spinner").add_class("active")

    def _hide_spinner(self) -> None:
        """Hide the animated loading indicator."""
        with suppress(Exception):
            self.query_one("#llm-spinner").remove_class("active")

    def _refresh_preview(self) -> None:
        """Update the preview pane with current form values."""
        try:
            preview = self.query_one("#preview-pane", PreviewPane)
            values = self._get_form_values()
            preview.update_values(values)
        except Exception:
            pass  # not mounted yet

    def _request_preview_refresh(self) -> None:
        """Refresh preview immediately and again after the next UI refresh."""
        self._refresh_preview()
        self.call_after_refresh(self._refresh_preview)

    def _get_form_values(self) -> dict[str, str]:
        form = self.query_one("#input-form", InputForm)
        return form.get_values()

    def _load_runtime_config(self):
        """Load an explicit runtime override when one was supplied."""
        from weavemark.engines import RuntimeConfig

        if self._config_path is None:
            return RuntimeConfig()
        if not self._config_path.is_file():
            raise FileNotFoundError(f"Runtime config not found: {self._config_path}")
        return RuntimeConfig.from_file(self._config_path)

    def _build_config(self, runtime_config=None):
        """Build compiler settings from the optional runtime override."""
        from weavemark.controller import WeaveMarkConfig
        from weavemark.defaults import DEFAULT_MODEL

        runtime = runtime_config or self._load_runtime_config()
        return WeaveMarkConfig(
            model=runtime.model or DEFAULT_MODEL,
            temperature=(
                runtime.temperature if runtime.temperature is not None else 0.3
            ),
        )

    @staticmethod
    def _load_vars(vars_path: Path | None) -> dict[str, str]:
        """Load variables from a JSON or YAML file."""
        if vars_path is None:
            return {}
        data = load_variables_file(vars_path)
        return {key: str(value) for key, value in data.items()}


def launch_tui(
    spec_path: Path,
    vars_path: Path | None = None,
    config_path: Path | None = None,
    protection: ProtectionContext | None = None,
) -> None:
    """Entry point for --ui mode."""
    app = WeaveMarkApp(
        spec_path=spec_path,
        vars_path=vars_path,
        config_path=config_path,
        protection=protection,
    )
    app.run()


async def launch_tui_async(
    spec_path: Path,
    vars_path: Path | None = None,
    config_path: Path | None = None,
    protection: ProtectionContext | None = None,
) -> None:
    """Entry point for launching the TUI from an existing asyncio loop."""
    app = WeaveMarkApp(
        spec_path=spec_path,
        vars_path=vars_path,
        config_path=config_path,
        protection=protection,
    )
    await app.run_async()
