"""Tests for the standard-library ``@iterate`` compile effect."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.compilation.iterate import (
    find_iterate_directives,
    find_next_compilation_step,
    replace_applications,
    source_for_applications,
)
from weavemark.compilation.macros import preprocess_weavemark
from weavemark.controller import (
    WeaveMarkConfig,
    WeaveMarkController,
    parse_composition_response,
)


def _xml_prompt(prompt: str, directives: list[dict[str, Any]] | None = None) -> str:
    return compiler_response(prompt, directives=directives)


class _StepIterateClient:
    def __init__(
        self,
        step_outputs: list[str],
        judgments: list[dict[str, Any]],
    ) -> None:
        self.step_outputs = step_outputs
        self.judgments = judgments
        self.complete_calls: list[Any] = []
        self.complete_with_tools_calls: list[Any] = []

    async def complete(self, *args: Any, **kwargs: Any) -> str:
        self.complete_calls.append((args, kwargs))
        if not self.judgments:
            raise AssertionError("Unexpected step judgment call.")
        return json.dumps(self.judgments.pop(0))

    async def complete_with_tools(self, *args: Any, **kwargs: Any) -> ToolCallResponse:
        self.complete_with_tools_calls.append((args, kwargs))
        if not self.step_outputs:
            raise AssertionError("Unexpected step compilation call.")
        return ToolCallResponse(content=_xml_prompt(self.step_outputs.pop(0)))


class _AskPreludeClient(_StepIterateClient):
    def __init__(self) -> None:
        super().__init__(step_outputs=[], judgments=[])
        self.ask_tool_seen = False

    async def complete_with_tools(self, *args: Any, **kwargs: Any) -> ToolCallResponse:
        self.complete_with_tools_calls.append((args, kwargs))
        ask_already_seen = self.ask_tool_seen
        tool_names = {
            tool["function"]["name"]
            for tool in kwargs["tools"]
            if isinstance(tool, dict) and "function" in tool
        }
        self.ask_tool_seen = self.ask_tool_seen or "ask_user" in tool_names
        if "ask_user" in tool_names and not ask_already_seen:
            answer = await kwargs["tool_executor"](
                "ask_user",
                {
                    "question": "Who is the audience?",
                    "question_type": "clarifying question",
                    "detail_level": "40%",
                    "scope": "iteration target",
                    "reason": "Audience changes the target.",
                },
            )
            assert "Enterprise buyers" in answer
            return ToolCallResponse(
                content=_xml_prompt("Draft a launch plan for enterprise buyers.")
            )
        if "ask_user" in tool_names:
            return ToolCallResponse(
                content=_xml_prompt("Draft a launch plan for enterprise buyers.")
            )
        return await super().complete_with_tools(*args, **kwargs)


def _preprocess(spec: str, tmp_path: Path) -> tuple[str, dict[str, Any]]:
    preprocessed = preprocess_weavemark(textwrap.dedent(spec).strip(), tmp_path)
    assert preprocessed.errors == []
    return preprocessed.text, preprocessed.semantic_definitions


class TestIterateParsing:
    def test_finds_active_iterates_innermost_first(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            @iterate 2
              Outer body.
              @iterate 1
                Inner body.
            """,
            tmp_path,
        )

        directives, errors = find_iterate_directives(spec, semantics)

        assert errors == []
        assert [directive.line_number for directive in directives] == [3, 1]
        assert [directive.turns for directive in directives] == [1, 2]

    def test_iterate_number_is_optional(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            @iterate
              Draft the plan.
            """,
            tmp_path,
        )

        directives, errors = find_iterate_directives(spec, semantics)

        assert errors == []
        assert directives[0].turns is None

    def test_named_turns_are_rejected(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            @iterate turns: 2
              Draft the plan.
            """,
            tmp_path,
        )

        directives, errors = find_iterate_directives(spec, semantics)

        assert directives == []
        assert errors == [
            "@iterate at line 1 does not accept named options; use a single "
            "optional integer, e.g. @iterate 3."
        ]

    def test_non_integer_budget_is_rejected(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            @iterate "polish this"
              Draft the plan.
            """,
            tmp_path,
        )

        directives, errors = find_iterate_directives(spec, semantics)

        assert directives == []
        assert errors == [
            "@iterate at line 1 has invalid turns 'polish this'; expected an "
            "integer greater than 0."
        ]

    def test_extracts_leading_ask_wrapper_as_target(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            @iterate 2
              @ask clarifying question detail_level: 40%
                Draft the plan.
            """,
            tmp_path,
        )

        directives, errors = find_iterate_directives(spec, semantics)

        assert errors == []
        directive = directives[0]
        assert directive.ask_prelude is not None
        assert directive.ask_prelude.name == "ask"
        assert directive.target_body == "Draft the plan."

    def test_ask_wrapper_must_be_only_top_level_child(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            @iterate 2
              @ask clarifying question
                Draft the plan.

              Extra sibling text.
            """,
            tmp_path,
        )

        directives, errors = find_iterate_directives(spec, semantics)

        assert directives == []
        assert errors == [
            "@iterate at line 1 uses a leading @ask wrapper; that wrapper must "
            "be the only top-level child of @iterate."
        ]


class TestStepDiscovery:
    def test_finds_innermost_directive_before_parent(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            @revise "Improve this." mode: editorial
              Target:
              @expand mode: intention
                compact idea
            """,
            tmp_path,
        )

        step = find_next_compilation_step(spec, semantics)

        assert [application.name for application in step] == ["expand"]
        assert source_for_applications(spec, step) == (
            "@expand mode: intention\n  compact idea"
        )

    def test_groups_contiguous_sibling_directives(self, tmp_path: Path) -> None:
        spec, semantics = _preprocess(
            """
            Intro.
            @expand mode: intention
              compact idea
            @style "For engineers: crisp."
            Outro.
            """,
            tmp_path,
        )

        step = find_next_compilation_step(spec, semantics)

        assert [application.name for application in step] == ["expand", "style"]
        replaced = replace_applications(spec, step, "Grouped result.")
        assert replaced == "Intro.\nGrouped result.\nOutro."


