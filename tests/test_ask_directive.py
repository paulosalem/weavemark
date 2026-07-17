"""Tests for the standard-library ``@ask`` compile effect."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.compilation.ask import find_ask_directives
from weavemark.compilation.macros import preprocess_weavemark
from weavemark.controller import WeaveMarkConfig, WeaveMarkController


def _xml_prompt(prompt: str) -> str:
    return compiler_response(prompt)


class _IterativeAskClient:
    def __init__(self) -> None:
        self.calls = 0
        self.messages: list[Any] = []
        self.ask_tool_seen = False

    async def complete_with_tools(self, *args, **kwargs) -> ToolCallResponse:
        self.calls += 1
        self.messages.append(kwargs["messages"])
        tool_names = {
            tool["function"]["name"]
            for tool in kwargs["tools"]
            if isinstance(tool, dict) and "function" in tool
        }
        self.ask_tool_seen = self.ask_tool_seen or "ask_user" in tool_names
        executor = kwargs["tool_executor"]

        if self.calls == 1:
            await executor(
                "ask_user",
                {
                    "question": "Who is the audience?",
                    "question_type": "clarifying question",
                    "detail_level": "40%",
                    "scope": "launch plan",
                    "reason": "Audience changes the remaining prompt.",
                },
            )
            return ToolCallResponse(
                content=_xml_prompt(
                    "@ask clarifying question detail_level: 40%\n"
                    "  Draft a launch plan for the answered audience."
                )
            )

        await executor(
            "ask_user",
            {
                "question": "What tone should the plan use?",
                "question_type": "clarifying question",
                "detail_level": "40%",
                "scope": "launch plan",
                "reason": "Tone only becomes relevant after the audience is known.",
            },
        )
        return ToolCallResponse(
            content=_xml_prompt(
                "Draft a concise executive launch plan for enterprise buyers."
            )
        )


class _RepeatedQuestionClient:
    def __init__(self) -> None:
        self.calls = 0

    async def complete_with_tools(self, *args: Any, **kwargs: Any) -> ToolCallResponse:
        self.calls += 1
        await kwargs["tool_executor"](
            "ask_user",
            {
                "question": "Who is the audience?",
                "question_type": "clarifying question",
                "detail_level": "40%",
                "scope": "launch plan",
                "reason": "Audience changes the plan.",
            },
        )
        if self.calls == 1:
            return ToolCallResponse(content=_xml_prompt(_ask_spec()))
        return ToolCallResponse(content=_xml_prompt("Final plan."))


def _ask_spec() -> str:
    return textwrap.dedent("""
        # Launch Planner

        @ask clarifying question detail_level: 40%
          Draft a launch plan.
        """).strip()


class TestAskDirective:
    def test_finds_active_asks_innermost_first(self, tmp_path: Path) -> None:
        spec = textwrap.dedent("""
            @ask clarifying question detail_level: 20%
              Outer body.
              @ask tradeoff question detail_level: 80%
                Inner body.
            """).strip()
        preprocessed = preprocess_weavemark(spec, tmp_path)

        directives, errors = find_ask_directives(
            preprocessed.text,
            preprocessed.semantic_definitions,
        )

        assert errors == []
        assert [directive.question_type for directive in directives] == [
            "tradeoff question",
            "clarifying question",
        ]
        assert [directive.detail_level for directive in directives] == ["80%", "20%"]

    def test_unquoted_multiword_question_type_before_named_options(
        self, tmp_path: Path
    ) -> None:
        spec = textwrap.dedent("""
            @ask clarifying tradeoff question detail_level: 40%
              Draft a prompt.
            """).strip()
        preprocessed = preprocess_weavemark(spec, tmp_path)

        directives, errors = find_ask_directives(
            preprocessed.text,
            preprocessed.semantic_definitions,
        )

        assert errors == []
        assert directives[0].question_type == "clarifying tradeoff question"

    def test_positional_text_after_named_options_is_rejected(
        self, tmp_path: Path
    ) -> None:
        spec = textwrap.dedent("""
            @ask detail_level: 40% clarifying question
              Draft a prompt.
            """).strip()
        preprocessed = preprocess_weavemark(spec, tmp_path)

        directives, errors = find_ask_directives(
            preprocessed.text,
            preprocessed.semantic_definitions,
        )

        assert directives == []
        assert errors == [
            "@ask at line 1: Unexpected positional token 'clarifying' after named "
            "parameters; put free-form text before named parameters or quote it "
            "as a named parameter value. Unexpected positional token 'question' "
            "after named parameters; put free-form text before named parameters "
            "or quote it as a named parameter value."
        ]

    @pytest.mark.asyncio
    async def test_ask_requires_host_handler(self, tmp_path: Path) -> None:
        client = _IterativeAskClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)

        result = await controller.compose(_ask_spec(), base_dir=tmp_path)

        assert client.calls == 0
        assert result.errors == [
            "@ask requires an interactive host ask handler. Run without "
            "--batch-only in the CLI or provide ask_handler when using the "
            "Python API."
        ]

    @pytest.mark.asyncio
    async def test_ask_in_discarded_branch_does_not_require_handler(
        self, tmp_path: Path
    ) -> None:
        client = _IterativeAskClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)
        spec = textwrap.dedent("""
            @match mode
              "plain" ==> No clarification needed.
              "interactive" ==>
                @ask clarifying question detail_level: 50%
                  Draft the interactive branch.
            """).strip()

        result = await controller.compose(
            spec,
            variables={"mode": "plain"},
            base_dir=tmp_path,
        )

        assert client.calls == 0
        assert result.errors == []
        assert result.composed_prompt == "No clarification needed."

    @pytest.mark.asyncio
    async def test_ask_can_survive_intermediate_rounds(self, tmp_path: Path) -> None:
        client = _IterativeAskClient()
        answers = iter(["Enterprise buyers", "Concise executive"])
        controller = WeaveMarkController(
            WeaveMarkConfig(max_effect_rounds=3),
            client=client,
        )

        result = await controller.compose(
            _ask_spec(),
            base_dir=tmp_path,
            ask_handler=lambda _prompt: next(answers),
        )

        assert result.errors == []
        assert client.ask_tool_seen
        assert client.calls == 2
        assert result.composed_prompt == (
            "Draft a concise executive launch plan for enterprise buyers."
        )
        assert [item["answer"] for item in result.ask_history] == [
            "Enterprise buyers",
            "Concise executive",
        ]
        second_round_prompt = client.messages[1][1]["content"]
        assert "Collected @ask answers from previous rounds" in second_round_prompt
        assert "Enterprise buyers" in second_round_prompt

    @pytest.mark.asyncio
    async def test_invalid_detail_level_fails_before_llm(self, tmp_path: Path) -> None:
        client = _IterativeAskClient()
        controller = WeaveMarkController(WeaveMarkConfig(), client=client)
        spec = textwrap.dedent("""
            @ask clarifying question detail_level: 0%
              Draft a prompt.
            """).strip()

        result = await controller.compose(
            spec,
            base_dir=tmp_path,
            ask_handler=lambda _prompt: "answer",
        )

        assert client.calls == 0
        assert result.errors == [
            "@ask at line 1 has invalid detail_level '0%'; expected a percentage "
            "greater than 0% and no greater than 100%."
        ]

    @pytest.mark.asyncio
    async def test_repeated_question_is_a_compilation_error(
        self,
        tmp_path: Path,
    ) -> None:
        client = _RepeatedQuestionClient()
        answers: list[str] = []
        controller = WeaveMarkController(
            WeaveMarkConfig(max_effect_rounds=2),
            client=client,
        )

        result = await controller.compose(
            _ask_spec(),
            base_dir=tmp_path,
            ask_handler=lambda _prompt: answers.append("Enterprise") or "Enterprise",
        )

        assert answers == ["Enterprise"]
        assert result.errors == [
            "ask_user repeated a question that was already answered: "
            "Who is the audience?"
        ]
