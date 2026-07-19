"""Claude-style references and generic inline directive calls."""

from __future__ import annotations

import hashlib
import mimetypes
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from weavemark.compilation.args import parse_header_args
from weavemark.compilation.inline_directives import (
    FENCE_OPEN_RE,
    INLINE_NAME_RE,
    has_closing_tick_run,
    is_fence_close,
    parse_inline_directive_call,
    parse_path_candidate,
)
from weavemark.source_comments import strip_markdown_comments

_BLOCK_REFERENCE_RE = re.compile(
    r"^(?P<indent>[ \t]*)@reference(?:\s+(?P<args>.*))?$"
)
_PROMPT_RE = re.compile(r"^@prompt\s+(?P<name>[A-Za-z_][A-Za-z0-9_.-]*)")
_DIRECTIVE_LINE_RE = re.compile(
    r"^[ \t]*@(?P<name>[A-Za-z_][A-Za-z0-9_.-]*\??)(?:\s|$)"
)
_TRUE_VALUES = {"1", "on", "true", "yes"}
_FALSE_VALUES = {"0", "off", "false", "no"}
_OPAQUE_BODY_DIRECTIVES = frozenset(
    {"embed", "execute", "note", "output", "package", "tool"}
)
_MAX_REFERENCE_DEPTH = 4
_MAX_REFERENCE_CHARS = 120_000
_MAX_TOTAL_REFERENCE_CHARS = 500_000

ReferenceReader = Callable[[str, Path], tuple[str, Path] | str]


@dataclass
class ReferenceRecord:
    """One resolved source reference used during compilation."""

    id: str
    path: str
    resolved_path: Path
    content: str
    keep: bool
    line: int
    column: int
    scope: str = "default"
    parent_id: str | None = None

    @property
    def sha256(self) -> str:
        """Return the resolved reference-content hash."""

        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    @property
    def media_type(self) -> str:
        """Return a stable best-effort media type."""

        if self.resolved_path.suffix.casefold() in {".md", ".markdown"}:
            return "text/markdown"
        guessed, _ = mimetypes.guess_type(self.resolved_path.name)
        return guessed or "text/plain"

    def metadata(self) -> dict[str, object]:
        """Return public metadata without host-private absolute paths."""

        return {
            "id": self.id,
            "path": self.path,
            "keep": self.keep,
            "scope": self.scope,
            "sha256": self.sha256,
            "media_type": self.media_type,
            "source_span": {
                "line": self.line,
                "column": self.column,
            },
            **({"parent_id": self.parent_id} if self.parent_id else {}),
        }


