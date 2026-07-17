"""Deterministic grammar-sync checker for WeaveMark.

The WeaveMark system prompt (``src/weavemark/prompts/weavemark.system.md``)
is the **source of truth** for the language. The companion deterministic
grammar (``docs/weavemark.ebnf``) MIRRORS it. When the two disagree, this
script reports actionable errors. By default the fix is to update the
grammar to match the prose, NOT the other way around.

The script extracts two things from both files:

1. The kernel grammar (the fenced ``ebnf`` block immediately following the
   "Formal Grammar (Shape Grammar — EBNF kernel)" / kernel marker). The two
   normalised production sets must be identical.

2. Every ``promplet-schema`` fenced block. Each block is parsed into a
   small struct describing the directive's header surface (positional value,
   named params, flags, body mode, LLM seam, notes). The two schema sets
   must be identical, modulo whitespace normalisation.

The script also reports (informational only) directives that have a prose
heading in the system prompt but no ``promplet-schema`` block. Authors
may opt into a schema directive-by-directive; missing schemas are NOT
errors.

Usage::

    python scripts/check_grammar_sync.py            # check the real files
    python scripts/check_grammar_sync.py --prompt P --grammar G  # check custom paths

Exit codes::

    0 -- all checks passed
    1 -- one or more checks failed

The companion test suite (``tests/test_grammar_sync.py``) exercises the
internal parser with both well-formed and malformed inputs; each negative
test doubles as documentation of a deliberate design choice.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Public lexicons (single source of truth for the script and its tests)
# ---------------------------------------------------------------------------

TYPE_LEXICON: frozenset[str] = frozenset({
    "STRING", "IDENT", "BAREWORD", "SLUG", "PATH", "PROMPLET_REF",
    "RESOURCE_REF", "URL",
    "INT", "NUMBER", "BOOL", "ANY",
})

BODY_MODE_LEXICON: frozenset[str] = frozenset({
    "none", "subspec", "free-text", "opaque",
})

# Directive names accept the same charset as the kernel grammar's IDENT,
# minus the leading sigil which we strip before validating.
DIRECTIVE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# A parameter or positional name is a plain identifier.
PARAM_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# ENUM(a|b|c) — at least one alternative, each a simple word.
ENUM_RE = re.compile(r"^ENUM\(([A-Za-z0-9_\-.]+(?:\|[A-Za-z0-9_\-.]+)*)\)$")

# dsl:<name>
DSL_BODY_MODE_RE = re.compile(r"^dsl:[a-z][a-z0-9_\-]*$")

# LLM seam slot.
SEAM_RE = re.compile(r"^<LLM:\s*[a-z][a-z0-9_\-]*>$")

# Fence extraction (regex-based; we deliberately avoid a Markdown parser).
_SCHEMA_FENCE_RE = re.compile(
    r"(?ms)^```promplet-schema[ \t]*\n(.*?)\n```[ \t]*$"
)
_KERNEL_FENCE_RE = re.compile(
    r"(?ms)^```ebnf[ \t]*\n(.*?)\n```[ \t]*$"
)
# Directive headings in prose: lines like "### `@refine ...`" or "#### `@if`".
_DIRECTIVE_HEADING_RE = re.compile(
    r"(?m)^####?\s+`(@[A-Za-z_][A-Za-z0-9_]*)\b"
)


# ---------------------------------------------------------------------------
# Schema data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SchemaField:
    """A positional or named parameter in a directive schema."""

    name: str
    type_: str
    required: bool = False
    default: str | None = None  # raw textual default, e.g. "true", "0.5", "\"strict\""

    def normalised(self) -> tuple:
        return (self.name, self.type_, self.required, self.default)


@dataclass
class Schema:
    """Parsed promplet-schema block."""

    directive: str  # without leading @, e.g. "refine"
    positional: list[SchemaField] = field(default_factory=list)
    params: list[SchemaField] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    body_mode: str = ""  # one of BODY_MODE_LEXICON or "dsl:<name>"
    seam: str | None = None
    notes: str | None = None
    source: str = ""  # file path the block came from, for diagnostics
    line: int = 0     # 1-based line number for diagnostics

    def normalised(self) -> tuple:
        """Stable comparable representation (excludes notes & source)."""
        return (
            self.directive,
            tuple(f.normalised() for f in self.positional),
            tuple(sorted(f.normalised() for f in self.params)),
            tuple(sorted(self.flags)),
            self.body_mode,
            self.seam,
        )

    def location(self) -> str:
        return f"{self.source}:{self.line}"


# ---------------------------------------------------------------------------
# Schema parsing
# ---------------------------------------------------------------------------


_FIELD_LINE_RE = re.compile(
    r"^\s*-\s+(?P<name>[^:]+?):\s+(?P<type>[A-Z_]+(?:\([^)]*\))?)"
    r"(?P<required>\s+\(required\))?"
    r"(?:\s+=\s+(?P<default>\S.*?))?\s*$"
)


def _strip_inline_comment(text: str) -> str:
    """Strip a trailing ``# ...`` comment, honouring ``#`` inside angle/quotes."""

    out_chars: list[str] = []
    in_string = False
    in_angle = 0
    for ch in text:
        if ch == '"' and not in_angle:
            in_string = not in_string
            out_chars.append(ch)
            continue
        if ch == "<" and not in_string:
            in_angle += 1
        elif ch == ">" and not in_string and in_angle > 0:
            in_angle -= 1
        if ch == "#" and not in_string and in_angle == 0:
            break
        out_chars.append(ch)
    return "".join(out_chars).rstrip()


