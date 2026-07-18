"""Tests for configurable compiled-spec implementation runs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from weavemark.app import create_implement_parser, create_parser
from weavemark.implementation import ImplementationRequest, run_implementation
from weavemark.protection import ProtectionContext, ProtectionError, ProtectionSettings
from weavemark.settings import load_weavemark_settings


def test_implementation_config_loads_custom_profile(tmp_path: Path) -> None:
    (tmp_path / "weavemark.json").write_text(
        json.dumps(
            {
                "implementation": {
                    "default_profile": "claude-code",
                    "profiles": {
                        "claude-code": {
                            "type": "process",
                            "command": "claude",
                            "args": ["-p", "{prompt_text}"],
                        }
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    result = load_weavemark_settings(tmp_path)

    assert result.errors == ()
    implementation = result.settings.implementation
    assert implementation.default_profile == "claude-code"
    assert implementation.profiles["claude-code"].command == "claude"
    assert implementation.profiles["copilot"].command == "copilot"


def test_dry_run_uses_exact_compiled_stem_without_prefix_stripping(
    tmp_path: Path,
) -> None:
    source = (
        tmp_path
        / "studies"
        / "games"
        / "orbital"
        / "outputs"
        / "compiled-prompts"
        / "02-treatment-promplet-orbital-drift.md"
    )
    source.parent.mkdir(parents=True)
    source.write_text("# Orbital Drift implementation spec\n", encoding="utf-8")
    settings = load_weavemark_settings(tmp_path).settings

    result = run_implementation(
        ImplementationRequest(
            compiled_spec_text=source.read_text(encoding="utf-8"),
            source_path=source,
            settings=settings.implementation,
            invocation_dir=tmp_path,
            dry_run=True,
        )
    )

    assert result.implementation_name == "02-treatment-promplet-orbital-drift"
    assert result.implementation_dir == (
        tmp_path / "outputs" / "implementations" / "02-treatment-promplet-orbital-drift"
    )
    assert result.compiled_spec_snapshot.name == (
        "02-treatment-promplet-orbital-drift.compiled-spec.md"
    )
    assert result.agent_prompt.name == (
        "02-treatment-promplet-orbital-drift.implementation-prompt.md"
    )
    assert result.transcript.name == (
        "02-treatment-promplet-orbital-drift.copilot.transcript.log"
    )
    assert (result.implementation_dir / "compiled-spec.md").is_file()
    assert (result.implementation_dir / "implementation-prompt.md").is_file()
    assert json.loads(result.manifest.read_text(encoding="utf-8"))["dry_run"] is True


def test_weavemark_source_stem_strips_only_weavemark_compound_suffix(
    tmp_path: Path,
) -> None:
    source = tmp_path / "planning-dashboard.weavemark.md"
    source.write_text("# Planning dashboard spec\n", encoding="utf-8")
    settings = load_weavemark_settings(tmp_path).settings

    result = run_implementation(
        ImplementationRequest(
            compiled_spec_text="Compiled app spec.",
            source_path=source,
            settings=settings.implementation,
            invocation_dir=tmp_path,
            dry_run=True,
        )
    )

    assert result.implementation_name == "planning-dashboard"
    assert result.implementation_dir.name == "planning-dashboard"


def test_implementation_name_overrides_default(tmp_path: Path) -> None:
    source = tmp_path / "02-treatment-promplet-orbital-drift.md"
    source.write_text("# Spec\n", encoding="utf-8")
    settings = load_weavemark_settings(tmp_path).settings

    result = run_implementation(
        ImplementationRequest(
            compiled_spec_text="# Spec\n",
            source_path=source,
            settings=settings.implementation,
            invocation_dir=tmp_path,
            implementation_name="orbital-drift",
            dry_run=True,
        )
    )

    assert result.implementation_name == "orbital-drift"
    assert result.implementation_dir.name == "orbital-drift"


def test_cli_parsers_accept_implementation_flags() -> None:
    parser = create_parser()
    args = parser.parse_args(
        [
            "spec.weavemark.md",
            "--implement",
            "--implementation-name",
            "orbital-drift",
            "--implementation-profile",
            "copilot",
            "--implementation-dry-run",
        ]
    )

    assert args.implement is True
    assert args.implementation_name == "orbital-drift"
    assert args.implementation_profile == "copilot"
    assert args.implementation_dry_run is True

    implement_parser = create_implement_parser()
    implement_args = implement_parser.parse_args(
        [
            "compiled.md",
            "--name",
            "orbital-drift",
            "--profile",
            "claude-code",
            "--dry-run",
        ]
    )
    assert implement_args.compiled_spec == Path("compiled.md")
    assert implement_args.name == "orbital-drift"
    assert implement_args.profile == "claude-code"
    assert implement_args.dry_run is True


def test_implementation_process_requires_approval(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = load_weavemark_settings(tmp_path).settings
    protection = ProtectionContext.create(
        ProtectionSettings(),
        entrypoint_dir=tmp_path,
        invocation_dir=tmp_path,
        approvals_path=tmp_path / "approvals.json",
    )
    monkeypatch.setattr(
        "weavemark.implementation.shutil.which", lambda _name: sys.executable
    )

    with pytest.raises(ProtectionError, match="external process execution"):
        run_implementation(
            ImplementationRequest(
                compiled_spec_text="# App\n",
                source_path=tmp_path / "app.weavemark.md",
                settings=settings.implementation,
                invocation_dir=tmp_path,
                implementation_name="app",
                protection=protection,
            )
        )


def test_implementation_process_receives_reduced_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "weavemark.json").write_text(
        json.dumps(
            {
                "implementation": {
                    "default_profile": "test",
                    "profiles": {
                        "test": {
                            "type": "process",
                            "command": "python",
                            "args": ["-c", "print('ok')"],
                            "env": {"PROFILE_SETTING": "enabled"},
                        }
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    settings = load_weavemark_settings(tmp_path).settings
    decisions: list[str] = []
    protection = ProtectionContext.create(
        ProtectionSettings(subprocess_environment=("PATH",)),
        entrypoint_dir=tmp_path,
        invocation_dir=tmp_path,
        approval_handler=lambda request: decisions.append(request.capability) or True,
        approvals_path=tmp_path / "approvals.json",
    )
    monkeypatch.setenv("PATH", os.environ.get("PATH", ""))
    monkeypatch.setenv("SECRET_TOKEN", "must-not-leak")
    monkeypatch.setattr(
        "weavemark.implementation.shutil.which", lambda _name: sys.executable
    )
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs["env"]
        return SimpleNamespace(stdout="", returncode=0)

    monkeypatch.setattr("weavemark.implementation.subprocess.run", fake_run)

    result = run_implementation(
        ImplementationRequest(
            compiled_spec_text="# App\n",
            source_path=tmp_path / "app.weavemark.md",
            settings=settings.implementation,
            invocation_dir=tmp_path,
            implementation_name="app",
            protection=protection,
        )
    )

    assert result.exit_code == 0
    assert decisions == ["external process execution"]
    assert captured["command"][0] == "python"
    assert captured["env"] == {
        "PATH": os.environ["PATH"],
        "PROFILE_SETTING": "enabled",
    }