@dataclass
class ReferenceResolutionResult:
    """Lowered source plus resolved reference resources."""

    text: str
    references: list[ReferenceRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class _ResolutionState:
    reader: ReferenceReader
    known_directives: frozenset[str]
    references: list[ReferenceRecord] = field(default_factory=list)
    by_path_scope: dict[tuple[Path, str], ReferenceRecord] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    total_chars: int = 0


def resolve_references(
    source: str,
    base_dir: Path,
    *,
    reader: ReferenceReader,
    known_directives: frozenset[str],
    enabled: bool,
) -> ReferenceResolutionResult:
    """Resolve block, inline, and Claude-style references in *source*."""

    if not enabled:
        return ReferenceResolutionResult(text=source)
    state = _ResolutionState(reader=reader, known_directives=known_directives)
    text = _resolve_source(
        source,
        base_dir.resolve(),
        state,
        depth=0,
        stack=(),
        parent_id=None,
        initial_scope="default",
    )
    return ReferenceResolutionResult(
        text=text,
        references=state.references,
        warnings=state.warnings,
        errors=state.errors,
    )


def _resolve_source(
    source: str,
    base_dir: Path,
    state: _ResolutionState,
    *,
    depth: int,
    stack: tuple[Path, ...],
    parent_id: str | None,
    initial_scope: str,
) -> str:
    if depth > _MAX_REFERENCE_DEPTH:
        chain = " -> ".join(path.name for path in stack)
        state.errors.append(
            "Reference recursion exceeds the maximum depth of "
            f"{_MAX_REFERENCE_DEPTH}: {chain}."
        )
        return source

    output: list[str] = []
    fence_marker: str | None = None
    opaque_indent: int | None = None
    current_prompt = initial_scope
    source_lines = source.splitlines(keepends=True)
    inline_ticks: int | None = None
    for line_index, line in enumerate(source_lines):
        line_number = line_index + 1
        bare_line = line.rstrip("\r\n")
        newline = line[len(bare_line) :]
        stripped_line = bare_line.lstrip()
        indent = len(bare_line) - len(stripped_line)
        if fence_marker is not None:
            output.append(line)
            if is_fence_close(line, fence_marker):
                fence_marker = None
            continue
        fence_match = FENCE_OPEN_RE.match(line) if inline_ticks is None else None
        if fence_match is not None:
            fence_marker = fence_match.group("marker")
            output.append(line)
            continue
        if opaque_indent is not None:
            if not stripped_line or indent > opaque_indent:
                output.append(line)
                continue
            opaque_indent = None
        if inline_ticks is not None:
            lowered, inline_ticks = _lower_inline_line(
                bare_line,
                base_dir,
                state,
                line_number=line_number,
                scope=current_prompt,
                depth=depth,
                stack=stack,
                parent_id=parent_id,
                inline_ticks=inline_ticks,
                future_text="".join(source_lines[line_index + 1 :]),
            )
            output.append(lowered + newline)
            continue

        if bare_line and not line.startswith((" ", "\t")):
            prompt_match = _PROMPT_RE.match(bare_line)
            if prompt_match is not None:
                current_prompt = prompt_match.group("name")
            else:
                current_prompt = initial_scope

        block_match = _BLOCK_REFERENCE_RE.match(bare_line)
        if block_match is not None:
            path, keep, parse_errors = _parse_reference_arguments(
                block_match.group("args") or ""
            )
            state.errors.extend(
                f"@reference at line {line_number}: {error}" for error in parse_errors
            )
            if path is not None and not parse_errors:
                _register_reference(
                    path,
                    keep,
                    base_dir,
                    state,
                    line=line_number,
                    column=len(block_match.group("indent")) + 1,
                    scope=current_prompt,
                    depth=depth,
                    stack=stack,
                    parent_id=parent_id,
                )
            output.append(newline)
            continue

        directive_match = _DIRECTIVE_LINE_RE.match(bare_line)
        if (
            directive_match is not None
            and directive_match.group("name") in state.known_directives
        ):
            if directive_match.group("name") in _OPAQUE_BODY_DIRECTIVES:
                opaque_indent = indent
            output.append(line)
            continue

        lowered, inline_ticks = _lower_inline_line(
            bare_line,
            base_dir,
            state,
            line_number=line_number,
            scope=current_prompt,
            depth=depth,
            stack=stack,
            parent_id=parent_id,
            inline_ticks=inline_ticks,
            future_text="".join(source_lines[line_index + 1 :]),
        )
        output.append(lowered + newline)
    return "".join(output)


def _lower_inline_line(
    line: str,
    base_dir: Path,
    state: _ResolutionState,
    *,
    line_number: int,
    scope: str,
    depth: int,
    stack: tuple[Path, ...],
    parent_id: str | None,
    inline_ticks: int | None,
    future_text: str,
) -> tuple[str, int | None]:
    output: list[str] = []
    index = 0
    while index < len(line):
        if line[index] == "`":
            end = index + 1
            while end < len(line) and line[end] == "`":
                end += 1
            ticks = end - index
            output.append(line[index:end])
            if inline_ticks is None and (
                has_closing_tick_run(line, end, ticks)
                or has_closing_tick_run(future_text, 0, ticks)
            ):
                inline_ticks = ticks
            elif ticks == inline_ticks:
                inline_ticks = None
            index = end
            continue
        if inline_ticks is not None or line[index] != "@":
            output.append(line[index])
            index += 1
            continue
        if index > 0 and (line[index - 1].isalnum() or line[index - 1] in "._+-"):
            output.append("@")
            index += 1
            continue
        if line.startswith("@@", index):
            output.append("@@")
            index += 2
            continue
        if line.startswith("@{", index):
            output.append("@")
            index += 1
            continue

        name_match = INLINE_NAME_RE.match(line, index + 1)
        if name_match is None:
            path, end = parse_path_candidate(line, index + 1)
            if path is None or not _looks_like_reference(path, base_dir):
                output.append("@")
                index += 1
                continue
            reference = _register_reference(
                path,
                True,
                base_dir,
                state,
                line=line_number,
                column=index + 1,
                scope=scope,
                depth=depth,
                stack=stack,
                parent_id=parent_id,
            )
            output.append(
                f"[Reference {reference.id}]" if reference is not None else ""
            )
            index = end
            continue
        name = name_match.group(0)
        if name_match.end() < len(line) and line[name_match.end()] == "(":
            call = parse_inline_directive_call(
                line,
                index,
                name,
                name_match.end(),
                line_number,
            )
            if isinstance(call, str):
                state.errors.append(call)
                output.append(line[index:])
                break
            if call.name != "reference":
                state.errors.append(
                    f"Directive '@{call.name}' at line {call.line}, column "
                    f"{call.column} does not support inline calls."
                )
                output.append(line[call.start : call.end])
                index = call.end
                continue
            path, keep, parse_errors = _parse_reference_arguments(call.arguments)
            state.errors.extend(
                f"@reference at line {call.line}, column {call.column}: {error}"
                for error in parse_errors
            )
            if path is None or parse_errors:
                output.append(line[call.start : call.end])
            else:
                reference = _register_reference(
                    path,
                    keep,
                    base_dir,
                    state,
                    line=call.line,
                    column=call.column,
                    scope=scope,
                    depth=depth,
                    stack=stack,
                    parent_id=parent_id,
                )
                if reference is not None and keep:
                    output.append(f"[Reference {reference.id}]")
                elif reference is not None and _surrounded_by_text(
                    line, call.start, call.end
                ):
                    state.warnings.append(
                        f"Inline @reference with keep:false at line {call.line}, "
                        f"column {call.column} contributes no visible text."
                    )
            index = call.end
            continue

        path, end = parse_path_candidate(line, index + 1)
        if path is None or not _looks_like_reference(path, base_dir):
            output.append("@")
            index += 1
            continue
        reference = _register_reference(
            path,
            True,
            base_dir,
            state,
            line=line_number,
            column=index + 1,
            scope=scope,
            depth=depth,
            stack=stack,
            parent_id=parent_id,
        )
        output.append(f"[Reference {reference.id}]" if reference is not None else "")
        index = end
    return "".join(output), inline_ticks


def _register_reference(
    path: str,
    keep: bool,
    base_dir: Path,
    state: _ResolutionState,
    *,
    line: int,
    column: int,
    scope: str,
    depth: int,
    stack: tuple[Path, ...],
    parent_id: str | None,
) -> ReferenceRecord | None:
    loaded = state.reader(path, base_dir)
    if isinstance(loaded, str):
        state.errors.append(loaded)
        return None
    content, resolved_path = loaded
    resolved_path = resolved_path.resolve()
    if resolved_path in stack:
        chain = " -> ".join(
            [*(candidate.name for candidate in stack), resolved_path.name]
        )
        state.errors.append(f"Cyclic @reference detected: {chain}.")
        return None
    path_scope = (resolved_path, scope)
    existing = state.by_path_scope.get(path_scope)
    if existing is not None:
        existing.keep = existing.keep or keep
        return existing
    if len(content) > _MAX_REFERENCE_CHARS:
        state.errors.append(
            f"Reference {path!r} contains {len(content)} characters; the maximum is "
            f"{_MAX_REFERENCE_CHARS}."
        )
        return None
    state.total_chars += len(content)
    if state.total_chars > _MAX_TOTAL_REFERENCE_CHARS:
        state.errors.append(
            "Referenced source content exceeds the aggregate "
            f"{_MAX_TOTAL_REFERENCE_CHARS}-character limit."
        )
        return None

    reference = ReferenceRecord(
        id=f"R{len(state.references) + 1}",
        path=path,
        resolved_path=resolved_path,
        content="",
        keep=keep,
        line=line,
        column=column,
        scope=scope,
        parent_id=parent_id,
    )
    state.references.append(reference)
    state.by_path_scope[path_scope] = reference
    stripped = strip_markdown_comments(
        content,
        source_name=f"referenced source {path}",
    )
    state.errors.extend(stripped.errors)
    reference.content = _resolve_source(
        stripped.text,
        resolved_path.parent,
        state,
        depth=depth + 1,
        stack=(*stack, resolved_path),
        parent_id=reference.id,
        initial_scope=scope,
    ).rstrip()
    return reference


def _parse_reference_arguments(arguments: str) -> tuple[str | None, bool, list[str]]:
    parsed = parse_header_args(arguments)
    errors = list(parsed.errors)
    unknown = sorted(set(parsed.options) - {"keep"})
    if unknown:
        errors.append(
            "@reference received unsupported parameter(s): " + ", ".join(unknown) + "."
        )
    if len(parsed.positional) != 1:
        errors.append("@reference requires exactly one file path.")
        path = None
    else:
        path = parsed.positional[0]
    keep_text = parsed.options.get("keep", "true").casefold()
    if keep_text in _TRUE_VALUES:
        keep = True
    elif keep_text in _FALSE_VALUES:
        keep = False
    else:
        errors.append("@reference keep must be true or false.")
        keep = True
    return path, keep, errors


def _looks_like_reference(candidate: str, base_dir: Path) -> bool:
    if candidate.startswith(("./", "../", "~/", "/")) or "/" in candidate:
        return True
    if "." in candidate:
        return True
    path = Path(candidate).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.is_file()


def _surrounded_by_text(line: str, start: int, end: int) -> bool:
    return bool(line[:start].strip() or line[end:].strip())


__all__ = [
    "ReferenceRecord",
    "ReferenceResolutionResult",
    "resolve_references",
]
