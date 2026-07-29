"""Tests for configurable compiled-spec implementation runs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from ellements.cli import CliPrinter

from weavemark.app import (
    create_implement_parser,
    create_parser,
    run_implement_command,
)
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
        / "software"
        / "sample-app"
        / "outputs"
        / "compiled-prompts"
        / "02-treatment-promplet-sample-app.md"
    )
    source.parent.mkdir(parents=True)
    source.write_text("# Sample app implementation spec\n", encoding="utf-8")
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

    assert result.implementation_name == "02-treatment-promplet-sample-app"
    assert result.implementation_dir == (
        tmp_path / "outputs" / "implementations" / "02-treatment-promplet-sample-app"
    )
    assert result.compiled_spec_snapshot.name == (
        "02-treatment-promplet-sample-app.compiled-spec.md"
    )
    assert result.agent_prompt.name == (
        "02-treatment-promplet-sample-app.implementation-prompt.md"
    )
    assert result.transcript.name == (
        "02-treatment-promplet-sample-app.copilot.transcript.log"
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
    source = tmp_path / "02-treatment-promplet-sample-app.md"
    source.write_text("# Spec\n", encoding="utf-8")
    settings = load_weavemark_settings(tmp_path).settings

    result = run_implementation(
        ImplementationRequest(
            compiled_spec_text="# Spec\n",
            source_path=source,
            settings=settings.implementation,
            invocation_dir=tmp_path,
            implementation_name="sample-app",
            dry_run=True,
        )
    )

    assert result.implementation_name == "sample-app"
    assert result.implementation_dir.name == "sample-app"


def test_builtin_prompt_requires_best_possible_verified_implementation(
    tmp_path: Path,
) -> None:
    source = tmp_path / "compiled.md"
    source.write_text("# Spec\n", encoding="utf-8")
    settings = load_weavemark_settings(tmp_path).settings

    result = run_implementation(
        ImplementationRequest(
            compiled_spec_text="# Spec\n",
            source_path=source,
            settings=settings.implementation,
            invocation_dir=tmp_path,
            implementation_name="sample-app",
            dry_run=True,
        )
    )

    prompt = result.agent_prompt.read_text(encoding="utf-8")
    assert "best possible complete, runnable implementation" in prompt
    assert "Do not optimize for the smallest or simplest implementation" in prompt
    assert "as much time, reasoning, tool use, and available resources as needed" in prompt
    assert "Implement, test, inspect, and verify the real result" in prompt
    assert "improve it and repeat the cycle" in prompt
    assert "use any available browser tools or MCP" in prompt
    assert "most gorgeous, beautiful, professional, cohesive" in prompt
    assert "MUST be evaluated through clean production" in prompt
    assert "vision-capable model or visual review agent" in prompt
    assert "inspecting the rendered pixels" in prompt
    assert "compare them directly with every visual criterion" in prompt
    assert "composition, realism, beauty, variety" in prompt
    assert "repeat vision review until" in prompt
    assert "report visual acceptance as blocked" in prompt
    assert "smallest complete, runnable implementation" not in prompt
    assert "simplest local stack" not in prompt


def test_builtin_copilot_profile_forwards_and_records_model(tmp_path: Path) -> None:
    source = tmp_path / "compiled.md"
    source.write_text("# Spec\n", encoding="utf-8")
    settings = load_weavemark_settings(tmp_path).settings

    result = run_implementation(
        ImplementationRequest(
            compiled_spec_text="# Spec\n",
            source_path=source,
            settings=settings.implementation,
            invocation_dir=tmp_path,
            implementation_name="sample-app",
            model="gpt-5.6-sol",
            dry_run=True,
        )
    )

    model_flag = result.command.index("--model")
    assert result.command[model_flag + 1] == "gpt-5.6-sol"
    manifest = json.loads(result.manifest.read_text(encoding="utf-8"))
    assert manifest["model"] == "gpt-5.6-sol"


def test_cli_parsers_accept_implementation_flags() -> None:
    parser = create_parser()
    args = parser.parse_args(
        [
            "spec.weavemark.md",
            "--implement",
            "--implementation-name",
            "sample-app",
            "--implementation-profile",
            "copilot",
            "--implementation-dry-run",
        ]
    )

    assert args.implement is True
    assert args.implementation_name == "sample-app"
    assert args.implementation_profile == "copilot"
    assert args.implementation_dry_run is True

    implement_parser = create_implement_parser()
    implement_args = implement_parser.parse_args(
        [
            "compiled.md",
            "--name",
            "sample-app",
            "--profile",
            "claude-code",
            "--dry-run",
        ]
    )
    assert implement_args.compiled_spec == Path("compiled.md")
    assert implement_args.name == "sample-app"
    assert implement_args.profile == "claude-code"
    assert implement_args.dry_run is True


def test_implement_subcommand_runs_dry_run_without_compile_only_arguments(
    tmp_path: Path,
) -> None:
    compiled_spec = tmp_path / "compiled.md"
    compiled_spec.write_text("# Compiled app\n", encoding="utf-8")
    output_root = tmp_path / "implementations"
    args = create_implement_parser().parse_args(
        [
            str(compiled_spec),
            "--name",
            "sample-app",
            "--output-root",
            str(output_root),
            "--dry-run",
            "--no-protections",
        ]
    )

    exit_code = run_implement_command(
        CliPrinter("WeaveMark", verbose=False),
        args,
    )

    assert exit_code == 0
    assert (output_root / "sample-app" / "compiled-spec.md").is_file()
    assert (output_root / "sample-app" / "implementation-prompt.md").is_file()


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
        approval_handler=lambda request: decisions.append(request.capability)
        or "allow_once",
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
