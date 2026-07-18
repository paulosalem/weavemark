# Signal Board — implementation specification

Design **Signal Board**, a local-first news and events intelligence board for a technical product lead deciding what the engineering team should evaluate, adopt, monitor, or communicate. The product promise is a high-signal view of changing topics without repeatedly showing the same story. It MUST be buildable, testable, and concrete enough for implementation.

Use RFC 2119 keywords precisely. Every requirement MUST be testable. Every durable entity MUST have a lifecycle, explicit data model fields, constraints, indexes, and archival/deletion behavior. Every API endpoint MUST specify method, path, request body, response body, error responses, and authentication requirements. All timestamps MUST be UTC ISO 8601 with timezone offset. Monetary amounts, including pricing-change facts when modeled numerically, MUST use integer cents or the smallest currency unit, never floats.

## 1. Product promise and user jobs

Signal Board monitors these configured interests:

- Topics: AI developer tools, foundation-model releases, model safety evaluations, and material policy or regulatory changes affecting software teams
- Event types: product launch, model release, benchmark or safety evaluation, API change, deprecation, security incident, pricing change, regulation, enforcement action
- Regions or jurisdictions: Global, with emphasis on the United States, European Union, and Brazil
- Refresh cadence: Every six hours, plus manual refresh
- Search lookback: Previous seven days
- Memory retention: retain source fingerprints indefinitely; retain active event details for two years; archive presentation history rather than deleting it
- Audience and decision context: a technical product lead deciding what the engineering team should evaluate, adopt, monitor, or communicate

Primary user jobs:

1. Know what materially changed since the last review.
2. Avoid duplicate cards for copied, syndicated, retitled, or URL-varied coverage.
3. Inspect why an event matters, what evidence supports it, and what remains uncertain.
4. Follow selected events and see only material updates.
5. Dismiss or mute noise without losing memory needed for future deduplication.
6. Browse prior memory, decisions, evidence, and refresh reports while offline.
7. Understand search/crawl gaps and partial coverage without mistaking them for a successful refresh.

The app MUST separate confirmed facts, reported claims, opinions, forecasts, rumors, repeated background, and speculative leads. A news item SHOULD include concrete named entities, relevant historical context, timelines, comparisons, stakeholders, benefits, risks, uncertainties, and why the story matters now. The app MUST avoid clickbait framing, sensationalism, shallow reposts, stale boilerplate, and false confidence.

## 2. Technology, architecture, and local-first boundaries

Build with:

- Next.js 14+ with App Router.
- TypeScript 5+ in strict mode with no `any`.
- Tailwind CSS using design tokens in `tailwind.config.ts`.
- React Server Components by default; Zustand only for local UI state that cannot live in server-rendered data.
- react-hook-form with zod validation schemas shared with UI, API routes, and Server Actions.
- Node.js runtime only for routes or actions that touch SQLite; do not use Edge runtime for SQLite work.
- Prisma with SQLite provider.
- `DATABASE_URL` pointing to a local SQLite file under the app workspace or OS user-data directory.
- SQLite 3 in WAL mode.
- Prisma Migrate. On startup, run pending migrations after creating a backup when existing data is present.
- camelCase in Prisma schema, mapped to snake_case table/column names where practical.
- `createdAt DateTime @default(now())`, `updatedAt DateTime @updatedAt`, and `deletedAt DateTime?` on recoverable entities.
- Explicit transactions for multi-entity updates.

Signal Board is a local-first web application:

- The local machine is the source of truth. Browser `localStorage`, IndexedDB, memory, and cache files MAY improve UX but MUST NOT be authoritative for source memory, event clusters, presentation history, user decisions, or settings.
- The app MUST be useful without a hosted multi-tenant backend. Do not add subscriptions, billing, tenant isolation, or organization onboarding.
- Define one default local workspace and allow choosing or creating another workspace directory.
- Store the SQLite file, attachments, generated artifacts, backups, repair logs, and derived artifacts under the workspace directory or OS user-data directory.
- Show the active workspace path in settings and diagnostics.
- Provide export/import so a workspace can move between machines without hidden server state.
- Keep private user data local by default. Before sending local content to an external AI, web, or integration service, the UI MUST make the destination and purpose clear.
- Logs MUST avoid secrets, API keys, refresh tokens, and full sensitive payloads unless the user explicitly enables diagnostic capture.
- The app MUST continue to load and display existing local data when network, providers, or model calls fail.

