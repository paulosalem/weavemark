"""Compile-time support for the standard-library ``@ask`` directive."""

from __future__ import annotations

import re
import textwrap
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from weavemark.compilation.args import parse_header_args
from weavemark.compilation.macros import WeaveMarkDefinition

_DIRECTIVE_RE = re.compile(
    r"^(?P<indent>[ \t]*)@(?P<name>[A-Za-z_][A-Za-z0-9_.-]*\??)"
    r"(?P<rest>(?:\s+.*)?)$"
)
_PERCENT_RE = re.compile(r"^(?P<value>\d+(?:\.\d+)?)%?$")


@dataclass(frozen=True)
class AskDirective:
    """One unresolved compile-time ``@ask`` directive found in a spec."""

    name: str
    line_number: int
    depth: int
    question_type: str
    detail_level: str
    body: str


@dataclass(frozen=True)
class AskPrompt:
    """Question request sent by the WeaveMark compiler to a host application."""

    question: str
    question_type: str
    detail_level: str
    scope: str = ""
    reason: str = ""
    round_index: int = 1
    question_index: int = 1


def find_ask_directives(
    spec_text: str,
    semantic_definitions: Mapping[str, WeaveMarkDefinition],
) -> tuple[list[AskDirective], list[str]]:
    """Return unresolved ``@ask`` calls and syntax errors.

    ``@ask`` is a standard-library semantic directive, so a line is treated as
    an ask call only when its directive name is bound to the imported
    ``semantics`` ask definition (including aliases such as ``@semantic.ask``).
    """

    ask_names = {
        call_name
        for call_name, definition in semantic_definitions.items()
        if definition.name == "ask" and definition.phase == "compile"
    }
    if not ask_names:
        return [], []

    lines = spec_text.splitlines()
    directives: list[AskDirective] = []
    errors: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        match = _DIRECTIVE_RE.match(line)
        if match is None:
            index += 1
            continue

        name = match.group("name")
        indent = match.group("indent")
        if name not in ask_names:
            index += 1
            continue

        block, _next_index = _collect_indented_block(lines, index + 1, len(indent))
        parsed = _parse_ask_header(
            match.group("rest").strip(),
            line_number=index + 1,
        )
        if isinstance(parsed, str):
            errors.append(parsed)
        else:
            question_type, detail_level = parsed
            directives.append(
                AskDirective(
                    name=name,
                    line_number=index + 1,
                    depth=len(indent),
                    question_type=question_type,
                    detail_level=detail_level,
                    body=block,
                )
            )
        index += 1

    directives.sort(key=lambda item: (-item.depth, item.line_number))
    return directives, errors


def format_ask_directives_for_prompt(directives: list[AskDirective]) -> str:
    """Render active ``@ask`` calls for the LLM compiler prompt."""

    if not directives:
        return "No active @ask directives detected."

    lines: list[str] = []
    for ordinal, directive in enumerate(directives, start=1):
        body = directive.body.strip()
        if body:
            body = textwrap.shorten(body.replace("\n", " "), width=280)
        else:
            body = "(no explicit body; applies to the current enclosing scope)"
        lines.append(
            f"{ordinal}. `@{directive.name}` at line {directive.line_number}, "
            f"depth {directive.depth}, question_type: {directive.question_type}, "
            f"detail_level: {directive.detail_level}\n"
            f"   Body/scope preview: {body}"
        )
    return "\n".join(lines)


def composition_result_to_weavemark_text(result: Any) -> str:
    """Convert a parsed composition result into a WeaveMark-like next pass.

    This is intentionally conservative and text-first: it preserves primary
    prompt text, named prompt blocks, and emitted artifacts so unresolved
    ``@ask`` directives can continue through another compilation round without
    pretending the intermediate XML is final output.
    """

    parts: list[str] = []
    if getattr(result, "composed_prompt", "").strip():
        parts.append(str(result.composed_prompt).strip())

    prompts = getattr(result, "prompts", {}) or {}
    prompt_roles = getattr(result, "prompt_roles", {}) or {}
    if list(prompts.keys()) != ["default"]:
        for name, prompt_text in prompts.items():
            header = f"@prompt {name}"
            role = prompt_roles.get(name)
            if role:
                header += f" role: {role}"
            parts.append(f"{header}\n{_indent(str(prompt_text).strip())}")
    elif not parts and prompts.get("default", "").strip():
        parts.append(str(prompts["default"]).strip())

    for file_name, content in (getattr(result, "emits", {}) or {}).items():
        parts.append(f"@emit file: {file_name}\n{_indent(str(content).strip())}")

    return "\n\n".join(part for part in parts if part.strip())


def ask_history_for_prompt(history: list[dict[str, str]]) -> str:
    """Format prior host answers for subsequent @ask composition rounds."""

    if not history:
        return "No @ask answers have been collected yet."
    lines = []
    for index, item in enumerate(history, start=1):
        lines.append(
            f"{index}. Q ({item.get('question_type', 'question')}, "
            f"{item.get('detail_level', '20%')}): {item.get('question', '')}\n"
            f"   A: {item.get('answer', '')}"
        )
    return "\n".join(lines)


def _parse_ask_header(rest: str, *, line_number: int) -> tuple[str, str] | str:
    parsed = parse_header_args(rest)
    if parsed.errors:
        return f"@ask at line {line_number}: " + " ".join(parsed.errors)
    positional, options = parsed.positional, parsed.options
    unsupported = sorted(key for key in options if key != "detail_level")
    if unsupported:
        return (
            f"@ask at line {line_number} has unsupported option(s): "
            + ", ".join(unsupported)
            + "."
        )

    question_type = " ".join(positional).strip() or "clarifying question"
    detail_level = options.get("detail_level", "20%")
    normalized = _normalize_detail_level(detail_level)
    if normalized is None:
        return (
            f"@ask at line {line_number} has invalid detail_level {detail_level!r}; "
            "expected a percentage greater than 0% and no greater than 100%."
        )
    return question_type, normalized


def _normalize_detail_level(value: str) -> str | None:
    cleaned = value.strip().strip("\"'")
    match = _PERCENT_RE.fullmatch(cleaned)
    if match is None:
        return None
    number = float(match.group("value"))
    if number <= 0 or number > 100:
        return None
    if number.is_integer():
        return f"{int(number)}%"
    return f"{number:g}%"

def _collect_indented_block(
    lines: list[str],
    start: int,
    parent_indent: int,
) -> tuple[str, int]:
    block: list[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            next_nonblank = next(
                (
                    future
                    for future in range(index + 1, len(lines))
                    if lines[future].strip()
                ),
                None,
            )
            if (
                next_nonblank is None
                or _indent_width(lines[next_nonblank]) <= parent_indent
            ):
                break
            block.append(line)
            index += 1
            continue
        if _indent_width(line) <= parent_indent:
            break
        block.append(line)
        index += 1
    return textwrap.dedent("\n".join(block)).strip("\n"), index


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _indent(text: str) -> str:
    if not text:
        return "  "
    return "\n".join(f"  {line}" if line else "" for line in text.splitlines())
