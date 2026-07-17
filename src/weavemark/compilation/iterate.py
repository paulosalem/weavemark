"""Compile-time support for the standard-library ``@iterate`` directive."""

from __future__ import annotations

import re
import textwrap
from collections.abc import Mapping
from dataclasses import dataclass

from weavemark.compilation.args import parse_header_args
from weavemark.compilation.macros import WeaveMarkDefinition
from weavemark.compilation.trace import DirectiveApplication, SourceSpan

_DIRECTIVE_RE = re.compile(
    r"^(?P<indent>[ \t]*)@(?P<name>[A-Za-z_][A-Za-z0-9_.-]*\??)"
    r"(?P<rest>(?:\s+.*)?)$"
)
_STEP_EXCLUDED_DIRECTIVES = {
    "ask",
    "assert",
    "bind",
    "body",
    "compile",
    "define",
    "effect",
    "else",
    "else_if",
    "include",
    "iterate",
    "module",
    "note",
    "param",
    "phase",
    "promplet",
    "returns",
    "scope",
    "use",
}


@dataclass(frozen=True)
class IterateAskPrelude:
    """Leading ``@ask`` wrapper that clarifies an ``@iterate`` target."""

    name: str
    rest: str
    line_number: int

    def wrap(self, body: str) -> str:
        """Render this prelude as a normal ``@ask`` directive around *body*."""

        header = f"@{self.name}"
        if self.rest:
            header += f" {self.rest}"
        if not body.strip():
            return header
        return f"{header}\n{_indent(body)}"


@dataclass(frozen=True)
class IterateDirective:
    """One unresolved compile-time ``@iterate`` directive found in a spec."""

    name: str
    line_number: int
    depth: int
    turns: int | None
    body: str
    start_index: int
    end_index: int
    ask_prelude: IterateAskPrelude | None = None
    applies_to_whole_spec: bool = False

    @property
    def target_body(self) -> str:
        """Return the body that should be compiled, judged, and improved."""

        return self.body


def find_iterate_directives(
    spec_text: str,
    semantic_definitions: Mapping[str, WeaveMarkDefinition],
) -> tuple[list[IterateDirective], list[str]]:
    """Return unresolved ``@iterate`` calls and syntax errors.

    ``@iterate`` is a standard-library semantic directive, so a line is treated
    as an iteration call only when its directive name is bound to the imported
    compile-phase ``iterate`` semantic definition.
    """

    iterate_names = {
        call_name
        for call_name, definition in semantic_definitions.items()
        if definition.name == "iterate" and definition.phase == "compile"
    }
    if not iterate_names:
        return [], []

    ask_names = {
        call_name
        for call_name, definition in semantic_definitions.items()
        if definition.name == "ask" and definition.phase == "compile"
    }
    lines = spec_text.splitlines()
    directives: list[IterateDirective] = []
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
        if name not in iterate_names:
            index += 1
            continue

        block, next_index = _collect_indented_block(lines, index + 1, len(indent))
        parsed = _parse_iterate_header(
            match.group("rest").strip(),
            line_number=index + 1,
        )
        if isinstance(parsed, str):
            errors.append(parsed)
            index += 1
            continue

        turns = parsed
        prelude_result = _extract_ask_prelude(
            block,
            ask_names,
            parent_line_number=index + 1,
        )
        if isinstance(prelude_result, str):
            errors.append(prelude_result)
            index += 1
            continue

        ask_prelude, target_body = prelude_result
        applies_to_whole_spec = not block.strip()
        directives.append(
            IterateDirective(
                name=name,
                line_number=index + 1,
                depth=len(indent),
                turns=turns,
                body=target_body,
                start_index=index,
                end_index=next_index,
                ask_prelude=ask_prelude,
                applies_to_whole_spec=applies_to_whole_spec,
            )
        )
        index += 1

    directives.sort(key=lambda item: (-item.depth, item.line_number))
    return directives, errors


