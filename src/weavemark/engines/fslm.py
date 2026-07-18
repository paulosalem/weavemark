"""Finite-State Linguistic Machine execution engine."""

from __future__ import annotations

import inspect
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from ellements.core import LLMClient, PromptKeyMissingError
from ellements.execution import OnStepCallback, StepRecord
from pydantic import BaseModel, ConfigDict, Field

from ..compilation.result import CompositionResult
from ..protection import ProtectionContext
from .base import (
    ArtifactCallback,
    BaseEngine,
    ExecutionResult,
    RuntimeConfig,
    resolve_call_settings,
)

_MACHINE_CONFIG_KEY = "machine"
_DEFAULT_MAX_STEPS = 12
_DEFAULT_HISTORY_LIMIT = 8
_MISSING = object()


class _FSLMDecision(BaseModel):
    """Provider-safe schema for prompt-backed FSLM decisions."""

    model_config = ConfigDict(extra="forbid")

    id: str
    allowed: bool
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class _FSLMApi:
    """Late-bound `ellements.fslm` runtime symbols.

    The engine is importable without the optional FSLM package; execution gives a
    precise installation error if the package is unavailable.
    """

    ActionResult: Any
    DecisionResult: Any
    FSLMContext: Any
    FSLMEvent: Any
    FSLMKernel: Any
    MachineDefinition: Any
    MachineSpec: Any
    OutputRecord: Any
    RuntimeBindings: Any
    load_machine_definition: Any


@dataclass(frozen=True)
class _PromptRequirement:
    """One prompt required by the FSLM prompt contract."""

    key: str
    kind: str
    source: str


class FSLMEngine(BaseEngine):
    """Execute existing `ellements.fslm` machines with WeaveMark prompts.

    WeaveMark owns the prompt library; the FSLM spec owns the state graph.  The
    engine validates the prompt contract before creating the initial snapshot,
    then injects machine/event/history context into each prompt-backed guard,
    invariant, action, state hook, and output.
    """

    async def execute(
        self,
        result: CompositionResult,
        config: RuntimeConfig | None = None,
        on_step: OnStepCallback | None = None,
        on_artifact: ArtifactCallback | None = None,
    ) -> ExecutionResult:
        self._require_text_only(result, "fslm")
        api = _load_fslm_api()
        engine_config = self._build_strategy_config(result, config)
        if "runner" in engine_config:
            raise ValueError(
                "The WeaveMark FSLM engine is event-driven and does not support "
                "`runner`. Supply `initial_event` or an ordered `events` list. "
                "Autonomous transition selection is not implemented."
            )
        prompt_contract = (
            str(engine_config.get("prompt_contract", "strict")).strip().lower()
        )
        if prompt_contract not in {"strict", "permissive"}:
            raise ValueError(
                "FSLM prompt_contract must be `strict` or `permissive`, "
                f"not {prompt_contract!r}."
            )
        base_dir = _path_or_none(engine_config.get("base_dir"))
        _authorize_fslm_sources(
            engine_config,
            base_dir,
            config.protection if config is not None else result.protection,
        )
        runtime_bindings = _runtime_bindings_or_none(api, engine_config.get("bindings"))
        definition = _load_machine_definition(
            api,
            engine_config,
            base_dir,
            runtime_bindings,
        )

        prompts = dict(result.prompts)
        requirements = _collect_prompt_requirements(definition.spec)
        if prompt_contract == "strict":
            _validate_prompt_contract(prompts, requirements)

        events = _events_from_config(api, engine_config)
        if not events:
            raise ValueError("FSLM execution requires `initial_event` or `events`.")

        runtime = _PromptBackedFSLMRuntime(
            api=api,
            definition=definition,
            prompts=prompts,
            client=self.client,
            runtime_config=config,
            result=result,
            engine_config=engine_config,
            tools=result.tools,
            on_step=on_step,
        )
        kernel = api.FSLMKernel(
            definition,
            guard_evaluator=runtime,
            invariant_checker=runtime,
            action_executor=runtime,
        )

        snapshot = definition.initial_snapshot(
            machine_id=_optional_str(engine_config.get("machine_id")),
            variables=_initial_variables(config, engine_config),
            random_seed=_optional_int(engine_config.get("random_seed")),
        )

        max_steps = _max_steps(engine_config, definition.spec, len(events))
        step_results: list[Any] = []
        status = "awaiting_event"

        for index, event in enumerate(events):
            if index >= max_steps:
                status = "max_steps"
                break
            if _is_terminal(definition.spec, snapshot.current_state):
                status = "terminal"
                break

            await runtime.run_state_prompt(snapshot, event)
            step_result = await kernel.step(snapshot, event)
            transition = _selected_transition(definition.spec, step_result)
            step_result = await runtime.materialize_outputs(
                step_result,
                transition,
                event,
            )

            runtime.record_machine_step(step_result, event)
            runtime.record_history(step_result, event)
            step_results.append(step_result)
            snapshot = step_result.new_snapshot
            status = _status_after_step(definition.spec, step_result, engine_config)
            if status in {"blocked", "no_transition", "terminal"}:
                break
        else:
            status = (
                "terminal"
                if _is_terminal(definition.spec, snapshot.current_state)
                else "awaiting_event"
            )

        output = _primary_output(step_results)
        metadata = {
            "engine": "fslm",
            "status": status,
            "machine": {
                "name": definition.spec.name,
                "description": definition.spec.description,
                "version": definition.spec.version,
            },
            "prompt_contract": {
                "mode": prompt_contract,
                "required": [
                    {
                        "key": item.key,
                        "kind": item.kind,
                        "source": item.source,
                    }
                    for item in requirements
                ],
            },
            "events": [event.model_dump(mode="json") for event in events],
            "steps": [step.model_dump(mode="json") for step in step_results],
            "final_snapshot": snapshot.model_dump(mode="json"),
        }
        return ExecutionResult(
            output=output,
            steps=runtime.steps,
            metadata=metadata,
        )


