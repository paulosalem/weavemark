# Blind evaluation packet

Study: Release Readiness Workbench
Variant: A
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# {{app_name}}: Matched Reusable Template variant

{{> common/implementation-spec}}

## Case-specific intent

{{product_brief}}

{{> programming/local-first-nextjs-sqlite}}

{{> domains/release-readiness}}

{{> programming/workspace-modules}}

{{> programming/browser-validation}}

## Required output

This coherent implementation specification includes architecture, local
workspace model, SQLite schema, release gates, validation matrix, evidence
ledger, docs/example workflow, risk register, waivers, decisions, action board,
APIs, realtime events, automation behavior, UI screens, dashboards,
privacy/provenance rules, failure handling, release decision rules,
rollback/monitoring loop, and acceptance criteria.


## Variable payload

{
  "app_name": "Release Readiness Workbench",
  "artifact_name": "Release Readiness Workbench",
  "product_brief": "Design Release Readiness Workbench, a local-first public-release command center that turns release notes, issue lists, pull request summaries, docs gaps, example runs, test results, package artifacts, screenshots, risks, blockers, waivers, and launch decisions into one auditable go/no-go workspace.",
  "release_surfaces": "Framework-X public README, docs, examples, generated outputs, study results, release notes, package artifacts, extension builds, CLI behavior, installation checks, browser-facing examples, screenshots, traces, issues, PR notes, local TODOs, deferred work, waivers, and known limitations."
}


## Compiled output

# Release Readiness Workbench: Matched Reusable Template variant

## Implementation specification contract

- This is the coherent implementation-ready specification for Release Readiness Workbench.
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

Design Release Readiness Workbench, a local-first public-release command center that turns release notes, issue lists, pull request summaries, docs gaps, example runs, test results, package artifacts, screenshots, risks, blockers, waivers, and launch decisions into one auditable go/no-go workspace.

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


## Release-readiness domain template

- The product should transform messy release material into release candidates,
  gates, evidence items, validation checks, docs/example readiness, risks,
  blockers, waivers, actions, release notes, decisions, exports, and post-launch
  monitoring records.
- Release gates should cover product behavior, documentation, examples, tests,
  build/package/install, security/privacy, accessibility, performance, rollback,
  support, migration notes, and release communication.
- Gate states should include not started, collecting evidence, ready, ready with
  caveat, blocked, waived, deferred, and not applicable.
- Evidence items should record type, source path or URL, command or flow,
  environment, artifact reference, freshness, scope, reviewer, quality,
  limitations, linked claim, and release impact.
- Critical gates should block release unless explicitly waived with rationale,
  owner, approver, expiry, accepted risk, and revisit trigger.
- Validation checks need expected proof, owner, status, last run, failure meaning,
  rerun requirement, release impact, and supersession history.
- Failed validation should create actions while preserving failed evidence until
  a passing rerun supersedes it.
- Release decisions should support ship, ship with caveat, wait, fix first,
  defer scope, rollback, or cancel.
- Release notes should distinguish verified behavior, known limitations,
  deferred work, migration notes, support guidance, and rollback/monitoring
  expectations.
- Apply release readiness to these surfaces: Framework-X public README, docs, examples, generated outputs, study results, release notes, package artifacts, extension builds, CLI behavior, installation checks, browser-facing examples, screenshots, traces, issues, PR notes, local TODOs, deferred work, waivers, and known limitations.


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

This coherent implementation specification includes architecture, local
workspace model, SQLite schema, release gates, validation matrix, evidence
ledger, docs/example workflow, risk register, waivers, decisions, action board,
APIs, realtime events, automation behavior, UI screens, dashboards,
privacy/provenance rules, failure handling, release decision rules,
rollback/monitoring loop, and acceptance criteria.
