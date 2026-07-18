"""WeaveMark Processor — CLI entry point.

Composes prompts from promplet files containing directives (@refine, @if,
@match, @compile, @emit, @note) and variable substitutions.

Usage:
    weavemark spec.md                                    # guided interactive compile
    weavemark spec.md --var key=value                    # prefill one input
    weavemark spec.md --vars-file v.json                 # prefill many inputs
    weavemark spec.md --batch-only --var k=v             # strict non-interactive batch
    weavemark spec.md --output result.md                 # write primary to file
    weavemark spec.md --output-dir out/                  # write artifacts to dir
    weavemark spec.md --format json --output result.json # JSON to file
    cat spec.md | weavemark --stdin --batch-only
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ellements.cli import (
    CliPrinter,
)
from ellements.cli import (
    section_rule as cli_section_rule,
)
from ellements.cli import (
    stats_footer as cli_stats_footer,
)
from ellements.cli import (
    step_log as cli_step_log,
)
from ellements.cli import (
    success as cli_success,
)
from ellements.cli import (
    tool_use_badge as cli_tool_use_badge,
)
from ellements.cli import (
    warning as cli_warning,
)
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.progress import TaskID
from rich.prompt import Confirm

from weavemark.cli_inputs import (
    missing_user_inputs,
    prompt_for_missing_inputs,
    render_missing_inputs_error,
)
from weavemark.compilation.ask import AskPrompt
from weavemark.compilation.diagnostics import Diagnostic, UserDiagnosticError
from weavemark.compilation.provenance import (
    ProvenanceOptions,
    ReplayMismatchError,
)
from weavemark.compilation.result import CompositionResult
from weavemark.compile_options import (
    DEFAULT_COMPILE_FORMAT,
    extension_for_compile_format,
    normalize_compile_format,
    supported_compile_formats_text,
)
from weavemark.controller import (
    WeaveMarkConfig,
    WeaveMarkController,
    _cleanup_litellm_logging_worker,
)
from weavemark.defaults import DEFAULT_MODEL
from weavemark.implementation import (
    ImplementationError,
    ImplementationRequest,
    print_dry_run,
    run_implementation,
)
from weavemark.logging_setup import (
    configure_logging,
    get_logger,
    log_cli_invocation,
)
from weavemark.protection import (
    ProtectionContext,
    ProtectionError,
    ProtectionRequest,
)
from weavemark.settings import (
    WeaveMarkSettings,
    builtin_weavemark_settings,
    load_weavemark_settings,
)
from weavemark.surfaces import lower_weavemark_surface
from weavemark.traces import execution_result_to_dict, render_execution_trace_markdown
from weavemark.version import LANGUAGE_VERSION, PROCESSOR_VERSION

if TYPE_CHECKING:
    from weavemark.engines import ExecutionResult

logger = get_logger("cli")

# ------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------


class WeaveMarkEventRenderer:
    """Render WeaveMark-specific verbose controller events."""

    def render(
        self,
        event_type: str,
        data: Mapping[str, Any],
        console: Console,
    ) -> None:
        if event_type == "composing":
            cli_section_rule(
                f"⚙ Semantic compilation · round {data.get('compile_effect_round')}",
                style="bright_blue",
                console=console,
            )
            cli_step_log(
                f"[dim]Model[/] [bright_cyan]{escape(str(data.get('model', '')))}[/]",
                position="first",
                console=console,
            )
            cli_step_log(
                f"[dim]Variables[/] [bright_cyan]{data.get('num_variables')}[/]",
                console=console,
            )
            cli_step_log(
                f"[dim]Source size[/] [bright_cyan]{data.get('spec_length')} chars[/]",
                position="last",
                console=console,
            )
            return

        if event_type == "tool_call":
            name = escape(str(data.get("name", "")))
            args = data.get("args") or {}
            target = ""
            if isinstance(args, Mapping):
                target_value = args.get("file_name") or args.get("question")
                if target_value:
                    target = f" [dim]{escape(str(target_value))}[/]"
            cli_tool_use_badge(f"{name}{target}", console=console)
            return

        if event_type == "tool_result":
            name = escape(str(data.get("name", "")))
            is_error = bool(data.get("error"))
            status = "[bright_red]error[/]" if is_error else "[bright_green]ok[/]"
            file_name = data.get("file")
            target = f" [dim]{escape(str(file_name))}[/]" if file_name else ""
            size = data.get("size")
            size_text = f", {size:,} chars" if isinstance(size, int) else ""
            cli_step_log(
                f"[bold]{name}[/]{target} ({status}{size_text})",
                position="mid",
                console=console,
            )
            return

        if event_type == "transition":
            text = escape(str(data.get("text", "") or ""))
            cli_step_log(
                f"🧭 [bold bright_magenta]Transition {data.get('step')}[/] [dim]{text}[/]",
                position="mid",
                console=console,
            )
            return

        if event_type == "compile_effect_round":
            remaining = data.get("remaining_iterate_count")
            if remaining is None:
                remaining = data.get("remaining_ask_count")
            cli_step_log(
                f"🔁 [bold bright_magenta]Compile-effect round "
                f"{data.get('completed_round')} complete[/] "
                f"[dim]remaining effects: {remaining}[/]",
                position="mid",
                console=console,
            )
            return

        if event_type == "ask_question":
            cli_step_log(
                f"❓ [bold]@ask question[/] [dim]round {data.get('round')}[/]",
                position="mid",
                console=console,
            )
            return

        if event_type == "ask_answer":
            cli_step_log(
                f"✓ [bold]@ask answer recorded[/] [dim]{data.get('answer_length')} chars[/]",
                position="mid",
                console=console,
            )
            return

        if event_type == "issue":
            severity = escape(str(data.get("severity", "issue")))
            message = escape(str(data.get("message", data)))
            cli_warning(f"{severity}: {message}", console=console)
            return

        if event_type == "done":
            cli_success("Composition complete", console=console)
            cli_stats_footer(
                {
                    "Tool calls": data.get("tool_calls_made", 0),
                    "Diagnostics": data.get("diagnostics_count", 0),
                    "Output": f"{data.get('output_length', 0)} chars",
                },
                console=console,
            )
            return

        if event_type == "iterate_start":
            requested = data.get("requested_turns")
            effective = data.get("effective_turns")
            cap = data.get("config_max_turns")
            ask = "enabled" if data.get("ask_wrapper") else "disabled"
            scope = "whole spec" if data.get("whole_spec") else "body"
            requested_text = "config default" if requested is None else str(requested)
            console.print(
                Panel(
                    "\n".join(
                        [
                            "[bold bright_magenta]Iterative compilation begins[/]",
                            "[dim]Criterion:[/] step-level material improvement",
                            (
                                f"[dim]Turns:[/] requested {requested_text}, "
                                f"effective {effective} (config cap {cap})"
                            ),
                            f"[dim]Ask prelude:[/] {ask}",
                            f"[dim]Target:[/] {scope}",
                        ]
                    ),
                    title="↻ @iterate",
                    border_style="bright_magenta",
                )
            )
            return

        if event_type == "iterate_judge":
            satisfied = bool(data.get("satisfied"))
            icon = "✅" if satisfied else "⚖️ "
            verdict = "satisfied" if satisfied else "not yet"
            why = escape(str(data.get("why", "") or "No explanation provided."))
            console.print(
                f"  {icon} [bold]Judge turn {data.get('turn')}[/]: "
                f"[bright_green]{verdict}[/] — [dim]{why}[/]"
            )
            return

        if event_type == "iterate_improve":
            feedback = escape(str(data.get("feedback", "")))
            console.print(
                f"  🛠️  [bold]Improve turn {data.get('turn')}[/]: "
                f"[dim]responding to judge feedback — {feedback}[/]"
            )
            return

        if event_type == "iterate_complete":
            reason = escape(str(data.get("reason", "")))
            console.print(
                Panel(
                    (
                        "[bold bright_green]Iteration converged[/]\n"
                        f"[dim]Improvement turns used:[/] {data.get('turns_used')}\n"
                        f"[dim]Reason:[/] {reason}"
                    ),
                    title="✓ @iterate complete",
                    border_style="bright_green",
                )
            )
            return

        if event_type == "iterate_exhausted":
            why = escape(str(data.get("why_not_yet", "")))
            console.print(
                Panel(
                    (
                        "[bold bright_yellow]Iteration budget exhausted[/]\n"
                        f"[dim]Improvement turns used:[/] {data.get('turns_used')}\n"
                        f"[dim]Best-effort warning:[/] {why}"
                    ),
                    title="⚠ @iterate",
                    border_style="yellow",
                )
            )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="weavemark",
        description=(
            "WeaveMark Processor: compose promplets into concrete prompt artifacts. "
            "By default, the Processor runs in guided interactive mode and asks "
            "for any missing inputs."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Modes:\n"
            "  default        Guided compile. Missing @{variables}, @match choices, and @if flags are prompted.\n"
            "  --batch-only   Strict non-interactive compile. Missing inputs fail before compilation.\n"
            "  --run          Compile, then execute through the declared or configured engine.\n"
            "  --implement    Compile, then hand the compiled spec to a configured programming agent.\n"
            "  --ui           Full terminal form for inspecting and running a spec.\n"
            "  --scan         Print discovered inputs and metadata as JSON; no LLM call.\n\n"
            "Commands:\n"
            "  library        Run or browse built-in and custom promplets.\n"
            "  implement      Hand a compiled specification to a programming agent.\n\n"
            "Examples:\n"
            "  weavemark library tutorial-generator\n"
            "  weavemark library investment-brief --var ticker=MSFT\n"
            "  weavemark library list finance --source all\n"
            "  weavemark promplets/catalog/executable/tree-of-thought-solver.weavemark.md --run --config promplets/catalog/executable/tree-of-thought-solver.weavemark.yaml\n"
            "  weavemark implement compiled-spec.md --name my-app --dry-run\n"
            "  weavemark promplets/catalog/standalone/ai-kanban-board.weavemark.md --implement --implementation-name ai-kanban --implementation-dry-run\n"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=(
            f"%(prog)s {PROCESSOR_VERSION} "
            f"(WeaveMark language {LANGUAGE_VERSION})"
        ),
    )

    # Input
    parser.add_argument(
        "spec_file",
        nargs="?",
        help="Path to the .weavemark.md file to compile. Omit only with --stdin or --discover.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read the spec from stdin. This implies non-interactive batch behavior.",
    )

    # Variables
    parser.add_argument(
        "--var",
        action="append",
        metavar="KEY=VALUE",
        help=(
            "Set or prefill one input (repeatable). Values override --vars-file. "
            "Booleans accept true/false, yes/no, or 1/0."
        ),
    )
    parser.add_argument(
        "--vars-file",
        type=Path,
        help="Load input values from a JSON object. Missing values are still prompted in default mode.",
    )

    # Output
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Write the primary composed prompt to this file. @emit and role-tagged "
            "@prompt sibling artifacts are written next to it."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        dest="output_dir",
        help=(
            "Write all artifacts into this directory. The primary composed prompt "
            "is written as <spec-stem>.md (or output.md when reading from stdin), "
            "and @emit / role-tagged @prompt files use their declared names. "
            "Mutually exclusive with --output."
        ),
    )
    parser.add_argument(
        "--trace-output",
        type=Path,
        help="With --run, write a readable Markdown trace of execution steps to this file.",
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        metavar="FILE",
        help=(
            "Write an optional compilation provenance manifest with hashes, "
            "lineage, latency, token usage, and provider-reported cost."
        ),
    )
    parser.add_argument(
        "--record-run",
        type=Path,
        metavar="DIR",
        help=(
            "Record a replayable compilation bundle. The bundle contains full "
            "LLM requests/responses and may contain sensitive content."
        ),
    )
    parser.add_argument(
        "--replay-run",
        type=Path,
        metavar="DIR",
        help=(
            "Replay a recorded compilation strictly offline; fail on any request "
            "or local-resource mismatch."
        ),
    )
    parser.add_argument(
        "--show-output",
        action="store_true",
        help="Print the primary composed or executed output even when --output or --output-dir is set.",
    )
    parser.add_argument(
        "--no-file-summary",
        action="store_true",
        help="Write requested output files without printing per-file success messages.",
    )
    parser.add_argument(
        "--format",
        default=None,
        dest="format",
        help=(
            "Output format. Overrides @compile format when supplied; "
            "defaults to @compile format or markdown."
        ),
    )

    # Mode
    parser.add_argument(
        "--batch-only",
        action="store_true",
        help="Disable all prompts. If any discovered input is missing, fail before compiling.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Compile and execute the composed prompt through an @execute or --config runtime engine.",
    )
    parser.add_argument(
        "--implement",
        action="store_true",
        help=(
            "After compiling, implement the compiled spec with the configured "
            "headless implementation profile."
        ),
    )
    parser.add_argument(
        "--no-protections",
        action="store_true",
        help=(
            "Disable all experimental promplet protections for this invocation. "
            "Use only when you deliberately trust the promplet and its code/resources."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed step-by-step progress",
    )

    # Model
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Text/vision model used for semantic compilation and execution. "
            f"Overrides runtime config (default: {DEFAULT_MODEL})."
        ),
    )
    parser.add_argument(
        "--image-model",
        default=None,
        help="Image-generation model override; never inferred from --model.",
    )

    # Config
    parser.add_argument(
        "--config",
        type=Path,
        help="Runtime config for --run: engine, prompt settings, tool bindings, and variables.",
    )
    parser.add_argument(
        "--implementation-name",
        help="Name for the implementation workspace. Defaults to the source stem.",
    )
    parser.add_argument(
        "--implementation-profile",
        help="Implementation profile from weavemark.json. Defaults to implementation.default_profile.",
    )
    parser.add_argument(
        "--implementation-output-root",
        type=Path,
        help="Root directory for implementation workspaces.",
    )
    parser.add_argument(
        "--implementation-model",
        help="Model value exposed to implementation profile templates as {model}.",
    )
    parser.add_argument(
        "--implementation-extra-instruction",
        action="append",
        help="Extra instruction appended to the implementation-agent prompt.",
    )
    parser.add_argument(
        "--implementation-reuse-dir",
        action="store_true",
        help="Allow implementing into an existing non-empty implementation directory.",
    )
    parser.add_argument(
        "--implementation-dry-run",
        action="store_true",
        help="Prepare implementation artifacts and print the resolved command without running it.",
    )

    # TUI
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch the full terminal UI with an input form, live preview, compose, and run actions.",
    )

    # Discovery
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Launch promplet discovery chat to find and open the right spec interactively.",
    )
    parser.add_argument(
        "--library-dir",
        action="append",
        type=Path,
        metavar="DIR",
        help="Additional promplet-library root (repeatable).",
    )
    parser.add_argument(
        "--env",
        action="store_true",
        help="Print resolved discovery configuration and environment, then exit.",
    )

    # Machine-readable scan (used by VS Code extension)
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Output promplet metadata as JSON: inputs, title, outputs, tools, and execution strategy.",
    )

    return parser


def create_implement_parser() -> argparse.ArgumentParser:
    """Create the parser for ``weavemark implement``."""

    parser = argparse.ArgumentParser(
        prog="weavemark implement",
        description=(
            "Implement an already-compiled WeaveMark software specification "
            "using a configured headless programming-agent profile."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  weavemark implement compiled-spec.md\n"
            "  weavemark implement compiled-spec.md --name orbital-drift --profile copilot\n"
            "  weavemark implement compiled-spec.md --profile claude-code --dry-run\n"
        ),
    )
    parser.add_argument(
        "compiled_spec",
        type=Path,
        help="Path to the compiled software specification to implement.",
    )
    parser.add_argument(
        "--name",
        help="Name for the implementation workspace. Defaults to the compiled spec stem.",
    )
    parser.add_argument(
        "--profile",
        help="Implementation profile from weavemark.json. Defaults to implementation.default_profile.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Root directory for implementation workspaces.",
    )
    parser.add_argument(
        "--model",
        help="Model value exposed to implementation profile templates as {model}.",
    )
    parser.add_argument(
        "--extra-instruction",
        action="append",
        help="Extra instruction appended to the implementation-agent prompt.",
    )
    parser.add_argument(
        "--reuse-dir",
        action="store_true",
        help="Allow implementing into an existing non-empty implementation directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare implementation artifacts and print the resolved command without running it.",
    )
    parser.add_argument(
        "--no-protections",
        action="store_true",
        help=(
            "Disable all experimental protections for this invocation. "
            "Use only for trusted compiled specs and implementation profiles."
        ),
    )
    parser.add_argument(
        "--no-file-summary",
        action="store_true",
        help="Write requested files without printing per-file success messages.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed progress.",
    )
    return parser


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _parse_variables(printer: CliPrinter, args: argparse.Namespace) -> dict[str, Any]:
    """Merge variables from --var flags and --vars-file."""
    variables: dict[str, Any] = {}

    if args.vars_file:
        try:
            with open(args.vars_file, encoding="utf-8") as handle:
                loaded = json.load(handle)
        except OSError as exc:
            raise UserDiagnosticError(
                Diagnostic(
                    code="WM-INPUT-VARS-READ",
                    message=f"Could not read variables file: {exc}",
                    source=str(args.vars_file),
                    parameter="--vars-file",
                )
            ) from exc
        except json.JSONDecodeError as exc:
            raise UserDiagnosticError(
                Diagnostic(
                    code="WM-INPUT-VARS-JSON",
                    message=exc.msg,
                    source=str(args.vars_file),
                    line=exc.lineno,
                    parameter="--vars-file",
                    suggestion="Provide one valid JSON object.",
                )
            ) from exc
        if not isinstance(loaded, dict):
            raise UserDiagnosticError(
                Diagnostic(
                    code="WM-INPUT-VARS-SHAPE",
                    message="Variables file must contain one JSON object.",
                    source=str(args.vars_file),
                    parameter="--vars-file",
                )
            )
        variables.update(loaded)

    if args.var:
        for item in args.var:
            if "=" not in item:
                raise UserDiagnosticError(
                    Diagnostic(
                        code="WM-INPUT-VAR-SYNTAX",
                        message=f"Malformed --var value {item!r}.",
                        parameter="--var",
                        suggestion="Use KEY=VALUE.",
                    )
                )
            key, _, value = item.partition("=")
            if not key.strip():
                raise UserDiagnosticError(
                    Diagnostic(
                        code="WM-INPUT-VAR-NAME",
                        message="Variable name cannot be empty.",
                        parameter="--var",
                        suggestion="Use KEY=VALUE with a non-empty KEY.",
                    )
                )
            if value.lower() in ("true", "yes", "1"):
                variables[key.strip()] = True
            elif value.lower() in ("false", "no", "0"):
                variables[key.strip()] = False
            else:
                variables[key.strip()] = value

    return variables


def _provenance_options(
    printer: CliPrinter,
    args: argparse.Namespace,
) -> ProvenanceOptions | None:
    """Build optional provenance settings from CLI arguments."""

    manifest_path = getattr(args, "provenance", None)
    record_dir = getattr(args, "record_run", None)
    replay_dir = getattr(args, "replay_run", None)
    if not any((manifest_path, record_dir, replay_dir)):
        return None
    if record_dir is not None:
        printer.warning(
            "Run recording stores full LLM requests, responses, tool results, "
            "variables, and imported content. Protect the bundle as sensitive data."
        )
    return ProvenanceOptions(
        manifest_path=manifest_path,
        record_dir=record_dir,
        replay_dir=replay_dir,
    )


def _render_user_diagnostic(
    printer: CliPrinter,
    error: UserDiagnosticError,
    *,
    json_output: bool,
) -> None:
    """Render one expected failure without a traceback."""

    if json_output:
        print(
            json.dumps(
                {"diagnostics": [error.diagnostic.to_dict()]},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return
    printer.error(
        f"[bold]{error.diagnostic.code}[/]: "
        f"{error.diagnostic.format_human()}"
    )


def _format_raw_output(result: CompositionResult, fmt: str) -> str:
    """Format the primary output for stdout or file.

    Always returns ONLY the prompt content (no issues):
    - ``markdown``: the composed prompt text
    - ``json``: full structured data (includes issues in JSON fields)
    """
    if fmt == "json":
        return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    return result.composed_prompt


def _resolve_output_format(
    result: CompositionResult,
    args: argparse.Namespace,
    printer: CliPrinter,
    settings: WeaveMarkSettings | None = None,
) -> str:
    """Resolve CLI output format with CLI flags taking precedence over @compile."""

    settings = settings or builtin_weavemark_settings()
    spec_format = result.compile.get("format") if result.compile else None
    if spec_format:
        normalized_spec_format = normalize_compile_format(spec_format, settings)
        if normalized_spec_format is None:
            raise UserDiagnosticError(
                Diagnostic(
                    code="WM-COMPILE-FORMAT",
                    message=f"Unsupported @compile format {spec_format!r}.",
                    directive="@compile",
                    parameter="format",
                    suggestion=(
                        "Use one of: "
                        f"{supported_compile_formats_text(settings)}."
                    ),
                )
            )
        spec_format = normalized_spec_format

    cli_format = getattr(args, "format", None)
    if cli_format:
        normalized_cli_format = normalize_compile_format(cli_format, settings)
        if normalized_cli_format is None:
            raise UserDiagnosticError(
                Diagnostic(
                    code="WM-OUTPUT-FORMAT",
                    message=f"Unsupported output format {cli_format!r}.",
                    parameter="--format",
                    suggestion=(
                        "Use one of: "
                        f"{supported_compile_formats_text(settings)}."
                    ),
                )
            )
        if spec_format and normalized_cli_format != spec_format:
            warning = (
                f"CLI --format {normalized_cli_format} overrides @compile format: "
                f"{spec_format}."
            )
            result.warnings.append(warning)
            printer.warning(warning)
        return normalized_cli_format

    return str(spec_format or DEFAULT_COMPILE_FORMAT)


def _derive_primary_filename(spec_file: str | None, extension: str) -> str:
    """Pick the primary output filename when --output-dir is used.

    Strips the conventional ``.weavemark`` suffix from the spec stem
    (e.g. ``asset-deep-search.weavemark.md`` -> ``asset-deep-search.md``).
    Falls back to ``output.<extension>`` when reading from stdin.
    """

    if not spec_file:
        return f"output.{extension}"
    stem = Path(spec_file).stem
    if stem.endswith(".weavemark"):
        stem = stem[: -len(".weavemark")]
    if not stem:
        return f"output.{extension}"
    return f"{stem}.{extension}"


def _resolve_output_layout(
    args: argparse.Namespace,
    base_dir: Path,
    primary_extension: str,
) -> tuple[Path | None, Path]:
    """Resolve where the primary file (if any) and emitted artifact files go.

    Returns ``(primary_output, emit_root)``:

    * ``--output FILE`` mode: primary is ``FILE``; emit root is ``FILE.parent``.
    * ``--output-dir DIR`` mode: primary is ``DIR/<derived-name>.<ext>`` and
      emit root is ``DIR``.
    * Neither set: primary is ``None`` (stdout) and emit root is ``base_dir``.
    """

    if args.output_dir is not None:
        root = args.output_dir
        primary = root / _derive_primary_filename(args.spec_file, primary_extension)
        return primary, root
    if args.output is not None:
        return args.output, args.output.parent
    return None, base_dir


def _resolve_emit_targets(
    result: CompositionResult,
    emit_root: Path,
    primary_output: Path | None,
) -> dict[Path, str]:
    """Resolve ``@emit`` / role-tagged ``@prompt`` file targets relative to ``emit_root``."""

    if not result.emits:
        return {}

    root = emit_root.resolve()
    primary_resolved = primary_output.resolve() if primary_output else None
    targets: dict[Path, str] = {}

    for file_name, content in result.emits.items():
        emit_path = Path(file_name)
        if emit_path.is_absolute():
            raise ValueError(f"@emit file path must be relative: {file_name}")
        target = (root / emit_path).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError(
                f"@emit file path escapes the output directory: {file_name}"
            ) from exc
        if primary_resolved is not None and target == primary_resolved:
            raise ValueError(
                f"@emit target cannot be the same as the primary output: {file_name}"
            )
        if target in targets:
            raise ValueError(
                f"Multiple @emit targets resolve to the same file: {file_name}"
            )
        targets[target] = content

    return targets


def _write_primary_file(
    primary_output: Path,
    content: str,
    printer: CliPrinter,
    *,
    show_summary: bool = True,
    protection: ProtectionContext | None = None,
) -> bool:
    """Write the primary composed prompt unless ``content`` is whitespace-only.

    Returns ``True`` when the file was written. When the content is empty or
    contains only whitespace, no file is written and a warning is printed,
    because the user asked for a primary output but the spec did not produce one
    (it likely only declared ``@emit`` / role-tagged ``@prompt`` blocks).
    """

    if content.strip():
        if protection is not None:
            primary_output = protection.authorize_write(
                primary_output,
                reason="Writing the primary compiled or executed output",
            )
        primary_output.parent.mkdir(parents=True, exist_ok=True)
        primary_output.write_text(content, encoding="utf-8")
        if show_summary:
            printer.file_written(primary_output)
        return True

    printer.warning(
        f"Primary output is empty; not writing {primary_output}. "
        "If the spec only declares @emit / role-tagged @prompt artifacts, this is expected."
    )
    return False


def _write_emit_targets(
    targets: dict[Path, str],
    printer: CliPrinter,
    *,
    show_summary: bool = True,
    protection: ProtectionContext | None = None,
) -> None:
    """Write previously resolved ``@emit`` files."""

    for path, content in targets.items():
        if protection is not None:
            path = protection.authorize_write(
                path,
                reason="Writing an @emit or role-tagged @prompt artifact",
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        if show_summary:
            printer.file_written(path)


def _source_path_from_args(args: argparse.Namespace) -> Path | None:
    spec_file = getattr(args, "spec_file", None)
    return Path(spec_file).resolve() if spec_file else None


def _run_compiled_implementation(
    printer: CliPrinter,
    compiled_output: str,
    source_path: Path | None,
    settings: WeaveMarkSettings,
    args: argparse.Namespace,
    protection: ProtectionContext | None = None,
) -> int:
    """Run the configured implementation profile for a compiled prompt."""

    if not compiled_output.strip():
        printer.error("Cannot implement an empty compiled output.")
        return 1

    request = ImplementationRequest(
        compiled_spec_text=compiled_output,
        source_path=source_path,
        settings=settings.implementation,
        invocation_dir=Path.cwd(),
        profile_name=getattr(args, "implementation_profile", None),
        implementation_name=getattr(args, "implementation_name", None),
        output_root=getattr(args, "implementation_output_root", None),
        dry_run=bool(getattr(args, "implementation_dry_run", False)),
        reuse_dir=bool(getattr(args, "implementation_reuse_dir", False)),
        model=getattr(args, "implementation_model", None),
        extra_instructions=tuple(
            getattr(args, "implementation_extra_instruction", None) or ()
        ),
        protection=protection,
    )
    return _execute_implementation_request(
        printer,
        request,
        show_summary=not getattr(args, "no_file_summary", False),
    )


def _execute_implementation_request(
    printer: CliPrinter,
    request: ImplementationRequest,
    *,
    show_summary: bool,
) -> int:
    try:
        result = run_implementation(request)
    except (ImplementationError, OSError) as exc:
        printer.error(str(exc))
        return 1

    if result.dry_run:
        print_dry_run(result)
        return 0

    if show_summary:
        printer.file_written(result.compiled_spec_snapshot)
        printer.file_written(result.agent_prompt)
        printer.file_written(result.manifest)
        printer.file_written(result.transcript)

    if result.exit_code:
        printer.error(
            f"Implementation profile {result.profile!r} exited with code "
            f"{result.exit_code}. Transcript: {result.transcript}"
        )
        return result.exit_code

    printer.done()
    return 0


def _show_result(
    printer: CliPrinter,
    result: CompositionResult,
    fmt: str,
    elapsed: float,
    verbose: bool = False,
) -> None:
    """Display the composition result using the printer."""
    if fmt == "json":
        printer.result_json(result.to_dict())
    else:
        # Markdown — always show the prompt
        printer.result_markdown(result.composed_prompt)
        if result.tools:
            printer.console.print()
            printer.console.print("[bold bright_blue]📦 Tools[/]")
            printer.console.print(
                json.dumps(result.tools, indent=2, ensure_ascii=False),
                highlight=False,
            )

    if verbose:
        printer.stats(
            {
                "Tool calls": result.tool_calls_made,
                "Diagnostics": len(result.diagnostics),
                "Output": f"{len(result.composed_prompt):,} chars",
            },
            elapsed=elapsed,
        )


def _show_composition_errors(
    printer: CliPrinter,
    result: CompositionResult,
    *,
    json_output: bool = False,
) -> None:
    """Render composition errors before returning a failing CLI exit code."""

    if json_output:
        print(
            json.dumps(
                {"diagnostics": result.diagnostics},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return
    for error in result.errors:
        printer.error(error)


async def _prompt_for_compile_ask(
    printer: CliPrinter,
    prompt: AskPrompt,
) -> str:
    """Collect one host answer for a compile-time ``@ask`` question."""

    details = [
        f"[bold bright_yellow]{prompt.question}[/bold bright_yellow]",
        "",
        f"[dim]Type:[/] {prompt.question_type}",
        f"[dim]Detail level:[/] {prompt.detail_level}",
    ]
    if prompt.scope:
        details.append(f"[dim]Scope:[/] {prompt.scope}")
    if prompt.reason:
        details.append(f"[dim]Why this matters:[/] {prompt.reason}")
    details.append(
        f"[dim]Round {prompt.round_index}, question {prompt.question_index}. "
        "Press Enter to submit or Ctrl+C to cancel.[/dim]"
    )
    printer.console.print()
    printer.console.print(
        Panel(
            "\n".join(details),
            title="@ask",
            border_style="yellow",
        )
    )
    answer = str(
        printer.console.input("[bold bright_cyan]Answer[/] [dim](Enter submits)[/]: ")
    ).strip()
    printer.console.print(
        "[bold green]✓ Answer received.[/] [dim]Continuing compilation…[/dim]"
    )
    return answer


def _confirm_protection_request(
    printer: CliPrinter,
    request: ProtectionRequest,
) -> bool:
    """Render one high-risk capability confirmation."""

    printer.console.print()
    printer.console.print(
        Panel(
            (
                f"[bold]Requested capability:[/] {escape(request.capability)}\n"
                f"[bold]Target:[/] [bright_cyan]{escape(request.subject)}[/]\n\n"
                f"[bold]Why requested:[/] {escape(request.reason)}\n\n"
                f"[bold yellow]Why this may be dangerous:[/] "
                f"{escape(request.danger)}\n\n"
                "[dim]WeaveMark remembers the decision for this exact item and "
                "content fingerprint under ~/.weavemark. Changed files require "
                "a new decision.[/]"
            ),
            title="⚠️  Potentially dangerous promplet capability",
            border_style="bold yellow",
            padding=(1, 2),
        )
    )
    return Confirm.ask(
        "[bold yellow]Allow and remember this exact item?[/]",
        default=False,
        console=printer.console,
    )


def _cli_protection_context(
    printer: CliPrinter,
    settings: WeaveMarkSettings,
    base_dir: Path,
    args: argparse.Namespace,
    *,
    interactive: bool,
) -> ProtectionContext:
    """Build one effective protection context for a CLI invocation."""

    return ProtectionContext.create(
        settings.protections,
        entrypoint_dir=base_dir,
        invocation_dir=Path.cwd(),
        library_roots=tuple(getattr(args, "library_dir", None) or ()),
        bypass=bool(getattr(args, "no_protections", False)),
        approval_handler=(
            (lambda request: _confirm_protection_request(printer, request))
            if interactive
            else None
        ),
    )


# ------------------------------------------------------------------
# Modes
# ------------------------------------------------------------------


async def run_batch(
    printer: CliPrinter,
    spec_text: str,
    variables: dict[str, Any],
    base_dir: Path,
    args: argparse.Namespace,
) -> int:
    """Run in batch mode — no interactivity."""
    missing_inputs = missing_user_inputs(spec_text, variables, base_dir)
    if missing_inputs:
        render_missing_inputs_error(
            printer,
            missing_inputs,
            mode="Batch mode",
        )
        return 1

    settings_result = load_weavemark_settings(base_dir)
    if args.implement and settings_result.errors:
        printer.error("Config loading failed:\n" + "\n".join(settings_result.errors))
        return 1
    settings = settings_result.settings
    protection = _cli_protection_context(
        printer,
        settings,
        base_dir,
        args,
        interactive=False,
    )
    provenance = _provenance_options(printer, args)
    effective_model = args.model or DEFAULT_MODEL
    config = WeaveMarkConfig(model=effective_model)
    controller = WeaveMarkController(config)

    if args.verbose:
        printer.header(
            {
                "Spec": args.spec_file or "stdin",
                "Model": effective_model,
                "Mode": "batch",
            }
        )
        printer.variables(variables)
        printer.status("Composing prompt…")

    result = await controller.compose(
        spec_text,
        variables,
        base_dir,
        on_event=printer.event,
        protection=protection,
        provenance=provenance,
        source_path=_source_path_from_args(args),
    )
    if result.errors:
        _show_composition_errors(
            printer,
            result,
            json_output=args.format == "json",
        )
        return 1
    output_format = _resolve_output_format(result, args, printer, settings)
    output = _format_raw_output(result, output_format)
    primary_output, emit_root = _resolve_output_layout(
        args,
        base_dir,
        extension_for_compile_format(output_format, settings),
    )
    try:
        emit_targets = _resolve_emit_targets(result, emit_root, primary_output)
    except ValueError as exc:
        printer.error(str(exc))
        return 1

    if (primary_output is None and not args.implement) or args.show_output:
        print(output, flush=True)
    if primary_output is not None:
        _write_primary_file(
            primary_output,
            output,
            printer,
            show_summary=not args.no_file_summary,
            protection=protection,
        )

    try:
        _write_emit_targets(
            emit_targets,
            printer,
            show_summary=not args.no_file_summary,
            protection=protection,
        )
    except OSError as exc:
        printer.error(f"Failed to write @emit output: {exc}")
        return 1

    if args.implement:
        return _run_compiled_implementation(
            printer,
            output,
            _source_path_from_args(args),
            settings,
            args,
            protection,
        )

    return 0


async def run_interactive(
    printer: CliPrinter,
    spec_text: str,
    variables: dict[str, Any],
    base_dir: Path,
    args: argparse.Namespace,
) -> int:
    """Run in interactive mode — compose, show result, allow follow-up."""
    prompted_variables = prompt_for_missing_inputs(
        printer,
        spec_text,
        variables,
        base_dir,
    )
    if prompted_variables is None:
        return 1
    variables = prompted_variables

    settings_result = load_weavemark_settings(base_dir)
    if args.implement and settings_result.errors:
        printer.error("Config loading failed:\n" + "\n".join(settings_result.errors))
        return 1
    settings = settings_result.settings
    protection = _cli_protection_context(
        printer,
        settings,
        base_dir,
        args,
        interactive=True,
    )
    provenance = _provenance_options(printer, args)
    effective_model = args.model or DEFAULT_MODEL
    config = WeaveMarkConfig(model=effective_model)
    controller = WeaveMarkController(config)

    printer.header({"Spec": args.spec_file or "stdin", "Model": effective_model})
    printer.variables(variables)
    printer.status("Composing prompt…")

    t0 = time.perf_counter()
    result = await controller.compose(
        spec_text,
        variables,
        base_dir,
        on_event=printer.event,
        ask_handler=lambda ask: _prompt_for_compile_ask(printer, ask),
        protection=protection,
        provenance=provenance,
        source_path=_source_path_from_args(args),
    )
    elapsed = time.perf_counter() - t0
    if result.errors:
        _show_composition_errors(
            printer,
            result,
            json_output=args.format == "json",
        )
        return 1
    output_format = _resolve_output_format(result, args, printer, settings)
    primary_output, emit_root = _resolve_output_layout(
        args,
        base_dir,
        extension_for_compile_format(output_format, settings),
    )
    try:
        emit_targets = _resolve_emit_targets(result, emit_root, primary_output)
    except ValueError as exc:
        printer.error(str(exc))
        return 1

    raw = _format_raw_output(result, output_format)
    if (primary_output is None and not args.implement) or args.show_output:
        _show_result(printer, result, output_format, elapsed, verbose=args.verbose)
    if primary_output is not None:
        _write_primary_file(
            primary_output,
            raw,
            printer,
            show_summary=not args.no_file_summary,
            protection=protection,
        )

    try:
        _write_emit_targets(
            emit_targets,
            printer,
            show_summary=not args.no_file_summary,
            protection=protection,
        )
    except OSError as exc:
        printer.error(f"Failed to write @emit output: {exc}")
        return 1

    if args.implement:
        return _run_compiled_implementation(
            printer,
            raw,
            _source_path_from_args(args),
            settings,
            args,
            protection,
        )

    if provenance is not None:
        printer.done()
        return 0

    # Interactive follow-up loop
    while True:
        printer.console.print()
        try:
            follow_up = printer.console.input(
                "[bold bright_blue]Enter feedback to refine, or press Enter to finish:[/] "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            printer.console.print()
            break

        if not follow_up:
            break

        spec_text_updated = f"{spec_text}\n\n# Additional Instructions\n\n{follow_up}"
        printer.status("Re-composing…")
        t0 = time.perf_counter()
        result = await controller.compose(
            spec_text_updated,
            variables,
            base_dir,
            on_event=printer.event,
            ask_handler=lambda ask: _prompt_for_compile_ask(printer, ask),
            protection=protection,
        )
        elapsed = time.perf_counter() - t0
        if result.errors:
            _show_composition_errors(
                printer,
                result,
                json_output=args.format == "json",
            )
            return 1
        output_format = _resolve_output_format(result, args, printer, settings)
        _show_result(printer, result, output_format, elapsed, verbose=args.verbose)

    printer.done()
    return 0


async def run_execute(
    printer: CliPrinter,
    spec_text: str,
    variables: dict[str, Any],
    base_dir: Path,
    args: argparse.Namespace,
) -> int:
    """Compile + execute: compose the spec, then run through an engine."""
    from ellements.execution import StepRecord

    from weavemark.engines import (
        RuntimeConfig,
        resolve_engine,
        resolve_runtime_engine_name,
    )

    # Load runtime config
    runtime_config = RuntimeConfig()
    if args.config:
        if not args.config.is_file():
            printer.error(f"Config file [bright_cyan]'{args.config}'[/] not found.")
            return 1
        try:
            if args.config.suffix in (".yaml", ".yml"):
                runtime_config = RuntimeConfig.from_yaml(args.config)
            else:
                runtime_config = RuntimeConfig.from_json(args.config)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise UserDiagnosticError(
                Diagnostic(
                    code="WM-RUNTIME-CONFIG",
                    message=str(exc),
                    source=str(args.config),
                    parameter="--config",
                    suggestion="Provide a valid runtime JSON or YAML object.",
                )
            ) from exc
    if args.model is not None:
        runtime_config.model = args.model
    elif runtime_config.model is None:
        runtime_config.model = DEFAULT_MODEL
    if args.image_model is not None:
        runtime_config.image_model = args.image_model
    args.model = runtime_config.model
    args.image_model = runtime_config.image_model

    settings = load_weavemark_settings(base_dir).settings
    protection = _cli_protection_context(
        printer,
        settings,
        base_dir,
        args,
        interactive=not args.batch_only,
    )
    provenance = _provenance_options(printer, args)
    runtime_config.protection = protection
    config = WeaveMarkConfig(model=runtime_config.model)
    controller = WeaveMarkController(config)

    # Merge config variables (CLI overrides config)
    variables = {**runtime_config.variables, **variables}

    missing_inputs = missing_user_inputs(spec_text, variables, base_dir)
    if missing_inputs:
        if args.batch_only:
            render_missing_inputs_error(
                printer,
                missing_inputs,
                mode="Run mode with --batch-only",
            )
            return 1
        prompted_variables = prompt_for_missing_inputs(
            printer,
            spec_text,
            variables,
            base_dir,
        )
        if prompted_variables is None:
            return 1
        variables = prompted_variables

    printer.header(
        {"Spec": args.spec_file or "stdin", "Model": args.model, "Mode": "run"}
    )
    printer.variables(variables)
    printer.status("Composing prompt…")

    t0 = time.perf_counter()
    logger.info(
        "compose start: spec=%s model=%s vars=%d",
        args.spec_file or "stdin",
        args.model,
        len(variables),
    )
    result = await controller.compose(
        spec_text,
        variables,
        base_dir,
        on_event=printer.event,
        ask_handler=(
            None
            if args.batch_only
            else lambda ask: _prompt_for_compile_ask(printer, ask)
        ),
        protection=protection,
        provenance=provenance,
        source_path=_source_path_from_args(args),
    )
    if result.errors:
        logger.error("compose failed: %s", "; ".join(result.errors))
        _show_composition_errors(
            printer,
            result,
            json_output=args.format == "json",
        )
        return 1
    output_format = _resolve_output_format(result, args, printer, settings)

    engine_name = resolve_runtime_engine_name(runtime_config, result)

    logger.info("execute start: engine=%s", engine_name)
    printer.status(f"Executing with engine: {engine_name}…")

    # Build live-step callback for --verbose
    step_counter = [0]
    step_icons = {
        "generate": "✏️ ",
        "evaluate": "🔍",
        "synthesize": "🧩",
        "critique": "🧐",
        "revise": "📝",
        "sample": "🎲",
        "vote": "🗳️ ",
        "judge": "⚖️ ",
        "call": "📡",
        "stop": "🛑",
    }

    def _on_step(step: StepRecord) -> None:
        step_counter[0] += 1
        elapsed_so_far = time.perf_counter() - t0
        base_name = step.name.split("_")[0]
        icon = step_icons.get(base_name, "▸ ")
        preview = step.response[:120].replace("\n", " ")
        if len(step.response) > 120:
            preview += "…"
        meta_parts = []
        if step.metadata.get("round") is not None:
            meta_parts.append(f"round {step.metadata['round']}")
        if step.metadata.get("reason"):
            meta_parts.append(step.metadata["reason"])
        if step.metadata.get("aggregation"):
            meta_parts.append(step.metadata["aggregation"])
        meta_str = f" ({', '.join(meta_parts)})" if meta_parts else ""
        printer.console.print(
            f"  {icon} [bold]Step {step_counter[0]}[/]: "
            f"[bright_cyan]{step.name}[/]{meta_str}  "
            f"[dim]{elapsed_so_far:.1f}s[/]"
        )
        if args.verbose:
            printer.console.print(f"     [dim]{preview}[/]")

    on_step = _on_step if args.verbose else None

    # Stream each produced artifact to disk the moment the engine emits it, so a
    # long multi-image run persists page-by-page (resilient + visible) instead of
    # only writing everything after the whole run finishes. Active in
    # --output-dir mode, where a stable artifact root is defined.
    streamed_stage_files: dict[str, list[str]] = {}
    on_artifact = None
    if args.output_dir is not None:
        from weavemark.packaging import persist_artifact_record

        _, stream_root = _resolve_output_layout(
            args,
            base_dir,
            extension_for_compile_format(output_format, settings),
        )

        def _on_artifact(record: dict[str, Any]) -> None:
            written = persist_artifact_record(record, stream_root, protection)
            if written is None:
                return
            stage = str(record.get("stage", "default"))
            streamed_stage_files.setdefault(stage, []).append(written)
            logger.info("streamed artifact: %s (stage=%s)", written, stage)
            if not args.no_file_summary:
                printer.file_written(stream_root / written)

        on_artifact = _on_artifact

    from weavemark.logging_setup import new_client

    engine = resolve_engine(
        engine_name,
        client=new_client(
            model=runtime_config.model,
            protection=protection,
            logging_settings=settings.logging,
        ),
        protection=protection,
    )
    try:
        from weavemark.engines import call_engine_execute

        exec_result = await call_engine_execute(
            engine, result, runtime_config, on_step=on_step, on_artifact=on_artifact
        )
    except Exception:
        logger.exception("execute failed: engine=%s", engine_name)
        raise
    finally:
        await _cleanup_litellm_logging_worker()
    elapsed = time.perf_counter() - t0
    logger.info(
        "execute done: engine=%s steps=%d artifacts=%d elapsed=%.1fs",
        engine_name,
        len(exec_result.steps),
        len(exec_result.metadata.get("artifacts", [])),
        elapsed,
    )
    exec_json = execution_result_to_dict(
        output=exec_result.output,
        steps=exec_result.steps,
        metadata=exec_result.metadata,
    )

    output = exec_result.output
    if output_format == "json":
        output = json.dumps(exec_json, indent=2, ensure_ascii=False)

    stats_before_artifacts = args.show_output and bool(
        args.output or args.output_dir or args.trace_output
    )

    # When the spec declares @package deliverables and only an output *directory*
    # was given, those packages ARE the deliverables — don't also dump the raw
    # terminal output (e.g. an image's base64) as a primary file. Likewise, when a
    # production point named its artifact with `@output file:`, that file is the
    # deliverable. An explicit --output FILE still writes the primary output.
    from weavemark.packaging import has_persistable_artifacts

    has_file_artifacts = has_persistable_artifacts(exec_result)
    suppress_primary = (
        bool(result.packages) or has_file_artifacts
    ) and args.output is None

    if args.output or args.output_dir:
        if args.show_output:
            if output_format == "json":
                printer.result_json(exec_json)
            else:
                printer.result_markdown(exec_result.output)
        primary_output, _ = _resolve_output_layout(
            args,
            base_dir,
            extension_for_compile_format(output_format, settings),
        )
        if primary_output is not None and not suppress_primary:
            _write_primary_file(
                primary_output,
                output,
                printer,
                show_summary=not args.no_file_summary,
                protection=protection,
            )
    elif output_format == "json":
        printer.result_json(exec_json)
    elif not suppress_primary:
        printer.result_markdown(exec_result.output)

    if stats_before_artifacts and args.verbose:
        _show_execution_stats(printer, engine_name, exec_result, elapsed)

    if args.trace_output:
        trace = render_execution_trace_markdown(
            spec=str(args.spec_file or "stdin"),
            model=args.model,
            engine=engine_name,
            output=exec_result.output,
            steps=exec_result.steps,
            metadata=exec_result.metadata,
        )
        try:
            trace_output = protection.authorize_write(
                args.trace_output,
                reason="Writing the requested execution trace",
            )
            trace_output.parent.mkdir(parents=True, exist_ok=True)
            trace_output.write_text(trace, encoding="utf-8")
        except OSError as exc:
            printer.error(f"Failed to write execution trace: {exc}")
            return 1
        if not args.no_file_summary:
            printer.file_written(trace_output)

    if args.verbose and not stats_before_artifacts:
        _show_execution_stats(printer, engine_name, exec_result, elapsed)

    if result.packages:
        await _run_packaging(
            printer,
            result,
            exec_result,
            variables,
            base_dir,
            args,
            output_format,
            settings,
            stage_files=streamed_stage_files or None,
            protection=protection,
        )
    elif (
        has_file_artifacts and args.output_dir is not None and not streamed_stage_files
    ):
        # No streaming sink ran (e.g. a single-image engine): persist at the end.
        _persist_artifacts(
            printer,
            exec_result,
            base_dir,
            args,
            output_format,
            settings,
            protection,
        )

    printer.done()
    return 0


def _persist_artifacts(
    printer: CliPrinter,
    exec_result: ExecutionResult,
    base_dir: Path,
    args: argparse.Namespace,
    output_format: str,
    settings: Any,
    protection: ProtectionContext,
) -> None:
    """Persist ``@output file:`` artifacts under the output dir (no packaging)."""

    from weavemark.packaging import persist_execution_artifacts

    _, emit_root = _resolve_output_layout(
        args,
        base_dir,
        extension_for_compile_format(output_format, settings),
    )
    stage_files = persist_execution_artifacts(
        exec_result,
        emit_root,
        protection,
    )
    if not args.no_file_summary:
        for files in stage_files.values():
            for rel in files:
                printer.file_written(emit_root / rel)


async def _run_packaging(
    printer: CliPrinter,
    result: CompositionResult,
    exec_result: ExecutionResult,
    variables: dict[str, Any],
    base_dir: Path,
    args: argparse.Namespace,
    output_format: str,
    settings: Any,
    stage_files: dict[str, list[str]] | None = None,
    protection: ProtectionContext | None = None,
) -> None:
    """Persist artifacts and run declared ``@package`` steps under the output dir.

    When *stage_files* is supplied the artifacts were already streamed to disk
    during execution, so packaging reuses that mapping instead of re-persisting.
    """

    from weavemark.packaging import run_packages

    _, emit_root = _resolve_output_layout(
        args,
        base_dir,
        extension_for_compile_format(output_format, settings),
    )
    printer.status("Packaging deliverables…")
    logger.info("packaging start: %d step(s) under %s", len(result.packages), emit_root)
    package_results = await run_packages(
        result.packages,
        variables,
        exec_result,
        base_dir=base_dir,
        root=emit_root,
        model=args.model,
        stage_files=stage_files,
        protection=protection or result.protection,
        logging_settings=settings.logging,
    )
    for package in package_results:
        if package.ok:
            logger.info("packaged %s (%s)", package.file.name, package.kind)
            if not args.no_file_summary:
                printer.file_written(package.file)
        else:
            logger.error("package %s failed: %s", package.file.name, package.note)
            printer.error(f"@package {package.file.name}: {package.note}")


def _show_execution_stats(
    printer: CliPrinter,
    engine_name: str,
    exec_result: ExecutionResult,
    elapsed: float,
) -> None:
    printer.stats(
        {
            "Engine": engine_name,
            "Steps": len(exec_result.steps),
            "Output": f"{len(exec_result.output):,} chars",
        },
        elapsed=elapsed,
    )


async def run_discover(args: argparse.Namespace) -> int:
    """Run the promplet discovery chat mode."""
    from weavemark.discovery.catalog import scan_directories
    from weavemark.discovery.chat_ui import DiscoveryChatUI
    from weavemark.discovery.config import load_config
    from weavemark.discovery.metadata import ensure_metadata
    from weavemark.discovery.tools import (
        DISCOVERY_TOOLS,
        SpecSelected,
        create_tool_executor,
    )
    from weavemark.engines.chat import ChatEngine
    from weavemark.promplet_library import library_sources

    ui = DiscoveryChatUI()

    # 1. Load config
    ui.show_step("⚙️ ", "Loading configuration…")
    env_config = load_config(
        project_dir=Path.cwd(),
        extra_library_dirs=getattr(args, "library_dir", None),
    )
    with library_sources(
        cwd=Path.cwd(),
        extra_library_dirs=getattr(args, "library_dir", None),
    ) as sources:
        dirs = [source.root for source in sources]
        entries = scan_directories(dirs)
    if env_config._global_path:
        ui.show_step("  ", f"[dim]Global:  {env_config._global_path}[/dim]")
    if env_config._project_path:
        ui.show_step("  ", f"[dim]Project: {env_config._project_path}[/dim]")

    # 2. Scan directories
    ui.show_step("📂", "Scanning promplet-library roots…")
    ui.show_scan_progress(entries, dirs)

    if not entries:
        ui.show_error(
            "No promplets found. Add promplets to ./promplets, "
            "~/.weavemark/promplets, or configure library_dirs."
        )
        return 1

    # 3. Compute/load metadata
    ui.show_step("🔍", "Loading metadata…")
    cached_count = [0]
    analyzed_count = [0]
    progress = ui.show_metadata_progress_start(len(entries))
    task_id: list[TaskID | None] = [None]

    def on_progress(current: int, total: int, title: str) -> None:
        analyzed_count[0] = current
        if task_id[0] is not None:
            progress.update(
                task_id[0],
                completed=current,
                description=f"[gold]Analyzing:[/gold] {title}",
            )

    with progress:
        task_id[0] = progress.add_task("Analyzing specs…", total=len(entries))
        metadata = await ensure_metadata(
            entries,
            model=args.model or DEFAULT_MODEL,
            on_progress=on_progress,
        )
        # Mark any cached (not analyzed) specs as completed in the bar
        assert task_id[0] is not None
        progress.update(task_id[0], completed=len(entries))

    cached_count[0] = len(entries) - analyzed_count[0]
    ui.show_cache_summary(cached_count[0], analyzed_count[0], len(entries))

    # 4. Load the discovery system prompt
    discovery_spec = (
        Path(__file__).parent.parent
        / "weavemark"
        / "specs"
        / "spec-discovery.weavemark.md"
    )
    # Try multiple locations
    for candidate in [
        Path.cwd() / "specs" / "spec-discovery.weavemark.md",
        Path(__file__).resolve().parent
        / ".."
        / ".."
        / "specs"
        / "spec-discovery.weavemark.md",
    ]:
        if candidate.is_file():
            discovery_spec = candidate
            break

    if discovery_spec.is_file():
        # Strip the @note and @tool blocks — use the text as system prompt
        raw = discovery_spec.read_text(encoding="utf-8")
        # Remove @note blocks and @tool blocks (they're handled by the tools system)
        lines = []
        in_note = False
        in_tool = False
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith("@note"):
                in_note = True
                continue
            if stripped.startswith("@tool"):
                in_tool = True
                continue
            if in_note and (
                not stripped or stripped.startswith("@") or not line.startswith(" ")
            ):
                in_note = False
            if in_tool and (
                stripped.startswith("@")
                and not stripped.startswith("@tool")
                and not line.startswith(" ")
            ):
                in_tool = False
            if in_note or in_tool:
                continue
            # Skip lines starting with "## Tools" header
            if stripped == "## Tools":
                in_tool = True
                continue
            lines.append(line)
        system_prompt = "\n".join(lines).strip()
    else:
        system_prompt = (
            "You are WeaveMark Discovery — a friendly assistant that helps users "
            "find the right promplet specification. Use search_catalog to find specs, "
            "read_spec to examine them, and select_spec when the user is ready."
        )

    # 5. Build the chat engine
    tool_executor = create_tool_executor(entries, metadata)

    ui.show_ready()
    ui.show_banner()

    engine = ChatEngine(
        system_prompt=system_prompt,
        tools=DISCOVERY_TOOLS,
        tool_executor=tool_executor,
        ui=ui,
        model=args.model or DEFAULT_MODEL,
    )

    # 6. Run the chat loop
    try:
        await engine.run()
    except SpecSelected as sel:
        # Hand off to TUI
        spec_path = Path(sel.spec_path)
        if spec_path.is_file():
            # Find the matching entry for a nice display
            matching = [e for e in entries if str(e.path) == sel.spec_path]
            if matching:
                meta = metadata.get(str(matching[0].path))
                ui.show_selected(matching[0], meta)
            try:
                from weavemark.tui.app import launch_tui_async

                await launch_tui_async(spec_path=spec_path)
            except ImportError:
                ui.show_error(
                    "Textual is required for the TUI. "
                    "Install with: pip install weavemark[ui]"
                )
                return 1
        else:
            ui.show_error(f"Promplet file not found: {spec_path}")
            return 1
    except KeyboardInterrupt:
        pass

    ui.show_goodbye()
    return 0


def run_implement_command(printer: CliPrinter, args: argparse.Namespace) -> int:
    """Run ``weavemark implement COMPILED_SPEC``."""

    compiled_spec = args.compiled_spec.expanduser().resolve()
    if not compiled_spec.is_file():
        printer.error(
            f"Compiled spec [bright_cyan]'{args.compiled_spec}'[/] not found."
        )
        return 1

    settings_result = load_weavemark_settings(compiled_spec.parent)
    if settings_result.errors:
        printer.error("Config loading failed:\n" + "\n".join(settings_result.errors))
        return 1
    configure_logging(settings=settings_result.settings.logging)
    log_cli_invocation(args, {}, settings_result.settings.logging)
    protection = _cli_protection_context(
        printer,
        settings_result.settings,
        compiled_spec.parent,
        args,
        interactive=True,
    )
    protection.authorize_read(
        compiled_spec,
        reason="Reading the compiled specification selected for implementation",
    )

    try:
        compiled_text = compiled_spec.read_text(encoding="utf-8")
    except OSError as exc:
        printer.error(f"Failed to read compiled spec: {exc}")
        return 1

    request = ImplementationRequest(
        compiled_spec_text=compiled_text,
        source_path=compiled_spec,
        settings=settings_result.settings.implementation,
        invocation_dir=Path.cwd(),
        profile_name=args.profile,
        implementation_name=args.name,
        output_root=args.output_root,
        dry_run=args.dry_run,
        reuse_dir=args.reuse_dir,
        model=args.model or DEFAULT_MODEL,
        extra_instructions=tuple(args.extra_instruction or ()),
        protection=protection,
    )
    return _execute_implementation_request(
        printer,
        request,
        show_summary=not args.no_file_summary,
    )


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------


def cli() -> None:
    """Main entry point for the weavemark command."""
    if len(sys.argv) > 1 and sys.argv[1] == "implement":
        implement_parser = create_implement_parser()
        implement_args = implement_parser.parse_args(sys.argv[2:])
        printer = CliPrinter(
            "WeaveMark",
            icon="🧩",
            verbose=implement_args.verbose,
            event_renderer=WeaveMarkEventRenderer(),
        )
        try:
            exit_code = run_implement_command(printer, implement_args)
        except ProtectionError as exc:
            printer.console.print(
                Panel(
                    exc.cli_message(),
                    title="🛑 Protection boundary",
                    border_style="bold red",
                    padding=(1, 2),
                )
            )
            exit_code = 2
        except KeyboardInterrupt:
            printer.console.print("\n[dim]Interrupted. 👋[/]")
            exit_code = 130
        sys.exit(exit_code)

    if len(sys.argv) > 1 and sys.argv[1] == "library":
        from weavemark.library_cli import (
            LIBRARY_MANAGEMENT_COMMANDS,
            create_library_parser,
            parse_library_target,
            run_library_command,
        )

        library_argv = sys.argv[2:]
        if not library_argv or library_argv[0] in LIBRARY_MANAGEMENT_COMMANDS:
            library_parser = create_library_parser()
            library_args = library_parser.parse_args(library_argv)
            try:
                exit_code = run_library_command(library_args)
            except KeyboardInterrupt:
                print("\nInterrupted.", file=sys.stderr)
                exit_code = 130
            sys.exit(exit_code)
        try:
            promplet_path, processor_args = parse_library_target(library_argv)
        except (FileNotFoundError, OSError, ValueError) as exc:
            print(f"weavemark library: {exc}", file=sys.stderr)
            sys.exit(1)
        sys.argv = [sys.argv[0], str(promplet_path), *processor_args]

    parser = create_parser()
    args = parser.parse_args()
    from weavemark.promplet_library import set_process_library_dirs

    set_process_library_dirs(getattr(args, "library_dir", None))

    printer = CliPrinter(
        "WeaveMark",
        icon="🧩",
        verbose=args.verbose,
        event_renderer=WeaveMarkEventRenderer(),
    )

    if args.output is not None and args.output_dir is not None:
        printer.error("--output and --output-dir are mutually exclusive.")
        sys.exit(2)
    if args.run and args.implement:
        printer.error("--run and --implement are mutually exclusive.")
        sys.exit(2)
    if args.ui and args.implement:
        printer.error("--ui and --implement are mutually exclusive.")
        sys.exit(2)
    if args.record_run is not None and args.replay_run is not None:
        printer.error("--record-run and --replay-run are mutually exclusive.")
        sys.exit(2)
    if args.replay_run is not None and (args.run or args.implement):
        printer.error(
            "--replay-run replays compilation only and cannot be combined with "
            "--run or --implement."
        )
        sys.exit(2)
    if (args.ui or args.scan or args.discover) and any(
        (args.provenance, args.record_run, args.replay_run)
    ):
        printer.error(
            "Provenance and run-recording options require a compilation mode, "
            "not --ui, --scan, or --discover."
        )
        sys.exit(2)

    # --env: print environment and exit
    if getattr(args, "env", False):
        from weavemark.discovery.config import load_config, print_env

        config = load_config(
            project_dir=Path.cwd(),
            extra_library_dirs=getattr(args, "library_dir", None),
        )
        printer.console.print(print_env(config))
        sys.exit(0)

    # --discover: launch promplet discovery chat
    if getattr(args, "discover", False):
        try:
            exit_code = asyncio.run(run_discover(args))
        except KeyboardInterrupt:
            printer.console.print("\n[dim]Interrupted. 👋[/]")
            exit_code = 130
        sys.exit(exit_code)

    # Read spec
    if args.stdin:
        spec_text = sys.stdin.read()
        base_dir = Path.cwd()
        spec_path = None
    elif args.spec_file:
        spec_path = Path(args.spec_file).resolve()
        if not spec_path.is_file():
            printer.error(
                f"Promplet file [bright_cyan]'{args.spec_file}'[/] not found."
            )
            sys.exit(1)
        try:
            spec_text = spec_path.read_text(encoding="utf-8")
        except OSError as exc:
            diagnostic = UserDiagnosticError(
                Diagnostic(
                    code="WM-INPUT-SPEC-READ",
                    message=f"Could not read promplet: {exc}",
                    source=str(spec_path),
                )
            )
            _render_user_diagnostic(
                printer,
                diagnostic,
                json_output=args.format == "json",
            )
            sys.exit(diagnostic.exit_code)
        base_dir = spec_path.parent
    else:
        parser.print_help()
        sys.exit(1)

    try:
        variables = _parse_variables(printer, args)
    except UserDiagnosticError as exc:
        _render_user_diagnostic(
            printer,
            exc,
            json_output=args.format == "json",
        )
        sys.exit(exc.exit_code)

    logging_settings = load_weavemark_settings(base_dir).settings.logging
    configure_logging(settings=logging_settings)
    log_cli_invocation(args, variables, logging_settings)

    # --scan: output promplet metadata as JSON and exit
    if getattr(args, "scan", False):
        import dataclasses as _dc

        from weavemark.tui.scanner import scan_spec

        surface_result = lower_weavemark_surface(spec_text)
        if surface_result.errors:
            printer.error(
                "Surface lowering failed:\n" + "\n".join(surface_result.errors)
            )
            sys.exit(1)
        settings_result = load_weavemark_settings(base_dir)
        if settings_result.errors:
            printer.error(
                "Config loading failed:\n" + "\n".join(settings_result.errors)
            )
            sys.exit(1)
        meta = scan_spec(surface_result.text, settings_result.settings)
        scan_data = {
            "title": meta.title,
            "description": meta.description,
            "inputs": [_dc.asdict(i) for i in meta.inputs],
            "compile": meta.compile,
            "execution": meta.execution,
            "prompt_names": meta.prompt_names,
            "tool_names": meta.tool_names,
            "binding_names": meta.binding_names,
            "module_name": meta.module_name,
            "use_modules": meta.use_modules,
            "include_modules": meta.include_modules,
            "macro_names": meta.macro_names,
            "refine_files": meta.refine_files,
            "embed_files": meta.embed_files,
            "emit_files": meta.emit_files,
            "surface": (
                surface_result.surface
                if surface_result.surface != "canonical"
                else None
            ),
        }
        print(json.dumps(scan_data, indent=2, ensure_ascii=False))
        sys.exit(0)

    # TUI mode
    if getattr(args, "ui", False):
        if spec_path is None:
            printer.error("--ui requires a promplet file (not stdin).")
            sys.exit(1)
        try:
            from weavemark.tui.app import launch_tui
        except ImportError:
            printer.error(
                "Textual is required for --ui mode. "
                "Install with: [bright_cyan]pip install promplet\\[ui][/]"
            )
            sys.exit(1)
        launch_tui(
            spec_path=spec_path,
            vars_path=args.vars_file,
            config_path=args.config,
            protection=_cli_protection_context(
                printer,
                load_weavemark_settings(base_dir).settings,
                base_dir,
                args,
                interactive=False,
            ),
        )
        sys.exit(0)

    try:
        if args.run:
            exit_code = asyncio.run(
                run_execute(printer, spec_text, variables, base_dir, args),
            )
        elif args.batch_only or args.stdin:
            exit_code = asyncio.run(
                run_batch(printer, spec_text, variables, base_dir, args),
            )
        else:
            exit_code = asyncio.run(
                run_interactive(printer, spec_text, variables, base_dir, args),
            )
    except ProtectionError as exc:
        printer.console.print()
        printer.console.print(
            Panel(
                exc.cli_message(),
                title="🛑 Protection boundary",
                border_style="bold red",
                padding=(1, 2),
            )
        )
        exit_code = 2
    except ReplayMismatchError as exc:
        diagnostic = UserDiagnosticError(
            Diagnostic(
                code="WM-REPLAY-MISMATCH",
                message=str(exc),
                parameter="--replay-run",
                suggestion="Use the original source, variables, model, and resources.",
            )
        )
        _render_user_diagnostic(
            printer,
            diagnostic,
            json_output=args.format == "json",
        )
        exit_code = diagnostic.exit_code
    except UserDiagnosticError as exc:
        _render_user_diagnostic(
            printer,
            exc,
            json_output=args.format == "json",
        )
        exit_code = exc.exit_code
    except KeyboardInterrupt:
        printer.console.print("\n[dim]Interrupted. 👋[/]")
        exit_code = 130

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
