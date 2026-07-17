# Blind evaluation packet

Study: Intelligence-to-Execution Kanban
Variant: A
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# @{app_name}: Framework-X Work-Intelligence variant

@directive-c target: structure preserve: hard
  @directive-a programming/foundations/software-spec
  @directive-a programming/stacks/stack-typescript-nextjs-prisma-sqlite
  @directive-a programming/types/type-local-first-webapp
  @directive-a domains/work-intelligence/topic-intelligence-monitor mingle: true
  @directive-a domains/work-intelligence/signal-to-action-workflow mingle: true
  @directive-a domains/work-intelligence/idea-execution-workspace mingle: true
  @directive-a programming/modules/module-local-sqlite-storage mingle: true
  @directive-a programming/modules/module-card mingle: true
  @directive-a programming/modules/module-workflow-board mingle: true
  @directive-a programming/modules/module-output-surfaces mingle: true
  @directive-a programming/modules/module-activity-stream mingle: true
  @directive-a programming/modules/module-dashboard mingle: true
  @directive-a programming/modules/module-notifications mingle: true
  @directive-a programming/modules/module-ai-features mingle: true
  @directive-a programming/modules/module-rest-api mingle: true
  @directive-a programming/modules/module-realtime mingle: true
  @directive-a programming/validation/playwright-mcp-browser-validation

  Design @{app_name}: a focused local-first Kanban that converts monitored
  signals into reviewed cards, decisions, actions, delegations, outputs, alerts,
  and updated watch rules.

  Monitor: @{topic_families}

  @directive-b mode: intention focus: "one product-shaped signal -> card -> decision/action/delegation -> output -> alert/watch-rule loop"
    Specify the first-build workflow, not a generic platform anthology. Every
    architecture, schema, UI, AI, API, realtime, and validation detail must name
    the exact work-intelligence entity or transition it supports. Prefer dense
    tables and concrete field/state lists over broad platform prose. Reusable
    storage, card, board, output, activity, dashboard, notification, AI, API,
    realtime, and browser-validation layers must be transformed into this
    lifecycle rather than appended as standalone reusable-module sections.

  Required output: one concise implementation specification with sections for
  first-build scope, local workspace/storage, signal/card/decision/delegation/
  output domain model, board lifecycle, monitoring triage, UI surfaces,
  automation guardrails, failure states, and acceptance proof for a complete
  signal-to-output session.


## Variable payload

{
  "app_name": "Work Intelligence Kanban",
  "topic_families": "- Framework-X, prompt languages, and specification-driven prompting.\n- Local-first AI tools and personal agent workspaces.\n- Agentic programming workflows, validation practices, and release-readiness examples.\n- UI/UX ideas for calm productivity and project command centers.\n- Research automation, recurring topic monitoring, and signal-to-action workflows.\n- Personal project opportunities, risks, deadlines, and follow-up items."
}



## Compiled output

# Work Intelligence Kanban — Implementation Specification

## 1. First-build scope

Build a local-first Kanban web app that turns recurring work-intelligence signals into reviewed cards, decisions, actions, delegations, typed outputs, alerts, and updated watch rules.

Target user: one local user or a small local workspace monitoring:
- Framework-X, prompt languages, and specification-driven prompting.
- Local-first AI tools and personal agent workspaces.
- Agentic programming workflows, validation practices, and release-readiness examples.
- UI/UX ideas for calm productivity and project command centers.
- Research automation, recurring topic monitoring, and signal-to-action workflows.
- Personal project opportunities, risks, deadlines, and follow-up items.

In scope for first build:
- One default local workspace with selectable workspace directory.
- SQLite-backed durable store with migrations, backup, export/import, and repair diagnostics.
- Topic/watch-rule management.
- compact signal capture and simulated/imported monitoring runs.
- Signal deduplication, triage scoring, provenance, and rejection/mute history.
- Kanban lifecycle from signal intake to output or archive.
- Mixed work-intelligence cards, not generic task cards.
- Decisions, actions, delegations, blockers, review queues, outputs, alerts, activity stream, dashboard, and local realtime updates.
- Inspectable AI suggestions with explicit external-call consent and rule-based fallback.
- REST API and Server Actions for local app behavior.
- Browser validation with Playwright MCP or equivalent.

