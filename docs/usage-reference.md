# WeaveMark Processor and language reference

The `weavemark` command is the **WeaveMark Processor**: the command-line tool for
compiling, inspecting, and running promplets.

## Live demo

Start with a plain single-spec run when you want the normal user experience:

```bash
cd weavemark
./examples/terminal-output-only/program-review-checklist/run.sh
```

That script is intentionally boring: it runs one WeaveMark Processor command with
a vars file and prints the composed prompt directly to the terminal, with no
saved-file summary.

Run the curated static suite when you want a tour of many directives:

```bash
./examples/batch-example-runs/static-prompts/run.sh
```

The suite walks through progressively more powerful compositions — from basic
`@refine` + `@match`, through content pipelines (`@extract` → `@summarize` →
`@compress`), to the full prompt-refactoring pipeline that treats a messy prompt
as a program and refactors it semantically.

Each example folder owns its `run.*`, `inputs/`, and `outputs/` files. The shell
runners are hardcoded command transcripts: inspect them to see the WeaveMark
Processor commands directly. Multi-example suites use `--show-output` so the terminal
first shows the actual composed or executed prompt experience, and
`--no-file-summary` so they can list saved artifact files once at the end
instead of interleaving file messages between prompts.
Run `weavemark --help` for the Processor's own usage.

## Built-in and custom promplet libraries

Wheel installations include the canonical repository `promplets/` tree as
package resources. `weavemark library` presents that built-in corpus together
with custom roots:

- project-local `./promplets/`;
- user `~/.weavemark/promplets/`;
- `library_dirs` in `~/.weavemark/config.json`;
- `library_dirs` in the nearest `.weavemark.config.json`;
- repeatable `--library-dir DIR` values.

```bash
# Inspect effective roots in precedence order.
weavemark library sources

# Search all sources, or one source explicitly.
weavemark library list research
weavemark library list --source user
weavemark library list --source builtin
weavemark library list --collection stdlib --kind fragment

# Run, inspect, or copy promplets.
weavemark library investment-brief --var ticker=MSFT
weavemark library show builtin:catalog/standalone/investment-brief
weavemark library copy ./weavemark-promplets
```

Bare references resolve project, user, additional, then built-in promplets.
Explicit source and module references remove ambiguity:

```bash
weavemark library investment-brief
weavemark library builtin:catalog/standalone/investment-brief
weavemark library module:weavemark.std.reasoning.base_analyst --scan
```

For scripting, `library sources` and `library list` accept `--json`. The default
text tables and `library show` write primary data to stdout; diagnostics and
copy summaries go to stderr.

## Experimental protections

WeaveMark enables experimental protection boundaries by default. They reduce the
chance that a malicious or surprising promplet reads unrelated files, overwrites
unrelated outputs, reaches private network services, executes code, launches a
process, or downloads an oversized payload.

> **Warning:** protected mode is not an OS sandbox. Python modules and approved
> external programs still run with your user account's permissions. Do not run
> promplets you do not trust, even with protections enabled.

The automatic read roots are the entrypoint promplet directory, the directory
where the CLI was invoked, the discovered project root, configured library roots,
and `~/.weavemark/promplets`. Automatic write roots are the entrypoint directory,
the invocation directory, and each directory's `outputs/` folder. Paths are
canonicalized, so a symlink cannot silently escape a root. Sensitive files such
as `.env`, private keys, credential stores, `.ssh`, and `.aws` remain denied even
when they sit under a read root.

Confirmation-required operations show a yellow warning panel and default to
**No**. Decisions are stored per exact item in
`~/.weavemark/protection-approvals.json`; changed Python files require approval
again. Batch mode and non-interactive API calls cannot ask, so an unapproved
confirmation-required operation is blocked. The red diagnostic identifies the
operation, danger, policy key, and remediation.

Configure protections in a user or system `weavemark.json`:

```json
{
  "protections": {
    "enabled": true,
    "readRoots": [],
    "writeRoots": [],
    "sensitiveFiles": "deny",
    "dynamicReads": "confirm",
    "writesOutsideRoots": "confirm",
    "pythonCode": "confirm",
    "externalProcess": "confirm",
    "remoteHttps": "allow",
    "remoteHttp": "deny",
    "privateNetworks": "deny",
    "maxDownloadBytes": 20000000,
    "downloadTimeoutSeconds": 30,
    "maxRedirects": 3,
    "subprocessEnvironment": ["PATH"]
  }
}
```

Policy values are `allow`, `confirm`, or `deny`. User/system configuration may
grant additional roots or change policy. A project `weavemark.json` may only
tighten protections: it cannot disable them, grant roots, increase download
limits, or add inherited environment variables.

Use `--no-protections` only when you intentionally trust the promplet and want
the previous unrestricted behavior:

```bash
weavemark trusted.weavemark.md --run --no-protections
weavemark implement compiled-spec.md --no-protections
```

The TUI enforces the same boundaries, but confirmation-required operations must
already be approved, configured as `allow`, or explicitly bypassed because the
TUI does not yet provide its own confirmation dialog. Remote hostname policy is
checked before each request and redirect, but DNS resolution is not pinned to
the subsequent connection; a narrow DNS-rebinding race remains. These are two
reasons the feature is explicitly experimental.

## Configurable debug logging

Logging is enabled and deliberately useful by default. Normal variables, LLM
requests/responses, tool data, usage, errors, CLI options, and application
events are retained; binary and base64 payloads are omitted. Configure each
surface independently in a user or system `weavemark.json`:

```json
{
  "log": {
    "enabled": true,
    "directory": null,
    "level": "INFO",
    "applicationEvents": true,
    "cliArguments": true,
    "variables": true,
    "llmCalls": true,
    "llmRequests": true,
    "llmResponses": true,
    "toolData": true,
    "usage": true,
    "errors": true,
    "binaryData": false,
    "maxFileBytes": 5242880,
    "backupCount": 5,
    "retentionDays": 30
  }
}
```

`variables` controls the structured variable map in the application log.
`llmRequests` stores the exact model request, which inherently contains any
variables interpolated into that request. Disable `llmRequests` when variable
values must not appear anywhere. `binaryData: false` recursively replaces image,
audio, PDF, byte, and media data-URL payloads with size-bearing omission markers
while preserving surrounding text and structure.

User/system configuration may enable or disable any logging surface. A project
config may only reduce logging, retention, and file sizes; it cannot redirect
logs or enable content the user disabled. Log directories and files use
restrictive permissions on POSIX. `--help` and `--version` do not initialize
logging.

`WEAVEMARK_LOG=0`, `WEAVEMARK_LOG_DIR`, and `WEAVEMARK_LOG_LEVEL` remain
process-level overrides. Full `--record-run` bundles are separate explicit
artifacts and always contain replay-critical request/response content.

## Optional provenance and exact run replay

Normal compilation remains unchanged and produces no provenance files. Add
`--provenance` when traceability matters:

```bash
weavemark example.weavemark.md \
  --provenance outputs/example.provenance.json
```

The manifest includes processor/language versions, model and effective compile
settings, system-prompt and response-schema hashes, source/variable/resource
hashes, structural-versus-semantic lineage, artifact hashes, timestamps,
compilation latency, provider-reported token usage, and provider-reported USD
cost when available. Variable values are hashed rather than copied into a
manifest.

Use a run recording for strict replay:

```bash
weavemark example.weavemark.md --record-run outputs/example-run
weavemark example.weavemark.md --replay-run outputs/example-run
```

`--record-run` writes `manifest.json`, `calls.jsonl`, and `result.json`.
Recordings include exact LLM requests, responses, and tool results and can
therefore contain source text, variables, imported content, and images. They
are created with restrictive permissions and must be treated as sensitive.

Replay makes no provider calls and never falls back to live completion. It
fails if the canonical request sequence or deterministic local tool results
differ. Exact replay reproduces the recorded compilation; it does not claim
that a provider would independently return the same answers later. Interactive
`@ask` recordings are intentionally not replayed because replay must not invent
or silently reuse a human decision.

## Quoting directive arguments

Simple single-token values can be unquoted:

```markdown
@expand mode: intention length: 70%
  Turn the compact idea into a fuller implementation-ready section.
@compile format: markdown
```

Free-form positional strings can also be unquoted across multiple words when
they appear before named parameters:

```markdown
@style "concise, direct, no filler"
  Summarize @{source_notes} for @{audience}.

@revise "remove contradictions" mode: editorial
  The product is self-serve. The product requires manual onboarding.

@normalize "use consistent terminology" scope: semantic
  Use "workspace", "project", and "team space" consistently.
```

Quote the string when a literal token contains `:` or bracket/list syntax:

```markdown
@style "Tone: direct"
  Explain @{decision}.

@style "Use [short, direct] bullets"
  List the risks, mitigations, and owner for @{plan}.
```

Once a named parameter appears, additional bare positional tokens are invalid.
Write free-form text before named parameters, or use a quoted named value when a
directive supports one.

## Usage

### Interactive mode (default)

```bash
# Guided compile: asks for missing @{variables}, @match choices, and @if flags.
weavemark library builtin:catalog/standalone/tutorial-generator

# Prefill a few values; the Processor asks only for what remains missing.
weavemark library builtin:catalog/standalone/tutorial-generator \
  --var topic="FastAPI" \
  --var audience=intermediate
```

