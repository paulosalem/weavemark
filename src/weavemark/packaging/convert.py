"""Deterministic conversion of a rendered deliverable to another format.

A markup deliverable (e.g. HTML produced by a packaging template) can be
converted to a format that has no markup of its own — currently PDF, via a
headless browser. This is intentionally general: conversions are keyed by the
target file extension, so new converters slot in without touching callers.

All converters are synchronous and must be invoked off the event loop (the
Playwright sync API refuses to run inside a running asyncio loop); the packaging
runner calls them via ``asyncio.to_thread``.
"""

from __future__ import annotations

from pathlib import Path


class ConversionError(RuntimeError):
    """Raised when a requested deliverable conversion is unsupported."""


def _html_to_pdf(source: Path, target: Path) -> bool:
    """Render an HTML file to PDF with headless Chromium. Returns success.

    Returns ``False`` (rather than raising) when Playwright/Chromium is not
    available, so packaging degrades gracefully to the HTML deliverable.
    """

    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(source.resolve().as_uri())
            page.pdf(path=str(target), print_background=True, prefer_css_page_size=True)
            browser.close()
    except Exception:
        return False
    return True


def convert_file(source: Path, target: Path) -> bool:
    """Convert *source* to *target*, dispatching on the target extension.

    Returns ``True`` on success, ``False`` when an optional backend is missing.
    Raises :class:`ConversionError` for an unsupported target format.
    """

    suffix = target.suffix.lower()
    if suffix == ".pdf":
        return _html_to_pdf(source, target)
    raise ConversionError(
        f"@package cannot convert to '{suffix or target.name}'. Supported "
        "conversion target(s): .pdf."
    )


__all__ = ["ConversionError", "convert_file"]
