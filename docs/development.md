# Development notes

Use this page as a maintainer map: it points to the editor extension, the main
runtime modules, the example/spec layout, and the logging path for inspecting
WeaveMark Processor behavior.

## VS Code extension

A syntax highlighting extension for `.weavemark.md` files is included in [`vscode-extension/`](../vscode-extension/). It provides:

- Directive, variable, match-case, and escape highlighting
- Two color themes (WeaveMark Dark and WeaveMark Light)

**Quick install:**

```bash
python scripts/install_vscode_extension.py
```

The installer checks the extension, detects local editor variants, and performs
an atomic owned copy by default. Use `--mode link` for live development or
`--target code-insiders` for one editor. Then reload VS Code. See
[`vscode-extension/README.md`](../vscode-extension/README.md) for details.

## Architecture

The most useful first reads are:

- `src/weavemark/app.py` for the WeaveMark Processor CLI surface;
- `src/weavemark/compilation/` for deterministic parsing, validation, and
  composition helpers;
- `src/weavemark/engines/` for prompt execution strategies;
- `src/weavemark/prompts/weavemark.system.md` for the formal language contract.

### Reference authority

WeaveMark has an explicit authority hierarchy:

1. `src/weavemark/prompts/weavemark.system.md` is the canonical source of truth
   for the WeaveMark language and its semantic compilation contract.
2. `docs/weavemark.ebnf` is a deterministic engineering mirror derived from the
   system prompt. When they disagree, update the EBNF unless the language itself
   is intentionally changing.
3. Executable product surfaces are authoritative for themselves:
   `create_parser()` / `create_implement_parser()` define the CLI;
   `src/weavemark/__init__.py` and public signatures define the Python API;
   typed settings and engine registries define their configuration surfaces.
4. README, tutorials, HTML reference pages, examples, editor metadata, and
   prose tables are downstream explanations. They must be updated from the
   authorities above and never override them.

For a language change, edit the system prompt first, update its EBNF/schema
mirror, then update deterministic implementation and downstream documentation.
Run `python scripts/check_grammar_sync.py` and the reference-authority tests.

```text
weavemark/
├── pyproject.toml          # Package configuration & dependencies
├── examples/               # Self-contained example folders with run.*, inputs/, outputs/
├── studies/                # Repository-only research artifacts and comparison runs
├── src/weavemark/         # Python package
│   ├── app.py              # CLI entry point (guided, batch, run, implement, UI, discovery)
│   ├── controller.py       # WeaveMarkController — drives the LLM composition loop
│   ├── compilation/        # Typed result/diagnostic/provenance contracts + helpers
│   ├── discovery/          # Spec discovery configuration and TUI integration
│   ├── engines/            # Execution engines (thin wrappers over internal strategies)
│   │   ├── base.py         # Engine protocol, BaseEngine, RuntimeConfig
│   │   ├── registry.py     # resolve_engine() — built-in names + custom import paths
│   │   ├── single_call.py  # Default: one LLM call
│   │   ├── self_consistency.py  # N samples + majority vote / LLM judge
│   │   ├── tree_of_thought.py   # Generate → evaluate → synthesize
│   │   └── reflection.py   # Generate → critique → revise loop
│   └── prompts/            # System prompt shipped with the package
├── promplets/              # Canonical built-in promplet library
│   ├── stdlib/
│   │   ├── prelude/        # Definition modules loaded by default
│   │   ├── definitions/    # Stable definition-first modules
│   │   └── fragments/      # Stable body-bearing module promplets
│   ├── domains/            # Domain-specific reusable modules/fragments
│   │   ├── creative/
│   │   ├── finance/
│   │   ├── game-design/
│   │   ├── product/
│   │   ├── programming/
│   │   └── research/
│   ├── catalog/
│   │   ├── standalone/     # Complete compile-oriented entrypoints
│   │   └── executable/     # Engine/tool/collaborative workflows
│   ├── tutorials/
│   └── experimental/       # FSLM, weave, and study experiments
├── studies/
│   ├── controlled-studies/
│   └── examples-studies/
├── tests/                  # Test suite
└── vscode-extension/       # Syntax highlighting for .weavemark.md files
```

