#!/usr/bin/env python3
# ruff: noqa: E402
"""Benchmark WeaveMark strategies against LLM benchmarks.

Composes one or more WeaveMark files (with @execute directives), then evaluates
each strategy against standard benchmarks (GSM8K, MMLU, etc.) via
lm-evaluation-harness.  Outputs a beautiful comparison table.

Usage:
    python examples/benchmark-runners/strategy-comparison/runner.py \\
        --specs promplets/catalog/executable/self-consistency-solver.weavemark.md \\
               promplets/catalog/executable/tree-of-thought-solver.weavemark.md \\
        --tasks gsm8k \\
        --limit 20 \\
        --model gpt-5.5

Requirements:
    pip install "weavemark[benchmarking]"
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
import warnings
from contextlib import suppress
from pathlib import Path
from typing import Any

# Suppress litellm's "coroutine was never awaited" noise from its
# async logging worker when we run strategies in fresh event loops.
warnings.filterwarnings("ignore", message="coroutine.*was never awaited")


def _cancel_pending(loop: asyncio.AbstractEventLoop) -> None:
    """Cancel all pending tasks on a loop to release their resources."""
    try:
        pending = asyncio.all_tasks(loop)
    except RuntimeError:
        return
    for task in pending:
        task.cancel()
    if pending:
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))


# ---------------------------------------------------------------------------
# Ensure the project is importable
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "examples" / "_lib"))

from weavemark_example_progress import weavemark_verbose_event

# ---------------------------------------------------------------------------
# Rich console (lazy import to give friendly error)
# ---------------------------------------------------------------------------


def _get_console():
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


CONSOLE = _get_console()


def _quiet_benchmark_libraries() -> None:
    """Keep third-party dataset/cache chatter out of example transcripts."""
    logging.getLogger("datasets").setLevel(logging.ERROR)
    logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

    with suppress(Exception):
        from datasets.utils import logging as datasets_logging

        datasets_logging.set_verbosity_error()

    with suppress(Exception):
        from huggingface_hub.utils import logging as hub_logging

        hub_logging.set_verbosity_error()


def print_banner():
    if CONSOLE:
        from rich.panel import Panel
        from rich.text import Text

        title = Text("⚡ WeaveMark Benchmark Runner", style="bold bright_yellow")
        sub = Text(
            "Evaluate prompting strategies against standard LLM benchmarks",
            style="dim",
        )
        CONSOLE.print(
            Panel(
                Text.assemble(title, "\n", sub),
                border_style="bright_blue",
                padding=(1, 3),
            )
        )
    else:
        print("=" * 60)
        print("  ⚡ WeaveMark Benchmark Runner")
        print("  Evaluate prompting strategies against LLM benchmarks")
        print("=" * 60)


def print_step(icon: str, msg: str, style: str = ""):
    if CONSOLE:
        CONSOLE.print(f"  {icon}  {msg}", style=style)
    else:
        print(f"  {icon}  {msg}")


def print_section(title: str):
    if CONSOLE:
        CONSOLE.print(f"\n[bold bright_cyan]▸ {title}[/]")
    else:
        print(f"\n▸ {title}")


# ---------------------------------------------------------------------------
# Compose a spec and extract strategy info
# ---------------------------------------------------------------------------


async def compose_spec(
    spec_path: Path,
    model: str,
    problem_placeholder: str = "__WEAVEMARK_BENCHMARK_PROBLEM__",
) -> dict[str, Any]:
    """Compose a WeaveMark file and extract strategy metadata.

    Returns a dict with:
      - name: human-friendly strategy name
      - strategy_type: engine name (e.g. "tree-of-thought")
      - prompts: dict of composed prompt templates
      - execution: raw @execute metadata
    """
    from weavemark.controller import WeaveMarkConfig, WeaveMarkController

    spec_text = spec_path.read_text()
    config = WeaveMarkConfig(model=model)
    controller = WeaveMarkController(config)

    # Compose with the placeholder intact so we can substitute per benchmark sample
    result = await controller.compose(
        spec_text,
        variables={"problem": problem_placeholder},
        base_dir=spec_path.parent,
        on_event=weavemark_verbose_event,
    )

    strategy_type = "single-call"
    if result.execution and result.execution.get("type"):
        strategy_type = result.execution["type"]

    name = spec_path.stem.replace(".weavemark", "").replace("-", " ").title()

    return {
        "name": name,
        "strategy_type": strategy_type,
        "prompts": (
            result.prompts if result.prompts else {"default": result.composed_prompt}
        ),
        "composed_prompt": result.composed_prompt,
        "execution": result.execution,
        "spec_path": str(spec_path),
    }


# ---------------------------------------------------------------------------
# WeaveMarkBenchmarkModel — spec-aware adapter
# ---------------------------------------------------------------------------


def create_benchmark_model(
    strategy_type: str,
    prompts: dict[str, str],
    execution_config: dict[str, Any],
    model: str,
    placeholder: str = "__WEAVEMARK_BENCHMARK_PROBLEM__",
    max_workers: int = 8,
):
    """Create a BenchmarkModel that uses composed WeaveMark prompts."""
    from ellements.core import LLMClient
    from lm_eval.api.model import LM

    model_name = model.split("/")[-1] if "/" in model else model

    # Resolve the strategy
    strategy = None
    strategy_config = dict(execution_config)

    if strategy_type != "single-call":
        from ellements.execution import (
            ReflectionStrategy,
            SelfConsistencyStrategy,
            SingleCallStrategy,
            TreeOfThoughtStrategy,
        )

        strategy_map = {
            "single-call": SingleCallStrategy,
            "self-consistency": SelfConsistencyStrategy,
            "tree-of-thought": TreeOfThoughtStrategy,
            "simplified-tree-of-thought": TreeOfThoughtStrategy,
            "reflection": ReflectionStrategy,
        }
        strategy_cls = strategy_map.get(strategy_type)
        if strategy_cls:
            strategy = strategy_cls()
            if strategy_type == "simplified-tree-of-thought":
                strategy_config.setdefault("mode", "simple")

    class WeaveMarkBenchmarkModel(LM):
        """LM adapter that fills prompt templates with benchmark inputs."""

        def __init__(self):
            super().__init__()
            # Use sync litellm.completion directly to avoid event-loop issues.
            # litellm's async LoggingWorker binds a Queue to the first event
            # loop it sees; creating new loops later causes RuntimeError.
            import litellm as _litellm

            self._litellm = _litellm

        def _sync_complete(self, prompt_text: str) -> str:
            """Sync LLM call via litellm.completion (no event loop needed)."""
            resp = self._litellm.completion(
                model=model_name,
                messages=[{"role": "user", "content": prompt_text}],
                timeout=120,  # 2 min per call
            )
            return resp.choices[0].message.content or ""

        def generate_until(self, requests: list) -> list[str]:
            total = len(requests)

            # Process a single request (async).
            async def _process_one_async(idx: int, req, sem: asyncio.Semaphore) -> str:
                async with sem:
                    context, gen_kwargs = req.args
                    stop_seqs = gen_kwargs.get("until", [])

                    filled = {}
                    for key, template in prompts.items():
                        filled[key] = template.replace(placeholder, context)

                    output = None
                    for attempt in range(5):
                        try:
                            if strategy is not None:
                                result = await asyncio.wait_for(
                                    strategy.execute(
                                        prompts=filled,
                                        client=LLMClient(model=model_name),
                                        config=strategy_config,
                                    ),
                                    timeout=300,
                                )
                                output = result.output
                            else:
                                prompt_text = filled.get("default", context)
                                output = self._sync_complete(prompt_text)
                            break
                        except Exception as e:
                            if attempt < 4:
                                wait = [10, 30, 60, 120][attempt]
                                print_step(
                                    "  ⚠️",
                                    f"Retry {attempt + 1}/5 sample {idx + 1} in {wait}s: {type(e).__name__}",
                                    "yellow",
                                )
                                await asyncio.sleep(wait)
                            else:
                                print_step(
                                    "  ❌",
                                    f"Sample {idx + 1} failed after 5 attempts: {type(e).__name__}: {e}",
                                    "red",
                                )
                                output = ""

                    for stop in stop_seqs:
                        if stop in output:
                            output = output[: output.index(stop)]

                    return output

            if strategy is not None:
                # Run ALL strategy samples through a single event loop with
                # a semaphore for concurrency control.  This shares aiohttp
                # connections properly and avoids socket/FD exhaustion.
                effective_workers = min(max_workers, 2)
                max_workers_actual = min(effective_workers, total)

                async def _run_all_strategy():
                    sem = asyncio.Semaphore(max_workers_actual)
                    done_count_box = [0]  # mutable counter

                    async def _tracked(idx, req):
                        output = await _process_one_async(idx, req, sem)
                        done_count_box[0] += 1
                        answer_preview = (output or "").replace("\n", " ").strip()
                        if len(answer_preview) > 120:
                            answer_preview = answer_preview[:117] + "..."
                        print_step(
                            "  ✔",
                            f"[{done_count_box[0]}/{total}] Sample {idx + 1}: {answer_preview or '(empty)'}",
                            "dim",
                        )
                        return output

                    return list(
                        await asyncio.gather(
                            *[_tracked(i, req) for i, req in enumerate(requests)]
                        )
                    )

                loop = asyncio.new_event_loop()
                try:
                    results = loop.run_until_complete(_run_all_strategy())
                finally:
                    with suppress(Exception):
                        loop.run_until_complete(loop.shutdown_asyncgens())
                    with suppress(Exception):
                        _cancel_pending(loop)
                    loop.close()
                    import gc

                    gc.collect()

                return results

            # ── Non-strategy (single-call) path: use thread pool ──────
            def _process_one(idx: int, req) -> str:
                context, gen_kwargs = req.args
                stop_seqs = gen_kwargs.get("until", [])

                filled = {}
                for key, template in prompts.items():
                    filled[key] = template.replace(placeholder, context)

                prompt_text = filled.get("default", context)
                output = self._sync_complete(prompt_text)

                for stop in stop_seqs:
                    if stop in output:
                        output = output[: output.index(stop)]

                return output

            from concurrent.futures import ThreadPoolExecutor, as_completed

            max_workers_actual = min(max_workers, total)
            results: list[str | None] = [None] * total

            with ThreadPoolExecutor(max_workers=max_workers_actual) as pool:
                futures = {
                    pool.submit(_process_one, i, req): i
                    for i, req in enumerate(requests)
                }
                for done_count, future in enumerate(as_completed(futures), start=1):
                    idx = futures[future]
                    output = future.result()
                    results[idx] = output
                    # Show truncated answer for each completed sample
                    answer_preview = (output or "").replace("\n", " ").strip()
                    if len(answer_preview) > 120:
                        answer_preview = answer_preview[:117] + "..."
                    print_step(
                        "  ✔",
                        f"[{done_count}/{total}] Sample {idx + 1}: {answer_preview or '(empty)'}",
                        "dim",
                    )

            return results

        def loglikelihood(self, requests: list) -> list[tuple[float, bool]]:
            return [(0.0, False) for _ in requests]

        def loglikelihood_rolling(self, requests: list) -> list[float]:
            return [0.0 for _ in requests]

    return WeaveMarkBenchmarkModel()


# ---------------------------------------------------------------------------
# Main benchmark runner
# ---------------------------------------------------------------------------


def run_benchmarks(
    specs: list[dict[str, Any]],
    tasks: list[str],
    model: str,
    limit: int | None = None,
    num_fewshot: int | None = None,
    max_workers: int = 8,
) -> dict[str, dict[str, Any]]:
    """Run lm-eval benchmarks for each composed spec."""
    _quiet_benchmark_libraries()

    from lm_eval.evaluator import simple_evaluate
    from lm_eval.tasks import TaskManager

    _quiet_benchmark_libraries()

    all_results: dict[str, dict[str, Any]] = {}

    # Reuse a single TaskManager so datasets are loaded/cached once
    task_manager = TaskManager()

    for i, spec_info in enumerate(specs, 1):
        name = spec_info["name"]
        strategy_type = spec_info["strategy_type"]

        print_step(
            "🚀", f"[{i}/{len(specs)}] Running: {name} ({strategy_type})", "bold"
        )

        benchmark_model = create_benchmark_model(
            strategy_type=strategy_type,
            prompts=spec_info["prompts"],
            execution_config=spec_info.get("execution", {}),
            model=model,
            max_workers=max_workers,
        )

        t0 = time.perf_counter()
        results = simple_evaluate(
            model=benchmark_model,
            tasks=tasks,
            num_fewshot=num_fewshot,
            limit=limit,
            batch_size=1,
            task_manager=task_manager,
        )
        elapsed = time.perf_counter() - t0

        all_results[name] = results
        print_step("✅", f"Done in {elapsed:.1f}s", "green")

    return all_results


def print_results_table(
    all_results: dict[str, dict[str, Any]],
    tasks: list[str],
    model: str,
    limit: int | None,
):
    """Print a beautiful comparison table."""
    from ellements.benchmarking import BenchmarkComparison

    comparison = BenchmarkComparison(
        model=model,
        tasks=tasks,
        results=all_results,
    )

    if CONSOLE:
        from rich.table import Table

        scores = comparison._extract_scores()
        strategies = list(scores.keys())

        # Collect all metrics
        all_metrics: list[str] = []
        seen: set[str] = set()
        for strat_scores in scores.values():
            for k in strat_scores:
                if k not in seen:
                    all_metrics.append(k)
                    seen.add(k)

        if not all_metrics:
            CONSOLE.print("\n[dim]No benchmark results to display.[/]")
            return

        table = Table(
            title="\n⚡ Benchmark Results",
            caption=f"Model: {model} │ Tasks: {', '.join(tasks)}"
            + (f" │ Limit: {limit} samples" if limit else ""),
            show_header=True,
            header_style="bold bright_cyan",
            border_style="bright_blue",
            padding=(0, 1),
        )

        table.add_column("Metric", style="bold", min_width=20)
        for s in strategies:
            table.add_column(s, justify="right", min_width=12)

        for metric in all_metrics:
            vals = {s: scores[s].get(metric) for s in strategies}
            best_val = max((v for v in vals.values() if v is not None), default=None)

            row = [metric]
            for s in strategies:
                v = vals[s]
                if v is None:
                    row.append("—")
                elif v == best_val and len(strategies) > 1:
                    row.append(f"[bold bright_green]{v:.4f} ★[/]")
                else:
                    row.append(f"{v:.4f}")
            table.add_row(*row)

        CONSOLE.print(table)
    else:
        comparison.print_table()

    # Summary
    print()
    scores = comparison._extract_scores()
    for metric in list(list(scores.values())[0].keys())[:3]:
        best = comparison.best_strategy(metric)
        if best:
            print_step("🏆", f"Best on {metric}: {best}", "bold bright_yellow")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark WeaveMark strategies against standard LLM benchmarks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Compare all four strategies on GSM8K (20 samples)
  python examples/benchmark-runners/strategy-comparison/runner.py \\
    --specs promplets/stdlib/fragments/reasoning/chain-of-thought.weavemark.md \\
           promplets/catalog/executable/self-consistency-solver.weavemark.md \\
           promplets/catalog/executable/tree-of-thought-solver.weavemark.md \\
           promplets/catalog/executable/reflection-solver.weavemark.md \\
    --tasks gsm8k --limit 20

  # Full GSM8K benchmark
  python examples/benchmark-runners/strategy-comparison/runner.py \\
    --specs promplets/catalog/executable/self-consistency-solver.weavemark.md \\
    --tasks gsm8k
""",
    )

    parser.add_argument(
        "--specs",
        "-s",
        nargs="+",
        required=True,
        type=Path,
        help="WeaveMark files to benchmark (with @execute directives)",
    )
    parser.add_argument(
        "--tasks",
        "-t",
        nargs="+",
        required=True,
        help="Benchmark tasks (e.g., gsm8k, mmlu, hellaswag)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="gpt-5.5",
        help="Model to use (default: gpt-5.5)",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Limit samples per task (e.g., 20 for quick test). Default: full benchmark.",
    )
    parser.add_argument(
        "--num-fewshot",
        "-f",
        type=int,
        default=None,
        help="Number of few-shot examples (default: benchmark default)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Save results to JSON file",
    )
    parser.add_argument(
        "--parallel",
        "-p",
        type=int,
        default=8,
        help="Max parallel samples per strategy (default: 8). Set to 1 for sequential.",
    )

    return parser.parse_args()


