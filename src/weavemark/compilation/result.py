"""Stable typed result contract for WeaveMark compilation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from weavemark.compilation.diagnostics import diagnostics_from_messages
from weavemark.compilation.multimodal import ImageRef, OutputContract
from weavemark.compilation.trace import (
    CompilationTrace,
    DirectiveApplication,
    directives_to_json,
)
from weavemark.protection import ProtectionContext

if TYPE_CHECKING:
    from weavemark.compilation.provenance import ProvenanceManifest


@dataclass
class CompositionResult:
    """Complete typed result of one WeaveMark compilation."""

    composed_prompt: str
    prompts: dict[str, str] = field(default_factory=dict)
    prompt_roles: dict[str, str] = field(default_factory=dict)
    prompt_images: dict[str, list[ImageRef]] = field(default_factory=dict)
    prompt_outputs: dict[str, OutputContract] = field(default_factory=dict)
    raw_response: str = ""
    analysis: str = ""
    compile: dict[str, Any] = field(default_factory=dict)
    tools: list[dict[str, Any]] = field(default_factory=list)
    bindings: list[dict[str, str]] = field(default_factory=list)
    execution: dict[str, Any] = field(default_factory=dict)
    emits: dict[str, str] = field(default_factory=dict)
    packages: list[dict[str, str]] = field(default_factory=list)
    references: list[dict[str, Any]] = field(default_factory=list)
    reference_contents: dict[str, str] = field(
        default_factory=dict,
        repr=False,
        compare=False,
    )
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    transitions: list[str] = field(default_factory=list)
    ask_history: list[dict[str, str]] = field(default_factory=list)
    iteration_history: list[dict[str, Any]] = field(default_factory=list)
    directives: list[DirectiveApplication] = field(default_factory=list)
    compilation_trace: CompilationTrace | None = None
    tool_calls_made: int = 0
    model_calls_made: int = 0
    partial_messages: list[dict[str, Any]] = field(default_factory=list)
    unresolved_tool_calls: list[dict[str, Any]] = field(default_factory=list)
    source_path: str | None = None
    provenance: ProvenanceManifest | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    protection: ProtectionContext | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    @property
    def diagnostics(self) -> list[dict[str, Any]]:
        """Return stable machine-readable diagnostics."""

        return [
            diagnostic.to_dict()
            for diagnostic in diagnostics_from_messages(
                warnings=self.warnings,
                errors=self.errors,
                suggestions=self.suggestions,
                source=self.source_path,
            )
        ]

    def to_dict(
        self,
        *,
        include_trace: bool = True,
        include_provenance: bool = True,
    ) -> dict[str, Any]:
        """Return the complete JSON-serializable result."""

        data: dict[str, Any] = {
            "composed_prompt": self.composed_prompt,
            "raw_response": self.raw_response,
            "analysis": self.analysis,
            "warnings": self.warnings,
            "errors": self.errors,
            "suggestions": self.suggestions,
            "diagnostics": self.diagnostics,
            "transitions": self.transitions,
            "tool_calls_made": self.tool_calls_made,
            "model_calls_made": self.model_calls_made,
        }
        optional_values: tuple[tuple[str, Any], ...] = (
            ("prompts", self.prompts),
            ("prompt_roles", self.prompt_roles),
            ("compile", self.compile),
            ("tools", self.tools),
            ("bindings", self.bindings),
            ("execution", self.execution),
            ("emits", self.emits),
            ("packages", self.packages),
            ("references", self.references),
            ("ask_history", self.ask_history),
            ("iteration_history", self.iteration_history),
            ("partial_messages", self.partial_messages),
            ("unresolved_tool_calls", self.unresolved_tool_calls),
        )
        for key, value in optional_values:
            if value:
                data[key] = value
        if self.prompt_images:
            data["prompt_images"] = {
                name: [ref.to_dict() for ref in refs]
                for name, refs in self.prompt_images.items()
            }
        if self.prompt_outputs:
            data["prompt_outputs"] = {
                name: contract.to_dict()
                for name, contract in self.prompt_outputs.items()
            }
        if self.directives:
            data["directives"] = directives_to_json(self.directives)
        if self.source_path is not None:
            data["source_path"] = self.source_path
        if include_trace and self.compilation_trace is not None:
            data["compilation_trace"] = self.compilation_trace.to_dict()
        if include_provenance and self.provenance is not None:
            data["provenance"] = self.provenance.to_dict()
        return data


__all__ = ["CompositionResult"]