Default mode is the normal human-facing WeaveMark Processor experience. It scans
the promplet without an LLM call, shows a compact guided-input panel when values
are missing, collects those values, compiles, prints the result, and then offers
the follow-up refinement prompt.

Use `--vars-file vars.json`, `--vars-file vars.yaml`, or `--vars-file vars.yml`
to load one object of reusable values. YAML block scalars (`|`) are convenient
for long prompts and source text. Inline `--var KEY=VALUE` values override the
file. Boolean Processor values accept `true`/`false`, `yes`/`no`, and `1`/`0`.
Variable files are input data only: model and engine selection remain explicit
runtime concerns.

### Batch mode (with `--batch-only`)

```bash
# Market research brief with inline variables. Missing inputs fail fast.
weavemark library builtin:catalog/standalone/market-research-brief \
  --var industry="electric vehicles" \
  --var company="Rivian" \
  --var report_depth=detailed \
  --var include_competitors=true \
  --var time_horizon="3 years" \
  --format markdown --batch-only

# Program review checklist with JSON vars file, saved to a file
weavemark library builtin:catalog/standalone/program-review-checklist \
  --vars-file examples/saved-artifact-workflows/program-review-json/inputs/vars.json \
  --format json --output review.json --batch-only

# Read spec from stdin. Stdin implies non-interactive behavior.
cat promplets/catalog/standalone/tutorial-generator.weavemark.md | weavemark --stdin \
  --vars-file examples/batch-example-runs/static-prompts/inputs/tutorial-fastapi.json --batch-only
```

Batch mode is the automation contract: no prompts, no follow-up loop, and no
silent unresolved inputs. If a user-facing input is missing, WeaveMark exits
before compilation and tells you which variables to provide with `--var` or
`--vars-file`.

### Metadata scan and full TUI

```bash
# Print the input schema and structural metadata as JSON; no LLM call.
weavemark library builtin:catalog/standalone/tutorial-generator --scan

# Open the terminal UI with a generated input form and live preview.
weavemark library builtin:catalog/standalone/tutorial-generator --ui
```

`--scan` is designed for IDEs, wrappers, and pre-flight checks. It reports
discovered inputs, output artifacts, tools, and execution metadata. `--ui` uses
the same scanner to build a richer terminal form.

### Output formats

```bash
# Produce machine-readable JSON for another program.
weavemark library builtin:catalog/standalone/tutorial-generator \
  --vars-file examples/batch-example-runs/static-prompts/inputs/tutorial-fastapi.json \
  --format json \
  --batch-only

# Save the primary composed prompt and still show it in the terminal transcript.
weavemark library builtin:catalog/standalone/tutorial-generator \
  --vars-file examples/batch-example-runs/static-prompts/inputs/tutorial-fastapi.json \
  --output tutorial-prompt.md \
  --show-output \
  --batch-only
```

- **`--format markdown`** (default) — Human-readable Markdown; non-verbose prints only the prompt
- **`--format json`** — Machine-readable JSON with `composed_prompt`, `tools`, `issues`, and `tool_calls_made`
- **`--output report.md`** / **`-o report.md`** — Write the primary composed prompt to a file (`@emit` / role-tagged `@prompt` artifacts land in the same directory)
- **`--output-dir dist/`** — Write all artifacts into a directory. The primary prompt is named after the spec stem (e.g. `asset-deep-search.weavemark.md` → `asset-deep-search.md`); `@emit` / role-tagged `@prompt` artifacts use their declared names. If the spec produces no primary content (whitespace-only), no primary file is written and a warning is printed. Mutually exclusive with `--output`.
- **`--show-output`** — When paired with `--output` or `--output-dir`, also print the primary composed/executed output before writing file artifacts. This is useful for demos and terminal transcripts that should show the authentic WeaveMark result first.
- **`--no-file-summary`** — Write requested output files without printing per-file success messages. Demo scripts use this with `--show-output`, then print one clean artifact summary at the end.

### Multi-file emission

When a spec has **no top-level `@execute`** and every `@prompt` block declares `role:`, the WeaveMark Processor treats the spec as artifact emission: each block becomes a file `<name>.<role>[.<prompt-format-ext-if-different>].<compile-ext>`.

```markdown
@prompt intro role: system
  You are a precise research assistant.

@prompt request role: user
  Research this topic: @{topic}
```

`role:` must be exactly one of `system`, `user`, `assistant`, or `tool` (case-insensitive). Use dotted prompt names for variants that should appear before the role, and optional per-prompt **`format:`** for content/template formats such as `mustache` or `jinja`:

```markdown
@prompt asset-deep-search role: system format: mustache
  You are searching for @{asset}. Use {{template_var}} like a Mustache template.

@prompt asset-deep-search.fallback role: system
  Simpler instructions for the fallback model.
```

