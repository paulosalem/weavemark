# Blind evaluation packet

Study: Intelligence-to-Execution Kanban
Variant: A
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# @{app_name}: Framework-X Work-Intelligence variant

@directive-c target: structure preserve: hard
  @directive-a programming/foundations/software-spec
    Mingle refinements into one implementation spec; no appendices.

  @directive-a programming/stacks/stack-typescript-nextjs-prisma-sqlite
  @directive-a programming/types/type-local-first-webapp

  Design @{app_name}: a local-first Kanban where monitored signals, ideas,
  decisions, delegations, actions, outputs, and future watch rules share one
  traceable card/board model.

  Use program/programming terms.

  @directive-b mode: intention focus: "monitoring -> evidence-backed cards -> decisions/delegations/outputs/alerts/reviews/watch rules"
    Topic monitoring becomes work execution.

  ## Lifecycle

  @directive-a domains/work-intelligence/topic-intelligence-monitor mingle: true
    Monitoring is board intake, not a separate feed.

  @directive-a domains/work-intelligence/signal-to-action-workflow mingle: true
    Every important signal needs a disposition.

  @directive-a domains/work-intelligence/idea-execution-workspace mingle: true
    Ideas carry owner, status, next action, review, and proof.

  @directive-a research/deep-web-source-discovery
  @directive-a research/news-event-triage
  @directive-a guidelines/news-quality

  Monitor these initial topic families:

  @{topic_families}

  ## Board and decisions

  @directive-a programming/modules/module-workflow-board
    Board states show signal-to-output progress.

  @directive-a programming/modules/module-card
    Cards are typed work-intelligence records.

  @directive-a guidelines/context-sufficiency
  @directive-a decision/strategy-selection
  @directive-a decision/forecast-uncertainty
  @directive-a lenses/comparative-alternatives
  @directive-a lenses/explainability

  ## Workspace, automation, and UI

  @directive-a programming/modules/module-local-sqlite-storage
  @directive-a programming/modules/module-context-attachments
  @directive-a programming/modules/module-output-surfaces
  @directive-a programming/modules/module-activity-stream

  @directive-a programming/modules/module-dashboard
  @directive-a programming/modules/module-notifications
  @directive-a programming/modules/module-ai-features
  @directive-a programming/modules/module-rest-api
  @directive-a programming/modules/module-realtime

  @directive-a product/product-validation-surface
    Prove signal -> reviewed card -> decision/action/delegation -> output ->
    notification -> archive/watch rule.

  ## Required output

  Produce one implementation spec covering architecture, schema, lifecycle,
  cards/boards, decisions, delegation, outputs, dashboards, alerts, APIs, live
  events, AI rules, provenance/privacy, failures, validation, and acceptance.


## Variable payload

{
  "app_name": "Work Intelligence Kanban",
  "topic_families": "- Framework-X, prompt languages, and specification-driven prompting.\n- Local-first AI tools and personal agent workspaces.\n- Agentic programming workflows, validation practices, and release-readiness examples.\n- UI/UX ideas for calm productivity and project command centers.\n- Research automation, recurring topic monitoring, and signal-to-action workflows.\n- Personal project opportunities, risks, deadlines, and follow-up items."
}



## Compiled output

# Work Intelligence Kanban: Implementation Specification

Use this implementation-ready software specification to build **Work Intelligence Kanban**, a local-first Kanban application where monitored signals, ideas, decisions, delegations, actions, outputs, future watch rules, alerts, reviews, and archives share one traceable card/board model.

Use this specification as the source of truth for a programming agent. Use concrete program/programming terms. Use MUST/SHOULD/MAY deliberately. State safe assumptions and the smallest set of genuinely blocking open decisions. Separate product behavior from implementation details while making both precise enough to build.

## Product intent

Define Work Intelligence Kanban as a local-first work-intelligence workspace that turns recurring monitoring into execution:

- Topic monitoring becomes board intake, not a separate feed.
- Every important signal needs a disposition: reject, mute, watch later, investigate, convert to idea, convert to decision input, delegate, act, output, archive, or create/update a watch rule.
- Ideas carry origin, owner, status, next action, review point, evidence, and proof of outcome.
- The app must answer: “What came in?”, “Why did it matter?”, “What did I decide?”, “Who is doing what?”, “What is blocked?”, “What changed because of this?”, and “Which outputs did this produce?”

