"""Configurable, privacy-aware logging for the WeaveMark Processor."""

from __future__ import annotations

import json
import logging
import os
from argparse import Namespace
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from ellements.core import JsonlPromptLogger, LLMClient
from ellements.core.observability import (
    LLMErrorEvent,
    LLMRequestEvent,
    LLMResponseEvent,
)

from .discovery.config import GLOBAL_DIR
from .logging_policy import LoggingSettings, sanitize_log_value
from .protection import ProtectionContext

_DISABLED_VALUES = {"0", "off", "false", "no"}

LOGGER_NAME = "weavemark"
_APP_LOG_FILE_NAME = "weavemark.log"
_APP_HANDLER_TAG = "weavemark_app_file_handler"


class PolicyPromptLogger:
    """Filter LLM events according to WeaveMark logging settings."""

    def __init__(self, directory: Path, settings: LoggingSettings) -> None:
        self.settings = settings
        self.delegate = JsonlPromptLogger(directory)

    async def on_request(self, event: LLMRequestEvent) -> None:
        messages = (
            _sanitize_messages(event.messages, self.settings)
            if self.settings.llm_requests
            else []
        )
        tools = (
            sanitize_log_value(
                event.tools,
                include_binary=self.settings.binary_data,
            )
            if self.settings.llm_requests and self.settings.tool_data
            else []
        )
        extra_params = (
            sanitize_log_value(
                event.extra_params,
                include_binary=self.settings.binary_data,
            )
            if self.settings.llm_requests
            else {}
        )
        await self.delegate.on_request(
            replace(
                event,
                messages=messages,
                tools=tools,
                extra_params=extra_params,
                metadata=sanitize_log_value(
                    event.metadata,
                    include_binary=self.settings.binary_data,
                ),
            )
        )

    async def on_response(self, event: LLMResponseEvent) -> None:
        response = (
            sanitize_log_value(
                event.response,
                include_binary=self.settings.binary_data,
            )
            if self.settings.llm_responses
            else ""
        )
        tool_calls = (
            sanitize_log_value(
                event.tool_calls,
                include_binary=self.settings.binary_data,
            )
            if self.settings.tool_data
            else []
        )
        await self.delegate.on_response(
            replace(
                event,
                response=str(response),
                tool_calls=tool_calls,
                usage=event.usage if self.settings.usage else None,
                metadata=sanitize_log_value(
                    event.metadata,
                    include_binary=self.settings.binary_data,
                ),
            )
        )

    async def on_error(self, event: LLMErrorEvent) -> None:
        error = (
            event.error
            if self.settings.errors
            else RuntimeError("<error details disabled by log.errors>")
        )
        await self.delegate.on_error(
            replace(
                event,
                error=error,
                metadata=sanitize_log_value(
                    event.metadata,
                    include_binary=self.settings.binary_data,
                ),
            )
        )


def logging_enabled(settings: LoggingSettings | None = None) -> bool:
    """Return whether logging is enabled after environment overrides."""

    configured = settings or LoggingSettings()
    environment_enabled = (
        os.environ.get("WEAVEMARK_LOG", "").strip().lower() not in _DISABLED_VALUES
    )
    return configured.enabled and environment_enabled