Out of scope unless explicitly added later:
- Hosted multi-tenant backend, billing, subscriptions, organization onboarding, or shared tenant isolation.
- Serverless deployments with ephemeral/shared filesystems.
- Hidden cloud sync as source of truth.
- Unapproved external AI/web calls.
- Fully autonomous execution without visible trigger, confidence, undo/tuning variants, and audit history.

## 2. Stack and architecture

| Layer | Requirement |
| --- | --- |
| Framework | Next.js 14+ App Router. |
| Language | TypeScript 5+ strict mode; no `any`. |
| Styling | Tailwind CSS with design tokens in `tailwind.config.ts`; calm dense productivity UI. |
| React model | React Server Components by default; Zustand only for local UI state such as selected card, open panels, drag state, filters, and optimistic board movement. |
| Forms/validation | react-hook-form with shared zod schemas for UI, Server Actions, and API routes. |
| Backend runtime | Node.js runtime only for routes/actions touching SQLite; do not use Edge runtime there. |
| ORM/database | Prisma with SQLite provider; SQLite 3 WAL mode. |
| Reads/mutations | Server Components and local API reads; Server Actions or `/api/v1/...` routes for mutations. |
| Tests | Vitest + happy-dom for components; Vitest with temporary SQLite files for storage/API; Playwright for browser E2E. |
| Coverage | Minimum 80% line coverage for application logic. |
| Health | `GET /api/health` returns local store status, schema version, app version, migration state, and workspace path. |

Process model:
- One local app server owns SQLite writes.
- `DATABASE_URL` points to a local SQLite file under the active workspace or OS user-data directory.
- Startup validates env through `env.mjs`, checks workspace readability/writability, schema version, WAL mode, migrations, and backup policy.
- Pending migrations run on startup only after creating a timestamped backup when existing data is present.
- Unsupported future schema versions block startup with backup/upgrade guidance rather than rewriting the database.

## 3. Local workspace and storage

Default development path: `.local-data/work-intelligence-kanban.sqlite`; packaged apps SHOULD use the OS user-data directory.

Workspace directory contains:
- `database/app.sqlite`
- `attachments/`
- `outputs/`
- `exports/`
- `backups/`
- `repair-logs/`
- `manifest.json`

Storage rules:
- SQLite is canonical durable store.
- Browser `localStorage`, IndexedDB, memory, and cache files are disposable caches only.
- Large attachments and generated artifacts live as files under the workspace, not large database blobs by default.
- Attachment metadata records content hash, MIME type, size, origin, relative path, and corruption status.
- Every durable table has stable `id`, `createdAt`, `updatedAt`, `deletedAt`, and `version` or equivalent optimistic-concurrency field.
- Multi-entity writes that alter a signal/card/decision/action/output lifecycle run inside one transaction.
- Event insertion and visible state updates persist atomically when the event explains the state change.
- Index board/order queries, search filters, event replay, topic lookups, source dedupe, dependency lookup, stale-work queries, alert evaluation, and output lineage.

Required recovery behavior:
- Missing store initializes deterministically via migrations.
- Locked, corrupted, disk-full, unreadable, or too-new stores show recoverable errors with backup, repair, retry, or upgrade guidance.
- Export includes SQLite database, referenced files, schema version, app version, and manifest checksums.
- Repair preserves the original damaged database when possible and reports what changed.

## 4. Domain model

### Core entities

