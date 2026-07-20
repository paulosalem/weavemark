"""Tests for WeaveMark engines, @prompt/@execute parsing, and the run flow.

Unit tests (no LLM required) verify:
- parse_composition_response handles strict prompt and execution metadata
- Engine protocol and registry
- RuntimeConfig loading
- Engine wrappers delegate to WeaveMark strategies correctly

Integration tests (require OPENAI_API_KEY) verify:
- @prompt and @execute directives work end-to-end
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest
from ellements.core import PromptKeyMissingError
from ellements.core.tools.records import ToolCallRecord, ToolCallResponse

from tests.wire_helpers import compiler_response
from weavemark.controller import (
    CompositionResult,
    parse_composition_response,
)

# ═══════════════════════════════════════════════════════════════════
# Mock LLMClient (same strategy-test pattern)
# ═══════════════════════════════════════════════════════════════════


class MockLLMClient:
    """Mock LLMClient for testing engines without real LLM calls.

    Tracks both ``complete`` and ``complete_structured`` invocations in
    :attr:`calls`.  Plain-text completions consume entries from
    ``responses``; structured completions consume from
    ``structured_responses`` (each entry may be a ``BaseModel`` instance
    or a ``dict`` validated against the requested ``response_format``).
    If ``structured_responses`` is exhausted (or never supplied) the mock
    synthesises a default-valued instance of ``response_format``.
    """

    def __init__(self, responses=None, structured_responses=None):
        self._responses = responses or ["Mock response"]
        self._call_count = 0
        self._structured_responses = list(structured_responses or [])
        self._structured_idx = 0
        self.calls: list[dict[str, Any]] = []
        self.default_model = "mock-model"

    async def complete(
        self,
        messages: str | list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        self.calls.append(
            {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "kind": "complete",
            }
        )
        if callable(self._responses):
            return self._responses(messages, **kwargs)
        idx = min(self._call_count, len(self._responses) - 1)
        self._call_count += 1
        return self._responses[idx]

    async def complete_structured(
        self,
        messages: str | list[dict[str, str]],
        response_model: Any,
        model: str | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Any:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        self.calls.append(
            {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "kind": "complete_structured",
                "response_model": response_model,
            }
        )

        if self._structured_idx < len(self._structured_responses):
            payload = self._structured_responses[self._structured_idx]
            self._structured_idx += 1
            if isinstance(payload, response_model):
                return payload
            if isinstance(payload, dict):
                return response_model(**payload)
            return payload

        return _default_structured_instance(response_model)


class BoundToolMockClient(MockLLMClient):
    """Mock one complete tool loop while exercising the supplied executor."""

    async def complete_with_tools(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        *,
        tool_executor: Any,
        **kwargs: Any,
    ) -> ToolCallResponse:
        result = await tool_executor("search_web", {"query": "current AI news"})
        return ToolCallResponse(
            content=f"Digest from {result}",
            tool_calls=[
                ToolCallRecord(
                    name="search_web",
                    arguments={"query": "current AI news"},
                    result=result,
                )
            ],
        )


def _default_structured_instance(response_model: Any) -> Any:
    """Build a default-valued instance of *response_model* for the mock."""
    name = getattr(response_model, "__name__", "")
    if name == "CritiqueResult":
        return response_model(is_satisfied=True, issues=[])
    if name == "Evaluation":
        return response_model(score=0.5, reasoning="default reasoning")
    fields = getattr(response_model, "model_fields", {})
    defaults: dict[str, Any] = {}
    for field_name, field in fields.items():
        annotation = getattr(field, "annotation", str)
        if annotation is bool:
            defaults[field_name] = False
        elif annotation in (int, float):
            defaults[field_name] = 0
        elif annotation is list or getattr(annotation, "__origin__", None) is list:
            defaults[field_name] = []
        else:
            defaults[field_name] = ""
    return response_model(**defaults)


# ═══════════════════════════════════════════════════════════════════
# Unit Tests: @prompt and @execute response parsing
# ═══════════════════════════════════════════════════════════════════


class TestParsePromptsAndExecution:
    """Test strict response parsing for prompts and execution metadata."""

    def test_single_prompt_default(self):
        result = parse_composition_response(compiler_response("Hello world."))
        assert result.composed_prompt == "Hello world."
        assert result.prompts == {"default": "Hello world."}

    def test_named_prompts(self):
        prompts = {
            "generate": "Generate 3 approaches to X.",
            "evaluate": "Rate these approaches.",
            "synthesize": "Elaborate the best one.",
        }
        result = parse_composition_response(
            compiler_response("Shared context.", prompts=prompts)
        )
        assert result.prompts == prompts
        assert "generate" in result.prompts
        assert "evaluate" in result.prompts
        assert "synthesize" in result.prompts

    def test_execution_metadata(self):
        execution = {
            "type": "tree-of-thought",
            "branching_factor": 3,
            "max_depth": 2,
        }
        result = parse_composition_response(
            compiler_response("Hello.", execution=execution)
        )
        assert result.execution == execution
        assert result.execution["type"] == "tree-of-thought"
        assert result.execution["branching_factor"] == 3

    def test_empty_execution(self):
        result = parse_composition_response(compiler_response("Hello.", execution={}))
        assert result.execution == {}

    def test_full_output_with_all_tags(self):
        prompts = {"default": "You are a helper."}
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "description": "Search",
                    "parameters": {"type": "object"},
                },
            }
        ]
        execution = {"type": "self-consistency", "samples": 5}
        result = parse_composition_response(
            compiler_response(
                "You are a helper.",
                prompts=prompts,
                tools=tools,
                execution=execution,
                analysis="Processed spec.",
                warnings=["Warning 1"],
            )
        )
        assert result.composed_prompt == "You are a helper."
        assert result.prompts == prompts
        assert len(result.tools) == 1
        assert result.execution == execution
        assert result.analysis == "Processed spec."
        assert len(result.warnings) == 1


class TestCompositionResultToDict:
    """Test to_dict includes prompts and execution."""

    def test_to_dict_with_prompts(self):
        prompts = {"generate": "gen", "evaluate": "eval"}
        result = CompositionResult(
            composed_prompt="gen",
            prompts=prompts,
        )
        d = result.to_dict()
        assert d["prompts"] == prompts

    def test_to_dict_with_execution(self):
        execution = {"type": "tree-of-thought", "branching_factor": 3}
        result = CompositionResult(
            composed_prompt="Hello",
            execution=execution,
        )
        d = result.to_dict()
        assert d["execution"] == execution

    def test_to_dict_empty_prompts_and_execution(self):
        result = CompositionResult(composed_prompt="Hello")
        d = result.to_dict()
        assert "prompts" not in d
        assert "execution" not in d


# ═══════════════════════════════════════════════════════════════════
# Unit Tests: Engine protocol and registry
# ═══════════════════════════════════════════════════════════════════


class TestEngineProtocol:
    """Verify Engine protocol and registry."""

    def test_builtin_engines_satisfy_protocol(self):
        from weavemark.engines import (
            Engine,
            FunctionalEngine,
            ReflectionEngine,
            SelfConsistencyEngine,
            SimplifiedTreeOfThoughtEngine,
            SingleCallEngine,
            TreeOfThoughtEngine,
        )

        assert isinstance(SingleCallEngine(), Engine)
        assert isinstance(SelfConsistencyEngine(), Engine)
        assert isinstance(TreeOfThoughtEngine(), Engine)
        assert isinstance(SimplifiedTreeOfThoughtEngine(), Engine)
        assert isinstance(ReflectionEngine(), Engine)
        assert isinstance(FunctionalEngine(), Engine)

    def test_custom_class_satisfies_protocol(self):
        from weavemark.engines import Engine, ExecutionResult

        class CustomEngine:
            async def execute(self, result, config=None):
                return ExecutionResult(output="custom")

        assert isinstance(CustomEngine(), Engine)

    def test_resolve_builtin_names(self):
        from weavemark.engines import resolve_engine
        from weavemark.engines.functional import FunctionalEngine
        from weavemark.engines.reflection import ReflectionEngine
        from weavemark.engines.self_consistency import SelfConsistencyEngine
        from weavemark.engines.single_call import SingleCallEngine
        from weavemark.engines.tree_of_thought import (
            SimplifiedTreeOfThoughtEngine,
            TreeOfThoughtEngine,
        )

        assert isinstance(resolve_engine("single-call"), SingleCallEngine)
        assert isinstance(resolve_engine("self-consistency"), SelfConsistencyEngine)
        assert isinstance(resolve_engine("tree-of-thought"), TreeOfThoughtEngine)
        assert isinstance(
            resolve_engine("simplified-tree-of-thought"), SimplifiedTreeOfThoughtEngine
        )
        assert isinstance(resolve_engine("reflection"), ReflectionEngine)
        assert isinstance(resolve_engine("functional"), FunctionalEngine)

    def test_custom_engine_import_requires_python_approval(self, tmp_path: Path):
        from weavemark.engines import resolve_engine
        from weavemark.protection import (
            ProtectionContext,
            ProtectionError,
            ProtectionSettings,
        )

        protection = ProtectionContext.create(
            ProtectionSettings(),
            entrypoint_dir=tmp_path,
            invocation_dir=tmp_path,
            approvals_path=tmp_path / "approvals.json",
        )

        with pytest.raises(ProtectionError, match="Python code execution"):
            resolve_engine("untrusted_plugin.CustomEngine", protection=protection)

    def test_resolve_unknown_raises(self):
        from weavemark.engines import resolve_engine

        with pytest.raises(ValueError, match="Unknown engine"):
            resolve_engine("nonexistent-engine")

    @pytest.mark.asyncio
    async def test_functional_engine_executes_bound_dependency_graph(
        self, tmp_path: Path
    ):
        from weavemark.api import execute_text
        from weavemark.protection import ProtectionContext, ProtectionSettings

        helper = tmp_path / "helpers.py"
        helper.write_text(
            """
