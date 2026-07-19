"""Lexical primitives for inline WeaveMark directive calls."""

from __future__ import annotations

import re
from dataclasses import dataclass

FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})")
INLINE_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*")
PATH_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "_./~+-"
)
TRAILING_PUNCTUATION = ".,;:!?"


@dataclass(frozen=True)
class InlineDirectiveCall:
    """One delimited ``@name(...)`` call in ordinary Markdown text."""

    name: str
    arguments: str
    start: int
    end: int
    line: int
    column: int


def parse_inline_directive_call(
    line: str,
    start: int,
    name: str,
    open_paren: int,
    line_number: int,
) -> InlineDirectiveCall | str:
    """Parse one balanced inline call or return a source-oriented error."""

    quote: str | None = None
    escaped = False
    depth = 1
    index = open_paren + 1
    while index < len(line):
        char = line[index]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif quote is not None:
            if char == quote:
                quote = None
        elif char in {'"', "'"}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return InlineDirectiveCall(
                    name=name,
                    arguments=line[open_paren + 1 : index],
                    start=start,
                    end=index + 1,
                    line=line_number,
                    column=start + 1,
                )
        index += 1
    return (
        f"Unterminated inline directive '@{name}(' at line {line_number}, "
        f"column {start + 1}."
    )


def parse_path_candidate(line: str, start: int) -> tuple[str | None, int]:
    """Return one shorthand path token and its exclusive end offset."""

    end = start
    while end < len(line) and line[end] in PATH_CHARS:
        end += 1
    if end == start:
        return None, start
    candidate = line[start:end]
    while candidate.endswith(tuple(TRAILING_PUNCTUATION)):
        candidate = candidate[:-1]
        end -= 1
    return (candidate or None), end


def is_fence_close(line: str, marker: str) -> bool:
    """Return whether *line* closes the current Markdown fence."""

    fence_char = re.escape(marker[0])
    return (
        re.fullmatch(
            rf" {{0,3}}{fence_char}{{{len(marker)},}}[ \t]*(?:\r?\n)?",
            line,
        )
        is not None
    )


def has_closing_tick_run(line: str, start: int, tick_count: int) -> bool:
    """Return whether an inline-code opener has a same-width closer."""

    index = start
    while index < len(line):
        if line[index] != "`":
            index += 1
            continue
        end = index + 1
        while end < len(line) and line[end] == "`":
            end += 1
        if end - index == tick_count:
            return True
        index = end
    return False


__all__ = [
    "FENCE_OPEN_RE",
    "INLINE_NAME_RE",
    "InlineDirectiveCall",
    "has_closing_tick_run",
    "is_fence_close",
    "parse_inline_directive_call",
    "parse_path_candidate",
]
