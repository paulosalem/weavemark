"""CLI variable discovery, prompting, and missing-input validation."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from weavemark.settings import builtin_weavemark_settings, load_weavemark_settings
from weavemark.surfaces import lower_weavemark_surface
from weavemark.tui.scanner import SpecInput, scan_spec


class CliPrinterLike(Protocol):
    """Small printer surface used by guided CLI input collection."""

    console: Console

    def error(self, message: str) -> None: ...

    def success(self, message: str) -> None: ...


def discover_user_inputs(spec_text: str, base_dir: Path) -> list[SpecInput]:
    """Return user-facing inputs discovered in a spec without making an LLM call."""

    settings_result = load_weavemark_settings(base_dir)
    settings = (
        settings_result.settings
        if not settings_result.errors
        else builtin_weavemark_settings()
    )
    surface_result = lower_weavemark_surface(spec_text)
    scan_text = spec_text if surface_result.errors else surface_result.text
    return scan_spec(scan_text, settings).inputs


def missing_user_inputs(
    spec_text: str,
    variables: Mapping[str, Any],
    base_dir: Path,
) -> list[SpecInput]:
    """Return discovered inputs that do not have a supplied value."""

    return [
        spec_input
        for spec_input in discover_user_inputs(spec_text, base_dir)
        if spec_input.name not in variables or variables[spec_input.name] is None
    ]


def render_missing_inputs_error(
    printer: CliPrinterLike,
    missing_inputs: list[SpecInput],
    *,
    mode: str,
) -> None:
    """Render a non-interactive missing-input error."""

    names = ", ".join(f"@{{{spec_input.name}}}" for spec_input in missing_inputs)
    printer.error(
        f"{mode} cannot continue because required inputs are missing: {names}"
    )

    table = Table(
        title="Missing WeaveMark inputs",
        box=box.ROUNDED,
        show_lines=False,
        header_style="bold bright_yellow",
        border_style="yellow",
    )
    table.add_column("Input", style="bold bright_cyan")
    table.add_column("Kind", style="bright_white")
    table.add_column("Source", style="dim")
    for spec_input in missing_inputs:
        table.add_row(
            spec_input.name,
            _friendly_input_type(spec_input),
            spec_input.source_directive or "",
        )
    printer.console.print(table)
    printer.console.print(
        "[dim]Provide values with [bold]--var KEY=VALUE[/bold] or "
        "[bold]--vars-file vars.json[/bold]. Omit [bold]--batch-only[/bold] "
        "for guided prompts, or use [bold]--ui[/bold] for the full form.[/dim]"
    )


def prompt_for_missing_inputs(
    printer: CliPrinterLike,
    spec_text: str,
    variables: Mapping[str, Any],
    base_dir: Path,
) -> dict[str, Any] | None:
    """Ask for missing variables and return an updated variable mapping.

    Returns ``None`` when stdin ends or the user interrupts before all required
    inputs are collected.
    """

    missing_inputs = missing_user_inputs(spec_text, variables, base_dir)
    if not missing_inputs:
        return dict(variables)

    updated: dict[str, Any] = dict(variables)
    _render_prompt_intro(printer, missing_inputs)

    try:
        for spec_input in missing_inputs:
            updated[spec_input.name] = _ask_for_input(printer, spec_input)
    except (EOFError, KeyboardInterrupt):
        printer.console.print()
        printer.error("Input ended before all WeaveMark variables were collected.")
        return None

    printer.console.print()
    printer.success("Inputs collected. Composing with your values.")
    return updated


def _render_prompt_intro(
    printer: CliPrinterLike,
    missing_inputs: list[SpecInput],
) -> None:
    """Render the guided-input welcome panel."""

    count = len(missing_inputs)
    noun = "input" if count == 1 else "inputs"
    printer.console.print()
    printer.console.print(
        Panel(
            (
                f"[bold bright_yellow]WeaveMark needs {count} {noun} before compiling.[/bold bright_yellow]\n"
                "[dim]Press Ctrl+C to cancel. Values supplied by --var or --vars-file are already kept.[/dim]"
            ),
            title="Guided inputs",
            border_style="yellow",
            box=box.ROUNDED,
        )
    )

    table = Table(
        box=box.SIMPLE_HEAVY,
        header_style="bold bright_yellow",
        border_style="yellow",
        show_lines=False,
    )
    table.add_column("Input", style="bold bright_cyan")
    table.add_column("Kind", style="bright_white")
    table.add_column("Help", style="dim")
    for spec_input in missing_inputs:
        table.add_row(
            spec_input.name,
            _friendly_input_type(spec_input),
            spec_input.description or "",
        )
    printer.console.print(table)
    printer.console.print()


def _ask_for_input(printer: CliPrinterLike, spec_input: SpecInput) -> Any:
    if spec_input.input_type == "boolean":
        default = (spec_input.default or "false").lower() in {"true", "1", "yes"}
        return Confirm.ask(
            _prompt_label(spec_input),
            default=default,
            console=printer.console,
        )
    if spec_input.input_type == "select":
        return _ask_select(printer, spec_input)
    if spec_input.input_type == "multiline":
        return _ask_multiline(printer, spec_input)
    return Prompt.ask(_prompt_label(spec_input), console=printer.console)


def _ask_select(printer: CliPrinterLike, spec_input: SpecInput) -> str:
    options = spec_input.options or []
    if not options:
        return Prompt.ask(_prompt_label(spec_input), console=printer.console)

    table = Table(
        box=box.SIMPLE,
        show_header=False,
        border_style="bright_black",
        pad_edge=False,
    )
    table.add_column("Number", style="bold bright_yellow", justify="right")
    table.add_column("Value", style="bright_white")
    for index, option in enumerate(options, start=1):
        label = "default branch (_)" if option == "_" else option
        table.add_row(str(index), label)

    printer.console.print(f"[bold bright_cyan]{spec_input.name}[/bold bright_cyan]")
    if spec_input.description:
        printer.console.print(f"[dim]{spec_input.description}[/dim]")
    printer.console.print(table)

    choices = [str(index) for index in range(1, len(options) + 1)]
    selected = Prompt.ask(
        "Choose",
        choices=choices,
        default=choices[0],
        console=printer.console,
    )
    return options[int(selected) - 1]


def _ask_multiline(printer: CliPrinterLike, spec_input: SpecInput) -> str:
    printer.console.print(f"[bold bright_cyan]{spec_input.name}[/bold bright_cyan]")
    if spec_input.description:
        printer.console.print(f"[dim]{spec_input.description}[/dim]")
    printer.console.print(
        "[dim]Paste text below. Finish with an empty line. "
        "For long inputs, --vars-file is often more comfortable.[/dim]"
    )

    lines: list[str] = []
    while True:
        line = printer.console.input("  [dim]│[/dim] ")
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def _prompt_label(spec_input: SpecInput) -> str:
    return f"[bold bright_cyan]{spec_input.name}[/bold bright_cyan]"


def _friendly_input_type(spec_input: SpecInput) -> str:
    if spec_input.input_type == "select":
        return "choice"
    if spec_input.input_type == "boolean":
        return "yes/no"
    if spec_input.input_type == "multiline":
        return "text block"
    if spec_input.input_type == "file":
        return "file path"
    return "text"
