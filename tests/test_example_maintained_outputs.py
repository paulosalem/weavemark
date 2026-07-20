"""Focused contracts for maintained non-image examples and benchmark runners."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import pytest

from weavemark.compilation.macros import preprocess_weavemark
from weavemark.compilation.structural import try_apply_structural_helpers

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"


def _load_python_example(relative_path: str, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_benchmark_runner_rejects_likelihood_tasks_and_requests(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = _load_python_example(
        "examples/benchmark-runners/strategy-comparison/runner.py",
        "strategy_comparison_runner",
    )

    class GenerationTask:
        OUTPUT_TYPE = "generate_until"

    class LikelihoodTask:
        OUTPUT_TYPE = "loglikelihood"

    runner._validate_generation_only_tasks({"gsm8k": GenerationTask()})
    with pytest.raises(
        runner.UnsupportedBenchmarkTaskError,
        match="no results were produced",
    ):
        runner._validate_generation_only_tasks({"unsupported": LikelihoodTask()})
    for method in ("loglikelihood", "loglikelihood_rolling"):
        with pytest.raises(
            runner.UnsupportedBenchmarkRequestError,
            match="zero-valued placeholder scores will be returned",
        ):
            runner._reject_unsupported_request_method(method)

    fake_lm_eval = ModuleType("lm_eval")
    fake_api = ModuleType("lm_eval.api")
    fake_model = ModuleType("lm_eval.api.model")

    class FakeLM:
        def __init__(self) -> None:
            pass

    fake_model.LM = FakeLM
    monkeypatch.setitem(sys.modules, "lm_eval", fake_lm_eval)
    monkeypatch.setitem(sys.modules, "lm_eval.api", fake_api)
    monkeypatch.setitem(sys.modules, "lm_eval.api.model", fake_model)
    adapter = runner.create_benchmark_model(
        strategy_type="single-call",
        prompts={"default": "Solve this: __WEAVEMARK_BENCHMARK_PROBLEM__"},
        execution_config={},
        model="gpt-5.5",
    )
    with pytest.raises(runner.UnsupportedBenchmarkRequestError):
        adapter.loglikelihood([object()])
    with pytest.raises(runner.UnsupportedBenchmarkRequestError):
        adapter.loglikelihood_rolling([object()])

    args = runner.parse_args(["--specs", "example.md", "--tasks", "gsm8k"])
    assert args.parallel == 2
    with pytest.raises(SystemExit):
        runner.parse_args(
            [
                "--specs",
                "example.md",
                "--tasks",
                "gsm8k",
                "--parallel",
                "3",
            ]
        )
    capsys.readouterr()

    source = (
        EXAMPLES / "benchmark-runners/strategy-comparison/runner.py"
    ).read_text(encoding="utf-8")
    assert "mmlu" not in source.casefold()
    assert "hellaswag" not in source.casefold()
    assert "return [(0.0" not in source
    assert "return [0.0" not in source
    assert "generate_until" in source
    assert "intentional safety cap: 2" in source
    benchmark_script = (
        EXAMPLES / "benchmark-runners/strategy-comparison/run.sh"
    ).read_text(encoding="utf-8")
    assert "--parallel 2" in benchmark_script
    readme = (EXAMPLES / "README.md").read_text(encoding="utf-8")
    assert 'OUTPUT_TYPE = "generate_until"' in readme
    assert "`loglikelihood` or `loglikelihood_rolling` are rejected" in readme


def test_tree_of_thought_numeric_option_contract_matches_maintained_output() -> None:
    root = EXAMPLES / "batch-example-runs/execution-engines"
    variables = json.loads(
        (root / "inputs/tree-of-thought-solver-example.json").read_text(
            encoding="utf-8"
        )
    )
    problem = variables["problem"]
    compiled = (root / "outputs/tree-of-thought-solver/compiled-prompt.md").read_text(
        encoding="utf-8"
    )
    output = (root / "outputs/tree-of-thought-solver/execution-output.md").read_text(
        encoding="utf-8"
    )
    trace = (root / "outputs/tree-of-thought-solver/execution-trace.md").read_text(
        encoding="utf-8"
    )

    assert "1 = A" in problem
    assert "2 = B" in problem
    assert "3 = C" in problem
    assert "numeric option number (1, 2, or 3)" in problem
    assert f"Problem: {problem}" in compiled
    assert output.rstrip().endswith("ANSWER: 3")
    assert "They must choose between: (A)" not in compiled + trace


def test_adaptive_interview_duration_is_coherent() -> None:
    input_path = (
        EXAMPLES
        / "batch-example-runs/static-prompts/inputs/adaptive-interview-senior-backend.json"
    )
    variables = json.loads(input_path.read_text(encoding="utf-8"))
    assert "num_questions" not in variables

    source = (
        ROOT / "promplets/catalog/standalone/adaptive-interview.weavemark.md"
    ).read_text(encoding="utf-8")
    output = (
        EXAMPLES
        / "batch-example-runs/static-prompts/outputs/adaptive-interview/compiled-prompt.md"
    ).read_text(encoding="utf-8")
    expected_allocations = {
        "Opening and calibration": 5,
        "Architecture and problem decomposition": 25,
        "System design": 25,
        "Candidate questions and close": 5,
    }
    for section, minutes in expected_allocations.items():
        assert f"{section}: {minutes} minutes" in source
        assert f"{section}: {minutes} minutes" in output
    assert sum(expected_allocations.values()) == 60
    assert "exact 60-minute allocation" in source
    assert "exact 60-minute allocation" in output
    assert "Architecture & Problem Decomposition — 30 minutes" not in output
    assert "System Design — 30 minutes" not in output


def test_adaptive_interview_false_branch_still_allocates_60_minutes() -> None:
    path = ROOT / "promplets/catalog/standalone/adaptive-interview.weavemark.md"
    source = path.read_text(encoding="utf-8").replace(
        "@refine module:weavemark.std.reasoning.base_analyst mingle: true",
        "@include weavemark.std.reasoning.base_analyst",
    )
    variables = json.loads(
        (
            EXAMPLES
            / "batch-example-runs/static-prompts/inputs/"
            "adaptive-interview-senior-backend.json"
        ).read_text(encoding="utf-8")
    )
    variables["include_system_design"] = False
    variables["include_scorecard"] = False
    preprocessed = preprocess_weavemark(source, path.parent)

    def read_file(reference: str, directory: Path) -> tuple[str, Path]:
        resolved = (directory / reference).resolve()
        return resolved.read_text(encoding="utf-8"), resolved

    compiled = try_apply_structural_helpers(
        preprocessed.text,
        variables,
        path.parent,
        read_file,
        preprocessed.semantic_definitions,
    )

    assert preprocessed.errors == []
    assert compiled is not None
    assert compiled.errors == []
    allocations = {
        label: int(minutes)
        for label, minutes in re.findall(
            r"^- (Opening and calibration|Architecture and problem decomposition|"
            r"Applied architecture deep dive|Candidate questions and close): "
            r"(\d+) minutes$",
            compiled.composed_prompt,
            flags=re.MULTILINE,
        )
    }
    assert allocations == {
        "Opening and calibration": 5,
        "Architecture and problem decomposition": 25,
        "Applied architecture deep dive": 25,
        "Candidate questions and close": 5,
    }
    assert sum(allocations.values()) == 60
    assert "### Applied Architecture Deep Dive (25 min)" in compiled.composed_prompt
    assert "### System Design (25 min)" not in compiled.composed_prompt


def test_financial_goal_plan_uses_repository_relative_source_path() -> None:
    """Maintained public artifacts must not disclose a maintainer's filesystem."""

    path = (
        EXAMPLES
        / "python-runtime-integrations/financial-independence-goal-plan/"
        "outputs/compiled-plan.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["source_path"] == (
        "promplets/catalog/executable/"
        "financial-independence-goal-plan.weavemark.md"
    )
    serialized = json.dumps(payload)
    assert "/Users/" not in serialized
    assert "GoogleDrive-" not in serialized