def parse_schema(body: str, *, source: str = "", line: int = 0) -> Schema:
    """Parse a single schema block body (the text inside the fence).

    Raises :class:`ValueError` with a precise message on any parse error;
    callers convert these into reported errors.
    """

    raw_lines = body.splitlines()
    # Strip inline comments and trailing whitespace.
    cleaned = [_strip_inline_comment(ln) for ln in raw_lines]

    schema = Schema(directive="", source=source, line=line)
    current_section: str | None = None
    seen_keys: set[str] = set()

    for idx, line_text in enumerate(cleaned):
        if not line_text.strip():
            continue

        # Section / scalar key lines start at column 0 with no leading dash.
        key_match = re.match(r"^([A-Za-z][A-Za-z_-]*):\s*(.*)$", line_text)
        if key_match and not line_text.lstrip().startswith("-"):
            key = key_match.group(1).lower()
            rest = key_match.group(2).strip()

            if key in seen_keys:
                raise ValueError(f"duplicate field {key!r}")
            seen_keys.add(key)

            if key == "directive":
                if not rest.startswith("@"):
                    raise ValueError(
                        f"`directive:` value must start with '@': {rest!r}"
                    )
                name = rest[1:]
                if not DIRECTIVE_NAME_RE.match(name):
                    raise ValueError(
                        f"`directive:` name {name!r} is not a valid identifier; "
                        f"expected /^[A-Za-z_][A-Za-z0-9_]*$/"
                    )
                schema.directive = name
                current_section = None
            elif key == "body-mode":
                if not _valid_body_mode(rest):
                    raise ValueError(
                        f"`body-mode:` value {rest!r} not in lexicon; "
                        f"allowed: {sorted(BODY_MODE_LEXICON)} or dsl:<name>"
                    )
                schema.body_mode = rest
                current_section = None
            elif key == "seam":
                if not SEAM_RE.match(rest):
                    raise ValueError(
                        f"`seam:` value {rest!r} must match <LLM: kebab-name>"
                    )
                schema.seam = rest
                current_section = None
            elif key == "notes":
                schema.notes = rest
                current_section = "notes-cont"
            elif key in {"positional", "params", "flags"}:
                if rest:
                    raise ValueError(
                        f"`{key}:` must be a header line followed by `- ...` "
                        f"entries; got inline value {rest!r}"
                    )
                current_section = key
            else:
                raise ValueError(f"unknown schema field {key!r}")
            continue

        # Continuation lines (only valid inside a section).
        stripped = line_text.lstrip()
        if not stripped.startswith("-"):
            # Allow continuation of `notes:` only.
            if current_section == "notes-cont" and schema.notes is not None:
                schema.notes = (schema.notes + " " + stripped).strip()
                continue
            raise ValueError(
                f"unexpected line in schema (line {idx + 1}): {line_text!r}"
            )

        if current_section in {"positional", "params"}:
            schema_field = _parse_field_line(stripped)
            target = schema.positional if current_section == "positional" else schema.params
            target.append(schema_field)
        elif current_section == "flags":
            name = stripped.lstrip("-").strip()
            if not PARAM_NAME_RE.match(name):
                raise ValueError(f"invalid flag name {name!r}")
            schema.flags.append(name)
        else:
            raise ValueError(
                f"`- ...` entry outside of a section header (line {idx + 1})"
            )

    # ----- final validation -----------------------------------------------
    if not schema.directive:
        raise ValueError("schema is missing required `directive:` field")
    if not schema.body_mode:
        raise ValueError("schema is missing required `body-mode:` field")

    # Validate types and ENUM defaults.
    for f in [*schema.positional, *schema.params]:
        _validate_type_and_default(f, directive=schema.directive)

    # Duplicate names across all field kinds.
    names = [f.name for f in (schema.positional + schema.params)] + schema.flags
    duplicates = {n for n in names if names.count(n) > 1}
    if duplicates:
        raise ValueError(
            f"duplicate parameter/positional/flag names: {sorted(duplicates)}"
        )

    return schema


