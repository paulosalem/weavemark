"""Tests for the deterministic grammar-sync checker.

This suite has two complementary purposes:

1. **Regression guard.** :func:`test_real_repo_is_in_sync` verifies that the
   checked-in ``weavemark.system.md`` and ``docs/weavemark.ebnf`` agree.
   This is the gate that protects the source-of-truth invariant in CI.

2. **Design documentation.** Every negative test (``test_rejects_*``,
   ``test_detects_*``) records a deliberate language choice. When you read
   the test, you also read the rule. Examples:

   - ``test_rejects_unknown_type`` documents that the type lexicon is
     closed.
   - ``test_rejects_enum_default_not_in_alternatives`` documents that
     ``ENUM`` defaults must be one of the listed values.
   - ``test_detects_orphan_grammar_schema`` documents that the prompt is
     the source of truth and that orphan productions in the grammar are
     a hard error.

If you intentionally relax one of these constraints, also update the
test that documents the prior constraint — the diff makes the design shift
explicit and reviewable.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from check_grammar_sync import (  # noqa: E402  (sys.path tweak above)
    BODY_MODE_LEXICON,
    TYPE_LEXICON,
    Schema,
    SchemaField,
    SyncError,
    check_sync,
    extract_directive_headings,
    extract_kernel_grammar,
    extract_schemas,
    main,
    parse_schema,
)

# ---------------------------------------------------------------------------
# Reusable fixtures
# ---------------------------------------------------------------------------

WELL_FORMED_PROMPT = textwrap.dedent(
    """\
    # WeaveMark — toy

    ### Formal Grammar (Shape Grammar — EBNF kernel)

    ```ebnf
    spec ::= line*
    line ::= directive_line | content_line
    ```

    ### `@sample <file>`

    ```promplet-schema
    directive:  @sample
    positional:
      - path: PATH (required)
    params:
      - mingle: BOOL = true
    body-mode:  none
    notes:      Loads <path> as a promplet and merges with S.
    ```

    ### `@if`

    ```promplet-schema
    directive:  @if
    body-mode:  subspec
    seam:       <LLM: if-condition>
    ```
    """
)

WELL_FORMED_GRAMMAR = textwrap.dedent(
    """\
    # WeaveMark grammar mirror

    ## Kernel grammar

    ```ebnf
    spec ::= line*
    line ::= directive_line | content_line
    ```

    ## Schemas

    ```promplet-schema
    directive:  @sample
    positional:
      - path: PATH (required)
    params:
      - mingle: BOOL = true
    body-mode:  none
    ```

    ```promplet-schema
    directive:  @if
    body-mode:  subspec
    seam:       <LLM: if-condition>
    ```
    """
)


def _schema_block(body: str) -> str:
    return f"```promplet-schema\n{body}\n```"


def _toy_prompt(*schemas: str) -> str:
    """Wrap one or more schema blocks in a minimal valid prompt."""
    return (
        "# WeaveMark\n\n"
        "### Formal Grammar (Shape Grammar — EBNF kernel)\n\n"
        "```ebnf\nspec ::= line*\n```\n\n"
        + "\n\n".join(schemas)
        + "\n"
    )


def _toy_grammar(*schemas: str) -> str:
    """Mirror of ``_toy_prompt`` for the grammar file."""
    return (
        "# Grammar mirror\n\n"
        "## Kernel grammar\n\n"
        "```ebnf\nspec ::= line*\n```\n\n"
        + "\n\n".join(schemas)
        + "\n"
    )


# ---------------------------------------------------------------------------
# Regression guard: the real repo is in sync
# ---------------------------------------------------------------------------


def test_real_repo_is_in_sync() -> None:
    """The shipped prompt and grammar agree.

    This is the contract that the rest of this file's negative tests
    protect. If this fails, run ``python scripts/check_grammar_sync.py``
    and fix the grammar (NOT the prose) until it passes.
    """
    prompt = (
        _REPO_ROOT / "src" / "weavemark" / "prompts" / "weavemark.system.md"
    ).read_text(encoding="utf-8")
    grammar = (_REPO_ROOT / "docs" / "weavemark.ebnf").read_text(encoding="utf-8")
    report = check_sync(prompt, grammar)
    assert report.ok, report.render()


def test_main_returns_zero_on_real_repo() -> None:
    """``python scripts/check_grammar_sync.py`` (no args) exits 0."""
    assert main([]) == 0


# ---------------------------------------------------------------------------
# Lexicons are closed (design choices)
# ---------------------------------------------------------------------------


def test_type_lexicon_is_closed() -> None:
    """The type lexicon enumerates exactly the supported primitive types.

    Closed lexicons keep specs portable across implementations (LLM and
    structural validator both know the full set).
    """
    assert TYPE_LEXICON == frozenset({
        "STRING", "IDENT", "BAREWORD", "SLUG", "PATH", "PROMPLET_REF",
        "RESOURCE_REF", "URL",
        "INT", "NUMBER", "BOOL", "ANY",
    })


def test_body_mode_lexicon_is_closed() -> None:
    """Body modes are closed except for the open extension ``dsl:<name>``."""
    assert BODY_MODE_LEXICON == frozenset({
        "none", "subspec", "free-text", "opaque",
    })


# ---------------------------------------------------------------------------
# Positive parses
# ---------------------------------------------------------------------------


def test_parses_minimal_schema() -> None:
    """A schema with only the two required fields is valid."""
    schema = parse_schema("directive:  @note\nbody-mode:  opaque")
    assert schema.directive == "note"
    assert schema.body_mode == "opaque"
    assert schema.positional == []
    assert schema.params == []
    assert schema.flags == []


def test_parses_full_schema() -> None:
    """All five field kinds (positional, params, flags, seam, notes) parse."""
    schema = parse_schema(textwrap.dedent("""\
        directive:  @example_dir
        positional:
          - first: STRING (required)
        params:
          - count: INT = 2
          - mode: ENUM(a|b|c) = a
        flags:
          - quiet
        body-mode:  free-text
        seam:       <LLM: example-spec>
        notes:      An example with everything.
        """))
    assert schema.directive == "example_dir"
    assert schema.positional == [
        SchemaField(name="first", type_="STRING", required=True),
    ]
    assert {f.name for f in schema.params} == {"count", "mode"}
    assert schema.flags == ["quiet"]
    assert schema.body_mode == "free-text"
    assert schema.seam == "<LLM: example-spec>"
    assert schema.notes == "An example with everything."


def test_parses_dsl_body_mode() -> None:
    """``body-mode: dsl:<name>`` is the open-ended body kind."""
    schema = parse_schema(
        "directive:  @custom\nbody-mode:  dsl:custom-syntax"
    )
    assert schema.body_mode == "dsl:custom-syntax"


def test_inline_comments_are_stripped() -> None:
    """``# comment`` to the right of a value is ignored."""
    schema = parse_schema(textwrap.dedent("""\
        directive:  @x   # leading comment
        body-mode:  none # trailing comment
        """))
    assert schema.directive == "x"
    assert schema.body_mode == "none"


