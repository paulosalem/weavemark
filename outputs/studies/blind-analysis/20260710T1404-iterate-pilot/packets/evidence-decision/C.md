# Blind evaluation packet

Study: Evidence-to-Decision Workspace
Variant: C
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# {{app_name}}: Matched Reusable Template variant

{{> common/implementation-spec}}

## Case-specific intent

{{product_brief}}

{{> programming/local-first-nextjs-sqlite}}

{{> domains/evidence-decision}}

{{> programming/workspace-modules}}

{{> programming/browser-validation}}

## Required output

This coherent implementation specification includes architecture, first-build
scope, data model, SQLite schema, transactions, source and attachment handling,
evidence grading, contradiction workflow, ACH matrix behavior, decision gates,
action planning, APIs, WebSocket events, automation behavior, UI screens,
privacy/provenance rules, failure handling, validation strategy, and acceptance
criteria.


## Variable payload

{
  "app_name": "Evidence-to-Decision Workspace",
  "artifact_name": "Evidence-to-Decision Workspace",
  "product_brief": "Design Evidence-to-Decision Workspace, a local-first application for turning messy personal and professional source material into auditable decisions and follow-up actions. The user imports notes, documents, links, research snippets, meeting fragments, and news, then normalizes inputs, extracts claims, grades evidence, surfaces contradictions, compares explanations or options, decides whether to act, wait, or investigate, and converts decisions into tracked actions.",
  "source_families": "documents, PDFs, notes, meeting transcripts, pasted snippets, URLs, newsletters, GitHub issues or releases, research papers, web pages, news items, calendars, and compact observations.",
  "decision_domains": "personal project choices, public-release decisions, technology adoption, vendor or tool selection, investment-like tradeoffs, operational incidents, and research-backed action plans."
}


## Compiled output

# Evidence-to-Decision Workspace: Matched Reusable Template variant

## Implementation specification contract

- This is the coherent implementation-ready specification for Evidence-to-Decision Workspace.
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

Design Evidence-to-Decision Workspace, a local-first application for turning messy personal and professional source material into auditable decisions and follow-up actions. The user imports notes, documents, links, research snippets, meeting fragments, and news, then normalizes inputs, extracts claims, grades evidence, surfaces contradictions, compares explanations or options, decides whether to act, wait, or investigate, and converts decisions into tracked actions.

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


## Evidence-to-decision domain template

- The product should turn messy sources into auditable claims, evidence items,
  contradictions, hypotheses, options, decision gates, actions, review loops,
  and typed outputs.
- Initial source families: documents, PDFs, notes, meeting transcripts, pasted snippets, URLs, newsletters, GitHub issues or releases, research papers, web pages, news items, calendars, and compact observations..
- Decision domains to support first: personal project choices, public-release decisions, technology adoption, vendor or tool selection, investment-like tradeoffs, operational incidents, and research-backed action plans..
- Sources should preserve title, author or organization when known, URL or local
  reference, source family, retrieved time, published time, checksum, import
  method, extraction status, and permission policy.
- Normalize inputs into source facts, inferred structure, existing decisions,
  action candidates, risks, blockers, open questions, contradictions, and
  confidence notes.
- Claims should be first-class records with statement, scope, status, source
  links, owner, confidence, decision relevance, tags, and review state.
- Evidence items should record relevance, specificity, freshness, independence,
  contradiction status, reliability, diagnostic value, direction, main gap, and
  decision impact.
- Contradictions should remain visible with type, affected claims, source
  family, severity, resolution state, and decision consequence.
- ACH-style review should compare evidence rows against competing hypotheses
  with consistent, inconsistent, neutral, or missing-but-expected assessments.
- Decision gates should support act, wait, investigate, delegate, monitor,
  archive, or escalate with thresholds, blockers, confirmations, and revisit
  triggers.
- Actions should link back to sources, claims, evidence, hypotheses, options,
  decisions, and generated outputs.


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
  undo path, and tuning variants.

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

This coherent implementation specification includes architecture, first-build
scope, data model, SQLite schema, transactions, source and attachment handling,
evidence grading, contradiction workflow, ACH matrix behavior, decision gates,
action planning, APIs, WebSocket events, automation behavior, UI screens,
privacy/provenance rules, failure handling, validation strategy, and acceptance
criteria.
