---
name: weavemark
description: |
Author, validate, compose, and run WeaveMark specifications
(`.weavemark.md` files). Use this skill whenever the user asks you
to write or modify a prompt-as-program spec, refactor an existing one,
  emit prompt artifacts, or run a composed prompt through an engine.
when_to_use: |
  - Authoring a new `.weavemark.md` file
  - Editing or refactoring an existing spec
  - Splitting a monolithic prompt into reusable fragments via `@refine`
  - Producing role-tagged artifacts (`system`/`user`/`assistant`) via emission
  - Wiring a multi-stage pipeline with `@execute`
  - Validating a spec without burning LLM calls
  - Composing or executing a spec from the CLI
---

# promplet

WeaveMark is a small, opinionated DSL for **prompts as programs**. A
`.weavemark.md` file is plain Markdown sprinkled with `@directives`
and `@{variables}`. The "compiler" is an LLM running the system prompt
at `src/weavemark/prompts/weavemark.system.md`, which is the
**source of truth** for the language. This skill teaches the workflow;
it never duplicates the language reference.

---

## 1. Find the canonical language reference (always)

You should fetch the full reference whenever you need to know exact
directive semantics, parameter names, or output-tag contracts. Two
equivalent ways:

**A. Inside this repo** (preferred when you're editing WeaveMark
itself or a sibling project that has the repo checked out):

```bash
cat src/weavemark/prompts/weavemark.system.md
cat docs/weavemark.ebnf   # deterministic grammar mirror
```

**B. Anywhere `weavemark` is pip-installed** (works in consumer
repos with no local checkout):

```bash
python -c "from importlib.resources import files; \
  print(files('weavemark').joinpath('prompts/weavemark.system.md').read_text())"
```

Both yield byte-identical content; the package data file IS the same
file the controller loads at runtime. Read the relevant sections of
the reference whenever you need authoritative behaviour; **never
guess** directive semantics from memory.

---

## 2. Mental model in one minute

1. A spec is a Markdown document.
2. Lines starting with `@name ...` are **directives**. They may carry
   inline arguments (`@compile format: markdown`) and/or an indented
   body (subspec, free-text, or a small directive-specific DSL).
3. `@{variable}` is the only WeaveMark variable syntax. Mustache
   (`{{ ... }}`) is literal template content — leave it alone.
4. The compiler:
   - **substitutes `@{variables}` first**, then
   - **applies directives in document order**, with declared
     evaluation rules.
5. Every spec compiles to a structured XML envelope (`<prompt>`,
   `<prompts>`, `<compile>`, `<tools>`, `<bindings>`, `<execution>`,
   `<emits>`, `<analysis>`, `<warnings>`, `<errors>`, `<suggestions>`).
   The CLI extracts the parts you care about.
6. Three high-level spec **shapes** exist; the compiler infers which
   one you mean from what's present:
   - **Single prompt** — no `@prompt`, no `@execute` → one composed
     prompt in `<prompt>`.
   - **Pipeline** — has `@execute` → each `@prompt` becomes a pipeline
     stage in `<prompts>`.
   - **Emission** — no `@execute`, every `@prompt` declares a `role:`
     → each block is written to `<emits>` as
     `<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`.

---

## 3. Hello-World specs

### Single-prompt spec

```markdown
@promplet version: 0.7

# Summarize a passage

@style "Crisp, professional, no filler. Two short paragraphs maximum."
  Summarize the following passage for a busy executive:

  @{passage}
```

Run it:

```bash
weavemark --batch-only --output-dir out --var passage="..." summary.weavemark.md
```

### Pipeline spec (multi-stage)

```markdown
@promplet version: 0.7

@execute single-call
  model: gpt-4.1

@prompt extract
  Extract the three most important claims from the text below.
  Return one claim per line.

  @{text}

@prompt critique
  For each of the following claims, rate how well-supported it is
  on a 1–5 scale and explain why in one sentence.

  @{extract.output}
```

### Emission spec (artifacts)

```markdown
@promplet version: 0.7

@prompt agent role: system
  You are a meticulous research assistant who cites sources.

@prompt agent role: user format: mustache
  Find three peer-reviewed papers on @{topic}.
```

Compose produces `agent.system.md` and `agent.user.mustache.md` in the
output directory.

---

## 4. Top-of-mind directives (cheat sheet)

Use this to recall what *exists*. **For exact semantics, parameters,
and edge cases, always consult the canonical reference** (§1). Every
directive listed here also has a `promplet-schema` block inline in
the reference that pins its surface deterministically.

