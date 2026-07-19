"""Reference directives, inline calls, and Claude-style path shorthand."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.compilation.directive_registry import CORE_DIRECTIVES
from weavemark.compilation.reference_artifacts import (
    format_reference_context,
    materialize_reference_appendices,
)
from weavemark.compilation.references import (
    resolve_references,
)
from weavemark.controller import (
    WeaveMarkConfig,
    WeaveMarkController,
    _reference_syntax_enabled,
    _source_declares_reference,
)


def _reader(reference: str, directory: Path) -> tuple[str, Path] | str:
    path = (directory / reference).resolve()
    if not path.is_file():
        return f"Error: file {reference!r} not found."
    return path.read_text(encoding="utf-8"), path


class _ReferenceClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.messages: list[list[dict[str, Any]]] = []

    async def complete_with_tools(self, *args: Any, **kwargs: Any) -> ToolCallResponse:
        self.messages.append(kwargs["messages"])
        return ToolCallResponse(content=self.response)


class _NestedReadClient:
    def __init__(self) -> None:
        self.loaded = ""

    async def complete_with_tools(
        self,
        *args: Any,
        tool_executor: Any,
        **kwargs: Any,
    ) -> ToolCallResponse:
        self.loaded = await tool_executor(
            "read_file",
            {"file_name": "./child.md", "reference_id": "R1"},
        )
        return ToolCallResponse(
            content=compiler_response(
                "Use [Reference R1].",
                references={"R1": "Resolved parent and child."},
            )
        )


class _MultipleNestedReadClient:
    def __init__(self) -> None:
        self.loaded: list[str] = []

    async def complete_with_tools(
        self,
        *args: Any,
        tool_executor: Any,
        **kwargs: Any,
    ) -> ToolCallResponse:
        for reference_id in ("R1", "R2"):
            self.loaded.append(
                await tool_executor(
                    "read_file",
                    {
                        "file_name": "./child.md",
                        "reference_id": reference_id,
                    },
                )
            )
        return ToolCallResponse(
            content=compiler_response(
                "Use [Reference R1] and [Reference R2].",
                references={"R1": "First.", "R2": "Second."},
            )
        )


def test_reference_syntax_lowers_block_inline_and_shorthand(tmp_path: Path) -> None:
    (tmp_path / "README").write_text("Overview.", encoding="utf-8")
    (tmp_path / "terms.md").write_text("Use widget.", encoding="utf-8")
    source = (
        "@reference terms.md keep:false\n"
        "See @reference(\"terms.md\" keep:true) and @README.\n"
    )

    result = resolve_references(
        source,
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == []
    assert result.text == "\nSee [Reference R1] and [Reference R2].\n"
    assert [(ref.id, ref.path, ref.keep) for ref in result.references] == [
        ("R1", "terms.md", True),
        ("R2", "README", True),
    ]


def test_explicit_relative_shorthand_path_is_supported(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "guide.md").write_text("Guide.", encoding="utf-8")

    result = resolve_references(
        "See @./nested/guide.md.",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == []
    assert result.text == "See [Reference R1]."
    assert result.references[0].path == "./nested/guide.md"


def test_reference_scanner_ignores_code_and_escaped_at_signs(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Overview.", encoding="utf-8")
    source = (
        "`@README.md`\n"
        "```weavemark\n"
        "@README.md\n"
        "```\n"
        "@@README.md\n"
    )

    result = resolve_references(
        source,
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.text == source
    assert result.references == []


def test_reference_scanner_ignores_multiline_code_spans(tmp_path: Path) -> None:
    (tmp_path / "guide.md").write_text("Guide.", encoding="utf-8")
    source = "`literal reference\n@guide.md\n`\nOutside @guide.md."

    result = resolve_references(
        source,
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == []
    assert result.text == "`literal reference\n@guide.md\n`\nOutside [Reference R1]."
    assert len(result.references) == 1


def test_reference_scanner_preserves_email_addresses(tmp_path: Path) -> None:
    result = resolve_references(
        "Contact dev@example.com.",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.text == "Contact dev@example.com."
    assert result.references == []
    assert result.errors == []


def test_reference_scanner_ignores_opaque_directive_bodies(tmp_path: Path) -> None:
    (tmp_path / "guide.md").write_text("Guide.", encoding="utf-8")
    source = "@note\n  @guide.md\n@embed\n  @guide.md\n"

    result = resolve_references(
        source,
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.text == source
    assert result.references == []


def test_non_reference_inline_directive_reports_surface_error(tmp_path: Path) -> None:
    result = resolve_references(
        'Make @style("formal") concise.',
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == [
        "Directive '@style' at line 1, column 6 does not support inline calls."
    ]


def test_nested_references_resolve_relative_to_containing_file(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "child.md").write_text("Child content.", encoding="utf-8")
    (nested / "parent.md").write_text(
        "Parent uses @child.md.",
        encoding="utf-8",
    )

    result = resolve_references(
        "Read @nested/parent.md.",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == []
    assert result.text == "Read [Reference R1]."
    assert result.references[0].content == "Parent uses [Reference R2]."
    assert result.references[1].content == "Child content."
    assert result.references[1].parent_id == "R1"


def test_cyclic_references_report_chain(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("@b.md", encoding="utf-8")
    (tmp_path / "b.md").write_text("@a.md", encoding="utf-8")

    result = resolve_references(
        "@a.md",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == ["Cyclic @reference detected: a.md -> b.md -> a.md."]


def test_appendix_uses_document_break_and_metadata(tmp_path: Path) -> None:
    path = tmp_path / "guide.md"
    path.write_text("Guide.", encoding="utf-8")
    resolved = resolve_references(
        "See @guide.md.",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    prompt, prompts, errors = materialize_reference_appendices(
        "See [Reference R1].",
        {"default": "See [Reference R1]."},
        resolved.references,
        {"R1": "Resolved guide."},
    )

    assert errors == []
    assert "\n\n***\n\n# Reference Appendix\n\n" in prompt
    assert "## Reference R1 — guide.md" in prompt
    assert "- Source: `guide.md`" in prompt
    assert prompt.endswith("Resolved guide.")
    assert prompts["default"] == prompt


def test_appendix_preserves_leading_reference_indentation(tmp_path: Path) -> None:
    path = tmp_path / "code.txt"
    path.write_text("    indented code\n", encoding="utf-8")
    resolved = resolve_references(
        "@code.txt",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    prompt, _, errors = materialize_reference_appendices(
        "",
        {},
        resolved.references,
        {"R1": "    indented code\n"},
    )

    assert errors == []
    assert prompt.endswith("\n\n    indented code")


def test_reference_context_exposes_scope_and_parent(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "child.md").write_text("Child.", encoding="utf-8")
    (nested / "parent.md").write_text("@child.md", encoding="utf-8")
    resolved = resolve_references(
        "@prompt stage\n  @nested/parent.md",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    context = format_reference_context(resolved.references)

    assert 'id="R1"' in context
    assert 'scope="stage"' in context
    assert 'id="R2"' in context
    assert 'parent_id="R1"' in context
    assert resolved.references[1].scope == "stage"


def test_reference_syntax_uses_only_the_actual_top_level_pragma() -> None:
    source = (
        "```weavemark\n"
        "@promplet version: 0.8\n"
        "```\n\n"
        "See @guide.md."
    )

    assert _reference_syntax_enabled(source) is True


def test_resolved_reference_preserves_leading_indentation(tmp_path: Path) -> None:
    (tmp_path / "code.md").write_text("    indented code\n", encoding="utf-8")

    resolved = resolve_references(
        "@code.md",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert resolved.errors == []
    assert resolved.references[0].content == "    indented code"


def test_declared_reads_require_file_directive_syntax() -> None:
    assert _source_declares_reference(
        "The prose mentions ./secrets.md but does not import it.",
        "./secrets.md",
    ) is False
    assert _source_declares_reference(
        "@refine ./rules.md mingle:false",
        "./rules.md",
    ) is True
    assert _source_declares_reference(
        "@embed file: ./data.md",
        "./data.md",
    ) is True


@pytest.mark.asyncio
async def test_controller_supplies_context_and_materializes_appendix(
    tmp_path: Path,
) -> None:
    (tmp_path / "guide.md").write_text(
        "# Guide\n\nUse the approved vocabulary.",
        encoding="utf-8",
    )
    client = _ReferenceClient(
        compiler_response(
            "Consult [Reference R1].",
            references={"R1": "# Guide\n\nUse the approved vocabulary."},
        )
    )

    result = await WeaveMarkController(
        WeaveMarkConfig(use_structural_helpers=True),
        client=client,
    ).compose(
        "@promplet version: 0.9\n\nConsult @guide.md.",
        base_dir=tmp_path,
    )

    assert result.errors == []
    assert result.composed_prompt.startswith("Consult [Reference R1].\n\n***\n\n")
    assert result.composed_prompt.endswith("Use the approved vocabulary.")
    assert result.references[0]["path"] == "guide.md"
    assert "reference_contents" not in result.to_dict()
    assert "Referenced Source Context" in client.messages[0][1]["content"]
    assert '<weavemark-reference id="R1"' in client.messages[0][1]["content"]


@pytest.mark.asyncio
async def test_keep_false_is_compiler_context_only(tmp_path: Path) -> None:
    (tmp_path / "terms.md").write_text("Prefer the word promplet.", encoding="utf-8")
    client = _ReferenceClient(
        compiler_response(
            "Write the release note using the approved terminology.",
            references={"R1": "Prefer the word promplet."},
        )
    )

    result = await WeaveMarkController(
        WeaveMarkConfig(),
        client=client,
    ).compose(
        "@promplet version: 0.9\n"
        "@reference terms.md keep:false\n\n"
        "Write the release note.",
        base_dir=tmp_path,
    )

    assert result.errors == []
    assert "Reference Appendix" not in result.composed_prompt
    assert result.references[0]["keep"] is False
    assert "Prefer the word promplet." in client.messages[0][1]["content"]


@pytest.mark.asyncio
async def test_named_prompt_receives_only_its_scoped_appendix(tmp_path: Path) -> None:
    (tmp_path / "stage.md").write_text("Stage context.", encoding="utf-8")
    client = _ReferenceClient(
        compiler_response(
            "",
            prompts={
                "first": "First prompt.",
                "second": "Use [Reference R1].",
            },
            references={"R1": "Resolved stage context."},
        )
    )

    result = await WeaveMarkController(
        WeaveMarkConfig(),
        client=client,
    ).compose(
        "@promplet version: 0.9\n"
        "@prompt first\n"
        "  First prompt.\n"
        "@prompt second\n"
        "  Use @stage.md.\n",
        base_dir=tmp_path,
    )

    assert result.errors == []
    assert "Reference Appendix" not in result.prompts["first"]
    assert "\n\n***\n\n# Reference Appendix" in result.prompts["second"]
    assert result.references[0]["scope"] == "second"


@pytest.mark.asyncio
async def test_same_file_is_retained_in_each_consuming_prompt(tmp_path: Path) -> None:
    (tmp_path / "shared.md").write_text("Shared.", encoding="utf-8")
    client = _ReferenceClient(
        compiler_response(
            "",
            prompts={
                "first": "Use [Reference R1].",
                "second": "Use [Reference R2].",
            },
            references={"R1": "First resolved.", "R2": "Second resolved."},
        )
    )

    result = await WeaveMarkController(WeaveMarkConfig(), client=client).compose(
        "@promplet version: 0.9\n"
        "@prompt first\n"
        "  Use @shared.md.\n"
        "@prompt second\n"
        "  Use @shared.md.\n",
        base_dir=tmp_path,
    )

    assert result.errors == []
    assert "Reference R1" in result.prompts["first"]
    assert "Reference R2" in result.prompts["second"]
    assert [reference["scope"] for reference in result.references] == [
        "first",
        "second",
    ]


@pytest.mark.asyncio
async def test_nested_declared_file_uses_reference_directory(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "child.md").write_text("Child source.", encoding="utf-8")
    (nested / "parent.weavemark.md").write_text(
        "@refine ./child.md mingle:false",
        encoding="utf-8",
    )
    client = _NestedReadClient()

    result = await WeaveMarkController(WeaveMarkConfig(), client=client).compose(
        "@promplet version: 0.9\nUse @nested/parent.weavemark.md.",
        base_dir=tmp_path,
    )

    assert result.errors == []
    assert client.loaded == "Child source."


@pytest.mark.asyncio
async def test_identical_nested_paths_use_explicit_reference_owners(
    tmp_path: Path,
) -> None:
    for folder, content in (("first", "First child."), ("second", "Second child.")):
        directory = tmp_path / folder
        directory.mkdir()
        (directory / "child.md").write_text(content, encoding="utf-8")
        (directory / "parent.weavemark.md").write_text(
            "@refine ./child.md mingle:false",
            encoding="utf-8",
        )
    client = _MultipleNestedReadClient()

    result = await WeaveMarkController(WeaveMarkConfig(), client=client).compose(
        "@promplet version: 0.9\n"
        "Use @first/parent.weavemark.md and @second/parent.weavemark.md.",
        base_dir=tmp_path,
    )

    assert result.errors == []
    assert client.loaded == ["First child.", "Second child."]


def test_top_level_reference_after_prompt_uses_default_scope(tmp_path: Path) -> None:
    (tmp_path / "shared.md").write_text("Shared.", encoding="utf-8")
    result = resolve_references(
        "@prompt first\n"
        "  Prompt body.\n"
        "@reference shared.md\n",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == []
    assert result.references[0].scope == "default"


def test_blank_lines_preserve_named_prompt_scope(tmp_path: Path) -> None:
    (tmp_path / "shared.md").write_text("Shared.", encoding="utf-8")
    result = resolve_references(
        "@prompt first\n"
        "  Prompt body.\n"
        "\n"
        "  @reference shared.md\n",
        tmp_path,
        reader=_reader,
        known_directives=CORE_DIRECTIVES,
        enabled=True,
    )

    assert result.errors == []
    assert result.references[0].scope == "first"


@pytest.mark.asyncio
async def test_version_08_keeps_inline_path_literal(tmp_path: Path) -> None:
    (tmp_path / "guide.md").write_text("Guide.", encoding="utf-8")

    result = await WeaveMarkController(WeaveMarkConfig()).compose(
        "@promplet version: 0.8\n\nSee @guide.md.",
        base_dir=tmp_path,
    )

    assert result.errors == []
    assert result.composed_prompt == "See @guide.md."
    assert result.references == []
