"""Typed accumulation of composition metadata across semantic compiler rounds."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from weavemark.compilation.multimodal import ImageRef, OutputContract
from weavemark.compilation.trace import DirectiveApplication


class CompositionEnvelope(Protocol):
    """Mutable composition-result surface consumed by the accumulator."""

    prompts: dict[str, str]
    prompt_roles: dict[str, str]
    prompt_images: dict[str, list[ImageRef]]
    prompt_outputs: dict[str, OutputContract]
    raw_response: str
    analysis: str
    compile: dict[str, Any]
    tools: list[dict[str, Any]]
    bindings: list[dict[str, str]]
    execution: dict[str, Any]
    emits: dict[str, str]
    packages: list[dict[str, str]]
    warnings: list[str]
    errors: list[str]
    suggestions: list[str]
    transitions: list[str]
    ask_history: list[dict[str, str]]
    iteration_history: list[dict[str, Any]]
    directives: list[DirectiveApplication]
    tool_calls_made: int


@dataclass
class CompositionAccumulator:
    """Preserve deterministic result state while prompt text is recompiled.

    Later rounds replace keyed values from earlier rounds. Sequence records use
    stable semantic identities, so rerunning a round updates its prior
    contribution rather than duplicating it.
    """

    prompts: dict[str, str] = field(default_factory=dict)
    prompt_roles: dict[str, str] = field(default_factory=dict)
    prompt_images: dict[str, list[ImageRef]] = field(default_factory=dict)
    prompt_outputs: dict[str, OutputContract] = field(default_factory=dict)
    raw_response: str = ""
    analysis: str = ""
    compile: dict[str, Any] = field(default_factory=dict)
    tools: dict[str, dict[str, Any]] = field(default_factory=dict)
    bindings: dict[str, dict[str, str]] = field(default_factory=dict)
    execution: dict[str, Any] = field(default_factory=dict)
    emits: dict[str, str] = field(default_factory=dict)
    packages: dict[str, dict[str, str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    transitions: list[str] = field(default_factory=list)
    ask_history: list[dict[str, str]] = field(default_factory=list)
    iteration_history: list[dict[str, Any]] = field(default_factory=list)
    directives: dict[str, DirectiveApplication] = field(default_factory=dict)
    tool_calls_made: int = 0

    def absorb(self, result: CompositionEnvelope) -> None:
        """Merge one newer round into accumulated state."""
        self.prompts.update(result.prompts)
        self.prompt_roles.update(result.prompt_roles)
        self.prompt_images.update(result.prompt_images)
        self.prompt_outputs.update(result.prompt_outputs)
        if result.raw_response:
            self.raw_response = result.raw_response
        if result.analysis:
            self.analysis = result.analysis
        self.compile.update(result.compile)
        self.execution.update(result.execution)
        self.emits.update(result.emits)

        for tool in result.tools:
            self.tools[_tool_identity(tool)] = tool
        for binding in result.bindings:
            self.bindings[_binding_identity(binding)] = binding
        for package in result.packages:
            self.packages[_package_identity(package)] = package
        for directive in result.directives:
            self.directives[directive.id] = directive

        _extend_unique(self.warnings, result.warnings)
        _extend_unique(self.suggestions, result.suggestions)
        _extend_unique(self.transitions, result.transitions)
        _extend_unique_records(self.ask_history, result.ask_history)
        _extend_unique_records(self.iteration_history, result.iteration_history)
        self.tool_calls_made += result.tool_calls_made

    def apply_to(self, result: CompositionEnvelope) -> None:
        """Apply accumulated state to the final result, preferring final values."""
        result.prompts = {**self.prompts, **result.prompts}
        result.prompt_roles = {**self.prompt_roles, **result.prompt_roles}
        result.prompt_images = {**self.prompt_images, **result.prompt_images}
        result.prompt_outputs = {**self.prompt_outputs, **result.prompt_outputs}
        result.raw_response = result.raw_response or self.raw_response
        result.analysis = result.analysis or self.analysis
        result.compile = {**self.compile, **result.compile}
        result.execution = {**self.execution, **result.execution}
        result.emits = {**self.emits, **result.emits}

        tools = dict(self.tools)
        for tool in result.tools:
            tools[_tool_identity(tool)] = tool
        result.tools = list(tools.values())

        bindings = dict(self.bindings)
        for binding in result.bindings:
            bindings[_binding_identity(binding)] = binding
        result.bindings = list(bindings.values())

        packages = dict(self.packages)
        for package in result.packages:
            packages[_package_identity(package)] = package
        result.packages = list(packages.values())

        directives = dict(self.directives)
        for directive in result.directives:
            directives[directive.id] = directive
        result.directives = list(directives.values())

        result.warnings = _merged_unique(self.warnings, result.warnings)
        result.suggestions = _merged_unique(self.suggestions, result.suggestions)
        result.transitions = _merged_unique(self.transitions, result.transitions)
        result.ask_history = _merged_unique_records(
            self.ask_history,
            result.ask_history,
        )
        result.iteration_history = _merged_unique_records(
            self.iteration_history,
            result.iteration_history,
        )
        result.tool_calls_made = self.tool_calls_made


@dataclass
class CompilationBudget:
    """Global convergence and resource budget for one compilation."""

    max_steps: int
    max_model_calls: int
    max_seconds: float
    started_at: float = field(default_factory=time.monotonic)
    steps_used: int = 0
    model_calls_used: int = 0
    _seen_states: dict[str, set[str]] = field(default_factory=dict)

    def consume_model_call(self, label: str) -> str | None:
        """Reserve one model call or return an exhaustion diagnostic."""
        timeout = self.check_time()
        if timeout is not None:
            return timeout
        self.model_calls_used += 1
        if self.model_calls_used > self.max_model_calls:
            return (
                f"Compilation model-call budget exhausted during {label}: "
                f"{self.model_calls_used - 1}/{self.max_model_calls} calls used."
            )
        return None

    def consume_step(self, scope: str, state: str) -> str | None:
        """Reserve one compiler step and reject repeated/no-progress states."""
        timeout = self.check_time()
        if timeout is not None:
            return timeout
        self.steps_used += 1
        if self.steps_used > self.max_steps:
            return (
                f"Compilation step budget exhausted in {scope}: "
                f"{self.steps_used - 1}/{self.max_steps} steps used."
            )
        fingerprint = hashlib.sha256(state.encode("utf-8")).hexdigest()
        seen = self._seen_states.setdefault(scope, set())
        if fingerprint in seen:
            return (
                f"Compilation made no progress in {scope}: the same compiler "
                "state was encountered again."
            )
        seen.add(fingerprint)
        return None

    def check_time(self) -> str | None:
        """Return a wall-clock exhaustion diagnostic when the budget elapsed."""
        elapsed = time.monotonic() - self.started_at
        if elapsed <= self.max_seconds:
            return None
        return (
            f"Compilation time budget exhausted after {elapsed:.2f}s "
            f"(limit {self.max_seconds:.2f}s)."
        )


def _tool_identity(tool: dict[str, Any]) -> str:
    function = tool.get("function")
    if isinstance(function, dict) and function.get("name"):
        return str(function["name"]).casefold()
    if tool.get("name"):
        return str(tool["name"]).casefold()
    return repr(tool)


def _binding_identity(binding: dict[str, str]) -> str:
    for key in ("name", "capability", "capability_name", "tool"):
        value = binding.get(key)
        if value:
            return value.casefold()
    return repr(sorted(binding.items()))


def _package_identity(package: dict[str, str]) -> str:
    return package.get("file", repr(sorted(package.items()))).casefold()


def _extend_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def _merged_unique(first: list[str], second: list[str]) -> list[str]:
    result = list(first)
    _extend_unique(result, second)
    return result


def _extend_unique_records(
    target: list[dict[str, Any]],
    values: list[dict[str, Any]],
) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def _merged_unique_records(
    first: list[dict[str, Any]],
    second: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = list(first)
    _extend_unique_records(result, second)
    return result


__all__ = [
    "CompilationBudget",
    "CompositionAccumulator",
    "CompositionEnvelope",
]
