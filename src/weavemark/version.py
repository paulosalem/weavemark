"""Authoritative WeaveMark processor and language versions."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

LANGUAGE_VERSION = "0.9"

try:
    __version__ = version("weavemark")
except PackageNotFoundError:
    __version__ = "0.9.1"

PROCESSOR_VERSION = __version__

__all__ = ["LANGUAGE_VERSION", "PROCESSOR_VERSION", "__version__"]