| Entity | Purpose | Required fields |
| --- | --- | --- |
| `Workspace` | Local source of truth. | `id`, `name`, `workspacePath`, `schemaVersion`, `appVersion`, `createdAt`, `updatedAt`. |
| `TopicFamily` | Broad monitoring family. | `id`, `name`, `description`, `intent`, `defaultCadence`, `createdAt`, `updatedAt`, `deletedAt`. |
| `WatchRule` | User-defined monitoring rule. | `id`, `topicFamilyId`, `name`, `query`, `subtopics`, `exclusions`, `sourceFamilies`, `intent`, `thresholds`, `muteRules`, `digestCadence`, `lastRunAt`, `enabled`, timestamps. |
| `MonitoringRun` | Dated monitoring cycle. | `id`, `watchRuleId`, `runDate`, `cadence`, `lookbackWindow`, `mode` (`news` or `events`), `sourceCoverage`, `gaps`, `status`, timestamps. |
| `Signal` | Captured external or compact work signal. | `id`, `watchRuleId`, `monitoringRunId`, `title`, `summary`, `sourceFamily`, `sourceName`, `authorOrOrg`, `urlOrLocalRef`, `retrievedAt`, `publishedAt`, `evidenceQuality`, `claimType`, `relevanceScore`, `noveltyScore`, `freshnessScore`, `confidenceScore`, `urgencyScore`, `impactScore`, `actionabilityScore`, `dedupeKey`, `status`, `rejectionReason`, timestamps. |
| `WorkCard` | Mixed work-intelligence card on board. | `id`, `kind`, `title`, `subtitle`, `body`, `state`, `columnId`, `sortOrder`, `priority`, `owner`, `nextStep`, `definitionOfDone`, `statusEvidence`, `sourceFamily`, `confidence`, `relevance`, `novelty`, `actionability`, `dueAt`, `seenAt`, `archivedAt`, timestamps. |
| `SignalCardLink` | Many-to-many provenance. | `signalId`, `cardId`, `relationship` (`origin`, `evidence`, `duplicate`, `contradicts`, `background`). |
| `Decision` | Explicit choice. | `id`, `cardId`, `decision`, `owner`, `rationale`, `alternativesConsidered`, `triggeringInputs`, `confidence`, `revisitCondition`, `decidedAt`, timestamps. |
| `ActionItem` | Committed or suggested action. | `id`, `cardId`, `decisionId`, `description`, `commitment` (`suggested` or `committed`), `owner`, `priority`, `timing`, `dependency`, `definitionOfDone`, `validationMethod`, `status`, timestamps. |
| `Delegation` | Work handed to another person/system. | `id`, `cardId`, `owner`, `request`, `expectedDeliverable`, `dueOrCheckInWindow`, `statusEvidence`, `blockers`, `followUpCadence`, `handoffContext`, `status`, timestamps. |
| `Blocker` | Blocking condition. | `id`, `cardId`, `actionId`, `delegationId`, `description`, `unblockOwner`, `evidenceNeeded`, `severity`, `status`, timestamps. |
| `OutputSurface` | Typed generated/user-created result. | `id`, `hostId`, `hostType`, `type`, `title`, `contentRef`, `schemaVersion`, `status`, `source`, `lineage`, timestamps. |
| `AlertRule` | Notification/watch condition. | `id`, `watchRuleId`, `name`, `condition`, `threshold`, `operator`, `cooldownWindow`, `channelPrefs`, `template`, `enabled`, `lastFiredAt`, timestamps. |
| `Notification` | In-app alert/digest item. | `id`, `alertRuleId`, `signalId`, `cardId`, `type`, `title`, `body`, `confidence`, `reason`, `nextAction`, `status`, `firedAt`, `dedupeKey`, timestamps. |
| `ActivityEvent` | Append-only audit stream. | `id`, `type`, `actor`, `targetType`, `targetId`, `timestamp`, `summary`, `payload`, `visibility`, `correlationId`, `traceId`. |
| `AiRun` | Inspectable AI suggestion or generation. | `id`, `provider`, `model`, `purpose`, `inputSummary`, `redactionSummary`, `outputSurfaceId`, `tokenUsage`, `estimatedCost`, `status`, `error`, timestamps. |

### Enumerations