def seed(payload):
    assert isinstance(payload, dict)
    return {"score": payload["score"] + 1}

async def combine(previous, body):
    assert isinstance(previous, dict)
    return {"score": previous["score"] * 2, "body": body}
""".strip(),
            encoding="utf-8",
        )
        source = tmp_path / "functional.weavemark.md"
        spec = """
@define seed
  @phase execute
  @scope self
  @returns value
  @param payload
    Native payload.
  @effect seed_data read
  @body
    Seed.

@define combine
  @phase execute
  @scope self
  @returns value
  @param previous
    Prior result.
  @param body implicit: true
    Instructions.
  @effect combine_data read
  @body
    Combine.

@bind seed_data language: python from: "./helpers.py" symbol: seed
@bind combine_data language: python from: "./helpers.py" symbol: combine

@execute functional scheduler: graph-strict
  allow_effects: [seed_data, combine_data]

@seed payload: "@{payload}" as: seeded
@combine previous: "@{seeded}" as: final uses: seeded
  Seed score: @{seeded.score}

Write a concise report from @{final}.
""".strip()
        source.write_text(spec, encoding="utf-8")
        client = MockLLMClient(["Final prose"])

        run = await execute_text(
            spec,
            {"payload": {"score": 3}},
            source_path=source,
            base_dir=tmp_path,
            client=client,
            protection_context=ProtectionContext.create(
                ProtectionSettings(enabled=False),
                entrypoint_dir=tmp_path,
                invocation_dir=tmp_path,
                approvals_path=tmp_path / "approvals.json",
            ),
        )
        executed = run.execution

        assert executed.output == "Final prose"
        assert [step.name for step in executed.steps] == [
            "seeded",
            "final",
            "document",
        ]
        assert executed.metadata["status"] == "executed"
        assert executed.metadata["execution"]["status"] == "executed"
        assert executed.metadata["results"]["seeded"] == {"score": 4}
        assert executed.metadata["results"]["final"] == {
            "score": 8,
            "body": "Seed score: 4",
        }
        assert executed.metadata["evidence"]["errors"] == []
        assert executed.metadata["evidence"]["plan_levels"] == [
            ["seeded"],
            ["final"],
        ]
        assert executed.metadata["bindings"] == run.compiled.bindings
        assert run.compiled.execution["nodes"][1]["params"][1] == {
            "name": "body",
            "implicit": True,
            "mode": "text",
        }
        assert client.calls[0]["messages"] == [
            {
                "role": "user",
                "content": (
                    '{"score": 4}\n'
                    '{"score": 8, "body": "Seed score: 4"}\n\n'
                    'Write a concise report from {"score": 8, '
                    '"body": "Seed score: 4"}.'
                ),
            }
        ]

    @pytest.mark.asyncio
    async def test_module_default_binding_loads_and_local_binding_overrides_it(
        self,
        tmp_path: Path,
    ) -> None:
        from weavemark.api import compile_file
        from weavemark.engines.bindings import load_binding_callables
        from weavemark.protection import (
            ProtectionContext,
            ProtectionError,
            ProtectionSettings,
        )

        module_dir = tmp_path / "promplets" / "company"
        companion_dir = module_dir / "companions"
        companion_dir.mkdir(parents=True)
        (companion_dir / "default.py").write_text(
            "def calculate(value):\n    return int(value) * 2\n",
            encoding="utf-8",
        )
        (module_dir / "math.weavemark.md").write_text(
            """