def test_hashes_inside_angle_seams_are_not_comments() -> None:
    """A ``#`` inside an ``<LLM: ...>`` value isn't a comment delimiter."""
    schema = parse_schema(textwrap.dedent("""\
        directive:  @x
        body-mode:  free-text
        seam:       <LLM: with-hash>
        """))
    assert schema.seam == "<LLM: with-hash>"


# ---------------------------------------------------------------------------
# Negative parses — each documents a deliberate constraint
# ---------------------------------------------------------------------------


def test_rejects_missing_directive() -> None:
    """`directive:` is required — the schema must declare which directive it describes."""
    with pytest.raises(ValueError, match="missing required `directive:`"):
        parse_schema("body-mode:  none")


def test_rejects_missing_body_mode() -> None:
    """`body-mode:` is required — every directive's body shape is contractual."""
    with pytest.raises(ValueError, match="missing required `body-mode:`"):
        parse_schema("directive:  @x")


def test_rejects_directive_value_without_at_sign() -> None:
    """`directive:` values MUST start with ``@`` to match the source syntax."""
    with pytest.raises(ValueError, match="must start with '@'"):
        parse_schema("directive:  refine\nbody-mode:  none")


def test_rejects_invalid_directive_name() -> None:
    """Directive names follow the IDENT charset (letters, digits, underscore)."""
    with pytest.raises(ValueError, match="not a valid identifier"):
        parse_schema("directive:  @bad-name!\nbody-mode:  none")