This produces `asset-deep-search.system.mustache.md` and `asset-deep-search.fallback.system.md`. `format:` is rejected when `@execute` is present (it is emission-only). `as:` is reserved for execution-result bindings on semantic definition calls.

Pair this with `--output-dir dist/` when the source contains *only* role-tagged `@prompt` or `@emit` blocks (no primary prompt body): WeaveMark drops the would-be empty primary file and writes only the named artifacts.

Use `@compile format: <configured-format>` to declare the spec's default CLI output format. This also controls the outer extension of role-tagged emissions. If neither the spec nor CLI specifies a format, WeaveMark assumes Markdown (`.md`). If both are present, the explicit CLI `--format` value wins and WeaveMark prints a warning.

```markdown
@compile format: json

@prompt intro role: system
  {"system": "You are a precise research assistant."}
```

By default, the spec's root-text prefix and suffix do **not** cascade into emitted artifacts (each emission stays self-contained). Set `@compile context: cascade` to enable cascading for emission specs, or `@compile context: local` to disable it for pipeline specs. `@compile context: auto` keeps the inferred default.

`@output` still describes the downstream assistant response format; use `@compile` for compile-time output defaults.

Use `@emit file: <relative-path>` when you need an explicit artifact file path instead. Emitted content is removed from the primary prompt, added to the structured `emits` result, and written by the CLI next to `--output` (or inside `--output-dir`, or next to the source spec when neither is provided).

```markdown
@emit file: system.md
  You are a precise research assistant.

@emit file: user.md
  Research this topic: @{topic}
```

### Modules, fragments, and configuration

All effective promplet-library roots share one dotted module namespace:

1. project `./promplets/`;
2. user `~/.weavemark/promplets/`;
3. configured `library_dirs` and `--library-dir` roots;
4. the built-in package library.

Curated reusable promplets declare `@module`. A body-bearing module is a
**fragment**; a bodyless module whose public surface is exported `@define`
operations is a **definition module**:

```weavemark
@promplet version: 0.8
@module company.writing.calm_voice

# Calm voice

Write with direct, reassuring language and no artificial urgency.
```

`@use` imports definitions. `@refine module:...` composes a module's reusable
body. Ordinary paths remain available for local anonymous fragments:

```weavemark
@use weavemark.std.planning.goals exposing goal_plan
@refine module:company.writing.calm_voice
@refine ./local-campaign-context.weavemark.md
```

`weavemark.*` is reserved for built-in modules. Duplicate module declarations
across effective roots are errors.

Promplet library roots are configured in `~/.weavemark/config.json`, the nearest
`.weavemark.config.json`, or with `--library-dir`:

```json
{
  "library_dirs": ["/work/team-promplets"]
}
```

WeaveMark separately reads optional `weavemark.json` files for format mappings,
default module imports, fragment path aliases, and implementation profiles:

```json
{
  "formats": {
    "markdown": {"extension": "md", "aliases": ["md", ".md"]},
    "mustache": {"extension": "mustache"},
    "jinja": {"extension": "jinja", "aliases": ["jinja2"]}
  },
  "modules": {
    "defaults": [
      "weavemark.prelude.semantics",
      {
        "name": "weavemark.prelude.presentation",
        "exposing": ["concise"]
      }
    ]
  },
  "fragments": {
    "aliases": {
      "repo": "promplets"
    }
  },
  "implementation": {
    "default_profile": "copilot",
    "output_root": "outputs/implementations",
    "default_name": "{source_stem}",
    "collision": "timestamp",
    "profiles": {
      "claude-code": {
        "type": "process",
        "command": "claude",
        "cwd": "{implementation_dir}",
        "args": ["-p", "{prompt_text}"]
      }
    }
  }
}
```

`formats` maps identifiers used by `@compile format:` and `@prompt format:` to
filename extensions. `modules.defaults` lists modules loaded into each root
promplet before explicit `@use` directives are processed; string entries expose
every exported definition directly, while object entries may specify `alias`
and `exposing`.
Directly exposing a name that a default module already made available is a
normal name collision; remove the redundant `@use` instead.

`fragments.aliases` remains available for project-local path shorthand. Stable
stdlib and domain fragments should prefer their declared `module:` identity.

`implementation` configures the optional `weavemark implement` phase, which
hands a compiled software specification to a headless programming agent. WeaveMark
has a built-in `copilot` process profile, so projects only need configuration
when they want to change naming, paths, collision behavior, or add additional
profiles such as Claude Code. The implementation name defaults to the exact
source stem; WeaveMark only strips the compound `.weavemark.md` suffix for
source specs. It does not remove study prefixes such as `02-treatment-`.

```bash
weavemark implement compiled-spec.md --name orbital-drift --dry-run
```