def test_consulting_engagement_and_roadmap_timelines_are_distinct() -> None:
    source = (
        ROOT / "promplets/catalog/standalone/consulting-proposal.weavemark.md"
    ).read_text(encoding="utf-8")
    output = (
        EXAMPLES
        / "batch-example-runs/static-prompts/outputs/consulting-proposal/compiled-prompt.md"
    ).read_text(encoding="utf-8")

    assert "consulting engagement itself lasts **@{timeline}**" in source
    assert "implementation roadmap may extend beyond that" in source
    assert "consulting engagement lasts **6 months**" in output
    assert "implementation roadmap may extend beyond that engagement" in output
    assert "Phase 3 — Scale, 9–18 months" in output
    assert "within the 6-month engagement window" not in output
    assert "continues afterward" in output


def test_program_review_inputs_match_without_duplicate_article() -> None:
    terminal_input = json.loads(
        (
            EXAMPLES
            / "terminal-output-only/program-review-checklist/inputs/vars.json"
        ).read_text(encoding="utf-8")
    )
    saved_input = json.loads(
        (
            EXAMPLES
            / "saved-artifact-workflows/program-review-json/inputs/vars.json"
        ).read_text(encoding="utf-8")
    )
    assert terminal_input == saved_input
    assert terminal_input["project_context"] == (
        "FastAPI microservice handling payment processing"
    )

    artifact = json.loads(
        (
            EXAMPLES
            / "saved-artifact-workflows/program-review-json/outputs/compiled-prompt.json"
        ).read_text(encoding="utf-8")
    )
    assert "**FastAPI microservice handling payment processing**" in artifact[
        "composed_prompt"
    ]
    assert "**a FastAPI microservice handling payment processing**" not in artifact[
        "composed_prompt"
    ]
    assert artifact["warnings"] == []
    assert artifact["errors"] == []
    terminal_artifact = (
        EXAMPLES
        / "terminal-output-only/program-review-checklist/outputs/compiled-prompt.md"
    ).read_text(encoding="utf-8")
    assert "**FastAPI microservice handling payment processing**" in terminal_artifact
    assert "**a FastAPI microservice handling payment processing**" not in (
        terminal_artifact
    )