async def _compose_all_specs(
    spec_paths: list[Path], model: str
) -> list[dict[str, Any]]:
    """Compose all specs (async — needs LLM calls)."""
    specs: list[dict[str, Any]] = []
    for spec_path in spec_paths:
        print_step("📄", f"Composing: {spec_path.name}")
        spec_info = await compose_spec(spec_path, model=model)
        specs.append(spec_info)
        print_step(
            "  ↳",
            f"{spec_info['name']}  •  strategy: {spec_info['strategy_type']}  "
            f"•  prompts: {list(spec_info['prompts'].keys())}",
            "dim",
        )
    return specs


def main():
    args = parse_args()

    print_banner()

    # Validate specs exist
    for spec_path in args.specs:
        if not spec_path.exists():
            print_step("❌", f"Spec not found: {spec_path}", "bold red")
            sys.exit(1)

    # ── Compose each spec (async phase) ───────────────────────────────
    print_section("Composing WeaveMark strategies")
    specs = asyncio.run(_compose_all_specs(args.specs, args.model))

    # Disable litellm's async LoggingWorker entirely for the benchmark phase.
    # It creates an asyncio.Queue bound to the composition event loop, which
    # is dead by now.  Each asyncio.run() in strategy execution would trigger
    # "Queue is bound to a different event loop" RuntimeError noise.
    # We don't need async logging during benchmarking.
    try:
        import litellm.litellm_core_utils.logging_worker as _lw

        _orig_start = _lw.LoggingWorker.start
        _lw.LoggingWorker.start = lambda self: None
        _lw.LoggingWorker.enqueue = lambda self, *a, **kw: None
        _lw.LoggingWorker.ensure_initialized_and_enqueue = lambda self, *a, **kw: None
        # Also reset the global singleton's stale queue
        _lw.GLOBAL_LOGGING_WORKER._queue = None
        _lw.GLOBAL_LOGGING_WORKER._worker_task = None
    except Exception:
        pass

    # ── Run benchmarks (sync phase — no outer event loop) ─────────────
    print_section(
        f"Running benchmarks: {', '.join(args.tasks)}"
        + (f" (limit: {args.limit} samples)" if args.limit else " (full)")
    )

    all_results = run_benchmarks(
        specs=specs,
        tasks=args.tasks,
        model=args.model,
        limit=args.limit,
        num_fewshot=args.num_fewshot,
        max_workers=args.parallel,
    )

    # ── Display results ───────────────────────────────────────────────
    print_section("Results")
    print_results_table(all_results, args.tasks, args.model, args.limit)

    # ── Export ─────────────────────────────────────────────────────────
    if args.output:
        from ellements.benchmarking import BenchmarkComparison

        comparison = BenchmarkComparison(
            model=args.model,
            tasks=args.tasks,
            results=all_results,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_json(str(args.output))
        print(f"  💾  Results saved to {args.output}")

    print()


if __name__ == "__main__":
    main()