def test_rejects_unknown_type() -> None:
    """The type lexicon is closed (see ``test_type_lexicon_is_closed``)."""
    with pytest.raises(ValueError, match="unknown type 'STRINGY'"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            params:
              - field: STRINGY
            body-mode:  none
            """))


def test_rejects_unknown_body_mode() -> None:
    """Body modes outside the closed lexicon are rejected (except ``dsl:<name>``)."""
    with pytest.raises(ValueError, match="body-mode.*'mystery'"):
        parse_schema("directive:  @x\nbody-mode:  mystery")


def test_rejects_malformed_dsl_body_mode() -> None:
    """``dsl:<name>`` must use lowercase-kebab; CamelCase is rejected."""
    with pytest.raises(ValueError, match="body-mode"):
        parse_schema("directive:  @x\nbody-mode:  dsl:CamelCase")


def test_rejects_enum_default_not_in_alternatives() -> None:
    """``ENUM`` defaults MUST be one of the listed values."""
    with pytest.raises(ValueError, match="default 'maybe' is not in ENUM"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            params:
              - mode: ENUM(yes|no) = maybe
            body-mode:  none
            """))


def test_rejects_bool_default_not_true_or_false() -> None:
    """``BOOL`` defaults MUST be literal ``true`` or ``false``."""
    with pytest.raises(ValueError, match="BOOL default"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            params:
              - flag: BOOL = yes
            body-mode:  none
            """))


def test_rejects_int_default_non_numeric() -> None:
    """``INT`` defaults MUST parse as an integer."""
    with pytest.raises(ValueError, match="INT default"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            params:
              - count: INT = many
            body-mode:  none
            """))


def test_rejects_duplicate_field() -> None:
    """The schema parser rejects two ``body-mode:`` lines (or any duplicate scalar)."""
    with pytest.raises(ValueError, match="duplicate field 'body-mode'"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            body-mode:  none
            body-mode:  subspec
            """))


def test_rejects_unknown_field() -> None:
    """Only the canonical fields are allowed — typos and inventions are rejected."""
    with pytest.raises(ValueError, match="unknown schema field 'mode-body'"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            mode-body:  none
            """))


def test_rejects_duplicate_param_name() -> None:
    """A name can appear once across positional + params + flags."""
    with pytest.raises(ValueError, match="duplicate parameter"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            positional:
              - foo: STRING
            params:
              - foo: BOOL = true
            body-mode:  none
            """))


def test_rejects_malformed_field_line() -> None:
    """``- name: TYPE`` is the only field-line shape; freeform text is rejected."""
    with pytest.raises(ValueError, match="invalid field line"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            params:
              - just a description
            body-mode:  none
            """))