def test_recurring_child_fixture_has_a_visible_runner_block() -> None:
    runner = (
        EXAMPLES / "batch-example-runs/execution-engines/run.sh"
    ).read_text(encoding="utf-8")
    fixture = "inputs/recurring-topic-monitor-child-events.json"
    assert runner.count(fixture) == 1
    assert "Recurring topic monitor: child-events preset" in runner
    assert "outputs/recurring-topic-monitor-child-events/execution-output.md" in runner
    assert "outputs/recurring-topic-monitor-child-events/execution-trace.md" in runner


def test_contrastive_mining_example_is_self_contained_and_maintained() -> None:
    root = EXAMPLES / "executable-promplet-programs/contrastive-mining"
    required = (
        "run.sh",
        "inputs/vars.json",
        "outputs/compiled-prompt.md",
        "outputs/execution-output.md",
        "outputs/execution-trace.md",
    )
    for relative in required:
        assert (root / relative).is_file()

    runner = (root / "run.sh").read_text(encoding="utf-8")
    assert runner.count(
        "weavemark library builtin:catalog/executable/contrastive-mining"
    ) == 2
    assert "--model gpt-5.5" in runner
    assert "--run" in runner
    assert "--trace-output" in runner
    assert "usage()" not in runner
    assert "argparse" not in runner
    assert not list((root / "inputs/samples").glob("*.txt"))

    packaged_samples = (
        Path(__file__).resolve().parents[1]
        / "promplets/catalog/executable/samples/contrastive-mining"
    )
    for filename in (
        "corporate-memo-pro-office.txt",
        "employee-blog-pro-remote.txt",
    ):
        assert (packaged_samples / filename).is_file()

    output = (root / "outputs/execution-output.md").read_text(encoding="utf-8")
    trace = (root / "outputs/execution-trace.md").read_text(encoding="utf-8")
    assert "`DIFFERENCE`" in output
    assert "`SIMILARITY`" in output
    assert "@{" not in output
    assert "| Steps | 5 |" in trace
    assert '"rounds_used": 3' in trace
    assert len(re.findall(r"^### \d+\. critique_\d+$", trace, re.MULTILINE)) == 2
    assert len(re.findall(r"^### \d+\. revise_\d+$", trace, re.MULTILINE)) == 2