def format_iterate_directives_for_prompt(directives: list[IterateDirective]) -> str:
    """Render active ``@iterate`` calls for diagnostics and compiler prompts."""

    if not directives:
        return "No active @iterate directives detected."

    lines: list[str] = []
    for ordinal, directive in enumerate(directives, start=1):
        target = (
            "(whole containing spec)"
            if directive.applies_to_whole_spec
            else textwrap.shorten(
                directive.target_body.strip().replace("\n", " "),
                width=280,
            )
        )
        turns = "config default" if directive.turns is None else str(directive.turns)
        ask = "yes" if directive.ask_prelude is not None else "no"
        lines.append(
            f"{ordinal}. `@{directive.name}` at line {directive.line_number}, "
            f"depth {directive.depth}, turns: {turns}, ask wrapper: {ask}\n"
            f"   Target preview: {target}"
        )
    return "\n".join(lines)


def replace_iterate_directive(
    spec_text: str,
    directive: IterateDirective,
    replacement: str,
) -> str:
    """Replace *directive* in *spec_text* with *replacement* prompt text."""

    if directive.applies_to_whole_spec:
        return replacement.strip()

    lines = spec_text.splitlines()
    replacement_lines = _indent(replacement.strip(), " " * directive.depth).splitlines()
    updated = [
        *lines[: directive.start_index],
        *replacement_lines,
        *lines[directive.end_index :],
    ]
    return "\n".join(updated).strip("\n")


def spec_without_whole_iterate_directive(
    spec_text: str,
    directive: IterateDirective,
) -> str:
    """Return the whole-spec target for a bodiless ``@iterate`` directive."""

    lines = spec_text.splitlines()
    updated = [*lines[: directive.start_index], *lines[directive.end_index :]]
    return "\n".join(updated).strip("\n")


def find_next_compilation_step(
    spec_text: str,
    semantic_definitions: Mapping[str, WeaveMarkDefinition],
) -> list[DirectiveApplication]:
    """Return the next innermost sibling directive group to compile.

    The grouping is intentionally conservative: only contiguous, ready sibling
    directive applications at the same indentation depth are grouped.
    """

    applications = _directive_applications(spec_text, semantic_definitions)
    if not applications:
        return []

    ready = [
        application
        for application in applications
        if not _has_ready_child(application, applications)
    ]
    if not ready:
        return []
    max_depth = max(application.depth for application in ready)
    ready_at_depth = [
        application for application in ready if application.depth == max_depth
    ]
    first = min(ready_at_depth, key=lambda item: item.source_span.start_line)
    group = [first]
    previous = first
    for candidate in sorted(ready_at_depth, key=lambda item: item.source_span.start_line):
        if candidate is first:
            continue
        if (
            candidate.parent_scope_id == first.parent_scope_id
            and candidate.source_span.start_line == previous.source_span.end_line + 1
        ):
            group.append(candidate)
            previous = candidate
        elif candidate.source_span.start_line > previous.source_span.end_line:
            break
    return group


def source_for_applications(
    spec_text: str,
    applications: list[DirectiveApplication],
) -> str:
    """Return source text covered by *applications*."""

    if not applications:
        return spec_text
    lines = spec_text.splitlines()
    start = min(application.source_span.start_line for application in applications) - 1
    end = max(application.source_span.end_line for application in applications)
    return textwrap.dedent("\n".join(lines[start:end])).strip("\n")


def replace_applications(
    spec_text: str,
    applications: list[DirectiveApplication],
    replacement: str,
) -> str:
    """Replace the source span covered by *applications* with *replacement*."""

    if not applications:
        return replacement.strip()
    lines = spec_text.splitlines()
    start = min(application.source_span.start_line for application in applications) - 1
    end = max(application.source_span.end_line for application in applications)
    depth = min(application.depth for application in applications)
    replacement_lines = _indent(replacement.strip(), " " * depth).splitlines()
    return "\n".join([*lines[:start], *replacement_lines, *lines[end:]]).strip("\n")


def step_key(applications: list[DirectiveApplication]) -> str:
    """Return a stable lineage key for a directive application group."""

    return "|".join(application.id for application in applications)


def _directive_applications(
    spec_text: str,
    semantic_definitions: Mapping[str, WeaveMarkDefinition],
) -> list[DirectiveApplication]:
    semantic_names = {
        call_name
        for call_name, definition in semantic_definitions.items()
        if definition.phase == "compile"
    }
    lines = spec_text.splitlines()
    applications: list[DirectiveApplication] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = _DIRECTIVE_RE.match(line)
        if match is None:
            index += 1
            continue
        name = match.group("name")
        indent = match.group("indent")
        block, next_index = _collect_indented_block(lines, index + 1, len(indent))
        if not _is_step_directive(name, semantic_names):
            index += 1
            continue
        line_number = index + 1
        end_line = max(line_number, next_index)
        depth = len(indent)
        parent_scope_id = _parent_scope_id(lines, index, depth)
        applications.append(
            DirectiveApplication(
                id=f"app-{line_number}-{name}",
                name=name,
                header=line.strip(),
                body=block,
                line=line_number,
                depth=depth,
                source_span=SourceSpan(
                    start_line=line_number,
                    end_line=end_line,
                    start_column=depth + 1,
                    end_column=len(lines[end_line - 1]) + 1 if lines else None,
                ),
                parent_scope_id=parent_scope_id,
            )
        )
        index += 1
    return applications


