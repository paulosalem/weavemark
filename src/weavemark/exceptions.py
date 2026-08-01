"""Custom exceptions for WeaveMark runtime modules."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from weavemark.compilation.result import CompositionResult


class WeaveMarkError(Exception):
    """Base exception for WeaveMark runtime errors."""


class WeaveMarkCompilationError(WeaveMarkError):
    """Raised when execution is requested for a spec that did not compile."""

    def __init__(self, result: CompositionResult) -> None:
        self.result = result
        message = "WeaveMark compilation failed"
        if result.errors:
            message += ": " + "; ".join(result.errors)
        super().__init__(message)


class LLMError(WeaveMarkError):
    """Exception raised for LLM-related errors."""


class ConversationError(WeaveMarkError):
    """Exception raised for conversation management errors."""


class ValidationError(WeaveMarkError):
    """Exception raised for validation errors."""