def test_functional_market_snapshot_artifacts_are_grounded_and_transparent() -> None:
    root = EXAMPLES / "saved-artifact-workflows/market-snapshot/outputs"
    output = (root / "execution-output.md").read_text(encoding="utf-8")
    trace = (root / "execution-trace.md").read_text(encoding="utf-8")
    dashboard = (root / "vale3-market-dashboard.html").read_text(encoding="utf-8")
    final_trace = trace.rsplit("## Final output", maxsplit=1)[-1]

    for unresolved in ("@{", "__WEAVEMARK", "example.com"):
        assert unresolved not in output
        assert unresolved not in final_trace
        assert unresolved not in dashboard
    assert "Unresolved functional value placeholder" not in trace
    assert "| Engine | `functional` |" in trace
    assert '"status": "executed"' in trace
    assert "| Steps | 3 |" in trace
    for name in (
        "asset_snapshot",
        "web_context",
        "finance_data",
        "web_search",
    ):
        assert name in trace
    assert "https://" in output
    assert "VALE3" in output
    assert re.search(
        r"(?:Current price[^\n]*BRL|BRL[^\n]*Current price)",
        output,
        re.IGNORECASE,
    )
    assert re.search(
        r"(?:Currency[^\n]*BRL|BRL[^\n]*Currency)",
        output,
        re.IGNORECASE,
    )
    assert dashboard.startswith("<!doctype html>")
    assert dashboard.rstrip().endswith("</html>")
    assert "VALE3 Market Learning Dashboard" in dashboard
    assert "Content-Security-Policy" in dashboard
    assert "@media print" in dashboard
    assert "overflow-wrap: anywhere" in dashboard
    assert "minmax(0, 1fr)" in dashboard
    for crawler_claim in ("web_crawl", "source_readings", "crawled source", "crawler"):
        assert crawler_claim not in (output + trace).lower()


def test_goal_plan_outputs_have_no_stale_warning_or_plan_only_artifact() -> None:
    from weavemark.engines.functional import _validated_plan

    root = (
        EXAMPLES
        / "python-runtime-integrations/financial-independence-goal-plan/outputs"
    )
    compiled = json.loads((root / "compiled-plan.json").read_text(encoding="utf-8"))
    output = (root / "execution-output.md").read_text(encoding="utf-8")
    trace = (root / "execution-trace.md").read_text(encoding="utf-8")

    assert compiled["warnings"] == []
    assert compiled["errors"] == []
    assert compiled["diagnostics"] == []
    for stale in (
        "Ready-to-paste final prompt",
        "host-runtime-required",
        '"status": "planned"',
        "The two @assert directives use parameter name `includes`",
    ):
        assert stale not in output
        assert stale not in trace
        assert stale not in json.dumps(compiled)
    assert output.startswith("## 1. Goal profile")
    assert "## 6. Failure modes and safeguards" in output
    assert "| Engine | `functional` |" in trace
    assert '"status": "executed"' in trace
    assert compiled["model_calls_made"] == 0
    nodes, levels, order = _validated_plan(compiled["execution"])
    assert order == ["public_assumptions"]
    assert levels == [["public_assumptions"]]
    assert nodes[0]["params"] == [
        {"name": "goal", "implicit": False, "mode": "text"},
        {"name": "domain", "implicit": False, "mode": "text"},
        {"name": "country", "implicit": False, "mode": "text"},
        {"name": "horizon", "implicit": False, "mode": "text"},
    ]
    assert nodes[0]["args"] == {
        "positional": [],
        "options": {
            "goal": "@{goal}",
            "domain": "personal finance",
            "country": "@{country}",
            "horizon": "@{horizon}",
        },
    }
    assert nodes[0]["effects"] == [{"name": "web_search", "mode": "read"}]


def test_readme_describes_both_helpers_and_configured_default_models() -> None:
    readme = (EXAMPLES / "README.md").read_text(encoding="utf-8")
    assert "_lib/example-env.sh" in readme
    assert "_lib/weavemark_example_progress.py" in readme
    assert "configured default" in readme
    assert "only shared helper" not in readme
    assert "see the exact model" not in readme
    assert "model named in the visible runner command" not in readme


