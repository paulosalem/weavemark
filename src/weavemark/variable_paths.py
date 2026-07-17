"""Dotted-path resolution for ``@{a.b.c}`` variable references.

WeaveMark variables may be nested JSON. A dotted name navigates that hierarchy:
each ``.``-separated segment descends one level — a mapping key, or an integer
index into a list/tuple. An exact flat-key match always wins first, so keys that
literally contain dots keep working. This single resolver is shared by the
compile-time substitutor and the runtime engine renderers so ``@{panels.0.beat}``
means the same thing everywhere.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

MISSING: Any = object()


def resolve_variable_path(variables: Mapping[str, Any], name: str) -> Any:
    """Resolve *name* (a flat key or dotted path) against *variables*.

    Returns the resolved value, or :data:`MISSING` when the path cannot be fully
    resolved.
    """

    if name in variables:
        return variables[name]
    if "." not in name:
        return MISSING
    current: Any = variables
    for segment in name.split("."):
        if isinstance(current, Mapping) and segment in current:
            current = current[segment]
        elif isinstance(current, (list, tuple)):
            try:
                index = int(segment)
            except ValueError:
                return MISSING
            if -len(current) <= index < len(current):
                current = current[index]
            else:
                return MISSING
        else:
            return MISSING
    return current


def variable_is_defined(variables: Mapping[str, Any], name: str) -> bool:
    """Whether *name* resolves to a non-None value."""

    value = resolve_variable_path(variables, name)
    return value is not MISSING and value is not None


__all__ = ["MISSING", "resolve_variable_path", "variable_is_defined"]
