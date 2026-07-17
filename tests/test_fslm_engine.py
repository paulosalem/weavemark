"""Tests for the WeaveMark FSLM execution engine."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path
from typing import Any

import pytest
from ellements.core import LLMClient, PromptKeyMissingError

from weavemark.api import compile_text, execute_text
from weavemark.controller import CompositionResult
from weavemark.engines import Engine, resolve_engine
from weavemark.engines.base import RuntimeConfig
from weavemark.engines.fslm import FSLMEngine
from weavemark.protection import (
    ProtectionContext,
    ProtectionError,
    ProtectionSettings,
)


class MockLLMClient:
    """Small WeaveMark/FSLM test double for text and structured calls."""

    def __init__(
        self,
        responses: list[str] | None = None,
        structured_responses: list[dict[str, Any]] | None = None,
    ) -> None:
        self.responses = responses or []
        self.structured_responses = structured_responses or []
        self.calls: list[dict[str, Any]] = []
        self.default_model = "mock-model"

    async def complete(
        self,
        messages: Any,
        *,
        model: str | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        self.calls.append(
            {
                "kind": "complete",
                "messages": messages,
                "model": model,
                "temperature": temperature,
            }
        )
        if self.responses:
            return self.responses.pop(0)
        return "mock response"

    async def complete_structured(
        self,
        messages: Any,
        response_model: Any,
        *,
        model: str | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Any:
        self.calls.append(
            {
                "kind": "complete_structured",
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "response_model": response_model,
            }
        )
        payload = (
            self.structured_responses.pop(0)
            if self.structured_responses
            else {
                "id": "decision",
                "allowed": True,
                "confidence": 1.0,
                "evidence": [],
                "uncertainties": [],
                "alternatives": [],
            }
        )
        return response_model(**payload)


def _write_machine(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "machine.yaml"
    path.write_text(textwrap.dedent(text).strip() + "\n", encoding="utf-8")
    return path


def test_fslm_is_registered_builtin_engine() -> None:
    assert isinstance(resolve_engine("fslm"), FSLMEngine)
    assert isinstance(FSLMEngine(client=MockLLMClient()), Engine)


@pytest.mark.asyncio
async def test_fslm_rejects_unsupported_autonomous_runner() -> None:
    with pytest.raises(ValueError, match="event-driven"):
        await FSLMEngine(client=MockLLMClient()).execute(
            CompositionResult(
                composed_prompt="",
                execution={
                    "type": "fslm",
                    "runner": "autonomous",
                },
            )
        )


@pytest.mark.asyncio
async def test_fslm_rejects_unknown_prompt_contract() -> None:
    with pytest.raises(ValueError, match="prompt_contract"):
        await FSLMEngine(client=MockLLMClient()).execute(
            CompositionResult(
                composed_prompt="",
                execution={
                    "type": "fslm",
                    "prompt_contract": "best-effort",
                },
            )
        )


@pytest.mark.asyncio
async def test_python_fslm_requires_remembered_protection_approval(
    tmp_path: Path,
) -> None:
    machine = tmp_path / "machine.py"
    machine.write_text(
        textwrap.dedent(
            """
            from ellements.fslm import machine

            builder = machine("protected-python", initial="waiting")
            with builder.state("waiting") as state:
                state.on("go").to("done", "finish")
            builder.state("done", terminal=True)
            definition = builder.build()
            """
        ),
        encoding="utf-8",
    )
    blocked_context = ProtectionContext.create(
        ProtectionSettings(),
        entrypoint_dir=tmp_path,
        approvals_path=tmp_path / "approvals.json",
    )
    result = CompositionResult(
        composed_prompt="",
        execution={"type": "fslm", "machine": "./machine.py"},
    )

    with pytest.raises(ProtectionError, match="Python code execution"):
        await FSLMEngine(client=MockLLMClient()).execute(
            result,
            RuntimeConfig(
                engine_config={
                    "base_dir": str(tmp_path),
                    "initial_event": "go",
                },
                protection=blocked_context,
            ),
        )

    approved_context = ProtectionContext.create(
        ProtectionSettings(),
        entrypoint_dir=tmp_path,
        approval_handler=lambda _request: True,
        approvals_path=tmp_path / "approvals.json",
    )
    executed = await FSLMEngine(client=MockLLMClient()).execute(
        result,
        RuntimeConfig(
            engine_config={
                "base_dir": str(tmp_path),
                "initial_event": "go",
            },
            protection=approved_context,
        ),
    )

    assert executed.metadata["status"] == "terminal"


@pytest.mark.asyncio
async def test_fslm_fails_before_llm_when_required_prompt_is_missing(
    tmp_path: Path,
) -> None:
    machine = _write_machine(
        tmp_path,
        """
        name: missing-prompt-demo
        initial: start
        states:
          start:
            transitions:
              - name: finish
                event: go
                target: done
                guards:
                  - id: ready
                    kind: nl
                    text: Allow only if ready.
          done:
            terminal: true
        """,
    )
    client = MockLLMClient()
    engine = FSLMEngine(client=client)

    with pytest.raises(PromptKeyMissingError, match="guard.ready"):
        await engine.execute(
            CompositionResult(
                composed_prompt="",
                prompts={},
                execution={
                    "type": "fslm",
                    "machine": str(machine),
                    "initial_event": "go",
                },
            )
        )

    assert client.calls == []


@pytest.mark.asyncio
async def test_fslm_runs_guard_action_and_output_prompts(tmp_path: Path) -> None:
    machine = _write_machine(
        tmp_path,
        """
        name: support-triage-demo
        initial: triage
        states:
          triage:
            transitions:
              - name: answer
                event: user_message
                target: done
                guards:
                  - id: relevant
                    kind: nl
                    text: Continue only if the user needs an answer.
                actions:
                  - name: draft_answer
                    kind: nl
                    tool: language
                    text: Draft the answer.
                emits:
                  - type: final_answer
                    kind: nl
                    text: Produce the final answer.
          done:
            terminal: true
            invariants:
              - id: answer_is_grounded
                kind: nl
                text: The answer must be grounded in the event payload.
        """,
    )
    client = MockLLMClient(
        responses=["State notes", "Action notes", "Final answer"],
        structured_responses=[
            {
                "id": "relevant",
                "allowed": True,
                "confidence": 0.95,
                "evidence": ["The event asks a question."],
                "uncertainties": [],
                "alternatives": [],
            },
            {
                "id": "answer_is_grounded",
                "allowed": True,
                "confidence": 1.0,
                "evidence": ["The answer uses event context."],
                "uncertainties": [],
                "alternatives": [],
            },
        ],
    )

    executed = await FSLMEngine(client=client).execute(
        CompositionResult(
            composed_prompt="",
            prompts={
                "state.triage": "Summarize the current state.",
                "guard.relevant": "Decide whether to continue.",
                "invariant.answer_is_grounded": "Check final-state grounding.",
                "action.draft_answer": "Draft using the runtime context.",
                "output.final_answer": "Write the final response.",
            },
            execution={
                "type": "fslm",
                "machine": str(machine),
                "initial_event": {
                    "type": "user_message",
                    "payload": {"message": "How do I reset my password?"},
                },
            },
        )
    )

    assert executed.output == "Final answer"
    assert executed.metadata["status"] == "terminal"
    assert [call["kind"] for call in client.calls] == [
        "complete",
        "complete_structured",
        "complete_structured",
        "complete",
        "complete",
    ]
    assert [step.prompt_key for step in executed.steps] == [
        "state.triage",
        "guard.relevant",
        "invariant.answer_is_grounded",
        "action.draft_answer",
        "output.final_answer",
        "machine",
    ]


@pytest.mark.asyncio
async def test_fslm_prompt_key_metadata_overrides_convention(tmp_path: Path) -> None:
    machine = _write_machine(
        tmp_path,
        """
        name: metadata-prompt-demo
        initial: start
        states:
          start:
            transitions:
              - name: finish
                event: go
                target: done
                guards:
                  - id: internal_ready
                    kind: nl
                    text: Continue if ready.
                    metadata:
                      prompt_key: guard.custom_ready
                emits:
                  - type: internal_answer
                    kind: nl
                    text: Produce an answer.
                    metadata:
                      prompt_key: output.custom_answer
          done:
            terminal: true
        """,
    )
    client = MockLLMClient(
        responses=["Overridden answer"],
        structured_responses=[
            {
                "id": "internal_ready",
                "allowed": True,
                "confidence": 1.0,
                "evidence": [],
                "uncertainties": [],
                "alternatives": [],
            }
        ],
    )

    executed = await FSLMEngine(client=client).execute(
        CompositionResult(
            composed_prompt="",
            prompts={
                "guard.custom_ready": "Use the custom guard prompt.",
                "output.custom_answer": "Use the custom output prompt.",
            },
            execution={"type": "fslm", "machine": str(machine), "initial_event": "go"},
        )
    )

    assert executed.output == "Overridden answer"
    assert {step.prompt_key for step in executed.steps} >= {
        "guard.custom_ready",
        "output.custom_answer",
    }


@pytest.mark.asyncio
async def test_fslm_runtime_context_includes_event_and_action_results(
    tmp_path: Path,
) -> None:
    machine = _write_machine(
        tmp_path,
        """
        name: context-demo
        initial: start
        states:
          start:
            transitions:
              - name: finish
                event: go
                target: done
                actions:
                  - name: gather_context
                    kind: nl
                    tool: language
                    text: Gather context.
                emits:
                  - type: final
                    kind: nl
                    text: Produce output.
          done:
            terminal: true
        """,
    )
    client = MockLLMClient(responses=["Action notes", "Final output"])

    await FSLMEngine(client=client).execute(
        CompositionResult(
            composed_prompt="",
            prompts={
                "action.gather_context": "Act on the event.",
                "output.final": "Use action output and event payload.",
            },
            execution={
                "type": "fslm",
                "machine": str(machine),
                "initial_event": {
                    "type": "go",
                    "payload": {"message": "hello from payload"},
                },
            },
        )
    )

    output_call = client.calls[1]
    content = output_call["messages"][1]["content"]
    assert "hello from payload" in content
    assert "Action notes" in content
    assert '"selected_transition": "finish"' in content


@pytest.mark.asyncio
async def test_fslm_engine_works_through_public_execute_text_with_relative_machine(
    tmp_path: Path,
) -> None:
    machines = tmp_path / "machines"
    machines.mkdir()
    machine = machines / "relative.yaml"
    machine.write_text(
        """
