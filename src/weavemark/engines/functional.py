"""Functional semantic-node execution engine."""

from __future__ import annotations

import inspect
import json
import math
import re
from collections.abc import Mapping
from typing import Any

from ellements.execution import OnStepCallback, StepRecord

from ..compilation.result import CompositionResult
from ..variable_paths import MISSING, resolve_variable_path
from .base import (
    ArtifactCallback,
    BaseEngine,
    ExecutionResult,
    RuntimeConfig,
    resolve_call_settings,
)
from .bindings import load_binding_callables

_VARIABLE_RE = re.compile(r"@\{\s*([A-Za-z_][\w.-]*)\s*\}")
_RESULT_NAME_RE = re.compile(r"^[A-Za-z_]\w*$")


class FunctionalEngine(BaseEngine):
    """Execute a validated semantic-function graph and render its document."""

    async def execute(
        self,
        result: CompositionResult,
        config: RuntimeConfig | None = None,
        on_step: OnStepCallback | None = None,
        on_artifact: ArtifactCallback | None = None,
    ) -> ExecutionResult:
        """Run bound semantic nodes, then complete the rendered document."""

        del on_artifact
        execution = result.execution
        nodes, levels, order = _validated_plan(execution)
        node_by_id = {_node_id(node): node for node in nodes}
        effect_names = [_node_effect_name(node, execution) for node in nodes]
        callables = load_binding_callables(result, effect_names)
        values = dict(config.execution_variables) if config is not None else {}
        results: dict[str, Any] = {}
        steps: list[StepRecord] = []
        evidence: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []

        for level_index, level in enumerate(levels):
            for node_id in level:
                node = node_by_id[node_id]
                effect_name = _node_effect_name(node, execution)
                arguments: dict[str, Any] = {}
                argument_evidence: Any = {}
                try:
                    arguments = _snapshot_value(
                        _resolve_node_arguments(node, values, results),
                        purpose=f"arguments for functional node {node_id!r}",
                    )
                    argument_evidence = _evidence_value(
                        _snapshot_value(
                            arguments,
                            purpose=f"arguments for functional node {node_id!r}",
                        )
                    )
                    returned_value = callables[effect_name](**arguments)
                    if inspect.isawaitable(returned_value):
                        returned_value = await returned_value
                    value = _snapshot_value(
                        returned_value,
                        purpose=f"result from functional node {node_id!r}",
                    )
                except Exception as exc:
                    error = {
                        "node": node_id,
                        "effect": effect_name,
                        "type": type(exc).__name__,
                        "message": str(exc),
                    }
                    errors.append(error)
                    step = StepRecord(
                        name=node_id,
                        prompt_key=str(node.get("definition") or node.get("directive")),
                        response="",
                        metadata={
                            "status": "error",
                            "level": level_index,
                            "effect": effect_name,
                            "arguments": argument_evidence,
                            "error": error,
                        },
                    )
                    steps.append(step)
                    if on_step is not None:
                        on_step(step)
                    raise RuntimeError(
                        f"@execute functional node {node_id!r} failed via "
                        f"@bind {effect_name!r}: {exc}"
                    ) from exc

                result_name = node.get("as")
                if result_name:
                    results[str(result_name)] = value
                node_evidence = {
                    "node": node_id,
                    "effect": effect_name,
                    "level": level_index,
                    "arguments": argument_evidence,
                    "result": _evidence_value(
                        _snapshot_value(
                            value,
                            purpose=f"evidence for functional node {node_id!r}",
                        )
                    ),
                }
                evidence.append(
                    _snapshot_value(
                        node_evidence,
                        purpose=f"aggregate evidence for functional node {node_id!r}",
                    )
                )
                step = StepRecord(
                    name=node_id,
                    prompt_key=str(node.get("definition") or node.get("directive")),
                    response=_display_value(value),
                    metadata={
                        "status": "executed",
                        **_snapshot_value(
                            node_evidence,
                            purpose=f"step evidence for functional node {node_id!r}",
                        ),
                    },
                )
                steps.append(step)
                if on_step is not None:
                    on_step(step)

        rendered_document = _render_document(result.composed_prompt, values, results)
        used_llm = _document_contains_instructions(result.composed_prompt)
        call_settings: dict[str, Any] | None = None
        if used_llm:
            settings = resolve_call_settings(
                result,
                config,
                prompt_key="default",
                stage="final-document",
            )
            kwargs: dict[str, Any] = {"model": settings.model}
            if settings.temperature is not None:
                kwargs["temperature"] = settings.temperature
            output = await self.client.complete(rendered_document, **kwargs)
            call_settings = settings.metadata()
        else:
            output = rendered_document

        document_step = StepRecord(
            name="document",
            prompt_key="default",
            response=output,
            metadata={
                "status": "executed",
                "mode": "llm" if used_llm else "rendered",
                **({"call_settings": call_settings} if call_settings else {}),
            },
        )
        steps.append(document_step)
        if on_step is not None:
            on_step(document_step)

        execution_evidence = {
            "plan_order": order,
            "plan_levels": levels,
            "nodes": evidence,
            "errors": errors,
            "rendered_document": rendered_document,
            "final_document_mode": "llm" if used_llm else "rendered",
        }
        executed_execution = {
            **_snapshot_value(
                execution,
                purpose="compiled functional execution metadata",
            ),
            "status": "executed",
            "evidence": _snapshot_value(
                execution_evidence,
                purpose="functional execution evidence metadata",
            ),
        }
        return ExecutionResult(
            output=output,
            steps=steps,
            metadata={
                "status": "executed",
                "execution": executed_execution,
                "bindings": _snapshot_value(
                    result.bindings,
                    purpose="functional binding metadata",
                ),
                "results": {
                    name: _evidence_value(
                        _snapshot_value(
                            value,
                            purpose=f"execution metadata result {name!r}",
                        )
                    )
                    for name, value in results.items()
                },
                "evidence": _snapshot_value(
                    execution_evidence,
                    purpose="functional result evidence metadata",
                ),
                **({"call_settings": call_settings} if call_settings else {}),
            },
        )