class _PromptBackedFSLMRuntime:
    """FSLM guard/invariant/action/output hooks backed by WeaveMark prompts."""

    def __init__(
        self,
        *,
        api: _FSLMApi,
        definition: Any,
        prompts: Mapping[str, str],
        client: LLMClient,
        runtime_config: RuntimeConfig | None,
        result: CompositionResult,
        engine_config: Mapping[str, Any],
        tools: list[dict[str, Any]],
        on_step: OnStepCallback | None,
    ) -> None:
        self.api = api
        self.definition = definition
        self.prompts = prompts
        self.client = client
        self.runtime_config = runtime_config
        self.result = result
        self.engine_config = engine_config
        self.tool_schemas = _tool_schemas_by_name(tools)
        self.on_step = on_step
        self.steps: list[StepRecord] = []
        self.history: list[dict[str, Any]] = []
        self.state_notes: list[dict[str, Any]] = []

    async def evaluate_guard(
        self,
        guard: Any,
        *,
        spec: Any,
        snapshot: Any,
        event: Any,
    ) -> Any:
        """Evaluate an NL guard through its WeaveMark prompt."""

        prompt_key = _prompt_key("guard", guard, guard.id)
        decision = await self._complete_decision(
            prompt_key,
            expected_id=guard.id,
            rule_text=guard.text,
            kind="guard",
            item=guard,
            spec=spec,
            snapshot=snapshot,
            event=event,
        )
        return self.api.DecisionResult(
            id=guard.id,
            allowed=decision.allowed,
            confidence=decision.confidence,
            evidence=decision.evidence,
            uncertainties=decision.uncertainties,
            alternatives=decision.alternatives,
            metadata={"prompt_key": prompt_key},
        )

    async def check_invariant(
        self,
        invariant: Any,
        *,
        spec: Any,
        snapshot: Any,
        event: Any,
    ) -> Any:
        """Evaluate an NL invariant through its WeaveMark prompt."""

        prompt_key = _prompt_key("invariant", invariant, invariant.id)
        decision = await self._complete_decision(
            prompt_key,
            expected_id=invariant.id,
            rule_text=invariant.text,
            kind="invariant",
            item=invariant,
            spec=spec,
            snapshot=snapshot,
            event=event,
        )
        return self.api.DecisionResult(
            id=invariant.id,
            allowed=decision.allowed,
            confidence=decision.confidence,
            evidence=decision.evidence,
            uncertainties=decision.uncertainties,
            alternatives=decision.alternatives,
            metadata={"prompt_key": prompt_key},
        )

    async def execute_action(
        self,
        action: Any,
        *,
        spec: Any,
        snapshot: Any,
        event: Any,
    ) -> Any:
        """Execute or plan one selected action."""

        if action.kind == "nl":
            action_name = _action_name(action)
            prompt_key = _prompt_key("action", action, action_name)
            response = await self._complete_text(
                prompt_key,
                kind="action",
                item=action,
                spec=spec,
                snapshot=snapshot,
                event=event,
                default_temperature=0.2,
                system=(
                    "You execute natural-language FSLM actions. Return only "
                    "the action result content; do not restate the full runtime "
                    "context."
                ),
            )
            return self.api.ActionResult(
                action_name=action_name,
                tool=action.tool or action.ref or "nl",
                status="executed",
                output={"text": response, "prompt_key": prompt_key},
                message="prompt-backed natural-language action",
            )

        if action.kind == "deterministic" and action.ref:
            payload = await self._invoke_binding(
                action.ref, "action", snapshot, event, action.args
            )
            return _action_from_payload(self.api, action, payload)

        if action.kind == "tool" and action.tool and self.definition.bindings.tools:
            arguments = self._tool_arguments(action, event)
            ctx = self._fsm_context(snapshot, event)
            output = await ctx.call_tool(action.tool, **arguments)
            return self.api.ActionResult(
                action_name=_action_name(action),
                tool=action.tool,
                status="executed",
                output=output if isinstance(output, dict) else {"value": output},
            )

        if action.kind == "tool" and action.tool:
            arguments = self._tool_arguments(action, event)
            return self.api.ActionResult(
                action_name=_action_name(action),
                tool=action.tool,
                status="planned",
                output={"arguments": arguments},
                message=(
                    "tool action planned but no ToolRegistry binding was configured"
                ),
            )

        return self.api.ActionResult(
            action_name=_action_name(action),
            tool=action.tool or action.ref or "python",
            status="planned",
            message="action planned but no executor/binding was configured",
        )

    async def run_state_prompt(self, snapshot: Any, event: Any) -> None:
        """Run a state-local prompt if one was explicitly supplied."""

        state = self.definition.spec.states[snapshot.current_state]
        prompt_key = _state_prompt_key(state)
        if prompt_key not in self.prompts:
            return
        response = await self._complete_text(
            prompt_key,
            kind="state",
            item=state,
            spec=self.definition.spec,
            snapshot=snapshot,
            event=event,
            default_temperature=0.2,
            system=(
                "You perform state-local FSLM reasoning. Return concise state "
                "notes that can guide subsequent guard, action, and output "
                "prompts."
            ),
        )
        self.state_notes.append(
            {
                "state": snapshot.current_state,
                "event_id": event.id,
                "prompt_key": prompt_key,
                "response": response,
            }
        )

    async def materialize_outputs(
        self,
        step_result: Any,
        transition: Any | None,
        event: Any,
    ) -> Any:
        """Replace NL output instructions with prompt-generated output payloads."""

        if transition is None or not step_result.outputs:
            return step_result

        materialized = []
        changed = False
        for index, output_record in enumerate(step_result.outputs):
            output_spec = (
                transition.emits[index] if index < len(transition.emits) else None
            )
            if output_spec is None or output_spec.kind != "nl":
                materialized.append(output_record)
                continue
            prompt_key = _prompt_key("output", output_spec, output_spec.type)
            response = await self._complete_text(
                prompt_key,
                kind="output",
                item=output_spec,
                spec=self.definition.spec,
                snapshot=step_result.new_snapshot,
                event=event,
                step_result=step_result,
                transition=transition,
                default_temperature=0.2,
                system=(
                    "You produce FSLM outputs. Return only the output content "
                    "requested by the prompt."
                ),
            )
            materialized.append(
                self.api.OutputRecord(
                    type=output_record.type,
                    payload={"text": response, "prompt_key": prompt_key},
                    description=output_record.description,
                    destination=output_record.destination,
                )
            )
            changed = True
        if not changed:
            return step_result
        return step_result.model_copy(update={"outputs": materialized})

    def record_machine_step(self, step_result: Any, event: Any) -> None:
        """Record one machine transition as an execution step."""

        record = StepRecord(
            name="fslm.step",
            prompt_key="machine",
            response=step_result.status,
            metadata={
                "event": event.model_dump(mode="json"),
                "source_state": step_result.source_state,
                "target_state": step_result.target_state,
                "selected_transition": step_result.selected_transition,
                "violations": step_result.violations,
            },
        )
        self._record_step(record)

    def record_history(self, step_result: Any, event: Any) -> None:
        """Keep a compact rolling history for subsequent prompt calls."""

        self.history.append(_compact_step(step_result, event))
        limit = (
            _optional_int(self.engine_config.get("history_limit"))
            or _DEFAULT_HISTORY_LIMIT
        )
        if limit > 0 and len(self.history) > limit:
            self.history = self.history[-limit:]

    def _tool_arguments(self, action: Any, event: Any) -> dict[str, Any]:
        arguments = dict(action.arguments)
        input_names = action.args.get("input_names", [])
        input_defaults = action.args.get("input_defaults", {})
        allowed_names = self.tool_schemas.get(action.tool or "")
        for name in input_names if isinstance(input_names, list) else []:
            if allowed_names is not None and name not in allowed_names:
                continue
            if name in arguments:
                continue
            value = _event_input_value(event, str(name), input_defaults)
            if value is not _MISSING:
                arguments[str(name)] = value
        return arguments

    async def _complete_decision(
        self,
        prompt_key: str,
        *,
        expected_id: str,
        rule_text: str,
        kind: str,
        item: Any,
        spec: Any,
        snapshot: Any,
        event: Any,
    ) -> _FSLMDecision:
        prompt = self._prompt_text(prompt_key)
        context = self._context_payload(
            kind=kind,
            item=item,
            spec=spec,
            snapshot=snapshot,
            event=event,
            extra={"rule_text": rule_text},
        )
        model, temperature, call_settings = self._call_options(
            prompt_key,
            f"{kind}_temperature",
            0.0,
        )
        raw_decision = await self.client.complete_structured(
            _messages(
                prompt,
                context,
                system=(
                    "You evaluate finite-state linguistic-machine decisions. "
                    "Return only the structured schema. Be conservative: if "
                    "the runtime context does not satisfy the rule, set "
                    "allowed=false and explain the uncertainty."
                ),
            ),
            response_model=_FSLMDecision,
            model=model,
            temperature=temperature,
        )
        decision = (
            raw_decision
            if isinstance(raw_decision, _FSLMDecision)
            else _FSLMDecision.model_validate(raw_decision)
        )
        if decision.id != expected_id:
            decision = decision.model_copy(update={"id": expected_id})
        self._record_step(
            StepRecord(
                name=f"fslm.{kind}",
                prompt_key=prompt_key,
                response=json.dumps(decision.model_dump(mode="json"), sort_keys=True),
                metadata={
                    "id": expected_id,
                    "allowed": decision.allowed,
                    "confidence": decision.confidence,
                    "call_settings": call_settings,
                },
            )
        )
        return decision

    async def _complete_text(
        self,
        prompt_key: str,
        *,
        kind: str,
        item: Any,
        spec: Any,
        snapshot: Any,
        event: Any,
        default_temperature: float,
        system: str,
        step_result: Any | None = None,
        transition: Any | None = None,
    ) -> str:
        prompt = self._prompt_text(prompt_key)
        context = self._context_payload(
            kind=kind,
            item=item,
            spec=spec,
            snapshot=snapshot,
            event=event,
            step_result=step_result,
            transition=transition,
        )
        model, temperature, call_settings = self._call_options(
            prompt_key,
            f"{kind}_temperature",
            default_temperature,
        )
        response = str(
            await self.client.complete(
                _messages(prompt, context, system=system),
                model=model,
                temperature=temperature,
            )
        )
        self._record_step(
            StepRecord(
                name=f"fslm.{kind}",
                prompt_key=prompt_key,
                response=response,
                metadata={
                    "state": snapshot.current_state,
                    "event_type": event.type,
                    "item": _item_identity(kind, item),
                    "call_settings": call_settings,
                },
            )
        )
        return response

    async def _invoke_binding(
        self,
        ref: str,
        category: str,
        snapshot: Any,
        event: Any,
        args: Mapping[str, Any],
    ) -> Any:
        fn = self.definition.bindings.resolve(ref, category)
        result = _invoke_callable(fn, self._fsm_context(snapshot, event), dict(args))
        if inspect.isawaitable(result):
            return await result
        return result

    def _fsm_context(self, snapshot: Any, event: Any) -> Any:
        return self.api.FSLMContext(
            spec=self.definition.spec,
            definition=self.definition,
            state=self.definition.spec.states[snapshot.current_state],
            transition=None,
            snapshot=snapshot,
            event=event,
            vars=snapshot.variables,
            step_id="",
            metadata={"history": list(self.history)},
        )

    def _context_payload(
        self,
        *,
        kind: str,
        item: Any,
        spec: Any,
        snapshot: Any,
        event: Any,
        extra: Mapping[str, Any] | None = None,
        step_result: Any | None = None,
        transition: Any | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": kind,
            "machine": {
                "name": spec.name,
                "description": spec.description,
                "version": spec.version,
                "initial": spec.initial,
            },
            "state": _model_dump(spec.states[snapshot.current_state]),
            "snapshot": snapshot.model_dump(mode="json"),
            "event": event.model_dump(mode="json"),
            "item": _model_dump(item),
            "candidate_transitions": _candidate_transitions(spec, snapshot, event),
            "history": list(self.history),
            "state_notes": list(self.state_notes),
        }
        if transition is not None:
            payload["transition"] = _model_dump(transition)
        if step_result is not None:
            payload["step_result"] = step_result.model_dump(mode="json")
        if extra:
            payload.update(dict(extra))
        return payload

    def _prompt_text(self, key: str) -> str:
        prompt = self.prompts.get(key)
        if prompt is None:
            raise PromptKeyMissingError(
                f"FSLM requires a prompt named {key!r}. "
                f"Available: {sorted(self.prompts.keys())}."
            )
        return prompt

    def _call_options(
        self,
        prompt_key: str,
        temperature_key: str,
        default_temperature: float,
    ) -> tuple[str, float, dict[str, Any]]:
        stage = temperature_key.removesuffix("_temperature")
        settings = resolve_call_settings(
            self.result,
            self.runtime_config,
            prompt_key=prompt_key,
            stage=stage,
        )
        temperature = settings.temperature
        if settings.temperature_source == "built-in default":
            temperature = default_temperature
        effective_temperature = (
            temperature if temperature is not None else default_temperature
        )
        metadata = settings.metadata()
        metadata["temperature"] = effective_temperature
        if settings.temperature_source == "built-in default":
            metadata["temperature_source"] = f"fslm.{stage} default"
        return settings.model, effective_temperature, metadata

    def _record_step(self, step: StepRecord) -> None:
        self.steps.append(step)
        if self.on_step is not None:
            self.on_step(step)


