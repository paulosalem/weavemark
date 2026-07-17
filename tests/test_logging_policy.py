"""Typed logging policy and configuration precedence tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from weavemark.logging_policy import LoggingSettings, sanitize_log_value
from weavemark.settings import load_weavemark_settings


def test_default_policy_is_debuggable_without_binary_payloads() -> None:
    settings = LoggingSettings()

    assert settings.enabled is True
    assert settings.application_events is True
    assert settings.cli_arguments is True
    assert settings.variables is True
    assert settings.llm_requests is True
    assert settings.llm_responses is True
    assert settings.tool_data is True
    assert settings.usage is True
    assert settings.errors is True
    assert settings.binary_data is False


def test_binary_sanitization_preserves_surrounding_structure() -> None:
    value = {
        "ticker": "MSFT",
        "image": b"\x89PNG",
        "nested": {
            "url": "data:image/png;base64,AAAA",
            "note": "keep me",
        },
    }

    sanitized = sanitize_log_value(value, include_binary=False)

    assert sanitized["ticker"] == "MSFT"
    assert sanitized["image"] == "<binary omitted: 4 bytes>"
    assert sanitized["nested"]["note"] == "keep me"
    assert "AAAA" not in sanitized["nested"]["url"]
    included = sanitize_log_value(value, include_binary=True)
    assert included["image"] == "iVBORw=="
    assert included["nested"]["url"].endswith("AAAA")


def test_user_logging_config_applies_and_project_can_only_reduce_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_config = tmp_path / "user.json"
    user_config.write_text(
        json.dumps(
            {
                "log": {
                    "directory": str(tmp_path / "user-logs"),
                    "variables": True,
                    "binaryData": True,
                    "retentionDays": 60,
                    "level": "DEBUG",
                }
            }
        ),
        encoding="utf-8",
    )
    global_config = tmp_path / "global.json"
    global_config.write_text("{}", encoding="utf-8")
    project = tmp_path / "project"
    project.mkdir()
    (project / "weavemark.json").write_text(
        json.dumps(
            {
                "log": {
                    "directory": str(tmp_path / "project-logs"),
                    "variables": False,
                    "binaryData": False,
                    "retentionDays": 7,
                    "level": "WARNING",
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("WEAVEMARK_USER_CONFIG", str(user_config))
    monkeypatch.setenv("WEAVEMARK_GLOBAL_CONFIG", str(global_config))

    result = load_weavemark_settings(project)

    assert result.errors == ()
    assert result.settings.logging.directory == tmp_path / "user-logs"
    assert result.settings.logging.variables is False
    assert result.settings.logging.binary_data is False
    assert result.settings.logging.retention_days == 7
    assert result.settings.logging.level == "WARNING"
    assert result.warnings == (
        f"{project / 'weavemark.json'} cannot change user-level log.directory.",
    )


def test_invalid_logging_config_is_reported(tmp_path: Path) -> None:
    (tmp_path / "weavemark.json").write_text(
        json.dumps(
            {
                "log": {
                    "variables": "yes",
                    "binaryData": False,
                    "retentionDays": -1,
                    "unknown": True,
                }
            }
        ),
        encoding="utf-8",
    )

    result = load_weavemark_settings(tmp_path)

    assert any("unsupported key" in error for error in result.errors)
    assert any("log.variables must be boolean" in error for error in result.errors)
    assert any("log.retentionDays" in error for error in result.errors)