def default_log_dir(settings: LoggingSettings | None = None) -> Path | None:
    """Return the effective log directory, or ``None`` when disabled."""

    configured = settings or LoggingSettings()
    if not logging_enabled(configured):
        return None
    override = os.environ.get("WEAVEMARK_LOG_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    return configured.directory or GLOBAL_DIR / "logs"


def new_client(
    *,
    model: str,
    protection: ProtectionContext | None = None,
    logging_settings: LoggingSettings | None = None,
    **kwargs: Any,
) -> LLMClient:
    """Construct an LLM client with policy-filtered WeaveMark call logging."""

    del protection
    settings = logging_settings or LoggingSettings()
    configured_log_dir = kwargs.pop("log_dir", None)
    directory = (
        Path(configured_log_dir).expanduser()
        if configured_log_dir is not None
        else default_log_dir(settings)
    )
    observers = list(kwargs.pop("observers", None) or ())
    if directory is not None and settings.llm_calls:
        _prepare_log_directory(directory, settings)
        observers.append(PolicyPromptLogger(directory, settings))
    return LLMClient(model=model, observers=observers, **kwargs)


def configure_logging(
    *,
    settings: LoggingSettings | None = None,
    level: int | str | None = None,
) -> Path | None:
    """Attach the configured rotating application-log handler."""

    configured = settings or LoggingSettings()
    directory = default_log_dir(configured)
    logger = logging.getLogger(LOGGER_NAME)
    if directory is None or not configured.application_events:
        _close_app_handlers(logger)
        return None

    logger.setLevel(_resolve_app_level(level or configured.level))
    logger.propagate = False

    target = (directory / _APP_LOG_FILE_NAME).resolve()
    for existing in list(logger.handlers):
        if getattr(existing, "_weavemark_tag", None) == _APP_HANDLER_TAG:
            base_filename = getattr(existing, "baseFilename", None)
            if (
                isinstance(base_filename, str)
                and Path(base_filename).resolve() == target
            ):
                return Path(base_filename)
            logger.removeHandler(existing)
            existing.close()

    try:
        _prepare_log_directory(directory, configured)
        handler = RotatingFileHandler(
            directory / _APP_LOG_FILE_NAME,
            maxBytes=configured.max_file_bytes,
            backupCount=configured.backup_count,
            encoding="utf-8",
        )
        _restrict_path(Path(handler.baseFilename), directory=False)
    except OSError:
        return None

    handler._weavemark_tag = _APP_HANDLER_TAG  # type: ignore[attr-defined]
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-7s %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    logger.addHandler(handler)
    return Path(handler.baseFilename)


def log_cli_invocation(
    args: Namespace,
    variables: dict[str, Any],
    settings: LoggingSettings,
) -> None:
    """Log one structured invocation without raw argument leakage."""

    if not logging_enabled(settings) or not settings.application_events:
        return
    payload: dict[str, Any] = {}
    if settings.cli_arguments:
        payload["arguments"] = {
            key: sanitize_log_value(
                value,
                include_binary=settings.binary_data,
            )
            for key, value in vars(args).items()
            if key not in {"var"}
        }
    if settings.variables:
        payload["variables"] = sanitize_log_value(
            variables,
            include_binary=settings.binary_data,
        )
    get_logger("cli").info(
        "invocation %s",
        json.dumps(payload, ensure_ascii=False, sort_keys=True),
    )


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the WeaveMark application logger or one of its children."""

    if not name:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def _sanitize_messages(
    messages: list[dict[str, Any]],
    settings: LoggingSettings,
) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for message in messages:
        if not settings.tool_data and message.get("role") == "tool":
            continue
        value = sanitize_log_value(
            message,
            include_binary=settings.binary_data,
        )
        if not isinstance(value, dict):
            continue
        if not settings.tool_data:
            value.pop("tool_calls", None)
            value.pop("tool_call_id", None)
        sanitized.append(value)
    return sanitized


def _resolve_app_level(level: int | str | None) -> int:
    if level is None:
        level = os.environ.get("WEAVEMARK_LOG_LEVEL", "INFO")
    elif "WEAVEMARK_LOG_LEVEL" in os.environ:
        level = os.environ["WEAVEMARK_LOG_LEVEL"]
    if isinstance(level, int):
        return level
    resolved = logging.getLevelName(str(level).strip().upper())
    return resolved if isinstance(resolved, int) else logging.INFO


def _prepare_log_directory(
    directory: Path,
    settings: LoggingSettings,
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    _restrict_path(directory, directory=True)
    _remove_expired_logs(directory, settings.retention_days)


def _remove_expired_logs(directory: Path, retention_days: int | None) -> None:
    if retention_days is None:
        return
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    for pattern in ("weavemark.log*", "llm-log-*.jsonl"):
        for path in directory.glob(pattern):
            try:
                modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
                if modified < cutoff:
                    path.unlink()
            except OSError:
                continue


def _restrict_path(path: Path, *, directory: bool) -> None:
    if os.name != "nt":
        path.chmod(0o700 if directory else 0o600)


def _close_app_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        if getattr(handler, "_weavemark_tag", None) == _APP_HANDLER_TAG:
            logger.removeHandler(handler)
            handler.close()


__all__ = [
    "LOGGER_NAME",
    "PolicyPromptLogger",
    "configure_logging",
    "default_log_dir",
    "get_logger",
    "log_cli_invocation",
    "logging_enabled",
    "new_client",
]
