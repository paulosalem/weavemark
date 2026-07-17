"""Tests for WeaveMark application logging (``configure_logging`` -> weavemark.log)."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from argparse import Namespace
from pathlib import Path

import pytest

from weavemark.logging_policy import LoggingSettings
from weavemark.logging_setup import (
    LOGGER_NAME,
    configure_logging,
    get_logger,
    log_cli_invocation,
)

_APP_TAG = "weavemark_app_file_handler"


def _clear_app_handlers() -> None:
    logger = logging.getLogger(LOGGER_NAME)
    for handler in list(logger.handlers):
        if getattr(handler, "_weavemark_tag", None) == _APP_TAG:
            logger.removeHandler(handler)
            handler.close()


def test_configure_logging_writes_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path))
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    _clear_app_handlers()
    try:
        log_file = configure_logging(level="INFO")
        assert log_file == tmp_path / "weavemark.log"

        get_logger("test").info("hello %d", 7)
        contents = log_file.read_text(encoding="utf-8")
        assert "hello 7" in contents
        assert "weavemark.test" in contents
        if os.name != "nt":
            assert log_file.stat().st_mode & 0o777 == 0o600
    finally:
        _clear_app_handlers()


def test_cli_invocation_logs_normal_variables_but_not_binary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path))
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    settings = LoggingSettings()
    _clear_app_handlers()
    try:
        log_file = configure_logging(settings=settings)
        assert log_file is not None
        log_cli_invocation(
            Namespace(
                spec_file="example.weavemark.md",
                model="gpt-5.5",
                var=["ticker=MSFT"],
            ),
            {"ticker": "MSFT", "image": b"\x89PNG"},
            settings,
        )

        contents = log_file.read_text(encoding="utf-8")
        assert "ticker" in contents
        assert "MSFT" in contents
        assert "ticker=MSFT" not in contents
        assert "89504e47" not in contents
        assert "binary omitted" in contents
    finally:
        _clear_app_handlers()


@pytest.mark.parametrize("flag", ["--help", "--version"])
def test_informational_cli_flags_create_no_logs(
    flag: str,
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).parents[1]
    environment = {
        **os.environ,
        "PYTHONPATH": str(repository_root / "src"),
        "WEAVEMARK_LOG_DIR": str(tmp_path / "logs"),
    }

    completed = subprocess.run(
        [sys.executable, "-m", "weavemark.app", flag],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert not (tmp_path / "logs").exists()


def test_configure_logging_removes_expired_logs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path))
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    expired = tmp_path / "llm-log-2000-01-01.jsonl"
    expired.write_text("{}\n", encoding="utf-8")
    old = time.time() - 40 * 24 * 60 * 60
    os.utime(expired, (old, old))
    _clear_app_handlers()
    try:
        configure_logging(settings=LoggingSettings(retention_days=30))
        assert not expired.exists()
    finally:
        _clear_app_handlers()


def test_cli_uses_configured_log_policy_and_omits_binary_variables(
    tmp_path: Path,
) -> None:
    repository_root = Path(__file__).parents[1]
    promplet = tmp_path / "example.weavemark.md"
    promplet.write_text("Hello @{name}.\n", encoding="utf-8")
    logs = tmp_path / "configured-logs"
    user_config = tmp_path / "user.json"
    user_config.write_text(
        json.dumps(
            {
                "log": {
                    "directory": str(logs),
                    "variables": True,
                    "binaryData": False,
                    "llmCalls": False,
                }
            }
        ),
        encoding="utf-8",
    )
    global_config = tmp_path / "global.json"
    global_config.write_text("{}", encoding="utf-8")
    environment = {
        **os.environ,
        "PYTHONPATH": str(repository_root / "src"),
        "WEAVEMARK_GLOBAL_CONFIG": str(global_config),
        "WEAVEMARK_USER_CONFIG": str(user_config),
    }

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "weavemark.app",
            str(promplet),
            "--var",
            "name=Ada",
            "--var",
            "image=data:image/png;base64,AAAA",
            "--batch-only",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    contents = (logs / "weavemark.log").read_text(encoding="utf-8")
    assert "Ada" in contents
    assert "AAAA" not in contents
    assert "binary data URL omitted" in contents
    assert not list(logs.glob("llm-log-*.jsonl"))


def test_configure_logging_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path))
    monkeypatch.delenv("WEAVEMARK_LOG", raising=False)
    _clear_app_handlers()
    try:
        first = configure_logging()
        second = configure_logging()
        assert first == second
        tagged = [
            h
            for h in logging.getLogger(LOGGER_NAME).handlers
            if getattr(h, "_weavemark_tag", None) == _APP_TAG
        ]
        assert len(tagged) == 1
    finally:
        _clear_app_handlers()


def test_configure_logging_disabled_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WEAVEMARK_LOG_DIR", str(tmp_path))
    monkeypatch.setenv("WEAVEMARK_LOG", "0")
    _clear_app_handlers()
    try:
        assert configure_logging() is None
        assert not (tmp_path / "weavemark.log").exists()
    finally:
        _clear_app_handlers()
