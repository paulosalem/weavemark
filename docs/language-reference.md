# WeaveMark Language Reference

Technical reference for the WeaveMark notation, version 0.9.

A **promplet** is a Markdown document augmented with directives. The Processor
compiles it into a concrete artifact. Compilation is hybrid: parsing, variable
substitution, branching, imports, assertions, and output contracts are resolved
**structurally** (deterministic, local, no model call); a defined subset of
directives is resolved **semantically** by an LLM.

The normative definition is the system prompt at
[`src/weavemark/prompts/weavemark.system.md`](../src/weavemark/prompts/weavemark.system.md).
Its deterministic mirror is [`weavemark.ebnf`](weavemark.ebnf), kept in sync by
`scripts/check_grammar_sync.py`. Where this document and the system prompt
disagree, the system prompt governs. For operating the Processor, see the
[manual](manual.md).

- [1. Lexical structure](#1-lexical-structure)
- [2. Grammar](#2-grammar)
- [3. Arguments](#3-arguments)
- [4. Variables](#4-variables)
- [5. Bodies and opacity](#5-bodies-and-opacity)
- [6. Resolution model](#6-resolution-model)
- [7. Directive catalogue](#7-directive-catalogue)
- [8. Module system](#8-module-system)
- [9. Macros and semantic functions](#9-macros-and-semantic-functions)
- [10. Diagnostics](#10-diagnostics)

---

## 1. Lexical structure

A promplet is UTF-8 text. A line is a **directive line** iff its first
non-whitespace token matches `@IDENT` and the line begins a logical line.
Otherwise it is a **content line** and passes through as prose.

```
IDENT       ::= /[A-Za-z_][A-Za-z0-9_.\-]*/
bareword    ::= /[A-Za-z0-9_./%\-]+/
PATH_TOKEN  ::= /[A-Za-z0-9_./~+\-]+/
VERSION     ::= /[0-9]+\.[0-9]+/
```

Scoping is by indentation. A directive's body is the maximally indented block
following its header, delimited by `INDENT`/`DEDENT`. There are no closing tags.

`@@` at the start of a logical line is an escape: it renders as a single literal
`@` **after** all directive processing, and only outside opaque carriers.

---

## 2. Grammar

The kernel shape grammar, verbatim from the normative source:

```ebnf
spec              ::= version_pragma? line*
version_pragma    ::= "@promplet" SP+ "version:" SP? VERSION
                      (SP+ "surface:" SP? SURFACE_NAME)? NEWLINE
SURFACE_NAME      ::= "canonical" | "markdown"

line              ::= BLANK_LINE | directive_line | content_line

directive_line    ::= "@" directive_name (SP+ directive_tail)? NEWLINE body?
directive_name    ::= IDENT
directive_tail    ::= define_signature | arg_list
define_signature  ::= IDENT "(" macro_param_list? ")"
body              ::= INDENT line+ DEDENT

content_line      ::= (TEXT | ESC_AT | variable_ref
                      | inline_directive | path_reference)+ NEWLINE
inline_directive  ::= "@" directive_name "(" arg_list? ")"
path_reference    ::= "@" PATH_TOKEN
```

A body is itself a sub-spec: it is parsed by the same rules, recursively.

The kernel fixes only structure and lexis. Per-directive parameter shapes are
specified by `promplet-schema` blocks, one per directive, in the system prompt.

---

## 3. Arguments

```ebnf
arg_list    ::= arg (SP+ arg)*
arg         ::= kv | flag | positional
kv          ::= IDENT ":" SP? value
flag        ::= IDENT
positional  ::= STRING | bareword
value       ::= STRING | NUMBER | BOOL | inline_list | bareword
inline_list ::= "[" (value ("," SP? value)*)? "]"
```

Ambiguity is resolved by **ordered choice**:

1. `kv` wins when an `IDENT` is followed by `:`;
2. `flag` wins when an `IDENT` is not followed by `:`;
3. `positional` otherwise.

Quote a value when it contains spaces, a colon, or leading/trailing whitespace
that matters. Booleans accept `true`/`false`.

---

## 4. Variables

```ebnf
variable_ref ::= "@{" SP? IDENT SP? "}"
```

A variable reference is recognised in content and in non-opaque argument values.
It is never a directive, since directives are line-leading.

The identifier may be a dotted path (`a.b.0.c`). Each segment descends one
nesting level: a mapping key, or an integer list index. **An exact flat key wins
first**; if the whole dotted string is a literal key, it is used before any
descent is attempted. An unresolved path is left intact in the output rather
than being replaced with an empty string, so authoring errors remain visible.

Variables are declared implicitly by use. `--scan` reports the full inferred
input schema without compiling.

---

## 5. Bodies and opacity

Body modes, declared per directive as `body-mode:` in its schema:

| Mode | Meaning |
|---|---|
| `none` | The directive takes no body. |
| `free-text` | Body is literal text. |
| `subspec` | Body is itself a promplet: directives and variables resolve, then the result is handed to the directive's semantics. |
| `opaque` | Body is **not** parsed for directives, variables, or escapes. |
| `dsl:<kind>` | Body is a small directive-specific mini-language, e.g. `dsl:output-kv`, `dsl:match-branches`, `dsl:tool-params`, `dsl:execute-kv`, `dsl:fslm-machine`, `dsl:fslm-state`, `dsl:fslm-transition`. |

Opaque carriers, with their opaque kind:

| Directive | Kind | Note |
|---|---|---|
| `@embed` | `embed-body` | Verbatim payload. |
| `@note` | `note-body` | Stripped before final output. |
| `@output` | `output-kv` | Output-contract key/value pairs. |

The opaque extent is delimited by `INDENT`/`DEDENT` exactly like a normal body.

---

## 6. Resolution model

Compilation proceeds in passes. Structural work is deterministic and local;
semantic work is delegated to a model at a declared **seam**.

**Structural.** Parsing; `@promplet`; module resolution (`@module`, `@use`,
`@include`); macro expansion (`@define` without `@effect`); variable
substitution; branch selection for `@if`/`@else_if`/`@else` and `@match` once
their conditions are decided; `@assert`; `@emit`; `@reference`; `@embed`;
`@note` stripping; output-contract validation.

**Semantic.** Directives that declare an `<LLM: …>` seam. Each seam names the
transformation the model must perform:

| Directive | Seam |
|---|---|
| `@if`, `@else_if` | `if-condition` |
| `@match` | `match-value` |
| `@expand` | `semantic-expansion` |
| `@style` | `style-transform` |
| `@polish` | `polish-transform` |
| `@normalize` | `normalize-transform` |
| `@revise` | `revise-transform` |
| `@compress` | `compress-transform` |
| `@summarize` | `summarize-transform` |
| `@extract` | `extract-transform` |
| `@generate_examples` | `example-generation` |

`@refine` is also semantic: it has no fixed schema and is handled as a general
imported directive.

Generated prose, code, and images are model- and run-dependent. WeaveMark
provides a stable language surface around that behavior; it does not make the
behavior deterministic and claims no formal verification.

---

## 7. Directive catalogue

Notation: `name: TYPE` is a positional argument; `key:` is a parameter;
`(required)` marks obligations; `= v` gives a default.

### 7.1 Document and modules

| Directive | Arguments | Effect |
|---|---|---|
| `@promplet` | `version:` NUMBER (required), `surface:` | Version pragma. Must be first when present. |
| `@module` | `name: IDENT` (required) | Declares this file importable under a dotted name. |
| `@use` | `module: IDENT` (required), `as:` | Imports a module, optionally aliased. |
| `@include` | `module: IDENT` (required) | Includes a module's content. |
| `@refine` | promplet reference, `mingle:` BOOL | Weaves another promplet's meaning into this one. |

`@refine` takes a bare fragment reference, a `module:` reference, or an explicit
filesystem path. **Bare names are library references, not paths**: to mean a
path, begin it with `./`, `../`, `/`, or `~/`.

```markdown
@refine module:weavemark.std.analysis.mece_core
@refine ./local-base.weavemark.md
@refine teaching/socratic-tutoring
  Shape the interaction loop; do not change the output format.
```

The body is Processor-facing *mingle guidance*, used only when `mingle` is true
or omitted, and never emitted as standalone text. With `mingle: false` the
import is preserved literally, and a non-empty body is an authoring error
because no mingle step exists for it to guide.

### 7.2 Control flow

| Directive | Arguments | Effect |
|---|---|---|
| `@if` | condition | Includes the body when the condition holds. |
| `@else_if` | condition | Alternative branch. |
| `@else` | — | Fallback branch. |
| `@match` | value | Selects among labelled branches. |

Conditions are evaluated at the `if-condition` seam, so they may be
natural-language predicates over variables, not only boolean flags. If
evaluation is blocked by a missing variable, the Processor warns and takes the
least-surprising fallback for that directive.

### 7.3 Semantic transformation

| Directive | Arguments | Effect |
|---|---|---|
| `@expand` | — | Elaborates a compact statement of intent. |
| `@style` | `instruction: STRING` (required) | Restyles content. |
| `@polish` | `instruction: STRING` | Improves without changing meaning. |
| `@normalize` | `instruction: STRING` (required), `scope:` | Unifies terminology and requirement strength. |
| `@revise` | `instruction: STRING` (required), `mode:` | Revises under an instruction. |
| `@compress` | `instruction: STRING` (required) | Shortens while preserving obligations. |
| `@summarize` | — | Condenses content. |
| `@extract` | `instruction: STRING`, `format:` | Extracts structured material. |
| `@generate_examples` | `count: NUMBER` | Produces illustrative examples. |

### 7.4 Contracts and validation

| Directive | Arguments | Effect |
|---|---|---|
| `@output` | `format: STRING`, `type: text\|image` = `text`, `enforce:`, `size:`, `quality:`, `model:`, `n:`, `edit:`, `file:` | Declares the output contract. Body is `dsl:output-kv`. |
| `@assert` | `contains: STRING` | Fails compilation unless the requirement holds. |
| `@structural_constraints` | `strict: BOOL` | Constrains structural shape. |
| `@compile` | `format: IDENT` | Selects a named output format. |

`@assert` is structural: it is checked deterministically, before any assistant
sees the compiled prompt.

### 7.5 Output and artifacts

| Directive | Arguments | Effect |
|---|---|---|
| `@prompt` | `name: IDENT` (required), `role: system\|user\|assistant\|tool` | Names a prompt stage or role-tagged artifact. |
| `@emit` | `file: PATH` (required) | Writes a file. |
| `@package` | `instructions: PROMPLET_REF`, `from: PATH`, `file: PATH` (required) | Packages an artifact, e.g. into HTML or PDF. |
| `@reference` | `file_path: PATH` (required), `keep: BOOL` = `true` | References a file's content. |
| `@embed` | `file: RESOURCE_REF`, `lang:`, `label:`, `indent: BOOL` = `true` | Embeds a payload. Body is opaque. |
| `@note` | — | Author note. Opaque, and stripped from output. |

`@package instructions:` accepts a promplet reference, which is what makes
packaging *semantic*: the referenced promplet describes how to render the
artifact rather than hard-coding a template.

### 7.6 Execution

| Directive | Arguments | Effect |
|---|---|---|
| `@execute` | `strategy: IDENT` (required) | Selects the runtime engine. |
| `@tool` | `function_name: IDENT` (required) | Declares a callable tool. |
| `@bind` | `capability_name: IDENT` (required), `language:` (required), `from: PATH` (required), `symbol: IDENT` (required) | Binds a trusted companion program. |
| `@effect` | `name: IDENT` (required) | Marks a definition as effectful. |

Built-in strategies: `single-call`, `self-consistency`, `tree-of-thought`,
`simplified-tree-of-thought`, `reflection`, `chain`, `collaborative`, `fslm`,
`functional`. A fully-qualified Python class path selects a custom engine.

Execution occurs only under `--run`. Compilation alone never runs an engine,
never calls a bound program, and never performs a declared effect.

### 7.7 Finite-state machines

Used by the `fslm` engine.

| Directive | Arguments |
|---|---|
| `@machine` | `name: IDENT` (required), `initial:` |
| `@state` | `name: IDENT` (required), `terminal: BOOL` |
| `@transition` | `name: IDENT` (required), `event:` |
| `@input` | `name: IDENT` (required), `default: STRING` |
| `@guard` | `id: IDENT` (required), `kind: nl\|deterministic` |
| `@action` | `name: IDENT` (required), `tool:` |

`@guard kind:` selects the evaluator: `deterministic` for structural predicates,
`nl` for model-judged ones.

### 7.8 Definitions

| Directive | Arguments | Effect |
|---|---|---|
| `@define` | `name: IDENT` (required), or compact signature | Declares a macro or semantic function. |
| `@param` | `name: IDENT` (required), `default: ANY` | Declares a parameter. |
| `@body` | — | Marks the body insertion point. |
| `@phase` | `compile\|execute` (required) | Declares when the definition resolves. |
| `@scope` | `self\|body\|enclosing_block\|prompt\|document\|metadata` (required) | Declares the extent affected. |
| `@returns` | `kind: IDENT` (required) | Declares the return kind. |

---

## 8. Module system

`@module name.path` makes a file importable. Names are dotted and conventionally
mirror the library layout — for example
`weavemark.std.analysis.mece_core`.

Resolution order for a bare reference is project → user → extra → builtin, so a
project promplet shadows a built-in of the same name. Prefixes force a source:
`project:`, `user:`, `extra:`, `builtin:`, `module:`.

Modules listed under `modules` in `weavemark.json` are imported into every
compilation. Aliases under `fragments` map short names to fragment paths.

---

## 9. Macros and semantic functions

`@define` without `@effect` declares a **deterministic macro**: it expands
structurally, with no model call.

```markdown
@define greeting(name: World)
  Hello, @{name}.
```

`@define` with `@effect` declares a **semantic function**: its body describes an
intent the model realizes at compile time.

Both are compile-time abstractions and are resolved *before* ordinary directive
evaluation.

---

## 10. Diagnostics

Structural errors — unknown directives, malformed arguments, unresolved required
inputs, failed assertions, `@emit` collisions, a body given to a directive whose
schema is `none` — are reported before any model call and fail the compilation.

Warnings are emitted where the language defines a defensible fallback, such as a
condition that cannot be evaluated because a variable is missing.

`--scan` performs structural analysis only, making it the correct way to validate
syntax and inspect the input schema without incurring provider cost.
