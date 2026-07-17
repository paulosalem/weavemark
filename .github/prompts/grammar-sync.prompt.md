---
name: grammar-sync
description: Keep weavemark.system.md and docs/weavemark.ebnf in agreement.
applyTo:
  - "src/weavemark/prompts/weavemark.system.md"
  - "docs/weavemark.ebnf"
  - "scripts/check_grammar_sync.py"
  - "tests/test_grammar_sync.py"
---

# Grammar-sync prompt (Copilot)

WeaveMark's language is defined twice on purpose:

1. **`src/weavemark/prompts/weavemark.system.md`** — the prose
   definition that the LLM compiler reads at runtime. This is the
   **source of truth**.
2. **`docs/weavemark.ebnf`** — a deterministic mirror used by the
   offline structural validator and other tooling that must work
   without an LLM.

When you edit either file (or change a directive's surface, or modify
the kernel grammar), keep them in sync:

```bash
python scripts/check_grammar_sync.py
```

If the script exits 0, you're done. If it reports errors, apply the
**source-of-truth rule**:

> Fix the grammar (`docs/weavemark.ebnf` and/or
> `promplet-schema` blocks) to match the prose. Only edit the prose
> to match the grammar when the user has **explicitly asked** for that.

The shared checker, the full skill instructions, the error catalogue,
and the authoring conventions live in
`.claude/skills/grammar-sync/SKILL.md`. Both Claude Code and Copilot
read the same checker — pick whichever skill UI you're working in.

## Quick checks

- After any edit to the listed files, run the checker.
- Run `python -m pytest tests/test_grammar_sync.py -q` to confirm.
- Never edit `docs/weavemark.ebnf` in ways that disagree with the
  prose without also updating the prose under explicit user direction.