Initial monitored topic families:

- Framework-X, prompt languages, and specification-driven prompting.
- Local-first AI tools and personal agent workspaces.
- Agentic programming workflows, validation practices, and release-readiness examples.
- UI/UX ideas for calm productivity and project command centers.
- Research automation, recurring topic monitoring, and signal-to-action workflows.
- Personal project opportunities, risks, deadlines, and follow-up items.

## First-build boundaries

Specify a credible first build:

- Local-first, single-user or one local workspace by default.
- No hosted multi-tenant backend, subscriptions, billing, organization onboarding, or tenant isolation unless explicitly marked later.
- The local machine is the source of truth. Browser-only storage may cache UI state but must not be canonical for user data.
- Existing local data must remain loadable when external AI, search, or integration calls fail.
- External network calls must be explicit in the UI and configuration; before sending local content to external AI/web services, show destination and purpose.
- Private data stays local by default. Logs must not store secrets, API keys, refresh tokens, or full sensitive payloads unless the user enables diagnostic capture.

## Required architecture and stack

Specify architecture for:

- Next.js 14+ App Router.
- TypeScript 5+ strict mode, no `any`.
- Tailwind CSS with design tokens in `tailwind.config.ts`.
- React Server Components by default; Zustand only for local client UI state that needs it.
- react-hook-form with zod validation schemas shared with API and Server Actions.
- Server Actions for mutations; `fetch` in Server Components for reads.
- Node.js runtime only for routes/actions that touch SQLite; do not use Edge runtime for SQLite paths.
- Prisma with SQLite provider.
- `DATABASE_URL` pointing to a local SQLite file under the active workspace or OS user-data directory.
- One local app server owns SQLite writes; if packaged for desktop use, the desktop shell starts and supervises that server.
- Environment validation via `env.mjs` with zod at startup.
- `GET /api/health` returning local store status, schema version, and app version.

Include major components, data flow, extension points, local server boundaries, and failure behavior.

## Local workspace and storage

Specify a workspace model:

- One default local workspace; user can choose/create another workspace directory.
- Store SQLite database, attachments, generated artifacts, backups, exports, derived files, repair logs, and manifests under the workspace/data directory.
- Show active workspace path in settings and diagnostics.
- Provide export/import so a workspace moves between machines without hidden server state.
- Startup validates readability, writability, schema version, migration status, and SQLite availability.
- Missing store initializes deterministically with migrations.
- Locked, corrupted, disk-full, unreadable, or future-version store shows recoverable backup/repair/upgrade guidance.

Specify SQLite/Prisma rules:

- SQLite 3 in WAL mode.
- Prisma Migrate.
- Run pending migrations on startup after creating a timestamped backup when existing data is present.
- camelCase Prisma fields mapped to snake_case table/column names where practical.
- Every durable table has stable primary key, `createdAt DateTime @default(now())`, `updatedAt DateTime @updatedAt`, deletion/archive behavior, and optimistic concurrency via `version` or `updatedAt` where agent/collaboration writes can occur.
- Recoverable entities use `deletedAt DateTime?` when appropriate.
- Multi-entity updates run in explicit transactions.
- Event insertion and visible state updates persist in the same transaction when the event explains the state change.
- Use indexes for board/order queries, search filters, event replay, dependency lookups, source deduplication, stale work, due dates, and watch-rule evaluation.
- Large attachments/artifacts are files by default, not large DB blobs. SQLite stores metadata, content hash, MIME type, size, origin, relative path, and host relation.
- Exports include SQLite database, referenced files, schema version, app version, and manifest checksums.
- Repair tools report changes and preserve the original damaged database when possible.

## Domain model

Define entities, fields, relations, identifiers, indexes, lifecycle states, and invariants for at least:

- `Workspace`
- `TopicFamily`
- `Topic`
- `WatchRule`
- `Source`
- `MonitoringRun`
- `Signal`
- `Evidence`
- `Card`
- `Board`
- `BoardColumn`
- `BoardView`
- `Idea`
- `Decision`
- `Alternative`
- `Forecast`
- `Delegation`
- `Action`
- `OutputSurface`
- `Attachment`
- `ActivityEvent`
- `NotificationRule`
- `Notification`
- `AiRun`
- `AiSuggestion`
- `UserPreference`
- `ExportManifest`

