"""Lower sugared FSLM WeaveMark blocks into executable machine specs."""

from __future__ import annotations

import re
import shlex
import textwrap
from dataclasses import dataclass, field
from typing import Any

_DIRECTIVE_RE = re.compile(
    r"^(?P<indent>[ \t]*)@(?P<name>[A-Za-z_][\w.-]*)(?P<rest>(?:\s+.*)?)$"
)
_IDENT_RE = re.compile(r"^[A-Za-z_][\w.-]*$")


@dataclass(frozen=True)
class FSLMLoweringResult:
    """Result of lowering one inline FSLM machine."""

    machine_name: str
    machine_spec: dict[str, Any]
    prompts: dict[str, str]
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class _InputSpec:
    name: str
    description: str
    default: str | None
    required: bool

    def to_metadata(self) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            metadata["default"] = self.default
        return metadata


@dataclass(frozen=True)
class _ChildBlock:
    name: str
    rest: str
    body: str


def is_fslm_machine_directive(
    directive: str,
    semantic_names: set[str],
) -> bool:
    """Return True when *directive* is the imported FSLM machine marker."""

    return directive in semantic_names and directive.endswith("machine")


def lower_machine_block(rest: str, block: str) -> FSLMLoweringResult:
    """Lower an ``@machine`` block into a serializable FSLM machine spec."""

    positional, options = _parse_options(rest)
    errors: list[str] = []
    warnings: list[str] = []
    prompts: dict[str, str] = {}
    if len(positional) != 1:
        return FSLMLoweringResult(
            machine_name="",
            machine_spec={},
            prompts={},
            errors=["@machine requires exactly one machine name."],
        )
    machine_name = positional[0]
    if not _IDENT_RE.fullmatch(machine_name):
        errors.append(f"@machine name is invalid: {machine_name}")

    unsupported = sorted(set(options) - {"initial", "version"})
    if unsupported:
        errors.append(
            "@machine has unsupported option(s): " + ", ".join(unsupported) + "."
        )

    children = _split_children(block)
    description = children.prose.strip()
    states: dict[str, Any] = {}

    for child in children.blocks:
        if not child.name.endswith("state"):
            errors.append(
                f"@machine may contain only @state blocks; got @{child.name}."
            )
            continue
        state_spec, state_prompts, state_warnings, state_errors = _lower_state(child)
        warnings.extend(state_warnings)
        errors.extend(state_errors)
        if not state_spec:
            continue
        state_name = str(state_spec["name"])
        if state_name in states:
            errors.append(f"Duplicate @state in @machine {machine_name}: {state_name}")
            continue
        states[state_name] = state_spec
        _merge_generated_prompts(
            prompts,
            state_prompts,
            errors,
            context=f"@machine {machine_name}",
        )

    initial = options.get("initial")
    if initial is None and states:
        initial = next(iter(states))
        warnings.append(
            f"@machine {machine_name} did not declare initial:; using {initial}."
        )
    if initial is None:
        errors.append(f"@machine {machine_name} requires at least one @state.")
        initial = ""
    elif initial not in states:
        errors.append(
            f"@machine {machine_name} initial state {initial!r} is not declared."
        )

    return FSLMLoweringResult(
        machine_name=machine_name,
        machine_spec={
            "name": machine_name,
            "description": description,
            "version": options.get("version", "0.1"),
            "initial": initial,
            "states": states,
            "metadata": {"source": "weavemark.fslm_sugar"},
        },
        prompts=prompts,
        warnings=warnings,
        errors=errors,
    )


