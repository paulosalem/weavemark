"""Stable user-facing and machine-readable diagnostic behavior."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from weavemark.compilation.fslm_sugar import lower_machine_block


def _environment(repository_root: Path) -> dict[str, str]:
    return {
        **os.environ,
        "PYTHONPATH": str(repository_root / "src"),
        "WEAVEMARK_LOG": "0",
    }


def test_malformed_vars_file_emits_json_diagnostic_without_traceback(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).parents[1]
    promplet = tmp_path / "example.weavemark.md"
    promplet.write_text("Hello @{name}.\n", encoding="utf-8")
    variables = tmp_path / "variables.json"
    variables.write_text('{"name":', encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.app",
            str(promplet),
            "--vars-file",
            str(variables),
            "--format",
            "json",
            "--batch-only",
        ],
        cwd=tmp_path,
        env=_environment(repository_root),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    diagnostic = json.loads(completed.stderr)["diagnostics"][0]
    assert diagnostic["code"] == "WM-INPUT-VARS-JSON"
    assert diagnostic["source"] == str(variables)
    assert diagnostic["line"] == 1
    assert "Traceback" not in completed.stderr


def test_malformed_inline_fslm_numbers_become_contextual_errors() -> None:
    result = lower_machine_block(
        "support initial: triage",
        """@state triage
  @transition retry target: triage weight: heavy
    @guard enough min_confidence: certain
""",
    )

    assert any(
        "@transition parameter 'weight' must be numeric" in error
        for error in result.errors
    )
    assert any(
        "@guard parameter 'min_confidence' must be numeric" in error
        for error in result.errors
    )


def test_compilation_error_json_includes_source_line_and_directive(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).parents[1]
    promplet = tmp_path / "invalid.weavemark.md"
    promplet.write_text("@iterate nope\n  Improve this.\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.app",
            str(promplet),
            "--format",
            "json",
            "--batch-only",
        ],
        cwd=tmp_path,
        env=_environment(repository_root),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    diagnostics = json.loads(completed.stderr)["diagnostics"]
    error = next(item for item in diagnostics if item["severity"] == "error")
    assert error["source"] == str(promplet)
    assert error["line"] == 1
    assert error["directive"] == "@iterate"