def _validated_plan(
    execution: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[list[str]], list[str]]:
    if execution.get("type") != "functional":
        raise ValueError("FunctionalEngine requires @execute functional metadata.")
    raw_nodes = execution.get("nodes")
    plan = execution.get("plan")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ValueError("@execute functional requires at least one compiled node.")
    if not isinstance(plan, Mapping):
        raise ValueError("@execute functional is missing its validated plan.")
    if not all(isinstance(node, dict) for node in raw_nodes):
        raise ValueError("@execute functional contains malformed node metadata.")
    nodes = raw_nodes
    node_ids = [_node_id(node) for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("@execute functional plan contains duplicate node IDs.")

    raw_order = plan.get("order")
    raw_levels = plan.get("levels")
    if not isinstance(raw_order, list) or not all(
        isinstance(item, str) for item in raw_order
    ):
        raise ValueError("@execute functional plan order must be a list of node IDs.")
    if not isinstance(raw_levels, list) or not all(
        isinstance(level, list)
        and level
        and all(isinstance(item, str) for item in level)
        for level in raw_levels
    ):
        raise ValueError("@execute functional plan levels must contain node ID lists.")
    order = list(raw_order)
    levels = [list(level) for level in raw_levels]
    flattened = [node_id for level in levels for node_id in level]
    if order != flattened or set(order) != set(node_ids) or len(order) != len(node_ids):
        raise ValueError(
            "@execute functional plan order/levels do not exactly match compiled nodes."
        )
    position = {node_id: index for index, node_id in enumerate(order)}
    producers = {
        str(node["as"]): _node_id(node) for node in nodes if node.get("as")
    }
    invalid_results = sorted(name for name in producers if not _RESULT_NAME_RE.fullmatch(name))
    if invalid_results:
        raise ValueError(
            "@execute functional result names must be simple identifiers: "
            + ", ".join(invalid_results)
            + "."
        )
    for node in nodes:
        uses = node.get("uses", [])
        if not isinstance(uses, list) or not all(
            isinstance(dependency, str) for dependency in uses
        ):
            raise ValueError(
                f"@execute functional node {_node_id(node)!r} has malformed uses metadata."
            )
        invalid_uses = sorted(
            dependency for dependency in uses if not _RESULT_NAME_RE.fullmatch(dependency)
        )
        if invalid_uses:
            raise ValueError(
                f"@execute functional node {_node_id(node)!r} uses invalid result "
                "name(s): "
                + ", ".join(invalid_uses)
                + "."
            )
        if (
            execution.get("scheduler") == "graph-strict"
            or plan.get("scheduler") == "graph-strict"
        ):
            referenced_results = _node_result_references(node, set(producers))
            missing_uses = sorted(referenced_results - set(uses))
            if missing_uses:
                raise ValueError(
                    f"@execute functional graph-strict node {_node_id(node)!r} "
                    "references result(s) without explicit uses: "
                    + ", ".join(missing_uses)
                    + "."
                )
        for dependency in uses:
            producer = producers.get(str(dependency))
            if producer is None or position[producer] >= position[_node_id(node)]:
                raise ValueError(
                    f"@execute functional node {_node_id(node)!r} has an invalid "
                    f"planned dependency {dependency!r}."
                )
    return nodes, levels, order


def _node_result_references(
    node: Mapping[str, Any],
    produced_results: set[str],
) -> set[str]:
    references: set[str] = set()
    args = node.get("args", {})
    values = [
        args.get("positional", []) if isinstance(args, Mapping) else [],
        args.get("options", {}) if isinstance(args, Mapping) else {},
        node.get("body", ""),
    ]

    def collect(value: Any) -> None:
        if isinstance(value, str):
            references.update(
                match.group(1).split(".", 1)[0]
                for match in _VARIABLE_RE.finditer(value)
                if match.group(1).split(".", 1)[0] in produced_results
            )
        elif isinstance(value, Mapping):
            for nested in value.values():
                collect(nested)
        elif isinstance(value, (list, tuple)):
            for nested in value:
                collect(nested)

    for value in values:
        collect(value)
    return references


def _node_id(node: Mapping[str, Any]) -> str:
    node_id = node.get("id") or node.get("as") or node.get("directive")
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("@execute functional node is missing its ID.")
    return node_id


def _node_effect_name(
    node: Mapping[str, Any],
    execution: Mapping[str, Any],
) -> str:
    effects = node.get("effects")
    if not isinstance(effects, list) or len(effects) != 1:
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} must declare exactly "
            "one bound effect."
        )
    effect = effects[0]
    if not isinstance(effect, Mapping) or not isinstance(effect.get("name"), str):
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} has malformed effect metadata."
        )
    name = str(effect["name"])
    allowed_effects = execution.get("allow_effects")
    if allowed_effects is not None and (
        not isinstance(allowed_effects, list)
        or name not in {
            str(item) for item in allowed_effects
        }
    ):
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} is not authorized "
            f"to execute effect {name!r}."
        )
    return name


