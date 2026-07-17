---
name: weavemark
description: Author, validate, compose, and run WeaveMark specifications.
applyTo:
  - "**/*.weavemark.md"
  - "src/weavemark/**"
  - "promplets/**"
---

# promplet (Copilot prompt)

WeaveMark is a small DSL for **prompts as programs**. A `.weavemark.md`
file is Markdown sprinkled with `@directives` and `@{variables}`. The
"compiler" is an LLM running the system prompt at
`src/weavemark/prompts/weavemark.system.md`, which is the **source
of truth** for the language. This prompt teaches the workflow; it
never duplicates the language reference.

## Always fetch the canonical reference

Before writing or modifying any spec, read the relevant section of
the reference. Two equivalent recipes:

```bash
# In the promplet repo:
cat src/weavemark/prompts/weavemark.system.md

# Anywhere promplet is installed:
python -c "from importlib.resources import files; \
  print(files('promplet').joinpath('prompts/weavemark.system.md').read_text())"
```

The deterministic grammar mirror lives at `docs/weavemark.ebnf` and
each directive has a `promplet-schema` fenced block inline in the
reference that pins its surface.

## Three spec shapes (compiler infers)

| Shape          | Trigger                                          | Output |
| -------------- | ------------------------------------------------ | ------ |
| Single prompt  | no `@prompt`, no `@execute`                      | one prompt in `<prompt>` |
| Pipeline       | top-level `@execute`                             | stages in `<prompts>` |
| Emission       | no `@execute`, every `@prompt` declares `role:`  | files in `<emits>` |

Mixing role-tagged and role-less `@prompt` without `@execute` is an
error.

## Top-of-mind directives

Core: `@promplet`, `@define`, `@param`, `@body`, `@phase`,
`@scope`, `@returns`, `@effect`, `@module`, `@use`, `@include`,
`@compile`, `@prompt`, `@execute`, `@emit`, `@if`/`@else_if`/`@else`,
`@match`, `@image`, `@note`, `@embed`, `@tool`, `@bind`.

Default standard-library definitions are already loaded from the configured
module defaults. This includes semantic functions such as `@refine`, `@ask`,
`@assert`, and `@inspect`, plus macro directives such as `@style`,
`@normalize`, `@output_format`, `@structural_constraints`, `@expand`,
`@compress`, `@summarize`, `@extract`, `@revise`, and
`@generate_examples`. Use `@use` for custom or optional modules.

For semantics, parameters, body modes, and edge cases: **read the
canonical reference**, never guess from memory.

## Common pitfalls

- Variables are `@{name}`, not `{{ name }}` (Mustache stays literal).
- Directive bodies are their indented block; blank-line-at-indent
  ends it.
- Literal `@` at start-of-line must be escaped as `@@`.
- Inline `#` is a comment outside of fenced code; quote or fence it
  to keep a literal hash.

## Workflow

```bash
# 1. Structural-only check (no LLM):
weavemark --scan path/to/spec.weavemark.md

# 2. Compose (LLM, no execution):
weavemark --batch-only --output-dir out/ path/to/spec.weavemark.md

# 3. Compose + run:
weavemark --run --batch-only -o out.md path/to/spec.weavemark.md

# 4. With variables:
weavemark --batch-only --var key=value -o out.md spec.weavemark.md
weavemark --batch-only --vars-file vars.json -o out.md spec.weavemark.md
```

Always pass `--batch-only` in non-interactive contexts.

## Iteration rule

If composed output is wrong, the fix is almost always in the spec —
clearer imported `@style`, sharper imported `@output_format`, an
explicit example, or an imported `@structural_constraints` block. Use
imported `@inspect` to surface what the compiler did at a specific
region.

## Related

- `grammar-sync` skill (`.github/prompts/grammar-sync.prompt.md` /
  `.claude/skills/grammar-sync/SKILL.md`) — keeps the language
  definition in sync with its deterministic mirror. Use it when
  changing the language; use **this** prompt when changing a spec
  written in the language.

Full Claude-Code version of this skill with longer examples lives at
`.claude/skills/weavemark/SKILL.md`.