| Field | Values |
| --- | --- |
| `Signal.claimType` | `confirmed_fact`, `reported_claim`, `announcement`, `opinion`, `forecast`, `rumor`, `background`, `speculative_lead`. |
| `Signal.status` | `new`, `deduped`, `triaged`, `muted`, `rejected`, `converted`, `watch_later`, `handled`, `archived`. |
| `WorkCard.kind` | `signal`, `insight`, `idea`, `task`, `decision_input`, `delegation`, `risk`, `opportunity`, `question`, `warning`, `output`, `watch_item`. |
| `WorkCard.state` | `intake`, `triage`, `investigate`, `decide`, `execute`, `waiting`, `review`, `shipped`, `watch_later`, `archived`, `rejected`, `blocked`. |
| `ActionItem.status` | `suggested`, `needs_confirmation`, `committed`, `in_progress`, `waiting`, `blocked`, `done`, `cancelled`. |
| `Delegation.status` | `draft`, `sent`, `waiting`, `blocked`, `received`, `accepted`, `rejected`, `follow_up_due`, `closed`. |
| `OutputSurface.type` | `text`, `program`, `table`, `diff`, `image`, `chart`, `status`, `log`, `terminal`, `form`, `canvas`, `file`, `decision_record`, `prompt`, `project_update`. |
| `OutputSurface.status` | `draft`, `streaming`, `complete`, `failed`, `stale`, `superseded`, `approved`. |
| `ActivityEvent.actor` | `human`, `agent`, `integration`, `system`, `automation`. |
| `AlertRule.operator` | `>`, `>=`, `<`, `<=`, `==`, `between`. |

## 5. Board lifecycle

Default columns:
1. `intake` — newly captured signals and compact ideas.
2. `triage` — relevance, novelty, evidence, confidence, urgency, impact, actionability review.
3. `investigate` — needs additional sources, context, or contradiction checks.
4. `decide` — ready for do/defer/delegate/research/merge/split/schedule/discard decision.
5. `execute` — committed action in progress.
6. `waiting` — delegated or blocked on external response.
7. `review` — output or decision needs human review.
8. `shipped` — produced visible output or completed project update.
9. `watch_later` — retained with future trigger/watch rule.
10. `archived` — deliberately closed, rejected, or retained for history.

Transition rules:
- `intake -> triage`: allowed after provenance exists.
- `triage -> investigate`: required when evidence quality/confidence is low or source gaps exist.
- `triage -> decide`: allowed when signal relevance and actionability are sufficient.
- `decide -> execute`: requires a committed `ActionItem` with owner, next step, and definition of done.
- `decide -> waiting`: requires a `Delegation` with owner, request, expected deliverable, check-in window, and handoff context.
- `execute -> review`: requires status evidence and at least one produced `OutputSurface` or explicit completion evidence.
- `review -> shipped`: requires approval or deliberate accept decision.
- Any active state -> `blocked`: requires blocker, unblock owner, and evidence needed.
- Any active state -> `watch_later`: requires revisit condition or updated `WatchRule`.
- Any active state -> `archived`: requires rationale: duplicate, irrelevant, handled, rejected, superseded, or no action.

Board interactions:
- Cards are scannable summaries with title, source/provenance, badges, score strip, owner/next step, due/check-in, output linkage, and visible state.
- Full detail panel shows provenance, evidence quality, related signals, decisions, actions, delegations, output surfaces, activity, AI suggestions, and watch-rule effects.
- Drag-and-drop has keyboard alternatives and validates allowed transitions before commit.
- Invalid moves explain the missing prerequisite at point of interaction.
- Reordering persists with optimistic update and rollback on conflict.
- Bulk actions support mute, merge duplicates, convert to cards, assign owner, archive, and create/update watch rule.
- Empty columns show useful creation/import/filter recovery actions.

## 6. Monitoring triage

Each monitoring run is a dated cycle with lookback window and mode (`news` or `events`). The run records:
- Run date.
- Cadence.
- Lookback window.
- Exact topic/watch rule.
- Mode.
- New items since last run.
- Still-important context.
- Source families searched/crawled.
- Monitoring gaps and unavailable coverage.

