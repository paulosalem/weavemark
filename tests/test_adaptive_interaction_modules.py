"""Contracts for reusable adaptive interaction modules."""

from __future__ import annotations

from pathlib import Path

import pytest

from weavemark.api import compile_file
from weavemark.tui.scanner import scan_spec

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "promplets/domains/programming/fragments/modules"


@pytest.mark.parametrize(
    ("filename", "module_name", "obligations"),
    [
        (
            "module-adaptive-workspace-shell.weavemark.md",
            "weavemark.domains.programming.modules.adaptive_workspace_shell",
            (
                "setup",
                "slim sticky",
                "mutually exclusive drawer",
                "Restore prior focus",
                "320 CSS-pixel",
            ),
        ),
        (
            "module-focus-preserving-inspection.weavemark.md",
            "weavemark.domains.programming.modules.focus_preserving_inspection",
            (
                "semantic disclosure",
                "original spatial position",
                "MUST NOT auto-open",
                "focus layout",
                "scroll-linked restoration",
            ),
        ),
    ],
)
@pytest.mark.asyncio
async def test_adaptive_interaction_module_contract(
    filename: str,
    module_name: str,
    obligations: tuple[str, ...],
) -> None:
    path = MODULES / filename
    source = path.read_text(encoding="utf-8")

    metadata = scan_spec(source)
    result = await compile_file(path)

    assert metadata.module_name == module_name
    assert result.errors == []
    for obligation in obligations:
        assert obligation in source