def _load_fslm_api() -> _FSLMApi:
    try:
        from ellements.fslm import (
            ActionResult,
            DecisionResult,
            FSLMContext,
            FSLMEvent,
            FSLMKernel,
            MachineDefinition,
            MachineSpec,
            OutputRecord,
            RuntimeBindings,
            load_machine_definition,
        )
    except ImportError as exc:
        raise ImportError(
            "The WeaveMark FSLM engine requires `ellements.fslm`. "
            "Install the public `ellements` package, then retry `@execute fslm`."
        ) from exc
    return _FSLMApi(
        ActionResult=ActionResult,
        DecisionResult=DecisionResult,
        FSLMContext=FSLMContext,
        FSLMEvent=FSLMEvent,
        FSLMKernel=FSLMKernel,
        MachineDefinition=MachineDefinition,
        MachineSpec=MachineSpec,
        OutputRecord=OutputRecord,
        RuntimeBindings=RuntimeBindings,
        load_machine_definition=load_machine_definition,
    )


def _load_machine_definition(
    api: _FSLMApi,
    engine_config: Mapping[str, Any],
    base_dir: Path | None,
    runtime_bindings: Any | None,
) -> Any:
    machine_spec = engine_config.get("machine_spec")
    if isinstance(machine_spec, Mapping):
        spec = api.MachineSpec.model_validate(dict(machine_spec))
        return api.MachineDefinition(
            spec,
            runtime_bindings or api.RuntimeBindings(),
        )
    machine_ref = _required_machine_ref(engine_config)
    return api.load_machine_definition(
        _resolve_reference(machine_ref, base_dir),
        bindings=runtime_bindings,
        binding_modules=_resolve_binding_modules(
            engine_config.get("binding_modules"),
            base_dir,
        ),
    )