Cards are typed work-intelligence records, not generic tasks. Define required and optional card fields:

- stable `id`
- semantic `type` or `kind`
- `title`
- `subtitle` or `summary`
- `body`
- priority, urgency, relevance, novelty, confidence, impact, actionability, evidence quality, source family, status, owner, due/check-in window, blocked state, unread/stale state, and review cadence
- `metadata`
- `actions`
- `links`
- timestamps: created, updated, seen, due, archived
- provenance links to signals, evidence, decisions, actions, delegations, outputs, attachments, AI runs, and activity events
- UI state: selected, focused, expanded, disabled, loading, error, stale, unread

Distinguish signal, insight, idea, task, decision, experiment, question, opportunity, risk, delegation, reminder, project, watch item, warning, and output artifact rather than forcing all items into a single task model.

## Board lifecycle

Specify default board states and allowed transitions. The board stages should show signal-to-output progress:

- intake
- triage
- investigate
- decide
- execute
- waiting
- review
- shipped
- watch later
- archived

For each stage, define purpose, entry conditions, exit conditions, required fields, validation rules, side effects, and failure states.

Movement requirements:

- Columns/groups have stable identifiers, display names, ordering, and optional descriptions.
- Support default system layout and user-customized saved views/filters.
- Drag-and-drop has keyboard alternatives.
- Reordering persistence, conflict handling, and optimistic rollback are defined.
- Invalid moves show the reason at the interaction point.
- Transitions may trigger assignment, notification, automation, review, approval, archive, escalation, or watch-rule update.
- Empty columns and empty boards have useful states and creation/filter recovery actions.
- Bulk operations, search, filter, sort, duplicate, archive/delete, and saved views are specified.

Board metrics should include signal volume, conversion rate, stale ideas, delegated work awaiting response, high-confidence warnings, decisions pending, outputs produced from monitored topics, throughput, bottlenecks, aging, ownership, and attention needs.

## Monitoring and source discovery

Specify recurring monitoring cycles:

- Each run has run date/timestamp, cadence, lookback window, exact topic, mode (`news` / `events` / domain custom), source coverage, new items, still-important context, gaps, and omissions.
- Separate genuinely new developments from background context, evergreen references, recycled commentary, duplicate coverage, and stale material.
- Prefer items changed within the lookback window.
- Preserve why each item matters to the user’s work.

Support topic configuration:

- topics, subtopics, exclusions, regions, organizations, people, projects, products, markets, technologies, communities
- intents: risks, opportunities, deadlines, competitor movement, funding, product releases, regulation, research, events, project-relevant ideas
- source-family preferences/exclusions: official pages, feeds, newsletters, journals, repositories, social posts, community forums, calendars, press releases, podcasts, videos, saved files

Specify deep source discovery:

- Start with diverse query families, not one query.
- Search recent/breaking, primary/official, expert/practitioner, local/domain-specific, skeptical/contrary, and roundup/index sources where relevant.
- Crawl selected first-level sources; inspect full context instead of snippets.
- Extract useful links and crawl second-level sources when they add original evidence.
- Use `depth 1`, `depth 2`, and rare `depth 3` discipline; the goal is deeper evidence, not more pages.
- Stop when additional pages are redundant, stale, inaccessible, or lower-value.
- Deduplicate syndicated stories, mirrored event listings, reposts, low-signal aggregators, duplicate coverage, and repeated underlying events.
- Preserve provenance for every material claim: source title, URL/local reference, author/organization when known, retrieved time, published time, evidence quality, and whether evidence came from search snippet, crawled text, file, or compact entry.

News/event triage requirements:

- Rank by user relevance, novelty, evidence quality, timeliness, freshness, confidence, urgency, potential impact, practical actionability, and decision impact.
- Separate confirmed facts, reported claims, announcements, opinions, forecasts, rumors, speculation, tentative leads, repeated background, and rejected/muted signals.
- Include only items relevant to exact topic, audience, geography, timing, and mode.
- For news, prioritize material developments, official announcements, credible reporting with named entities/dates, analysis that explains why it matters, and contradictory/skeptical evidence that changes interpretation. Avoid generic explainers, SEO posts, duplicate syndicated stories, thin commentary, and claims without credible traceable sources.
- For events, prioritize upcoming/current events with official event pages, venue calendars, organizer pages, practical date/time/location/cost/booking/cancellation/safety details, and alternatives. Avoid past events unless next recurrence is clear, vague unsourced activities, and unsuitable items.

News quality:

- Present relevant facts clearly and informatively.
- Include historical context, timelines, comparisons, and what changed.
- Use concrete named entities.
- Present benefits, risks, uncertainties, trade-offs, winners/losers, and relevant stakeholder perspectives.
- Distinguish evidence from claims.
- Explain why the story matters now.
- Avoid clickbait, shallow summaries, fear/outrage framing, boilerplate repetition, alarm inflation, or false confidence.

## Signal-to-action workflow

Specify end-to-end workflows:

1. Configure topic/watch rule.
2. Run monitoring.
3. Capture signal with evidence and provenance.
4. Deduplicate and score.
5. Triage into board intake.
6. Convert signal into insight, idea, decision input, action, delegation, warning, output, watch item, or archive decision.
7. Investigate with attachments and source links.
8. Decide using alternatives, uncertainty, rationale, owner, confidence, and revisit trigger.
9. Execute action or delegation.
10. Review status evidence.
11. Produce typed output surface.
12. Notify user.
13. Archive or create/update watch rule.
14. Preserve complete trace from input to output.

A signal may become an insight, idea, task, question, watch item, warning, decision input, delegation, project risk, or output artifact. An idea may link back to many signals and forward to many actions/outputs. Completed outputs record which signals, ideas, decisions, actions, attachments, and AI runs contributed.

Feedback loop:

- User can mark signals useful, irrelevant, duplicate, already handled, watch later, converted into action, muted, or rejected.
- Feedback adjusts future relevance/alert behavior without hiding provenance or making irreversible filtering decisions.
- Preserve rejected/muted signal history when useful for future filtering.
- Track whether signals led to decisions, delegations, artifacts, project changes, discarded ideas, or watch rules.

Automation requirements:

- Suggestions are distinct from committed work.
- Suggest next actions, merging duplicates, linking related items, escalating warnings, creating reminders, converting insights into outputs, and updating watch rules.
- Automation remains inspectable: show trigger, inputs, confidence, action proposed/taken, undo, and tuning variants.

## Decisions, alternatives, and uncertainty

Specify decision support directly in cards and detail views:

- Classify decision shape: reversible, irreversible, adversarial, forecast-heavy, portfolio, values-heavy, option-preserving.
- Choose method because it changes the recommendation.
- Preserve optionality when information value is high and delay is cheap.
- Recommend commitment when delay is costly and uncertainty cannot be resolved.
- Make next action proportional to stakes and reversibility.
- Track what evidence would flip the decision.

Decision records include:

- decision shape and reasons
- chosen method
- decisive uncertainties
- option set: choices, hybrids, deferrals, probes, no-action baseline
- alternatives considered
- rationale
- triggering inputs
- decision owner
- confidence
- revisit condition
- reversal/escalation triggers
- recommended next move
- review point

Forecast support includes:

- known facts, assumptions, forecasts, and preferences separated
- forecast variables
- base case / upside / downside scenarios with triggers
- ranges instead of false precision
- base-rate reasoning where relevant
- leading indicators/signposts
- correlation/dependency between uncertainties
- robust action and contingent action
- review cadence

Comparative alternative views should expose leading option, runner-up, decisive criterion, confidence (`low | medium | high`), criterion-by-option comparison, best-if/avoid-if notes, and ranking trigger.

Explainability views should start with conclusion and show reasoning chain: step, claim/inference, evidence/basis, confidence; then assumptions, checks performed, limits, and simplest explanation.

Context sufficiency:

- Classify high-impact recommendations as `sufficient`, `limited`, or `insufficient` when this changes how the user should use the answer.
- If limited, explain gaps and caveat output.
- If insufficient, avoid action recommendations, provide scoping output, missing inputs, and smallest next evidence.
- Do not silently infer missing values that materially affect conclusions.

## Delegation, actions, blockers, and review

Specify action-planning behavior:

- Separate tasks, decisions, risks, open questions, and background information.
- Prefer concrete next actions over vague intentions.
- Attach owner, sequence, due/check-in window, dependency, trigger, and definition of done whenever supported.
- Distinguish committed actions from suggested actions.
- Flag actions needing confirmation before execution.
- Keep first next step small enough to start immediately.
- Include validation, escalation, and review points.

Delegations track:

- owner
- request
- expected deliverable
- due/check-in window
- status evidence
- blockers
- follow-up cadence
- handoff context
- source signals/ideas/decisions
- last contact and next reminder

Blocked work shows blocker, unblocker, status evidence needed, and escalation path.

Repeatedly ignored ideas, stale delegations, unresolved decisions, and missing proofs should become visible without notification noise.

## Attachments and provenance

Specify attachment model and UX:

Each attachment has `id`, `host_id`, `type`, `title`, `source`, `content_ref`, `mime_type`/format, `size`, checksum, `created_by`, `created_at`, provenance, and permissions.

Support file, URL, text, image, table, artifact, reference, related entity, and domain-specific attachments.

UX requirements:

- previews for common types
- graceful unsupported/unavailable previews
- rename, reorder, remove, download, copy link, open
- related-entity navigation with relationship direction
- visible states for large uploads, failed uploads, scans, broken URLs, expired refs, missing/deleted files, oversized attachments

Agent/AI use:

- Define which attachment types agents may read and how they receive content.
- Preserve source provenance for citations.
- Do not silently include sensitive attachments in AI context.
- Store extracted text, thumbnails, embeddings, and summaries as traceable derived artifacts.

## Output surfaces

Specify typed output surfaces instead of one undifferentiated text area.

Each surface has `id`, `host_id`, `type`, `title`, `content` or content reference, `schema_version`, `status`, `source`, timestamps, lineage, and actions.

Include surface types and interactions:

- text: safe Markdown/rich text
- program: syntax-highlighted implementation text with language/file path/copy/apply actions when repository integration exists
- table: schema validation, sorting, filtering, export
- diff: before/after comparison, comments, approval
- image/media: preview, gallery, zoom, download, alt text, provenance
- status: metrics, thresholds, progress, health, trend
- log/terminal: streaming, ANSI handling, search, pause, auto-scroll
- form: structured questions/decisions with validation
- canvas/diagram: nodes, edges, layout, zoom, export

Surfaces are orderable, pinnable, minimizable, openable in detail, commentable, approvable, versioned, and lineage-aware. Streaming surfaces distinguish partial from final. Failed/stale surfaces explain recovery. Applying a surface externally is explicit and auditable.

## Activity stream and audit

Specify append-oriented activity events for cards, runs, decisions, actions, delegations, outputs, attachments, AI runs, automations, notifications, and workspace changes.

Each event has `id`, `type`, `actor`, `target`, `timestamp`, `summary`, `payload`, `visibility`, and `correlation_id` or `trace_id`.

Requirements:

- Persist events before broadcasting when the stream is an audit source.
- Support pagination, incremental loading, live append, filters by event type/actor/severity/source/errors, and linkable/copyable events.
- Compact routine entries; richer expandable entries for significant events.
- Distinguish human, agent, automation, integration, system, error, decision, and output-update events visually but calmly.
- Show relative and exact times.
- Preserve chronological clarity when events arrive out of order or replay after reconnect.
- Avoid logging secrets or excessive raw internals.
- For agentic systems, record enough lineage to connect prompts, tool calls, artifacts, questions, answers, and final outputs.
- Define retention, export, redaction, and privacy behavior.

## Dashboard and UI

Specify screens and UI states:

- Workspace setup/settings.
- Topic and watch-rule management.
- Monitoring run history.
- Kanban board.
- Card detail panel.
- Evidence/source drawer.
- Decision/alternative/forecast panel.
- Delegation/action tracker.
- Output surfaces.
- Notification center.
- Dashboard.
- Activity stream.
- Import/export/backup/repair diagnostics.

Card UI:

- clear purpose: summary, action, monitoring, comparison, preview, status display, or mixed
- scannable at rest, detailed through expansion/navigation/detail panel
- compact but information-rich for board columns
- visual hierarchy: title, high-value summary, metadata, actions
- responsive in narrow columns, dense grids, and detail panes
- empty, loading, error, stale, permission-limited states
- calm visual design; color/badges/icons clarify grouping/status/action only

Interactions:

- pointer and keyboard access for primary actions
- unambiguous click, double-click, drag, context menu, checkbox selection, inline editing
- focus styles, selection affordance, drag preview, drop targets, cancellation
- persistence and undo for expand, pin, archive, dismiss, reorder
- semantic labels, visible focus, sufficient contrast, screen-reader text for icon-only variants

Dashboard:

- responsive grid: 1 column mobile, 2 tablet, 3–4 desktop
- widgets as cards with title bar, content, optional action menu
- loading skeleton and retryable error state
- drag-to-reorder and show/hide widgets persisted to preferences
- charts for monitoring volume, conversion rate, stale work, outcomes by topic, alerts over time, delegation aging, confidence distribution, and output production
- line, bar, donut/pie, and sparkline chart support where useful
- dark/light theme, responsive resize, accessible palettes, formatted tooltips, export as PNG
- sortable/filterable/paginated data tables with row actions, bulk selection/export/delete, and useful empty states
- global date range picker with presets and custom range; locale-aware dates

## Notifications and alerts

Specify an alerts engine:

- Users define watch/notification rules with condition, threshold, comparison operator, action, cadence, scope, and cooldown.
- Supported operators: `>`, `>=`, `<`, `<=`, `==`, `between`.
- Conditions evaluate after relevant monitoring runs, signal triage, card changes, due/check-in changes, delegation updates, and output events.
- Same alert rule must not fire more than once per evaluation period/cooldown; track last-fired timestamp.
- Channels: in-app toast, persistent notification center, optional email digest/immediate critical alerts, optional web push via Service Worker + VAPID keys.
- Alerts explain why the item matters, what changed, confidence, source/evidence, and next action.
- Noise is controlled through thresholds, mute rules, feedback, digest cadence, and grouping.
- Templates support variable substitution and locale-aware formatting.
- Notifications link to the exact card, signal, rule, decision, delegation, or output that caused them.

## AI and automation

Specify provider-agnostic AI integration:

- interface supports OpenAI, Anthropic, and local models
- configurable model name, temperature, max_tokens, system prompt per use case
- retry policy: exponential backoff 1s, 2s, 4s, max 3 retries on 429/500/503
- cost/token tracking per request
- `data_policy: no_training` where supported
- sanitize/redact sensitive content before external calls
- rate limits per local policy/configuration
- graceful fallback with “AI unavailable” badge and rule-based fallback

AI features should include:

- signal deduplication assistance
- relevance/actionability scoring suggestions
- topic/watch-rule suggestions
- natural language board/search queries parsed to structured query, executed, and formatted
- weekly/daily digest generation
- decision/alternative/forecast draft support
- output-surface draft generation
- stale-work and next-action suggestions
- provenance-aware summaries that cite evidence

All AI outputs are suggestions until accepted. Show prompt inputs, attachments used, evidence links, confidence, limits, cost, and activity trace where useful.

## REST API

Specify internal REST API routes using standards:

- plural nouns under `/api/v1/...`
- nesting limited to one level
- query parameters for filtering, sorting, pagination: `?status=active&sort=-created_at&page=1&per_page=20`
- `Content-Type: application/json`
- collection response envelope: `{"data": ..., "meta": {...}}`
- single resource envelope: `{"data": ...}`
- pagination meta: `{"total": N, "page": P, "per_page": S, "total_pages": T}`
- empty collections return `{"data": [], "meta": {"total": 0, ...}}`, never 404
- Problem Details errors following RFC 7807
- status codes: 400, 401, 403, 404, 409, 422, 429, 500
- POST create endpoints accept `Idempotency-Key`; repeated key within 24 hours returns original response
- GET, PUT, DELETE are idempotent
- breaking changes increment API version; additive changes may stay on current version