Startup MUST validate that the workspace is readable, writable, and on a supported schema version. If the store is missing, initialize deterministically. If the store is locked, corrupted, or too new for the app version, show a recoverable error with backup, repair, or upgrade guidance. The app MUST refuse to start on an unsupported future schema version instead of silently rewriting the database.

Expose `GET /api/health` returning local store status, schema version, app version, last migration status, and provider configuration health without exposing credentials.

## 3. Bounded search and ingestion pipeline

Provider credentials and model selection are host configuration, never ordinary promplet variables and never exposed in the UI. Search/crawl requests MUST be bounded by per-refresh query, result, page, time, and cost budgets. Respect robots/provider terms and retain source URLs, timestamps, and retrieval outcomes.

Each scheduled or manual refresh is a dated monitoring cycle with a clear lookback window. For every refresh:

1. Create a `refreshRun` with mode `scheduled` or `manual`, cadence, lookback window, topic set, event-type filters, region filters, budgets, and started time.
2. Build searches from monitored topics, wanted event types, regions, exclusions, source-family preferences, and the lookback window.
3. Fetch result metadata.
4. Crawl only candidates that pass deterministic domain, date, URL, source-family, and budget filters.
5. Canonicalize URLs, remove tracking parameters, normalize content, and hash normalized content.
6. Extract candidate event type, entities, action/change, location, effective date, claims, source evidence, source family, and retrieval metadata.
7. Compare against source memory and event memory.
8. Store the source document even when it is not shown, with a reason code.
9. Create, update, suppress, or resurface an event cluster according to the clustering and presentation rules.
10. Persist activity events for search, crawl, extraction, clustering, model judgment, suppression, resurface, notification, provider failure, and user-visible partial coverage.
11. Complete the refresh run with counts for new events, material updates, suppressed duplicates, uncertain matches, failed sources, exhausted budgets, and partial-coverage causes.

Use exact URL/content hashes and deterministic entity/date keys before semantic similarity. The model MAY judge whether two documents describe the same event or whether an update is material only after deterministic checks leave ambiguity. A failed provider or partial crawl MUST produce a visible partial-coverage state; it MUST NOT make the refresh appear successful.

Record omissions and monitoring gaps when search or crawl access is partial. Prefer items that changed within the previous seven days. Preserve source detail so a future run can compare what changed.

## 4. Core domain model: sources, events, presentations

Keep these concepts separate:

1. **Source document** — one fetched article, release, filing, bulletin, repository post, safety report, benchmark page, regulatory page, enforcement notice, or event page with canonical URL, publisher, publication/update time, content hash, extracted entities, claims, and retrieval metadata.
2. **Event cluster** — the underlying real-world development represented by one or more source documents. Store event type, entities, location, time window, current status, material facts, uncertainty, and source-family coverage.
3. **Presentation history** — when and why the event was shown, dismissed, followed, muted, archived, or resurfaced.

SQLite is authoritative for source fingerprints, event clusters, user decisions, presentation history, attachments, typed output surfaces, activity history, monitor configuration, refresh runs, and notification state. Never infer “unseen” from browser state.

### Required SQLite tables

Implement explicit relational tables. Every table MUST have a stable primary key, `createdAt`, `updatedAt`, applicable `deletedAt`, and indexes for board/order queries, search filters, event replay, dependency lookups, and deduplication.

#### `workspace_settings`

Fields:

- `id`: string primary key.
- `workspacePath`: string, unique, non-empty.
- `schemaVersion`: string.
- `appVersion`: string.
- `providerConfigStatus`: enum `unconfigured | configured | degraded`.
- `createdAt`, `updatedAt`.

#### `monitors`

Fields:

- `id`: string primary key.
- `name`: string, unique within workspace.
- `topics`: JSON array of exact monitored topics.
- `eventTypes`: JSON array.
- `regions`: JSON array.
- `sourceFamilyPreferences`: JSON object.
- `exclusions`: JSON array.
- `cadence`: string; default `Every six hours, plus manual refresh`.
- `lookbackWindow`: string; default `Previous seven days`.
- `importancePolicy`: JSON object.
- `mutePolicy`: JSON object.
- `lastCompletedAt`: datetime nullable.
- `nextRefreshAt`: datetime nullable.
- `status`: enum `active | paused | error`.
- `createdAt`, `updatedAt`, `deletedAt`.

Indexes: `status`, `nextRefreshAt`, `updatedAt`.

#### `refresh_runs`

Fields:

- `id`: string primary key.
- `monitorId`: foreign key.
- `mode`: enum `scheduled | manual`.
- `startedAt`, `completedAt`: datetime nullable.
- `status`: enum `running | succeeded | partial_failure | failed | cancelled`.
- `lookbackStart`, `lookbackEnd`: datetime.
- `budgets`: JSON object with query, result, page, time, cost, model-call, and token limits.
- `counts`: JSON object containing new events, material updates, suppressed duplicates, uncertain matches, failed sources, exhausted budgets, and crawled candidates.
- `coverageGaps`: JSON array.
- `error`: JSON nullable.
- `createdAt`, `updatedAt`.

Indexes: `monitorId, startedAt`, `status`, `completedAt`.

#### `source_documents`

Fields:

- `id`: string primary key.
- `canonicalUrl`: string nullable, unique when present.
- `urlHash`: string, indexed.
- `contentHash`: string, indexed.
- `publisher`: string nullable.
- `sourceFamily`: enum or string such as `official`, `primary_document`, `credible_reporting`, `community`, `social`, `syndicated`, `unknown`.
- `title`: string.
- `authorOrOrganization`: string nullable.
- `publishedAt`: datetime nullable.
- `updatedAtSource`: datetime nullable.
- `retrievedAt`: datetime.
- `retrievalStatus`: enum `fetched | skipped | failed | blocked | partial`.
- `retrievalReasonCode`: string.
- `normalizedTextRef`: relative file path nullable.
- `contentSnippet`: string nullable.
- `extractedEntities`: JSON array.
- `extractedClaims`: JSON array.
- `evidenceQuality`: JSON object using relevance, specificity, freshness, independence, contradictions, evidence grade, main gap, and decision impact.
- `refreshRunId`: foreign key.
- `createdAt`, `updatedAt`, `deletedAt`.

Uniqueness and indexes: unique `canonicalUrl` where non-null; indexes on `contentHash`, `urlHash`, `publishedAt`, `publisher`, `sourceFamily`, `refreshRunId`.

#### `event_clusters`

Fields:

- `id`: string primary key.
- `stableKey`: string unique deterministic key from event type, primary entities, normalized action/change, location, and effective date where available.
- `title`: string.
- `eventStatement`: concise factual statement.
- `eventType`: enum matching the configured event types.
- `entities`: JSON array.
- `location`: string nullable.
- `region`: string.
- `timeWindowStart`, `timeWindowEnd`: datetime nullable.
- `currentStatus`: enum `reported | confirmed | corrected | superseded | resolved | stale | disputed | needs_review`.
- `materialFacts`: JSON array.
- `uncertainty`: string nullable.
- `confidence`: enum `high | medium | low | insufficient`.
- `freshness`: enum `new | updated | stale | archived`.
- `sourceFamilyCoverage`: JSON object with counts and strongest source.
- `strongestSourceDocumentId`: foreign key nullable.
- `firstSeenAt`: datetime.
- `lastMaterialChangeAt`: datetime nullable.
- `lastPresentedAt`: datetime nullable.
- `importanceScore`: integer range 0–100.
- `actionabilityScore`: integer range 0–100.
- `relevanceExplanation`: string explaining why it matters to the audience context.
- `boardState`: enum `new_signal | following | needs_review | read_later | dismissed | archived`.
- `version`: integer optimistic concurrency field.
- `createdAt`, `updatedAt`, `deletedAt`.

Indexes: `stableKey`, `eventType`, `region`, `boardState`, `lastMaterialChangeAt`, `firstSeenAt`, `confidence`, `importanceScore`.

#### `event_sources`

Join table:

- `id`: string primary key.
- `eventClusterId`: foreign key.
- `sourceDocumentId`: foreign key.
- `relationship`: enum `primary | corroborating | syndicated | conflicting | background | correction | duplicate`.
- `addedByRule`: string.
- `createdAt`, `updatedAt`.

Unique: `eventClusterId, sourceDocumentId`.

#### `presentation_history`

Fields:

- `id`: string primary key.
- `eventClusterId`: foreign key.
- `presentedAt`: datetime.
- `presentationType`: enum `new_event | material_update | resurface | review_hold | suppression | notification`.
- `boardStateAtPresentation`: string.
- `rule`: string.
- `reason`: string.
- `whatChanged`: JSON array of field-level diffs.
- `sourceDocumentIds`: JSON array.
- `modelJudgmentId`: foreign key nullable.
- `userDecisionId`: foreign key nullable.
- `createdAt`, `updatedAt`.

Indexes: `eventClusterId, presentedAt`, `presentationType`.