def _lower_state(
    block: _ChildBlock,
) -> tuple[dict[str, Any], dict[str, str], list[str], list[str]]:
    positional, options = _parse_options(block.rest)
    errors: list[str] = []
    warnings: list[str] = []
    prompts: dict[str, str] = {}
    if len(positional) != 1:
        return {}, {}, [], ["@state requires exactly one state name."]
    state_name = positional[0]
    unsupported = sorted(set(options) - {"terminal"})
    if unsupported:
        errors.append(
            f"@state {state_name} has unsupported option(s): "
            + ", ".join(unsupported)
            + "."
        )

    children = _split_children(block.body)
    transitions: list[dict[str, Any]] = []
    transition_names: set[str] = set()
    for child in children.blocks:
        if not child.name.endswith("transition"):
            errors.append(
                f"@state may contain only @transition blocks; got @{child.name}."
            )
            continue
        transition, transition_prompts, transition_warnings, transition_errors = (
            _lower_transition(state_name, child)
        )
        warnings.extend(transition_warnings)
        errors.extend(transition_errors)
        if transition:
            transition_name = str(transition["name"])
            if transition_name in transition_names:
                errors.append(
                    f"Duplicate @transition in @state {state_name}: "
                    f"{transition_name}"
                )
                continue
            transition_names.add(transition_name)
            transitions.append(transition)
            _merge_generated_prompts(
                prompts,
                transition_prompts,
                errors,
                context=f"@state {state_name}",
            )

    return (
        {
            "name": state_name,
            "objective": children.prose.strip(),
            "description": children.prose.strip(),
            "terminal": _parse_bool(options.get("terminal"), default=False),
            "transitions": transitions,
            "metadata": {"source": "weavemark.fslm_sugar"},
        },
        prompts,
        warnings,
        errors,
    )


def _lower_transition(
    state_name: str,
    block: _ChildBlock,
) -> tuple[dict[str, Any], dict[str, str], list[str], list[str]]:
    positional, options = _parse_options(block.rest)
    errors: list[str] = []
    warnings: list[str] = []
    prompts: dict[str, str] = {}
    if len(positional) != 1:
        return {}, {}, [], ["@transition requires exactly one transition name."]
    transition_name = positional[0]
    unsupported = sorted(
        set(options) - {"event", "target", "to", "internal", "external", "weight"}
    )
    if unsupported:
        errors.append(
            f"@transition {transition_name} has unsupported option(s): "
            + ", ".join(unsupported)
            + "."
        )
    target = options.get("target", options.get("to"))
    if not target:
        errors.append(f"@transition {transition_name} requires target: <state>.")
        target = state_name
    event = options.get("event", transition_name)
    internal = _parse_bool(options.get("internal"), default=True)
    external = _parse_bool(options.get("external"), default=False)
    if not internal and not external:
        warnings.append(
            f"@transition {transition_name} is neither internal nor external; "
            "it will not be offered to the autonomous runner or external hosts."
        )

    children = _split_children(block.body)
    inputs: list[_InputSpec] = []
    guards: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    input_names: set[str] = set()
    guard_ids: set[str] = set()
    action_names: set[str] = set()

    for child in children.blocks:
        if child.name.endswith("input"):
            input_spec, input_errors = _lower_input(child)
            errors.extend(input_errors)
            if input_spec is not None:
                if input_spec.name in input_names:
                    errors.append(
                        f"Duplicate @input in @transition {transition_name}: "
                        f"{input_spec.name}"
                    )
                    continue
                input_names.add(input_spec.name)
                inputs.append(input_spec)
            continue
        if child.name.endswith("guard"):
            guard, prompt_key, guard_errors = _lower_guard(
                child,
                state_name=state_name,
                transition_name=transition_name,
            )
            errors.extend(guard_errors)
            if guard:
                guard_id = str(guard["id"])
                if guard_id in guard_ids:
                    errors.append(
                        f"Duplicate @guard in @transition {transition_name}: "
                        f"{guard_id}"
                    )
                    continue
                guard_ids.add(guard_id)
                guards.append(guard)
                if prompt_key:
                    _add_generated_prompt(
                        prompts,
                        prompt_key,
                        child.body.strip(),
                        errors,
                        context=f"@transition {transition_name}",
                    )
            continue
        if child.name.endswith("action"):
            action, prompt_key, action_errors = _lower_action(
                child,
                inputs,
                state_name=state_name,
                transition_name=transition_name,
            )
            errors.extend(action_errors)
            if action:
                action_name = str(action["name"])
                if action_name in action_names:
                    errors.append(
                        f"Duplicate @action in @transition {transition_name}: "
                        f"{action_name}"
                    )
                    continue
                action_names.add(action_name)
                actions.append(action)
                if prompt_key:
                    _add_generated_prompt(
                        prompts,
                        prompt_key,
                        child.body.strip(),
                        errors,
                        context=f"@transition {transition_name}",
                    )
            continue
        errors.append(
            f"@transition may contain only @input, @guard, or @action blocks; "
            f"got @{child.name}."
        )

    metadata: dict[str, Any] = {
        "internal": internal,
        "external": external,
        "inputs": [item.to_metadata() for item in inputs],
        "source": "weavemark.fslm_sugar",
    }
    transition: dict[str, Any] = {
        "name": transition_name,
        "source": state_name,
        "target": target,
        "event": event,
        "description": children.prose.strip(),
        "guards": guards,
        "actions": actions,
        "metadata": metadata,
    }
    if "weight" in options:
        weight = _parse_number_option(
            options["weight"],
            directive="@transition",
            parameter="weight",
            errors=errors,
        )
        if weight is not None:
            transition["weight"] = weight
    return transition, prompts, warnings, errors