def _resolve_node_arguments(
    node: Mapping[str, Any],
    variables: Mapping[str, Any],
    results: Mapping[str, Any],
) -> dict[str, Any]:
    params = node.get("params")
    args = node.get("args")
    if not isinstance(params, list) or not all(
        isinstance(param, Mapping) and isinstance(param.get("name"), str)
        for param in params
    ):
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} is missing parameter metadata."
        )
    if not isinstance(args, Mapping):
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} has malformed arguments."
        )
    positional = args.get("positional", [])
    options = args.get("options", {})
    if not isinstance(positional, list) or not isinstance(options, Mapping):
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} has malformed arguments."
        )

    implicit = [param for param in params if param.get("implicit")]
    if len(implicit) > 1:
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} has multiple implicit parameters."
        )
    inline = [param for param in params if not param.get("implicit")]
    names = {str(param["name"]) for param in inline}
    unknown = sorted(str(name) for name in options if str(name) not in names)
    if unknown:
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} has unknown argument(s): "
            + ", ".join(unknown)
            + "."
        )
    available = [param for param in inline if param["name"] not in options]
    if len(positional) > len(available):
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} has too many positional arguments."
        )

    context = {**variables, **results}
    resolved = {
        str(name): _resolve_runtime_value(value, context)
        for name, value in options.items()
    }
    for param, value in zip(available, positional, strict=False):
        resolved[str(param["name"])] = _resolve_runtime_value(value, context)
    if implicit:
        resolved[str(implicit[0]["name"])] = _resolve_runtime_value(
            node.get("body", ""), context
        )
    for param in params:
        name = str(param["name"])
        if name in resolved:
            continue
        if "default" in param:
            resolved[name] = _resolve_runtime_value(param["default"], context)
            continue
        raise ValueError(
            f"@execute functional node {_node_id(node)!r} is missing argument {name!r}."
        )
    return resolved