`weavemark implement` writes a fresh workspace under `output_root`, copies the
compiled spec to a name-derived snapshot and to `compiled-spec.md`, writes the
agent prompt to a name-derived artifact and to `implementation-prompt.md`, and
records a JSON manifest. Use `--reuse-dir` to continue in an existing workspace;
otherwise non-empty destination collisions use the configured behavior
(`timestamp` by default).

Override path templates when a project wants different public artifact names:

```json
{
  "implementation": {
    "paths": {
      "implementation_dir": "{output_root}/{implementation_name}",
      "compiled_spec_snapshot": "{implementation_name}.compiled-spec.md",
      "agent_prompt": "{implementation_name}.implementation-prompt.md",
      "transcript": "{implementation_name}.{profile}.transcript.log",
      "manifest": "{implementation_name}.implementation.json"
    },
    "workspace_aliases": {
      "compiled_spec": "compiled-spec.md",
      "agent_prompt": "implementation-prompt.md"
    }
  }
}
```

Profiles currently support `type: "process"` with a command, argv-style `args`,
working directory, optional `env`, and optional `defaults`. Arguments are not
shell strings. They are expanded only through explicit placeholders such as
`{implementation_dir}`, `{prompt_text}`, `{profile}`, `{session_name}`,
`{max_continues}`, and `{model}`.

```markdown
@refine repo:programming/foundations/software-spec
@refine repo:programming/types/web-based-game
```

If exactly one fragment alias is configured, the alias is optional:

```markdown
@refine programming/foundations/software-spec
```

By default, `@refine` performs semantic mingling: the referenced spec constrains
the compiled result, but the final prompt should read as one concrete
specification rather than pasted fragments. Add an indented body when a specific
refinement needs local guidance:

```markdown
@refine teaching/socratic-tutoring
  Use this refinement to shape the interaction loop and feedback behavior.
  Do not change the requested final output format.
```

That body is Processor-facing mingle guidance. It is used only when `mingle` is
true or omitted, and it should not appear as standalone output text. With
`mingle: false`, a non-empty body is an authoring error because literal
preservation has no semantic mingle step for the body to guide.

Bare fragment references are intentionally different from explicit filesystem
paths. Use `./`, `../`, `/`, or `~/` when you mean a concrete path:

```markdown
@refine ./local-base.weavemark.md
@refine ../shared/team-style.weavemark.md
```

When a bare reference is used with no fragment alias, WeaveMark reports an
error. When multiple aliases exist, WeaveMark reports an ambiguity and asks for
the `alias:path` form. Fragment lookup tries the exact reference, then
`.weavemark.md`, then `.md` for extensionless references.

Use `@expand` when a compact phrase should be semantically elaborated during
compilation. Put expansion intent in the directive header and the compact source
material in the indented body:

```markdown
@expand mode: intention focus: "data model and validation implications"
  A personal observatory for work.
```

`focus:` is not an enum. Use ordinary language to say what matters for this
expansion, such as interaction behavior, failure modes, metaphor mapping,
pedagogy, UI implications, or any other local concern. The body is the material
being expanded.

Use `@compress` when a local section should become more concise without losing
its distinct operational information:

```markdown
@compress "Make this dense enough for an implementation handoff; preserve hard requirements."
  @refine programming/foundations/software-spec

  Design a local-first release checklist app with gates, evidence, waivers,
  validation records, and acceptance criteria.
```

`preserve: hard` is the safe default: WeaveMark should exceed the requested
budget rather than silently drop important requirements. The indented body is
the sub-spec or content being compressed; put the compression instruction inline
and keep the body reserved for the target material. Use `@compress` as a scoped
directive for sections where concision matters; a future compile-level verbosity
setting could provide a broad default, but scoped compression is the more
precise tool when only part of a specification needs tightening.

### Tool/Function Calling

Use the `@tool` directive to define tools/functions that the composed prompt's consumer can invoke via LLM function calling. Tool definitions are compiled to OpenAI-compatible JSON Schema — which works universally across all providers via LiteLLM.

```markdown
@tool search_web
  Search the web for information and return relevant results.
  - query: string (required) - The search query
  - max_results: integer default: 5 - Maximum results

@bind search_web language: python from: "./tools/search.py" symbol: search_web

@tool get_weather
  Get current weather for a location.
  - location: string (required) - City name or coordinates
  - units: string enum: [celsius, fahrenheit] default: celsius - Units
```

`@tool` declares schema only. Helper implementations are always attached with
`@bind`; inline implementation parameters such as `@tool search impl: python`
are rejected.

When a `single-call` executable declares both `@tool` and matching Python
`@bind` entries, `weavemark ... --run` executes the complete multi-turn tool
loop directly. The model chooses calls from the declared schemas; the bound
functions implement only those calls. Use `max_iterations` and
`max_tool_calls` under `@execute single-call` to bound the loop. Python binding
imports remain subject to WeaveMark protections.