Define route groups for health, workspaces, topics, watch rules, monitoring runs, sources, signals, cards, boards/views/columns, decisions, alternatives, forecasts, actions, delegations, output surfaces, attachments, activity events, notifications, AI runs/suggestions, exports/imports, backups, and search.

## Realtime events

Specify realtime protocol for live local updates:

- WebSocket endpoint `ws(s)://host/ws`.
- Authentication/session token in first message or query param as appropriate for local app.
- Message format: JSON `{"type": "...", "payload": {...}, "id": "uuid"}`.
- Server sends `{"type": "ack", "id": "..."}` for every client message.
- Heartbeat: server sends `{"type": "ping"}` every 30 seconds; client responds `{"type": "pong"}` within 10 seconds or connection closes.
- Reconnection uses exponential backoff 1s, 2s, 4s, 8s, max 30s.
- Client resumes with `{"type": "resume", "payload": {"last_event_id": "..."}}`.
- Server replays missed events since `last_event_id` up to a bounded limit.
- Broadcast card movement, content updates, comments, monitoring run status, AI run status, activity events, notifications, output-surface updates, and presence when useful.
- Define event names, payloads, ordering guarantees, persistence-before-broadcast, replay behavior, idempotency, and error messages.
- Include calm UI handling for reconnecting, stale state, replay, and optimistic rollback.

## Non-functional requirements

Specify performance, reliability, privacy, security, observability, portability, and maintainability:

- first-run initialization, restart persistence, offline operation, and workspace switching
- local data remains available without network
- explicit backup before destructive migrations/repair
- bounded monitoring run concurrency and cancellation
- deterministic deduplication and transactional state changes
- accessible keyboard operation for board/card flows
- responsive behavior for narrow columns and large boards
- safe rendering for Markdown/content surfaces
- no secrets in logs
- clear diagnostics and health status
- maintainable module boundaries and shared zod schemas
- minimum 80% line coverage for application logic

## Testing and verification

Specify tests:

- Vitest with happy-dom for component tests.
- Vitest with temporary SQLite files and isolated data directories for API/storage.
- Playwright for critical local flows.
- Migration tests from at least one older schema fixture once schema evolves.
- Backup/restore and export/import with attachments.
- Transactional rollback for failed multi-entity writes.
- Database locking, disk-full handling where practical, corrupted-file detection.
- First-run initialization, restart persistence, offline operation.
- Upload/link/add/remove attachment flows, missing/deleted/expired/oversized attachments.
- Permission/policy-limited AI context inclusion.
- Activity history when attachment-derived or AI-derived context affects output.
- REST envelopes, RFC 7807 errors, idempotency, pagination.
- WebSocket ack/heartbeat/reconnect/resume/replay.
- Board movement validation, keyboard alternatives, optimistic rollback.
- Monitoring deduplication, relevance scoring, source provenance, gaps.
- Notification cooldown/deduplication.
- End-to-end proof: signal → reviewed card → decision/action/delegation → output → notification → archive/watch rule.

## Product validation surface

Include:

1. First successful user session:
   - create/select workspace
   - configure at least one topic family and watch rule
   - run/import a monitoring cycle
   - triage a signal into a card
   - add evidence/attachment
   - choose a disposition
   - create a decision/action/delegation
   - produce an output surface
   - receive notification
   - archive or create/update a watch rule
2. State coverage:
   - empty, active, loading, streaming, error, recovery, stale, repeated-use states
3. Evidence checklist:
   - screenshots, persisted records, activity events, provenance links, exported workspace, output artifact, notification, test trace
4. Failure probes:
   - invalid input, duplicate signal, missing context, stale source, network failure, AI unavailable, locked DB, failed migration, corrupt attachment, conflicting board move, expired watch rule
5. Release gate:
   - credible first public demo criteria tied to user value, not only technical completion

## Acceptance criteria

The implementation spec is complete only if it covers architecture, schema, lifecycle, cards/boards, decisions, delegation, outputs, dashboards, alerts, APIs, live events, AI rules, provenance/privacy, failures, validation, and acceptance criteria in one coherent artifact. It must be directly actionable by a programming agent and must not read like a brainstorm, interview plan, or append-only anthology.
