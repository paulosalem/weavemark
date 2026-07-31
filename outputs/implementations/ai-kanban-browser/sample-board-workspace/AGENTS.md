# AI Kanban workspace

This folder is a portable AI Kanban Board Workspace and its trust boundary.

Before changing work:

1. Read `manifest.json`.
2. Read the canonical skill at `.agents/skills/ai-kanban/SKILL.md`.
3. Run the skill preflight and use its CLI for every board mutation.
4. Respect the cooperative writer baton, expected revision, control generation,
   idempotency keys, and relative-path boundary.

Do not edit `board.sqlite` or `.ai-kanban/coordination/` outside the documented
protocol. Do not render or execute untrusted workspace content.