The controller uses `LLMClient.complete_with_tools()` — a lightweight multi-turn
tool-calling loop built on LiteLLM (no OpenAI Agents SDK dependency). The LLM
reads the promplet, calls `read_file` when encountering
`@refine <reference>`, and calls `log_transition` to record composition steps.
Directives are evaluated inside-out through bounded composition passes until the
promplet is resolved or the budget is exhausted.

`compilation/result.py` owns the stable compilation result contract,
`compilation/diagnostics.py` owns user-facing diagnostics, and
`compilation/provenance.py` owns optional manifest/record/replay behavior. This
keeps the controller focused on orchestration while preserving the hybrid
structural-plus-LLM compilation model.

### Repository artifact policy

Run `python scripts/check_repository_hygiene.py` before release commits. The
gate inspects exactly the tracked and untracked non-ignored files that could
enter a commit, rejects caches/build outputs/packages, caps ordinary Git at
10 MiB per file and 50 MiB total, and caps curated Git LFS assets at 100 MiB per
file and 512 MiB total.

Git LFS is reserved for full-resolution PNG/PDF outputs under the illustrated
storybook and comic examples. Site previews, source, tests, prompts, text
outputs, and normal documentation stay in ordinary Git. Dependency trees,
caches, and generated package archives belong in neither.

### Release automation

Ordinary pushes to `main` run CI and deploy GitHub Pages; they do not publish a
package. A pushed `vMAJOR.MINOR.PATCH` tag triggers
`.github/workflows/release.yml`, which:

1. requires the tagged commit to belong to `main`;
2. validates all version authorities and the changelog;
3. runs the test and repository gates;
4. builds and checks the wheel and source distribution;
5. publishes to PyPI with Trusted Publishing (OIDC);
6. creates the matching GitHub release and attaches both distributions.

The workflow carries no PyPI API token. Configure its trust relationship once:

1. In the GitHub repository, create an environment named `pypi`. Optional
   required reviewers can provide a manual publication approval.
2. In the `weavemark` project on PyPI, open **Publishing**, add a GitHub trusted
   publisher, and set:
   - owner: `paulosalem`
   - repository: `weavemark`
   - workflow: `release.yml`
   - environment: `pypi`

Prepare a release by synchronizing the same version in:

- `pyproject.toml`;
- the source-checkout fallback in `src/weavemark/version.py`;
- `vscode-extension/package.json`;
- the wheel-version assertion in `.github/workflows/ci.yml`.

Move every entry from `## Unreleased` into a non-empty
`## X.Y.Z - YYYY-MM-DD` section, leaving `Unreleased` empty. Validate locally:

```bash
python scripts/check_release.py --tag vX.Y.Z --notes /tmp/release-notes.md
python -m build
twine check --strict dist/*
```

After the release commit is on `main` and CI is green:

```bash
git tag -a vX.Y.Z -m "WeaveMark X.Y.Z"
git push origin vX.Y.Z
```

PyPI versions are immutable. If publication succeeds but the later GitHub
release job fails, use GitHub Actions' **Re-run failed jobs** action so the
successful PyPI job is not repeated. The GitHub job recovers an existing draft,
replaces its assets, and explicitly publishes it. Do not rerun the entire
workflow after PyPI has accepted the version.

Publishing the VS Code extension to its marketplace remains a separate process;
the release contract only verifies that its version matches.

### Debug logging

Logging is enabled by default. Application events and policy-filtered LLM JSONL
records are written under the configured WeaveMark log directory. Normal text,
variables, responses, tools, usage, and errors remain available while binary
payloads are omitted by default.

```bash
weavemark library market-research-brief \
  --vars-file examples/batch-example-runs/static-prompts/inputs/market-research-example.json \
  --batch-only --verbose
```

Use the `log` object in `weavemark.json` to independently control application
events, CLI arguments, variables, requests, responses, tool data, usage, errors,
binary payloads, rotation, and retention. See the
[Processor reference](usage-reference.md#configurable-debug-logging).
