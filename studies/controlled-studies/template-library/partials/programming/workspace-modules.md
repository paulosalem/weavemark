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