def _resolve_runtime_value(value: Any, context: Mapping[str, Any]) -> Any:
    if not isinstance(value, str):
        return value
    exact = _VARIABLE_RE.fullmatch(value.strip())
    if exact:
        resolved = resolve_variable_path(context, exact.group(1))
        if resolved is MISSING:
            raise ValueError(
                f"Unresolved functional value placeholder: @{{{exact.group(1)}}}"
            )
        return _snapshot_value(
            resolved,
            purpose=f"functional placeholder @{{{exact.group(1)}}}",
        )

    def replace(match: re.Match[str]) -> str:
        resolved = resolve_variable_path(context, match.group(1))
        if resolved is MISSING:
            raise ValueError(
                f"Unresolved functional value placeholder: @{{{match.group(1)}}}"
            )
        return _display_value(resolved)

    return _VARIABLE_RE.sub(replace, value)


def _render_document(
    document: str,
    variables: Mapping[str, Any],
    results: Mapping[str, Any],
) -> str:
    return str(_resolve_runtime_value(document, {**variables, **results}))


def _document_contains_instructions(document: str) -> bool:
    return bool(_VARIABLE_RE.sub("", document).strip())


def _display_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def _evidence_value(value: Any) -> Any:
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return _display_value(value)
    return value


def _snapshot_value(value: Any, *, purpose: str) -> Any:
    """Return an alias-free JSON-safe snapshot or reject the value explicitly."""

    seen_containers: set[int] = set()

    def snapshot(item: Any, path: str) -> Any:
        if item is None or type(item) in {bool, int, str}:
            return item
        if type(item) is float:
            if not math.isfinite(item):
                raise TypeError(
                    f"Cannot safely snapshot {purpose}: non-finite float at {path}."
                )
            return item
        if type(item) in {list, tuple}:
            container_id = id(item)
            if container_id in seen_containers:
                raise TypeError(
                    f"Cannot safely snapshot {purpose}: shared or cyclic container "
                    f"at {path}."
                )
            seen_containers.add(container_id)
            return [
                snapshot(nested, f"{path}[{index}]")
                for index, nested in enumerate(item)
            ]
        if isinstance(item, Mapping):
            container_id = id(item)
            if container_id in seen_containers:
                raise TypeError(
                    f"Cannot safely snapshot {purpose}: shared or cyclic container "
                    f"at {path}."
                )
            seen_containers.add(container_id)
            copied: dict[str, Any] = {}
            for key, nested in item.items():
                if type(key) is not str:
                    raise TypeError(
                        f"Cannot safely snapshot {purpose}: mapping key at {path} "
                        f"must be a string, got {type(key).__name__}."
                    )
                copied[key] = snapshot(nested, f"{path}.{key}")
            return copied
        raise TypeError(
            f"Cannot safely snapshot {purpose}: unsupported value type "
            f"{type(item).__name__} at {path}."
        )

    return snapshot(value, "$")


__all__ = ["FunctionalEngine"]
