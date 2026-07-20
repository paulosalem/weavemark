#!/usr/bin/env python3
# ruff: noqa: E402
"""Interactive collaborative editing demo.

Demonstrates the Collaborative Editing strategy by drafting an
investment strategy with the user acting as editor.

Usage:
    # Interactive mode (opens $EDITOR for each round):
    python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py

    # AI-agent handoff mode (this agent writes each edit response file):
    python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py --agent-collaborator

    # Non-interactive smoke mode (auto-approves the first draft):
    python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py --non-interactive

    # Custom spec + vars:
    python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py \
        --spec promplets/catalog/executable/collaborative-writer.weavemark.md \
        --vars examples/interactive-ui-and-handoff-demos/collaborative-writer/inputs/vars.json

Requires: OPENAI_API_KEY set, WeaveMark installed (pip install -e '.[all,dev]')
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure the project is importable
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = (
    REPO_ROOT
    / "examples"
    / "interactive-ui-and-handoff-demos"
    / "collaborative-investment-strategy"
)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "examples" / "_lib"))

from ellements.execution import (
    FileEditCallback,
    StepRecord,
)
from weavemark_example_progress import (
    normalize_generated_markdown,
    weavemark_verbose_event,
)

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.engines.base import RuntimeConfig
from weavemark.engines.collaborative import (
    AgentHandoffEditCallback,
    CollaborativeEngine,
)
from weavemark.traces import execution_result_to_dict, render_execution_trace_markdown
from weavemark.variable_files import load_variables_file

# ── ANSI colours ─────────────────────────────────────────────────

BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RED = "\033[31m"
RESET = "\033[0m"
RULE = "═" * 72


def banner(title: str) -> None:
    print(f"\n{MAGENTA}{RULE}{RESET}")
    print(f"{BOLD}{MAGENTA}  {title}{RESET}")
    print(f"{MAGENTA}{RULE}{RESET}\n")


def step_label(step: StepRecord) -> None:
    source = step.metadata.get("source", "?")
    rnd = step.metadata.get("round", "-")
    colour = GREEN if source == "llm" else YELLOW
    icon = "🤖" if source == "llm" else "✏️"
    reason = step.metadata.get("reason", "")
    extra = f" ({reason})" if reason else ""
    print(f"{colour}{icon}  [{step.name}] round={rnd} source={source}{extra}{RESET}")


def on_step(step: StepRecord) -> None:
    """Pretty-print each step as it happens."""
    step_label(step)
    preview = step.response[:200] if step.response else "(empty)"
    if len(step.response) > 200:
        preview += f"… ({len(step.response)} chars total)"
    print(f"{DIM}    {preview}{RESET}\n")


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# ── CLI editing callback ─────────────────────────────────────────


class CLIEditCallback:
    """Interactive callback: prints content and lets user type edits inline.

    Simpler than FileEditCallback — no $EDITOR dependency.
    The user can:
      - Press Enter on empty input to approve (unchanged)
      - Type DONE to finish
      - Type ABORT to cancel
      - Type replacement text line-by-line (end with a blank line)
    """

    async def request_edit(self, content: str, context: str = "") -> str:
        print(f"\n{CYAN}{'─' * 60}{RESET}")
        print(f"{BOLD}{CYAN}  📝 YOUR TURN — {context}{RESET}")
        print(f"{CYAN}{'─' * 60}{RESET}")
        print(content)
        print(f"{CYAN}{'─' * 60}{RESET}")
        print(f"{DIM}Options:{RESET}")
        print(f"{DIM}  • Press Enter to approve this version as-is{RESET}")
        print(f"{DIM}  • Type 'DONE' to finish with the current version{RESET}")
        print(f"{DIM}  • Type 'ABORT' to cancel entirely{RESET}")
        print(f"{DIM}  • Type replacement text (end with an empty line){RESET}")
        print()

        lines = []
        first_line = input(f"{YELLOW}> {RESET}")

        if first_line.strip() == "":
            return content  # Approve unchanged
        if first_line.strip() == "ABORT":
            return ""  # Abort signal
        if first_line.strip() == "DONE":
            return content + "\nDONE"  # Done signal

        lines.append(first_line)
        print(f"{DIM}(Continue typing. Empty line to finish.){RESET}")
        while True:
            line = input(f"{YELLOW}> {RESET}")
            if line == "":
                break
            lines.append(line)

        return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────


async def run(
    spec_path: Path,
    vars_path: Path | None,
    output_dir: Path,
    interactive: bool,
    use_editor: bool,
    agent_collaborator: bool,
    agent_timeout_seconds: float,
    agent_poll_seconds: float,
) -> None:
    variables = load_variables_file(vars_path) if vars_path else {}
    config = RuntimeConfig(execution_variables=variables)

    # Compose the spec
    banner("COMPOSING SPEC")
    print(f"{DIM}  Spec:   {spec_path}{RESET}")
    print(f"{DIM}  Vars:   {vars_path or '(none)'}{RESET}")
    print()

    spec_text = spec_path.read_text(encoding="utf-8")
    controller = WeaveMarkController(WeaveMarkConfig())
    result = await controller.compose(
        spec_text,
        variables=variables,
        base_dir=spec_path.parent,
        on_event=weavemark_verbose_event,
    )
    print(f"{GREEN}  ✓ Composed successfully{RESET}")
    print(
        f"{DIM}    Engine:  {result.execution.get('type', 'collaborative') if result.execution else 'collaborative'}{RESET}"
    )
    print(
        f"{DIM}    Prompts: {list(result.prompts.keys()) if result.prompts else ['default']}{RESET}"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    compiled_path = output_dir / "compiled-prompt.md"
    print()

    # Choose callback
    if agent_collaborator:
        callback = AgentHandoffEditCallback(
            output_dir / "agent-turns",
            timeout_seconds=agent_timeout_seconds,
            poll_seconds=agent_poll_seconds,
            label=display_path(spec_path),
        )
        print(
            f"{YELLOW}  ▸ Agent collaborator mode: waiting for AI-authored edit files{RESET}"
        )
        print(f"{DIM}    Handoff dir: {output_dir / 'agent-turns'}{RESET}\n")
    elif not interactive:
        callback = None
        print(f"{YELLOW}  ▸ Non-interactive smoke mode: auto-approving drafts{RESET}\n")
    elif use_editor:
        callback = FileEditCallback()
        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano"
        print(f"{YELLOW}  ▸ Editor mode: will open {editor} for each round{RESET}\n")
    else:
        callback = CLIEditCallback()
        print(f"{YELLOW}  ▸ Interactive CLI mode: you'll edit inline{RESET}\n")

    if callback is not None:
        config.engine_config["edit_callback"] = callback

    # Execute
    banner("EXECUTING — Collaborative Editing")
    engine = CollaborativeEngine()
    exec_result = await engine.execute(result, config=config, on_step=on_step)
    composed_prompt = normalize_generated_markdown(result.composed_prompt)
    final_output = normalize_generated_markdown(exec_result.output)
    normalized_steps = [
        replace(
            step,
            response=normalize_generated_markdown(step.response),
        )
        for step in exec_result.steps
    ]
    if normalized_steps and normalized_steps[-1].response != final_output:
        raise RuntimeError(
            "Collaborative engine output does not match its final execution step."
        )
    execution_path = output_dir / "execution-output.md"
    steps_path = output_dir / "execution-steps.json"
    trace_path = output_dir / "execution-trace.md"

    # Show final output
    banner("FINAL OUTPUT")
    print(final_output)
    print()

    compiled_path.write_text(composed_prompt, encoding="utf-8")
    execution_path.write_text(final_output, encoding="utf-8")
    steps_path.write_text(
        json.dumps(
            execution_result_to_dict(
                output=final_output,
                steps=normalized_steps,
                metadata=exec_result.metadata,
            ),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    trace_path.write_text(
        render_execution_trace_markdown(
            spec=display_path(spec_path),
            model="gpt-5.5",
            engine="collaborative",
            output=final_output,
            steps=normalized_steps,
            metadata=exec_result.metadata,
        ),
        encoding="utf-8",
    )

    # Summary
    rounds = exec_result.metadata.get("rounds_completed", "?")
    max_rounds = exec_result.metadata.get("max_rounds", "?")
    total_steps = len(exec_result.steps)
    print(f"{GREEN}{RULE}{RESET}")
    print(f"{BOLD}{GREEN}  ✓ Collaborative editing complete!{RESET}")
    print(f"{DIM}    Rounds: {rounds}/{max_rounds}  |  Steps: {total_steps}{RESET}")
    print(f"{DIM}    Compiled prompt: {compiled_path}{RESET}")
    print(f"{DIM}    Saved:  {execution_path}{RESET}")
    print(f"{DIM}    Steps:  {steps_path}{RESET}")
    print(f"{DIM}    Trace:  {trace_path}{RESET}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collaborative editing demo — draft an investment strategy with LLM + human co-editing."
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=REPO_ROOT
        / "promplets"
        / "catalog"
        / "executable"
        / "collaborative-investment-strategy.weavemark.md",
        help="Path to the .weavemark.md file",
    )
    parser.add_argument(
        "--vars",
        type=Path,
        default=REPO_ROOT
        / "examples"
        / "interactive-ui-and-handoff-demos"
        / "collaborative-investment-strategy"
        / "inputs"
        / "vars.json",
        help="Path to the variables JSON/YAML file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=EXAMPLE_ROOT / "outputs",
        help="Directory where compiled prompt and execution output are saved",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Smoke mode: auto-approve drafts instead of asking for edits",
    )
    parser.add_argument(
        "--agent-collaborator",
        action="store_true",
        help=(
            "Ask the surrounding AI agent to provide each human/editor turn via "
            "request/response files under the output directory"
        ),
    )
    parser.add_argument(
        "--agent-timeout-seconds",
        type=float,
        default=900.0,
        help="Maximum time to wait for each agent-authored edit response",
    )
    parser.add_argument(
        "--agent-poll-seconds",
        type=float,
        default=1.0,
        help="Polling interval while waiting for an agent-authored edit response",
    )
    parser.add_argument(
        "--editor",
        action="store_true",
        help="Use $EDITOR for editing instead of inline CLI input",
    )

    args = parser.parse_args()

    if args.agent_collaborator and (args.non_interactive or args.editor):
        parser.error(
            "--agent-collaborator cannot be combined with --non-interactive or --editor"
        )

    if not os.environ.get("OPENAI_API_KEY"):
        print(f"{YELLOW}⚠  OPENAI_API_KEY not set. Export it first:{RESET}")
        print("   export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    asyncio.run(
        run(
            spec_path=args.spec,
            vars_path=args.vars,
            output_dir=args.output_dir,
            interactive=not args.non_interactive and not args.agent_collaborator,
            use_editor=args.editor,
            agent_collaborator=args.agent_collaborator,
            agent_timeout_seconds=args.agent_timeout_seconds,
            agent_poll_seconds=args.agent_poll_seconds,
        )
    )


if __name__ == "__main__":
    main()