Triage obligations:
- Include only items relevant to the exact topic, audience, timing, and mode.
- Prefer developments within the lookback window.
- Separate new developments from evergreen background, recycled commentary, and duplicate coverage.
- Deduplicate same underlying event/idea across sources.
- Rank by relevance, novelty, evidence quality, timeliness, urgency, impact, and actionability.
- Separate high-confidence items from tentative leads.
- Preserve strongest source link and provenance for every surfaced item.
- Track rejected/muted/duplicate history when it improves future filtering.

News-mode priority:
- Official announcements and primary documents.
- Credible reporting with named entities and dates.
- Material developments within lookback.
- Contradictory evidence or skepticism that changes interpretation.
- Analysis that explains why the development matters.

Events-mode priority:
- Upcoming/current items inside the requested window.
- Official event pages, organizer pages, venue calendars, and local calendars.
- Date, time, location, cost, booking, cancellation, access, safety, and practical constraints.
- Alternatives by weather, energy level, budget, or distance when relevant.

## 7. Signal-to-output workflow

The app must answer:
- What came in?
- Why did it matter?
- What did I decide?
- Who is doing what?
- What is blocked?
- What changed because of this?
- Which outputs did this produce?

First-build happy path:
1. User creates or enables a `WatchRule` for a topic family.
2. A `MonitoringRun` imports or simulates candidate signals.
3. The app deduplicates and scores signals.
4. User opens a `Signal` in `triage`.
5. User converts it to a `WorkCard`.
6. User investigates evidence, links related signals, and records confidence/gaps.
7. User decides to act, delegate, watch later, merge, split, or archive.
8. If acting, user creates a committed `ActionItem`.
9. If delegating, user creates a `Delegation` with follow-up cadence.
10. User creates or reviews a typed `OutputSurface`.
11. The card moves through `review` to `shipped`, `watch_later`, or `archived`.
12. Alert/watch rules update based on user feedback.
13. Activity stream records every consequential transition.

Action-planning rules:
- Separate tasks, decisions, risks, open questions, and background.
- Prefer concrete next actions over vague intentions.
- Attach owner, sequence, due window, dependency, trigger, and validation whenever supported.
- Distinguish committed actions from suggestions.
- Flag actions needing confirmation.
- Keep first next step small enough to start immediately.
- Define validation: how the user knows the action worked.
- Include escalation/review points for high-risk or blocked work.

## 8. UI surfaces

### Primary layout

Responsive app shell:
- Left sidebar: workspace, topic families, saved views, settings.
- Top bar: global search, monitoring run status, AI/network consent indicator, notification center.
- Main board: Kanban columns with counts, WIP indicators, stale-work indicators, blocked indicators, and confidence warnings.
- Right detail panel: selected card, provenance, decisions, actions, delegations, outputs, activity.
- Dashboard view: metrics and charts.
- Settings view: workspace path, export/import, backup/restore, model/provider config, source families, alert rules, diagnostics.

### Card design

Card fields visible at rest:
- `title`
- `kind`
- source family badge
- confidence/relevance/novelty/actionability badges
- urgency/impact indicator
- owner and next step
- due/check-in indicator
- output linkage icon
- blocker/warning state
- unread/stale marker

Card states:
- selected, focused, expanded, disabled, loading, error, stale, unread.
- Pointer and keyboard access for all primary actions.
- Semantic labels, visible focus, sufficient contrast, and screen-reader text for icon-only variants.
- Drag preview, drop targets, cancellation behavior, undo, and conflict rollback.

### Typed output surfaces

Each surface supports appropriate renderer and actions:
- Text: Markdown/rich text, copy, export, approve.
- Program: syntax highlight, language, file path, copy/apply when repository integration exists.
- Table: sort/filter/export/schema validation.
- Diff: before/after, inline comments, approval workflow.
- Image/media: preview, zoom, download, alt text, provenance.
- Status: metrics, thresholds, progress, health, trend.
- Log/terminal: streaming, ANSI handling, search, pause, auto-scroll.
- Form: structured decisions/questions with validation.
- Canvas/diagram: nodes, edges, layout, zoom, export.

