#!/usr/bin/env python3
# ruff: noqa: E402
"""Compile the financial-independence goal planner and run its public lookup."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import json
import re
import sys
from collections.abc import Awaitable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "python-runtime-integrations" / "financial-independence-goal-plan"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "examples" / "_lib"))

from weavemark_example_progress import (
    normalize_generated_markdown,
    weavemark_verbose_event,
)

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.defaults import DEFAULT_MODEL

SPEC_PATH = (
    REPO_ROOT
    / "promplets"
    / "catalog"
    / "executable"
    / "financial-independence-goal-plan.weavemark.md"
)
COMPANION_PATH = (
    REPO_ROOT
    / "promplets"
    / "catalog"
    / "executable"
    / "companions"
    / "public_finance_reference.py"
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
    controller = WeaveMarkController(WeaveMarkConfig(model=DEFAULT_MODEL))
    result = await controller.compose(
        SPEC_PATH.read_text(encoding="utf-8"),
        variables=variables,
        base_dir=SPEC_PATH.parent,
        on_event=weavemark_verbose_event,
    )
    if result.errors:
        raise RuntimeError("\n".join(result.errors))

    _section("WeaveMark compiled executable goal-plan prompt")
    print(result.composed_prompt)

    _section("Weave execution plan emitted by WeaveMark")
    print(
        json.dumps(
            {"execution": result.execution, "bindings": result.bindings},
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )

    _section("Companion runtime public-reference lookup")
    companion = _load_companion()
    assumptions = await _maybe_await(
        companion.lookup_public_goal_assumptions(
            variables["goal"],
            "personal finance",
            variables["country"],
            variables["horizon"],
        )
    )
    print(json.dumps(assumptions, indent=2, ensure_ascii=False, default=str))

    composed_prompt = normalize_generated_markdown(result.composed_prompt)
    ready_prompt = normalize_generated_markdown(
        _inject_assumptions(composed_prompt, assumptions)
    )
    _section("Ready-to-paste final prompt")
    print(ready_prompt)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    compiled_prompt_path = OUTPUT_DIR / "compiled-prompt.md"
    compiled_plan_path = OUTPUT_DIR / "compiled-plan.json"
    assumptions_path = OUTPUT_DIR / "public-assumptions.json"
    output_path = OUTPUT_DIR / "execution-output.md"
    trace_path = OUTPUT_DIR / "execution-trace.md"

    compiled_prompt_path.write_text(composed_prompt, encoding="utf-8")
    compiled_plan_path.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    assumptions_path.write_text(
        json.dumps(assumptions, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    output_path.write_text(ready_prompt, encoding="utf-8")
    trace_path.write_text(
        _render_trace(
            composed_prompt=composed_prompt,
            execution_plan=result.execution,
            bindings=result.bindings,
            assumptions=assumptions,
            output=ready_prompt,
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


def _load_companion() -> Any:
    spec = importlib.util.spec_from_file_location(
        "public_finance_reference_companion",
        COMPANION_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load companion module from {COMPANION_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _maybe_await(value: Awaitable[Any] | Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _inject_assumptions(composed_prompt: str, assumptions: dict[str, Any]) -> str:
    rendered = json.dumps(assumptions, indent=2, ensure_ascii=False, default=str)
    if "@{public_assumptions}" in composed_prompt:
        return composed_prompt.replace("@{public_assumptions}", rendered)
    return "\n\n".join(
        [
            composed_prompt.rstrip(),
            "# Runtime public assumptions",
            _fence(rendered, "json"),
            (
                "Use these runtime assumptions as the `public_assumptions` context "
                "referenced above. Verify current limits, rates, tax rules, and "
                "benefits before acting."
            ),
        ]
    )


def _render_trace(
    *,
    composed_prompt: str,
    execution_plan: dict[str, Any],
    bindings: list[dict[str, Any]],
    assumptions: dict[str, Any],
    output: str,
) -> str:
    return "\n".join(
        [
            "# Financial Independence Goal-Plan Runtime Trace",
            "",
            f"- Spec: `{SPEC_PATH.relative_to(REPO_ROOT)}`",
            "- Reusable module: `promplets/stdlib/definitions/planning/goals.weavemark.md`",
            "- Companion runtime: `promplets/catalog/executable/companions/public_finance_reference.py`",
            "- Effect: `web_search read`",
            "",
            "## Compiled prompt",
            "",
            _fence(composed_prompt, "markdown"),
            "",
            "## Weave execution plan",
            "",
            _fence(
                json.dumps(
                    {"execution": execution_plan, "bindings": bindings},
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                ),
                "json",
            ),
            "",
            "## Runtime public assumptions",
            "",
            _fence(json.dumps(assumptions, indent=2, ensure_ascii=False), "json"),
            "",
            "## Ready-to-paste final prompt",
            "",
            _fence(output, "markdown"),
        ]
    )


def _fence(value: str, language: str = "") -> str:
    longest_run = max(
        (len(match.group(0)) for match in re.finditer(r"`+", value)),
        default=0,
    )
    marker = "`" * max(3, longest_run + 1)
    return f"{marker}{language}\n{value.rstrip()}\n{marker}"


if __name__ == "__main__":
    asyncio.run(main())
