# WeaveMark for AI coding agents

WeaveMark is designed to work with coding agents such as GitHub Copilot, Claude
Code, and Cursor.

## Why an agent might use it

- Capture reusable personas, policies, reasoning methods, domain constraints, and
  output contracts in versioned files instead of regenerating ad-hoc prompts.
- Ask the Processor to turn abstract intent into a concrete prompt, role-tagged
  pack, executable plan, or build-ready software specification.
- Run `--scan` before spending model tokens to inspect required inputs and
  structural obligations.
- Give humans a readable surface for reviewing and correcting intent without
  editing generated implementation detail.

## Useful commands

```bash
# Inspect without compiling.
weavemark <promplet> --scan

# Compile non-interactively and return machine-readable output.
weavemark <promplet> --batch-only --format json

# Record provenance or a replayable run.
weavemark <promplet> --provenance outputs/run.provenance.json
weavemark <promplet> --record-run outputs/run
weavemark <promplet> --replay-run outputs/run

# Prepare a programming-agent implementation workspace.
weavemark implement compiled-spec.md --name my-app --dry-run
```

## Bundled agent skills

| Skill | Purpose |
|---|---|
| [`weavemark`](../.claude/skills/weavemark/SKILL.md) | Author, validate, compose, and run `.weavemark.md` sources. |
| [`weavemark-collaborative-handoff`](../.claude/skills/weavemark-collaborative-handoff/SKILL.md) | Run and debug collaborative/human-in-the-loop promplets. |
| [`weavemark-compiled-spec-implementation`](../.github/skills/weavemark-compiled-spec-implementation/SKILL.md) | Turn a compiled software specification into a runnable project. |
| [`weavemark-study-reporting`](../.github/skills/weavemark-study-reporting/SKILL.md) | Maintain controlled-study reports and metrics. |
| [`grammar-sync`](../.claude/skills/grammar-sync/SKILL.md) | Keep the language authority and grammar mirror synchronized. |

Repository-wide guidance lives in
[`CLAUDE.md`](../CLAUDE.md) and
[`.github/copilot-instructions.md`](../.github/copilot-instructions.md).