| Directive            | What it does (one line) |
| -------------------- | ----------------------- |
| `@promplet`        | Version pragma; put at top of file. |
| `@compile`           | Compile-time options (`format`, `context`, …). |
| `@prompt`            | Define a named sub-prompt; optionally tagged with `role:`. |
| `@execute`           | Declare an execution strategy + model for pipeline specs. |
| `@emit`              | Emit a verbatim file to `<emits>`. |
| `@refine`            | Pull in another spec as a starting point; cycle-detected. |
| `@if` / `@else_if` / `@else` | Conditional sub-specs; truthiness judged by the LLM. |
| `@match`             | Pattern-style branching DSL. |
| `@example`           | Few-shot example block. |
| `@image`             | Attach an image input by path or URL. |
| `@inspect`           | Mark a region for verbose post-compose inspection. |
| `@note`              | Author-only commentary; stripped from output. |
| `@style`             | Tone / voice / register / formatting / audience guidance. |
| `@normalize`         | Canonicalize + smooth wording across sections. |
| `@output_format`     | Describe expected output shape. |
| `@structural_constraints` | Pin layout/length/format constraints. |
| `@expand` / `@compress` / `@summarize` / `@extract` / `@revise` / `@generate_examples` | Local content transforms. |
| `@assert`            | Compile-time invariants on the spec/text. |
| `@embed`             | Inline opaque content (won't be parsed). |
| `@tool`              | Declare a callable tool (OpenAI function-calling format). |

Common pitfalls:

- **Variables**: `@{name}`, *not* `{{ name }}`. Mustache stays literal.
- **Indentation matters**: a directive's body is its indented block,
  ended by a blank line at the directive's indent level or by a less-
  indented line.
- **Escape literal `@` at line start** with `@@` so it isn't treated
  as a directive.
- **Inline `#` is a comment** outside of fenced code blocks; quote
  the line or move it into a fence to keep a literal hash.
- **`@prompt` disposition is inferred** — see §2 (single / pipeline /
  emission). Mixing role-tagged and role-less `@prompt` blocks in a
  spec without `@execute` is an error.

---

## 5. Validate before composing

Two structural checks run **without any LLM call**:

```bash
# Language-level: are the prose + grammar mirror in sync?
python scripts/check_grammar_sync.py

# Spec-level: parse the spec, list its inputs, title, strategy.
weavemark --scan promplets/catalog/standalone/investment-brief.weavemark.md
```

`--scan` emits JSON; an exit code of 0 means the spec parses
structurally. Use it as a fast smoke test in CI or in a pre-commit
hook for spec-heavy repos.

---

## 6. Compose (LLM, no execution)

```bash
# Single-file output:
weavemark --batch-only -o out.md promplets/catalog/standalone/deep-summary-prompt.weavemark.md \
  --var document="..." \
  --var audience="executive"

# Multi-artifact output (pipeline or emission specs):
weavemark --batch-only --output-dir out/ promplets/catalog/executable/tree-of-thought-solver.weavemark.md

# Variables on the command line or from a JSON file:
weavemark --batch-only --var topic=ferns -o out.md promplets/catalog/standalone/research-brief.weavemark.md
weavemark --batch-only --vars-file vars.json -o out.md promplets/catalog/standalone/research-brief.weavemark.md

# Override output format:
weavemark --batch-only --format json -o out.json promplets/catalog/standalone/research-brief.weavemark.md
```

Always pass `--batch-only` in non-interactive contexts (scripts, CI,
agent loops) to disable any TUI prompts. Use `-v` if a compose fails
and you need to see per-step composition transitions.

---

## 7. Run (compose + execute)

Add `--run` to feed the composed prompt(s) through the engine
declared in `@execute` (or `single-call` if none):

```bash
weavemark --run --batch-only -o out.md promplets/catalog/executable/tree-of-thought-solver.weavemark.md
```

For specs with `@execute`, this dispatches to the matching strategy
(`single-call`, `self-consistency`, `tree-of-thought`,
`simplified-tree-of-thought`, `reflection`).

---

## 8. Workflow recipe for an author agent

1. **Read the user's intent.** Identify which spec shape fits (§2).
2. **Fetch the canonical reference** for any directives you intend to
   use (§1). Read the relevant sections; don't guess.
3. **Sketch the spec** in the smallest form that delivers the user's
   intent. Prefer composition (`@refine`, `@prompt`) over giant
   inline prose.
4. **Validate structurally** with `weavemark --scan` (§5).
5. **Compose** with `--batch-only --output-dir …` and inspect the
   output (§6).
6. **Iterate.** If output is wrong, the fix is almost always in the
   spec — clearer `@style`, sharper `@output_format`, an explicit
   `@example`, or a missing `@structural_constraints`. Use
   `@inspect` to surface what the compiler did at a specific point.
7. **Run** with `--run` only after compose is clean (§7).

---

## 9. Discovery (optional)

If the user is unsure which existing spec to start from:

```bash
weavemark --discover --library-dir /path/to/repo/promplets
```

This launches a small chat that searches available specs and helps
pick a `@refine` target. The non-interactive equivalent is
`weavemark --scan` over each candidate plus your own selection.

---

## 10. Related skills in this repo

- **`grammar-sync`** — Keeps `weavemark.system.md` and
  `docs/weavemark.ebnf` in agreement. Invoke after editing either
  one. The source-of-truth rule (prose wins) is documented there.
- **`weavemark-collaborative-handoff`** — Run, test, debug, and automate
  `@execute collaborative` specs through non-interactive smoke mode or
  filesystem agent handoff.

When you change the **language** (add or modify a directive), use
`grammar-sync`. When you change a **spec written in the language**,
use this skill.