def _parse_field_line(stripped: str) -> SchemaField:
    """Parse one ``- name: TYPE [(required)] [= default]`` line."""

    m = _FIELD_LINE_RE.match(stripped)
    if not m:
        raise ValueError(
            f"invalid field line {stripped!r}; expected "
            f"`- <name>: <TYPE> [(required)] [= <default>]`"
        )
    name = m.group("name").strip()
    if not PARAM_NAME_RE.match(name):
        raise ValueError(f"invalid field name {name!r}")
    type_ = m.group("type")
    required = m.group("required") is not None
    default = m.group("default")
    if default is not None:
        default = default.strip()
    return SchemaField(name=name, type_=type_, required=required, default=default)


def _valid_body_mode(value: str) -> bool:
    if value in BODY_MODE_LEXICON:
        return True
    return bool(DSL_BODY_MODE_RE.match(value))


def _validate_type_and_default(f: SchemaField, *, directive: str) -> None:
    """Check that ``f.type_`` is in the lexicon and that any default conforms."""

    type_str = f.type_
    enum_match = ENUM_RE.match(type_str)
    if enum_match:
        alternatives = enum_match.group(1).split("|")
        if f.default is not None:
            unquoted = _unquote(f.default)
            if unquoted not in alternatives:
                raise ValueError(
                    f"{directive}.{f.name}: default {f.default!r} is not in "
                    f"ENUM({'|'.join(alternatives)})"
                )
        return

    if type_str not in TYPE_LEXICON:
        raise ValueError(
            f"{directive}.{f.name}: unknown type {type_str!r}; "
            f"allowed: {sorted(TYPE_LEXICON)} or ENUM(a|b|c)"
        )

    if f.default is None:
        return
    if type_str == "BOOL":
        if f.default not in {"true", "false"}:
            raise ValueError(
                f"{directive}.{f.name}: BOOL default must be true|false, "
                f"got {f.default!r}"
            )
    elif type_str in {"INT", "NUMBER"}:
        try:
            (int if type_str == "INT" else float)(f.default)
        except ValueError as exc:
            raise ValueError(
                f"{directive}.{f.name}: {type_str} default must be numeric, "
                f"got {f.default!r}"
            ) from exc
    # STRING, PATH, URL, etc. — defaults are free-form text; do not validate.


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


# ---------------------------------------------------------------------------
# Extraction from files
# ---------------------------------------------------------------------------


