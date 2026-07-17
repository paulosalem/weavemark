"""Compilation trace records for stepwise WeaveMark composition."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceSpan:
    """One-based source span for a WeaveMark directive application."""

    start_line: int
    end_line: int
    start_column: int = 1
    end_column: int | None = None

    def to_dict(self) -> dict[str, int]:
        data = {
            "start_line": self.start_line,
            "end_line": self.end_line,
            "start_column": self.start_column,
        }
        if self.end_column is not None:
            data["end_column"] = self.end_column
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SourceSpan:
        return cls(
            start_line=int(data["start_line"]),
            end_line=int(data["end_line"]),
            start_column=int(data.get("start_column", 1)),
            end_column=(
                int(data["end_column"]) if data.get("end_column") is not None else None
            ),
        )


@dataclass(frozen=True)
class DirectiveApplication:
    """A concrete directive application compiled by one compilation step."""

    id: str
    name: str
    header: str
    body: str
    line: int
    depth: int
    source_span: SourceSpan
    parent_scope_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "header": self.header,
            "body": self.body,
            "line": self.line,
            "depth": self.depth,
            "source_span": self.source_span.to_dict(),
        }
        if self.parent_scope_id is not None:
            data["parent_scope_id"] = self.parent_scope_id
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DirectiveApplication:
        span_data = data.get("source_span")
        if not isinstance(span_data, dict):
            line = int(data.get("line", 1))
            span = SourceSpan(start_line=line, end_line=line)
        else:
            span = SourceSpan.from_dict(span_data)
        return cls(
            id=str(data.get("id") or f"app-{span.start_line}"),
            name=str(data["name"]),
            header=str(data.get("header") or f"@{data['name']}"),
            body=str(data.get("body") or ""),
            line=int(data.get("line", span.start_line)),
            depth=int(data.get("depth", 0)),
            source_span=span,
            parent_scope_id=(
                str(data["parent_scope_id"])
                if data.get("parent_scope_id") is not None
                else None
            ),
        )


@dataclass(frozen=True)
class StepJudgment:
    """Diagnostic judgment for a previous compilation step."""

    needs_improvement: bool
    good_points: list[str]
    bad_points: list[str]
    suggestions: list[str]
    compliance_notes: list[str]
    constraint_findings: list[str]
    directive_feedback: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "needs_improvement": self.needs_improvement,
            "good_points": self.good_points,
            "bad_points": self.bad_points,
            "suggestions": self.suggestions,
            "compliance_notes": self.compliance_notes,
            "constraint_findings": self.constraint_findings,
            "directive_feedback": self.directive_feedback,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StepJudgment:
        feedback: dict[str, list[str]] = {}
        raw_feedback = data.get("directive_feedback", {})
        if isinstance(raw_feedback, dict):
            for key, value in raw_feedback.items():
                if isinstance(value, list):
                    feedback[str(key)] = [str(item) for item in value]
                else:
                    feedback[str(key)] = [str(value)]
        return cls(
            needs_improvement=bool(data.get("needs_improvement")),
            good_points=_string_list(data.get("good_points")),
            bad_points=_string_list(data.get("bad_points")),
            suggestions=_string_list(data.get("suggestions")),
            compliance_notes=_string_list(data.get("compliance_notes")),
            constraint_findings=_string_list(data.get("constraint_findings")),
            directive_feedback=feedback,
        )


@dataclass
class CompilationStep:
    """One atomic compiler operation over one or more sibling directives."""

    id: str
    iteration: int
    applications: list[DirectiveApplication]
    envelope: Any
    previous_step_id: str | None = None
    judgment: StepJudgment | None = None

    @property
    def needs_improvement(self) -> bool:
        return bool(self.judgment and self.judgment.needs_improvement)

    def to_dict(self) -> dict[str, Any]:
        envelope = self.envelope
        if hasattr(envelope, "to_dict"):
            envelope_data = envelope.to_dict(include_trace=False)
        else:
            envelope_data = str(envelope)
        data: dict[str, Any] = {
            "id": self.id,
            "iteration": self.iteration,
            "applications": [application.to_dict() for application in self.applications],
            "envelope": envelope_data,
        }
        if self.previous_step_id is not None:
            data["previous_step_id"] = self.previous_step_id
        if self.judgment is not None:
            data["judgment"] = self.judgment.to_dict()
        return data


@dataclass
class CompilationTrace:
    """Ordered sequence of compilation steps."""

    steps: list[CompilationStep] = field(default_factory=list)

    def extend(self, steps: list[CompilationStep]) -> None:
        self.steps.extend(steps)

    def to_dict(self) -> dict[str, Any]:
        return {"steps": [step.to_dict() for step in self.steps]}


def directives_from_json(value: Any) -> list[DirectiveApplication]:
    """Parse the optional ``<directives>`` envelope JSON value."""

    if value is None:
        return []
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []

    applications: list[DirectiveApplication] = []
    for item in value:
        if isinstance(item, dict) and item.get("name"):
            applications.append(DirectiveApplication.from_dict(item))
    return applications


def directives_to_json(applications: list[DirectiveApplication]) -> list[dict[str, Any]]:
    """Convert directive applications to JSON-serializable dictionaries."""

    return [application.to_dict() for application in applications]


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []
