"""Deterministic validation of WeaveMark directive names."""

from __future__ import annotations

import difflib
import re
from collections.abc import Mapping
from typing import Any

CORE_DIRECTIVES = frozenset(
    {
        "bind",
        "body",
        "compile",
        "define",
        "directives?",
        "effect",
        "else",
        "else_if",
        "embed",
        "emit",
        "execute",
        "if",
        "include",
        "match",
        "module",
        "note",
        "output",
        "package",
        "param",
        "phase",
        "promplet",
        "prompt",
        "returns",
        "scope",
        "structure?",
        "tool",
        "use",
        "vars?",
    }
)

_DIRECTIVE_RE = re.compile(
    r"^(?P<indent>[ \t]*)@(?P<name>[A-Za-z_][A-Za-z0-9_.-]*\??)(?:\s|$)"
)
_OPAQUE_BODY_DIRECTIVES = frozenset(
    {"embed", "execute", "note", "output", "package", "tool"}
)


def validate_directive_names(
    source: str,
    semantic_definitions: Mapping[str, Any],
) -> list[str]:
    """Return source-oriented errors for unknown directive names.

    Imported/local semantic definitions are valid directives. Fenced Markdown,
    escaped ``@@`` lines, and bodies owned by opaque directives are ignored.
    """
    known = {*CORE_DIRECTIVES, *semantic_definitions}
    errors: list[str] = []
    in_fence = False
    opaque_indent: int | None = None

    for line_number, line in enumerate(source.splitlines(), start=1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith("@@"):
            continue
        if opaque_indent is not None:
            if not stripped or indent > opaque_indent:
                continue
            opaque_indent = None

        match = _DIRECTIVE_RE.match(line)
        if match is None:
            continue
        name = match.group("name")
        if name not in known:
            suggestion = difflib.get_close_matches(name, sorted(known), n=1)
            detail = f"Unknown directive '@{name}' at line {line_number}."
            if suggestion:
                detail += f" Did you mean '@{suggestion[0]}'?"
            errors.append(detail)
            continue
        if name in _OPAQUE_BODY_DIRECTIVES:
            opaque_indent = len(match.group("indent"))
    return errors


__all__ = ["CORE_DIRECTIVES", "validate_directive_names"]