def extract_schemas(text: str, *, source: str) -> list[Schema]:
    """Find and parse every ``promplet-schema`` fenced block in ``text``."""

    schemas: list[Schema] = []
    for match in _SCHEMA_FENCE_RE.finditer(text):
        body = match.group(1)
        line = text.count("\n", 0, match.start()) + 1
        try:
            schemas.append(parse_schema(body, source=source, line=line))
        except ValueError as exc:
            raise SyncError(
                f"{source}:{line}: malformed promplet-schema block: {exc}"
            ) from exc
    return schemas


def extract_kernel_grammar(text: str, *, source: str) -> str:
    """Return the normalised body of the first ``ebnf`` fenced block.

    Normalisation: trailing whitespace stripped per line, blank lines kept.
    """

    match = _KERNEL_FENCE_RE.search(text)
    if not match:
        raise SyncError(f"{source}: no ```ebnf fenced block found")
    body = match.group(1)
    lines = [ln.rstrip() for ln in body.splitlines()]
    # Strip trailing blank lines for a stable hash.
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def extract_directive_headings(text: str) -> list[str]:
    """Return the set of ``@name`` directive headings found in the prose."""

    found: list[str] = []
    seen: set[str] = set()
    for match in _DIRECTIVE_HEADING_RE.finditer(text):
        name = match.group(1)
        if name in seen:
            continue
        seen.add(name)
        found.append(name)
    return found


# ---------------------------------------------------------------------------
# The sync check itself
# ---------------------------------------------------------------------------


class SyncError(Exception):
    """A grammar-sync violation. Message is human-actionable."""


