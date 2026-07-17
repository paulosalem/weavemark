"""Typed diagnostics shared by compiler, API, and CLI surfaces."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

DiagnosticSeverity = Literal["error", "warning", "suggestion"]


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """One stable, machine-readable WeaveMark diagnostic."""

    code: str
    message: str
    severity: DiagnosticSeverity = "error"
    source: str | None = None
    line: int | None = None
    directive: str | None = None
    parameter: str | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable diagnostic payload."""

        data: dict[str, Any] = {
            "code": self.code,
            "type": self.severity,
            "severity": self.severity,
            "message": self.message,
        }
        for key in ("source", "line", "directive", "parameter", "suggestion"):
            value = getattr(self, key)
            if value is not None:
                data[key] = value
        return data

    def format_human(self) -> str:
        """Render a concise diagnostic with available source context."""

        location = self.source or ""
        if self.line is not None:
            location = f"{location}:{self.line}" if location else f"line {self.line}"
        subject = self.directive or ""
        if self.parameter:
            subject = f"{subject} parameter {self.parameter}".strip()
        context = " · ".join(part for part in (location, subject) if part)
        prefix = f"{context}: " if context else ""
        suffix = f" Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"{prefix}{self.message}{suffix}"


class UserDiagnosticError(Exception):
    """Expected user-facing failure that must not produce a traceback."""

    def __init__(self, diagnostic: Diagnostic, *, exit_code: int = 2) -> None:
        self.diagnostic = diagnostic
        self.exit_code = exit_code
        super().__init__(diagnostic.format_human())


def diagnostics_from_messages(
    *,
    warnings: list[str],
    errors: list[str],
    suggestions: list[str],
    source: str | None = None,
) -> list[Diagnostic]:
    """Convert legacy compiler message collections into typed diagnostics."""

    diagnostics = [
        _diagnostic_from_message(
            message,
            code="WM-COMPILER-WARNING",
            severity="warning",
            source=source,
        )
        for message in warnings
    ]
    diagnostics.extend(
        _diagnostic_from_message(
            message,
            code="WM-COMPILER-ERROR",
            severity="error",
            source=source,
        )
        for message in errors
    )
    diagnostics.extend(
        _diagnostic_from_message(
            message,
            code="WM-COMPILER-SUGGESTION",
            severity="suggestion",
            source=source,
        )
        for message in suggestions
    )
    return diagnostics


def _diagnostic_from_message(
    message: str,
    *,
    code: str,
    severity: DiagnosticSeverity,
    source: str | None,
) -> Diagnostic:
    line_match = re.search(r"\bline\s+(\d+)\b", message, flags=re.IGNORECASE)
    directive_match = re.search(r"@[A-Za-z_][\w.-]*", message)
    parameter_match = re.search(
        r"\b(?:parameter|option)\s+['\"]?([A-Za-z_][\w.-]*)",
        message,
        flags=re.IGNORECASE,
    )
    return Diagnostic(
        code=code,
        message=message,
        severity=severity,
        source=source,
        line=int(line_match.group(1)) if line_match else None,
        directive=directive_match.group(0) if directive_match else None,
        parameter=parameter_match.group(1) if parameter_match else None,
    )


__all__ = [
    "Diagnostic",
    "DiagnosticSeverity",
    "UserDiagnosticError",
    "diagnostics_from_messages",
]
