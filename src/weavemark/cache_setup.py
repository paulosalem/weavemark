"""Runtime setup and observability for WeaveMark's local API cache."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from ellements.core import LocalCacheConfig
from ellements.core.observability import (
    LLMErrorEvent,
    LLMRequestEvent,
    LLMResponseEvent,
)

from .cache_policy import CacheSettings
from .discovery.config import GLOBAL_DIR

_DISABLED_VALUES = {"0", "off", "false", "no"}
_LOGGER_NAME = "weavemark"
CacheHitCallback = Callable[[dict[str, Any]], None]


def cache_enabled(settings: CacheSettings | None = None) -> bool:
    """Return whether local caching is enabled after environment overrides."""

    configured = settings or CacheSettings()
    environment_enabled = (
        os.environ.get("WEAVEMARK_CACHE", "").strip().lower()
        not in _DISABLED_VALUES
    )
    return configured.enabled and environment_enabled


def default_cache_dir(settings: CacheSettings | None = None) -> Path | None:
    """Return the effective local-cache directory, or ``None`` when disabled."""

    configured = settings or CacheSettings()
    if not cache_enabled(configured):
        return None
    override = os.environ.get("WEAVEMARK_CACHE_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    return configured.directory or Path(GLOBAL_DIR) / "cache"


def local_cache_config(
    settings: CacheSettings | None = None,
) -> LocalCacheConfig | None:
    """Translate WeaveMark policy into Ellements client configuration."""

    directory = default_cache_dir(settings)
    return LocalCacheConfig(directory) if directory is not None else None


class LocalCacheObserver:
    """Report exact local-cache hits distinctly from provider prompt caching."""

    def __init__(self, callback: CacheHitCallback | None = None) -> None:
        self._callback = callback

    async def on_request(self, event: LLMRequestEvent) -> None:
        del event

    async def on_response(self, event: LLMResponseEvent) -> None:
        self._report(event.method, event.model, event.metadata)

    async def on_error(self, event: LLMErrorEvent) -> None:
        self._report(event.method, event.model, event.metadata)

    def _report(
        self,
        method: str,
        model: str,
        metadata: Mapping[str, Any],
    ) -> None:
        cache_data = metadata.get("local_cache")
        if not isinstance(cache_data, Mapping) or cache_data.get("hit") is not True:
            return
        data = {
            "method": method,
            "model": model,
            "backend": str(cache_data.get("backend", "local")),
            "hits": int(cache_data.get("hits", 1)),
        }
        logging.getLogger(_LOGGER_NAME).info(
            "LOCAL cache used: method=%s model=%s backend=%s hits=%d",
            data["method"],
            data["model"],
            data["backend"],
            data["hits"],
        )
        if self._callback is not None:
            self._callback(data)


__all__ = [
    "CacheHitCallback",
    "LocalCacheObserver",
    "cache_enabled",
    "default_cache_dir",
    "local_cache_config",
]
