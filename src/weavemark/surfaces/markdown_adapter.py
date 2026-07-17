"""Markdown surface adapter for WeaveMark.

Activated when the spec declares ``surface: markdown``::

    @promplet version: 0.8 surface: markdown

Two sugar forms are lowered to canonical WeaveMark:

1. **Directive headings** — a Markdown heading whose heading text begins with
   a WeaveMark directive name::

       ## @prompt extract role: user

       Extract claims from @{passage}.

       ## @prompt critique

       Critique each claim.

   Lowers to::

       @prompt extract role: user
         Extract claims from @{passage}.

       @prompt critique
         Critique each claim.

2. **WeaveMark callouts** — a Markdown blockquote beginning with
   ``[!PROMPLET ...]``::

       > [!PROMPLET style]
       > Crisp, direct, professional.

   Lowers to::

       @style "Crisp, direct, professional."

Everything else is preserved verbatim.  The lowering pass is purely textual
and deterministic; it does not call the LLM.

Implementation notes
--------------------
* Fenced code blocks (`` ``` `` and ``~~~``) are treated as opaque — directive
  headings and callouts inside fences are ignored and passed through verbatim.
  This is essential so that example code in the prompt body is not accidentally
  consumed.
* The ``@promplet`` pragma line itself is always passed through unchanged.
  The pragma is written in canonical syntax to make the surface declaration
  itself bootstrappable without the adapter.
* Indentation used in lowered bodies is 2 spaces, consistent with existing
  WeaveMark conventions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from weavemark.surfaces.base import SurfaceLoweringResult

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# ATX heading: capture level (number of #) and heading text
_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+)$")

# A heading whose text begins with a WeaveMark directive
_DIRECTIVE_HEADING_RE = re.compile(
    r"^#{1,6}\s+@(?P<directive>[A-Za-z_][\w.-]*)(?P<rest>[^\n]*)$"
)

# Callout: first line of a blockquote must be exactly "[!PROMPLET ...]"
_CALLOUT_OPEN_RE = re.compile(r"^>\s*\[!PROMPLET(?:\s+(?P<header>[^\]]*))?\]\s*$")

# Subsequent blockquote lines
_BLOCKQUOTE_LINE_RE = re.compile(r"^>\s?(?P<content>.*)$")

# Fenced code block markers
_FENCE_RE = re.compile(r"^(?:```|~~~)")

_IDENT_RE = re.compile(r"^[A-Za-z_][\w.-]*$")

_BODY_INDENT = "  "  # 2-space indent for lowered bodies
_CALLOUT_BODY_AS_POSITIONAL = {"normalize", "revise", "style"}


# ---------------------------------------------------------------------------
# Lowering helpers
# ---------------------------------------------------------------------------


def _is_directive_heading(line: str) -> re.Match[str] | None:
    return _DIRECTIVE_HEADING_RE.match(line)


def _heading_level(line: str) -> int | None:
    m = _HEADING_RE.match(line)
    return len(m.group("hashes")) if m else None


def _indent_body(body_lines: list[str]) -> list[str]:
    """Indent a list of body lines by _BODY_INDENT, preserving blank lines."""
    result: list[str] = []
    for line in body_lines:
        if line.strip():
            result.append(_BODY_INDENT + line)
        else:
            result.append("")
    # Strip trailing blank lines from the body
    while result and not result[-1].strip():
        result.pop()
    return result


def _lower_directive_heading(
    directive: str,
    rest: str,
    body_lines: list[str],
) -> list[str]:
    """Produce canonical WeaveMark lines for one directive heading + body."""
    header = f"@{directive}{rest}"
    out: list[str] = [header]
    indented = _indent_body(body_lines)
    if indented:
        out.extend(indented)
    return out


def _lower_callout(header: str, body_lines: list[str]) -> list[str]:
    """Produce canonical WeaveMark lines for one callout + body."""
    header = (header or "").strip()
    if not header:
        return []  # empty callout header — silently drop
    header_parts = header.split(maxsplit=1)
    if (
        len(header_parts) == 1
        and header_parts[0] in _CALLOUT_BODY_AS_POSITIONAL
        and body_lines
    ):
        positional = " ".join(line.strip() for line in body_lines if line.strip())
        return [f"@{header_parts[0]} {_quote_header_string(positional)}"]
    directive_line = f"@{header}"
    out: list[str] = [directive_line]
    indented = _indent_body(body_lines)
    if indented:
        out.extend(indented)
    return out


def _quote_header_string(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


# ---------------------------------------------------------------------------
# Tokenizer — splits raw source into segments
# ---------------------------------------------------------------------------


@dataclass
class _Segment:
    kind: str  # "fence", "directive_heading", "callout", "plain"
    lines: list[str] = field(default_factory=list)
    # For directive_heading / callout
    directive: str = ""
    rest: str = ""
    header: str = ""  # callout header
    body: list[str] = field(default_factory=list)
    # heading level, for directive headings
    level: int = 0


def _tokenize(lines: list[str]) -> list[_Segment]:
    """Split source lines into segments for lowering."""
    segments: list[_Segment] = []
    i = 0
    in_fence = False
    fence_marker = ""

    while i < len(lines):
        line = lines[i]

        # ── Fenced block tracking ─────────────────────────────────────────
        if _FENCE_RE.match(line.rstrip()):
            if not in_fence:
                in_fence = True
                fence_marker = line.rstrip()[:3]
                seg = _Segment(kind="fence", lines=[line])
                i += 1
                while i < len(lines):
                    seg.lines.append(lines[i])
                    if lines[i].rstrip().startswith(fence_marker):
                        i += 1
                        break
                    i += 1
                in_fence = False
                segments.append(seg)
                continue
            # Should not happen in well-formed Markdown, but handle gracefully
            seg = _Segment(kind="plain", lines=[line])
            segments.append(seg)
            i += 1
            continue

        # ── Callout: blockquote starting with [!PROMPLET] ──────────────
        callout_m = _CALLOUT_OPEN_RE.match(line)
        if callout_m:
            header = callout_m.group("header") or ""
            body_lines: list[str] = []
            i += 1
            while i < len(lines):
                bq_m = _BLOCKQUOTE_LINE_RE.match(lines[i])
                if bq_m:
                    body_lines.append(bq_m.group("content"))
                    i += 1
                else:
                    break
            seg = _Segment(
                kind="callout",
                header=header.strip(),
                body=body_lines,
            )
            segments.append(seg)
            continue

        # ── Directive heading ─────────────────────────────────────────────
        dh_m = _is_directive_heading(line)
        if dh_m:
            directive = dh_m.group("directive")
            rest = dh_m.group("rest")  # may include " role: user" etc.
            level = len(_HEADING_RE.match(line).group("hashes"))  # type: ignore[union-attr]
            body_lines = []
            i += 1
            while i < len(lines):
                candidate = lines[i]
                # Stop if we hit a heading at same or higher level
                lvl = _heading_level(candidate)
                if lvl is not None and lvl <= level:
                    break
                # Stop at a fence that follows immediately (rare but safe)
                body_lines.append(candidate)
                i += 1
            # Trim trailing blank lines from body
            while body_lines and not body_lines[-1].strip():
                body_lines.pop()
            seg = _Segment(
                kind="directive_heading",
                directive=directive,
                rest=rest,
                body=body_lines,
                level=level,
            )
            segments.append(seg)
            continue

        # ── Plain line ────────────────────────────────────────────────────
        if segments and segments[-1].kind == "plain":
            segments[-1].lines.append(line)
        else:
            segments.append(_Segment(kind="plain", lines=[line]))
        i += 1

    return segments


# ---------------------------------------------------------------------------
# Main lowering logic
# ---------------------------------------------------------------------------


def _lower_segments(segments: list[_Segment]) -> tuple[list[str], list[str]]:
    """Convert segments to canonical WeaveMark lines.

    Returns ``(output_lines, errors)``.
    """
    out: list[str] = []
    errors: list[str] = []

    for seg in segments:
        if seg.kind in ("plain", "fence"):
            out.extend(seg.lines)

        elif seg.kind == "directive_heading":
            # Blank line before directive heading body (if previous output is not blank)
            if out and out[-1].strip():
                out.append("")
            lowered = _lower_directive_heading(seg.directive, seg.rest, seg.body)
            out.extend(lowered)
            out.append("")  # blank line after

        elif seg.kind == "callout":
            header = seg.header
            if not header:
                errors.append(
                    "Empty [!PROMPLET] callout header — a directive name is required."
                )
                continue
            # Blank line before if needed
            if out and out[-1].strip():
                out.append("")
            lowered = _lower_callout(header, seg.body)
            if lowered:
                out.extend(lowered)
                out.append("")

    # Collapse consecutive blank lines (more than 2 → 1)
    cleaned: list[str] = []
    blank_run = 0
    for line in out:
        if not line.strip():
            blank_run += 1
            if blank_run <= 1:
                cleaned.append(line)
        else:
            blank_run = 0
            cleaned.append(line)

    return cleaned, errors


# ---------------------------------------------------------------------------
# Adapter class
# ---------------------------------------------------------------------------


class MarkdownSurfaceAdapter:
    """Markdown surface adapter.

    Lowers directive headings and WeaveMark callouts to canonical
    ``@directive`` form.  All other Markdown content is preserved verbatim.
    """

    @property
    def name(self) -> str:
        return "markdown"

    def lower(self, spec_text: str) -> SurfaceLoweringResult:
        lines = spec_text.splitlines()
        segments = _tokenize(lines)
        output_lines, errors = _lower_segments(segments)
        canonical = "\n".join(output_lines)
        # Ensure a single trailing newline
        canonical = canonical.rstrip("\n") + "\n"
        return SurfaceLoweringResult(
            text=canonical,
            surface="markdown",
            warnings=[],
            errors=errors,
        )
