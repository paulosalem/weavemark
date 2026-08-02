"""Fast console-launch and no-provider discovery behavior."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def _run_python(code: str, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_package_root_defers_llm_runtime_until_api_use() -> None:
    completed = _run_python(
        "import sys, weavemark; "
        "assert 'litellm' not in sys.modules; "
        "assert callable(weavemark.compile_text); "
        "assert 'litellm' in sys.modules"
    )

    assert completed.returncode == 0, completed.stderr


def test_launcher_version_does_not_import_llm_runtime() -> None:
    completed = _run_python(
        "import sys; "
        "sys.argv=['weavemark', '--version']; "
        "from weavemark.launcher import cli; "
        "cli(); "
        "print('LITELLM_LOADED=' + str('litellm' in sys.modules))"
    )

    assert completed.returncode == 0, completed.stderr
    assert "weavemark 0.9.2 (WeaveMark language 0.9)" in completed.stdout
    assert "LITELLM_LOADED=False" in completed.stdout


def test_no_key_discovery_fails_once_without_litellm_banners(
    tmp_path: Path,
) -> None:
    env = dict(os.environ)
    env["HOME"] = str(tmp_path)
    for name in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
    ):
        env.pop(name, None)
    completed = subprocess.run(
        [sys.executable, "-m", "weavemark.app", "--discover"],
        cwd=ROOT,
        env=env,
        input="",
        capture_output=True,
        text=True,
        check=False,
    )

    combined = completed.stdout + completed.stderr
    assert completed.returncode == 1
    assert "Semantic discovery needs a configured model provider" in combined
    assert "Give Feedback / Get Help" not in combined


@pytest.mark.parametrize(
    ("collection", "target"),
    (
        ("executable", "market-snapshot"),
        ("standalone", "ai-kanban-board"),
    ),
)
def test_bundled_library_replays_are_strictly_offline(
    collection: str,
    target: str,
) -> None:
    env = dict(os.environ)
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
        env.pop(name, None)
    env.update(
        {
            "HTTP_PROXY": "http://127.0.0.1:9",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "NO_PROXY": "",
        }
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            "library",
            target,
            "--replay",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    replay_path = (
        ROOT
        / "promplets"
        / "replays"
        / "catalog"
        / collection
        / target
    )
    manifest = json.loads((replay_path / "manifest.json").read_text(encoding="utf-8"))
    original_run = manifest.get("original_run", {})
    if original_run.get("artifacts"):
        primary_output = original_run["primary_output"]
        artifact = next(
            item
            for item in original_run["artifacts"]
            if item["path"] == primary_output
        )
        expected = (replay_path / artifact["bundle_path"]).read_text(encoding="utf-8")
    else:
        expected = json.loads(
            (replay_path / "result.json").read_text(encoding="utf-8")
        )["composed_prompt"]

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.rstrip() == expected
    assert "Failed to fetch remote model cost map" not in completed.stderr


def test_market_replay_verbose_writes_output_and_original_run_stats(
    tmp_path: Path,
) -> None:
    output = tmp_path / "vale3-market-report.md"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            "library",
            "market-snapshot",
            "--replay",
            "--verbose",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert output.is_file()
    assert "# Vale S.A. (VALE3.SA) — Market-Learning Brief" in output.read_text(
        encoding="utf-8"
    )
    assert (tmp_path / "execution-trace.md").is_file()
    assert (tmp_path / "market-dashboard.html").is_file()
    rendered = " ".join((completed.stdout + completed.stderr).split())
    for statistic in (
        "Recorded input",
        "11,002",
        "Recorded cached",
        "0 (0%)",
        "Recorded output",
        "20,728",
        "API cost",
        "$0.3384",
    ):
        assert statistic in rendered


def test_ai_kanban_replay_verbose_reports_recorded_usage(
    tmp_path: Path,
) -> None:
    output = tmp_path / "ai-kanban-spec.md"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            "library",
            "ai-kanban-board",
            "--replay",
            "--verbose",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    rendered = " ".join((completed.stdout + completed.stderr).split())
    assert completed.returncode == 0, rendered
    assert output.is_file()
    for statistic in (
        "Tool calls: 14",
        "input:",
        "133,251",
        "Recorded cached",
        "114,705 (86%)",
        "output:",
        "10,917",
        "API cost",
        "$0.1910",
    ):
        assert statistic in rendered


@pytest.mark.parametrize("target", ["market-snapshot", "ai-kanban-board"])
def test_replay_open_publishes_a_real_artifact_without_an_output_path(
    target: str,
) -> None:
    """`--replay --verbose --open` hands a written file to the default opener."""

    env = {**os.environ, "BROWSER": "echo"}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            "library",
            target,
            "--replay",
            "--verbose",
            "--open",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    rendered = completed.stdout + completed.stderr
    assert completed.returncode == 0, rendered

    opened = [
        line.strip()
        for line in rendered.splitlines()
        if line.strip().startswith("file://")
    ]
    assert opened, rendered

    artifact = Path(opened[0].removeprefix("file://"))
    assert artifact.is_file()
    assert artifact.read_text(encoding="utf-8").strip()
    if target == "market-snapshot":
        assert artifact.name == "market-dashboard.html"
        assert "VALE3 Market Learning Dashboard" in artifact.read_text(
            encoding="utf-8"
        )
        assert (artifact.parent / "execution-output.md").is_file()
        assert (artifact.parent / "execution-trace.md").is_file()


def test_direct_replay_run_restores_and_opens_the_recorded_dashboard() -> None:
    replay = (
        ROOT
        / "promplets"
        / "replays"
        / "catalog"
        / "executable"
        / "market-snapshot"
    )
    env = {**os.environ, "BROWSER": "echo"}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            str(
                ROOT
                / "promplets"
                / "catalog"
                / "executable"
                / "market-snapshot.weavemark.md"
            ),
            "--replay-run",
            str(replay),
            "--vars-file",
            str(replay / "inputs.json"),
            "--model",
            "gpt-5.6-terra",
            "--open",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    rendered = completed.stdout + completed.stderr
    assert completed.returncode == 0, rendered
    assert "market-dashboard.html" in rendered
    assert "# Executable Market Learning Snapshot" not in completed.stdout


def test_complete_replay_rejects_format_overrides() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            "library",
            "market-snapshot",
            "--replay",
            "--format",
            "json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "--format cannot reformat exact recorded-run artifacts" in completed.stderr


def test_complete_replay_rejects_output_collisions(tmp_path: Path) -> None:
    output = tmp_path / "market-dashboard.html"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            "library",
            "market-snapshot",
            "--replay",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "resolve to the same output path" in completed.stderr
    assert not output.exists()


def test_complete_replay_rejects_symlinks_outside_output_root(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    outside = tmp_path / "outside.html"
    outside.write_text("do not overwrite", encoding="utf-8")
    (output_dir / "market-dashboard.html").symlink_to(outside)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.launcher",
            "library",
            "market-snapshot",
            "--replay",
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "destination escapes the selected output directory" in completed.stderr
    assert outside.read_text(encoding="utf-8") == "do not overwrite"
    assert not (output_dir / "execution-output.md").exists()