def test_collaborative_markdown_and_json_final_artifacts_are_byte_identical() -> None:
    roots = sorted(
        (EXAMPLES / "interactive-ui-and-handoff-demos").glob(
            "collaborative-*/outputs"
        )
    )
    assert roots
    for root in roots:
        markdown = (root / "execution-output.md").read_text(encoding="utf-8")
        steps = json.loads(
            (root / "execution-steps.json").read_text(encoding="utf-8")
        )
        assert steps["output"] == markdown
        assert steps["steps"][-1]["response"] == markdown

    generator = (
        EXAMPLES
        / "interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py"
    ).read_text(encoding="utf-8")
    assert re.search(r"steps=normalized_steps", generator)


def test_recurring_monitor_artifact_matches_fresh_input_date() -> None:
    root = EXAMPLES / "saved-artifact-workflows/recurring-topic-monitor"
    variables = json.loads((root / "inputs/ai-news.json").read_text(encoding="utf-8"))
    output = (root / "outputs/ai-news/execution-output.md").read_text(encoding="utf-8")
    trace = (root / "outputs/ai-news/execution-trace.md").read_text(encoding="utf-8")
    run_date = variables["run_date"]

    assert f"**Run date:** {run_date}" in output
    assert run_date in trace
    assert "@{" not in output
    assert "example.com" not in output
    assert "https://" in output


def test_bebe_fusquinha_pt_page_5_and_html_artifacts_are_distinct() -> None:
    root = EXAMPLES / "saved-artifact-workflows/childrens-book-bebe-fusquinha/pt"
    variables = json.loads((root / "inputs/vars.json").read_text(encoding="utf-8"))
    page_files = {page: root / f"outputs/pages/page-{page}.png" for page in (5, 15)}
    actual_hashes = {
        "page_5_narration": sha256(
            variables["pages"]["5"]["text"].encode("utf-8")
        ).hexdigest(),
        "page_15_narration": sha256(
            variables["pages"]["15"]["text"].encode("utf-8")
        ).hexdigest(),
        "page_5_image": _binary_or_lfs_sha256(page_files[5]),
        "page_15_image": _binary_or_lfs_sha256(page_files[15]),
    }
    expected_hashes = {
        "page_5_narration": (
            "036aa7797b9842c1e71a1adf3ae82a8573b1acec7041b6187218ef504bb484f1"
        ),
        "page_15_narration": (
            "50b8d7309c2df878d1e1c3d5e3da29c9c3e6dedc57c05d1f0786e39cf7656f3e"
        ),
        "page_5_image": (
            "5e67ca6cc94d6b8268ed2086fa915ae4ee9bd98b497e7eb60276b6849f898b6a"
        ),
        "page_15_image": (
            "ee33d72d4a8b241f26c4f2f5d53fc4534063aa718e1e3663505267cc13452802"
        ),
    }

    assert actual_hashes == expected_hashes
    assert actual_hashes["page_5_narration"] != actual_hashes["page_15_narration"]
    assert actual_hashes["page_5_image"] != actual_hashes["page_15_image"]

    html = (root / "outputs/book.html").read_text(encoding="utf-8")
    image_sources = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', html)
    expected_pages = [f"pages/page-{page}.png" for page in range(1, 16)]

    assert image_sources == ["cover.png", *expected_pages]
    assert len(set(image_sources[1:])) == 15


def _binary_or_lfs_sha256(path: Path) -> str:
    """Hash hydrated content or return the object hash from an LFS pointer."""

    payload = path.read_bytes()
    if payload.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        match = re.search(rb"^oid sha256:([0-9a-f]{64})$", payload, re.MULTILINE)
        assert match is not None, path
        return match.group(1).decode("ascii")
    return sha256(payload).hexdigest()


def test_binary_or_lfs_sha256_accepts_pointer_checkout(tmp_path: Path) -> None:
    expected = "a" * 64
    pointer = tmp_path / "artifact.png"
    pointer.write_text(
        "version https://git-lfs.github.com/spec/v1\n"
        f"oid sha256:{expected}\n"
        "size 123\n",
        encoding="ascii",
    )

    assert _binary_or_lfs_sha256(pointer) == expected