name: public-api-demo
initial: start
states:
  start:
    transitions:
      - name: finish
        event: go
        target: done
        emits:
          - type: final
            kind: nl
            text: Produce output.
  done:
    terminal: true
""",
        encoding="utf-8",
    )
    spec = """
@promplet version: 0.7
@use weavemark.experimental.fslm exposing machine state transition input guard action

@execute fslm
  machine: machines/relative.yaml
  initial_event: go

@prompt output.final
  Produce the final output from the runtime context.
"""

    run = await execute_text(
        spec,
        base_dir=tmp_path,
        engine=FSLMEngine(client=MockLLMClient(responses=["Relative output"])),
    )

    assert run.output == "Relative output"
    assert run.execution.metadata["machine"]["name"] == "public-api-demo"


@pytest.mark.asyncio
async def test_fslm_sugar_lowers_inline_machine_to_machine_spec() -> None:
    spec = """
@promplet version: 0.7
@use weavemark.experimental.fslm exposing machine state transition input guard action

@execute fslm
  machine: support_triage
  initial_event: user_message

Shared FSLM context.

@machine support_triage initial: triage
  Support triage workflow.

  @state triage
    The request is being triaged.

    @transition gather_evidence target: triage internal: true external: false
      Search documentation before answering.

      @input query
        Search query.

      @input max_results default: 5
        Maximum result count.

      @guard needs_more_evidence
        Choose this when the current evidence is insufficient.

      @action search_docs tool: search_docs
        Search docs using matching transition inputs.

      @action summarize_findings
        Summarize the gathered evidence.

  @state waiting_for_user
    Waiting for the user.

    @transition receive_user_reply event: user_message target: triage internal: false external: true
      Resume when the user replies.
