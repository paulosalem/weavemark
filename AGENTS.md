# Agent Instructions

## Machine-local agent workspace

Temporary agent material must live outside this repository at:

```text
~/.weavemark/agent-workspace/weavemark/
```

Use these subdirectories:

- `reports/` — audits, reviews, investigation reports, and release assessments.
- `notes/` — working notes, plans, decision drafts, and handoff context.
- `artifacts/` — generated evidence or intermediate outputs that are useful locally
  but are not product deliverables.
- `tmp/` — disposable files. Clean these when the task ends.

The location may be overridden for automation with
`WEAVEMARK_AGENT_WORKSPACE`, but it must remain outside the repository.

## Repository hygiene

- Do not add agent plans, audit reports, scratch notes, session state, raw logs, or
  temporary evidence to this repository.
- Do not symlink the machine-local workspace into the repository.
- Do not copy material from the local workspace into the repository unless the user
  explicitly asks to promote it into product documentation or another tracked file.
- Do not store secrets in either the repository or the agent workspace.
- Product artifacts that are intentionally part of WeaveMark—source, tests,
  documentation, maintained examples, and explicitly curated outputs—belong in the
  repository. The local-workspace rule applies to agent process material, not to
  intentional project content.

## Current repository state

The local repository is linked to `https://github.com/paulosalem/weavemark.git`,
which is currently empty. Do not create the initial commit until the user chooses
its contents and sequencing.

Nested `AGENTS.md` files may add domain-specific instructions for their subtree.

## Reference authority

- `src/weavemark/prompts/weavemark.system.md` is authoritative for the WeaveMark
  language and semantic compilation contract.
- `docs/weavemark.ebnf` is derived from and must mirror the system prompt.
- The CLI parsers, public Python package exports/signatures, typed settings, and
  engine registries are authoritative for their respective executable surfaces.
- README, site pages, tutorials, examples, editor metadata, and prose tables are
  downstream documentation. Never change the language to match downstream docs;
  update downstream material from the relevant authority.
