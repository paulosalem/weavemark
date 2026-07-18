"""Cross-round metadata preservation and global compilation-budget tests."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.compilation.multimodal import ImageRef, OutputContract
from weavemark.compilation.state import CompilationBudget, CompositionAccumulator
from weavemark.controller import CompositionResult, WeaveMarkConfig, WeaveMarkController


def _tool(name: str, description: str) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object"},
        },
    }


def test_accumulator_preserves_and_replaces_metadata_by_identity() -> None:
    image = ImageRef(source="url", ref="https://example.com/image.png")
    first = CompositionResult(
        composed_prompt="First.",
        prompts={"draft": "Draft."},
        prompt_roles={"draft": "assistant"},
        prompt_images={"draft": [image]},
        prompt_outputs={
            "draft": OutputContract(type="text", params={"file": "draft.md"})
        },
        compile={"format": "json"},
        tools=[_tool("lookup", "First description")],
        bindings=[{"capability": "lookup", "language": "python"}],
        execution={"type": "chain"},
        emits={"system.md": "System"},
        packages=[{"file": "out.html", "template": "template.md"}],
        warnings=["warning"],
        suggestions=["suggestion"],
        transitions=["transition"],
        ask_history=[{"question": "Audience?", "answer": "Experts"}],
        iteration_history=[{"iteration": 1}],
        tool_calls_made=2,
    )
    second = CompositionResult(
        composed_prompt="Second.",
        prompts={"draft": "Improved draft.", "review": "Review."},
        tools=[_tool("lookup", "Updated description")],
        bindings=[{"capability": "lookup", "language": "javascript"}],
        packages=[{"file": "out.html", "template": "new-template.md"}],
        tool_calls_made=3,
    )
    accumulator = CompositionAccumulator()

    accumulator.absorb(first)
    accumulator.absorb(second)
    accumulator.apply_to(second)

    assert second.prompts == {
        "draft": "Improved draft.",
        "review": "Review.",
    }
    assert second.prompt_roles == {"draft": "assistant"}
    assert second.prompt_images == {"draft": [image]}
    assert second.prompt_outputs["draft"].params["file"] == "draft.md"
    assert second.compile == {"format": "json"}
    assert second.tools[0]["function"]["description"] == "Updated description"
    assert second.bindings == [
        {"capability": "lookup", "language": "javascript"}
    ]
    assert second.execution == {"type": "chain"}
    assert second.emits == {"system.md": "System"}
    assert second.packages == [
        {"file": "out.html", "template": "new-template.md"}
    ]
    assert second.warnings == ["warning"]
    assert second.suggestions == ["suggestion"]
    assert second.transitions == ["transition"]
    assert second.ask_history == [{"question": "Audience?", "answer": "Experts"}]
    assert second.iteration_history == [{"iteration": 1}]
    assert second.tool_calls_made == 5


class _MetadataAskClient:
    def __init__(self) -> None:
        self.calls = 0

    async def complete_with_tools(self, *args: Any, **kwargs: Any) -> ToolCallResponse:
        self.calls += 1
        if self.calls == 1:
            await kwargs["tool_executor"](
                "ask_user",
                {
                    "question": "Who is the audience?",
                    "question_type": "clarifying question",
                    "detail_level": "40%",
                    "scope": "plan",
                    "reason": "The audience changes the plan.",
                },
            )
            return ToolCallResponse(
                content=compiler_response(
                    "@ask clarifying question detail_level: 40%\n"
                    "  Draft the plan with the answer.",
                    prompts={
                        "default": {
                            "text": (
                                "@ask clarifying question detail_level: 40%\n"
                                "  Draft the plan with the answer."
                            ),
                            "role": "user",
                        },
                        "system": {"text": "System context.", "role": "system"},
                    },
                    compile={"format": "json"},
                    tools=[_tool("lookup", "Look up facts")],
                    bindings=[{"capability": "lookup", "language": "python"}],
                    execution={"type": "single-call"},
                    emits={"system.md": "System context."},
                    outputs={"default": {"type": "text", "file": "answer.md"}},
                    packages=[{"file": "out.html", "template": "template.md"}],
                )
            )
        return ToolCallResponse(
            content=compiler_response("Final plan for enterprise buyers.")
        )


@pytest.mark.asyncio
async def test_ask_rounds_preserve_complete_compiler_metadata(
    tmp_path: Path,
) -> None:
    client = _MetadataAskClient()
    controller = WeaveMarkController(
        WeaveMarkConfig(max_effect_rounds=2),
        client=client,
    )

    result = await controller.compose(
        "@ask clarifying question detail_level: 40%\n  Draft the plan.",
        base_dir=tmp_path,
        ask_handler=lambda _prompt: "Enterprise buyers",
    )

    assert result.errors == []
    assert result.composed_prompt == "Final plan for enterprise buyers."
    assert result.prompts["system"] == "System context."
    assert result.prompt_roles == {"default": "user", "system": "system"}
    assert result.compile == {"format": "json"}
    assert result.tools[0]["function"]["name"] == "lookup"
    assert result.bindings == [
        {"name": "lookup", "language": "python"}
    ]
    assert result.execution == {"type": "single-call"}
    assert result.emits == {"system.md": "System context."}
    assert result.prompt_outputs["default"].params["file"] == "answer.md"
    assert result.packages == [
        {"file": "out.html", "template": "template.md"}
    ]
    assert result.ask_history[0]["answer"] == "Enterprise buyers"


def test_compilation_budget_rejects_repeated_states_and_exhaustion() -> None:
    budget = CompilationBudget(max_steps=2, max_model_calls=1, max_seconds=60)

    assert budget.consume_step("scope", "first") is None
    assert "same compiler state" in (budget.consume_step("scope", "first") or "")
    assert budget.consume_model_call("round") is None
    assert "model-call budget exhausted" in (
        budget.consume_model_call("round") or ""
    )


def test_compilation_budget_rejects_elapsed_deadline() -> None:
    budget = CompilationBudget(
        max_steps=1,
        max_model_calls=1,
        max_seconds=0.01,
        started_at=time.monotonic() - 1,
    )

    assert "time budget exhausted" in (budget.check_time() or "")


class _NeverCalledClient:
    async def complete_with_tools(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("The exhausted model-call budget must fail first.")


@pytest.mark.asyncio
async def test_model_call_budget_failure_returns_partial_diagnostics(
    tmp_path: Path,
) -> None:
    controller = WeaveMarkController(
        WeaveMarkConfig(
            use_structural_helpers=False,
            max_total_model_calls=0,
        ),
        client=_NeverCalledClient(),
    )

    result = await controller.compose("Semantic compilation required.", base_dir=tmp_path)

    assert result.composed_prompt == ""
    assert result.model_calls_made == 1
    assert result.errors == [
        "Compilation model-call budget exhausted during semantic composition: "
        "0/0 calls used."
    ]
