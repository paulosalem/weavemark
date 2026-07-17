"""Canonical runtime-model resolution and engine wiring tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from ellements.core import ToolCallResponse
from ellements.execution import StepRecord

from weavemark.api import CompileOptions, execute_text, load_runtime_config
from weavemark.app import create_parser
from weavemark.compilation.multimodal import ImageRef
from weavemark.controller import CompositionResult
from weavemark.engines import resolve_engine
from weavemark.engines.base import (
    ExecutionResult,
    PromptConfig,
    RuntimeConfig,
    resolve_call_settings,
)
from weavemark.engines.single_call import SingleCallEngine


def _result(**kwargs: Any) -> CompositionResult:
    return CompositionResult(
        composed_prompt="Prompt.",
        prompts={"default": "Prompt."},
        **kwargs,
    )


def test_runtime_override_has_highest_precedence_and_provenance() -> None:
    result = _result(execution={"model": "task-model", "temperature": 0.8})
    config = RuntimeConfig(
        model="runtime-model",
        temperature=0.1,
        engine_config={"model": "engine-model", "temperature": 0.2},
        prompts={"draft": PromptConfig(model="prompt-model", temperature=0.3)},
    )

    settings = resolve_call_settings(
        result,
        config,
        prompt_key="draft",
        stage="draft",
    )

    assert settings.model == "runtime-model"
    assert settings.temperature == 0.1
    assert settings.model_source == "runtime.model"
    assert settings.temperature_source == "runtime.temperature"


@pytest.mark.parametrize(
    ("config", "execution", "expected_model", "expected_source"),
    (
        (
            RuntimeConfig(
                prompts={"draft": PromptConfig(model="prompt-model")},
                engine_config={"draft_model": "stage-model"},
            ),
            {"model": "task-model"},
            "prompt-model",
            "prompts.draft.model",
        ),
        (
            RuntimeConfig(engine_config={"draft_model": "stage-model"}),
            {"model": "task-model"},
            "stage-model",
            "engine_config.draft_model",
        ),
        (
            RuntimeConfig(engine_config={"model": "engine-model"}),
            {"model": "task-model"},
            "engine-model",
            "engine_config.model",
        ),
        (
            RuntimeConfig(),
            {"model": "task-model"},
            "task-model",
            "@execute.model",
        ),
    ),
)
def test_model_precedence_below_runtime_override(
    config: RuntimeConfig,
    execution: dict[str, Any],
    expected_model: str,
    expected_source: str,
) -> None:
    settings = resolve_call_settings(
        _result(execution=execution),
        config,
        prompt_key="draft",
        stage="draft",
    )

    assert settings.model == expected_model
    assert settings.model_source == expected_source


def test_image_model_is_explicit_and_output_model_is_lower_precedence() -> None:
    from weavemark.compilation.multimodal import OutputContract

    contract = OutputContract(type="image", params={"model": "output-image"})
    settings = resolve_call_settings(
        _result(),
        RuntimeConfig(image_model="runtime-image"),
        prompt_key="default",
        modality="image",
        output_contract=contract,
    )

    assert settings.model == "runtime-image"
    assert settings.model_source == "runtime.image_model"


def test_allowed_model_policy_rejects_non_resident_model() -> None:
    with pytest.raises(ValueError, match="not allowed by runtime policy"):
        resolve_call_settings(
            _result(),
            RuntimeConfig(
                model="remote-model",
                allowed_models=("resident-model",),
            ),
            prompt_key="default",
        )


def test_runtime_mapping_loads_all_model_fields() -> None:
    config = load_runtime_config(
        {
            "model": "text-model",
            "image_model": "image-model",
            "temperature": 0.25,
            "allowed_models": ["text-model", "image-model"],
        }
    )

    assert config is not None
    assert config.model == "text-model"
    assert config.image_model == "image-model"
    assert config.temperature == 0.25
    assert config.allowed_models == ("text-model", "image-model")


@pytest.mark.parametrize(
    "config",
    (
        {"allowed_models": "text-model"},
        {"temperature": "cold"},
        {"prompts": []},
        {"engine_config": []},
    ),
)
def test_runtime_mapping_rejects_invalid_setting_types(
    config: dict[str, Any],
) -> None:
    with pytest.raises(ValueError, match="Runtime config"):
        load_runtime_config(config)


def test_cli_model_flags_are_explicit_overrides() -> None:
    parser = create_parser()

    defaults = parser.parse_args(["spec.weavemark.md"])
    explicit = parser.parse_args(
        [
            "spec.weavemark.md",
            "--model",
            "text-model",
            "--image-model",
            "image-model",
        ]
    )

    assert defaults.model is None
    assert defaults.image_model is None
    assert explicit.model == "text-model"
    assert explicit.image_model == "image-model"


def test_registry_injects_client_into_builtin_engine() -> None:
    client: Any = object()

    engine = resolve_engine("single-call", client=client)

    assert engine.client is client


class _CapturingEngine:
    def __init__(self) -> None:
        self.config: RuntimeConfig | None = None

    async def execute(
        self,
        result: CompositionResult,
        config: RuntimeConfig | None = None,
        on_step: Any = None,
    ) -> ExecutionResult:
        self.config = config
        return ExecutionResult(output=result.composed_prompt)


@pytest.mark.asyncio
async def test_public_execute_uses_compile_model_for_execution_by_default(
    tmp_path: Path,
) -> None:
    engine = _CapturingEngine()

    run = await execute_text(
        "Prompt.",
        base_dir=tmp_path,
        options=CompileOptions(model="shared-model"),
        engine=engine,
    )

    assert run.compiled.errors == []
    assert engine.config is run.runtime_config
    assert engine.config is not None
    assert engine.config.model == "shared-model"


class _MultimodalClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def complete_with_tools(
        self,
        messages: Any,
        tools: Any,
        **kwargs: Any,
    ) -> ToolCallResponse:
        self.calls.append(
            {"messages": messages, "tools": tools, **kwargs}
        )
        return ToolCallResponse(content="Multimodal result.")


@pytest.mark.asyncio
async def test_multimodal_single_call_preserves_tools_settings_and_callback() -> None:
    client = _MultimodalClient()
    steps: list[StepRecord] = []
    result = _result(
        prompt_images={
            "default": [
                ImageRef(
                    source="url",
                    ref="https://example.com/reference.png",
                )
            ]
        },
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "lookup",
                    "description": "Look up context",
                    "parameters": {"type": "object"},
                },
            }
        ],
    )

    executed = await SingleCallEngine(client=client).execute(
        result,
        RuntimeConfig(model="vision-model", temperature=0.0),
        on_step=steps.append,
    )

    assert executed.output == "Multimodal result."
    assert len(client.calls) == 1
    assert client.calls[0]["model"] == "vision-model"
    assert client.calls[0]["temperature"] == 0.0
    assert client.calls[0]["tools"] == result.tools
    assert [step.response for step in steps] == ["Multimodal result."]
    assert executed.metadata["call_settings"]["model_source"] == "runtime.model"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "engine_name",
    (
        "self-consistency",
        "tree-of-thought",
        "simplified-tree-of-thought",
        "collaborative",
        "fslm",
    ),
)
async def test_text_only_engines_reject_multimodal_inputs_explicitly(
    engine_name: str,
) -> None:
    result = _result(
        prompt_images={
            "default": [
                ImageRef(
                    source="url",
                    ref="https://example.com/reference.png",
                )
            ]
        }
    )

    with pytest.raises(ValueError, match="does not support multimodal"):
        await resolve_engine(engine_name).execute(result)
