"""Regression checks for commands readers copy from the tutorial track."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _tutorial(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_batch_tutorial_commands_supply_all_documented_inputs() -> None:
    first = _tutorial("tutorial.html")
    assert "--var depth=committee" in first
    assert "--var include_watchlist=true" in first

    reuse = _tutorial("tutorial-reuse.html")
    for key in (
        "age",
        "annual_income",
        "annual_spending",
        "annual_investments",
        "emergency_fund",
        "real_return",
        "reduced_hours_income",
        "lower_pressure_income",
        "expected_monthly_passive_income",
        "confirmed_monthly_passive_income",
        "monthly_reinvestment_target",
        "monthly_tax_reserve",
        "principal_drawdown_preference",
    ):
        assert f'"{key}"' in reuse
    assert "--vars-file outputs/reuse/decision-vars.json" in reuse

    directives = _tutorial("tutorial-directives.html")
    for argument in (
        "--var add_section=true",
        "--var new_section_content=",
        "--var remove_section=false",
        "--var contraction_instruction=",
    ):
        assert argument in directives

    advanced = _tutorial("tutorial-advanced.html")
    assert "--var public_assumptions=" in advanced

    executable = _tutorial("tutorial-executable.html")
    for argument in (
        "--run",
        "--no-protections",
        "--trace-output",
        "--vars-file examples/saved-artifact-workflows/market-snapshot/inputs/vars.json",
    ):
        assert argument in executable


def test_illustrated_runners_write_inspectable_chain_json() -> None:
    runners = (
        "examples/saved-artifact-workflows/comic-strip-en/run.sh",
        "examples/saved-artifact-workflows/childrens-book-orion-en/run.sh",
        "examples/saved-artifact-workflows/childrens-book-bebe-fusquinha/en/run.sh",
        "examples/saved-artifact-workflows/childrens-book-bebe-fusquinha/pt/run.sh",
    )
    for relative in runners:
        script = (ROOT / relative).read_text(encoding="utf-8")
        assert "--format json" in script
        assert 'compiled-chain.json"' in script
        assert 'compiled-prompt.md"' not in script


def test_runtime_trace_fence_handles_nested_code_blocks() -> None:
    path = (
        ROOT
        / "examples"
        / "python-runtime-integrations"
        / "financial-independence-goal-plan"
        / "run.py"
    )
    spec = importlib.util.spec_from_file_location("financial_goal_plan_example", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    fenced = module._fence("before\n```json\n{}\n```\nafter", "markdown")

    assert fenced.startswith("````markdown\n")
    assert fenced.endswith("\n````")


def test_programming_tutorials_use_maintained_surfaces() -> None:
    reuse = _tutorial("tutorial-reuse.html")
    implement = _tutorial("tutorial-implement.html")
    refine = _tutorial("tutorial-refine.html")

    assert "passive-income-planning-dashboard" in reuse
    assert "passive-income-planning-dashboard" in implement
    assert "passive-income-android-app" not in reuse + implement
    assert "android_kotlin_compose" not in reuse
    assert "Python async task cancellation" in refine
    assert "Rust ownership" not in refine

    assert (
        ROOT
        / "outputs"
        / "examples"
        / "compiled-prompt-snapshots"
        / "passive-income-planning-dashboard"
        / "compiled-prompt.md"
    ).is_file()
    assert (
        ROOT
        / "examples"
        / "batch-example-runs"
        / "static-prompts"
        / "outputs"
        / "news-intelligence-board"
        / "compiled-prompt.md"
    ).is_file()


def test_weavemark_tutorial_snippets_do_not_fake_hash_comments() -> None:
    weavemark_tutorials = (
        "tutorial.html",
        "tutorial-advanced.html",
        "tutorial-games.html",
        "tutorial-products.html",
        "tutorial-refine.html",
        "tutorial-reuse.html",
    )
    for name in weavemark_tutorials:
        assert '<span class="syntax-comment">#' not in _tutorial(name)

    assert _tutorial("tutorial-illustrated.html").count(
        '<span class="syntax-comment">#'
    ) == 1
    assert _tutorial("tutorial-implement.html").count(
        '<span class="syntax-comment">#'
    ) == 3


def test_tutorial_track_includes_executable_market_report_lesson() -> None:
    tutorial_paths = sorted((ROOT / "docs").glob("tutorial*.html"))
    assert tutorial_paths

    for path in tutorial_paths:
        html = path.read_text(encoding="utf-8")
        assert '<a href="tutorial-executable.html"' in html, path
        assert "<span>8</span> Market report" in html, path
        assert "<span>9</span> Spec to app" in html, path
        assert "<span>10</span> Illustrated stories" in html, path

    executable = _tutorial("tutorial-executable.html")
    assert "market-snapshot.weavemark.md" in executable
    assert "market_data.py" in executable
    assert "@execute</span> functional" in executable
    assert "@bind</span> finance_data" in executable
    assert "@fetch_asset_snapshot</span>" in executable
    assert "@package</span>" in executable
    assert "information_dashboard_html" in executable
    assert "execution-output.md" in executable
    assert "execution-trace.md" in executable
    assert "vale3-market-dashboard.html" in executable


def test_tutorials_end_with_explicit_output_use_step() -> None:
    tutorial_paths = sorted((ROOT / "docs").glob("tutorial*.html"))
    assert tutorial_paths

    for path in tutorial_paths:
        html = path.read_text(encoding="utf-8")
        assert '<a href="#use-output">Final step: Use the output</a>' in html
        output_section = '<section id="use-output" class="article-section">'
        output_index = html.index(output_section)
        assert "<h2>Final step: Use the output</h2>" in html[output_index:]
        assert (
            "<strong>What to do with the output:</strong>" in html[output_index:]
        )

        finish_index = html.find('<section id="finish"', output_index)
        next_index = html.find('<section id="next"', output_index)
        assert finish_index > output_index or next_index > output_index