def _lower_input(block: _ChildBlock) -> tuple[_InputSpec | None, list[str]]:
    positional, options = _parse_options(block.rest)
    errors: list[str] = []
    if len(positional) != 1:
        return None, ["@input requires exactly one input name."]
    unsupported = sorted(set(options) - {"default", "required"})
    if unsupported:
        errors.append(
            f"@input {positional[0]} has unsupported option(s): "
            + ", ".join(unsupported)
            + "."
        )
    return (
        _InputSpec(
            name=positional[0],
            description=block.body.strip(),
            default=options.get("default"),
            required=_parse_bool(options.get("required"), default=True),
        ),
        errors,
    )


def _lower_guard(
    block: _ChildBlock,
    *,
    state_name: str,
    transition_name: str,
) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    positional, options = _parse_options(block.rest)
    errors: list[str] = []
    if len(positional) != 1:
        return None, None, ["@guard requires exactly one guard id."]
    guard_id = positional[0]
    unsupported = sorted(set(options) - {"kind", "ref", "prompt_key", "min_confidence"})
    if unsupported:
        errors.append(
            f"@guard {guard_id} has unsupported option(s): "
            + ", ".join(unsupported)
            + "."
        )
    kind = options.get("kind", "deterministic" if "ref" in options else "nl")
    guard: dict[str, Any] = {
        "id": guard_id,
        "kind": kind,
        "text": block.body.strip(),
        "metadata": {"source": "weavemark.fslm_sugar"},
    }
    prompt_key: str | None = None
    if "ref" in options:
        guard["ref"] = options["ref"]
    if "min_confidence" in options:
        min_confidence = _parse_number_option(
            options["min_confidence"],
            directive="@guard",
            parameter="min_confidence",
            errors=errors,
        )
        if min_confidence is not None:
            guard["min_confidence"] = min_confidence
    if "prompt_key" in options:
        guard["metadata"]["prompt_key"] = options["prompt_key"]
    if kind == "nl":
        prompt_key = guard["metadata"].get("prompt_key") or (
            f"guard.{state_name}.{transition_name}.{guard_id}"
        )
        guard["metadata"]["prompt_key"] = prompt_key
    return guard, prompt_key, errors


def _lower_action(
    block: _ChildBlock,
    inputs: list[_InputSpec],
    *,
    state_name: str,
    transition_name: str,
) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    positional, options = _parse_options(block.rest)
    errors: list[str] = []
    if len(positional) != 1:
        return None, None, ["@action requires exactly one action name."]
    action_name = positional[0]
    unsupported = sorted(
        set(options) - {"kind", "tool", "ref", "prompt_key", "optional"}
    )
    if unsupported:
        errors.append(
            f"@action {action_name} has unsupported option(s): "
            + ", ".join(unsupported)
            + "."
        )
    kind = options.get("kind")
    if kind is None:
        if "ref" in options:
            kind = "deterministic"
        elif "tool" in options:
            kind = "tool"
        else:
            kind = "nl"
    action: dict[str, Any] = {
        "name": action_name,
        "kind": kind,
        "instruction": block.body.strip(),
        "text": block.body.strip(),
        "metadata": {
            "source": "weavemark.fslm_sugar",
            "optional": _parse_bool(options.get("optional"), default=False),
        },
    }
    if "tool" in options:
        action["tool"] = options["tool"]
    if "ref" in options:
        action["ref"] = options["ref"]
    if "prompt_key" in options:
        action["metadata"]["prompt_key"] = options["prompt_key"]

    prompt_key: str | None = None
    if kind == "nl":
        prompt_key = action["metadata"].get("prompt_key") or (
            f"action.{state_name}.{transition_name}.{action_name}"
        )
        action["metadata"]["prompt_key"] = prompt_key
    if kind == "tool":
        action["args"] = {
            "auto_map_inputs": True,
            "input_names": [item.name for item in inputs],
            "input_defaults": {
                item.name: item.default for item in inputs if item.default is not None
            },
        }
    return action, prompt_key, errors