def _is_step_directive(name: str, semantic_names: set[str]) -> bool:
    root_name = name.split(".", 1)[-1]
    if root_name in _STEP_EXCLUDED_DIRECTIVES:
        return False
    if root_name in semantic_names or name in semantic_names:
        return True
    return root_name in {
        "embed",
        "emit",
        "execute",
        "if",
        "match",
        "output",
        "prompt",
        "tool",
    }


def _parent_scope_id(lines: list[str], directive_index: int, depth: int) -> str | None:
    for index in range(directive_index - 1, -1, -1):
        line = lines[index]
        if not line.strip():
            continue
        line_depth = _indent_width(line)
        if line_depth < depth:
            match = _DIRECTIVE_RE.match(line)
            if match is not None:
                return f"scope-{index + 1}-{match.group('name')}"
            return f"scope-{index + 1}"
    return "root"


def _has_ready_child(
    parent: DirectiveApplication,
    applications: list[DirectiveApplication],
) -> bool:
    for candidate in applications:
        if candidate is parent:
            continue
        if (
            candidate.source_span.start_line > parent.source_span.start_line
            and candidate.source_span.end_line <= parent.source_span.end_line
            and candidate.depth > parent.depth
        ):
            return True
    return False


def _parse_iterate_header(rest: str, *, line_number: int) -> int | None | str:
    parsed = parse_header_args(rest)
    if parsed.errors:
        return f"@iterate at line {line_number}: " + " ".join(parsed.errors)
    positional, options = parsed.positional, parsed.options
    if options:
        return (
            f"@iterate at line {line_number} does not accept named options; "
            "use a single optional integer, e.g. @iterate 3."
        )

    if not positional:
        return None
    if len(positional) > 1:
        return (
            f"@iterate at line {line_number} accepts at most one positional "
            "integer turn budget."
        )
    turns_text = positional[0]
    try:
        turns = int(turns_text.strip().strip("\"'"))
    except ValueError:
        return (
            f"@iterate at line {line_number} has invalid turns {turns_text!r}; "
            "expected an integer greater than 0."
        )
    if turns <= 0:
        return (
            f"@iterate at line {line_number} has invalid turns {turns_text!r}; "
            "expected an integer greater than 0."
        )
    return turns


def _extract_ask_prelude(
    block: str,
    ask_names: set[str],
    *,
    parent_line_number: int,
) -> tuple[IterateAskPrelude | None, str] | str:
    if not block.strip():
        return None, ""

    lines = block.splitlines()
    first = next(
        (index for index, line in enumerate(lines) if line.strip()),
        None,
    )
    if first is None:
        return None, ""

    first_match = _DIRECTIVE_RE.match(lines[first])
    if (
        first_match is None
        or _indent_width(lines[first]) != 0
        or first_match.group("name") not in ask_names
    ):
        return None, block

    ask_body, next_index = _collect_indented_block(lines, first + 1, 0)
    if not ask_body.strip():
        return (
            f"@iterate at line {parent_line_number} uses a leading @ask wrapper, "
            "but that @ask has no body to iterate."
        )

    trailing_content = [line for line in lines[next_index:] if line.strip()]
    if trailing_content:
        return (
            f"@iterate at line {parent_line_number} uses a leading @ask wrapper; "
            "that wrapper must be the only top-level child of @iterate."
        )

    prelude = IterateAskPrelude(
        name=first_match.group("name"),
        rest=first_match.group("rest").strip(),
        line_number=parent_line_number + first + 1,
    )
    return prelude, ask_body

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


def _indent(text: str, prefix: str = "  ") -> str:
    if not text:
        return prefix
    return "\n".join(f"{prefix}{line}" if line else "" for line in text.splitlines())
