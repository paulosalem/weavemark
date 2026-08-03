# Python API

WeaveMark is also a first-class Python library for apps that want to keep
their prompts as promplets instead of shelling out to the WeaveMark Processor CLI.
The public API is async because deterministic structural helpers handle many promplets locally,
but semantic directives may still require the LLM reference compilation path.

```python
from weavemark import (
    bundled_promplet,
    compile_file,
    compile_text,
    execute_file,
    execute_text,
    read_bundled_promplet,
)
```

`weavemark.__version__` reports the installed processor package version;
`weavemark.LANGUAGE_VERSION` reports the current language contract.

Use the Python API when the host application should own input collection,
storage, UI, logging, or runtime execution. Use the WeaveMark Processor CLI when
you want a Unix-style command for files, scripts, demos, or CI.

| Function | Use when | Returns |
|----------|----------|---------|
| `compile_text(source, variables=None, ...)` | Your app already has WeaveMark source in memory, from a database, package resource, editor buffer, or generated document | `CompositionResult` |
| `compile_file(path, variables=None, ...)` | Your app stores prompts as `.weavemark.md` files on disk | `CompositionResult` |
| `execute_text(source, variables=None, ...)` | You want to compile in-memory source and immediately run it through an engine | `WeaveMarkRunResult` |
| `execute_file(path, variables=None, ...)` | You want to compile a spec file and run it through an engine | `WeaveMarkRunResult` |

## Read the built-in promplet library

The canonical corpus remains visible at the repository root under `promplets/`.
Wheel builds map that same tree into `weavemark/promplets`, so installed
applications can read it without a repository checkout and without maintaining
a duplicate source copy.

```python
from weavemark import bundled_promplet, iter_bundled_promplets, read_bundled_promplet

paths = list(iter_bundled_promplets())
resource = bundled_promplet("catalog/standalone/prompt-refactoring-pipeline.weavemark.md")
source = read_bundled_promplet(
    "stdlib/fragments/reasoning/chain-of-thought.weavemark.md"
)
```

The returned resource implements `importlib.resources.abc.Traversable`. When an
external tool requires a real filesystem path, use the context manager:

```python
from weavemark import bundled_promplet_path

with bundled_promplet_path(
    "catalog/standalone/prompt-refactoring-pipeline.weavemark.md"
) as path:
    print(path)
```

The CLI's `weavemark library` command combines these bundled resources with the
project `./promplets`, user `~/.weavemark/promplets`, configured `library_dirs`,
and `--library-dir`. Project and user sources precede built-ins for bare
references; `project:`, `user:`, `extra:`, `builtin:`, and `module:` are explicit.

## Compile a promplet file

```python
import asyncio
from weavemark import bundled_promplet_path, compile_file


async def main() -> None:
    with bundled_promplet_path(
        "catalog/standalone/ai-kanban-board.weavemark.md"
    ) as source:
        result = await compile_file(source)
    if result.errors:
        raise RuntimeError(result.errors)

    print(result.composed_prompt)
    print(result.prompts)   # named @prompt blocks
    print(result.emits)     # @emit and role-tagged prompt artifacts
    print(result.tools)     # @tool schemas
    print(result.bindings)  # @bind companion declarations


asyncio.run(main())
```

`compile_file()` uses the promplet file's parent directory as `base_dir`, so
relative `@refine`, `@embed`, and `@image` paths work exactly as they do in the
WeaveMark Processor. It also discovers `weavemark.json` from that location,
including configured formats and implementation profiles.

## Compile in-memory WeaveMark source

```python
import asyncio
from pathlib import Path
from weavemark import compile_text

async def main() -> None:
    source = """
@promplet version: 0.9 surface: markdown

# Support answer

Reply to @{question} in a concise, kind voice.
"""

    result = await compile_text(
        source,
        {"question": "How do modules work?"},
        base_dir=Path("prompts"),  # controls relative refs and config lookup
    )
    print(result.composed_prompt)


asyncio.run(main())
```

