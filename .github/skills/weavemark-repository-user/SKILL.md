---
name: weavemark-repository-user
description: |
  Help people using a WeaveMark checkout select, customize, run, and inspect
  its practical examples and built-in promplets.
when_to_use: |
  - The person identifies as a repository user rather than a maintainer
  - The person asks what they can try in a cloned WeaveMark repository
  - The person wants help running, tailoring, or viewing an example
---

# WeaveMark Repository User

Use this skill to make a cloned WeaveMark repository useful immediately. Be a
concise guide and hands-on operator, not an exhaustive documentation reader or
an implementation maintainer.

## First reply

After the person identifies as a repository user, say in one or two sentences
that WeaveMark can compose reusable prompts and run selected executable
workflows. Then offer this short menu and ask which outcome they want:

1. turn notes into an action plan;
2. summarize or research a subject;
3. improve a prompt;
4. review code or a program;
5. explore financial or local-topic monitoring;
6. make a creative artifact such as a storybook or comic;
7. browse the available examples first.

Do not dump the full example catalog unless asked.

## Selecting an example

Read `examples/README.md` and the selected example's `run.sh` or `run.py`
before recommending or executing it. Describe only:

- what it produces;
- whether it composes a prompt or also executes it;
- its likely provider, network, optional-package, or cost implications;
- the exact input file the person can edit.

Start with these practical paths:

| User goal | Example |
| --- | --- |
| Notes to next actions | `examples/terminal-output-only/messy-notes-action-plan/` |
| Summary of supplied material | `examples/terminal-output-only/deep-summary/` |
| Research or a decision | `examples/terminal-output-only/research-brief/` or `examples/terminal-output-only/decision-advisor/` |
| Improve an existing prompt | `examples/terminal-output-only/prompt-refiner/` |
| Review a program or repository | `examples/terminal-output-only/program-review-checklist/` |
| Monitor a topic | `examples/saved-artifact-workflows/recurring-topic-monitor/` |
| Market or investment brief | `examples/saved-artifact-workflows/market-snapshot/` or `examples/saved-artifact-workflows/investment-brief/` |
| Inspect a creative workflow | `examples/saved-artifact-workflows/childrens-book-orion-en/` or `examples/saved-artifact-workflows/comic-strip-en/` |

Prefer `terminal-output-only/` examples for a first live run. They compose a
prompt for the user to inspect or paste into a chat assistant and generally
have the smallest operational footprint. Use a saved-artifact workflow only
when the person wants its specific output.

## Setup and safe first checks

From the repository root:

```bash
pip install -e .
weavemark promplets/catalog/standalone/program-review-checklist.weavemark.md --scan
```

The scan is local and does not need model credentials. For a live composition
or execution, first load the local shell environment without printing secrets:

```bash
source ~/.zshenv >/dev/null 2>&1 || true
source ~/.zshrc >/dev/null 2>&1 || true
```

Install `pip install -e ".[examples]"` and `playwright install chromium` only
for an example that genuinely needs finance, web, or browser companions. Tell
the person before installing optional dependencies or making a live model call.

## Customizing inputs

Open the chosen example's `inputs/vars.json` before editing it. Explain the
smallest meaningful change, then make only the requested changes. Preserve the
JSON structure and use the existing fields; do not invent a configuration
framework or alter the runner.

For examples that keep source material alongside vars, such as
`reference-context`, explain which input file supplies the content. For
examples whose source is in the catalog, open the referenced promplet only when
the person wants to change behavior rather than input values.

If a user wants an entirely new task, first identify the closest catalog
promplet or example. Prefer tailoring its vars and source material before
authoring a new promplet.

## Running examples

Treat each `run.sh` as a readable command transcript. Run it from the
repository root; the shared helper makes its current directory safe. Do not
add arguments, wrappers, or alternative modes to example runners.

Before a live run:

1. State whether it composes only or executes a model workflow.
2. State where it will write outputs, if any.
3. Confirm that its configured model/provider and optional dependencies are
   available.
4. Load the shell environment for model-backed commands.

For terminal-only examples, let the composed prompt remain visible in the
terminal. For a saved-artifact workflow, inspect the generated files under that
example's `outputs/` directory and summarize the useful artifacts, not every
intermediate file.

## Viewing outputs

Organize outputs where the selected example already expects them: its local
`outputs/` directory. Do not create a new output abstraction or scatter files
elsewhere.

After a successful run:

- inspect Markdown and JSON before presenting conclusions;
- open HTML, PDF, and image outputs in an appropriate external viewer when that
  helps the person assess the result;
- use the integrated browser for HTML when available, otherwise use the
  platform's ordinary file opener;
- tell the person the exact artifact path and what to look at;
- for multi-file visual work, open the packaged `book.html`, `book.pdf`, or
  top-level image rather than every page separately.

If output is absent or malformed, report that directly, inspect the trace when
one exists, and correct the specific cause before rerunning.

## Boundaries

- Keep guidance concise and outcome-oriented.
- Do not modify WeaveMark source, examples, or repository instructions for a
  repository user unless they explicitly ask to become a contributor.
- Do not run costly, networked, or image-generation workflows by default.
- Never claim a workflow succeeded solely from its exit code; inspect its
  promised prompt, report, trace, or visual artifact.