def _authorize_fslm_sources(
    engine_config: Mapping[str, Any],
    base_dir: Path | None,
    protection: ProtectionContext | None,
) -> None:
    if protection is None or not protection.enabled:
        return
    if isinstance(engine_config.get("machine_spec"), Mapping):
        return

    machine_reference = _required_machine_ref(engine_config)
    resolved_reference = _resolve_reference(machine_reference, base_dir)
    machine_path = _reference_path(resolved_reference)
    if machine_path is not None and machine_path.is_file():
        protection.authorize_read(
            machine_path,
            reason=f"FSLM machine definition {machine_reference!r}",
        )
        if machine_path.suffix == ".py":
            protection.authorize_python(
                machine_reference,
                path=machine_path,
                reason="Loading a Python FSLM machine imports and executes its code.",
            )
        elif machine_path.suffix in {".yaml", ".yml"}:
            _authorize_yaml_binding_imports(machine_path, protection)
    else:
        protection.authorize_python(
            machine_reference,
            reason="Loading a module-referenced FSLM machine imports Python code.",
        )

    for binding_reference in _resolve_binding_modules(
        engine_config.get("binding_modules"),
        base_dir,
    ) or []:
        binding_path = Path(str(binding_reference)).expanduser()
        if binding_path.is_file():
            protection.authorize_read(
                binding_path,
                reason=f"FSLM binding module {binding_reference!r}",
            )
            protection.authorize_python(
                str(binding_reference),
                path=binding_path,
                reason="Loading an FSLM binding module imports and executes its code.",
            )
        else:
            protection.authorize_python(
                str(binding_reference),
                reason="Loading an FSLM binding module imports Python code.",
            )