class TestIterateExecution:
    @pytest.mark.asyncio
    async def test_iterate_reruns_step_from_judge_feedback(
        self, tmp_path: Path
    ) -> None:
        client = _StepIterateClient(
            step_outputs=["Thin expansion.", "Rich expansion."],
            judgments=[
                {
                    "needs_improvement": True,
                    "good_points": ["The first result stays on topic."],
                    "bad_points": ["It is too thin."],
                    "suggestions": ["Add concrete implications."],
                    "compliance_notes": ["Keep mode: intention."],
                    "constraint_findings": [],
                    "directive_feedback": {"app-2-expand": ["Improve specificity."]},
                },
                {
                    "needs_improvement": False,
                    "good_points": ["The result is now rich and concrete."],
                    "bad_points": [],
                    "suggestions": [],
                    "compliance_notes": ["Still complies with mode: intention."],
                    "constraint_findings": [],
                    "directive_feedback": {},
                },
            ],
        )
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)
        events: list[tuple[str, dict[str, Any]]] = []
        spec = textwrap.dedent("""
            @iterate 2
              @expand mode: intention
                compact idea
            """).strip()

        result = await controller.compose(
            spec,
            base_dir=tmp_path,
            on_event=lambda name, data: events.append((name, data)),
        )

        assert result.errors == []
        assert result.composed_prompt == "Rich expansion."
        assert len(client.complete_with_tools_calls) == 2
        assert len(client.complete_calls) == 2
        assert result.compilation_trace is not None
        assert [step.iteration for step in result.compilation_trace.steps] == [0, 1, 2]
        improved_prompt = client.complete_with_tools_calls[1][1]["messages"][1][
            "content"
        ]
        assert "Judge bad points to fix" in improved_prompt
        assert "It is too thin." in improved_prompt
        assert "Keep mode: intention." in improved_prompt
        improve_events = [
            data for name, data in events if name == "iterate_improve"
        ]
        assert improve_events[0]["unmet_points"] == ["It is too thin."]

    @pytest.mark.asyncio
    async def test_iterate_exhaustion_warns_and_returns_best_result(
        self, tmp_path: Path
    ) -> None:
        client = _StepIterateClient(
            step_outputs=["Thin expansion.", "Richer but still flawed."],
            judgments=[
                {
                    "needs_improvement": True,
                    "good_points": ["On topic."],
                    "bad_points": ["Still incomplete."],
                    "suggestions": ["Add edge cases."],
                    "compliance_notes": ["Respect original mode."],
                    "constraint_findings": [],
                    "directive_feedback": {},
                }
            ],
        )
        controller = WeaveMarkController(
            WeaveMarkConfig(max_iterate_turns=1),
            client=client,
        )
        spec = textwrap.dedent("""
            @iterate 1
              @expand mode: intention
                compact idea
            """).strip()

        result = await controller.compose(spec, base_dir=tmp_path)

        assert result.errors == []
        assert result.composed_prompt == "Richer but still flawed."
        assert result.warnings == [
            "@iterate at line 1 reached its improvement budget after 1 iteration(s); "
            "returning the best available result even though at least one "
            "compilation step still had material improvement opportunities."
        ]
        assert result.compilation_trace is not None
        assert any(step.needs_improvement for step in result.compilation_trace.steps)

    @pytest.mark.asyncio
    async def test_plain_body_without_directives_converges_without_llm_judge(
        self, tmp_path: Path
    ) -> None:
        client = _StepIterateClient(step_outputs=[], judgments=[])
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)
        spec = textwrap.dedent("""
            @iterate 3
              Mention cats.
            """).strip()

        result = await controller.compose(spec, base_dir=tmp_path)

        assert result.errors == []
        assert result.composed_prompt == "Mention cats."
        assert client.complete_calls == []
        assert client.complete_with_tools_calls == []

    @pytest.mark.asyncio
    async def test_assertion_failures_feed_step_judgment(
        self, tmp_path: Path
    ) -> None:
        client = _StepIterateClient(
            step_outputs=["Thin expansion.", "Required phrase with richer detail."],
            judgments=[
                {
                    "needs_improvement": True,
                    "good_points": ["The output is topical."],
                    "bad_points": ["It failed a constraint."],
                    "suggestions": ["Include the required phrase."],
                    "compliance_notes": ["Respect the original expand mode."],
                    "constraint_findings": ["@assert failed: contains: Required phrase"],
                    "directive_feedback": {},
                },
                {
                    "needs_improvement": False,
                    "good_points": ["The constraint is satisfied."],
                    "bad_points": [],
                    "suggestions": [],
                    "compliance_notes": [],
                    "constraint_findings": [],
                    "directive_feedback": {},
                },
            ],
        )
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)
        spec = textwrap.dedent("""
            @iterate 2
              @expand mode: intention
                compact idea
              @assert contains: "Required phrase"
            """).strip()

        result = await controller.compose(spec, base_dir=tmp_path)

        assert result.errors == []
        assert result.composed_prompt == "Required phrase with richer detail."
        first_judge_prompt = client.complete_calls[0][0][0][1]["content"]
        assert "Constraint findings from the previous result" in first_judge_prompt
        assert "@assert failed: contains: Required phrase" in first_judge_prompt

    @pytest.mark.asyncio
    async def test_ask_wrapper_reuses_normal_ask_semantics(self, tmp_path: Path) -> None:
        client = _AskPreludeClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)
        spec = textwrap.dedent("""
            @iterate 1
              @ask clarifying question detail_level: 40%
                Draft a launch plan.
            """).strip()

        result = await controller.compose(
            spec,
            base_dir=tmp_path,
            ask_handler=lambda _prompt: "Enterprise buyers",
        )

        assert result.errors == []
        assert client.ask_tool_seen
        assert result.composed_prompt == "Draft a launch plan for enterprise buyers."

    @pytest.mark.asyncio
    async def test_directives_tag_is_parsed_into_composition_result(self) -> None:
        raw = _xml_prompt(
            "Expanded.",
            directives=[
                {
                    "id": "app-7-expand",
                    "name": "expand",
                    "header": "@expand mode: intention",
                    "body": "idea",
                    "line": 7,
                    "depth": 2,
                    "source_span": {"start_line": 7, "end_line": 8},
                }
            ],
        )

        result = parse_composition_response(raw)

        assert len(result.directives) == 1
        assert result.directives[0].name == "expand"
        assert result.directives[0].source_span.start_line == 7
