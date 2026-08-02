"""Contracts for curated examples and retained runtime studies."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from hashlib import sha256
from pathlib import Path
from types import ModuleType

import pytest

from weavemark.cli_inputs import missing_user_inputs
from weavemark.variable_files import load_variables_file

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "examples"
RUNTIME_STUDIES = ROOT / "studies" / "runtime-studies"


def test_public_example_inventory_is_curated() -> None:
    projects = {
        str(project.relative_to(EXAMPLES))
        for category in EXAMPLES.iterdir()
        if category.is_dir() and category.name != "_lib"
        for project in category.iterdir()
        if project.is_dir()
    }
    assert projects == {
        "interactive-ui-and-handoff-demos/collaborative-writer",
        "python-runtime-integrations/financial-independence-goal-plan",
        "saved-artifact-workflows/arcana",
        "saved-artifact-workflows/childrens-book-bebe-fusquinha",
        "saved-artifact-workflows/childrens-book-orion-en",
        "saved-artifact-workflows/comic-strip-en",
        "saved-artifact-workflows/market-snapshot",
        "saved-artifact-workflows/prompt-refactoring-pipeline",
        "saved-artifact-workflows/recurring-topic-monitor",
    }


def test_arcana_retains_compiled_spec_app_and_public_bundle() -> None:
    root = EXAMPLES / "saved-artifact-workflows/arcana"
    outputs = root / "outputs"

    for relative in (
        "README.md",
        "run.sh",
        "inputs/vars.json",
        "outputs/arcana-app-spec.md",
        "outputs/cards-artifacts.sha256",
        "outputs/cards-build.sha256",
        "outputs/deck-data.js",
        "outputs/index.html",
        "outputs/README.md",
        "outputs/assets/card-back.png",
        "outputs/assets/cards/prototype.png",
    ):
        assert (root / relative).is_file(), relative

    data_source = (outputs / "deck-data.js").read_text(encoding="utf-8")
    payload = json.loads(data_source.split("=", 1)[1].rsplit(";", 1)[0])
    cards = [payload["prototype_card"], *payload["cards"].values()]
    assert payload["card_count"] == 55
    assert len(cards) == 55
    assert sum(card["category"] == "major" for card in cards) == 15
    assert sum(card["category"] == "minor" for card in cards) == 40
    assert payload["ai_guide"]["reflection_depth"]["default"] == 3

    assert len(list((outputs / "assets/cards").glob("*.png"))) == 55
    specification = (outputs / "arcana-app-spec.md").read_text(encoding="utf-8")
    assert specification.startswith(
        "# Arcana — browser application implementation specification"
    )
    for obligation in (
        "Playwright MCP",
        "Reflection depth",
        "Card reflection",
        "media controller",
        "Use restored key",
        'autocomplete="current-password"',
    ):
        assert obligation in specification

    html = (outputs / "index.html").read_text(encoding="utf-8")
    for marker in (
        "Enter without the OpenAI guide?",
        "reflection-trigger",
        "question-preset",
        "ai-stage",
        "Close interpretation",
        "magic-orbit",
        "media-transport",
        "class DeckRepository",
        "class OpenAIClient",
        "class MediaController",
        "text-pending",
        "voice-pending",
        "card-turn",
        "reflection-depth",
        "Use restored key",
        "Restored key connected from protected browser storage",
        "A saved key was restored by your browser",
        'autocomplete:"current-password"',
    ):
        assert marker in html
    assert "Math.random(" not in html
    assert "Draw next" not in html
    assert "Reveal all" not in html
    assert "overflow-x:clip" in html
    assert "stage.contains(document.activeElement)" in html
    assert (
        ".position.ai-stage-owner.ai-stage-overlap "
        ".reflection-trigger{display:block"
    ) in html
    reflection_source = html.split("renderReflection(){", 1)[1].split(
        "refreshReflection(", 1
    )[0]
    assert "Optional OpenAI reflection" not in reflection_source
    assert "item.ai" not in reflection_source
    readme_text = " ".join(
        (outputs / "README.md").read_text(encoding="utf-8").split()
    )
    assert "does not reuse the previous runtime source" in readme_text

    public = ROOT / "outputs/implementations/arcana"
    assert (public / "index.html").is_file()
    assert (public / "deck-data.js").is_file()
    assert (public / "index.html").read_bytes() == (outputs / "index.html").read_bytes()
    public_images = [
        public / "assets/card-back.png",
        public / "assets/cards/prototype.png",
        *(public / f"assets/cards/card-{index}.png" for index in range(1, 55)),
    ]
    assert all(path.is_file() for path in public_images)
    assert all(path.stat().st_size < 500_000 for path in public_images)


def _load_python_file(relative_path: str, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_strategy_study_rejects_likelihood_tasks_and_requests(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = _load_python_file(
        "studies/runtime-studies/reasoning-strategies/strategy-comparison/runner.py",
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
        RUNTIME_STUDIES / "reasoning-strategies" / "strategy-comparison" / "runner.py"
    ).read_text(encoding="utf-8")
    assert "mmlu" not in source.casefold()
    assert "hellaswag" not in source.casefold()
    assert "return [(0.0" not in source
    assert "return [0.0" not in source
    assert "generate_until" in source
    assert "intentional safety cap: 2" in source


def test_tree_of_thought_study_matches_maintained_output() -> None:
    root = RUNTIME_STUDIES / "reasoning-strategies" / "execution-engines"
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
    assert f"Problem: {problem}" in compiled
    assert output.rstrip().endswith("ANSWER: 3")
    assert "They must choose between: (A)" not in compiled + trace


def test_financial_goal_plan_uses_repository_relative_source_path() -> None:
    path = (
        EXAMPLES / "python-runtime-integrations/financial-independence-goal-plan/"
        "outputs/compiled-plan.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["source_path"] == (
        "promplets/catalog/executable/financial-independence-goal-plan.weavemark.md"
    )
    serialized = json.dumps(payload)
    assert "/Users/" not in serialized
    assert "GoogleDrive-" not in serialized


def test_contrastive_mining_study_is_self_contained() -> None:
    root = RUNTIME_STUDIES / "contrastive-mining"
    for relative in (
        "run.sh",
        "inputs/vars.json",
        "outputs/compiled-prompt.md",
        "outputs/execution-output.md",
        "outputs/execution-trace.md",
        "promplets/contrastive-mining.weavemark.md",
    ):
        assert (root / relative).is_file()

    runner = (root / "run.sh").read_text(encoding="utf-8")
    assert (
        runner.count(
            "studies/runtime-studies/contrastive-mining/promplets/"
            "contrastive-mining.weavemark.md"
        )
        == 2
    )
    assert "--model gpt-5.5" in runner
    assert "--run" in runner
    assert "--trace-output" in runner

    samples = root / "promplets/samples/contrastive-mining"
    for filename in (
        "corporate-memo-pro-office.txt",
        "employee-blog-pro-remote.txt",
    ):
        assert (samples / filename).is_file()

    output = (root / "outputs/execution-output.md").read_text(encoding="utf-8")
    trace = (root / "outputs/execution-trace.md").read_text(encoding="utf-8")
    assert "`DIFFERENCE`" in output
    assert "`SIMILARITY`" in output
    assert "@{" not in output
    assert "| Steps | 5 |" in trace


def test_market_snapshot_artifacts_are_grounded_and_transparent() -> None:
    root = EXAMPLES / "saved-artifact-workflows/market-snapshot/outputs"
    output = (root / "execution-output.md").read_text(encoding="utf-8")
    trace = (root / "execution-trace.md").read_text(encoding="utf-8")
    dashboard = (root / "market-dashboard.html").read_text(encoding="utf-8")
    final_trace = trace.rsplit("## Final output", maxsplit=1)[-1]

    for unresolved in ("@{", "__WEAVEMARK", "example.com"):
        assert unresolved not in output
        assert unresolved not in final_trace
        assert unresolved not in dashboard
    assert "| Engine | `functional` |" in trace
    assert '"status": "executed"' in trace
    assert "| Steps | 3 |" in trace
    assert "https://" in output
    assert "VALE3" in output
    assert "WeaveMark provenance" in dashboard
    assert dashboard.startswith("<!doctype html>")
    assert dashboard.rstrip().endswith("</html>")
    assert "Content-Security-Policy" in dashboard


def test_goal_plan_outputs_match_the_functional_contract() -> None:
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
    assert output.startswith("## 1. Goal profile")
    assert "## 6. Failure modes and safeguards" in output
    assert "| Engine | `functional` |" in trace
    assert '"status": "executed"' in trace
    nodes, levels, order = _validated_plan(compiled["execution"])
    assert order == ["public_assumptions"]
    assert levels == [["public_assumptions"]]
    assert nodes[0]["effects"] == [{"name": "web_search", "mode": "read"}]


def test_curated_examples_readme_names_only_maintained_projects() -> None:
    readme = (EXAMPLES / "README.md").read_text(encoding="utf-8")
    for name in (
        "childrens-book-bebe-fusquinha",
        "childrens-book-orion-en",
        "comic-strip-en",
        "market-snapshot",
        "prompt-refactoring-pipeline",
        "recurring-topic-monitor",
        "financial-independence-goal-plan",
        "collaborative-writer",
    ):
        assert name in readme
    assert "terminal-output-only" not in readme
    assert "batch-example-runs" not in readme
    assert "_lib/example-env.sh" in readme
    assert "_lib/weavemark_example_progress.py" in readme
    assert "configured default" in readme


def test_collaborative_writer_is_self_contained_and_consistent() -> None:
    root = EXAMPLES / "interactive-ui-and-handoff-demos/collaborative-writer"
    markdown = (root / "outputs/execution-output.md").read_text(encoding="utf-8")
    steps = json.loads(
        (root / "outputs/execution-steps.json").read_text(encoding="utf-8")
    )
    assert steps["output"] == markdown
    assert steps["steps"][-1]["response"] == markdown

    runner = (root / "run.py").read_text(encoding="utf-8")
    handoff = (root / "run-agent-handoff.sh").read_text(encoding="utf-8")
    assert "collaborative-investment-strategy" not in runner + handoff
    assert "collaborative-writer.weavemark.md" in runner
    assert "steps=normalized_steps" in runner


def test_prompt_refactoring_example_is_focused_and_maintained() -> None:
    root = EXAMPLES / "saved-artifact-workflows/prompt-refactoring-pipeline"
    for relative in ("run.sh", "inputs/vars.yaml", "outputs/compiled-prompt.md"):
        assert (root / relative).is_file()
    runner = (root / "run.sh").read_text(encoding="utf-8")
    assert runner.count("prompt-refactoring-pipeline") >= 3
    assert "batch-example-runs" not in runner


@pytest.mark.parametrize(
    ("example", "spec", "defaults", "runtime_values", "expected_missing"),
    [
        (
            "saved-artifact-workflows/recurring-topic-monitor",
            "promplets/catalog/executable/recurring-topic-monitor.weavemark.md",
            "inputs/interactive-defaults.json",
            {"run_date": "2026-07-20"},
            ["topic"],
        ),
        (
            "saved-artifact-workflows/market-snapshot",
            "promplets/catalog/executable/market-snapshot.weavemark.md",
            "inputs/interactive-defaults.json",
            {},
            ["provider_ticker", "display_ticker", "company_name"],
        ),
        (
            "interactive-ui-and-handoff-demos/collaborative-writer",
            "promplets/catalog/executable/collaborative-writer.weavemark.md",
            "inputs/interactive-defaults.json",
            {},
            ["topic"],
        ),
        (
            "python-runtime-integrations/financial-independence-goal-plan",
            "promplets/catalog/executable/financial-independence-goal-plan.weavemark.md",
            "inputs/interactive-defaults.json",
            {},
            ["goal", "country", "horizon"],
        ),
        (
            "saved-artifact-workflows/prompt-refactoring-pipeline",
            "promplets/catalog/standalone/prompt-refactoring-pipeline.weavemark.md",
            "inputs/interactive-defaults.yaml",
            {"raw_prompt": "Write a useful answer."},
            ["revision_instruction"],
        ),
    ],
)
def test_personalized_runners_leave_only_concise_guided_inputs(
    example: str,
    spec: str,
    defaults: str,
    runtime_values: dict[str, object],
    expected_missing: list[str],
) -> None:
    example_root = EXAMPLES / example
    spec_path = ROOT / spec
    variables = load_variables_file(example_root / defaults)
    variables.update(runtime_values)

    missing = missing_user_inputs(
        spec_path.read_text(encoding="utf-8"),
        variables,
        spec_path.parent,
    )

    assert [item.name for item in missing] == expected_missing


@pytest.mark.parametrize(
    "example",
    [
        "saved-artifact-workflows/recurring-topic-monitor",
        "saved-artifact-workflows/market-snapshot",
        "interactive-ui-and-handoff-demos/collaborative-writer",
        "python-runtime-integrations/financial-independence-goal-plan",
        "saved-artifact-workflows/prompt-refactoring-pipeline",
    ],
)
def test_personalized_runners_use_guided_inputs_and_isolated_outputs(
    example: str,
) -> None:
    runner = EXAMPLES / example / "run-interactive.sh"
    source = runner.read_text(encoding="utf-8")

    assert runner.stat().st_mode & 0o111
    assert "--batch-only" not in source
    assert "outputs/interactive/$RUN_ID" in source
    assert ("--open" in source) is (
        example == "saved-artifact-workflows/market-snapshot"
    )
    if example in {
        "interactive-ui-and-handoff-demos/collaborative-writer",
        "python-runtime-integrations/financial-independence-goal-plan",
    }:
        assert "--guided-inputs" in source
    else:
        assert "weavemark " in source


def test_python_examples_reuse_weavemark_guided_input_collection() -> None:
    helper = (EXAMPLES / "_lib/weavemark_guided_inputs.py").read_text(encoding="utf-8")

    assert "from weavemark.cli_inputs import prompt_for_missing_inputs" in helper
    assert "prompt_for_missing_inputs(" in helper


def test_recurring_monitor_artifact_matches_fresh_input_date() -> None:
    root = EXAMPLES / "saved-artifact-workflows/recurring-topic-monitor"
    variables = json.loads((root / "inputs/ai-news.json").read_text(encoding="utf-8"))
    output = (root / "outputs/ai-news/execution-output.md").read_text(encoding="utf-8")
    trace = (root / "outputs/ai-news/execution-trace.md").read_text(encoding="utf-8")
    run_date = variables["run_date"]

    assert run_date in output
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
    assert actual_hashes == {
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

    html = (root / "outputs/book.html").read_text(encoding="utf-8")
    image_sources = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', html)
    expected_pages = [f"pages/page-{page}.png" for page in range(1, 16)]
    assert image_sources == ["cover.png", *expected_pages]


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
