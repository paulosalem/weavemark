"""Live-provider validation for semantic path and module refinement."""

from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

import pytest

from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.defaults import DEFAULT_MODEL

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set — live semantic tests require a provider",
    ),
]

_MARKER = "SOURCE_FIDELITY_MARKER_42"
_FRAGMENT_BODY = f"""
# Evidence discipline

Preserve the exact identifier `{_MARKER}`.

For every material claim:
1. distinguish verified fact from assumption;
2. state uncertainty explicitly;
3. name the evidence needed to resolve that uncertainty.
"""


def _controller() -> WeaveMarkController:
    return WeaveMarkController(
        WeaveMarkConfig(
            model=DEFAULT_MODEL,
            temperature=0.0,
        )
    )


@pytest.mark.asyncio
async def test_live_module_and_path_refinement_preserve_same_obligations(
    tmp_path: Path,
) -> None:
    library = tmp_path / "promplets"
    library.mkdir()
    fragment = library / "evidence-discipline.weavemark.md"
    fragment.write_text(
        "@promplet version: 0.7\n"
        "@module validation.evidence_discipline\n\n"
        f"{textwrap.dedent(_FRAGMENT_BODY).strip()}\n",
        encoding="utf-8",
    )
    task = """
    Prepare a concise launch-risk brief for a new developer tool.
    The output must include Findings, Uncertainties, and Next Evidence.
    """
    path_source = (
        "@refine ./promplets/evidence-discipline.weavemark.md\n\n"
        + textwrap.dedent(task).strip()
    )
    module_source = (
        "@refine module:validation.evidence_discipline\n\n"
        + textwrap.dedent(task).strip()
    )

    path_result = await _controller().compose(path_source, {}, tmp_path)
    module_result = await _controller().compose(module_source, {}, tmp_path)

    assert path_result.errors == []
    assert module_result.errors == []
    for output in (path_result.composed_prompt, module_result.composed_prompt):
        assert _MARKER in output
        assert "uncert" in output.lower()
        assert "evidence" in output.lower()
        assert "launch" in output.lower()
        assert "@refine" not in output


@pytest.mark.asyncio
async def test_live_builtin_module_refinement_is_semantically_integrated() -> None:
    source = """
    @refine module:weavemark.std.reasoning.base_analyst

    Assess whether a small company should launch a paid API beta.
    Return: Recommendation, Evidence, Uncertainties, and Next Tests.
    """

    result = await _controller().compose(
        textwrap.dedent(source).strip(),
        {},
        Path.cwd(),
    )

    assert result.errors == []
    output = result.composed_prompt.lower()
    assert "recommend" in output
    assert "evidence" in output
    assert "uncert" in output
    assert "next" in output
    assert "@refine" not in output


@pytest.mark.asyncio
async def test_live_story_example_composes_builtin_local_module_and_path() -> None:
    repo = Path(__file__).resolve().parents[1]
    example = (
        repo
        / "examples"
        / "saved-artifact-workflows"
        / "childrens-book-bebe-fusquinha"
    )
    promplet = example / "promplets" / "book-en.weavemark.md"
    variables = json.loads(
        (example / "en" / "inputs" / "vars.json").read_text(encoding="utf-8")
    )

    result = await _controller().compose(
        promplet.read_text(encoding="utf-8"),
        variables,
        promplet.parent,
    )

    assert result.errors == []
    assert {"author", "cover", "page"} <= result.prompts.keys()
    author = result.prompts["author"].lower()
    cover = result.prompts["cover"].lower()
    assert "baby bug" in author
    assert "library of questions" in author
    assert "baby bug" in cover
    assert "@refine" not in author
    assert "@refine" not in cover
