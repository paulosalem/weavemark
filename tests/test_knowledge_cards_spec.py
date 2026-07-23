"""Contracts for the Knowledge Cards source and compiled specification."""

from __future__ import annotations

import json
import re
from pathlib import Path

from weavemark.tui.scanner import scan_spec

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "promplets" / "catalog" / "standalone" / "knowledge-cards.weavemark.md"
VARS = SOURCE.with_name("knowledge-cards.vars.json")
COMPILED = (
    ROOT / "outputs" / "implementations" / "knowledge-cards" / "compiled-spec.md"
)


def test_knowledge_cards_source_is_concise_and_parameterized() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    variables = json.loads(VARS.read_text(encoding="utf-8"))

    assert scan_spec(source).title == "Knowledge Cards"
    assert len(source.splitlines()) < 110
    assert source.count("@refine module:") == 7
    assert "@{topics}" in source
    assert "@{cards_per_pack}" in source
    assert variables["cards_per_pack"] == 50
    assert "document/main window MUST be the only vertical scroll container" in source
    assert "MUST NOT use an internal scroll pane" in source
    assert variables["topics"] == [
        "Banking Industry and Central Banks",
        "Economics",
        "Children Rearing, Development and Care",
        "Personal Investments for Total Beginners",
    ]


def test_compiled_knowledge_cards_spec_is_implementation_ready() -> None:
    compiled = COMPILED.read_text(encoding="utf-8")

    headings = [
        "## Product promise, learning model, and non-goals",
        "## Static architecture, mobile shell, and offline lifecycle",
        "## Pack convention, schemas, discovery, and build-time validation",
        "## Knowledge-card model, curriculum rules, and example-pack requirements",
        "## Feed ordering, interactions, notes, progress, and attention safeguards",
        "## IndexedDB state, export/import, privacy, and recovery",
        "## Interface states, accessibility, responsive behavior, and visual direction",
        "## File tree, implementation sequence, tests, and acceptance criteria",
    ]
    assert compiled.startswith("# Knowledge Cards\n")
    assert re.findall(r"^## .+$", compiled, re.MULTILINE) == headings

    for obligation in (
        "Each pack MUST contain exactly 50 cards",
        "content/packs/<pack-id>/",
        "content/packs/index.json",
        "source_refs",
        "0.50 * importance",
        "10 cards or 10 minutes",
        "IndexedDB",
        "document/main window MUST be the only vertical scroll container",
        "MUST NOT use an internal scroll pane",
        "no runtime LLM calls",
        "320 CSS pixels",
        "outputs/implementations/knowledge-cards/",
    ):
        assert obligation in compiled

    assert "Next.js" not in compiled
    assert "Prisma" not in compiled
    assert "WebSocket" not in compiled