def _add_generated_prompt(
    prompts: dict[str, str],
    key: str,
    text: str,
    errors: list[str],
    *,
    context: str,
) -> None:
    if key in prompts:
        errors.append(f"Duplicate generated FSLM prompt key {key!r} in {context}.")
        return
    prompts[key] = text


def _merge_generated_prompts(
    prompts: dict[str, str],
    incoming: dict[str, str],
    errors: list[str],
    *,
    context: str,
) -> None:
    for key, text in incoming.items():
        _add_generated_prompt(prompts, key, text, errors, context=context)


@dataclass(frozen=True)
class _SplitBlock:
    prose: str
    blocks: list[_ChildBlock]


def _split_children(block: str) -> _SplitBlock:
    lines = block.splitlines()
    prose_lines: list[str] = []
    children: list[_ChildBlock] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = _DIRECTIVE_RE.match(line)
        if match is None or match.group("indent"):
            prose_lines.append(line)
            index += 1
            continue

        child_body, next_index = _collect_indented_block(lines, index + 1, 0)
        children.append(
            _ChildBlock(
                name=match.group("name"),
                rest=match.group("rest").strip(),
                body=child_body,
            )
        )
        index = next_index

    return _SplitBlock(
        prose=textwrap.dedent("\n".join(prose_lines)).strip(),
        blocks=children,
    )


def _collect_indented_block(
    lines: list[str],
    start: int,
    parent_indent: int,
) -> tuple[str, int]:
    block: list[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            next_nonblank = next(
                (
                    future
                    for future in range(index + 1, len(lines))
                    if lines[future].strip()
                ),
                None,
            )
            if (
                next_nonblank is None
                or _indent_width(lines[next_nonblank]) <= parent_indent
            ):
                break
            block.append(line)
            index += 1
            continue
        if _indent_width(line) <= parent_indent:
            break
        block.append(line)
        index += 1
    return textwrap.dedent("\n".join(block)).strip("\n"), index


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _parse_options(rest: str) -> tuple[list[str], dict[str, str]]:
    tokens = _split_tokens(rest)
    positional: list[str] = []
    options: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.endswith(":") and index + 1 < len(tokens):
            options[token[:-1]] = tokens[index + 1]
            index += 2
        elif ":" in token:
            key, value = token.split(":", 1)
            if value:
                options[key] = value
                index += 1
            elif index + 1 < len(tokens):
                options[key] = tokens[index + 1]
                index += 2
            else:
                positional.append(token)
                index += 1
        else:
            positional.append(token)
            index += 1
    return positional, options


def _split_tokens(text: str) -> list[str]:
    try:
        return shlex.split(text.strip())
    except ValueError:
        return text.strip().split()


def _parse_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"", "0", "false", "no", "off", "none"}


def _parse_number(value: str) -> int | float:
    try:
        return int(value)
    except ValueError:
        return float(value)


def _parse_number_option(
    value: str,
    *,
    directive: str,
    parameter: str,
    errors: list[str],
) -> int | float | None:
    try:
        return _parse_number(value)
    except ValueError:
        errors.append(
            f"{directive} parameter {parameter!r} must be numeric; got {value!r}."
        )
        return None


__all__ = [
    "FSLMLoweringResult",
    "is_fslm_machine_directive",
    "lower_machine_block",
]