#### `user_decisions`

Fields:

- `id`: string primary key.
- `eventClusterId`: foreign key.
- `decision`: enum `follow | read_later | dismiss | mute_topic | mute_event_type | archive | restore | mark_duplicate | mark_material | mark_not_material`.
- `scope`: JSON object.
- `expiresAt`: datetime nullable for mutes.
- `reason`: string nullable.
- `createdAt`, `updatedAt`.

#### `activity_events`

Each event MUST define:

- `id`: stable identifier.
- `type`: semantic event type.
- `actor`: enum `human | model | integration | system | automation`.
- `targetType`, `targetId`.
- `timestamp`: authoritative UTC time.
- `summary`: short human-readable description.
- `payload`: structured details.
- `visibility`: enum `public | private | internal | redacted`.
- `correlationId` or `traceId`.
- `createdAt`, `updatedAt`.

The stream SHOULD be append-only. Persist events before broadcasting live updates when the stream is an audit source. Support pagination, incremental loading, filters by event type, actor, severity, source, and errors. Avoid secrets and excessive raw internals.

#### `attachments`

Each attachment MUST define:

- `id`, `hostId`, `hostType`.
- `type`: enum `file | url | text | image | table | artifact | reference | source_document | related_entity`.
- `title`, `source`, `contentRef`, `mimeType`, `size`, `checksum`.
- `createdBy`, `createdAt`, `updatedAt`.
- `provenance`: JSON object.
- `permissions`: JSON object.

Source documents attached to event cards MUST preserve provenance. Generated derivatives such as extracted text, thumbnails, embeddings, summaries, evidence tables, and claim comparisons MUST be traceable artifacts.

#### `output_surfaces`

Each typed surface MUST define:

- `id`, `hostId`, `hostType`.
- `type`: enum `summary | evidence_table | timeline | claim_comparison | change_diff | status | log | file | custom`.
- `title`.
- `content`: JSON payload or file reference.
- `schemaVersion`.
- `status`: enum `draft | streaming | complete | failed | stale | superseded | approved`.
- `source`: enum `human | model | integration | import | system`.
- `lineage`: JSON object linking inputs, prompts, tools, attachments, model calls, and upstream artifacts.
- `actions`: JSON array.
- `createdAt`, `updatedAt`.

#### `model_judgments`

Fields:

- `id`: string primary key.
- `purpose`: enum `event_extraction | same_event_match | material_update | evidence_grading | relevance_ranking | summary_generation | notification_threshold`.
- `inputFingerprint`: string.
- `inputRefs`: JSON array.
- `outputSchemaVersion`: string.
- `output`: JSON object validated against a closed schema.
- `confidence`: enum `high | medium | low | insufficient`.
- `evidenceRefs`: JSON array.
- `modelIdentity`: string from host configuration.
- `provider`: string from host configuration.
- `latencyMs`: integer nullable.
- `tokenUsage`: JSON nullable.
- `providerCostCents`: integer nullable.
- `createdAt`, `updatedAt`.

#### `notifications`

Fields:

- `id`: string primary key.
- `eventClusterId`: foreign key.
- `ruleVersion`: string.
- `recipient`: string.
- `channel`: enum `in_app | email | push`.
- `dedupeKey`: string.
- `severity`: enum `info | attention | critical`.
- `subject`: string.
- `body`: string.
- `actionUrl`: string.
- `deliveryState`: enum `queued | sent | delivered | failed | suppressed`.
- `attempts`: integer.
- `lastAttemptAt`: datetime nullable.
- `terminalFailureReason`: string nullable.
- `createdAt`, `updatedAt`.

Unique: `dedupeKey, recipient, channel` within cooldown/evaluation period.

### Files and payloads

Store large attachments, normalized crawled text, generated reports, and artifacts as files under the data directory, not as large database blobs by default. Store metadata, content hash, MIME type, size, origin, and relative file path in SQLite. Use content hashes to detect duplicate attachments and corrupted files. Deleting or archiving a record MUST define whether referenced files are retained, archived, garbage-collected, or moved to a trash area.

### Backup, export, migration, and repair

Provide explicit backup, restore, import, and export flows. Before destructive migrations or repair attempts, create a timestamped backup unless the database is unreadable. Exports MUST include the SQLite database, referenced files, schema version, app version, and manifest checksums. Repair tools MUST report what changed and preserve the original damaged database when possible.

## 5. Event clustering, memory, suppression, and resurface rules

Classify each candidate as exactly one of:

- **Exact duplicate:** same canonical URL or content hash. Attach retrieval metadata to the existing source; never show again.
- **Syndicated/near duplicate:** materially the same facts from another outlet. Add source coverage to the existing event; do not create a new card.
- **Same event, no material change:** wording or commentary changed, but status, decisive facts, actionability, or confidence did not. Append the source silently.
- **Material update:** a new confirmed fact, official action, corrected number, changed status, changed date/location, meaningful consequence, or new evidence that changes confidence or actionability. Update and resurface the existing event card with a visible “What changed” diff.
- **New event:** no existing cluster represents the development. Create a card.
- **Uncertain match:** hold in Needs Review; do not guess or notify.

Decision order:

1. Match canonical URL and content hash.
2. Match deterministic normalized entity/date/action keys.
3. Match known source-family syndication and copied article patterns.
4. Compare extracted facts, claims, dates, affected products, jurisdictions, API names, model names, benchmark names, regulatory bodies, and security identifiers.
5. If ambiguity remains, run a bounded model judgment against a closed schema.
6. If the model confidence is not high enough or evidence is conflicting, classify as `uncertain_match` and send to Needs Review.

A material update MUST produce a `whatChanged` diff that identifies previous value, new value, evidence, source documents, confidence change, and user relevance. Examples include official confirmation after an initial report, corrected numbers or dates, a deprecation date change, a security incident status change, a new enforcement action, a benchmark or safety evaluation that changes confidence, or a pricing/API change that affects adoption decisions.

An event the user dismissed MAY resurface only for a material update. A muted topic or event type MUST remain suppressed until its mute expires or the user changes it. Every suppression and resurface decision MUST record the rule, evidence, model judgment if any, and timestamp.

Memory retention:

- Source fingerprints MUST be retained indefinitely.
- Active event details MUST be retained for two years.
- Presentation history MUST be archived rather than deleted.
- Archived events MUST remain available for deduplication and audit, subject to retention rules.

## 6. Board, card, dashboard, evidence, and states

### Workflow board

Use a workflow board whose unit type is `event_cluster`. Default columns have stable identifiers, display names, ordering, counts, empty states, and recovery actions:

1. `new_signal` — unseen event clusters that passed the display policy.
2. `following` — events the user wants updated.
3. `needs_review` — uncertain clustering, weak evidence, or conflicting sources.
4. `read_later` — intentionally deferred items.
5. `dismissed` — hidden from normal views but retained for memory and deduplication.
6. `archived` — closed or stale events beyond the active horizon.

Allowed transitions:

- New signal → following, read later, dismissed, archived, needs review.
- Following → read later, dismissed, archived, needs review.
- Needs review → new signal, following, dismissed, archived after human decision.
- Read later → following, dismissed, archived, new signal.
- Dismissed → new signal only on material update or manual restore.
- Archived → new signal only on material update or manual restore.

Drag-and-drop MUST have keyboard alternatives. Reordering within a group MUST persist, handle conflicts, and roll back optimistic updates on failure. If movement is not allowed, show the reason at the point of interaction. Board state MUST persist across refreshes and restarts.

Provide search, filter, sort, saved views, and bulk selection for topic, event type, region, confidence, freshness, source family, followed status, mute status, and last material change. Empty boards and empty columns MUST explain what data or configuration is missing and offer the next useful action.

### Event cards

Each event card MUST be scannable at rest and open a detail view. The card MUST show:

- concise event statement and event type;
- why it matters to the technical product lead;
- current status, confidence, freshness, and region;
- source-family count and strongest primary/official source;
- first-seen and last-material-change timestamps;
- “What changed” since the previous presentation;
- badges for followed, muted, needs review, partial coverage, weak evidence, conflict, or stale;
- actions: follow, read later, dismiss, mute topic, mute event type, inspect evidence.

Cards MUST expose pointer and keyboard access, visible focus, sufficient contrast, semantic labels, and screen-reader text for icon-only controls. Click, double-click, drag, context menu, checkbox selection, and inline editing behavior MUST be unambiguous. Compact cards MUST remain legible in narrow columns, dense grids, and detail panes. Provide loading, empty, error, stale, disabled, and offline states.

### Detail view and typed output surfaces

Use context attachments for source documents and typed output surfaces for:

- `summary`: concise event statement, user relevance, and action implications.
- `evidence_table`: source rows with relevance, specificity, freshness, independence, contradictions, evidence grade, main gap, and decision impact.
- `timeline`: first seen, publication/update dates, official actions, corrections, user presentations, and notifications.
- `claim_comparison`: confirmed facts, reported claims, opinions, forecasts, rumors, repeated background, and conflicting statements.
- `change_diff`: previous presentation vs current material update.

