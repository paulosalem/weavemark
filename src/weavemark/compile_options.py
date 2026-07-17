"""Shared helpers for WeaveMark compile-time options."""

from __future__ import annotations

from weavemark.settings import (
    WeaveMarkSettings,
    builtin_weavemark_settings,
)

DEFAULT_COMPILE_FORMAT = "markdown"
SUPPORTED_CONTEXT_MODES = ("auto", "cascade", "local")


def normalize_compile_format(
    value: object,
    settings: WeaveMarkSettings | None = None,
) -> str | None:
    """Return the canonical compile format name, or ``None`` if unsupported."""

    return (settings or builtin_weavemark_settings()).normalize_format(value)


def supported_compile_formats_text(settings: WeaveMarkSettings | None = None) -> str:
    """Return a human-readable list of supported compile formats."""

    return (settings or builtin_weavemark_settings()).supported_formats_text()


def extension_for_compile_format(
    format_name: str | None,
    settings: WeaveMarkSettings | None = None,
) -> str:
    """Return the file extension (without dot) for a normalized compile format."""

    return (settings or builtin_weavemark_settings()).format_extension(
        format_name or DEFAULT_COMPILE_FORMAT
    )


def normalize_context_mode(value: object) -> str | None:
    """Return the canonical shared-context mode, or ``None`` if unsupported."""

    text = str(value).strip().lower()
    return text if text in SUPPORTED_CONTEXT_MODES else None
