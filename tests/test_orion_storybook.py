"""Contracts for the lightweight Orion storybook demo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
DEMO = ROOT / "outputs" / "implementations" / "orion-storybook"


def test_orion_storybook_has_complete_lightweight_pages() -> None:
    pages = sorted((DEMO / "pages").glob("page-*.jpg"))

    assert len(pages) == 12
    assert all(path.stat().st_size < 400_000 for path in pages)
    assert sum(path.stat().st_size for path in pages) < 3_000_000


def test_orion_storybook_exposes_result_and_provenance() -> None:
    html = (DEMO / "index.html").read_text(encoding="utf-8")
    script = (DEMO / "reader.js").read_text(encoding="utf-8")
    css = (DEMO / "styles.css").read_text(encoding="utf-8")

    for label in ("Promplet", "Tutorial", "Compiled chain"):
        assert f">{label}</a>" in html
    assert "Orion and the Hunt for His Spark" in html
    assert "const pages = [" in script
    assert script.count("alt:") == 12
    assert script.count("caption:") == 12
    assert "[hidden]" in css
    assert "display: none !important;" in css