Surfaces SHOULD use purpose-built renderers instead of flattening everything into prose. Streaming surfaces MUST distinguish partial from final output. Failed or stale surfaces MUST explain what happened and what the user can do. Generated surfaces SHOULD carry lineage to inputs, prompts, tools, attachments, and model steps. Applying a surface to an external system, repository, database, or file MUST be explicit and auditable.

### Activity stream

The activity stream records ingestion, crawling, extraction, clustering, corrections, user decisions, notifications, model judgments, partial failures, and resurface events. Use compact entries for routine events and expandable details for significant events. Show relative time for scanning and exact timestamp in detail. Preserve chronological clarity when events arrive out of order or are replayed after reconnecting.

### Dashboard

The quiet dashboard answers:

- What is being monitored?
- When did each monitor last complete?
- When is the next refresh?
- How many new events, material updates, suppressed duplicates, uncertain matches, and failed sources were found?
- Which followed events changed?
- Which sources or providers are degraded and how that affects trust?

Do not foreground raw crawl volume. Foreground signal, attention, freshness, evidence, and failed coverage that affects trust. Put the primary decision/status answer first, followed by exceptions and attention items, then trends and supporting detail. Distinguish observed, confirmed, inferred, projected, and stale values.

Dashboard states:

- **Quiet:** current answer, monitored scope, last successful refresh, next scheduled refresh.
- **Attention:** material changes, threshold crossings, failed checks, weak evidence, or needs-review items.
- **Loading:** preserve the last valid result where possible and label its age.
- **Partial failure:** keep healthy widgets usable and explain the failed source/calculation, effect, and retry path.
- **Empty:** explain missing configuration or data and offer setup/manual refresh.
- **Offline:** show locally available evidence and last sync state without pretending data is current.

Every visualization MUST have an accessible text/table equivalent, labels, keyboard access, responsive sizing, and non-color-only distinctions. Preserve active filters, selection, scroll, and focus across background refreshes.

## 7. API and background refresh contracts

All JSON endpoints MUST use `Content-Type: application/json`. Collection responses MUST use `{"data": ..., "meta": {...}}`; single-resource responses MUST use `{"data": ...}`. Empty collections return `{"data": [], "meta": {"total": 0, ...}}`, never 404. Pagination meta MUST include `{"total": N, "page": P, "per_page": S, "total_pages": T}`.

Errors MUST follow RFC 7807 Problem Details:

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "field 'amount' must be a positive integer",
  "errors": [{"field": "amount", "message": "must be a positive integer"}]
}
```

Use status codes 400, 401, 403, 404, 409, 422, 429, and 500. POST requests that create resources MUST accept an `Idempotency-Key` header; resubmitting the same key within 24 hours returns the original response. Version APIs under `/api/v1/...`.

Minimum endpoints:

- `GET /api/health` → local store status, schema version, app version, provider status.
- `GET /api/v1/monitors` → list monitors.
- `POST /api/v1/monitors` → create monitor from zod-validated body.
- `GET /api/v1/monitors/{id}` → monitor details.
- `PUT /api/v1/monitors/{id}` → replace/update monitor settings.
- `DELETE /api/v1/monitors/{id}` → soft delete monitor.
- `POST /api/v1/monitors/{id}/refresh-runs` → start manual refresh with idempotency key.
- `GET /api/v1/refresh-runs/{id}` → run status, counts, gaps, errors.
- `GET /api/v1/event-clusters` → filterable board query with pagination.
- `GET /api/v1/event-clusters/{id}` → detail including sources, surfaces, presentation history, and activity.
- `POST /api/v1/event-clusters/{id}/decisions` → follow, read later, dismiss, mute, archive, restore.
- `GET /api/v1/event-clusters/{id}/sources` → source documents for an event.
- `GET /api/v1/event-clusters/{id}/activity-events` → paginated activity stream.
- `GET /api/v1/source-documents/{id}` → source metadata and available extracted text reference.
- `GET /api/v1/notifications` → notification center.
- `POST /api/v1/notifications/{id}/acknowledge` → acknowledge notification.
- `POST /api/v1/workspace/export` → create export artifact.
- `POST /api/v1/workspace/import` → validate/import workspace artifact.
- `POST /api/v1/workspace/backup` → create backup.
- `POST /api/v1/workspace/restore` → restore from backup.

Background refresh MUST be serialized per workspace so one local app server owns SQLite writes. Duplicate manual refresh requests with the same idempotency key MUST NOT start duplicate work. Use explicit transactions when source insertion, event cluster update, presentation history, and activity event insertion must appear atomically.

If realtime updates are enabled, expose a local WebSocket endpoint `ws(s)://host/ws`. Message format is JSON with `{"type": "...", "payload": {...}, "id": "uuid"}`. Server sends `{"type": "ack", "id": "..."}` for every client message. Heartbeat: server sends `{"type": "ping"}` every 30 seconds; client MUST respond with `{"type": "pong"}` within 10 seconds or the connection is closed. On reconnect, the client sends `{"type": "resume", "payload": {"last_event_id": "..."}}`; the server replays missed events since `last_event_id` up to 1000 events or 5 minutes. Broadcast message types SHOULD include `refresh_run_update`, `event_cluster_update`, `activity_event`, `notification`, `partial_failure`, and `error`.

