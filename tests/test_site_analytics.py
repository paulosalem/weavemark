"""GA4 coverage and privacy contracts for the published documentation site."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs"
ANALYTICS_SCRIPT = '<script src="analytics.js?v=20260720" defer></script>'


def test_every_documentation_page_loads_central_analytics_module() -> None:
    pages = sorted(DOCS.glob("*.html"))
    assert pages

    for page in pages:
        html = page.read_text(encoding="utf-8")
        assert html.count(ANALYTICS_SCRIPT) == 1, page
        assert "G-LS8DP9R5KX" not in html, page


def test_analytics_module_is_consent_first_and_disables_ad_signals() -> None:
    source = (DOCS / "analytics.js").read_text(encoding="utf-8")

    assert 'const MEASUREMENT_ID = "G-LS8DP9R5KX"' in source
    assert '"paulosalem.github.io"' in source
    assert "window.localStorage.getItem(CONSENT_KEY)" in source
    assert 'consent === "granted"' in source
    assert "allow_google_signals: false" in source
    assert "allow_ad_personalization_signals: false" in source
    assert "www.googletagmanager.com/gtag/js" in source
    assert "Allow analytics" in source
    assert "Analytics preferences" in source
    assert '"analytics-preview"' in source


def test_pages_build_contains_analytics_module(tmp_path: Path) -> None:
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(
        "pages_builder_for_analytics",
        ROOT / "scripts" / "build_pages_site.py",
    )
    assert spec is not None and spec.loader is not None
    builder = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = builder
    spec.loader.exec_module(builder)

    destination = tmp_path / "site"
    builder.build_site(destination, ROOT)

    assert (destination / "docs" / "analytics.js").is_file()
    assert builder.validate_site(destination) == []
