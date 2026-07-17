"""Reference-output tests for WeaveMark compilation.

These tests intentionally compare the real WeaveMark controller output against
fixed reference prompts. They are stricter than the usual E2E smoke tests: the
goal is to reveal where compilation still behaves like semantic rewriting rather
than reproducible prompt compilation.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.compilation.macros import preprocess_weavemark
from weavemark.controller import WeaveMarkConfig, WeaveMarkController
from weavemark.defaults import DEFAULT_MODEL
from weavemark.settings import DefaultModuleImport, load_weavemark_settings


def _write(path: Path, text: str) -> Path:
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")
    return path


async def _compile(spec_path: Path) -> str:
    controller = WeaveMarkController(
        WeaveMarkConfig(model=DEFAULT_MODEL, temperature=0.0)
    )
    result = await controller.compose(
        spec_path.read_text(encoding="utf-8"),
        variables={},
        base_dir=spec_path.parent,
    )
    assert result.errors == []
    return result.composed_prompt


class _FakeLLMClient:
    def __init__(self) -> None:
        self.calls = 0

    async def complete_with_tools(self, *args, **kwargs) -> ToolCallResponse:
        self.calls += 1
        return ToolCallResponse(
            content=compiler_response(
                "LLM compiled prompt.",
                analysis="LLM path used.",
            )
        )


class _CapturingFakeLLMClient:
    def __init__(self) -> None:
        self.calls = 0
        self.messages: list[Any] = []

    async def complete_with_tools(self, *args, **kwargs) -> ToolCallResponse:
        self.calls += 1
        self.messages.append(kwargs["messages"])
        return ToolCallResponse(
            content=compiler_response(
                "LLM compiled prompt.",
                analysis="LLM path used.",
            )
        )


class TestReferenceCompilation:
    """Compare easy, medium, and hard specs to exact reference outputs."""

    @pytest.mark.asyncio
    async def test_easy_refine_note_and_literal_text(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "writing-helper-base.weavemark.md",
            """
            @note
              # Writing Helper — Base Note
              This engineering note must not appear in compiled output.

            # Writing Helper

            You are a writing helper.

            Preserve final content exactly.
            """,
        )
        spec_path = _write(
            tmp_path / "writing-helper-easy.weavemark.md",
            """
            @refine ./writing-helper-base.weavemark.md mingle: false
            """,
        )

        compiled = await _compile(spec_path)

        assert compiled == (
            "# Writing Helper\n\n"
            "You are a writing helper.\n\n"
            "Preserve final content exactly."
        )

    @pytest.mark.asyncio
    async def test_refine_mingle_false_rejects_body_guidance(
        self,
        tmp_path: Path,
    ) -> None:
        _write(
            tmp_path / "writing-helper-base.weavemark.md",
            """
            # Writing Helper

            You are a writing helper.
            """,
        )
        spec_path = _write(
            tmp_path / "writing-helper-guided.weavemark.md",
            """
            @refine ./writing-helper-base.weavemark.md mingle: false
              This body is guidance for semantic mingling and must not leak.

            Preserve final content exactly.
            """,
        )

        controller = WeaveMarkController(
            WeaveMarkConfig(model=DEFAULT_MODEL, temperature=0.0)
        )
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == [
            "@refine with mingle: false cannot have an indented body. "
            "Use `with <name>: <value>` binding lines, or remove the "
            "body."
        ]
        assert result.composed_prompt == "Preserve final content exactly."
        assert "must not leak" not in result.composed_prompt
        assert result.warnings == []

    @pytest.mark.asyncio
    async def test_medium_refine_match_and_if(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "writing-helper-base.weavemark.md",
            """
            # Writing Helper

            You improve XML writing drafts.

            @match audience
              "book-reader" ==>
                Explain revisions in beginner-friendly language.
              "expert" ==>
                Use concise editorial terminology.

            @if preserve_final
              Never modify `<content status="final">` blocks.
            """,
        )
        spec_path = _write(
            tmp_path / "writing-helper-medium.weavemark.md",
            """
            @refine ./writing-helper-base.weavemark.md mingle: false

            Variables:
            - audience = book-reader
            - preserve_final = true
            """,
        )

        controller = WeaveMarkController(
            WeaveMarkConfig(model=DEFAULT_MODEL, temperature=0.0)
        )
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"audience": "book-reader", "preserve_final": True},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == (
            "# Writing Helper\n\n"
            "You improve XML writing drafts.\n\n"
            "Explain revisions in beginner-friendly language.\n\n"
            'Never modify `<content status="final">` blocks.\n\n'
            "Variables:\n"
            "- audience = book-reader\n"
            "- preserve_final = true"
        )

    @pytest.mark.asyncio
    async def test_match_wildcard_branch_with_refine_is_deterministic(
        self, tmp_path: Path
    ) -> None:
        """`_ ==> @refine ...` wins when no named branch matches.

        Regression guard: the wildcard branch must be evaluated by the
        deterministic structural helper (no LLM call), and its `@refine`
        target must be loaded with no flakiness.
        """
        _write(
            tmp_path / "default-method.weavemark.md",
            """
            ## Default Method
            MARKER_DEFAULT — wildcard refine target loaded.
            """,
        )
        spec_path = _write(
            tmp_path / "dispatcher.weavemark.md",
            """
            @promplet version: 0.6

            # Dispatcher

            @match method
              "known" ==>
                Known branch text.
              _ ==>
                @refine ./default-method.weavemark.md mingle: false
            """,
        )

        controller = WeaveMarkController(
            WeaveMarkConfig(model=DEFAULT_MODEL, temperature=0.0)
        )
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"method": "anything-not-listed"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert "MARKER_DEFAULT" in result.composed_prompt
        assert "Known branch text" not in result.composed_prompt
        assert result.tool_calls_made >= 1, (
            "Structural helper must invoke read_file for the wildcard " "@refine target"
        )

    @pytest.mark.asyncio
    async def test_match_named_branch_with_refine_does_not_load_other_branches(
        self, tmp_path: Path
    ) -> None:
        """Only the winning branch's `@refine` triggers `read_file`."""
        _write(
            tmp_path / "winner.weavemark.md",
            "MARKER_WINNER — selected branch loaded.\n",
        )
        _write(
            tmp_path / "loser.weavemark.md",
            "MARKER_LOSER — must NOT appear.\n",
        )
        spec_path = _write(
            tmp_path / "router.weavemark.md",
            """
            @promplet version: 0.6

            @match pick
              "win" ==>
                @refine ./winner.weavemark.md mingle: false
              "lose" ==>
                @refine ./loser.weavemark.md mingle: false
            """,
        )

        controller = WeaveMarkController(
            WeaveMarkConfig(model=DEFAULT_MODEL, temperature=0.0)
        )
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"pick": "win"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert "MARKER_WINNER" in result.composed_prompt
        assert "MARKER_LOSER" not in result.composed_prompt

    @pytest.mark.asyncio
    async def test_structural_assertions_are_removed_when_satisfied(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "finance-assertions.weavemark.md",
            """
            # Finance Assistant

            ## Output Format

            Show assumptions before recommendations.

            @assert section: "Output Format"
            @assert contains: "Show assumptions"
            """,
        )

        compiled = await _compile(spec_path)

        assert compiled == (
            "# Finance Assistant\n\n"
            "## Output Format\n\n"
            "Show assumptions before recommendations."
        )

    @pytest.mark.asyncio
    async def test_structural_assertion_failures_are_reported(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "finance-assertion-failure.weavemark.md",
            """
            # Finance Assistant

            @assert section: "Output Format"
            """,
        )
        client = _FakeLLMClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)
        preprocessed = preprocess_weavemark(
            spec_path.read_text(encoding="utf-8"),
            spec_path.parent,
        )
        assert [param.name for param in preprocessed.semantic_definitions["style"].params] == [
            "description",
            "body",
        ]

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.composed_prompt == "# Finance Assistant"
        assert result.errors == ["@assert failed: section: Output Format"]

    @pytest.mark.asyncio
    async def test_weavemark_variables_do_not_consume_mustache_templates(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "promplet-variable-with-mustache.weavemark.md",
            """
            # Template Bridge

            WeaveMark variable: @{name}

            Mustache template:
            {{#items}}
            - {{name}}: {{value}}
            {{/items}}
            """,
        )
        client = _FakeLLMClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"name": "Alice", "value": "ignored"},
            base_dir=spec_path.parent,
        )

        assert result.composed_prompt == (
            "# Template Bridge\n\n"
            "WeaveMark variable: Alice\n\n"
            "Mustache template:\n"
            "{{#items}}\n"
            "- {{name}}: {{value}}\n"
            "{{/items}}"
        )

    @pytest.mark.asyncio
    async def test_emit_directive_collects_multi_file_artifacts(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "prompt-pack.weavemark.md",
            """
            # Prompt Pack

            Shared authoring notes.

            @emit file: system.md
            You are a concise assistant.

            @emit file="user.md"
            Summarize @{topic}.
            """,
        )
        client = _FakeLLMClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"topic": "Mars missions"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "# Prompt Pack\n\nShared authoring notes."
        assert result.emits == {
            "system.md": "You are a concise assistant.",
            "user.md": "Summarize Mars missions.",
        }

    @pytest.mark.asyncio
    async def test_compile_directive_sets_compile_metadata(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "compiled-json.weavemark.md",
            """
            @compile format: .json

            # Prompt Pack

            Build a prompt for @{topic}.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"topic": "launch planning"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.compile == {"format": "json"}
        assert (
            result.composed_prompt
            == "# Prompt Pack\n\nBuild a prompt for launch planning."
        )

    @pytest.mark.asyncio
    async def test_compile_directive_rejects_invalid_parameters(
        self,
        tmp_path: Path,
    ) -> None:
        controller = WeaveMarkController(WeaveMarkConfig())
        cases = (
            (
                "@compile target: chat",
                "@compile only supports the format and context parameters. "
                "Unsupported parameter(s): target.",
            ),
            (
                "@compile json",
                "@compile requires key-value parameters such as format: markdown; "
                "positional arguments are not supported.",
            ),
            (
                "@compile format: pdf",
                "Unsupported @compile format: pdf. Supported formats: "
                "jinja, json, markdown, mustache.",
            ),
        )

        for source, expected_error in cases:
            result = await controller.compose(
                source,
                variables={},
                base_dir=tmp_path,
            )
            assert result.composed_prompt == ""
            assert result.compile == {}
            assert result.errors == [expected_error]

    @pytest.mark.asyncio
    async def test_emit_indented_block_preserves_following_primary_prompt(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "emit-with-primary.weavemark.md",
            """
            @emit file: prompts/system.md
              System-only instructions.

            Primary prompt content.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "Primary prompt content."
        assert result.emits == {"prompts/system.md": "System-only instructions."}

    @pytest.mark.asyncio
    async def test_emit_rejects_non_file_parameters(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "bad-emit.weavemark.md",
            """
            @emit file: system.md role: system
              System-only instructions.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.composed_prompt == ""
        assert result.emits == {}
        assert result.errors == [
            "@emit only supports the file parameter. Unsupported parameter(s): role."
        ]

    @pytest.mark.asyncio
    async def test_emit_rejects_unsafe_paths_and_duplicates(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "unsafe-emit.weavemark.md",
            """
            @emit file: ../outside.md
              Outside.

            @emit file: system.md
              First system prompt.

            @emit file: system.md
              Second system prompt.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.emits == {"system.md": "First system prompt."}
        assert result.errors == [
            "@emit file path must stay relative to the output directory: ../outside.md",
            "Duplicate emitted artifact target: system.md",
        ]

    @pytest.mark.asyncio
    async def test_role_tagged_prompt_emits_default_role_files(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "chat-pack.weavemark.md",
            """
            # Chat Pack

            Shared authoring notes.

            @prompt intro role: system
            You are a precise assistant.

            @prompt request role: user
            Summarize @{topic}.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"topic": "Mars missions"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "# Chat Pack\n\nShared authoring notes."
        assert result.emits == {
            "intro.system.md": "You are a precise assistant.",
            "request.user.md": "Summarize Mars missions.",
        }

    @pytest.mark.asyncio
    async def test_role_tagged_prompt_compiles_nested_content(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "prompt-with-structure.weavemark.md",
            """
            @prompt request role: user
              @if include_context
                Context: @{context}

              Task: @{task}

            Primary prompt content.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={
                "include_context": True,
                "context": "launch schedule",
                "task": "write the brief",
            },
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "Primary prompt content."
        assert result.emits == {
            "request.user.md": "Context: launch schedule\n\nTask: write the brief"
        }

    @pytest.mark.asyncio
    async def test_role_tagged_prompt_rejects_duplicate_targets(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "prompt-collisions.weavemark.md",
            """
            @prompt intro role: system
              First message.

            @emit file: intro.system.md
              Explicit collision.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.emits == {"intro.system.md": "First message."}
        assert result.errors == [
            "Duplicate emitted artifact target: intro.system.md",
        ]

    @pytest.mark.asyncio
    async def test_unified_prompt_mixed_roles_without_execute_errors(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "mixed-roles.weavemark.md",
            """
            @prompt with_role role: system
              Body A.

            @prompt without_role
              Body B.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.emits == {}
        assert any(
            "Mixing role-tagged and role-less" in e for e in result.errors
        ), result.errors

    @pytest.mark.asyncio
    async def test_unified_prompt_emit_extension_follows_compile_format(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "emit-json.weavemark.md",
            """
            @compile format: json

            @prompt intro role: system
              You are precise.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.emits == {"intro.system.json": "You are precise."}
        assert result.compile == {"format": "json"}

    @pytest.mark.asyncio
    async def test_compile_format_xml_is_rejected(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "emit-xml.weavemark.md",
            """
            @compile format: xml

            @prompt intro role: system
              <system>precise</system>
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == [
            "Unsupported @compile format: xml. Supported formats: "
            "jinja, json, markdown, mustache."
        ]
        assert result.emits == {"intro.system.md": "<system>precise</system>"}

    @pytest.mark.asyncio
    async def test_unified_prompt_refine_target_keeps_blocks_in_prompts(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "refine-targets.weavemark.md",
            """
            @prompt diagnose
              Identify issues.

            @prompt revise
              Produce improvement.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.emits == {}
        assert set(result.prompts.keys()) == {"diagnose", "revise"}
        assert result.prompts["diagnose"] == "Identify issues."
        assert result.prompts["revise"] == "Produce improvement."

    @pytest.mark.asyncio
    async def test_compile_context_local_in_pipeline(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "pipeline-no-cascade.weavemark.md",
            """
            @compile context: local
            @execute reflection
              max_iterations: 2

            You are an expert.

            @prompt generate
              Generate options.

            @prompt evaluate
              Score them.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.prompts["generate"] == "Generate options."
        assert result.prompts["evaluate"] == "Score them."

    @pytest.mark.asyncio
    async def test_compile_context_cascade_in_emission(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "emission-with-cascade.weavemark.md",
            """
            @compile context: cascade

            Shared preamble.

            @prompt intro role: system
              You are precise.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.emits == {
            "intro.system.md": "Shared preamble.\n\nYou are precise.",
        }

    @pytest.mark.asyncio
    async def test_compile_context_rejects_unknown_mode(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "bad-cascade.weavemark.md",
            """
            @compile context: maybe

            @prompt intro role: system
              Body.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert any("@compile context" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_hard_nested_refine_with_named_prompts(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "writing-helper-core.weavemark.md",
            """
            # Writing Helper

            You polish XML documents one safe iteration at a time.

            @tool inspect_xml
              Inspect XML for malformed tags.
              - xml: string (required) — XML document to inspect
            """,
        )
        _write(
            tmp_path / "writing-helper-style.weavemark.md",
            """
            @refine ./writing-helper-core.weavemark.md mingle: false

            Style rules:
            - Preserve the author's intent.
            - Prefer direct, concrete edits.
            """,
        )
        spec_path = _write(
            tmp_path / "writing-helper-hard.weavemark.md",
            """
            @execute single-call

            @refine ./writing-helper-style.weavemark.md mingle: false

            @prompt diagnose role: system
              Identify which XML blocks are draft, final, or suggestions.

            @prompt revise role: user
              Produce the next improved XML document.

            Final constraint:
            Never modify final content.
            """,
        )

        controller = WeaveMarkController(
            WeaveMarkConfig(model=DEFAULT_MODEL, temperature=0.0)
        )
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.tools == [
            {
                "type": "function",
                "function": {
                    "name": "inspect_xml",
                    "description": "Inspect XML for malformed tags.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "xml": {
                                "type": "string",
                                "description": "XML document to inspect",
                            }
                        },
                        "required": ["xml"],
                    },
                },
            }
        ]
        assert result.prompts == {
            "diagnose": (
                "# Writing Helper\n\n"
                "You polish XML documents one safe iteration at a time.\n\n"
                "Style rules:\n"
                "- Preserve the author's intent.\n"
                "- Prefer direct, concrete edits.\n\n"
                "Identify which XML blocks are draft, final, or suggestions.\n\n"
                "Final constraint:\n"
                "Never modify final content."
            ),
            "revise": (
                "# Writing Helper\n\n"
                "You polish XML documents one safe iteration at a time.\n\n"
                "Style rules:\n"
                "- Preserve the author's intent.\n"
                "- Prefer direct, concrete edits.\n\n"
                "Produce the next improved XML document.\n\n"
                "Final constraint:\n"
                "Never modify final content."
            ),
        }
        assert result.prompt_roles == {"diagnose": "system", "revise": "user"}

    @pytest.mark.asyncio
    async def test_structural_helpers_can_be_disabled(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "writing-helper-base.weavemark.md",
            """
            # Writing Helper

            You are a writing helper.
            """,
        )
        spec_path = _write(
            tmp_path / "writing-helper-llm-only.weavemark.md",
            """
            @refine ./writing-helper-base.weavemark.md mingle: false
            """,
        )
        client = _FakeLLMClient()
        controller = WeaveMarkController(
            WeaveMarkConfig(use_structural_helpers=False),
            client=client,
        )

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert client.calls == 1
        assert result.composed_prompt == "LLM compiled prompt."

    @pytest.mark.asyncio
    async def test_structural_helpers_preserve_mustache_and_frontmatter(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = tmp_path / "template-report.weavemark.md"
        spec_path.write_text(
            "---\n"
            "slug: templated-report\n"
            "title: Templated Report\n"
            "---\n"
            "# Report\n\n"
            "{{#items}}\n"
            "- {{name}}: {{value}}\n"
            "{{/items}}\n\n"
            "    \n"
            "Keep whitespace-only interior lines stable.\n",
            encoding="utf-8",
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.composed_prompt == (
            "---\n"
            "slug: templated-report\n"
            "title: Templated Report\n"
            "---\n"
            "# Report\n\n"
            "{{#items}}\n"
            "- {{name}}: {{value}}\n"
            "{{/items}}\n\n"
            "    \n"
            "Keep whitespace-only interior lines stable."
        )

    @pytest.mark.asyncio
    async def test_compact_define_expands_before_variables(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "macro-label.weavemark.md",
            """
            @define label(text: label text)
              Label: @{text}
              Topic: @{topic}

            @label "Urgent"
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"topic": "pricing"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "Label: Urgent\nTopic: pricing"

    @pytest.mark.asyncio
    async def test_single_text_macro_accepts_unquoted_multiword_positional(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "macro-freeform.weavemark.md",
            """
            @define label(text: text to render)
              Label: @{text}

            @label concise direct no filler
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "Label: concise direct no filler"

    @pytest.mark.asyncio
    async def test_unquoted_colon_in_freeform_positional_is_rejected(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "macro-colon.weavemark.md",
            """
            @define label(text: text to render)
              Label: @{text}

            @label tone: direct
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            base_dir=spec_path.parent,
        )

        assert result.errors == ["@label got unknown argument 'tone'."]

    @pytest.mark.asyncio
    async def test_positional_tokens_after_named_assert_parameter_are_rejected(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "assert-order.weavemark.md",
            """
            Prompt body.
            @assert severity: warning The prompt specifies a body.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            base_dir=spec_path.parent,
        )

        assert result.errors
        assert (
            "Unexpected positional token 'The' after named parameters"
            in result.errors[0]
        )

    @pytest.mark.asyncio
    async def test_long_define_supports_defaults_and_implicit_body(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "macro-wrapper.weavemark.md",
            """
            @define wrap
              @param tone default: direct
                Tone label to apply.

              @param body implicit: true mode: subspec
                Wrapped WeaveMark content.

              @body
                Tone: @{tone}

                @{body}

            @wrap
              Hello @{name}.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"name": "Alice"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "Tone: direct\n\nHello Alice."

    def test_text_mode_implicit_body_is_not_macro_expanded(
        self, tmp_path: Path
    ) -> None:
        result = preprocess_weavemark(
            textwrap.dedent("""
                @define inner()
                  EXPANDED

                @define quote
                  @param body implicit: true mode: text
                    Raw text to quote.

                  @body
                    Quoted:
                    @{body}

                @quote
                  @inner
                """).strip(),
            tmp_path,
        )

        assert result.errors == []
        assert result.text == "Quoted:\n@inner"

    def test_long_define_rejects_unknown_param_mode(self, tmp_path: Path) -> None:
        result = preprocess_weavemark(
            textwrap.dedent("""
                @define quote
                  @param body implicit: true mode: opaque
                    Raw text to quote.

                  @body
                    @{body}

                @quote
                  Text.
                """).strip(),
            tmp_path,
        )

        assert result.text == ""
        assert result.errors == [
            "@param body mode must be text, subspec, path, or promplet."
        ]

    def test_effectful_define_registers_semantic_function(
        self,
        tmp_path: Path,
    ) -> None:
        result = preprocess_weavemark(
            textwrap.dedent("""
                @define fetch
                  @phase execute
                  @scope self
                  @returns value

                  @param query
                    Search query.

                  @effect web_search read

                  @body
                    Search for @{query}.

                @fetch query: "rates" as: market_data
                """).strip(),
            tmp_path,
        )

        assert result.errors == []
        assert result.macros == []
        assert result.text == '@fetch query: "rates" as: market_data'
        assert result.semantic_definitions["fetch"].phase == "execute"
        assert result.semantic_definitions["fetch"].scope == "self"
        assert result.semantic_definitions["fetch"].returns == "value"
        assert [
            (effect.name, effect.mode)
            for effect in result.semantic_definitions["fetch"].effects
        ] == [("web_search", "read")]

    def test_effectful_define_requires_phase_and_returns(
        self,
        tmp_path: Path,
    ) -> None:
        missing_phase = preprocess_weavemark(
            textwrap.dedent("""
                @define fetch
                  @returns value
                  @effect web_search read
                  @body
                    Search.

                @fetch
                """).strip(),
            tmp_path,
        )
        missing_returns = preprocess_weavemark(
            textwrap.dedent("""
                @define fetch
                  @phase execute
                  @effect web_search read
                  @body
                    Search.

                @fetch
                """).strip(),
            tmp_path,
        )

        assert missing_phase.errors == [
            "Semantic @define fetch requires @phase compile or @phase execute."
        ]
        assert missing_returns.errors == ["Semantic @define fetch requires @returns."]

    @pytest.mark.asyncio
    async def test_execute_weave_collects_semantic_nodes_and_bindings(
        self,
        tmp_path: Path,
    ) -> None:
        helper = tmp_path / "search.py"
        helper.write_text("def search(query):\n    return []\n", encoding="utf-8")
        spec_path = _write(
            tmp_path / "weave.weavemark.md",
            """
            @define fetch
              @phase execute
              @scope self
              @returns value

              @param query
                Search query.

              @effect web_search read

              @body
                Search for @{query}.

            @bind web_search language: python from: "./search.py" symbol: search

            @execute weave scheduler: graph-strict
              allow_effects: [web_search]

            # Market Workbench

            @fetch query: "rates" as: market_data

            Use @{market_data}.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == (
            "# Market Workbench\n\n" "@{market_data}\n\n" "Use @{market_data}."
        )
        assert result.bindings == [
            {
                "name": "web_search",
                "language": "python",
                "from": "./search.py",
                "symbol": "search",
            }
        ]
        assert result.execution["type"] == "weave"
        assert result.execution["scheduler"] == "graph-strict"
        assert result.execution["allow_effects"] == ["web_search"]
        assert result.execution["nodes"][0]["as"] == "market_data"
        assert result.execution["nodes"][0]["effects"] == [
            {"name": "web_search", "mode": "read"}
        ]
        assert result.execution["plan"] == {
            "scheduler": "graph-strict",
            "order": ["market_data"],
            "levels": [["market_data"]],
        }

    @pytest.mark.asyncio
    async def test_weavemark_version_is_compile_metadata(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "versioned.weavemark.md",
            """
            @promplet version: 0.6

            # Versioned
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.compile["weavemark_version"] == "0.6"
        assert result.composed_prompt == "# Versioned"

    @pytest.mark.asyncio
    async def test_execute_weave_preserves_result_binding_shadowing(
        self,
        tmp_path: Path,
    ) -> None:
        helper = tmp_path / "search.py"
        helper.write_text("def search(query):\n    return []\n", encoding="utf-8")
        spec_path = _write(
            tmp_path / "weave-shadow.weavemark.md",
            """
            @define fetch
              @phase execute
              @scope self
              @returns value
              @effect web_search read
              @body
                Search.

            @bind web_search language: python from: "./search.py" symbol: search

            @execute weave scheduler: sequential

            @fetch as: market_data

            Use @{market_data}.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"market_data": "EXTERNAL"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "@{market_data}\n\nUse @{market_data}."

    @pytest.mark.asyncio
    async def test_execute_weave_rejects_unknown_dependencies_and_effects(
        self,
        tmp_path: Path,
    ) -> None:
        helper = tmp_path / "search.py"
        helper.write_text("def search(query):\n    return []\n", encoding="utf-8")
        spec_path = _write(
            tmp_path / "bad-weave.weavemark.md",
            """
            @define fetch
              @phase execute
              @scope self
              @returns value
              @effect web_search read
              @body
                Search.

            @bind web_search language: python from: "./search.py" symbol: search

            @execute weave scheduler: graph-strict
              allow_effects: [read_file]

            @fetch as: market_data uses: missing_snapshot
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert (
            "@execute weave node market_data uses unknown result: missing_snapshot"
            in result.errors
        )
        assert (
            "@execute weave node market_data requests effect(s) not listed in "
            "allow_effects: web_search." in result.errors
        )

    @pytest.mark.asyncio
    async def test_execute_weave_detects_dependency_cycles(
        self,
        tmp_path: Path,
    ) -> None:
        helper = tmp_path / "search.py"
        helper.write_text("def search(query):\n    return []\n", encoding="utf-8")
        spec_path = _write(
            tmp_path / "cyclic-weave.weavemark.md",
            """
            @define fetch
              @phase execute
              @scope self
              @returns value
              @effect web_search read
              @body
                Search.

            @bind web_search language: python from: "./search.py" symbol: search

            @execute weave scheduler: graph

            @fetch as: first uses: second
            @fetch as: second uses: first
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert any(
            error.startswith("@execute weave dependency cycle detected:")
            for error in result.errors
        )

    @pytest.mark.asyncio
    async def test_tool_rejects_inline_implementation_binding(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "bad-tool.weavemark.md",
            """
            @tool search impl: python
              Search.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == [
            "@tool declares only the LLM-facing schema; use @bind for helper "
            "implementations. Unsupported parameter(s): impl."
        ]

    @pytest.mark.asyncio
    async def test_module_import_namespace_and_exposing(self, tmp_path: Path) -> None:
        module_dir = tmp_path / "promplets" / "company"
        module_dir.mkdir(parents=True)
        _write(
            module_dir / "review.weavemark.md",
            """
            @module company.review

            @define checklist(body: review material)
              Checklist:
              @{body}
            """,
        )
        spec_path = _write(
            tmp_path / "use-review.weavemark.md",
            """
            @use company.review as review exposing checklist

            @review.checklist
              Namespaced item.

            @checklist
              Exposed item.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == (
            "Checklist:\n" "Namespaced item.\n\n" "Checklist:\n" "Exposed item."
        )

    def test_user_library_can_supply_custom_modules(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        user_home = tmp_path / "user-home"
        module_path = user_home / "promplets" / "voice.weavemark.md"
        module_path.parent.mkdir(parents=True)
        _write(
            module_path,
            """
            @promplet version: 0.7
            @module company.voice

            @define calm(body: source material)
              Calm rewrite:
              @{body}
            """,
        )
        monkeypatch.setattr("weavemark.promplet_library.GLOBAL_DIR", user_home)

        result = preprocess_weavemark(
            textwrap.dedent("""
            @use company.voice exposing calm

            @calm
              Rewrite the announcement.
            """).strip(),
            tmp_path,
        )

        assert result.errors == []
        assert result.text == "Calm rewrite:\nRewrite the announcement."

    def test_project_library_is_discovered_upward(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        module_path = project / "promplets" / "format.weavemark.md"
        module_path.parent.mkdir(parents=True)
        _write(
            module_path,
            """
            @promplet version: 0.7
            @module team.format

            @define brief(body: source material)
              Project library:
              @{body}
            """,
        )
        nested = project / "nested" / "work"
        nested.mkdir(parents=True)

        result = preprocess_weavemark(
            textwrap.dedent("""
            @use team.format exposing brief

            @brief
              Trim this prompt.
            """).strip(),
            nested,
        )

        assert result.errors == []
        assert result.text == "Project library:\nTrim this prompt."

    def test_configured_library_dir_supplies_modules(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        extra = project / "shared-promplets"
        module_path = extra / "review.weavemark.md"
        module_path.parent.mkdir(parents=True)
        _write(
            module_path,
            """
            @promplet version: 0.7
            @module team.review

            @define checklist(body: source material)
              Shared library:
              @{body}
            """,
        )
        (project / ".weavemark.config.json").write_text(
            json.dumps({"library_dirs": ["shared-promplets"]}),
            encoding="utf-8",
        )

        result = preprocess_weavemark(
            textwrap.dedent("""
            @use team.review exposing checklist

            @checklist
              Check invariants.
            """).strip(),
            project,
        )

        assert result.errors == []
        assert result.text == "Shared library:\nCheck invariants."

    def test_settings_parse_default_modules(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        empty_global = tmp_path / "global-weavemark.json"
        empty_user = tmp_path / "user-weavemark.json"
        empty_global.write_text("{}", encoding="utf-8")
        empty_user.write_text("{}", encoding="utf-8")
        monkeypatch.setenv("WEAVEMARK_GLOBAL_CONFIG", str(empty_global))
        monkeypatch.setenv("WEAVEMARK_USER_CONFIG", str(empty_user))

        project = tmp_path / "project"
        project.mkdir()
        (project / "weavemark.json").write_text(
            json.dumps(
                {
                    "modules": {
                        "defaults": [
                            "weavemark.prelude.semantics",
                            {
                                "name": "company.voice",
                                "alias": "voice",
                                "exposing": "calm, crisp",
                            },
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

        result = load_weavemark_settings(project)

        assert result.errors == ()
        defaults = result.settings.default_module_imports
        assert defaults.count(
            DefaultModuleImport("weavemark.prelude.semantics")
        ) == 1
        assert (
            DefaultModuleImport(
                "weavemark.prelude.presentation",
                exposing=("concise",),
            )
            in defaults
        )
        assert (
            DefaultModuleImport(
                "company.voice",
                alias="voice",
                exposing=("calm", "crisp"),
            )
            in defaults
        )

    def test_project_default_module_makes_macros_available_without_use(
        self,
        tmp_path: Path,
    ) -> None:
        project = tmp_path / "project"
        module_path = project / "promplets" / "voice.weavemark.md"
        module_path.parent.mkdir(parents=True)
        (project / "weavemark.json").write_text(
            json.dumps(
                {
                    "modules": {
                        "defaults": [
                            {"name": "company.voice", "exposing": ["calm"]}
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )
        _write(
            module_path,
            """
            @promplet version: 0.7
            @module company.voice

            @define calm(body: source material)
              Calm rewrite:
              @{body}
            """,
        )

        result = preprocess_weavemark(
            textwrap.dedent("""
            @calm
              Rewrite the announcement.
            """).strip(),
            project,
        )

        assert result.errors == []
        assert result.imports == []
        assert result.text == "Calm rewrite:\nRewrite the announcement."

    def test_explicit_exposure_of_default_module_name_reports_collision(
        self,
        tmp_path: Path,
    ) -> None:
        result = preprocess_weavemark(
            textwrap.dedent("""
            @use weavemark.prelude.semantics exposing refine

            @refine ./base.weavemark.md
            """).strip(),
            tmp_path,
        )

        assert result.text == ""
        assert result.errors == [
            "Duplicate module namespace 'weavemark.prelude.semantics': "
            "weavemark.prelude.semantics is already imported."
        ]

    def test_module_reference_returns_fragment_body(self, tmp_path: Path) -> None:
        controller = WeaveMarkController(WeaveMarkConfig())

        body = controller._read_file(
            "module:weavemark.std.reasoning.base_analyst",
            tmp_path,
        )

        assert body.startswith("# Base Analyst")
        assert "uncertainty" in body.lower()

    def test_definition_module_cannot_be_refined(self, tmp_path: Path) -> None:
        controller = WeaveMarkController(WeaveMarkConfig())

        body = controller._read_file(
            "module:weavemark.std.planning.goals",
            tmp_path,
        )

        assert body.startswith("Error:")
        assert "has no refinable body" in body
        assert "@use" in body

    @pytest.mark.asyncio
    async def test_embed_accepts_module_body_reference(self, tmp_path: Path) -> None:
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            "@embed file: module:weavemark.std.reasoning.base_analyst",
            {},
            tmp_path,
        )

        assert result.errors == []
        assert "Base Analyst" in result.composed_prompt
        assert "@module" not in result.composed_prompt

    @pytest.mark.asyncio
    async def test_fragment_alias_resolves_bare_refine_path(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        user_config = tmp_path / "user-weavemark.json"
        user_config.write_text("{}", encoding="utf-8")
        monkeypatch.setenv("WEAVEMARK_USER_CONFIG", str(user_config))
        project_root = tmp_path / "project"
        fragment_dir = project_root / "promplets" / "fragments" / "team"
        fragment_dir.mkdir(parents=True)
        (project_root / "weavemark.json").write_text(
            json.dumps({"fragments": {"aliases": {"repo": "promplets/fragments"}}}),
            encoding="utf-8",
        )
        _write(
            fragment_dir / "review.weavemark.md",
            """
            # Review Fragment

            Check @{topic}.
            """,
        )
        library_dir = project_root / "promplets" / "catalog"
        library_dir.mkdir(parents=True)
        spec_path = _write(
            library_dir / "main.weavemark.md",
            """
            @refine team/review mingle: false
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"topic": "edge cases"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "# Review Fragment\n\nCheck edge cases."

    @pytest.mark.asyncio
    async def test_fragment_alias_resolves_explicit_alias_refine_path(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        user_config = tmp_path / "user-weavemark.json"
        user_config.write_text("{}", encoding="utf-8")
        monkeypatch.setenv("WEAVEMARK_USER_CONFIG", str(user_config))
        project_root = tmp_path / "project"
        fragment_dir = project_root / "fragments" / "product"
        fragment_dir.mkdir(parents=True)
        (project_root / "weavemark.json").write_text(
            json.dumps({"fragments": {"aliases": {"repo": "fragments"}}}),
            encoding="utf-8",
        )
        _write(fragment_dir / "brief.weavemark.md", "Product brief for @{name}.")
        library_dir = project_root / "prompts"
        library_dir.mkdir()
        spec_path = _write(
            library_dir / "main.weavemark.md",
            """
            @refine repo:product/brief mingle: false
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"name": "Atlas"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "Product brief for Atlas."

    @pytest.mark.asyncio
    async def test_bare_refine_without_fragment_alias_reports_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        user_config = tmp_path / "user-weavemark.json"
        user_config.write_text("{}", encoding="utf-8")
        monkeypatch.setenv("WEAVEMARK_USER_CONFIG", str(user_config))
        _write(tmp_path / "base.weavemark.md", "Base.")
        spec_path = _write(
            tmp_path / "main.weavemark.md",
            """
            @refine base.weavemark.md mingle: false
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.composed_prompt == ""
        assert any("Bare fragment reference" in error for error in result.errors)

    @pytest.mark.asyncio
    async def test_bare_refine_with_multiple_fragment_aliases_reports_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        user_config = tmp_path / "user-weavemark.json"
        user_config.write_text("{}", encoding="utf-8")
        monkeypatch.setenv("WEAVEMARK_USER_CONFIG", str(user_config))
        (tmp_path / "weavemark.json").write_text(
            json.dumps(
                {
                    "fragments": {
                        "aliases": {
                            "repo": "fragments",
                            "team": "team-fragments",
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        spec_path = _write(
            tmp_path / "main.weavemark.md",
            """
            @refine product/brief mingle: false
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.composed_prompt == ""
        assert any("is ambiguous; use alias:path" in error for error in result.errors)

    @pytest.mark.asyncio
    async def test_include_inserts_reusable_spec_module(self, tmp_path: Path) -> None:
        module_dir = tmp_path / "promplets" / "company" / "agent"
        module_dir.mkdir(parents=True)
        _write(
            module_dir / "reviewer.weavemark.md",
            """
            @module company.agent.reviewer

            You are a careful program reviewer.

            @define marker(text: marker text)
              Marker: @{text}

            @marker READY
            """,
        )
        spec_path = _write(
            tmp_path / "include-reviewer.weavemark.md",
            """
            @use company.agent.reviewer as reviewer

            @include reviewer

            Review the diff.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == (
            "You are a careful program reviewer.\n\n"
            "Marker: READY\n\n"
            "Review the diff."
        )

    @pytest.mark.asyncio
    async def test_define_cycle_fails_before_composition(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "cycle.weavemark.md",
            """
            @define a()
              @b

            @define b()
              @a

            @a
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.composed_prompt == ""
        assert any("Cycle detected in @define" in error for error in result.errors)

    @pytest.mark.asyncio
    async def test_builtin_presentation_module_expands(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "presentation.weavemark.md",
            """
            @weavemark.prelude.presentation.concise
              Explain the migration plan.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == (
            "Presentation constraints:\n"
            "- Be concise, direct, and high-signal.\n"
            "- Remove filler and avoid unnecessary preamble.\n\n"
            "Explain the migration plan."
        )

    @pytest.mark.asyncio
    async def test_standard_library_style_block_shape(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "std-style-block.weavemark.md",
            """
            @style "For senior engineers: crisp, direct, no filler."
            """,
        )
        client = _FakeLLMClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "LLM compiled prompt."
        assert client.calls == 1
        assert "Style constraints:" not in result.composed_prompt

    @pytest.mark.asyncio
    async def test_standard_library_revise_and_normalize_target_body_shape(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "std-revise-normalize.weavemark.md",
            """
            @revise "Remove contradictions." mode: editorial
              Draft prompt text.

            @normalize "Use consistent terminology." scope: semantic intensity: medium
              Draft prompt text.
            """,
        )
        preprocessed = preprocess_weavemark(
            spec_path.read_text(encoding="utf-8"),
            spec_path.parent,
        )

        assert [
            param.name for param in preprocessed.semantic_definitions["revise"].params
        ] == [
            "instruction",
            "mode",
            "body",
        ]
        assert [
            param.name for param in preprocessed.semantic_definitions["normalize"].params
        ] == [
            "guidance",
            "scope",
            "headings",
            "lists",
            "terminology",
            "intensity",
            "body",
        ]

    @pytest.mark.asyncio
    async def test_standard_library_polish_target_body_shape(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "std-polish.weavemark.md",
            """
            @polish "Harmonize duplicated sections without adding or removing information."
              Draft prompt text.
            """,
        )
        preprocessed = preprocess_weavemark(
            spec_path.read_text(encoding="utf-8"),
            spec_path.parent,
        )

        assert [
            param.name for param in preprocessed.semantic_definitions["polish"].params
        ] == [
            "guidance",
            "body",
        ]

    @pytest.mark.asyncio
    async def test_standard_library_output_inline_shape(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "std-output-inline.weavemark.md",
            """
            @output "Return JSON only."
            """,
        )
        client = _FakeLLMClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        # @output is a core directive resolved by structural helpers — no LLM call.
        assert client.calls == 0
        assert "Return JSON only." in result.composed_prompt
        assert result.prompt_outputs["default"].type == "text"

    @pytest.mark.asyncio
    async def test_standard_library_expand_block_shape(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "std-expand-block.weavemark.md",
            """
            @expand mode: intention length: 70% cap: 1200 focus: "interface implications"
              best bank app no fees Brazil
            """,
        )
        client = _CapturingFakeLLMClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "LLM compiled prompt."
        assert client.calls == 1
        assert "Expand the following material" not in result.composed_prompt
        composition_prompt = client.messages[0][1]["content"]
        assert "focus[mode=text] default=" in composition_prompt
        assert "interface implications" in composition_prompt

    @pytest.mark.asyncio
    async def test_refine_body_guidance_reaches_llm_semantic_contract(
        self,
        tmp_path: Path,
    ) -> None:
        _write(
            tmp_path / "base.weavemark.md",
            """
            # Base

            Use careful review.
            """,
        )
        spec_path = _write(
            tmp_path / "guided-refine.weavemark.md",
            """
            @refine ./base.weavemark.md
              Apply the refinement only to validation behavior.

            Build the final prompt.
            """,
        )
        client = _CapturingFakeLLMClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "LLM compiled prompt."
        assert client.calls == 1
        composition_prompt = client.messages[0][1]["content"]
        assert "body[mode=subspec] implicit" in composition_prompt
        assert "Apply the refinement only to validation behavior." in composition_prompt
        assert "compiler-facing guidance" in composition_prompt

    @pytest.mark.asyncio
    async def test_refined_child_file_can_define_macros(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "child.weavemark.md",
            """
            @define tag(text: tag text)
              Tag: @{text}

            @tag child
            """,
        )
        spec_path = _write(
            tmp_path / "parent.weavemark.md",
            """
            @refine ./child.weavemark.md mingle: false

            Parent: @{topic}
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={"topic": "macro expansion"},
            base_dir=spec_path.parent,
        )

        assert result.errors == []
        assert result.composed_prompt == "Tag: child\n\nParent: macro expansion"


class _ConfigurableFakeLLMClient:
    """Fake LLM client that returns a caller-supplied XML body verbatim."""

    def __init__(self, xml_body: str) -> None:
        self.calls = 0
        self._xml_body = xml_body

    async def complete_with_tools(self, *args, **kwargs) -> ToolCallResponse:
        self.calls += 1
        return ToolCallResponse(content=self._xml_body)


class TestLLMFallbackCascade:
    """LLM-fallback path honours the unified disposition + cascade rules."""

    @pytest.mark.asyncio
    async def test_llm_fallback_emission_disposition_skips_cascade(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "emit.weavemark.md",
            """
            Shared preamble.

            @prompt intro role: system
              You are precise.
            """,
        )
        response_body = compiler_response(
            "Shared preamble.",
            prompts={"intro": "You are precise."},
            emits={"intro.system.md": "You are precise."},
            analysis="LLM emission path.",
        )
        client = _ConfigurableFakeLLMClient(response_body)
        controller = WeaveMarkController(
            WeaveMarkConfig(use_structural_helpers=False),
            client=client,
        )

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        # Emits is populated and no explicit override → cascade OFF.
        # Named prompt must NOT have the shared preamble prepended.
        assert result.prompts == {"intro": "You are precise."}
        assert result.emits == {"intro.system.md": "You are precise."}

    @pytest.mark.asyncio
    async def test_llm_fallback_respects_cascade_override_off(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "pipeline.weavemark.md",
            """
            @compile context: local
            @execute reflection
            Shared preamble.

            @prompt generate
              Produce the answer.
            @prompt critique role: system
              Review the answer.
            """,
        )
        response_body = compiler_response(
            "Shared preamble.",
            prompts={
                "generate": "Produce the answer.",
                "critique": "Review the answer.",
            },
            compile={"context": "local"},
            execution={"plan": "reflection"},
            analysis="LLM pipeline path.",
        )
        client = _ConfigurableFakeLLMClient(response_body)
        controller = WeaveMarkController(
            WeaveMarkConfig(use_structural_helpers=False),
            client=client,
        )

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        # Override explicitly OFF → named prompts left unmodified.
        assert result.prompts == {
            "generate": "Produce the answer.",
            "critique": "Review the answer.",
        }

    @pytest.mark.asyncio
    async def test_llm_fallback_respects_cascade_override_on_for_emission(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "emit-with-cascade.weavemark.md",
            """
            @compile context: cascade
            Shared preamble.

            @prompt intro role: system
              You are precise.
            """,
        )
        response_body = compiler_response(
            "Shared preamble.",
            prompts={"intro": "You are precise."},
            emits={"intro.system.md": "You are precise."},
            compile={"context": "cascade"},
            analysis="LLM emission with cascade.",
        )
        client = _ConfigurableFakeLLMClient(response_body)
        controller = WeaveMarkController(
            WeaveMarkConfig(use_structural_helpers=False),
            client=client,
        )

        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )

        # Override explicitly ON for emission → shared preamble prepended
        # to named prompts even though emits is populated.
        assert result.prompts == {
            "intro": "Shared preamble.\n\nYou are precise.",
        }


class TestRoleFormat:
    """role:/format: parsing, validation, and filename composition."""

    @pytest.mark.asyncio
    async def test_role_only_emits_simple_filename(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: system
              You are precise.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {"foo.system.md": "You are precise."}

    @pytest.mark.asyncio
    async def test_role_and_format_appends_after_role(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: user format: mustache
              Hello {{name}}.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {"foo.user.mustache.md": "Hello {{name}}."}

    @pytest.mark.asyncio
    async def test_prompt_format_matching_compile_format_collapses(
        self,
        tmp_path: Path,
    ) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @compile format: markdown

            @prompt foo role: user format: markdown
              Markdown content.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {"foo.user.md": "Markdown content."}

    @pytest.mark.asyncio
    async def test_dotted_name_prepends_variant_before_role(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo.fallback role: system
              Fallback prompt.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {"foo.fallback.system.md": "Fallback prompt."}

    @pytest.mark.asyncio
    async def test_dotted_name_and_format_combined(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo.fallback role: system format: mustache
              Combined slots.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {
            "foo.fallback.system.mustache.md": "Combined slots.",
        }

    @pytest.mark.asyncio
    async def test_parameter_order_is_free(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo.fallback format: mustache role: system
              Free order.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {
            "foo.fallback.system.mustache.md": "Free order.",
        }

    @pytest.mark.asyncio
    async def test_dotted_name_and_format(self, tmp_path: Path) -> None:
        (tmp_path / "weavemark.json").write_text(
            json.dumps({"formats": {"jinja.v2": {"extension": "jinja.v2"}}}),
            encoding="utf-8",
        )
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo.experimental role: user format: jinja.v2
              Dotted variants.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {
            "foo.experimental.user.jinja.v2.md": "Dotted variants.",
        }

    @pytest.mark.asyncio
    async def test_format_json_with_dotted_name_and_prompt_format(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "weavemark.json").write_text(
            json.dumps({"formats": {"jinja.v2": {"extension": "jinja.v2"}}}),
            encoding="utf-8",
        )
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @compile format: json

            @prompt foo.experimental role: user format: jinja.v2
              {"key": "value"}
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {
            "foo.experimental.user.jinja.v2.json": '{"key": "value"}',
        }

    @pytest.mark.asyncio
    async def test_role_case_insensitive(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: SYSTEM
              upper-case role.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {"foo.system.md": "upper-case role."}

    @pytest.mark.asyncio
    async def test_invalid_role_plain_error(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: bogus
              not a real role.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any("invalid role 'bogus'" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_qualifier_parameter_is_not_supported(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: system qualifier: fallback
              Unsupported parameter.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any(
            "unknown parameter 'qualifier'" in e for e in result.errors
        ), result.errors

    @pytest.mark.asyncio
    async def test_prompt_format_without_role_rejected(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo format: mustache
              No role.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any(
            "format:" in e and "requires role:" in e for e in result.errors
        ), result.errors

    @pytest.mark.asyncio
    async def test_duplicate_role_rejected(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: system role: user
              Duplicate.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any(
            "duplicate parameter 'role'" in e for e in result.errors
        ), result.errors

    @pytest.mark.asyncio
    async def test_missing_role_value_rejected(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role:
              Missing value.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any(
            "missing value for 'role'" in e for e in result.errors
        ), result.errors

    @pytest.mark.asyncio
    async def test_unknown_parameter_rejected(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: system unknown: value
              Unknown parameter.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any(
            "unknown parameter 'unknown'" in e for e in result.errors
        ), result.errors

    @pytest.mark.asyncio
    async def test_stray_token_rejected(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: system extra_token
              Stray token.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any("unexpected token" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_prompt_format_leading_dot_rejected(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: system format: .bad
              Leading dot.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any("invalid format" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_prompt_format_consecutive_dots_rejected(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo role: system format: bad..dot
              Consecutive dots.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any("invalid format" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_emission_name_consecutive_dots_rejected(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt foo..fallback role: system
              Consecutive dots.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any("safe dotted identifier" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_prompt_format_rejected_with_execute(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @execute reflection
            @prompt foo role: system format: mustache
              Pipeline block.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any("emission-only parameter" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_case_insensitive_filename_collision_detected(
        self, tmp_path: Path
    ) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt FOO role: system
              first.

            @prompt foo role: system
              second.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert any("case-insensitive" in e for e in result.errors), result.errors

    @pytest.mark.asyncio
    async def test_all_four_roles_accepted(self, tmp_path: Path) -> None:
        spec_path = _write(
            tmp_path / "spec.weavemark.md",
            """
            @prompt a role: system
              a body.

            @prompt b role: user
              b body.

            @prompt c role: assistant
              c body.

            @prompt d role: tool
              d body.
            """,
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(
            spec_path.read_text(encoding="utf-8"),
            variables={},
            base_dir=spec_path.parent,
        )
        assert result.errors == []
        assert result.emits == {
            "a.system.md": "a body.",
            "b.user.md": "b body.",
            "c.assistant.md": "c body.",
            "d.tool.md": "d body.",
        }
