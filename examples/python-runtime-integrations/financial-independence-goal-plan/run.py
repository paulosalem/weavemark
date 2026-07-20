#!/usr/bin/env python3
# ruff: noqa: E402
"""Compile and run the financial-independence goal planner integration."""

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "python-runtime-integrations" / "financial-independence-goal-plan"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "examples" / "_lib"))

from ellements.core import LLMClient
from weavemark_example_progress import (
    normalize_generated_markdown,
    weavemark_verbose_event,
)

from weavemark.api import CompileOptions, execute_file
from weavemark.defaults import DEFAULT_MODEL
from weavemark.engines import RuntimeConfig
from weavemark.protection import ProtectionContext, ProtectionSettings
from weavemark.traces import render_execution_trace_markdown

SPEC_PATH = (
    REPO_ROOT
    / "promplets"
    / "catalog"
    / "executable"
    / "financial-independence-goal-plan.weavemark.md"
)
VARS_PATH = EXAMPLE_ROOT / "inputs" / "vars.json"
OUTPUT_DIR = EXAMPLE_ROOT / "outputs"


def _section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


async def main() -> None:
    variables = json.loads(VARS_PATH.read_text(encoding="utf-8"))
    client = LLMClient(model=DEFAULT_MODEL)
    run = await execute_file(
        SPEC_PATH,
        variables,
        options=CompileOptions(model=DEFAULT_MODEL),
        runtime_config=RuntimeConfig(model=DEFAULT_MODEL),
        client=client,
        on_event=weavemark_verbose_event,
        protection_context=ProtectionContext.create(
            ProtectionSettings(enabled=False),
            entrypoint_dir=SPEC_PATH.parent,
            invocation_dir=REPO_ROOT,
        ),
    )
    compiled = run.compiled
    if compiled.errors:
        raise RuntimeError("\n".join(compiled.errors))
    composed_prompt = normalize_generated_markdown(compiled.composed_prompt)
    assumptions = run.execution.metadata.get("results", {}).get(
        "public_assumptions"
    )
    if not isinstance(assumptions, dict):
        raise RuntimeError("Functional execution did not return public assumptions.")
    final_output = normalize_generated_markdown(run.output)

    _section("WeaveMark compiled executable goal-plan prompt")
    print(composed_prompt)

    _section("Compiled functional plan")
    print(
        json.dumps(
            {"execution": compiled.execution, "bindings": compiled.bindings},
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )

    _section("Bound public-reference result")
    print(json.dumps(assumptions, indent=2, ensure_ascii=False, default=str))

    _section("Final financial-independence plan")
    print(final_output)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    compiled_prompt_path = OUTPUT_DIR / "compiled-prompt.md"
    compiled_plan_path = OUTPUT_DIR / "compiled-plan.json"
    assumptions_path = OUTPUT_DIR / "public-assumptions.json"
    output_path = OUTPUT_DIR / "execution-output.md"
    trace_path = OUTPUT_DIR / "execution-trace.md"

    compiled_prompt_path.write_text(composed_prompt, encoding="utf-8")
    compiled_payload = compiled.to_dict()
    compiled_payload["source_path"] = str(SPEC_PATH.relative_to(REPO_ROOT))
    compiled_plan_path.write_text(
        json.dumps(compiled_payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    assumptions_path.write_text(
        json.dumps(assumptions, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    output_path.write_text(final_output, encoding="utf-8")
    trace_path.write_text(
        render_execution_trace_markdown(
            spec=str(SPEC_PATH.relative_to(REPO_ROOT)),
            model=DEFAULT_MODEL,
            engine=run.engine,
            output=final_output,
            steps=run.execution.steps,
            metadata=run.execution.metadata,
        ),
        encoding="utf-8",
    )

    _section("Artifacts written")
    for path in (
        compiled_prompt_path,
        compiled_plan_path,
        assumptions_path,
        output_path,
        trace_path,
    ):
        print(f"Wrote {path.relative_to(REPO_ROOT)}")


def _fence(value: str, language: str = "") -> str:
    longest_run = max(
        (len(match.group(0)) for match in re.finditer(r"`+", value)),
        default=0,
    )
    marker = "`" * max(3, longest_run + 1)
    return f"{marker}{language}\n{value.rstrip()}\n{marker}"


if __name__ == "__main__":
    asyncio.run(main())
