## Local AI Kanban domain template

- The product should be a local-first board where each card is a durable
  workspace for human-AI collaboration.
- Cards should support human planning, context attachment, agent assignment,
  progress monitoring, typed outputs, review, approval, recovery, and audit
  history.
- Include Planner, Programmer, Researcher, Reviewer, and Orchestrator roles with
  scoped local API key access, allowed attachment types, allowed surface types,
  allowed tools, runtime budgets, provider/model settings, activity visibility,
  and lineage.
- Required output surfaces include Text, Program, Table, Diff, Image, Status,
  Canvas, Terminal, and Form.
- Agents may only read attachments granted by card or workspace policy.
  Attachment-derived context that affects output must be saved as a traceable
  artifact and logged in activity history.
- Track token usage, estimated cost where possible, card/run/surface lineage,
  correlation IDs, questions, answers, errors, tool calls, and recovery actions.
- Existing local data must remain visible when external AI providers fail.
- API keys should use OS credential storage where available or encrypted local
  fallback with clear warnings.