@module company.math
@bind calculator language: python from: "./companions/default.py" symbol: calculate

@define calculate
  @phase execute
  @scope self
  @returns value
  @param value
    Number.
  @effect calculator read
  @body
    Calculate @{value}.
""".strip()
            + "\n",
            encoding="utf-8",
        )
        (tmp_path / "override.py").write_text(
            "def calculate(value):\n    return int(value) * 3\n",
            encoding="utf-8",
        )
        default_path = tmp_path / "default.weavemark.md"
        default_path.write_text(
            """
@use company.math exposing calculate
@execute functional
  allow_effects: [calculator]
@calculate value: "4" as: result
""".strip()
            + "\n",
            encoding="utf-8",
        )
        override_path = tmp_path / "override.weavemark.md"
        override_path.write_text(
            """
@use company.math exposing calculate
@bind calculator language: python from: "./override.py" symbol: calculate
@execute functional
  allow_effects: [calculator]
@calculate value: "4" as: result
""".strip()
            + "\n",
            encoding="utf-8",
        )

        protection = ProtectionContext.create(
            ProtectionSettings(enabled=False),
            entrypoint_dir=tmp_path,
            invocation_dir=tmp_path,
            approvals_path=tmp_path / "approvals.json",
        )
        compiled_default = await compile_file(
            default_path,
            protection_context=protection,
        )
        compiled_override = await compile_file(
            override_path,
            protection_context=protection,
        )

        assert compiled_default.errors == []
        assert compiled_default.bindings[0]["module"] == "company.math"
        assert compiled_default.execution["bindings"] == compiled_default.bindings
        default_callable = load_binding_callables(
            compiled_default,
            ["calculator"],
        )["calculator"]
        assert default_callable("4") == 8

        assert compiled_override.errors == []
        assert compiled_override.bindings == [
            {
                "name": "calculator",
                "language": "python",
                "from": "./override.py",
                "symbol": "calculate",
            }
        ]
        assert compiled_override.execution["bindings"] == compiled_override.bindings
        override_callable = load_binding_callables(
            compiled_override,
            ["calculator"],
        )["calculator"]
        assert override_callable("4") == 12

        protected = await compile_file(
            default_path,
            protection_context=ProtectionContext.create(
                ProtectionSettings(),
                entrypoint_dir=tmp_path,
                invocation_dir=tmp_path,
                approvals_path=tmp_path / "protected-approvals.json",
            ),
        )
        with pytest.raises(ProtectionError, match="Python code execution"):
            load_binding_callables(protected, ["calculator"])

    @pytest.mark.asyncio
    async def test_functional_engine_isolates_runtime_and_prior_results(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        from weavemark.engines import RuntimeConfig
        from weavemark.engines import functional as functional_module
        from weavemark.engines.functional import FunctionalEngine

        runtime_input = {"nested": {"score": 1}}

        def seed(payload):
            return payload

        def mutate(previous):
            previous["nested"]["score"] = 99
            return previous

        monkeypatch.setattr(
            functional_module,
            "load_binding_callables",
            lambda _result, _names: {"seed_data": seed, "mutate_data": mutate},
        )
        result = CompositionResult(
            composed_prompt="@{seeded}",
            execution={
                "type": "functional",
                "allow_effects": ["seed_data", "mutate_data"],
                "plan": {
                    "order": ["seeded", "mutated"],
                    "levels": [["seeded"], ["mutated"]],
                },
                "nodes": [
                    {
                        "id": "seeded",
                        "directive": "seed",
                        "effects": [{"name": "seed_data", "mode": "read"}],
                        "args": {
                            "positional": [],
                            "options": {"payload": "@{payload}"},
                        },
                        "params": [
                            {
                                "name": "payload",
                                "implicit": False,
                                "mode": "text",
                            }
                        ],
                        "body": "",
                        "as": "seeded",
                    },
                    {
                        "id": "mutated",
                        "directive": "mutate",
                        "effects": [{"name": "mutate_data", "mode": "read"}],
                        "args": {
                            "positional": [],
                            "options": {"previous": "@{seeded}"},
                        },
                        "params": [
                            {
                                "name": "previous",
                                "implicit": False,
                                "mode": "text",
                            }
                        ],
                        "body": "",
                        "as": "mutated",
                        "uses": ["seeded"],
                    },
                ],
            },
        )

        executed = await FunctionalEngine(client=MockLLMClient()).execute(
            result,
            RuntimeConfig(execution_variables={"payload": runtime_input}),
        )

        assert runtime_input == {"nested": {"score": 1}}
        assert executed.metadata["results"]["seeded"] == {"nested": {"score": 1}}
        assert executed.metadata["results"]["mutated"] == {"nested": {"score": 99}}
        assert executed.metadata["evidence"]["nodes"][0]["result"] == {
            "nested": {"score": 1}
        }
        assert executed.metadata["evidence"]["nodes"][1]["arguments"] == {
            "previous": {"nested": {"score": 1}}
        }

    @pytest.mark.asyncio
    async def test_functional_engine_rejects_unsnapshotable_placeholder(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        from weavemark.engines import RuntimeConfig
        from weavemark.engines import functional as functional_module
        from weavemark.engines.functional import FunctionalEngine

        deepcopy_called = False

        class Unsnapshotable:
            def __deepcopy__(self, memo):
                nonlocal deepcopy_called
                del memo
                deepcopy_called = True
                raise RuntimeError("copy disabled")

        monkeypatch.setattr(
            functional_module,
            "load_binding_callables",
            lambda _result, _names: {"identity": lambda payload: payload},
        )
        result = CompositionResult(
            composed_prompt="",
            execution={
                "type": "functional",
                "allow_effects": ["identity"],
                "plan": {"order": ["value"], "levels": [["value"]]},
                "nodes": [
                    {
                        "id": "value",
                        "directive": "identity",
                        "effects": [{"name": "identity", "mode": "read"}],
                        "args": {
                            "positional": [],
                            "options": {"payload": "@{payload}"},
                        },
                        "params": [
                            {
                                "name": "payload",
                                "implicit": False,
                                "mode": "text",
                            }
                        ],
                        "body": "",
                        "as": "value",
                    }
                ],
            },
        )

        with pytest.raises(
            RuntimeError,
            match=r"Cannot safely snapshot functional placeholder @\{payload\}",
        ):
            await FunctionalEngine(client=MockLLMClient()).execute(
                result,
                RuntimeConfig(
                    execution_variables={
                        "payload": {"safe": [1, {"malicious": Unsnapshotable()}]}
                    }
                ),
            )
        assert deepcopy_called is False

    @pytest.mark.asyncio
    async def test_functional_engine_snapshots_normal_nested_json_values(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        from weavemark.engines import RuntimeConfig
        from weavemark.engines import functional as functional_module
        from weavemark.engines.functional import FunctionalEngine

        runtime_input = {"items": [{"value": 1}, (2, 3)]}

        def mutate(payload):
            payload["items"][0]["value"] = 9
            payload["items"][1].append(4)
            return payload

        monkeypatch.setattr(
            functional_module,
            "load_binding_callables",
            lambda _result, _names: {"mutate": mutate},
        )
        result = CompositionResult(
            composed_prompt="@{value}",
            execution={
                "type": "functional",
                "scheduler": "sequential",
                "allow_effects": ["mutate"],
                "plan": {
                    "scheduler": "sequential",
                    "order": ["value"],
                    "levels": [["value"]],
                },
                "nodes": [
                    {
                        "id": "value",
                        "directive": "mutate",
                        "effects": [{"name": "mutate", "mode": "read"}],
                        "args": {
                            "positional": [],
                            "options": {"payload": "@{payload}"},
                        },
                        "params": [
                            {
                                "name": "payload",
                                "implicit": False,
                                "mode": "text",
                            }
                        ],
                        "body": "",
                        "as": "value",
                    }
                ],
            },
        )

        executed = await FunctionalEngine(client=MockLLMClient()).execute(
            result,
            RuntimeConfig(execution_variables={"payload": runtime_input}),
        )

        assert runtime_input == {"items": [{"value": 1}, (2, 3)]}
        assert executed.metadata["results"]["value"] == {
            "items": [{"value": 9}, [2, 3, 4]]
        }
        assert executed.output == "{'items': [{'value': 9}, [2, 3, 4]]}"

    @pytest.mark.asyncio
    async def test_functional_engine_rejects_tampered_graph_strict_uses(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        from weavemark.engines import functional as functional_module
        from weavemark.engines.functional import FunctionalEngine

        monkeypatch.setattr(
            functional_module,
            "load_binding_callables",
            lambda _result, _names: {"effect": lambda **_kwargs: {}},
        )
        result = CompositionResult(
            composed_prompt="",
            execution={
                "type": "functional",
                "scheduler": "graph-strict",
                "plan": {
                    "scheduler": "graph-strict",
                    "order": ["first", "second"],
                    "levels": [["first"], ["second"]],
                },
                "nodes": [
                    {
                        "id": "first",
                        "directive": "effect",
                        "effects": [{"name": "effect", "mode": "read"}],
                        "args": {"positional": [], "options": {}},
                        "params": [],
                        "body": "",
                        "as": "first",
                    },
                    {
                        "id": "second",
                        "directive": "effect",
                        "effects": [{"name": "effect", "mode": "read"}],
                        "args": {
                            "positional": [],
                            "options": {"payload": "@{first.value}"},
                        },
                        "params": [
                            {
                                "name": "payload",
                                "implicit": False,
                                "mode": "text",
                            }
                        ],
                        "body": "",
                        "as": "second",
                    },
                ],
            },
        )

        with pytest.raises(
            ValueError,
            match=(
                "graph-strict node 'second' references result\\(s\\) "
                "without explicit uses: first"
            ),
        ):
            await FunctionalEngine(client=MockLLMClient()).execute(result)

    @pytest.mark.asyncio
    async def test_functional_engine_rejects_tampered_dotted_result_name(
        self,
    ) -> None:
        from weavemark.engines.functional import FunctionalEngine

        result = CompositionResult(
            composed_prompt="@{first.result}",
            execution={
                "type": "functional",
                "scheduler": "sequential",
                "plan": {
                    "scheduler": "sequential",
                    "order": ["first.result"],
                    "levels": [["first.result"]],
                },
                "nodes": [
                    {
                        "id": "first.result",
                        "directive": "fetch",
                        "effects": [{"name": "data", "mode": "read"}],
                        "args": {"positional": [], "options": {}},
                        "params": [],
                        "body": "",
                        "as": "first.result",
                    }
                ],
            },
        )

        with pytest.raises(
            ValueError,
            match="result names must be simple identifiers: first.result",
        ):
            await FunctionalEngine(client=MockLLMClient()).execute(result)


# ═══════════════════════════════════════════════════════════════════
# Unit Tests: RuntimeConfig
# ═══════════════════════════════════════════════════════════════════


class TestRuntimeConfig:
    """Test RuntimeConfig loading."""

    def test_from_json(self):
        from weavemark.engines import RuntimeConfig

        config_data = {
            "engine": "tree-of-thought",
            "engine_config": {"branching_factor": 3},
            "prompts": {
                "generate": {"model": "gpt-4.1-mini", "temperature": 0.9},
                "evaluate": {"model": "gpt-4.1-mini", "temperature": 0.1},
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            f.flush()
            config = RuntimeConfig.from_json(Path(f.name))

        assert config.engine == "tree-of-thought"
        assert config.engine_config == {"branching_factor": 3}
        assert config.prompts["generate"].model == "gpt-4.1-mini"
        assert config.prompts["generate"].temperature == 0.9
        assert config.prompts["evaluate"].temperature == 0.1
        Path(f.name).unlink()

    def test_from_yaml(self):
        from weavemark.engines import RuntimeConfig

        yaml_text = (
            "engine: self-consistency\n"
            "engine_config:\n"
            "  samples: 5\n"
            "  aggregation: majority_vote\n"
            "prompts:\n"
            "  default:\n"
            "    model: gpt-4.1-mini\n"
            "    temperature: 0.8\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_text)
            f.flush()
            config = RuntimeConfig.from_yaml(Path(f.name))

        assert config.engine == "self-consistency"
        assert config.engine_config["samples"] == 5
        assert config.prompts["default"].model == "gpt-4.1-mini"
        assert config.prompts["default"].temperature == 0.8
        Path(f.name).unlink()

    def test_defaults(self):
        from weavemark.engines import RuntimeConfig, resolve_runtime_engine_name

        config = RuntimeConfig()
        assert config.engine is None
        assert config.engine_config == {}
        assert config.prompts == {}
        assert config.execution_variables == {}
        declared = CompositionResult(
            composed_prompt="",
            execution={"type": "reflection"},
        )
        assert resolve_runtime_engine_name(config, declared) == "reflection"
        assert (
            resolve_runtime_engine_name(RuntimeConfig(engine="chain"), declared)
            == "chain"
        )
        assert (
            resolve_runtime_engine_name(config, CompositionResult(composed_prompt="x"))
            == "single-call"
        )


# ═══════════════════════════════════════════════════════════════════
# Unit Tests: Engine wrappers with MockLLMClient
# ═══════════════════════════════════════════════════════════════════


class TestSingleCallEngine:
    @pytest.mark.asyncio
    async def test_basic_execution(self):
        from weavemark.engines.base import ExecutionResult
        from weavemark.engines.single_call import SingleCallEngine

        client = MockLLMClient(["The answer is 42."])
        engine = SingleCallEngine(client=client)

        result_cr = CompositionResult(
            composed_prompt="What is the meaning?",
            prompts={"default": "What is the meaning?"},
        )
        exec_result = await engine.execute(result_cr)

        assert isinstance(exec_result, ExecutionResult)
        assert exec_result.output == "The answer is 42."
        assert len(exec_result.steps) == 1
        assert len(client.calls) == 1

    @pytest.mark.asyncio
    async def test_executes_explicit_python_tool_binding(self, tmp_path: Path):
        from weavemark.engines.single_call import SingleCallEngine

        helper = tmp_path / "web_tools.py"
        helper.write_text(
            "async def search_web(query):\n"
            "    return {'query': query, 'items': ['relevant result']}\n",
            encoding="utf-8",
        )
        source = tmp_path / "monitor.weavemark.md"
        source.write_text("# Monitor\n", encoding="utf-8")
        composition = CompositionResult(
            composed_prompt="Find relevant current AI news.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "search_web",
                        "description": "Search the web.",
                        "parameters": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"],
                        },
                    },
                }
            ],
            bindings=[
                {
                    "capability_name": "search_web",
                    "language": "python",
                    "from": "./web_tools.py",
                    "symbol": "search_web",
                }
            ],
            execution={
                "type": "single-call",
                "max_iterations": 4,
                "max_tool_calls": 3,
            },
            source_path=str(source),
        )

        executed = await SingleCallEngine(client=BoundToolMockClient()).execute(
            composition
        )

        assert "relevant result" in executed.output
        assert executed.metadata["tool_call_count"] == 1
        assert executed.metadata["tool_call_budget"] == 3
        assert executed.metadata["tool_calls"][0]["name"] == "search_web"


@pytest.mark.parametrize("name_field", ("name", "capability", "capability_name", "tool"))
def test_compiler_binding_name_is_canonicalized(name_field: str) -> None:
    binding = {
        name_field: "search_web",
        "language": "python",
        "from": "./tools.py",
        "symbol": "search_web",
    }

    result = parse_composition_response(
        compiler_response("Search.", bindings=[binding])
    )

    assert result.errors == []
    assert result.bindings == [
        {
            "name": "search_web",
            "language": "python",
            "from": "./tools.py",
            "symbol": "search_web",
        }
    ]


class TestCollaborativeEngine:
    @pytest.mark.asyncio
    async def test_agent_handoff_runtime_config_collaborates_via_files(
        self,
        tmp_path: Path,
    ):
        from weavemark.engines.base import RuntimeConfig
        from weavemark.engines.collaborative import CollaborativeEngine

        client = MockLLMClient(["Initial draft", "Revised draft preserving notes"])
        engine = CollaborativeEngine(client=client)
        handoff_dir = tmp_path / "agent-turns"
        result_cr = CompositionResult(
            composed_prompt="shared context",
            prompts={
                "generate": "Write the first draft.",
                "continue": (
                    "Edited:\n@{edited_content}\n\nPrevious:\n@{original_content}\n"
                ),
            },
            execution={"type": "collaborative", "max_rounds": 1},
        )
        runtime_config = RuntimeConfig(
            engine="collaborative",
            engine_config={
                "agent_handoff_dir": str(handoff_dir),
                "agent_handoff_timeout_seconds": 5,
                "agent_handoff_poll_seconds": 0.01,
                "agent_handoff_announce": False,
            },
        )

        answer_task = asyncio.create_task(
            self._answer_agent_turn(
                handoff_dir,
                "Initial draft\n\nEditor note: add a practical close.",
            )
        )
        exec_result = await engine.execute(result_cr, runtime_config)
        await answer_task

        assert exec_result.output == "Revised draft preserving notes"
        assert [step.name for step in exec_result.steps] == [
            "generate",
            "user_edit_0",
            "continue_0",
        ]
        assert "Editor note: add a practical close." in exec_result.steps[1].response
        assert exec_result.metadata["rounds_completed"] == 1
        assert len(client.calls) == 2
        continue_prompt = client.calls[1]["messages"][0]["content"]
        assert "Editor note: add a practical close." in continue_prompt
        assert "Initial draft" in continue_prompt
        request = (handoff_dir / "turn-001-request.md").read_text(encoding="utf-8")
        assert "AI agent collaborating as the human/editor side" in request
        assert "`" in request and "turn-001-response.md" in request

    @pytest.mark.asyncio
    async def test_agent_handoff_callback_times_out_without_response(
        self,
        tmp_path: Path,
    ):
        from weavemark.engines.collaborative import AgentHandoffEditCallback

        callback = AgentHandoffEditCallback(
            tmp_path,
            timeout_seconds=0.01,
            poll_seconds=0.01,
            announce=False,
        )

        with pytest.raises(TimeoutError, match="agent collaboration response"):
            await callback.request_edit("Draft", "Round 1")

    @pytest.mark.asyncio
    async def test_invalid_agent_handoff_config_raises(self, tmp_path: Path):
        from weavemark.engines.base import RuntimeConfig
        from weavemark.engines.collaborative import CollaborativeEngine

        engine = CollaborativeEngine(client=MockLLMClient(["Draft"]))
        result_cr = CompositionResult(
            composed_prompt="shared context",
            prompts={
                "generate": "Write.",
                "continue": "Edited: @{edited_content}\nPrevious: @{original_content}",
            },
            execution={"type": "collaborative"},
        )
        runtime_config = RuntimeConfig(
            engine="collaborative",
            engine_config={
                "agent_handoff_dir": str(tmp_path),
                "agent_handoff_timeout_seconds": 0,
            },
        )

        with pytest.raises(ValueError, match="timeout"):
            await engine.execute(result_cr, runtime_config)

    async def _answer_agent_turn(
        self,
        handoff_dir: Path,
        response_text: str,
    ) -> None:
        request_path = handoff_dir / "turn-001-request.md"
        response_path = handoff_dir / "turn-001-response.md"
        for _ in range(500):
            if request_path.exists():
                response_path.write_text(response_text, encoding="utf-8")
                return
            await asyncio.sleep(0.01)
        raise AssertionError(f"Agent handoff request was not created: {request_path}")


class TestSelfConsistencyEngine:
    @pytest.mark.asyncio
    async def test_majority_vote(self):
        from weavemark.engines.self_consistency import SelfConsistencyEngine

        client = MockLLMClient(["Paris", "Paris", "London"])
        engine = SelfConsistencyEngine(client=client)

        result_cr = CompositionResult(
            composed_prompt="Capital of France?",
            prompts={"default": "Capital of France?"},
            execution={"type": "self-consistency", "samples": 3},
        )
        exec_result = await engine.execute(result_cr)

        assert exec_result.output == "Paris"
        assert len(client.calls) == 3


class TestTreeOfThoughtEngine:
    """Tests for the simplified tree-of-thought engine."""

    @pytest.mark.asyncio
    async def test_three_stage_pipeline(self):
        from ellements.execution import Evaluation

        from weavemark.engines.tree_of_thought import SimplifiedTreeOfThoughtEngine

        responses = [
            "Path A solution",  # generate_0
            "Path B solution",  # generate_1
            "Path C solution",  # generate_2
            "Detailed solution B",  # synthesize (after structured evaluation)
        ]
        structured = [Evaluation(score=0.9, reasoning="Path B is best")]
        client = MockLLMClient(responses, structured_responses=structured)
        engine = SimplifiedTreeOfThoughtEngine(client=client)

        result_cr = CompositionResult(
            composed_prompt="shared context",
            prompts={
                "generate": "Solve the problem",
                "evaluate": "Evaluate: @{candidates}",
                "synthesize": "Elaborate: @{best_approach}",
            },
            execution={"type": "simplified-tree-of-thought", "branching_factor": 3},
        )
        exec_result = await engine.execute(result_cr)

        assert exec_result.output == "Detailed solution B"
        # 3 generate (complete) + 1 evaluate (complete_structured) + 1 synthesize (complete)
        assert len(client.calls) == 5
        assert len(exec_result.steps) == 5

    @pytest.mark.asyncio
    async def test_config_override(self):
        """RuntimeConfig engine_config overrides @execute params."""
        from ellements.execution import Evaluation

        from weavemark.engines.base import RuntimeConfig
        from weavemark.engines.tree_of_thought import SimplifiedTreeOfThoughtEngine

        responses = ["g1", "g2", "g3", "g4", "g5", "synth"]
        structured = [Evaluation(score=0.9, reasoning="g3 is best")]
        client = MockLLMClient(responses, structured_responses=structured)
        engine = SimplifiedTreeOfThoughtEngine(client=client)

        result_cr = CompositionResult(
            composed_prompt="ctx",
            prompts={
                "generate": "Solve it",
                "evaluate": "Eval @{candidates}",
                "synthesize": "Synth @{best_approach}",
            },
            execution={"type": "simplified-tree-of-thought", "branching_factor": 2},
        )
        runtime_config = RuntimeConfig(
            engine="simplified-tree-of-thought",
            engine_config={"branching_factor": 5},
        )
        await engine.execute(result_cr, runtime_config)

        # With branching_factor=5, there should be 5 generate calls at the
        # generate temperature (0.9 by default for the simple ToT mode).
        gen_calls = [
            c
            for c in client.calls
            if c["kind"] == "complete" and c["temperature"] == 0.9
        ]
        assert len(gen_calls) == 5


class TestFullTreeOfThoughtEngine:
    """Tests for the FULL tree-of-thought engine (BFS/DFS)."""

    @pytest.mark.asyncio
    async def test_full_tot_basic(self):
        from ellements.execution import Evaluation

        from weavemark.engines.tree_of_thought import TreeOfThoughtEngine

        # depth=1, branching=3 → 3 thoughts (complete) + 3 evaluations
        # (complete_structured) + 1 synthesize (complete) = 4 text + 3 structured
        responses = [
            "Step 1: calc A",
            "Step 1: calc B",
            "Step 1: calc C",
            "Final answer: 42",
        ]
        structured = [
            Evaluation(score=0.9, reasoning="A is solid"),
            Evaluation(score=0.5, reasoning="B is uncertain"),
            Evaluation(score=0.1, reasoning="C is hopeless"),
        ]
        client = MockLLMClient(responses, structured_responses=structured)
        engine = TreeOfThoughtEngine(client=client)

        result_cr = CompositionResult(
            composed_prompt="ctx",
            prompts={
                "thought_step": "Given:\n@{state}\n\nNext step.",
                "evaluate_step": "Evaluate:\n@{state}\n\nsure/maybe/impossible.",
                "synthesize": "Best path:\n@{best_path}\n\nAnswer.",
            },
            execution={
                "type": "tree-of-thought",
                "max_depth": 1,
                "branching_factor": 3,
                "beam_width": 2,
            },
        )
        exec_result = await engine.execute(result_cr)

        assert exec_result.output  # Got a non-empty result
        assert exec_result.steps[-1].name == "synthesize"


class TestReflectionEngine:
    @pytest.mark.asyncio
    async def test_generates_and_reflects(self):
        from ellements.execution import CritiqueResult

        from weavemark.engines.reflection import ReflectionEngine

        responses = ["Draft answer"]
        structured = [CritiqueResult(is_satisfied=True, issues=[])]
        client = MockLLMClient(responses, structured_responses=structured)
        engine = ReflectionEngine(client=client)

        result_cr = CompositionResult(
            composed_prompt="ctx",
            prompts={
                "generate": "Write about X",
                "critique": "Critique: @{response}",
                "revise": "Fix: @{response} — @{issues}",
            },
            execution={"type": "reflection", "max_rounds": 3},
        )
        exec_result = await engine.execute(result_cr)

        assert exec_result.output == "Draft answer"
        # 1 generate (complete) + 1 critique (complete_structured) — stopped early
        assert len(client.calls) == 2


class TestBaseEngineConfigMerge:
    """Test that BaseEngine._build_strategy_config merges correctly."""

    def test_spec_only(self):
        from weavemark.engines.base import BaseEngine

        engine = BaseEngine()
        result = CompositionResult(
            composed_prompt="x",
            execution={"type": "tot", "branching_factor": 3, "max_depth": 2},
        )
        config = engine._build_strategy_config(result)
        assert config["branching_factor"] == 3
        assert config["max_depth"] == 2
        assert "type" not in config  # type is stripped

    def test_runtime_overrides_spec(self):
        from weavemark.engines.base import BaseEngine, RuntimeConfig

        engine = BaseEngine()
        result = CompositionResult(
            composed_prompt="x",
            execution={"type": "tot", "branching_factor": 3},
        )
        runtime = RuntimeConfig(engine_config={"branching_factor": 5, "extra": True})
        config = engine._build_strategy_config(result, runtime)
        assert config["branching_factor"] == 5  # runtime wins
        assert config["extra"] is True  # new key from runtime

    def test_empty_spec_and_runtime(self):
        from weavemark.engines.base import BaseEngine

        engine = BaseEngine()
        result = CompositionResult(composed_prompt="x")
        config = engine._build_strategy_config(result)
        assert config == {"model": "gpt-5.5"}


# ═══════════════════════════════════════════════════════════════════
# Integration Tests — require OPENAI_API_KEY
# ═══════════════════════════════════════════════════════════════════

_skip = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — requires a real LLM",
)


@_skip
class TestPromptDirectiveE2E:
    """End-to-end tests for the @prompt directive."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_named_prompts(self):
        """@prompt directives produce named prompts in the output."""
        from weavemark.controller import WeaveMarkConfig, WeaveMarkController

        spec = (
            "You are a problem solver.\n\n"
            "@prompt generate\n"
            "  Generate 3 approaches to solving the problem.\n\n"
            "@prompt evaluate\n"
            "  Evaluate and rank the following approaches.\n"
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(spec, {})

        assert result.prompts, "Should produce named prompts"
        assert len(result.prompts) >= 2
        assert "generate" in result.prompts
        assert "evaluate" in result.prompts

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_execution_directive(self):
        """@execute directive produces execution metadata."""
        from weavemark.controller import WeaveMarkConfig, WeaveMarkController

        spec = (
            "You are a solver.\n\n"
            "@execute self-consistency\n"
            "  samples: 5\n"
            "  aggregation: majority_vote\n"
        )
        controller = WeaveMarkController(WeaveMarkConfig())
        result = await controller.compose(spec, {})

        assert result.execution, "Should have execution metadata"
        assert result.execution.get("type") == "self-consistency"


# ═══════════════════════════════════════════════════════════════════
# Prompt validation tests
# ═══════════════════════════════════════════════════════════════════


class TestPromptValidation:
    """Verify engines reject specs missing required @prompt blocks."""

    @pytest.mark.asyncio
    async def test_tree_of_thought_missing_prompts(self):
        """Full ToT engine rejects spec with only default prompt."""
        from weavemark.engines.tree_of_thought import TreeOfThoughtEngine

        engine = TreeOfThoughtEngine(client=MockLLMClient(["x"] * 20))
        result = CompositionResult(
            composed_prompt="solve this",
            raw_response="",
            prompts={"default": "solve this"},
        )
        with pytest.raises(PromptKeyMissingError, match="thought_step"):
            await engine.execute(result)

    @pytest.mark.asyncio
    async def test_simplified_tot_missing_prompts(self):
        """Simplified ToT engine rejects spec with only default prompt."""
        from weavemark.engines.tree_of_thought import SimplifiedTreeOfThoughtEngine

        engine = SimplifiedTreeOfThoughtEngine(client=MockLLMClient(["x"] * 5))
        result = CompositionResult(
            composed_prompt="solve this",
            raw_response="",
            prompts={"default": "solve this"},
        )
        with pytest.raises(PromptKeyMissingError, match="generate"):
            await engine.execute(result)

    @pytest.mark.asyncio
    async def test_tree_of_thought_with_all_prompts(self):
        """Full ToT engine accepts spec with all required prompts."""
        from ellements.execution import Evaluation

        from weavemark.engines.tree_of_thought import TreeOfThoughtEngine

        client = MockLLMClient(
            responses=["x"] * 20,
            structured_responses=[
                Evaluation(score=0.5, reasoning="ok") for _ in range(20)
            ],
        )
        engine = TreeOfThoughtEngine(client=client)
        result = CompositionResult(
            composed_prompt="",
            raw_response="",
            prompts={
                "thought_step": "Given: @{state}\nNext step.",
                "evaluate_step": "Evaluate: @{state}",
                "synthesize": "Best: @{best_path}",
            },
            execution={"max_depth": 1, "branching_factor": 1, "beam_width": 1},
        )
        exec_result = await engine.execute(result)
        assert exec_result.output

    @pytest.mark.asyncio
    async def test_reflection_missing_prompts(self):
        """Reflection engine rejects spec missing critique/revise."""
        from weavemark.engines.reflection import ReflectionEngine

        engine = ReflectionEngine(client=MockLLMClient(["x"] * 5))
        result = CompositionResult(
            composed_prompt="write something",
            raw_response="",
            prompts={"default": "write something", "generate": "write"},
        )
        with pytest.raises(PromptKeyMissingError, match="critique"):
            await engine.execute(result)

    @pytest.mark.asyncio
    async def test_self_consistency_with_default_only(self):
        """Self-consistency only needs default — should pass."""
        from weavemark.engines.self_consistency import SelfConsistencyEngine

        engine = SelfConsistencyEngine(client=MockLLMClient(["ans"] * 5))
        result = CompositionResult(
            composed_prompt="What is 2+2?",
            raw_response="",
        )
        exec_result = await engine.execute(result)
        assert exec_result.output

    @pytest.mark.asyncio
    async def test_single_call_with_default_only(self):
        """Single-call only needs default — should pass."""
        from weavemark.engines.single_call import SingleCallEngine

        engine = SingleCallEngine(client=MockLLMClient(["ok"]))
        result = CompositionResult(
            composed_prompt="Hello",
            raw_response="",
        )
        exec_result = await engine.execute(result)
        assert exec_result.output == "ok"
