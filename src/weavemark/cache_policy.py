"""Typed local API-response cache policy for WeaveMark."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

_CACHE_KEYS = {"enabled", "directory"}


@dataclass(frozen=True, slots=True)
class CacheSettings:
    """Resolved controls for exact local API-response caching."""

    enabled: bool = True
    directory: Path | None = None


def cache_settings_from_config(
    data: Mapping[str, Any] | None,
    *,
    source: str,
    errors: list[str],
    base: CacheSettings | None = None,
) -> CacheSettings:
    """Parse one cache object over *base* settings."""

    current = base or CacheSettings()
    if data is None:
        return current

    unknown = sorted(set(data) - _CACHE_KEYS)
    if unknown:
        errors.append(f"{source} cache has unsupported key(s): {', '.join(unknown)}.")

    enabled = current.enabled
    if "enabled" in data:
        raw_enabled = data["enabled"]
        if isinstance(raw_enabled, bool):
            enabled = raw_enabled
        else:
            errors.append(f"{source} cache.enabled must be boolean.")

    directory = current.directory
    if "directory" in data:
        raw_directory = data["directory"]
        if raw_directory is None:
            directory = None
        elif isinstance(raw_directory, str) and raw_directory.strip():
            directory = Path(raw_directory).expanduser()
        else:
            errors.append(f"{source} cache.directory must be a path string or null.")

    return CacheSettings(enabled=enabled, directory=directory)


def tighten_cache_settings(
    current: CacheSettings,
    data: Mapping[str, Any] | None,
    *,
    source: str,
    warnings: list[str],
    errors: list[str],
) -> CacheSettings:
    """Allow project configuration to disable, but never force or redirect, caching."""

    if data is None:
        return current
    parsed = cache_settings_from_config(
        data,
        source=source,
        errors=errors,
        base=current,
    )
    if "directory" in data and parsed.directory != current.directory:
        warnings.append(f"{source} cannot change user-level cache.directory.")
    return replace(
        current,
        enabled=current.enabled and parsed.enabled,
        directory=current.directory,
    )


__all__ = [
    "CacheSettings",
    "cache_settings_from_config",
    "tighten_cache_settings",
]
