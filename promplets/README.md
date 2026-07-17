# WeaveMark built-in promplet library

This directory is the canonical, human-browsable source for the promplets shipped
with WeaveMark. Wheel builds map this same tree to `weavemark/promplets`; there is
no second maintained copy.

Every maintained file declares `@promplet version: 0.7`.

## Collections

### `stdlib/`

General, stable reusable promplets.

- `prelude/` contains the small definition modules loaded by default.
- `definitions/` contains definition-first modules whose public surface is
  exported `@define` macros or semantic functions.
- `fragments/` contains body-bearing module promplets refined into other
  promplets.

Every reusable stdlib artifact declares a stable module name under
`weavemark.prelude.*` or `weavemark.std.*`.

### `domains/`

Reusable domain-specific fragments and definitions. Built-in module names use
`weavemark.domains.<domain>.*`.

Current domains include creative work, finance, game design, product,
programming, research, and work intelligence.

### `catalog/`

Complete, ready-to-use entrypoints.

- `standalone/` primarily compiles into prompt or specification artifacts.
- `executable/` declares an execution workflow, engine, tools, or packaged
  outputs.

Catalog promplets usually do not need module declarations: their library path is
their entrypoint identity.

### `tutorials/`

Canonical teaching promplets used by the documentation.

### `experimental/`

Unstable language/runtime experiments. These artifacts ship for inspection and
development but carry no compatibility promise.

## Reuse

Stable reusable content should use a module reference:

```weavemark
@refine module:weavemark.std.reasoning.base_analyst
@use weavemark.std.planning.goals exposing goal_plan
```

Project-local, anonymous material may use an ordinary relative path:

```weavemark
@refine ./library-of-questions-story.weavemark.md
```

`@refine module:...` consumes the module's reusable body in its lexical
environment. A definitions-only module has no refinable body and must be imported
with `@use`.

## Effective libraries

The Processor combines these roots in order:

1. project `./promplets/`;
2. user `~/.weavemark/promplets/`;
3. configured `library_dirs` and `--library-dir` roots;
4. this built-in library.

All roots share one module namespace. `weavemark.*` is reserved for built-in
artifacts; duplicate module identities are errors.

Use `weavemark library` to run or browse the effective library:

```bash
weavemark library tutorial-generator
weavemark library list --collection stdlib --kind fragment
weavemark library show module:weavemark.std.reasoning.base_analyst
```