Use `compile_text()` when promplets live outside regular files: bundled package
resources, notebooks, web editors, databases, or generated WeaveMark programs.

## Control compilation

```python
import asyncio
from weavemark import CompileOptions, bundled_promplet_path, compile_file

async def main() -> None:
    with bundled_promplet_path("tutorials/adaptive-tutor.weavemark.md") as source:
        result = await compile_file(
            source,
            variables={
                "topic": "battery recycling",
                "learner_context": "a product manager",
                "learning_goal": "explain the main recovery tradeoffs",
                "learner_level": "beginner",
                "include_practice": True,
            },
            options=CompileOptions(
                model="gpt-5.6-terra",
                max_iterations=12,
                use_structural_helpers=True,
                max_effect_rounds=6,
                max_effect_questions=20,
                max_iterate_turns=6,
            ),
        )
    print(result.composed_prompt)


asyncio.run(main())
```

Most practical specs should compile deterministically through structural
helpers. If a spec uses directives that require semantic interpretation,
WeaveMark falls back to the LLM reference compilation path with the model
settings above.

## Answer compile-time `@ask` questions

Promplets that import `@ask` can ask host-mediated questions while they compile.
Provide `ask_handler` to answer those questions from your app:

```python
import asyncio
from weavemark import AskPrompt, bundled_promplet_path, compile_file


async def answer_ask(prompt: AskPrompt) -> str:
    print(prompt.question)
    return "Predict how one gradient update changes a parameter."


async def main() -> None:
    with bundled_promplet_path(
        "tutorials/adaptive-tutor-guided.weavemark.md"
    ) as source:
        result = await compile_file(
            source,
            variables={
                "topic": "gradient descent",
                "learner_context": "a designer learning machine-learning basics",
                "learner_level": "beginner",
                "include_practice": True,
            },
            ask_handler=answer_ask,
        )
    print(result.composed_prompt)


asyncio.run(main())
```

`@ask` is iterative. A compile round can ask several questions, return
intermediate XML that still contains `@ask`, then run another round after more
of the target body has been transformed. `CompileOptions.max_effect_rounds` and
`CompileOptions.max_effect_questions` bound that process. If a spec contains an
active `@ask` and no `ask_handler` is supplied, compilation returns an error
instead of silently guessing.

## Bound `@iterate` improvement loops

Promplets that use standard-library `@iterate` compile a target body through
inside-out directive-application steps. Iteration 0 records a compilation trace;
later iterations judge each prior step envelope and rerun only the directive
application(s) whose judge feedback says material improvement is worthwhile.

```python
import asyncio
from weavemark import CompileOptions, bundled_promplet_path, compile_file


async def main() -> None:
    with bundled_promplet_path("tutorials/iterate-onboarding.weavemark.md") as source:
        result = await compile_file(
            source,
            options=CompileOptions(max_iterate_turns=4),
        )
    print(result.composed_prompt)


asyncio.run(main())
```

The optional positional integer on `@iterate` is capped by
`CompileOptions.max_iterate_turns`. If the effective improvement budget is
exhausted while any step still needs improvement, compilation returns the best
available result with a warning. Runs expose `result.compilation_trace` and
`result.iteration_history` for hosts that want to render progress, inspect step
envelopes, or diagnose why a step was rerun.

## Render WeaveMark Processor-style output

The library result exposes structured fields directly. When you need the same
primary output shape as the WeaveMark Processor, use `format_compiled_output()`:

```python
import asyncio
from weavemark import bundled_promplet_path, compile_file, format_compiled_output


async def main() -> None:
    with bundled_promplet_path(
        "tutorials/language-learning-goal-plan.weavemark.md"
    ) as source:
        compiled = await compile_file(source)
    markdown = format_compiled_output(compiled)
    data_json = format_compiled_output(compiled, "json")
    mustache = format_compiled_output(compiled, "mustache")
    raw_response = compiled.raw_response
    print(markdown, data_json, mustache, raw_response, sep="\n---\n")


asyncio.run(main())
```

