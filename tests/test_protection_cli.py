"""CLI behavior for experimental protections and explicit bypass."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from weavemark.app import create_implement_parser, create_parser


def test_cli_parsers_expose_explicit_protection_bypass() -> None:
    processor = create_parser().parse_args(
        ["spec.weavemark.md", "--no-protections"]
    )
    implement = create_implement_parser().parse_args(
        ["compiled.md", "--no-protections"]
    )

    assert processor.no_protections is True
    assert implement.no_protections is True


def test_batch_mode_blocks_confirmation_and_bypass_restores_trusted_behavior(
    tmp_path: Path,
) -> None:
    entrypoint = tmp_path / "entrypoint"
    outside = tmp_path / "outside"
    entrypoint.mkdir()
    outside.mkdir()
    (outside / "base.weavemark.md").write_text(
        "Trusted base content.\n",
        encoding="utf-8",
    )
    spec = entrypoint / "spec.weavemark.md"
    spec.write_text(
        "@refine ../outside/base.weavemark.md mingle: false\n",
        encoding="utf-8",
    )
    user_config = tmp_path / "user-config.json"
    user_config.write_text(
        json.dumps({"protections": {"enabled": True}}),
        encoding="utf-8",
    )
    global_config = tmp_path / "global-config.json"
    global_config.write_text("{}", encoding="utf-8")
    repository_root = Path(__file__).parents[1]
    environment = {
        **os.environ,
        "HOME": str(tmp_path / "home"),
        "PYTHONPATH": str(repository_root / "src"),
        "WEAVEMARK_GLOBAL_CONFIG": str(global_config),
        "WEAVEMARK_LOG": "0",
        "WEAVEMARK_USER_CONFIG": str(user_config),
    }
    base_command = [
        sys.executable,
        "-m",
        "weavemark.app",
        str(spec),
        "--batch-only",
    ]

    blocked = subprocess.run(
        base_command,
        cwd=entrypoint,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    bypassed = subprocess.run(
        [*base_command, "--no-protections"],
        cwd=entrypoint,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert blocked.returncode == 2
    blocked_output = blocked.stdout + blocked.stderr
    assert "WEAVEMARK PROTECTION BLOCKED" in blocked_output
    assert "protections.dynamicReads" in blocked_output
    assert "--no-protections" in blocked_output
    assert bypassed.returncode == 0
    assert "Trusted base content." in bypassed.stdout
