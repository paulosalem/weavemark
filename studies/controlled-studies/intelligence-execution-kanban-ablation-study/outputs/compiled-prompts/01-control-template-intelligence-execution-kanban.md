# Work Intelligence Kanban: Matched Reusable Template Control

## Implementation specification contract

- This is the coherent implementation-ready specification for Work Intelligence Kanban.
- Treat this specification as the source of truth for a programming agent or human engineer.
- Include first-build scope, out-of-scope items, architecture, domain model,
  durable records, workflows, UI surfaces, automation rules, validation plan,
  failure handling, privacy/provenance rules, and acceptance criteria.
- Distinguish required first-build behavior from optional later enhancements.
- Avoid separate support prompts, prompt packs, or artifact manifests.
- Every major requirement should have an observable user-facing or validation
  consequence.
- Use concrete field names, states, events, screens, checks, and recovery paths
  instead of generic quality advice.


## Case-specific intent

Design Work Intelligence Kanban, a local-first workspace that connects information intake with project execution. The user follows selected work topics, receives relevant signals, captures ideas, decides what to do, delegates or executes work, tracks status, and turns useful inputs into concrete outputs.

## Local-first Next.js, Prisma, and SQLite foundation

- Use Next.js with TypeScript strict mode, Prisma, and SQLite.
- Keep authoritative workspace state local by default in a user-selectable
  directory.
- Use SQLite WAL mode, schema versioning, deterministic migrations, startup
  diagnostics, explicit transaction boundaries, backups before risky migrations,
  and visible repair guidance.
- Store large attachments and generated artifacts as files; store metadata,
  content hash, MIME type, size, origin, relative path, and provenance in SQLite.
- Durable records should have stable IDs, created/updated timestamps, status,
  owner or actor when relevant, provenance links, optimistic versioning for
  conflicting writes, and archive or soft-delete behavior.
- Exports should include database, referenced files, schema version, application
  version, manifest, and checksums. Imports should validate checksums and require
  explicit confirmation before overwriting a workspace.
- External providers are optional. Existing local data must remain usable when
  AI, search, feeds, or integrations are unavailable.
- Logs must avoid secrets, tokens, private payloads, and full sensitive artifacts
  unless diagnostic capture is explicitly enabled.


## Work-intelligence domain template

- The product should turn monitored topics, external signals, personal ideas,
  decisions, delegations, actions, warnings, and generated outputs into one
  inspectable Kanban workspace.
- Monitor these initial topic families: WeaveMark and prompt languages; local-first AI tools; agentic workflows; research automation; UI/UX examples; personal project opportunities; selected competitors and communities..
- Each topic should define watch intent, source families, cadence, exclusions,
  thresholds, muted patterns, review cadence, and failure behavior.
- Signals should preserve title, source, URL or local reference, author or
  organization when known, retrieved time, published time, topic match, source
  family, evidence quality, novelty, confidence, relevance, and summary.
- Signals may become insights, ideas, questions, warnings, decisions,
  delegations, actions, watch items, outputs, or deliberate archive records.
- Ideas should carry hypothesis, expected value, owner, status, next action,
  dependencies, output links, review cadence, and evidence that the idea was
  executed or deliberately dropped.
- Delegations should track owner, request, expected deliverable, due or check-in
  window, status evidence, blockers, handoff context, and follow-up cadence.
- Recommendations should preserve alternatives, rationale, uncertainty,
  confidence, source trace, and revisit condition.
- Notifications should be explainable, deduplicated, cooldown-aware, thresholded
  by topic, and tied to meaningful card conversions or status changes.
- The system should answer: what came in, why it mattered, what was decided, who
  is doing what, what is blocked, what changed, and what output was produced.


## Reusable workspace modules

### Cards, boards, and workflow states

- Use cards as durable bounded records, not only tasks.
- Cards need type, title, summary, status, owner, priority, tags, due or review
  window, source links, dependencies, next action, blocked reason, output links,
  and activity history.
- Boards should support explicit stages, meaningful transition rules, keyboard
  movement, drag movement, invalid-move explanations, saved views, search,
  filters, sorting, and detail panes.

### Output surfaces and artifacts

- Provide typed output surfaces for text, tables, structured records, reports,
  status, forms, images or screenshots when relevant, terminal logs, and audit
  exports.
- Each surface should preserve payload or file reference, schema version, source,
  lineage, status, revision history, comments, approvals, pin/minimize/pop-out
  state, and export/apply actions.
- Streaming or generated surfaces must visibly distinguish draft, partial, final,
  failed, stale, superseded, and approved states.

### Activity, attachments, and provenance

- Activity events should be append-only and ordered with actor, event type,
  severity, payload summary, target entity, correlation ID, source, and timestamp.
- Attachments need type, title, source, content reference, MIME/format,
  checksum, permissions, derived-context reference, relative path, and provenance.
- The UI should let users reconstruct what happened and filter by actor, event
  type, severity, source, and error state.

### APIs, realtime, and automation

- Provide local REST APIs with JSON envelopes, schema validation, pagination,
  idempotency keys for mutating retries, and RFC 7807-style problem details.
- Provide realtime events for durable state changes with acknowledgements,
  heartbeat, reconnect, replay from last event ID, and persisted-before-broadcast
  behavior for important changes.
- AI automation may summarize, classify, draft, compare, suggest, ask questions,
  create artifacts, or check status, but every material automation needs trigger,
  inputs, confidence, proposed or taken action, evidence links, review state,
  undo path, and tuning controls.

### Command-center UI

- The main UI should combine an attention inbox, board or matrix, detail pane,
  output surfaces, dashboards, notification center, activity stream, and settings
  without feeling cluttered.
- Dashboards should show health, blockers, stale items, overdue reviews, failed
  checks, risk exposure, ownership, and confidence changes.
- Empty, loading, locked database, provider unavailable, permission-limited,
  duplicate, stale, unsupported file, failed automation, and export mismatch
  states need useful recovery actions.


## Browser validation and evidence

- Validate the actual browser experience, not only static source inspection.
- Record command used to run the app, URL tested, browser flows exercised,
  screenshots or traces when available, console errors found and resolved, and
  remaining limitations.
- Browser validation should cover first load, primary user flow, invalid inputs,
  persistence across restart or reload, responsive layout, keyboard/focus
  behavior, recovery states, and absence of runtime console errors.
- Prefer Playwright MCP or an equivalent real-browser tool when available. If the
  browser tool cannot run, report the exact blocker and do not claim browser
  validation happened.
- Acceptance requires a first-session path that proves the product is usable,
  understandable, recoverable, and backed by saved evidence.


## Required output

This coherent implementation specification includes architecture, data model,
SQLite schema, transactions, monitoring lifecycle, board states, card types,
decision semantics, delegation and status-check workflows, output surfaces,
dashboards, notifications, APIs, live events, AI automation rules,
privacy/provenance behavior, failure handling, validation scripts, and acceptance
criteria.
