"""Custom exceptions for WeaveMark runtime modules."""


class WeaveMarkError(Exception):
    """Base exception for WeaveMark runtime errors."""


class LLMError(WeaveMarkError):
    """Exception raised for LLM-related errors."""


class ConversationError(WeaveMarkError):
    """Exception raised for conversation management errors."""


class ValidationError(WeaveMarkError):
    """Exception raised for validation errors."""