## 8. AI judgment schemas, evidence, budgets, and human review

Define each AI feature as a bounded outcome with explicit inputs, output schema, confidence/evidence expectations, and failure behavior. Prefer deterministic parsing, filtering, retrieval, and exact matching before model judgment. Centralize retries, timeouts, budgets, and rate limits in the LLM client layer; feature code MUST NOT invent independent retry loops.

AI features:

1. Event extraction from a source document.
2. Same-event matching when deterministic keys are ambiguous.
3. Material-update judgment.
4. Evidence grading.
5. Relevance and actionability explanation for the technical product lead.
6. Summary, evidence table, claim comparison, timeline, and change diff generation.
7. Notification threshold explanation.

Structured outputs MUST be validated against closed zod schemas and rejected when malformed, incomplete, or out-of-policy. Store model identity, request purpose, timestamps, latency, token usage, provider-reported cost where available, input fingerprint, output schema version, evidence references, and confidence.

Evidence quality MUST use this rubric:

| Criterion | Strong | Weak | Rating |
| --- | --- | --- | --- |
| Relevance | Directly supports or challenges the claim | Adjacent, generic, or loosely related | high/medium/low |
| Specificity | Concrete facts, numbers, examples, or observations | Vague assertions or broad commentary | high/medium/low |
| Freshness | Current enough for the domain | Stale or undated when timing matters | high/medium/low |
| Independence | Multiple independent sources or methods | Same source family repeated | high/medium/low |
| Contradictions | Tensions are surfaced and explained | Contrary evidence is ignored | high/medium/low |

Every event detail MUST end evidence review with:

- **Evidence grade:** strong | adequate | weak | insufficient.
- **Main gap:** the missing evidence that most limits confidence.
- **Decision impact:** whether the evidence is enough to act, wait, or investigate.

Do not upgrade the evidence grade because the conclusion is plausible. Grade the evidence actually available, and separate the evidence grade from the usefulness of provisional judgment.

Human review rules:

- Uncertain matches, conflicting sources, weak evidence that would otherwise notify, and low-confidence material-update judgments MUST enter Needs Review.
- Users MUST be able to correct duplicate, material-update, evidence, and relevance decisions.
- Corrections MUST be preserved as product state and activity history, not hidden retraining or rewritten history.
- High-impact actions require explicit confirmation; a model suggestion never silently approves, publishes, deletes, spends, changes permissions, or notifies outside the configured policy.

Privacy rules:

- Minimize model input to fields required for the feature.
- Keep secrets, credentials, private attachments, and unrelated historical data out of prompts.
- Make remote processing visible and provide a degraded local-only path when possible.
- Cache only when request inputs, relevant configuration, and source data identify an equivalent task.

## 9. Notification policy

Notify only for a new event or material update that matches the user's event-type and importance policy. Never notify once per article.

A notification MUST identify:

- the event;
- whether it is new or a material update;
- “What changed”;
- why it passed the threshold;
- confidence and evidence grade;
- source-family count and strongest source;
- link to the existing card;
- any partial-coverage warning that affects interpretation.

Rules MUST include triggering event or state transition, optional scope, condition, threshold, comparison operator, severity, recipients, channel, and cooldown. Evaluate rules after relevant domain events and scheduled checks. Record rule version, event, values, and evaluation time.

Channels:

- In-app: transient feedback plus persistent notification center.
- Email: immediate delivery for critical alerts and configurable digests for lower-priority updates.
- Push: optional web push through a Service Worker and VAPID keys.