@dataclass
class SyncReport:
    """Outcome of a sync run."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        lines: list[str] = []
        if self.errors:
            lines.append("ERRORS:")
            lines.extend(f"  - {e}" for e in self.errors)
            lines.append("")
            lines.append(
                "The system prompt (`weavemark.system.md`) is the SOURCE OF TRUTH "
                "for WeaveMark.\n"
                "The grammar (`docs/weavemark.ebnf`) MIRRORS it. Fix the grammar "
                "to match the prose,\nnot the other way around — unless the user has "
                "explicitly asked to change the prose."
            )
        if self.warnings:
            lines.append("WARNINGS:")
            lines.extend(f"  - {w}" for w in self.warnings)
        if self.info:
            lines.append("INFO:")
            lines.extend(f"  - {i}" for i in self.info)
        if not lines:
            lines.append("Grammar sync OK.")
        return "\n".join(lines)


def check_sync(
    prompt_text: str,
    grammar_text: str,
    *,
    prompt_path: str = "weavemark.system.md",
    grammar_path: str = "weavemark.ebnf",
) -> SyncReport:
    """Run the full sync check on already-loaded file contents."""

    report = SyncReport()

    # ---- kernel grammar mirror ------------------------------------------
    try:
        prompt_kernel = extract_kernel_grammar(prompt_text, source=prompt_path)
    except SyncError as exc:
        report.errors.append(str(exc))
        prompt_kernel = ""
    try:
        grammar_kernel = extract_kernel_grammar(grammar_text, source=grammar_path)
    except SyncError as exc:
        report.errors.append(str(exc))
        grammar_kernel = ""

    if prompt_kernel and grammar_kernel and prompt_kernel != grammar_kernel:
        report.errors.append(
            f"Kernel grammar drift: the ```ebnf block in {prompt_path} "
            f"does not match the ```ebnf block in {grammar_path}. "
            f"Run `diff <(extract prompt) <(extract grammar)` to inspect."
        )

    # ---- schema sets -----------------------------------------------------
    try:
        prompt_schemas = extract_schemas(prompt_text, source=prompt_path)
    except SyncError as exc:
        report.errors.append(str(exc))
        prompt_schemas = []
    try:
        grammar_schemas = extract_schemas(grammar_text, source=grammar_path)
    except SyncError as exc:
        report.errors.append(str(exc))
        grammar_schemas = []

    prompt_by_name = {s.directive: s for s in prompt_schemas}
    grammar_by_name = {s.directive: s for s in grammar_schemas}

    # Duplicate detection within each file.
    for src, schemas in (
        (prompt_path, prompt_schemas),
        (grammar_path, grammar_schemas),
    ):
        seen: dict[str, Schema] = {}
        for s in schemas:
            if s.directive in seen:
                report.errors.append(
                    f"{src}: duplicate schema for @{s.directive} "
                    f"(first at {seen[s.directive].location()}, "
                    f"again at {s.location()})"
                )
            else:
                seen[s.directive] = s

    prompt_names = set(prompt_by_name)
    grammar_names = set(grammar_by_name)

    # Orphans in the grammar (no matching prose schema).
    for name in sorted(grammar_names - prompt_names):
        s = grammar_by_name[name]
        report.errors.append(
            f"Orphan grammar schema: @{name} appears in {grammar_path} "
            f"(at {s.location()}) but has no `promplet-schema` block "
            f"in {prompt_path}. The prose is the source of truth — "
            f"remove this production from the grammar, or add a matching "
            f"schema to the prose."
        )

    # Orphans in the prompt (no matching grammar schema).
    for name in sorted(prompt_names - grammar_names):
        s = prompt_by_name[name]
        report.errors.append(
            f"Missing grammar schema: @{name} has a `promplet-schema` "
            f"block in {prompt_path} (at {s.location()}) but no matching "
            f"production in {grammar_path}. Add the schema to "
            f"{grammar_path}."
        )

    # Field-level disagreement on the intersection.
    for name in sorted(prompt_names & grammar_names):
        p = prompt_by_name[name]
        g = grammar_by_name[name]
        if p.normalised() != g.normalised():
            report.errors.append(
                f"Schema disagreement for @{name}:\n"
                f"      prose:   {_render_schema(p)}\n"
                f"      grammar: {_render_schema(g)}"
            )

    # Informational: directives in the prose without any schema.
    for heading in extract_directive_headings(prompt_text):
        name = heading.lstrip("@")
        if name not in prompt_by_name:
            report.info.append(
                f"@{name} has a prose heading in {prompt_path} but no "
                f"`promplet-schema` block. Schemas are optional; add one "
                f"when the surface is stable."
            )

    return report


def _render_schema(s: Schema) -> str:
    parts = [f"directive=@{s.directive}", f"body-mode={s.body_mode}"]
    if s.positional:
        parts.append("positional=[" + ", ".join(
            f"{f.name}:{f.type_}{'!' if f.required else ''}"
            f"{'=' + f.default if f.default else ''}"
            for f in s.positional
        ) + "]")
    if s.params:
        parts.append("params={" + ", ".join(
            f"{f.name}:{f.type_}{'!' if f.required else ''}"
            f"{'=' + f.default if f.default else ''}"
            for f in sorted(s.params, key=lambda x: x.name)
        ) + "}")
    if s.flags:
        parts.append("flags={" + ", ".join(sorted(s.flags)) + "}")
    if s.seam:
        parts.append(f"seam={s.seam}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_PROMPT = _REPO_ROOT / "src" / "weavemark" / "prompts" / "weavemark.system.md"
_DEFAULT_GRAMMAR = _REPO_ROOT / "docs" / "weavemark.ebnf"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that weavemark.system.md and docs/weavemark.ebnf agree.",
    )
    parser.add_argument(
        "--prompt", type=Path, default=_DEFAULT_PROMPT,
        help="Path to weavemark.system.md (default: repo's copy)",
    )
    parser.add_argument(
        "--grammar", type=Path, default=_DEFAULT_GRAMMAR,
        help="Path to docs/weavemark.ebnf (default: repo's copy)",
    )
    args = parser.parse_args(argv)

    if not args.prompt.is_file():
        print(f"error: prompt file not found: {args.prompt}", file=sys.stderr)
        return 2
    if not args.grammar.is_file():
        print(f"error: grammar file not found: {args.grammar}", file=sys.stderr)
        return 2

    report = check_sync(
        args.prompt.read_text(encoding="utf-8"),
        args.grammar.read_text(encoding="utf-8"),
        prompt_path=str(args.prompt),
        grammar_path=str(args.grammar),
    )
    print(report.render())
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
