"""Strict wire schema for semantic compiler responses."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class CompilerProtocolError(ValueError):
    """Raised when a semantic compiler response violates the wire contract."""


class _StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class PromptPayload(_StrictModel):
    """One named prompt returned by the semantic compiler."""

    text: str
    role: Literal["system", "user", "assistant", "tool"] | None


class OutputPayload(_StrictModel):
    """One text or image output contract."""

    type: Literal["text", "image"] = "text"
    format: str | None = None
    enforce: str | None = None
    body: str | None = None
    size: str | None = None
    quality: str | None = None
    model: str | None = None
    n: int | None = None
    edit: bool | None = None
    file: str | None = None

    def contract_dict(self) -> dict[str, Any]:
        """Return the dictionary shape consumed by ``OutputContract``."""
        return self.model_dump(exclude_none=True)


class CompilePayload(_StrictModel):
    """Closed compile options emitted by the semantic compiler."""

    format: str | None = None
    context: Literal["auto", "cascade", "local"] | None = None
    images: Literal["on", "off"] | None = None
    weavemark_version: str | None = None


class ToolFunctionPayload(_StrictModel):
    """Function metadata in provider-neutral tool schema form."""

    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolPayload(_StrictModel):
    """One LLM-facing function tool."""

    type: Literal["function"] = "function"
    function: ToolFunctionPayload


class PackagePayload(_StrictModel):
    """One execution-phase package instruction."""

    file: str
    instructions: str | None = None
    body: str | None = None
    from_: str | None = Field(default=None, alias="from")

    @model_validator(mode="after")
    def validate_source(self) -> PackagePayload:
        """Require one semantic instruction source or one conversion source."""

        has_semantic_source = self.instructions is not None or bool(
            self.body and self.body.strip()
        )
        if has_semantic_source == (self.from_ is not None):
            raise ValueError(
                "package requires instructions/body or from, but not both"
            )
        return self

    def package_dict(self) -> dict[str, str]:
        """Return the structural compiler's package dictionary shape."""
        result = {"file": self.file}
        if self.instructions is not None:
            result["instructions"] = self.instructions
        if self.body is not None and self.body.strip():
            result["body"] = self.body
        if self.from_ is not None:
            result["from"] = self.from_
        return result


class SourceSpanPayload(_StrictModel):
    """One-based source span for a directive application."""

    start_line: int
    end_line: int
    start_column: int = 1
    end_column: int | None = None


class DirectivePayload(_StrictModel):
    """One concrete directive application."""

    id: str
    name: str
    header: str
    body: str
    line: int
    depth: int
    source_span: SourceSpanPayload
    parent_scope_id: str | None = None


class CompositionWireResult(_StrictModel):
    """Complete semantic compiler response.

    Every field is required, including empty collections. This prevents model
    omissions from looking like successful empty metadata.
    """

    prompt: str
    prompts: dict[str, PromptPayload]
    compile: CompilePayload
    tools: list[ToolPayload]
    bindings: list[dict[str, str]]
    execution: dict[str, Any]
    emits: dict[str, str]
    outputs: dict[str, OutputPayload]
    packages: list[PackagePayload]
    references: dict[str, str]
    directives: list[DirectivePayload]
    analysis: str
    warnings: list[str]
    errors: list[str]
    suggestions: list[str]

    @model_validator(mode="after")
    def validate_prompt_consistency(self) -> CompositionWireResult:
        """Keep the primary/default prompt representation unambiguous."""
        default = self.prompts.get("default")
        if default is not None and default.text != self.prompt:
            raise ValueError("prompts.default.text must equal prompt")
        return self


def parse_wire_result(raw_response: str) -> CompositionWireResult:
    """Parse one strict JSON response and reject duplicate object keys."""
    try:
        data = json.loads(raw_response, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, CompilerProtocolError) as exc:
        raise CompilerProtocolError(f"invalid compiler JSON: {exc}") from exc
    try:
        return CompositionWireResult.model_validate(data, strict=True)
    except ValidationError as exc:
        raise CompilerProtocolError(f"compiler response schema violation: {exc}") from exc


def compiler_response_format() -> dict[str, Any]:
    """Return provider-side JSON Schema guidance for the compiler protocol.

    Provider ``strict`` mode cannot represent the intentionally dynamic tool
    parameter schemas and execution config. The local parser remains the
    authoritative strict boundary: it rejects duplicate keys, missing fields,
    wrong types, and extra fields with Pydantic before compilation continues.
    """
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "weavemark_composition_result",
            "strict": False,
            "schema": CompositionWireResult.model_json_schema(
                by_alias=True,
            ),
        },
    }


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CompilerProtocolError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


__all__ = [
    "CompilerProtocolError",
    "CompositionWireResult",
    "compiler_response_format",
    "parse_wire_result",
]
