"""Typed, privacy-aware logging policy for WeaveMark."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

_LOG_KEYS = {
    "enabled",
    "directory",
    "level",
    "applicationEvents",
    "cliArguments",
    "variables",
    "llmCalls",
    "llmRequests",
    "llmResponses",
    "toolData",
    "usage",
    "errors",
    "binaryData",
    "maxFileBytes",
    "backupCount",
    "retentionDays",
}
_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_BINARY_KEYS = {
    "audio_data",
    "b64_json",
    "base64",
    "file_data",
    "image_bytes",
    "pdf_data",
}
_DATA_URL_RE = re.compile(
    r"^data:(?:image|audio|video|application/octet-stream|application/pdf)/?[^,]*;base64,",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class LoggingSettings:
    """Resolved controls for application and LLM-call logs."""

    enabled: bool = True
    directory: Path | None = None
    level: str = "INFO"
    application_events: bool = True
    cli_arguments: bool = True
    variables: bool = True
    llm_calls: bool = True
    llm_requests: bool = True
    llm_responses: bool = True
    tool_data: bool = True
    usage: bool = True
    errors: bool = True
    binary_data: bool = False
    max_file_bytes: int = 5 * 1024 * 1024
    backup_count: int = 5
    retention_days: int | None = 30


def logging_settings_from_config(
    data: Mapping[str, Any] | None,
    *,
    source: str,
    errors: list[str],
    base: LoggingSettings | None = None,
) -> LoggingSettings:
    """Parse one logging object over *base* settings."""

    current = base or LoggingSettings()
    if data is None:
        return current
    unknown = sorted(set(data) - _LOG_KEYS)
    if unknown:
        errors.append(f"{source} log has unsupported key(s): {', '.join(unknown)}.")

    directory = current.directory
    if "directory" in data:
        raw_directory = data["directory"]
        if raw_directory is None:
            directory = None
        elif isinstance(raw_directory, str) and raw_directory.strip():
            directory = Path(raw_directory).expanduser()
        else:
            errors.append(f"{source} log.directory must be a path string or null.")

    level = current.level
    if "level" in data:
        raw_level = data["level"]
        if isinstance(raw_level, str) and raw_level.upper() in _LEVELS:
            level = raw_level.upper()
        else:
            errors.append(f"{source} log.level must be one of: {', '.join(_LEVELS)}.")

    return LoggingSettings(
        enabled=_bool(data, "enabled", current.enabled, source, errors),
        directory=directory,
        level=level,
        application_events=_bool(
            data,
            "applicationEvents",
            current.application_events,
            source,
            errors,
        ),
        cli_arguments=_bool(
            data,
            "cliArguments",
            current.cli_arguments,
            source,
            errors,
        ),
        variables=_bool(data, "variables", current.variables, source, errors),
        llm_calls=_bool(data, "llmCalls", current.llm_calls, source, errors),
        llm_requests=_bool(
            data,
            "llmRequests",
            current.llm_requests,
            source,
            errors,
        ),
        llm_responses=_bool(
            data,
            "llmResponses",
            current.llm_responses,
            source,
            errors,
        ),
        tool_data=_bool(data, "toolData", current.tool_data, source, errors),
        usage=_bool(data, "usage", current.usage, source, errors),
        errors=_bool(data, "errors", current.errors, source, errors),
        binary_data=_bool(
            data,
            "binaryData",
            current.binary_data,
            source,
            errors,
        ),
        max_file_bytes=_positive_int(
            data,
            "maxFileBytes",
            current.max_file_bytes,
            source,
            errors,
        ),
        backup_count=_nonnegative_int(
            data,
            "backupCount",
            current.backup_count,
            source,
            errors,
        ),
        retention_days=_optional_nonnegative_int(
            data,
            "retentionDays",
            current.retention_days,
            source,
            errors,
        ),
    )


def tighten_logging_settings(
    current: LoggingSettings,
    data: Mapping[str, Any] | None,
    *,
    source: str,
    warnings: list[str],
    errors: list[str],
) -> LoggingSettings:
    """Allow project configuration to reduce, but never expand, logging."""

    if data is None:
        return current
    parsed = logging_settings_from_config(
        data,
        source=source,
        errors=errors,
        base=current,
    )
    if "directory" in data and parsed.directory != current.directory:
        warnings.append(f"{source} cannot change user-level log.directory.")
    booleans = {
        "enabled": "enabled",
        "applicationEvents": "application_events",
        "cliArguments": "cli_arguments",
        "variables": "variables",
        "llmCalls": "llm_calls",
        "llmRequests": "llm_requests",
        "llmResponses": "llm_responses",
        "toolData": "tool_data",
        "usage": "usage",
        "errors": "errors",
        "binaryData": "binary_data",
    }
    updates: dict[str, Any] = {"directory": current.directory}
    for config_key, field_name in booleans.items():
        updates[field_name] = (
            bool(getattr(current, field_name) and getattr(parsed, field_name))
            if config_key in data
            else getattr(current, field_name)
        )
    updates["level"] = (
        max(current.level, parsed.level, key=_LEVELS.index)
        if "level" in data
        else current.level
    )
    updates["max_file_bytes"] = (
        min(current.max_file_bytes, parsed.max_file_bytes)
        if "maxFileBytes" in data
        else current.max_file_bytes
    )
    updates["backup_count"] = (
        min(current.backup_count, parsed.backup_count)
        if "backupCount" in data
        else current.backup_count
    )
    updates["retention_days"] = (
        _tighter_retention(
            current.retention_days,
            parsed.retention_days,
        )
        if "retentionDays" in data
        else current.retention_days
    )
    return replace(current, **updates)


def sanitize_log_value(value: Any, *, include_binary: bool) -> Any:
    """Recursively omit binary/base64 payloads while preserving debug structure."""

    if isinstance(value, bytes | bytearray | memoryview):
        return (
            base64.b64encode(bytes(value)).decode("ascii")
            if include_binary
            else f"<binary omitted: {len(value)} bytes>"
        )
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = str(key)
            if not include_binary and normalized_key.casefold() in _BINARY_KEYS:
                sanitized[normalized_key] = _binary_marker(item)
            else:
                sanitized[normalized_key] = sanitize_log_value(
                    item,
                    include_binary=include_binary,
                )
        return sanitized
    if isinstance(value, tuple | list | set | frozenset):
        return [
            sanitize_log_value(item, include_binary=include_binary) for item in value
        ]
    if isinstance(value, str) and not include_binary and _DATA_URL_RE.match(value):
        payload = value.partition(",")[2]
        return f"<binary data URL omitted: {len(payload)} base64 chars>"
    if value is None or isinstance(value, str | int | float | bool):
        return value
    return repr(value)


def _binary_marker(value: Any) -> str:
    if isinstance(value, str):
        return f"<binary omitted: {len(value)} chars>"
    if isinstance(value, bytes | bytearray | memoryview):
        return f"<binary omitted: {len(value)} bytes>"
    return "<binary omitted>"


def _bool(
    data: Mapping[str, Any],
    key: str,
    default: bool,
    source: str,
    errors: list[str],
) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        errors.append(f"{source} log.{key} must be boolean.")
        return default
    return value


def _positive_int(
    data: Mapping[str, Any],
    key: str,
    default: int,
    source: str,
    errors: list[str],
) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        errors.append(f"{source} log.{key} must be a positive integer.")
        return default
    return value


def _nonnegative_int(
    data: Mapping[str, Any],
    key: str,
    default: int,
    source: str,
    errors: list[str],
) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{source} log.{key} must be a non-negative integer.")
        return default
    return value


def _optional_nonnegative_int(
    data: Mapping[str, Any],
    key: str,
    default: int | None,
    source: str,
    errors: list[str],
) -> int | None:
    value = data.get(key, default)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{source} log.{key} must be a non-negative integer or null.")
        return default
    return value


def _tighter_retention(
    current: int | None,
    parsed: int | None,
) -> int | None:
    if current is None:
        return parsed
    if parsed is None:
        return current
    return min(current, parsed)


__all__ = [
    "LoggingSettings",
    "logging_settings_from_config",
    "sanitize_log_value",
    "tighten_logging_settings",
]
