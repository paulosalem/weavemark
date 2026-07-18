"""Lexical handling for Markdown-native WeaveMark comments."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<marker>`{3,}|~{3,})")


@dataclass
class CommentStrippingResult:
    """WeaveMark source with non-semantic HTML comments removed."""

    text: str
    errors: list[str] = field(default_factory=list)


def _is_fence_close(line: str, marker: str) -> bool:
    fence_char = re.escape(marker[0])
    return (
        re.fullmatch(
            rf" {{0,3}}{fence_char}{{{len(marker)},}}[ \t]*(?:\r?\n)?",
            line,
        )
        is not None
    )


def _has_closing_tick_run(line: str, start: int, tick_count: int) -> bool:
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


def strip_markdown_comments(
    source: str,
    *,
    source_name: str = "WeaveMark source",
) -> CommentStrippingResult:
    """Strip complete ``<!-- ... -->`` comments outside code spans and fences."""

    output: list[str] = []
    fence_marker: str | None = None
    in_comment = False
    comment_line = 0
    comment_has_newline = False
    comment_left_is_text = False

    for line_number, line in enumerate(source.splitlines(keepends=True), start=1):
        if fence_marker is not None:
            output.append(line)
            if _is_fence_close(line, fence_marker):
                fence_marker = None
            continue

        if not in_comment:
            fence_match = _FENCE_OPEN_RE.match(line)
            if fence_match is not None:
                fence_marker = fence_match.group("marker")
                output.append(line)
                continue

        inline_code_ticks: int | None = None
        index = 0
        while index < len(line):
            if in_comment:
                if line.startswith("-->", index):
                    in_comment = False
                    index += 3
                    if (
                        comment_left_is_text
                        and not comment_has_newline
                        and index < len(line)
                        and not line[index].isspace()
                    ):
                        output.append(" ")
                    continue
                if line[index] in "\r\n":
                    output.append(line[index])
                    comment_has_newline = True
                index += 1
                continue

            if line[index] == "`":
                end = index + 1
                while end < len(line) and line[end] == "`":
                    end += 1
                tick_count = end - index
                output.append(line[index:end])
                if inline_code_ticks is None and _has_closing_tick_run(
                    line, end, tick_count
                ):
                    inline_code_ticks = tick_count
                elif tick_count == inline_code_ticks:
                    inline_code_ticks = None
                index = end
                continue

            if inline_code_ticks is None and line.startswith("<!--", index):
                in_comment = True
                comment_line = line_number
                comment_has_newline = False
                comment_left_is_text = bool(output and not output[-1][-1:].isspace())
                index += 4
                continue

            output.append(line[index])
            index += 1

    errors: list[str] = []
    if in_comment:
        errors.append(
            f"Unterminated HTML comment in {source_name} starting at line "
            f"{comment_line}."
        )
    return CommentStrippingResult(text="".join(output), errors=errors)


__all__ = ["CommentStrippingResult", "strip_markdown_comments"]
