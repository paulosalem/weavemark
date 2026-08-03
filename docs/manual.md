# WeaveMark Processor Manual

Operational reference for installing, configuring, and running the WeaveMark
Processor. This document explains *how the tool works*; it does not argue for the
approach. For the notation itself, see the
[language reference](language-reference.md).

- [1. Installation](#1-installation)
- [2. Model providers](#2-model-providers)
- [3. Running the Processor](#3-running-the-processor)
- [4. Inputs and variables](#4-inputs-and-variables)
- [5. Outputs and artifacts](#5-outputs-and-artifacts)
- [6. Execution engines](#6-execution-engines)
- [7. The promplet library](#7-the-promplet-library)
- [8. Adding your own promplets](#8-adding-your-own-promplets)
- [9. Configuration files](#9-configuration-files)
- [10. Protections](#10-protections)
- [11. Logging](#11-logging)
- [12. Response cache](#12-response-cache)
- [13. Provenance, recording, and replay](#13-provenance-recording-and-replay)
- [14. Machine integration](#14-machine-integration)
- [15. Environment variables](#15-environment-variables)
- [16. Exit codes](#16-exit-codes)
- [17. Troubleshooting](#17-troubleshooting)

---

## 1. Installation

Requires Python 3.11, 3.12, or 3.13.

```bash
pip install weavemark                 # library and CLI
pip install "weavemark[examples]"     # plus finance/search integrations used by examples
pip install -e ".[dev]"               # from a source checkout, with test tooling
```

Verify:

```bash
weavemark --version
weavemark --env          # resolved config, model, cache dir, and library roots
```

`weavemark --env` is the fastest way to see what the Processor actually resolved
on this machine, and should be the first command run when diagnosing setup.

Full-resolution comic and storybook media in the repository use Git LFS. They are
not needed for installation; run `git lfs pull` in a clone to fetch them.

---

## 2. Model providers

Semantic compilation and execution call an LLM through
[LiteLLM](https://docs.litellm.ai/), so any provider LiteLLM supports may be
used. Credentials are read from that provider's usual environment variable:

```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

The default model is `gpt-5.6-terra`; every bundled example is exercised against
it. Override per invocation or in configuration:

```bash
weavemark spec.weavemark.md --model gpt-5.6-terra
weavemark spec.weavemark.md --image-model gpt-image-1
```

`--image-model` is never inferred from `--model`: image generation must be
selected explicitly.

Three operations need **no** provider credentials, because they perform no model
call: `--scan`, `--replay-run` (and `library … --replay`), and the library
management subcommands.

---

## 3. Running the Processor

```text
weavemark [SPEC_FILE] [OPTIONS]
```

`SPEC_FILE` is a `.weavemark.md` file. Omit it only with `--stdin` or
`--discover`.

### Modes

| Mode | Flag | Behavior |
|---|---|---|
| Guided | *(default)* | Compiles, prompting for missing variables, `@match` choices, and `@if` flags. |
| Batch | `--batch-only` | No prompts. Missing inputs fail before compilation. |
| Execute | `--run` | Compiles, then runs the result through the declared engine. |
| Implement | `--implement` | Compiles, then hands the spec to a programming agent. |
| Terminal UI | `--ui` | Input form with live preview, compose, and run. |
| Scan | `--scan` | Prints inputs and metadata as JSON. No LLM call. |
| Discover | `--discover` | Chat interface for finding a promplet. |

Reading from stdin implies batch behavior:

```bash
cat spec.weavemark.md | weavemark --stdin --output result.md
```

### Subcommands

```bash
weavemark library …      # run or browse promplets (see section 7)
weavemark implement …    # hand an already-compiled spec to a programming agent
```

---

## 4. Inputs and variables

A promplet declares inputs as `@{variable}`. Discover them without compiling:

```bash
weavemark spec.weavemark.md --scan
```

Supply values by flag, by file, or interactively:

```bash
weavemark spec.weavemark.md --var topic="supply chains" --var depth=3
weavemark spec.weavemark.md --vars-file inputs.json
```

`--var` is repeatable and overrides `--vars-file`. Booleans accept
`true`/`false`, `yes`/`no`, or `1`/`0`. The vars file may be JSON or YAML and
must contain a single object. In guided mode, any value still missing is
prompted for; in `--batch-only` the run fails first.

Keep promplet inputs in `--vars-file`. `--config` is for runtime concerns
(model routing, engine host settings), not inputs.

---

## 5. Outputs and artifacts

By default the compiled prompt goes to stdout, so it composes with other tools:

```bash
weavemark spec.weavemark.md --batch-only | pbcopy
```

| Flag | Effect |
|---|---|
| `--output FILE` | Write the primary compiled prompt to `FILE`. `@emit` siblings land beside it. |
| `--output-dir DIR` | Write everything into `DIR`. Primary becomes `<spec-stem>.md`. |
| `--show-output` | Print to stdout *and* write files. |
| `--no-file-summary` | Suppress per-file "written" messages. |
| `--open` | Open the produced artifacts in the default application. |
| `--format FORMAT` | Override the `@compile` format (default: markdown). |
| `--trace-output FILE` | With `--run`, write a readable Markdown execution trace. |

`--output` and `--output-dir` are mutually exclusive. With `--run`, `--open`
opens every successful `@package` artifact; otherwise it opens the compiled
output, writing it to a temporary file when no output path was given.

stdout carries data; progress and diagnostics go to stderr; exit codes are
meaningful. `--verbose` adds a step-by-step view plus a closing footer with token
counts, prompt-cache hits, and provider-reported cost.

---

## 6. Execution engines

`--run` executes the compiled prompt through the engine named by `@execute`, or
one supplied via `--config`. Built-in engines:

| Name | Behavior |
|---|---|
| `single-call` | One model call. |
| `self-consistency` | N samples, then majority vote. |
| `tree-of-thought` | Branching search over intermediate thoughts. |
| `simplified-tree-of-thought` | Cheaper single-pass variant. |
| `reflection` | Draft, critique, revise. |
| `chain` | Sequential `@prompt` stages, optionally repeated. |
| `collaborative` | Multiple cooperating personas. |
| `fslm` | Finite-state language machine (see `@machine`). |
| `functional` | Capability graph with declared dependencies. |

A custom engine is selected by fully-qualified Python path — no inheritance is
required, duck typing suffices:

```markdown
@execute my_package.engines.CustomEngine
```

---

## 7. The promplet library

WeaveMark ships a corpus of reusable promplets and resolves four kinds of root,
**in this precedence order**:

| Order | Kind | Location |
|---|---|---|
| 1 | `project` | Nearest `promplets/` directory, searching upward from the working directory. |
| 2 | `user` | `~/.weavemark/promplets` |
| 3 | `extra` | `--library-dir DIR` (repeatable), `library_dirs` in config, then `WEAVEMARK_LIBRARY_PATH`. |
| 4 | `builtin` | The corpus bundled inside the installed package. |

A bare target name is searched in that order, so a project promplet shadows a
built-in of the same name. Force one source with an explicit prefix:

```bash
weavemark library market-snapshot                    # search all roots in order
weavemark library builtin:catalog/standalone/ai-kanban-board
weavemark library project:my-promplet
weavemark library user:my-promplet
weavemark library extra:my-promplet
weavemark library module:weavemark.std.reasoning.base_analyst
```

Inspect and browse:

```bash
weavemark library sources                       # effective roots, in precedence order
weavemark library list                          # everything
weavemark library list finance --collection domains
weavemark library list --source builtin --kind fragment --json
weavemark library show builtin:catalog/standalone/ai-kanban-board
```

`list` filters by `--source` (`all`, `project`, `user`, `extra`, `builtin`),
`--collection` (`stdlib`, `domains`, `catalog`, `tutorials`, `experimental`,
`personal`), and `--kind` (`definition`, `fragment`, `standalone`, `executable`,
`tutorial`). The query matches path, title, module, variables, and engine.

Running a library promplet directly accepts the same options as a file path:

```bash
weavemark library market-snapshot --scan
weavemark library market-snapshot --replay --verbose --open
weavemark library ai-kanban-board --var project_name=Atlas --output spec.md
```

`--replay` re-runs a recorded compilation stored beside the promplet: no API key,
no network. Only promplets that ship a replay bundle support it.

---

## 8. Adding your own promplets

### Per project

Create a `promplets/` directory at or above your working directory. Anything in
it is discoverable by bare name and takes precedence over built-ins:

```text
my-project/
  promplets/
    house-style.weavemark.md
    reports/weekly.weavemark.md
```

```bash
weavemark library house-style --scan
```

### Per user

Put promplets in `~/.weavemark/promplets` to make them available in every
project.

### Elsewhere

```bash
weavemark library my-promplet --library-dir ~/work/shared-promplets
export WEAVEMARK_LIBRARY_PATH="$HOME/work/shared:$HOME/other"   # os.pathsep-separated
```

Or persist it in `weavemark.json`:

```json
{ "library_dirs": ["~/work/shared-promplets"] }
```

### Starting from the built-in corpus

```bash
weavemark library copy ./weavemark-promplets
```

This writes the complete built-in corpus to a directory you own, which is the
easiest way to adapt an existing fragment rather than write one from scratch.

### Making a promplet importable as a module

Give the file a `@module` name, then import it by dotted path from anywhere:

```markdown
@module acme.style.house_voice
```

```markdown
@refine module:acme.style.house_voice
```

---

## 9. Configuration files

Configuration lives in files named **`weavemark.json`** at three levels, merged
in this order (later overrides earlier):

| Level | Location |
|---|---|
| Global (system) | macOS `/Library/Application Support/WeaveMark/weavemark.json` · Linux `/etc/weavemark/weavemark.json` · Windows `%PROGRAMDATA%\WeaveMark\weavemark.json` |
| User | macOS `~/Library/Application Support/WeaveMark/weavemark.json` · Linux `${XDG_CONFIG_HOME:-~/.config}/weavemark/weavemark.json` · Windows `%APPDATA%\WeaveMark\weavemark.json` |
| Project | `weavemark.json` in the working directory or an ancestor |

Override the global and user paths with `WEAVEMARK_GLOBAL_CONFIG` and
`WEAVEMARK_USER_CONFIG`. `weavemark --env` prints which files were found.

**Projects cannot escalate privilege.** A project config may tighten protections,
reduce logging, and disable the cache, but it cannot loosen protections, enable
logging surfaces the user disabled, redirect log or cache directories, or
re-enable a disabled cache. This keeps cloning an untrusted repository from
silently changing your machine's safety posture.

Top-level keys:

```json
{
  "formats": {},
  "modules": [],
  "fragments": {},
  "library_dirs": [],
  "implementation": {},
  "protections": {},
  "log": {},
  "cache": {}
}
```

| Key | Purpose |
|---|---|
| `formats` | Named output formats selectable via `@compile format:` or `--format`. |
| `modules` | Modules imported into every compilation by default. |
| `fragments` | Aliases mapping short names to fragment paths. |
| `library_dirs` | Additional promplet-library roots. |
| `implementation` | Programming-agent profiles for `--implement`. |
| `protections` | Capability policy (section 10). |
| `log` | Debug logging (section 11). |
| `cache` | Local response cache (section 12). |

---

## 10. Protections

Protections are **enabled by default** and gate local reads and writes,
downloads, Python execution, and external processes. They reduce common risks
but are **not an operating-system sandbox**: do not run untrusted promplets.

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

Each capability takes `allow`, `confirm`, or `deny`. Under `confirm` the
Processor asks interactively; in `--batch-only` there is nobody to ask, so the
operation is denied and the run fails with an explanatory message naming the
policy key. Grant the capability explicitly, or add a `readRoots`/`writeRoots`
entry, rather than disabling protections wholesale.

A project `weavemark.json` may only *tighten* protections. It cannot disable
them, grant roots, raise download limits, or add inherited environment
variables.

`--no-protections` disables every check for a single invocation. Use it only for
promplets you have read and trust.

The Processor automatically authorizes the paths it was asked to write —
`--output`, `--output-dir`, `--record-run`, and the temporary file created by
`--open` — so ordinary output does not require configuration.

---

## 11. Logging

Logging is on by default and writes to `~/.weavemark/logs`. Binary and base64
payloads are omitted; everything else is retained.

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

`llmRequests` stores the exact model request, which inherently contains any
variable values interpolated into it. **Disable `llmRequests` when variable
values must not appear on disk** — disabling `variables` alone is not enough.

Process-level overrides: `WEAVEMARK_LOG=0`, `WEAVEMARK_LOG_DIR`,
`WEAVEMARK_LOG_LEVEL`. `--help` and `--version` never initialize logging.

---

## 12. Response cache

Identical API calls are cached locally, so re-running the same prompt, model,
tools, and parameters costs nothing. Text calls use LiteLLM's disk cache; image
generation and edits use a content-addressed image cache. WeaveMark requests
durable base64 responses only from image operations that support that parameter;
image-edit providers use their native response encoding. Default directory:
`~/.weavemark/cache`.

```json
{ "cache": { "enabled": true, "directory": null } }
```

Set `WEAVEMARK_CACHE=0` to disable for one process, or `WEAVEMARK_CACHE_DIR` to
relocate it. Cache hits appear as `LOCAL cache used` in verbose output. This is
distinct from provider-side prompt caching, which is reported separately in the
usage footer.

---

## 13. Provenance, recording, and replay

```bash
weavemark spec.weavemark.md --provenance run.json
weavemark spec.weavemark.md --record-run ./bundle
weavemark spec.weavemark.md --replay-run ./bundle
```

- **`--provenance FILE`** writes a manifest: hashes, lineage, latency, token
  usage, and provider-reported cost. It contains no prompt text.
- **`--record-run DIR`** writes a replayable bundle containing full LLM requests
  and responses. **It may therefore contain sensitive content** — review before
  sharing or committing.
- **`--replay-run DIR`** re-runs the recording strictly offline. It verifies the
  source hash, variable hash, compiler prompt hash, response-schema hash, compile
  configuration, module and resource hashes, and every recorded call hash. Any
  mismatch, or any attempt to reach the network, fails the run.
- Verbose replay distinguishes compilation activity from the retained original
  execution. Compile-only recordings report `Compilation tool calls`; retained
  runs report recorded execution steps, effect calls, underlying provider tool
  calls, and model calls when those counters are present in `original_run.activity`.

A bundle may also retain a snapshot of the final artifacts from the execution
that followed compilation. Each retained artifact declares a safe relative path,
byte count, and SHA-256 hash. After compilation validates, replay verifies those
files. With no output option it sends the recorded primary output to stdout;
`--output`, `--output-dir`, or `--open` restores all retained artifacts
byte-for-byte. `--open` then opens the bundle's declared final artifact. Market
Snapshot, for example, restores `execution-output.md`, `execution-trace.md`, and
`market-dashboard.html`, then opens the HTML dashboard.

Retained artifacts replay the *result* of effects; they do not call live finance,
search, Python, or packaging effects again. A fresh compilation or execution of
your own input still requires the appropriate model provider and capabilities.

`--record-run` and `--replay-run` are mutually exclusive. `--replay-run` cannot
be combined with `--run` or `--implement`, because it consumes recorded responses
and retained artifacts rather than performing a new live execution.

---

## 14. Machine integration

For GUIs, editors, and workflow runners, use the structured event stream instead
of parsing terminal output:

```bash
weavemark library market-snapshot --vars-file inputs.json --run \
  --output-dir outputs/market \
  --events-jsonl outputs/market/events.jsonl
```

Each JSON Lines record carries an ISO timestamp, a monotonic sequence number, a
type, an optional phase, and structured data including absolute artifact and
package paths. Use `-` to stream to stdout.
During replay, the composition `done` record includes `recorded_activity` when
the bundle declares `original_run.activity`; its counters describe the retained
execution rather than the offline compilation pass.

`--interaction-stdin jsonl` makes the channel bidirectional: the Processor emits
interaction requests (missing variables, protection confirmations) on the event
stream and reads scoped responses from stdin. It requires `--events-jsonl` and
cannot be combined with `--stdin`. An invalid, closed, or timed-out interaction
stream denies the requested capability rather than hanging.

The Python API is documented separately in [python-api.md](python-api.md).

---

## 15. Environment variables

| Variable | Effect |
|---|---|
| `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, … | Provider credentials, as required by LiteLLM. |
| `WEAVEMARK_GLOBAL_CONFIG` | Override the global `weavemark.json` path. |
| `WEAVEMARK_USER_CONFIG` | Override the user `weavemark.json` path. |
| `WEAVEMARK_LIBRARY_PATH` | Additional library roots, separated by `os.pathsep`. |
| `WEAVEMARK_CACHE` | `0` disables the response cache for this process. |
| `WEAVEMARK_CACHE_DIR` | Override the cache directory. |
| `WEAVEMARK_LOG` | `0` disables logging for this process. |
| `WEAVEMARK_LOG_DIR` | Override the log directory. |
| `WEAVEMARK_LOG_LEVEL` | Log level, e.g. `DEBUG`. |
| `WEAVEMARK_RESPONSES_API` | Force the Responses API on or off for providers that support both. |
| `WEAVEMARK_REASONING_EFFORT` | Reasoning-effort hint for models that accept one. |

---

## 16. Exit codes

| Code | Meaning |
|---|---|
| `0` | Success. |
| `1` | Compilation, execution, or output error — including a required input missing under `--batch-only`. Diagnostics go to stderr. |
| `2` | Invalid CLI usage: conflicting or unsupported flag combinations. |

---

## 17. Troubleshooting

**"No model provider configured."** Export the provider's API key. Confirm with
`weavemark --env`. `--scan` and `--replay` need no key at all.

**A promplet name resolves to the wrong file.** Precedence is project → user →
extra → builtin. Run `weavemark library sources` to see the effective roots, and
use an explicit `builtin:` / `project:` prefix to disambiguate.

**An operation is denied in batch mode.** A `confirm` capability cannot prompt
when nobody is present. The error names the policy key; grant that capability in
`weavemark.json` or add the path to `readRoots`/`writeRoots`.

**Replay fails with a hash mismatch.** The source, variables, modules, or
compiler prompt changed since recording. Re-record with `--record-run`.

**Results are unexpectedly identical.** The local cache is returning a stored
response. Set `WEAVEMARK_CACHE=0` to force fresh calls.

**Variable values must not reach disk.** Set `log.llmRequests` to `false`;
`log.variables` alone does not cover values interpolated into the request.