def test_rejects_malformed_seam() -> None:
    """Seams MUST take the shape ``<LLM: kebab-name>``."""
    with pytest.raises(ValueError, match="seam"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            body-mode:  free-text
            seam:       LLM: missing-angle-brackets
            """))


def test_rejects_inline_value_on_list_header() -> None:
    """`positional:` / `params:` / `flags:` are header-only; values come as ``- ...`` lines."""
    with pytest.raises(ValueError, match="must be a header line"):
        parse_schema(textwrap.dedent("""\
            directive:  @x
            params: inline value
            body-mode:  none
            """))


# ---------------------------------------------------------------------------
# Sync-level checks
# ---------------------------------------------------------------------------


def test_sync_passes_on_minimal_pair() -> None:
    """The smallest possible matched prompt + grammar passes the sync check."""
    report = check_sync(WELL_FORMED_PROMPT, WELL_FORMED_GRAMMAR)
    assert report.ok, report.render()


def test_detects_kernel_drift() -> None:
    """If the kernel grammar block differs between files, that's an error."""
    bad_grammar = WELL_FORMED_GRAMMAR.replace(
        "spec ::= line*", "spec ::= line+"
    )
    report = check_sync(WELL_FORMED_PROMPT, bad_grammar)
    assert not report.ok
    assert any("Kernel grammar drift" in e for e in report.errors)


def test_detects_orphan_grammar_schema() -> None:
    """A schema in the grammar with no matching prose schema is an error.

    Documents the source-of-truth rule: the prompt drives, not the grammar.
    """
    prompt = _toy_prompt(_schema_block(
        "directive:  @real\nbody-mode:  none"
    ))
    grammar = _toy_grammar(
        _schema_block("directive:  @real\nbody-mode:  none"),
        _schema_block("directive:  @phantom\nbody-mode:  none"),
    )
    report = check_sync(prompt, grammar)
    assert not report.ok
    assert any("Orphan grammar schema: @phantom" in e for e in report.errors)


def test_detects_missing_grammar_schema() -> None:
    """A schema in the prompt with no matching grammar schema is an error."""
    prompt = _toy_prompt(
        _schema_block("directive:  @here\nbody-mode:  none"),
        _schema_block("directive:  @ungrammared\nbody-mode:  none"),
    )
    grammar = _toy_grammar(_schema_block(
        "directive:  @here\nbody-mode:  none"
    ))
    report = check_sync(prompt, grammar)
    assert not report.ok
    assert any("Missing grammar schema: @ungrammared" in e for e in report.errors)


def test_detects_field_level_disagreement() -> None:
    """Same directive, different params → reported with side-by-side render."""
    prompt = _toy_prompt(_schema_block(textwrap.dedent("""\
        directive:  @x
        params:
          - mode: ENUM(a|b) = a
        body-mode:  none
        """).strip()))
    grammar = _toy_grammar(_schema_block(textwrap.dedent("""\
        directive:  @x
        params:
          - mode: ENUM(a|b) = b
        body-mode:  none
        """).strip()))
    report = check_sync(prompt, grammar)
    assert not report.ok
    assert any("Schema disagreement for @x" in e for e in report.errors)


def test_detects_body_mode_disagreement() -> None:
    """Disagreement on body mode alone is a hard error.

    Body mode determines whether the body is opaque, free-text, etc., which
    in turn determines whether ``@@`` escaping and ``@{var}`` substitution
    apply. It is contractual.
    """
    prompt = _toy_prompt(_schema_block(
        "directive:  @x\nbody-mode:  subspec"
    ))
    grammar = _toy_grammar(_schema_block(
        "directive:  @x\nbody-mode:  free-text"
    ))
    report = check_sync(prompt, grammar)
    assert not report.ok
    assert any("Schema disagreement for @x" in e for e in report.errors)


def test_param_order_is_insensitive() -> None:
    """Named ``params`` are an unordered set; reordering does NOT trigger drift.

    (Positional values, by contrast, are order-sensitive — they map to
    positional arguments in the directive header.)
    """
    prompt = _toy_prompt(_schema_block(textwrap.dedent("""\
        directive:  @x
        params:
          - a: STRING
          - b: STRING
        body-mode:  none
        """).strip()))
    grammar = _toy_grammar(_schema_block(textwrap.dedent("""\
        directive:  @x
        params:
          - b: STRING
          - a: STRING
        body-mode:  none
        """).strip()))
    report = check_sync(prompt, grammar)
    assert report.ok, report.render()


def test_positional_order_is_sensitive() -> None:
    """Reordering ``positional:`` entries IS drift (positions matter)."""
    prompt = _toy_prompt(_schema_block(textwrap.dedent("""\
        directive:  @x
        positional:
          - first: STRING
          - second: STRING
        body-mode:  none
        """).strip()))
    grammar = _toy_grammar(_schema_block(textwrap.dedent("""\
        directive:  @x
        positional:
          - second: STRING
          - first: STRING
        body-mode:  none
        """).strip()))
    report = check_sync(prompt, grammar)
    assert not report.ok


def test_notes_are_not_compared() -> None:
    """``notes:`` content may differ — it's informational, not contractual."""
    prompt = _toy_prompt(_schema_block(
        "directive:  @x\nbody-mode:  none\nnotes:      Short prose note."
    ))
    grammar = _toy_grammar(_schema_block(
        "directive:  @x\nbody-mode:  none\nnotes:      Much longer engineering note with more context."
    ))
    report = check_sync(prompt, grammar)
    assert report.ok, report.render()


def test_detects_duplicate_schema_within_a_file() -> None:
    """A directive may only have one schema per file."""
    prompt = _toy_prompt(
        _schema_block("directive:  @x\nbody-mode:  none"),
        _schema_block("directive:  @x\nbody-mode:  subspec"),
    )
    grammar = _toy_grammar(_schema_block(
        "directive:  @x\nbody-mode:  none"
    ))
    report = check_sync(prompt, grammar)
    assert not report.ok
    assert any("duplicate schema for @x" in e for e in report.errors)


def test_directive_without_schema_is_informational_not_error() -> None:
    """A directive that has a prose heading but no schema is fine.

    Schemas are opt-in per directive — authors may leave a directive
    schemaless while its surface is still in flux. The sync script
    surfaces these as INFO so they're visible but not blocking.
    """
    prompt = (
        "# WeaveMark\n\n"
        "### Formal Grammar (Shape Grammar — EBNF kernel)\n\n"
        "```ebnf\nspec ::= line*\n```\n\n"
        "### `@no_schema_yet`\n\n"
        "Prose only — no schema block.\n"
    )
    grammar = "## Grammar\n\n```ebnf\nspec ::= line*\n```\n"
    report = check_sync(prompt, grammar)
    assert report.ok
    assert any("@no_schema_yet" in i for i in report.info)


def test_propagates_malformed_block_with_location() -> None:
    """A malformed schema block is reported as an error with its source location."""
    prompt = _toy_prompt(_schema_block(
        "directive:  refine\nbody-mode:  none"  # missing @ sign
    ))
    grammar = _toy_grammar()
    report = check_sync(prompt, grammar)
    assert not report.ok
    assert any(
        "malformed promplet-schema" in e and "must start with '@'" in e
        for e in report.errors
    ), report.render()


# ---------------------------------------------------------------------------
# Auxiliary extractors
# ---------------------------------------------------------------------------


def test_extract_kernel_grammar_strips_trailing_blank_lines() -> None:
    """Trailing blank lines in the ``ebnf`` block must NOT cause drift."""
    text_a = "```ebnf\nspec ::= x\n\n\n```"
    text_b = "```ebnf\nspec ::= x\n```"
    assert extract_kernel_grammar(text_a, source="a") == extract_kernel_grammar(
        text_b, source="b"
    )


def test_extract_directive_headings_dedupes() -> None:
    """A directive name appears once even if its heading appears multiple times."""
    text = "### `@a`\n#### `@b`\n### `@a more`\n"
    assert extract_directive_headings(text) == ["@a", "@b"]


def test_extract_schemas_locates_each_block() -> None:
    """Each extracted schema knows its 1-based line number for diagnostics."""
    text = "preamble\n\n" + _schema_block("directive:  @x\nbody-mode:  none")
    schemas = extract_schemas(text, source="<test>")
    assert len(schemas) == 1
    assert schemas[0].directive == "x"
    # The fence opener is on line 3, so the line we report is around there.
    assert schemas[0].line >= 3