"""

    compiled = await compile_text(spec)

    assert not compiled.errors
    machine_spec = compiled.execution["machine_spec"]
    assert machine_spec["name"] == "support_triage"
    transition = machine_spec["states"]["triage"]["transitions"][0]
    assert transition["metadata"]["internal"] is True
    assert transition["metadata"]["external"] is False
    assert [item["name"] for item in transition["metadata"]["inputs"]] == [
        "query",
        "max_results",
    ]
    assert transition["actions"][0]["kind"] == "tool"
    assert transition["actions"][0]["args"]["input_names"] == [
        "query",
        "max_results",
    ]
    assert transition["actions"][1]["kind"] == "nl"
    guard_key = "guard.triage.gather_evidence.needs_more_evidence"
    action_key = "action.triage.gather_evidence.summarize_findings"
    assert transition["guards"][0]["metadata"]["prompt_key"] == guard_key
    assert transition["actions"][1]["metadata"]["prompt_key"] == action_key
    assert "Shared FSLM context." in compiled.prompts[guard_key]
    assert "Choose this when" in compiled.prompts[guard_key]
    assert (
        "Summarize the gathered evidence."
        in compiled.prompts[action_key]
    )


@pytest.mark.asyncio
async def test_fslm_sugar_executes_inline_machine_with_multiple_actions() -> None:
    spec = """