def _authorize_yaml_binding_imports(
    machine_path: Path,
    protection: ProtectionContext,
) -> None:
    data = yaml.safe_load(machine_path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        return
    bindings = data.get("bindings")
    if not isinstance(bindings, Mapping):
        return
    imports = bindings.get("imports")
    if not isinstance(imports, Mapping):
        return
    for module_reference in imports.values():
        reference = str(module_reference)
        candidate = (machine_path.parent / reference).expanduser().resolve()
        if candidate.is_file():
            protection.authorize_read(
                candidate,
                reason=f"Python binding imported by {machine_path.name}",
            )
            protection.authorize_python(
                reference,
                path=candidate,
                reason=f"FSLM machine {machine_path.name} imports a Python binding.",
            )
        else:
            protection.authorize_python(
                reference,
                reason=(
                    f"FSLM machine {machine_path.name} imports a Python module binding."
                ),
            )


def _reference_path(reference: str) -> Path | None:
    path_text = reference.rsplit(":", 1)[0] if ":" in reference else reference
    path = Path(path_text).expanduser()
    return path if path.is_absolute() or path.exists() else None


def _required_machine_ref(engine_config: Mapping[str, Any]) -> str:
    machine = engine_config.get(_MACHINE_CONFIG_KEY)
    if not isinstance(machine, str) or not machine.strip():
        raise ValueError("FSLM execution requires `machine: <path-or-module>`.")
    return machine.strip()


def _runtime_bindings_or_none(api: _FSLMApi, value: Any) -> Any | None:
    if isinstance(value, api.RuntimeBindings):
        return value
    if value is None:
        return None
    raise TypeError("FSLM `bindings` must be an ellements.fslm.RuntimeBindings object.")


def _resolve_reference(reference: str, base_dir: Path | None) -> str:
    if base_dir is None:
        return reference
    path_part, separator, attr = reference.partition(":")
    path = Path(path_part).expanduser()
    if path.is_absolute() or path.exists():
        resolved = path
    elif path.suffix in {".yaml", ".yml", ".json", ".py"} or path_part.startswith("."):
        resolved = (base_dir / path).resolve()
    else:
        return reference
    return f"{resolved}{separator}{attr}" if separator else str(resolved)


def _resolve_binding_modules(
    value: Any, base_dir: Path | None
) -> list[str | Path] | None:
    if value is None:
        return None
    raw_items = value if isinstance(value, list) else [value]
    result: list[str | Path] = []
    for item in raw_items:
        text = str(item)
        path = Path(text).expanduser()
        if (
            base_dir is not None
            and not path.is_absolute()
            and (path.suffix == ".py" or text.startswith("."))
        ):
            result.append((base_dir / path).resolve())
        else:
            result.append(text)
    return result


def _collect_prompt_requirements(spec: Any) -> list[_PromptRequirement]:
    requirements: list[_PromptRequirement] = []
    seen: set[tuple[str, str]] = set()

    def add(key: str, kind: str, source: str) -> None:
        signature = (key, source)
        if signature in seen:
            return
        seen.add(signature)
        requirements.append(_PromptRequirement(key=key, kind=kind, source=source))

    for state in spec.states.values():
        if _metadata_prompt_key(state.metadata):
            add(
                _state_prompt_key(state),
                "state",
                f"state {state.name}",
            )
        for invariant in state.invariants:
            if invariant.kind == "nl":
                add(
                    _prompt_key("invariant", invariant, invariant.id),
                    "invariant",
                    f"state {state.name} invariant {invariant.id}",
                )

    for transition in spec.transitions.values():
        for guard in transition.guards:
            if guard.kind == "nl":
                add(
                    _prompt_key("guard", guard, guard.id),
                    "guard",
                    f"transition {transition.name} guard {guard.id}",
                )
        for action in transition.actions:
            if action.kind == "nl":
                action_name = _action_name(action)
                add(
                    _prompt_key("action", action, action_name),
                    "action",
                    f"transition {transition.name} action {action_name}",
                )
        for output in transition.emits:
            if output.kind == "nl":
                add(
                    _prompt_key("output", output, output.type),
                    "output",
                    f"transition {transition.name} output {output.type}",
                )
    return requirements


def _validate_prompt_contract(
    prompts: Mapping[str, str],
    requirements: list[_PromptRequirement],
) -> None:
    missing = [item for item in requirements if item.key not in prompts]
    if not missing:
        return
    details = "\n".join(
        f"- {item.key} ({item.kind}, {item.source})" for item in missing
    )
    raise PromptKeyMissingError(
        "FSLM prompt contract is incomplete. Missing required prompts:\n"
        f"{details}\nAvailable prompts: {sorted(prompts.keys())}."
    )


def _events_from_config(api: _FSLMApi, engine_config: Mapping[str, Any]) -> list[Any]:
    raw_events = engine_config.get("events")
    if raw_events is None:
        raw_event = engine_config.get("initial_event")
        if raw_event is None:
            return []
        raw_events = [raw_event]
    elif not isinstance(raw_events, list):
        raw_events = [raw_events]

    default_payload = engine_config.get("event_payload")
    events = []
    for raw in raw_events:
        events.append(_coerce_event(api, raw, default_payload))
    return events


def _coerce_event(api: _FSLMApi, raw: Any, default_payload: Any = None) -> Any:
    if isinstance(raw, api.FSLMEvent):
        return raw
    if isinstance(raw, str):
        payload = default_payload if isinstance(default_payload, dict) else {}
        return api.FSLMEvent(type=raw, payload=payload)
    if isinstance(raw, Mapping):
        data = dict(raw)
        if "type" not in data:
            raise ValueError(f"FSLM event is missing `type`: {raw!r}")
        return api.FSLMEvent.model_validate(data)
    raise TypeError(f"Unsupported FSLM event value: {raw!r}")


def _initial_variables(
    config: RuntimeConfig | None,
    engine_config: Mapping[str, Any],
) -> dict[str, Any]:
    variables = dict(config.execution_variables) if config is not None else {}
    for key in ("initial_variables", "snapshot_variables", "variables"):
        value = engine_config.get(key)
        if isinstance(value, Mapping):
            variables.update(dict(value))
    return variables


def _max_steps(engine_config: Mapping[str, Any], spec: Any, event_count: int) -> int:
    configured = _optional_int(engine_config.get("max_steps"))
    if configured is not None:
        return configured
    policy_limit = getattr(spec.policy.budgets, "max_steps", None)
    if isinstance(policy_limit, int) and policy_limit > 0:
        return policy_limit
    return max(event_count, _DEFAULT_MAX_STEPS if event_count == 0 else event_count)


def _status_after_step(
    spec: Any,
    step_result: Any,
    engine_config: Mapping[str, Any],
) -> str:
    if step_result.status == "blocked":
        return "blocked"
    if step_result.status == "no_transition" and _bool_config(
        engine_config,
        "stop_on_no_transition",
        True,
    ):
        return "no_transition"
    if _is_terminal(spec, step_result.new_snapshot.current_state):
        return "terminal"
    return "awaiting_event"


def _selected_transition(spec: Any, step_result: Any) -> Any | None:
    if step_result.selected_transition is None:
        return None
    return spec.transitions.get(step_result.selected_transition)


def _is_terminal(spec: Any, state_name: str) -> bool:
    return bool(spec.states[state_name].terminal)


def _primary_output(step_results: list[Any]) -> str:
    rendered: list[str] = []
    for step in step_results:
        for output in step.outputs:
            text = _payload_text(output.payload)
            if text:
                rendered.append(text)
        if not step.outputs:
            for action in step.actions:
                text = _payload_text(action.output)
                if text:
                    rendered.append(text)
    if rendered:
        return "\n\n".join(rendered)
    if step_results:
        final = step_results[-1]
        return json.dumps(
            {
                "status": final.status,
                "state": final.new_snapshot.current_state,
                "selected_transition": final.selected_transition,
            },
            indent=2,
            sort_keys=True,
        )
    return ""


def _payload_text(payload: Mapping[str, Any]) -> str:
    for key in ("text", "value", "instruction"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    if payload:
        return json.dumps(payload, indent=2, sort_keys=True)
    return ""


def _tool_schemas_by_name(tools: list[dict[str, Any]]) -> dict[str, set[str]]:
    schemas: dict[str, set[str]] = {}
    for tool in tools:
        function = tool.get("function") if isinstance(tool, Mapping) else None
        if not isinstance(function, Mapping):
            continue
        name = function.get("name")
        parameters = function.get("parameters")
        if not isinstance(name, str) or not isinstance(parameters, Mapping):
            continue
        properties = parameters.get("properties")
        if not isinstance(properties, Mapping):
            continue
        schemas[name] = {str(key) for key in properties}
    return schemas


def _event_input_value(
    event: Any,
    name: str,
    defaults: Mapping[str, Any],
) -> Any:
    payload = event.payload if isinstance(event.payload, Mapping) else {}
    if name in payload:
        return payload[name]
    for container_name in ("input", "inputs"):
        nested = payload.get(container_name)
        if isinstance(nested, Mapping) and name in nested:
            return nested[name]
    if name in defaults:
        return defaults[name]
    return _MISSING


def _candidate_transitions(
    spec: Any, snapshot: Any, event: Any
) -> list[dict[str, Any]]:
    state = spec.states[snapshot.current_state]
    result = []
    for name in [*state.transitions, *state.recovery_transitions]:
        transition = spec.transitions[name]
        if transition.trigger.type in (event.type, "*"):
            result.append(_model_dump(transition))
    return result


def _prompt_key(kind: str, item: Any, identifier: str) -> str:
    return _metadata_prompt_key(item.metadata) or f"{kind}.{identifier}"


def _state_prompt_key(state: Any) -> str:
    return _metadata_prompt_key(state.metadata) or f"state.{state.name}"


def _metadata_prompt_key(metadata: Mapping[str, Any]) -> str | None:
    value = metadata.get("prompt_key")
    return value.strip() if isinstance(value, str) and value.strip() else None


def _action_name(action: Any) -> str:
    return str(action.name or action.tool or action.ref or "action")


def _item_identity(kind: str, item: Any) -> str:
    if kind == "output":
        return str(getattr(item, "type", kind))
    return str(getattr(item, "id", None) or getattr(item, "name", None) or kind)


def _model_dump(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        dumped = value.model_dump(mode="json")
        if isinstance(dumped, Mapping):
            return {str(key): item for key, item in dumped.items()}
        return {"value": dumped}
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": str(value)}


def _messages(
    prompt: str,
    context: Mapping[str, Any],
    *,
    system: str,
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": "\n\n".join(
                [
                    prompt.strip(),
                    "FSLM runtime context:",
                    "```json\n"
                    + json.dumps(context, indent=2, sort_keys=True, default=str)
                    + "\n```",
                ]
            ),
        },
    ]


def _compact_step(step_result: Any, event: Any) -> dict[str, Any]:
    return {
        "event": {"id": event.id, "type": event.type, "payload": event.payload},
        "source_state": step_result.source_state,
        "target_state": step_result.target_state,
        "status": step_result.status,
        "selected_transition": step_result.selected_transition,
        "guards": [item.model_dump(mode="json") for item in step_result.guard_results],
        "invariants": [
            item.model_dump(mode="json") for item in step_result.invariant_results
        ],
        "actions": [item.model_dump(mode="json") for item in step_result.actions],
        "outputs": [item.model_dump(mode="json") for item in step_result.outputs],
        "violations": list(step_result.violations),
    }


def _invoke_callable(fn: Any, ctx: Any, args: dict[str, Any]) -> Any:
    signature = inspect.signature(fn)
    return fn(ctx, args) if len(signature.parameters) >= 2 else fn(ctx)


def _action_from_payload(api: _FSLMApi, action: Any, value: Any) -> Any:
    if isinstance(value, api.ActionResult):
        return value
    return api.ActionResult(
        action_name=_action_name(action),
        tool=action.tool or action.ref or "python",
        status="executed",
        output=value if isinstance(value, dict) else {"value": value},
    )


def _path_or_none(value: Any) -> Path | None:
    if isinstance(value, str) and value:
        return Path(value).expanduser().resolve()
    if isinstance(value, Path):
        return value.expanduser().resolve()
    return None


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _bool_config(
    config: Mapping[str, Any],
    key: str,
    default: bool,
) -> bool:
    value = config.get(key, default)
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() not in {"", "0", "false", "no", "off"}


__all__ = ["FSLMEngine"]