Streaming surfaces distinguish partial from final. Failed/stale surfaces explain cause and next action. Approvals, comments, and revisions preserve version history.

### Activity stream

Append-only by default. Each event has semantic type, actor, target, timestamp, summary, payload, visibility, correlation/trace ID. The stream supports:
- Pagination and incremental loading.
- Live append.
- Filters for event type, actor, severity, source, and errors.
- Compact routine entries and expandable significant entries.
- Relative and exact timestamps.
- Link/copy/reference for important events.
- Redaction without destroying audit metadata.
- No secrets, API keys, refresh tokens, or excessive raw sensitive payloads.

## 9. Dashboard and metrics

Dashboard widgets are responsive cards:
- 1 column mobile, 2 tablet, 3–4 desktop.
- Loading skeleton and error state with retry.
- Drag-to-reorder and show/hide persisted in local preferences.

Required widgets:
- Signal volume by topic and cadence.
- Conversion rate: signals to cards/actions/delegations/outputs.
- High-confidence warnings.
- Decisions pending.
- Stale ideas.
- Delegated work awaiting response.
- Blockers by owner/evidence needed.
- Outputs produced from monitored topics.
- Watch rules firing/muted.
- Source coverage and monitoring gaps.
- Recent activity and review queue.

Charts:
- Line chart for signal/action/output trends over time with zoom/pan.
- Bar chart for source family, topic, state, owner, or blocker comparisons.
- Donut/pie chart for card kinds, decision outcomes, or output surface types.
- Sparkline for compact widget trend indicators.
- All charts support dark/light theme, responsive resize, accessible palettes, hover tooltips with formatted values, and PNG export.

Tables:
- Sortable columns, shift-click multi-sort.
- Text search plus dropdown filters.
- Pagination: 10/25/50/100 rows with total count.
- Row actions: view detail, edit, archive/delete with confirmation.
- Bulk actions: select all, archive, export, mute, convert, assign.
- Empty state with recovery CTA.

Date ranges:
- Global date range picker with This Month, Last 30 Days, This Year, Custom.
- Applies to dashboard widgets and data tables.
- Locale-aware display.

## 10. Alerts and notifications

Alert rules contain condition, threshold, comparison operator, channel preference, cooldown, and action. Conditions evaluate after relevant signal/card/action/delegation/output events.

Supported channels:
- In-app toast for immediate feedback.
- Persistent notification center.
- Local digest view for daily/weekly summaries.
- Email/push are optional only if explicitly configured; local-first app must work without them.

Deduplication:
- Same alert rule must not fire more than once per evaluation period/cooldown.
- Track last-fired timestamp and dedupe key.

Alert content must explain:
- Why the item matters.
- What changed.
- Confidence level.
- Suggested next action.
- Source/watch rule that triggered it.
- How to mute, tune, or convert it.

Example templates use safe runtime placeholders, not Framework-X variables:
- `High-confidence signal: {{signalTitle}} changed {{topicName}}. Suggested next step: {{nextAction}}.`
- `Delegation follow-up due: {{owner}} for {{expectedDeliverable}} by {{checkInWindow}}.`
- `Watch rule {{watchRuleName}} fired because {{conditionSummary}}.`

Noise variants:
- Thresholds.
- Mute rules.
- Digest cadence.
- Feedback: useful, irrelevant, duplicate, already handled, watch later, converted into action.
- Learning from feedback must remain reversible and inspectable.

## 11. AI and automation guardrails

AI features:
- Signal summarization and claim separation.
- Duplicate/related signal suggestions.
- Relevance/novelty/confidence/actionability scoring explanation.
- Suggested next actions, decisions, delegations, blockers, output drafts, and watch-rule adjustments.
- Natural-language queries over local workspace data through structured query generation.
- Weekly/monthly insight generation for monitored topics and work outcomes.

LLM integration:
- Provider-agnostic abstraction for OpenAI, Anthropic, and local models.
- Configurable model name, temperature, max tokens, and system prompt per use case.
- Retry policy: exponential backoff 1s, 2s, 4s; max 3 retries for 429/500/503.
- Token usage and estimated cost logged per request.
- Graceful degradation: show `AI unavailable` badge and use rule-based fallback.
- User data is never used for training; include `data_policy: no_training` where supported.

Safety:
- External network/AI calls are explicit in UI and configuration.
- Before sending local content externally, show destination, purpose, included fields, and redaction summary.
- Sanitize LLM inputs and strip secrets/PII where possible.
- Do not store API keys, refresh tokens, secrets, or full sensitive payloads in logs.
- Suggestions are labeled separately from committed work.
- Automation must show trigger, inputs, confidence, proposed/taken action, undo, and tuning variants.
- Applying output to files, repositories, databases, or external systems must be explicit and auditable.

## 12. REST API and realtime

### REST standards

Base version: `/api/v1`.

Resource URLs are plural nouns with at most one nesting level:
- `/api/v1/workspaces`
- `/api/v1/topic-families`
- `/api/v1/watch-rules`
- `/api/v1/monitoring-runs`
- `/api/v1/signals`
- `/api/v1/cards`
- `/api/v1/cards/{id}/actions`
- `/api/v1/cards/{id}/delegations`
- `/api/v1/cards/{id}/outputs`
- `/api/v1/decisions`
- `/api/v1/alerts`
- `/api/v1/notifications`
- `/api/v1/activity-events`

Use query parameters for filtering/sorting/pagination:
`?status=active&sort=-created_at&page=1&per_page=20`

Responses:
- `Content-Type: application/json`
- Collections: `{"data": [...], "meta": {"total": N, "page": P, "per_page": S, "total_pages": T}}`
- Single resources: `{"data": {...}}`
- Empty collections return `{"data": [], "meta": {"total": 0, ...}}`, not 404.

Errors follow RFC 7807 Problem Details with statuses 400, 401, 403, 404, 409, 422, 429, 500. POST creates accept `Idempotency-Key`; same key within 24h returns original response. GET, PUT, DELETE are idempotent.

### Realtime

Use local WebSocket endpoint `ws(s)://host/ws`.

Message format:
- Client/server messages: `{"type": "...", "payload": {...}, "id": "uuid"}`
- Server ack: `{"type": "ack", "id": "..."}`
- Heartbeat: server sends `{"type": "ping"}` every 30s; client replies `{"type": "pong"}` within 10s.
- Resume: `{"type": "resume", "payload": {"last_event_id": "..."}}`
- Replay missed events since `last_event_id` up to 1000 events or 5 minutes.

Domain message types:
- `card_moved`
- `card_updated`
- `signal_triaged`
- `decision_recorded`
- `action_committed`
- `delegation_updated`
- `output_surface_updated`
- `alert_fired`
- `activity_appended`
- `error`

Presence is optional for first build, but if implemented uses `{"type": "presence", "payload": {"user_id": "...", "status": "online|offline"}}`.

Persist events before broadcasting live updates when the stream is an audit source.

## 13. Failure states

| Failure | Required UX/recovery |
| --- | --- |
| First-run missing store | Initialize workspace and migrations deterministically. |
| Store locked | Show retry, close-other-process guidance, and diagnostics. |
| Corrupted store | Offer backup, repair, export salvage, and preserve damaged original. |
| Future schema | Refuse startup; show app/schema versions and upgrade guidance. |
| Disk full | Abort transaction, preserve current state, explain cleanup/backup options. |
| Migration failure | Restore backup or keep pre-migration copy; show logs. |
| External AI unavailable | Show `AI unavailable`; use rule fallback; do not block local data access. |
| Network/source failure | Record monitoring gap; keep existing local data visible. |
| Duplicate signal | Link duplicate to canonical signal; preserve source history. |
| Low confidence signal | Require investigate or watch-later path before action. |
| Invalid board move | Explain missing prerequisite and keep card in original state. |
| Optimistic conflict | Roll back UI, refresh card, show conflict reason. |
| Delegation stale | Surface follow-up due without noisy repeated alerts. |
| Output generation failed | Keep failed surface with error summary and retry option. |
| Notification storm | Apply cooldown/dedupe and suggest threshold tuning. |
| Browser validation unavailable | State setup blocker; do not claim validation happened. |