@promplet version: 0.7
@use weavemark.experimental.fslm exposing machine state transition input guard action

@tool search_docs
  Search documentation.
  - query: string (required) — Search query.
  - max_results: integer (optional) — Maximum results.

@execute fslm
  machine: evidence_machine
  initial_event:
  max_steps: 1

@machine evidence_machine initial: triage
  Evidence collection machine.

  @state triage
    The machine should gather evidence and summarize it.

    @transition gather_evidence event: user_message target: triage
      Search docs and summarize results.

      @input query
        Search query.

      @input max_results default: 3
        Maximum results.

      @guard should_search
        Search is needed.

      @action search_docs tool: search_docs
        Search docs.

      @action summarize_findings
        Summarize findings after the search action.
"""
    client = MockLLMClient(
        responses=["Summary after planned search"],
        structured_responses=[
            {
                "id": "should_search",
                "allowed": True,
                "confidence": 1.0,
                "evidence": ["Need evidence."],
                "uncertainties": [],
                "alternatives": [],
            }
        ],
    )

    run = await execute_text(
        spec,
        engine=FSLMEngine(client=client),
        runtime_config={
            "engine": "fslm",
            "engine_config": {
                "initial_event": {
                    "type": "user_message",
                    "payload": {"query": "password reset", "unused": "ignored"},
                }
            },
        },
    )

    step = run.execution.metadata["steps"][0]
    assert [action["action_name"] for action in step["actions"]] == [
        "search_docs",
        "summarize_findings",
    ]
    assert step["actions"][0]["status"] == "planned"
    assert step["actions"][0]["output"]["arguments"] == {
        "query": "password reset",
        "max_results": "3",
    }
    assert step["actions"][1]["output"]["text"] == "Summary after planned search"
    assert "Summary after planned search" in run.output


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_fslm_guard_and_action_through_weavemark() -> None:
    if not (
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("LITELLM_API_KEY")
    ):
        pytest.skip("live LLM credentials are not configured")
    model = os.environ.get("FSLM_TEST_MODEL", "gpt-5.5")
    spec = """
@promplet version: 0.7
@use weavemark.experimental.fslm exposing machine state transition guard action

@execute fslm
  machine: live_machine
  max_steps: 1

@machine live_machine initial: waiting
  @state waiting
    @transition finish event: approval target: done
      @guard approval_is_explicit
        Allow only when the event payload says approved is true.
      @action report_success
        Return exactly FSLM_LIVE_OK and nothing else.
  @state done terminal: true
"""

    run = await execute_text(
        spec,
        engine=FSLMEngine(client=LLMClient(model=model)),
        runtime_config={
            "engine": "fslm",
            "model": model,
            "engine_config": {
                "initial_event": {
                    "type": "approval",
                    "payload": {"approved": True},
                }
            },
        },
    )

    assert run.execution.metadata["status"] == "terminal"
    assert run.execution.metadata["steps"][0]["selected_transition"] == "finish"
    assert run.execution.output.strip() == "FSLM_LIVE_OK"
