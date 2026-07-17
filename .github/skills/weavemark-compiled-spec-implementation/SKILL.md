---
name: weavemark-compiled-spec-implementation
description: |
  Implement compiled WeaveMark software specifications, including game studies,
  by handing the compiled spec to GitHub Copilot CLI headless mode in a fresh
  implementation workspace.
when_to_use: |
  - The user asks to implement a compiled WeaveMark software spec
  - The user asks to run the optional implementation step for an example or study
  - The user asks to turn a game study's compiled prompt into a runnable game
  - The user wants behavioral evidence from a WeaveMark software-spec study
---

# WeaveMark Compiled-Spec Implementation

Use this skill when a task moves beyond compiling or inspecting a promplet
software specification and asks for an actual implementation. The canonical
path is a two-stage handoff:

1. WeaveMark compiles a `.weavemark.md` source into an implementation-ready
   Markdown spec.
2. GitHub Copilot CLI runs headlessly in a fresh implementation directory and
   builds code from that compiled spec.

Keep these stages separate. Compilation is a reproducible WeaveMark artifact;
implementation is a mutating programming-agent run whose output depends on agent
version, model, date, tools, and validation.

## Canonical command

Use the first-class CLI instead of hand-writing a Copilot command:

```bash
weavemark implement COMPILED_SPEC.md --name <implementation-name>
```

Example for a game study:

```bash
weavemark implement \
  studies/games/orbital-drift-racing-ablation-study/outputs/compiled-prompts/02-treatment-promplet-orbital-drift.md \
  --name orbital-drift
```

Example for the software-spec README example:

```bash
weavemark implement \
  outputs/examples/compiled-prompt-snapshots/passive-income-android-app/compiled-prompt.md \
  --name passive-income-android-app
```

The command copies the compiled spec to a name-derived snapshot and
`compiled-spec.md`, writes the exact implementation prompt to a name-derived
artifact and `implementation-prompt.md`, runs the selected headless profile from
the implementation directory, and records a manifest plus transcript path.

## Workflow

1. **Find or create the compiled spec.**
   - Prefer an existing checked-in compiled output under `examples/**/outputs/`
     or `studies/**/outputs/compiled-prompts/`.
   - If a compiled output is missing or stale, run the documented `weavemark`
     compile command first and save the output under the example or study's
     `outputs/` folder.
   - For semantic compilation, load the user's local LLM environment before live
     runs:

     ```bash
     source ~/.zshenv 2>/dev/null || true
     source ~/.zshrc 2>/dev/null || true
     ```

2. **Use a fresh implementation workspace.**
   - Default to `outputs/implementations/<name>`.
   - Do not implement inside `examples/`, `studies/`, `promplets/`, or source
     directories.
   - Do not use `--reuse-dir` unless the user explicitly wants to continue a
     previous implementation run.

3. **Run the implementation command.**
   - Use `--dry-run` when only validating docs or command wiring.
   - Use the real command when the user wants files generated.
   - Use `--extra-instruction` for narrow user constraints instead of editing the
     compiled spec.

4. **Validate the generated implementation.**
   - Read the generated `README.md` and run its documented install/build/test or
     smoke commands.
   - For browser games or browser apps, start the app and inspect it through
     Playwright MCP or an equivalent real browser path before claiming success.
   - If validation fails, fix the generated implementation in the implementation
     directory and rerun the relevant checks.

5. **Report implementation evidence.**
   - Mention the compiled spec path, implementation directory, Copilot transcript,
     run/test commands, and any known gaps.
   - Do not call the result behavioral evidence until the generated app or code
     has actually been run or tested.

## Guardrails

- Keep the original compiled prompt unchanged during implementation.
- Keep study scoring honest: structural and saved-output semantic evidence do
  not become behavioral evidence merely because Copilot created files.
- If comparing controls and treatments, use the same agent, model, continuation
  budget, permissions, time window, and validation checklist for each variant.
- Do not hide failed implementation requirements behind success-shaped README
  claims. Document gaps explicitly or fix them.
- Prefer simple, inspectable generated projects unless the compiled spec names a
  required stack.

## Alternatives

Use `weavemark implement` as the default because it preserves paths and
transcripts. Other acceptable user-facing options are:

- paste or attach the compiled spec manually in Copilot CLI, VS Code Copilot,
  Claude Code, or another local programming agent;
- add a small per-example `run-implementation.sh` only when a polished example
  genuinely needs its own transcript;
- add richer provider-specific adapters later if configurable process profiles
  are not enough;
- run a manual GitHub Actions workflow in a disposable checkout that publishes
  artifacts or opens a draft PR.
