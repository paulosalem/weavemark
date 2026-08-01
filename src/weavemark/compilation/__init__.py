"""WeaveMark compilation strategies and helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .structural import StructuralHelperResult, try_apply_structural_helpers


def __getattr__(name: str) -> Any:
    """Load the structural compiler only when its public helpers are requested."""

    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from . import structural

    value = getattr(structural, name)
    globals()[name] = value
    return value

__all__ = [
    "StructuralHelperResult",
    "try_apply_structural_helpers",
]
