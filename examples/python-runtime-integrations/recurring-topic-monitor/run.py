#!/usr/bin/env python3
# ruff: noqa: E402
"""Compile and run recurring news/events monitoring with Ellements web tools."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_ROOT = (
    REPO_ROOT / "examples" / "python-runtime-integrations" / "recurring-topic-monitor"
)
WORKSPACE_ROOT = REPO_ROOT.parent
ELLEMENTS_ROOT = WORKSPACE_ROOT / "ellements"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

for path in [
    REPO_ROOT / "src",
    REPO_ROOT / "examples" / "_lib",
    ELLEMENTS_ROOT / "ellements-core" / "src",
    ELLEMENTS_ROOT / "ellements-standard-tools" / "src",
]:
    sys.path.insert(0, str(path))

from ellements.core import LLMClient
from weavemark_example_progress import weavemark_verbose_event

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.defaults import DEFAULT_MODEL

logging.getLogger("promplet.controller").setLevel(logging.ERROR)

SPEC_PATH = (
    REPO_ROOT
    / "promplets"
    / "catalog"
    / "executable"
    / "recurring-topic-monitor.weavemark.md"
)
COMPANION_PATH = (
    REPO_ROOT
    / "promplets"
    / "catalog"
    / "executable"
    / "companions"
    / "recurring_topic_monitor.py"
)
INPUTS = [
    ("ai-news", EXAMPLE_ROOT / "inputs" / "ai-news.json"),
    ("child-events", EXAMPLE_ROOT / "inputs" / "child-events.json"),
]
OUTPUT_DIR = EXAMPLE_ROOT / "outputs"


def _section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


async def main() -> None:
    companion = _load_companion()
    controller = WeaveMarkController(WeaveMarkConfig(model=DEFAULT_MODEL))

    for scenario_name, vars_path in INPUTS:
        await _run_scenario(
            scenario_name=scenario_name,
            vars_path=vars_path,
            companion=companion,
            controller=controller,
        )

    _section("Artifacts written")
    for path in sorted(OUTPUT_DIR.glob("*/*")):
        if path.is_file():
            print(f"Wrote {path.relative_to(REPO_ROOT)}")


async def _run_scenario(
    *,
    scenario_name: str,
    vars_path: Path,
    companion: Any,
    controller: WeaveMarkController,
) -> None:
    raw_variables = json.loads(vars_path.read_text(encoding="utf-8"))
    variables = companion.compile_variables(raw_variables)

    _section(f"WeaveMark compiled recurring monitor — {scenario_name}")
    result = await controller.compose(
        SPEC_PATH.read_text(encoding="utf-8"),
        variables=variables,
        base_dir=SPEC_PATH.parent,
        on_event=weavemark_verbose_event,
    )
    if result.errors:
        raise RuntimeError("\n".join(result.errors))
    print(result.composed_prompt)

    _section(f"Ellements search/crawl execution — {scenario_name}")
    monitor_context = await companion.collect_monitor_context(variables)
    source_counts = monitor_context["source_counts"]
    print(
        "Search/crawl summary: "
        f"{source_counts['queries']} query families, "
        f"{source_counts['search_results']} search results, "
        f"{source_counts['first_level_crawled']} first-level crawls, "
        f"{source_counts['second_level_crawled']} second-level crawls."
    )

    model_label = DEFAULT_MODEL
    if os.environ.get("OPENAI_API_KEY"):
        _section(
            f"Synthesizing final {variables['monitor_mode']} digest with {DEFAULT_MODEL}"
        )
        response = await LLMClient(model=DEFAULT_MODEL).complete(
            _synthesis_prompt(result.composed_prompt, monitor_context),
            temperature=0.2,
        )
    else:
        _section("Synthesizing final digest without an LLM")
        model_label = f"{DEFAULT_MODEL} (not invoked; OPENAI_API_KEY unavailable)"
        response = _fallback_digest(variables, monitor_context)

    _section(f"Final response — {scenario_name}")
    print(response)

    scenario_output = OUTPUT_DIR / scenario_name
    scenario_output.mkdir(parents=True, exist_ok=True)
    (scenario_output / "compiled-prompt.md").write_text(
        result.composed_prompt,
        encoding="utf-8",
    )
    (scenario_output / "tool-results.json").write_text(
        json.dumps(monitor_context, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (scenario_output / "execution-output.md").write_text(response, encoding="utf-8")
    (scenario_output / "execution-trace.md").write_text(
        _render_trace(
            scenario_name=scenario_name,
            model_label=model_label,
            variables=variables,
            composed_prompt=result.composed_prompt,
            monitor_context=monitor_context,
            output=response,
        ),
        encoding="utf-8",
    )


def _load_companion() -> Any:
    spec = importlib.util.spec_from_file_location(
        "recurring_topic_monitor_companion",
        COMPANION_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load companion module from {COMPANION_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _synthesis_prompt(composed_prompt: str, monitor_context: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            composed_prompt,
            "# Companion runtime results",
            _fence(
                json.dumps(monitor_context, indent=2, ensure_ascii=False, default=str),
                "json",
            ),
            (
                "Write the final recurring monitor digest now. Use the companion "
                "runtime results as the concrete search and crawl evidence. Cite "
                "URLs when making source-grounded claims. Explain any search or "
                "crawl gaps plainly."
            ),
        ]
    )


def _fallback_digest(
    variables: dict[str, Any],
    monitor_context: dict[str, Any],
) -> str:
    source_counts = monitor_context["source_counts"]
    return "\n".join(
        [
            f"# Recurring {variables['monitor_mode']} monitor: {variables['topic']}",
            "",
            "OPENAI_API_KEY was not available, so the companion runtime collected "
            "search/crawl evidence but did not synthesize an LLM digest.",
            "",
            "## Evidence collected",
            "",
            f"- Query families: {source_counts['queries']}",
            f"- Search results: {source_counts['search_results']}",
            f"- First-level crawls: {source_counts['first_level_crawled']}",
            f"- Second-level crawls: {source_counts['second_level_crawled']}",
        ]
    )


def _render_trace(
    *,
    scenario_name: str,
    model_label: str,
    variables: dict[str, Any],
    composed_prompt: str,
    monitor_context: dict[str, Any],
    output: str,
) -> str:
    return "\n".join(
        [
            f"# Recurring Topic Monitor Trace — {scenario_name}",
            "",
            f"- Model: `{model_label}`",
            f"- Spec: `{SPEC_PATH.relative_to(REPO_ROOT)}`",
            "- Companion runtime: `examples/python-runtime-integrations/recurring-topic-monitor/run.py`",
            "- Tool providers:",
            "  - `ellements.standard_tools.web.search`",
            "  - `ellements.standard_tools.web.crawler`",
            "",
            "## Variables",
            "",
            _fence(json.dumps(variables, indent=2, ensure_ascii=False), "json"),
            "",
            "## Compiled prompt",
            "",
            _fence(composed_prompt, "markdown"),
            "",
            "## Companion runtime results",
            "",
            _fence(
                json.dumps(monitor_context, indent=2, ensure_ascii=False, default=str),
                "json",
            ),
            "",
            "## Final output",
            "",
            output,
        ]
    )


def _fence(text: str, language: str) -> str:
    return f"```{language}\n{text}\n```"


if __name__ == "__main__":
    asyncio.run(main())