```markdown
@execute single-call
  max_iterations: 12
  max_tool_calls: 20

@bind search_web language: python from: "./tools/web.py" symbol: search_web

@tool search_web
  Search the web.
  - query: string (required) - Focused query
```

For recurring workflows, a promplet may embed a bounded folder of prior
Markdown reports and summarize it into comparison memory:

```markdown
@if use_previous_reports
  @summarize
    Keep only story identity, decisive facts, status, and material changes.
    @embed folder: "@{previous_reports}" label: "Previous reports"
```

Folder embedding reads sorted `.md` files only, with a maximum of 20 files and
120,000 characters. Keep execution traces outside the history folder so memory
contains reports rather than raw logs.

Tools compose naturally with control-flow directives:

```markdown
@if include_web_tools
  @tool search_web
    Search the web for information.
      - query: string (required) - Search query

@match agent_type
  "researcher" ==>
    @tool read_paper
      Read an academic paper.
      - url: string (required) - Paper URL
  "programmer" ==>
    @tool run_program
      Execute a program in a sandbox.
      - source: string (required) - Program text to run
```

In JSON output mode, tool definitions appear in the `tools` array alongside the composed prompt:

```json
{
  "composed_prompt": "You are a research assistant...",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_web",
        "description": "Search the web for information.",
        "parameters": {
          "type": "object",
          "properties": {
            "query": { "type": "string", "description": "The search query" }
          },
          "required": ["query"]
        }
      }
    }
  ]
}
```

See [`promplets/catalog/executable/react-agent.weavemark.md`](../promplets/catalog/executable/react-agent.weavemark.md) for a full example.

### Deterministic assertions

Use `@assert` for prompt invariants that should be checked during composition. Free-text assertions keep their normal semantic behavior, while explicit checks can run deterministically:

```markdown
@assert includes: "Output Format"
@assert includes: "Do not invent missing data."
@assert not_contains: "@{"
@assert variable: "finance_surface"
```

Satisfied assertions are removed from the final prompt. Failed assertions are reported as errors unless `severity: warning` is set.

### Compile-time clarification with `@ask`

Use `@ask` when the Processor should pause and clarify consequential ambiguity
before finishing the prompt under its scope:

```markdown
@ask clarifying question detail_level: 40%
  Draft a customer interview prompt for @{product}.
```

Syntax:

```markdown
@ask <question type> detail_level:<percentage>
  <body>
```

- `<question type>` defaults to `clarifying question`.
- `detail_level` defaults to `20%` and must be greater than `0%` and no greater
  than `100%`.
- The indented body is the sub-spec being clarified. If no body is provided,
  the directive applies to the current enclosing spec scope.
- When several `@ask` directives are active, innermost scopes ask first.
- `@ask` is iterative: the Processor may ask, transform part of the body, keep
  `@ask` in intermediate XML, ask again after newly exposed ambiguities, and
  continue until the final output no longer contains unresolved `@ask`.

Guided CLI mode asks the questions in the terminal. `--batch-only` and `--stdin`
are non-interactive, so they fail clearly if active `@ask` directives need a
host answer. Python hosts can pass `ask_handler` to `compile_text()`,
`compile_file()`, `execute_text()`, or `execute_file()`.

### Iterative compile-time improvement with `@iterate`

Use `@iterate` when a body should be compiled through explicit inside-out
directive steps, judged step by step, and rerun where a previous directive
application can be materially improved:

```markdown
@iterate 4
  @expand mode: intention
    Draft an onboarding prompt for @{product}.
```

Syntax:

```markdown
@iterate [n]
  <body>
```

- `n` is an optional positional integer. It counts improvement iterations after
  iteration 0.
- If `n` is omitted, WeaveMark uses
  `CompileOptions.max_iterate_turns` / `WeaveMarkConfig.max_iterate_turns`.
- If `n` is greater than the configured cap, the effective budget is capped by
  configuration.
- If the budget is exhausted and any step still needs material improvement,
  compilation returns the best available result and emits a warning.
- If no indented body is provided, `@iterate` targets the whole containing spec
  with the `@iterate` directive itself removed.

`@iterate` does not accept user-specified criteria. Its built-in criterion is:
each directive application should be compiled as well as possible while fully
obeying the original directive semantics, parameters, body, local context, and
downstream purpose.

Iteration 0 compiles the target and records a trace. Each trace step is a strict
compiler-result JSON object whose `directives` array identifies the directive
application or sibling directive group compiled by that step.
Later iterations judge each previous step envelope, producing good points, bad
points, concrete suggestions, compliance notes, constraint findings, and
directive-specific feedback. A step is rerun only when that diagnosis says
material improvement is worthwhile. The rerun is the same directive application
under the same directive contract; it is not a generic edit of the final output.