Custom output formats and aliases are resolved through `weavemark.json`; pass
`base_dir="prompts"` or a loaded settings object to
`format_compiled_output()` when using them.

## Execute a spec

`execute_file()` compiles first, then runs the compiled prompts through an
engine. It raises `WeaveMarkCompilationError` if compilation produced errors,
so execution never proceeds with an invalid spec.

```python
import asyncio
from weavemark import RuntimeConfig, bundled_promplet_path, execute_file


async def main() -> None:
    with bundled_promplet_path("tutorials/api-execution.weavemark.md") as source:
        run = await execute_file(
            source,
            variables={
                "topic": "whether to expand a pilot",
                "context": (
                    "The pilot met its quality target, but support load is uncertain."
                ),
            },
            runtime_config=RuntimeConfig(
                model="gpt-5.6-terra",
                allowed_models=("gpt-5.6-terra",),
            ),
        )
    print(run.output)            # shortcut for run.execution.output
    print(run.engine)            # selected engine name
    print(run.compiled.prompts)  # compiled prompt set passed to the engine
    print(run.execution.steps)   # engine step trace


asyncio.run(main())
```

Runtime config can be passed as:

- a `RuntimeConfig` object;
- a mapping with provider, policy, prompt-routing, and engine override fields;
- a path to a `.json`, `.yaml`, or `.yml` runtime config file.

Pass promplet inputs through the `variables` argument. Runtime config does not
contain variables; it is reserved for optional host/deployment overrides.

## Custom engines and callbacks

Apps can use built-in engines by name or pass an object implementing the
`Engine` protocol:

```python
import asyncio
from weavemark import bundled_promplet_path, execute_file
from weavemark.engines import ExecutionResult


class MyEngine:
    async def execute(self, result, config=None, on_step=None):
        # Use result.prompts, result.tools, result.bindings, or result.execution.
        return ExecutionResult(output=result.composed_prompt.upper())


async def main() -> None:
    with bundled_promplet_path(
        "tutorials/language-learning-goal-plan.weavemark.md"
    ) as source:
        run = await execute_file(source, engine=MyEngine())
    print(run.output)


asyncio.run(main())
```

Use `on_event` to observe compilation events (`composing`, `transition`,
`issue`, `done`) and `on_step` to observe execution-engine steps. Advanced
integrations can pass a custom `ellements` `LLMClient` through the `client`
parameter for compilation.

## Optional provenance and replay

```python
import asyncio
from pathlib import Path

from weavemark import ProvenanceOptions, bundled_promplet_path, compile_file


async def main() -> None:
    with bundled_promplet_path(
        "tutorials/language-learning-goal-plan.weavemark.md"
    ) as source:
        result = await compile_file(
            source,
            provenance=ProvenanceOptions(
                record_dir=Path("outputs/language-goal-run"),
            ),
        )
        replayed = await compile_file(
            source,
            provenance=ProvenanceOptions(
                replay_dir=Path("outputs/language-goal-run"),
            ),
        )
    assert replayed.composed_prompt == result.composed_prompt


asyncio.run(main())
```

Use `manifest_path=` for metadata and hashes without full request/response
recording. Run recordings are sensitive and strict replay never falls back to a
live provider.

## Diagnostics and errors

Compilation returns diagnostics instead of throwing for normal spec problems:

```python
import asyncio
from weavemark import bundled_promplet_path, compile_file


async def main() -> None:
    with bundled_promplet_path(
        "catalog/standalone/ai-kanban-board.weavemark.md"
    ) as source:
        compiled = await compile_file(source)
    for diagnostic in compiled.diagnostics:
        print(diagnostic["type"], diagnostic["message"])


asyncio.run(main())
```

Execution raises `WeaveMarkCompilationError` when the compile phase has errors;
the exception carries the failed `CompositionResult` as `exc.result`.
