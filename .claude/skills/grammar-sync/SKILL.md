---
name: grammar-sync
description: |
  Keep the WeaveMark language definition (`weavemark.system.md`) in sync
  with its deterministic mirror (`docs/weavemark.ebnf`). Invoke this skill
  whenever you edit either file, add or modify a directive, change a
  parameter schema, or touch the kernel grammar block.
when_to_use: |
  - After editing `src/weavemark/prompts/weavemark.system.md`
  - After editing `docs/weavemark.ebnf`
  - Before opening a PR that touches the language surface
  - When CI reports a failure from `tests/test_grammar_sync.py`
---

# grammar-sync

WeaveMark's language is defined twice on purpose:

1. **`src/weavemark/prompts/weavemark.system.md`** — the prose definition
   that the LLM compiler reads at runtime. This is the **source of truth**.
2. **`docs/weavemark.ebnf`** — a deterministic mirror used by the offline
   structural validator and other tooling that must work without an LLM.

This skill keeps the two in agreement. The check is run by
`scripts/check_grammar_sync.py` (pure stdlib, no LLM) and exercised in CI
via `tests/test_grammar_sync.py`.

## How to use

1. Run the check:

   ```bash
   python scripts/check_grammar_sync.py
   ```

2. **If the script exits 0**, the language definition and its grammar
   mirror agree. You're done.

3. **If the script reports errors**, read each error carefully, then apply
   the **source-of-truth rule** below to decide which file to edit.

## Source-of-truth rule (default behaviour)

> The system prompt prose is canonical. The grammar mirror exists to
> serve the prose, not the other way around. When the two disagree,
> **fix the grammar** to match the prose.

The only time you should edit the prose to match the grammar is when the
user has **explicitly asked** for that — for example:

- "I want the grammar to require `enum: [...]` for all enum-typed params;
  please reflect that in the prose."
- "The grammar correctly limits `@compile format` to three values; the
  prose says four — please bring the prose in line with the grammar."

In every other case (including: ambiguity, drift you noticed yourself,
typos in either file, missing schemas), assume the prose is right and
update `docs/weavemark.ebnf` and/or any `promplet-schema` blocks.

## Error catalogue

The script produces these error kinds. Each is fixable mechanically:

- **Kernel grammar drift** — the `ebnf` block in the prompt and the one
  in the grammar file are not byte-identical (after whitespace
  normalisation). Copy the prompt's block into the grammar file.

- **Orphan grammar schema: @foo** — `@foo` has a schema in the grammar
  but no schema in the prompt. Either remove the grammar schema (if the
  directive really doesn't exist) or add a matching `promplet-schema`
  block under the directive's prose section.

- **Missing grammar schema: @foo** — `@foo` has a schema in the prompt
  but no schema in the grammar. Copy the prompt's schema block verbatim
  into `docs/weavemark.ebnf`.

- **Schema disagreement for @foo** — both files have a schema for
  `@foo`, but the params / positionals / flags / body-mode / seam differ.
  The script prints a one-line "prose vs grammar" render of both sides
  to make the diff obvious.

- **Malformed promplet-schema block** — a schema block doesn't parse
  cleanly. The error message includes the file path and line number, and
  the precise violation (unknown type, bad ENUM default, duplicate
  field, etc.). Fix the block in place.

- **Duplicate schema for @foo** — the same directive has two
  `promplet-schema` blocks in the same file. Delete one.

## Informational output

If a directive has a prose heading (`### \`@foo\``) but no
`promplet-schema` block, the script reports it under `INFO:`. Schemas
are **optional** per directive — authors may leave a directive
schemaless while its surface is in flux. Treat INFO entries as gentle
nudges, not failures.

## Authoring conventions

When adding a `promplet-schema` block to the prose, place it
**immediately after the last example** for that directive (and before
the next `###` / `####` heading). The block format and lexicons are
defined in the system prompt's "Per-Directive Schema Blocks (convention)"
section.

After any edit, ALWAYS:

1. Run `python scripts/check_grammar_sync.py` and ensure it prints
   `Grammar sync OK.`
2. Run `python -m pytest tests/test_grammar_sync.py -q` and ensure all
   tests pass.
3. Briefly note the change in your PR description (e.g. "Added
   `@new_directive` schema; mirrored in `docs/weavemark.ebnf`").

## Related files

- `scripts/check_grammar_sync.py` — the deterministic checker
- `tests/test_grammar_sync.py` — the test suite (positive + negative)
- `src/weavemark/prompts/weavemark.system.md` — the language definition
- `docs/weavemark.ebnf` — the grammar mirror
- `src/weavemark/compilation/structural.py` — downstream consumer of the
  grammar (validates `.weavemark.md` files without invoking the LLM)