Respect recipient preferences, quiet hours, disabled channels, verified delivery destinations, cooldowns, and mute rules. The same semantic event MUST NOT notify the same recipient and channel more than once within its cooldown or evaluation period. Retries MUST be bounded and MUST NOT create duplicate notifications. Digests SHOULD group related updates rather than replaying one message per event. Templates MUST use typed runtime fields and MUST NOT expose secrets or sensitive attachment contents in previews. Missing required fields fail validation instead of producing malformed messages.

## 10. Security, source, provider, and operational boundaries

- Provider credentials, API keys, and model selection live in host configuration and validated environment, not in user-editable monitor data.
- Use `env.mjs` with zod validation at startup.
- External network calls MUST be explicit in UI and configuration.
- Respect robots/provider terms.
- Retain source URLs, retrieved timestamps, published timestamps, retrieval outcomes, and coverage gaps.
- Logs MUST redact secrets and avoid full sensitive payloads by default.
- Workspace export/import MUST include manifest checksums.
- Backup and restore MUST preserve database, files, schema version, app version, and artifacts.
- Offline mode MUST support browsing memory, decisions, evidence, prior refresh reports, and locally available attachments.
- Partial crawl, provider outage, budget exhaustion, timeout, blocked-policy, and retry states MUST be visible and actionable.
- Concurrency and race conditions MUST be addressed for shared mutable state, including duplicate ingestion races, simultaneous user decisions, refresh cancellation, and restart during a refresh.

## 11. Testing, labeled evaluation, and acceptance criteria

Testing stack:

- Vitest for unit tests.
- happy-dom for component tests.
- Vitest with temporary SQLite files and isolated data directories for API/storage tests.
- Playwright for critical local user flows.
- Minimum 80% line coverage for application logic.

Required deterministic fixtures:

- exact URL duplicates and tracking-parameter variants;
- copied/syndicated articles;
- same event with no material change;
- official confirmation after an initial report;
- corrected numbers or dates;
- conflicting sources and uncertain clustering;
- dismissed and muted events;
- expired memory and retention boundaries;
- provider outage, partial crawl, and offline browsing;
- restart persistence, migration, backup/restore, export/import, and duplicate ingestion races;
- disk-full handling where practical;
- locked database and corrupted-file detection;
- first-run initialization;
- manual refresh idempotency;
- WebSocket reconnect and replay if realtime is enabled;
- attachment add/remove/preview/unavailable states;
- notification deduplication, cooldown, quiet hours, and malformed-template validation;
- accessibility for board navigation, card actions, filters, charts/tables, and keyboard drag alternatives.

Evaluate clustering and resurface quality on a labeled event corpus. Report false new-event and missed-material-update rates separately; do not collapse them into one accuracy score. Also report uncertain-match rate, duplicate suppression precision, duplicate suppression recall, evidence-grade calibration, notification precision, notification recall for material updates, and user-correction outcomes.

Acceptance criteria:

1. A user can configure the specified monitor topics, event types, regions, cadence, lookback, and retention policy.
2. Scheduled and manual refreshes produce durable source memory, event memory, presentation history, activity events, and visible run status.
3. Exact duplicates, syndicated duplicates, same-event/no-change items, material updates, new events, and uncertain matches follow the required classification rules.
4. A dismissed event resurfaces only for a material update; a muted topic or event type remains suppressed until expiration or user change.
5. Every event card displays status, confidence, freshness, region, strongest source, first-seen timestamp, last-material-change timestamp, and “What changed”.
6. The board, dashboard, evidence table, timeline, claim comparison, change diff, attachments, and activity stream remain usable after restart and while offline.
7. Partial provider failures are visible and do not masquerade as success.
8. API responses, error responses, idempotency, migrations, transactions, and backup/restore behavior are covered by tests.
9. AI judgments use closed schemas, retained evidence, budgets, model observability, correction paths, and human review gates.
10. Notifications fire only for new events or material updates that pass policy and are deduplicated by semantic event, recipient, channel, and cooldown.

Return the final answer in this structure:

1. Product promise and user jobs
2. System architecture and bounded search pipeline
3. SQLite data model and migration strategy
4. Event clustering, memory, suppression, and resurface rules
5. Board, card, dashboard, evidence, and quiet/error/offline states
6. API and background refresh contracts
7. AI judgment schemas, evidence, budgets, and human review
8. Notification policy
9. Security, privacy, source, and provider boundaries
10. Testing, labeled evaluation, and acceptance criteria