Sibling directives may be compiled in one step when they share the same parent
scope and nesting level, have non-overlapping spans, and do not depend on one
another's outputs. If grouping is ambiguous, WeaveMark splits them.

#### `@ask` as an `@iterate` prelude

WeaveMark has a small **prelude principle**: an enclosing directive may define
that a leading direct-child directive configures the enclosing operation while
keeping the child directive's own semantics unchanged. `@iterate` uses this
principle for a leading `@ask` wrapper.

```markdown
@iterate 5
  @ask clarifying question detail_level: 40%
    Draft an implementation prompt for the onboarding workflow.
    Clarify what matters most before expanding the prompt.
```

In this form:

- `@ask` means exactly what it always means: it clarifies its own body.
- The body of `@ask` is also the `@iterate` target.
- The Processor may apply that same `@ask` wrapper on every iteration, so
  clarification stays scoped to the current target.
- The leading `@ask` must be the only top-level child of `@iterate`.
- Later or nested `@ask` directives inside the target keep ordinary `@ask`
  behavior.

Constraint directives such as `@assert`, `@output`, and
`@structural_constraints` also work naturally inside `@iterate`: intermediate
constraint findings become judge feedback for later reruns, while final
constraint failures keep their normal severity behavior.

In CLI `--verbose` mode, WeaveMark renders the start of each iteration, the
effective turn budget, whether the `@ask` prelude is active, each judge verdict,
each improvement pass, and the final convergence or exhaustion result.

### Execution Engines (`--run`)

WeaveMark can **compile and execute** specs in one step. Use `--run` to invoke an execution engine that orchestrates multi-step strategies like Tree of Thought, Self-Consistency, and Reflection.

```bash
# Compile + execute with Tree of Thought
weavemark library builtin:catalog/executable/tree-of-thought-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/tree-of-thought-solver-example.json \
  --run --batch-only

# Self-consistency with 5 samples + majority vote
weavemark library builtin:catalog/executable/self-consistency-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/self-consistency-solver-example.json \
  --run --batch-only
```

`--run` uses the same input rules as compilation: missing values from the spec
are prompted in human-facing mode. Add `--batch-only` to make
execution strict and fail before compilation when any required input is missing.

**The `@execute` directive — bridging specification and execution.**
Most WeaveMark directives operate within the *specification* domain: they transform, compose, and annotate prompt text. The `@execute` directive is a special case — it bridges the spec domain with the *execution* domain, declaring *how* the runtime should orchestrate LLM calls rather than *what* the prompt says. It is metadata only and never modifies prompt content.

Today `@execute` selects multi-step reasoning strategies (Tree of Thought, Self-Consistency, Reflection), finite-state linguistic-machine execution with `fslm`, and the executable-document `weave` planner. In the future, it may be extended to declare other runtime concerns — caching policies, evaluation harnesses, or integration with external orchestration systems.

**Built-in engines** (backed by internal WeaveMark strategies):

| Engine | Strategy | Description |
|--------|----------|-------------|
| `single-call` | Default | One LLM call, returns result directly |
| `self-consistency` | N samples + vote | Runs the prompt N times, aggregates via majority vote or LLM judge |
| `tree-of-thought` | Generate → Evaluate → Synthesize | Explores multiple reasoning paths, evaluates, synthesizes the best |
| `reflection` | Generate → Critique → Revise | Iterative self-improvement loop until critique finds no issues |
| `fslm` | Finite-State Linguistic Machine | Runs an `ellements.fslm` machine and backs NL guards, invariants, actions, and outputs with named WeaveMark prompts |
| `weave` | Execute semantic functions | Validates and runs effectful semantic-function nodes |

**Multi-prompt promplets** use the `@prompt` directive to define stage-specific prompts:

```markdown
@execute tree-of-thought
  branching_factor: 3

You are a problem solver.  # ← shared context (prepended to all prompts)

@prompt generate
  Generate @{branching_factor} approaches to: @{problem}

@prompt evaluate
  Evaluate these candidates: @{candidates}

@prompt synthesize
  Elaborate the best approach: @{best_approach}
```

**Executable weave specs** collect execute-phase semantic-function calls into a
validated plan. The current built-in engine materializes the plan; authorized
host runtimes are responsible for actually running companion implementations bound with
`@bind`.

```markdown
@define fetch_asset_snapshot
  @phase execute
  @scope self
  @returns value
  @param ticker
    Ticker symbol.
  @effect finance_data read
  @body
    Fetch latest finance data for @{ticker}.

@bind finance_data language: python from: "./companions/market_data.py" symbol: fetch_asset_snapshot

@execute weave scheduler: graph-strict
  allow_effects: [finance_data]

@fetch_asset_snapshot ticker: "@{ticker}" as: asset_snapshot

Use @{asset_snapshot} in the report.
```

