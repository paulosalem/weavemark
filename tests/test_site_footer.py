from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_website_pages_include_author_and_copyright_footer() -> None:
    pages = sorted((ROOT / "docs").glob("*.html"))
    assert pages

    for page in pages:
        html = page.read_text(encoding="utf-8")
        assert '<div class="footer-meta">' in html, page
        assert "WeaveMark is authored by Dr. Paulo Salem." in html, page
        assert 'href="https://www.paulosalem.com">www.paulosalem.com</a>' in html, page
        assert (
            'href="https://www.linkedin.com/in/paulosalem/">LinkedIn</a>' in html
        ), page
        assert "Copyright (c) 2026 Paulo Salem" in html, page
