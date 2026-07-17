"""Regression tests for qualified public-release claims."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _collapsed(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))


def test_reuse_claim_describes_propagation_not_guaranteed_improvement() -> None:
    readme = _collapsed(ROOT / "README.md")
    tutorial = _collapsed(ROOT / "docs" / "tutorial-reuse.html")

    assert "every promplet that refines it improves" not in readme
    assert "every promplet that refines it improves" not in tutorial
    assert "picks up the new guidance" in readme
    assert "model- and run-dependent" in readme


def test_template_claim_is_scoped_to_ordinary_templating() -> None:
    tutorial = _collapsed(ROOT / "docs" / "tutorial-directives.html")

    assert "impossible for a template engine" not in tutorial
    assert "beyond ordinary variable-substitution" in tutorial


def test_implementation_claims_are_traceable_not_sandboxed_or_reproducible() -> None:
    tutorial = _collapsed(ROOT / "docs" / "tutorial-implement.html")

    assert "its own sandbox" not in tutorial
    assert "implementation is reproducible" not in tutorial
    assert "for reproducibility" not in tutorial
    assert "proves the loop" not in tutorial
    assert "not an operating-system security sandbox" in tutorial
    assert "making the run traceable" in tutorial
    assert "demonstrates one successful end-to-end run" in tutorial


def test_study_headline_is_explicitly_exploratory() -> None:
    markdown = (
        ROOT / "studies" / "controlled-studies" / "results.md"
    ).read_text(encoding="utf-8")
    html = (
        ROOT / "studies" / "controlled-studies" / "results.html"
    ).read_text(encoding="utf-8")

    for text in (markdown, html):
        assert "9 wins" not in text
        assert "0 losses" not in text
        assert "Why WeaveMark wins" not in text
        assert "single-output studies in this corpus" in text
        assert "positive deltas" in text