See [`promplets/experimental/weave/weave-market-snapshot.weavemark.md`](../promplets/experimental/weave/weave-market-snapshot.weavemark.md) for a fuller stock-learning example with finance, web-search, and web-crawl effects connected by dependency edges via `uses:`.

**FSLM specs** pair a normal WeaveMark prompt library with an `ellements.fslm` machine. The name is deliberately linguistic: WeaveMark supplies prompts for semantic guards, invariants, actions, and outputs while `ellements.fslm` supplies the graph and runtime contract. You can either reference an external YAML/JSON/Python machine or import the separate `fslm` module and declare the machine inline with WeaveMark sugar. Prompt names are validated before the first snapshot or LLM/tool call:

FSLM support requires `ellements[fslm]>=0.2.0`; the normal WeaveMark
installation declares and installs this compatible floor.

| Machine item | Required prompt key |
|--------------|---------------------|
| NL guard `has_answerable_question` | `guard.has_answerable_question` |
| NL invariant `answer_is_grounded` | `invariant.answer_is_grounded` |
| NL action `draft_answer` | `action.draft_answer` |
| NL output `final_answer` | `output.final_answer` |
| State metadata `prompt_key: state.triage` | that exact key |

Each prompt receives appended runtime context: machine, state, snapshot variables, event payload, candidate transitions, selected transition, previous actions/outputs, and compact step history. Machine specs can override a prompt name with `metadata.prompt_key`.

```markdown
@execute fslm
  machine: support-triage.fslm.yaml
  initial_event: user_message
  max_steps: 2
  prompt_contract: strict

@prompt guard.has_answerable_question
  Decide whether the event contains an answerable support question.

@prompt action.draft_answer
  Draft the support answer from the runtime context.

@prompt output.final_answer
  Return only the final user-facing answer.
```

Run the included demo with:

```bash
weavemark library builtin:experimental/fslm/fslm-support-triage \
  --run --config promplets/experimental/fslm/fslm-support-triage.runtime.json
```

Inline FSLM sugar keeps the machine next to its prompts:

```weavemark
@execute fslm
  machine: support_triage
  prompt_contract: strict

@machine support_triage initial: triage
  Prompt-backed support workflow.

  @state triage
    The request is being triaged.

    @transition gather_evidence target: triage internal: true external: false
      Search documentation because evidence is missing.

      @input query
        Search query.

      @guard needs_more_evidence
        Choose this transition only when evidence is insufficient.

      @action search_docs tool: search_docs
        Search docs using matching transition inputs.

      @action summarize_findings
        Summarize what was found.
```

The engine is event-driven: supply `initial_event` for one step or an ordered
`events` list for a bounded multi-step run. `internal:` and `external:` are
preserved as transition metadata for hosts and future runners; they do not
autonomously synthesize events. Guards are authoritative during transition
validation. Tool actions automatically receive transition `@input` values whose
names match the tool schema. See
[`promplets/experimental/fslm/fslm-support-triage-sugared.weavemark.md`](../promplets/experimental/fslm/fslm-support-triage-sugared.weavemark.md).

**Runtime config** is an optional, explicit host/deployment override. Use a
descriptive `.runtime.yaml` or `.runtime.json` file when a deployment needs
model routing, model residency policy, or runtime-only engine input that does
not belong in the promplet. Runtime config is never auto-discovered and does not
contain promplet variables:

```yaml
model: gpt-5.5
image_model: gpt-image-2
allowed_models: [gpt-5.5, gpt-4.1-mini, gpt-image-2]
prompts:
  evaluate:
    model: gpt-4.1-mini
```

Keep normal execution semantics in `@execute` and run inputs in
`--vars-file`. A variable named `model` is ordinary promplet data; it does not
silently change provider behavior. Use `--model`, `--image-model`, the Python
API, or an explicit runtime config for that.

For each provider call, precedence is: explicit CLI/API runtime override, named
prompt config, engine/stage config, the promplet's task/output declaration, then
the built-in default. `--model` and `--image-model` are explicit overrides; if
they are omitted, the runtime config remains authoritative. `allowed_models`
turns model residency into an enforced policy: execution fails before a provider
call if the resolved model is not listed. Compilation and execution use the same
text model by default.

**Custom engines**: implement the `Engine` protocol or extend `BaseEngine`:

```python
from weavemark.engines import Engine, ExecutionResult, resolve_engine

# Use a built-in engine
engine = resolve_engine("self-consistency")

# Or create your own (no inheritance required — duck typing works)
class MyEngine:
    async def execute(self, result, config=None):
        # Custom orchestration logic
        return ExecutionResult(output="...")
```

### Help

```bash
weavemark --help
```