## 14. Verification and acceptance proof

### Automated tests

Storage/API:
- First-run initialization.
- Restart persistence.
- Migration against older fixture once schema evolves.
- Backup/restore.
- Export/import with attachments and checksums.
- Transaction rollback for failed multi-entity lifecycle write.
- Database locking and corrupted-file detection where practical.
- Health endpoint.
- REST envelopes, pagination, Problem Details, idempotency.

Domain:
- Signal dedupe.
- Triage scoring and claim-type separation.
- Convert signal to card.
- Required transition prerequisites.
- Decision/action/delegation persistence.
- Output lineage.
- Alert cooldown/dedupe.
- Activity event ordering and correlation.
- Watch-rule feedback adjustment without irreversible hiding.

UI:
- Board render, empty/loading/error states.
- Keyboard and pointer card actions.
- Drag/drop and keyboard move validation.
- Detail panel, output surfaces, notification center, dashboard widgets.
- Accessibility labels, focus visibility, contrast, responsive layouts.

### Browser validation

Use Playwright MCP or equivalent browser automation. If unavailable, install/configure the official Playwright MCP server where possible, commonly with `npx @playwright/mcp@latest`. If setup cannot be completed, report the exact blocker and do not claim browser validation.

Required build-run-observe-improve loop:
1. Inspect spec, repository, scripts, tests, and framework conventions.
2. Implement smallest coherent browser-visible slice.
3. Start app using existing dev/preview command or add minimal project-appropriate command.
4. Open the URL with Playwright MCP.
5. Interact as a real user: create watch rule, import/simulate signal, triage, convert to card, move card, record decision, create action/delegation, create output, fire alert, update watch rule, export workspace.
6. Observe rendered page, accessibility tree, console, network, screenshots/traces, persisted state.
7. Fix defects and repeat until the main experience works without high-value obvious improvements.
8. Final report distinguishes verified behavior from unverified assumptions.

Evidence to leave:
- Command used.
- URL tested.
- Flows exercised.
- Screenshots/traces for board, detail panel, output surface, dashboard, notification center.
- Console/network/runtime errors found and resolved.
- Remaining limitations.

### End-to-end acceptance proof

A first build is complete only when a browser-verified session proves:

1. A user creates a local workspace and sees the active workspace path.
2. A watch rule for one monitored topic family is created.
3. A monitoring run captures at least three candidate signals with source provenance and gaps.
4. Duplicate/rejected/muted behavior is visible for at least one signal.
5. One high-value signal is triaged with relevance, novelty, confidence, urgency, impact, actionability, and claim type.
6. The signal becomes a `WorkCard`.
7. The card moves through `triage -> investigate -> decide`.
8. A decision records rationale, alternatives, confidence, and revisit condition.
9. The user creates either a committed action or delegation with owner, timing, dependency, and definition of done/check-in.
10. A typed output surface is created and linked to the signal/card/decision/action.
11. The card moves to `review` and then `shipped`, `watch_later`, or `archived` with rationale.
12. An alert or digest item explains what changed, why it matters, confidence, and next action.
13. The watch rule updates from user feedback.
14. Activity stream shows the full lineage.
15. Dashboard metrics reflect signal volume, conversion, decision/action/delegation/output state.
16. Restarting the app preserves all state.
17. Export/import recreates the workspace with database, files, manifest, and checksums.
18. No high-severity console/runtime errors remain.
