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

Build a local-first TypeScript/Next.js Kanban for a single user or local workspace that converts monitored topic signals into reviewed cards, decisions, actions, delegations, typed outputs, alerts, and updated watch rules.

Monitor these topic families:
- Framework-X, prompt languages, and specification-driven prompting.
- Local-first AI tools and personal agent workspaces.
- Agentic programming workflows, validation practices, and release-readiness examples.
- UI/UX ideas for calm productivity and project command centers.
- Research automation, recurring topic monitoring, and signal-to-action workflows.
- Personal project opportunities, risks, deadlines, and follow-up items.

## 1. First-build scope

### Product intent
- Help the user answer: What came in? Why did it matter? What did I decide? Who is doing what? What is blocked? What changed because of this? Which output did it produce?
- Preserve the full path from external signal to local work output; do not split monitoring, ideas, tasks, and artifacts into disconnected modules.
- Optimize for one product-shaped loop: signal capture → reviewed card → decision/action/delegation → output → alert or watch-rule update.

### In scope
| Area | First-build requirement |
| --- | --- |
| Local workspace | Choose/create a workspace directory; store SQLite DB, attachments, generated artifacts, backups, repair logs, exports, and manifest files under it. |
| Monitoring | Create topic rules for the listed topic families; run dated monitoring cycles with cadence, lookback window, source families, gaps, and omissions. |
| Signal triage | Capture provenance, deduplicate repeated coverage, classify evidence, score relevance/novelty/freshness/confidence/urgency/impact/actionability. |
| Kanban cards | Cards are mixed work-intelligence objects, not generic tasks. They may represent signals, insights, ideas, questions, risks, decisions, delegations, actions, outputs, warnings, or watch items. |
| Board lifecycle | Columns: Intake, Triage, Investigate, Decide, Execute, Waiting, Review, Shipped, Watch Later, Archived. |
| Decisions and delegations | Track rationale, alternatives, owner, confidence, revisit condition, request, expected deliverable, due/check-in window, blockers, follow-up cadence, and handoff context. |
| Output surfaces | Render outputs as typed surfaces: text, table, diff, status, log, file, chart, form, or custom domain surface; preserve lineage to signals/cards/actions/prompts/tools/files. |
| Activity stream | Append-only event history for monitoring runs, card transitions, decisions, automations, outputs, alerts, watch-rule edits, errors, and validation evidence. |
| Alerts | In-app toasts and persistent notification center; digest view; thresholds, mute rules, cooldowns, and user feedback. |
| AI assistance | Optional, explicit LLM calls for summarization, triage suggestions, next-action suggestions, duplicate detection, watch-rule proposals, and digest generation. |
| API/realtime | Local REST API and WebSocket updates for board/card/activity/output changes. |
| Validation | Unit, storage, API, E2E, and browser-grounded Playwright MCP validation proving a complete signal-to-output session. |

### Out of scope for first build
- Hosted multi-tenant backend, billing, subscriptions, organization onboarding, and serverless deployments with ephemeral/shared filesystems.
- Email/push notification delivery unless explicitly added later; first build uses in-app notifications and digest.
- Automatic external posting or applying outputs to external systems; applying/exporting must remain explicit and auditable.
- Browser-only canonical storage. Browser storage may cache UI preferences only.

## 2. Tech stack and architecture

### Required stack
| Layer | Requirement |
| --- | --- |
| Frontend | Next.js 14+ App Router, TypeScript 5+ strict mode, no `any`, Tailwind CSS with design tokens in `tailwind.config.ts`. |
| React model | Server Components by default; client components only for board drag/drop, local UI state, forms, toasts, realtime subscriptions, and interactive surfaces. |
| State | Zustand for local UI state only; SQLite is canonical. |
| Forms/validation | react-hook-form plus zod schemas shared by client, Server Actions, and API routes. |
| Backend runtime | Node.js runtime only for routes/actions touching SQLite; do not use Edge runtime. |
| ORM/database | Prisma with SQLite provider, SQLite 3 WAL mode, Prisma Migrate. |
| Data fetching | Server Actions for mutations; Server Components and local API fetches for reads. |
| Config | `env.mjs` with zod startup validation. `DATABASE_URL` points to a local SQLite file under the active workspace or OS user-data directory. |
| Health | `GET /api/health` returns local store status, schema version, app version, workspace path, WAL status, and migration status. |
| Target | Local Node.js process, self-hosted single-user service, or optional Electron/Tauri wrapper. |

### Component/data flow
1. Startup validates workspace readability/writability, supported schema version, migrations, WAL mode, and repair/backup status.
2. Monitoring run creates `monitoring_runs`, `source_snapshots`, candidate `signals`, `signal_claims`, and activity events in one transaction per imported batch.
3. Triage service deduplicates, scores, classifies, and creates or updates `work_cards`.
4. Board UI reads saved view filters, columns, counts, WIP indicators, stale/blocked markers, and alert badges.
5. User decides, delegates, executes, reviews, archives, or ships from card detail and board transitions.
6. Output surfaces are created under cards and linked to contributing signals, decisions, actions, prompts, tools, and files.
7. Watch-rule feedback updates future monitoring behavior without hiding provenance or making irreversible filtering decisions.
8. Activity stream persists before WebSocket broadcast.

## 3. Local workspace and SQLite storage

### Workspace contract
- One default local workspace; user can choose or create another directory.
- Show active workspace path in settings and diagnostics.
- Store under the workspace:
  - `.local-data/app.sqlite` in development or OS user-data equivalent when packaged.
  - `attachments/`, `artifacts/`, `backups/`, `exports/`, `repair-logs/`, `logs/`.
- External calls must be explicit in UI and configuration; existing local data must load when network/AI calls fail.
- Private data remains local by default. Before sending content to AI/web/integration services, show destination, purpose, payload preview/scope, and user-controlled confirmation or saved permission.
- Logs must not store secrets, API keys, refresh tokens, or full sensitive payloads unless diagnostic capture is explicitly enabled.

### Database requirements
- Every durable entity has `id`, `createdAt`, `updatedAt`, `deletedAt?`, and optimistic concurrency via `version` or `updatedAt`.
- Use camelCase Prisma fields mapped to snake_case table/column names where practical.
- Multi-entity changes use explicit Prisma transactions.
- Event insertion and visible state updates are persisted in the same transaction when the event explains the state change.
- App runs pending migrations on startup after creating a timestamped backup when existing data is present.
- Refuse to start on an unsupported future schema version.
- Provide backup, restore, import, export, and repair flows. Exports include SQLite DB, referenced files, schema version, app version, and manifest checksums.
- Large attachments/generated artifacts are files, not DB blobs by default; DB stores metadata, MIME type, size, origin, relative path, content hash, and corruption status.
- Define deletion behavior per file reference: retain, archive, trash, or garbage-collect.

### Required indexes
| Query family | Indexes |
| --- | --- |
| Board | `(workspace_id, column_id, sort_order)`, `(workspace_id, state, updated_at)`, `(workspace_id, owner_id, state)`. |
| Monitoring | `(topic_id, run_id)`, `(published_at)`, `(retrieved_at)`, `(source_family)`, `(url_hash)`. |
| Deduplication | `(canonical_event_key)`, `(content_hash)`, `(source_id, external_id)`. |
| Scoring/filtering | `(relevance_score)`, `(urgency_score)`, `(confidence_score)`, `(actionability_score)`. |
| Activity/replay | `(target_type, target_id, timestamp)`, `(correlation_id)`, `(trace_id)`. |
| Outputs | `(host_id, type, status)`, `(lineage_signal_id)`, `(artifact_hash)`. |
| Alerts | `(rule_id, last_fired_at)`, `(severity, unread_at)`. |

## 4. Domain model

### Core tables
| Table | Key fields |
| --- | --- |
| `workspaces` | `id`, `name`, `path`, `schemaVersion`, `appVersion`, `createdAt`, `updatedAt`. |
| `topics` | `id`, `workspaceId`, `name`, `family`, `intent`, `subtopicsJson`, `exclusionsJson`, `sourceFamiliesJson`, `regionsJson`, `peopleJson`, `organizationsJson`, `projectsJson`, `priority`, `cadence`, `lookbackWindow`, `lastRunAt`, `nextRunAt`, `muteUntil`. |
| `watch_rules` | `id`, `topicId`, `name`, `conditionJson`, `threshold`, `operator` (`>`, `>=`, `<`, `<=`, `==`, `between`), `severity`, `cooldownMinutes`, `digestCadence`, `enabled`, `lastFiredAt`, `feedbackWeight`. |
| `monitoring_runs` | `id`, `topicId`, `runDate`, `cadence`, `lookbackStart`, `lookbackEnd`, `mode` (`news`, `events`, `mixed`), `sourceCoverageJson`, `gapsJson`, `status`, `error`, `startedAt`, `finishedAt`. |
| `sources` | `id`, `family`, `name`, `url`, `authorOrOrg`, `credibility`, `accessNotes`, `lastCheckedAt`. |
| `signals` | `id`, `topicId`, `runId`, `sourceId`, `title`, `summary`, `url`, `localRef`, `authorOrOrg`, `retrievedAt`, `publishedAt`, `evidenceQuality`, `claimType`, `canonicalEventKey`, `contentHash`, `relevanceScore`, `noveltyScore`, `freshnessScore`, `confidenceScore`, `urgencyScore`, `impactScore`, `actionabilityScore`, `triageStatus`, `rejectionReason`, `mutedUntil`. |
| `signal_claims` | `id`, `signalId`, `claimText`, `claimType` (`confirmed_fact`, `reported_claim`, `announcement`, `opinion`, `forecast`, `rumor`, `speculative_lead`, `background`), `confidence`, `evidenceSnippet`, `sourceUrl`. |
| `signal_duplicates` | `id`, `primarySignalId`, `duplicateSignalId`, `reason`, `similarityScore`. |
| `work_cards` | `id`, `workspaceId`, `kind`, `title`, `subtitle`, `body`, `summary`, `columnId`, `state`, `sortOrder`, `priority`, `ownerId`, `nextStep`, `definitionOfDone`, `dueAt`, `checkInAt`, `blockedReason`, `staleAt`, `confidence`, `relevance`, `novelty`, `sourceFamily`, `actionability`, `statusEvidence`, `outputLinkageJson`, `metadataJson`. |
| `card_links` | `id`, `fromCardId`, `toCardId`, `linkType` (`source`, `related`, `parent`, `child`, `depends_on`, `blocks`, `merged_into`, `produced_output`, `revisit_after`). |
| `signal_card_links` | `id`, `signalId`, `cardId`, `role` (`origin`, `evidence`, `counter_evidence`, `duplicate`, `context`). |
| `decisions` | `id`, `cardId`, `decision`, `ownerId`, `rationale`, `alternativesJson`, `triggeringInputsJson`, `confidence`, `revisitCondition`, `decidedAt`. |
| `actions` | `id`, `cardId`, `description`, `ownerId`, `priority`, `timing`, `dependency`, `trigger`, `committed`, `needsConfirmation`, `definitionOfDone`, `status`, `validatedAt`. |
| `delegations` | `id`, `cardId`, `ownerName`, `request`, `expectedDeliverable`, `dueAt`, `checkInAt`, `status`, `statusEvidence`, `blockers`, `followUpCadence`, `handoffContext`. |
| `output_surfaces` | `id`, `hostId`, `hostType`, `type`, `title`, `contentRef`, `contentJson`, `schemaVersion`, `status` (`draft`, `streaming`, `complete`, `failed`, `stale`, `superseded`, `approved`), `source`, `lineageJson`, `createdAt`, `updatedAt`. |
| `artifacts` | `id`, `surfaceId`, `relativePath`, `mimeType`, `sizeBytes`, `contentHash`, `origin`, `garbageCollectState`. |
| `alerts` | `id`, `ruleId`, `cardId`, `signalId`, `title`, `message`, `whyItMatters`, `whatChanged`, `confidence`, `severity`, `nextAction`, `status`, `dedupeKey`, `firedAt`, `readAt`, `dismissedAt`. |
| `notifications` | `id`, `alertId`, `channel` (`in_app`, `digest`), `templateKey`, `payloadJson`, `status`, `createdAt`. |
| `activity_events` | `id`, `type`, `actorType`, `actorId`, `targetType`, `targetId`, `timestamp`, `summary`, `payloadJson`, `visibility`, `correlationId`, `traceId`. |
| `ai_runs` | `id`, `purpose`, `provider`, `model`, `inputScopeJson`, `outputSurfaceId`, `promptHash`, `tokenPrompt`, `tokenCompletion`, `estimatedCost`, `dataPolicy`, `status`, `error`. |
| `user_preferences` | `id`, `workspaceId`, `theme`, `dashboardLayoutJson`, `savedViewsJson`, `notificationSettingsJson`, `aiConsentJson`. |

### Card kinds and states
| Kind | Purpose |
| --- | --- |
| `signal` | A monitored item requiring triage. |
| `insight` | Interpretation or pattern extracted from one or more signals. |
| `idea` | A possible project, product, prompt, workflow, or improvement. |
| `question` | An open question blocking interpretation or action. |
| `risk` | A project, reliability, deadline, security, or opportunity risk. |
| `decision` | A recorded choice with rationale and revisit condition. |
| `action` | Committed executable work with owner and definition of done. |
| `delegation` | Work requested from another person/system with check-in cadence. |
| `output` | A produced artifact, report, prompt, issue, message, plan, prototype, or update. |
| `warning` | A high-confidence alert requiring attention. |
| `watch_item` | A muted/deferred item that should influence future monitoring. |

States: `raw`, `clarified`, `researched`, `decided`, `delegated`, `in_progress`, `waiting`, `blocked`, `review`, `shipped`, `watch_later`, `archived`, `rejected`.

## 5. Board lifecycle and transitions

### Columns
| Column | Accepts | Primary action | Exit criteria |
| --- | --- | --- | --- |
| Intake | New signals and compact captures | Inspect provenance and duplicates | Has triage status and score. |
| Triage | Scored signals/cards | Mark useful, irrelevant, duplicate, watch later, or convert | Has decision to investigate, discard, mute, or convert. |
| Investigate | Insights, questions, risks, ideas | Add claims, sources, context, open questions | Has enough evidence for decision or deliberate deferral. |
| Decide | Ideas, risks, decision inputs | Do, defer, delegate, research, merge, split, schedule, discard | Decision record exists with rationale and confidence. |
| Execute | Committed actions and output work | Complete next step | Action has definition-of-done evidence or moves to waiting/blocked/review. |
| Waiting | Delegations, dependencies, external responses | Check status and follow up | Response/evidence received, due window changed, or escalated. |
| Review | Outputs and completed actions | Approve, revise, archive, ship | Output is approved, superseded, rejected, or shipped. |
| Shipped | Approved outputs | Link result and lessons | Output lineage and activity summary complete. |
| Watch Later | Deferred signals/topics | Tune watch rule or revisit later | Revisited, muted, archived, or converted. |
| Archived | Closed/rejected/duplicate records | Restore or export | No active workflow obligation remains. |

### Transition rules
- Invalid moves show the reason at the point of interaction.
- Drag-and-drop has keyboard alternatives and visible focus/drop targets.
- Reordering persists `sortOrder` with optimistic rollback on conflict.
- Transitions run in transactions that update card state, related decision/action/delegation/output rows, and activity events together.
- Hooks may create alerts, reminders, review tasks, watch-rule proposals, or output surfaces.
- Suggested actions remain visually and structurally separate from committed actions.

### Required transition side effects
| Transition | Side effect |
| --- | --- |
| Intake → Triage | Create triage activity with score snapshot. |
| Triage → Investigate | Link selected claims and strongest sources. |
| Triage → Watch Later | Create/update watch rule feedback; preserve provenance. |
| Triage → Archived | Store rejection reason: irrelevant, duplicate, already handled, low confidence, muted, outside scope. |
| Investigate → Decide | Require open questions list or explicit none. |
| Decide → Execute | Create committed `actions` row with owner, timing, dependency, definition of done. |
| Decide → Waiting | Create `delegations` row. |
| Execute → Review | Require output surface or completion evidence. |
| Review → Shipped | Mark output approved and link contributing signals/decisions/actions. |
| Any active → Blocked | Store blocker, who/what can unblock, evidence that would change status. |

## 6. Monitoring triage

### Monitoring run fields
Each run records run date, cadence, lookback window, exact topic, mode, new-since-last-run items, still-important context, source coverage, and gaps.

### Source families
Official pages, feeds, newsletters, journals, repositories, social/community posts, forums, calendars, press releases, podcasts, videos, saved files, and compact imports.

### Triage classification
- Include only items relevant to exact topic, audience, geography, timing, and mode.
- Prefer material developments in the lookback window, official announcements, primary documents, credible dated reporting, and analysis that changes interpretation.
- Avoid generic explainers with no new development, SEO/thin commentary, duplicates, and untraceable claims.
- Events additionally require current/upcoming timing, official pages when possible, date/time/location/cost/booking/cancellation/access constraints.
- Preserve omissions and gaps when search/crawl access is partial.

### Scores
| Score | Meaning |
| --- | --- |
| Relevance | Fit to topic intent and user projects. |
| Novelty | New development vs repeated background. |
| Freshness | Recency inside lookback window. |
| Confidence | Evidence strength and source quality. |
| Urgency | Time sensitivity or deadline proximity. |
| Impact | Potential effect on project/opportunity/risk. |
| Actionability | Clear next step, decision, delegation, or output potential. |

### Feedback loop
The user can mark a signal as useful, irrelevant, duplicate, already handled, watch later, or converted into action. Feedback adjusts relevance/alert behavior but never hides provenance or deletes history by default.

## 7. UI surfaces

### Main screens
| Screen | Requirements |
| --- | --- |
| Workspace setup/settings | Choose workspace, show path, schema/app versions, health, export/import, backup/restore, AI/network permissions. |
| Monitoring dashboard | Topic cards, last/next run, source coverage, gaps, volume trends, high-confidence warnings, conversion rate, stale ideas, pending decisions, delegated work awaiting response, outputs produced. |
| Board | Kanban columns, counts, filters, search, sort, saved views, keyboard drag/move, bulk selection, responsive layout. |
| Card detail | Provenance, claims, score breakdown, related cards/signals, decisions, actions, delegations, outputs, activity stream, automation explanations. |
| Triage inbox | Dedup clusters, strongest source, claim type, confidence, relevance rationale, accept/reject/watch-later variants. |
| Output review | Typed surfaces with approve, revise, copy, download, export, compare, comment, pin/minimize/open actions. |
| Notification center | Alerts grouped by topic, severity, confidence, decision impact, cooldown status, and suggested follow-up. |
| Activity stream | Chronological events with filters for type, actor, severity, source, errors, card, and correlation/trace IDs. |

### Card UI contract
- Cards are scannable at rest and reveal detail through expansion or detail panel.
- Required card display fields: `kind`, `title`, `summary`, `badges`, `state`, `score chips`, `source family`, `confidence`, `next step`, `owner`, `due/check-in`, `blocked/stale marker`, `output linkage`.
- Actions: triage, convert, merge, split, decide, delegate, create action, create output, watch later, archive, mute, open detail.
- Cards provide empty/loading/error/stale states, pointer and keyboard access, visible focus, sufficient contrast, semantic labels, and screen-reader text for icon-only variants.
- Responsive behavior: cards remain legible in narrow columns, dense grids, and detail panes; avoid visual noise.

### Dashboard/widgets
- Responsive grid: 1 column mobile, 2 tablet, 3–4 desktop.
- Widgets have title bar, content area, optional action menu, loading skeleton, error state with retry.
- Drag-to-reorder and show/hide widgets persisted to preferences.
- Charts support dark/light theme, responsive resize, accessible palettes, hover tooltips, and PNG export.
- Required charts/tables adapted to work intelligence: monitoring volume over time, conversion by topic/source family, urgency by stage, output count by week, stale/delegated/blocked aging, sortable/filterable signal and decision tables.
- Date range picker variants dashboard widgets and tables with preset ranges and custom locale-aware range.

## 8. Automation, AI, alerts, and guardrails

### Automation rules
- Automation must show trigger, inputs, confidence, proposed/taken action, and undo/tuning variants.
- Supported suggestions: merge duplicates, link related items, escalate warnings, create follow-up reminders, convert insights into outputs, propose next action, propose watch-rule edit.
- Suggestions are not committed work until the user accepts or a saved rule explicitly allows the action.

### AI features
| Feature | Requirement |
| --- | --- |
| Provider abstraction | Provider-agnostic interface for OpenAI, Anthropic, and local models. |
| Config | Model, temperature, max tokens, and system prompt configurable per use case. |
| Safety | Sanitize inputs; strip unnecessary PII; show destination/purpose; include `data_policy: no_training` where supported. |
| Reliability | Retry 429/500/503 with exponential backoff 1s, 2s, 4s, max 3 retries. |
| Cost | Log prompt/completion tokens and estimated cost per `ai_runs` row. |
| Fallback | If AI unavailable, show AI unavailable badge and use rule-based fallback for scoring, templates, and sorting. |
| Use cases | Triage summary, claim extraction, duplicate hints, next-action suggestions, watch-rule proposals, digest/report drafting, output review checklist. |

### Alert engine
- Alert rules include condition, threshold, comparison operator, severity, action, cooldown, digest cadence, and enabled state.
- Evaluate after relevant signal/card/decision/delegation/output changes.
- Same alert rule must not fire more than once per evaluation period or cooldown window.
- In-app alerts explain why the item matters, what changed, confidence level, and what the user can do next.
- Digests group by topic, source family, urgency, decision impact, and suggested follow-up.
- Noise variants: thresholds, mute rules, feedback, cooldowns, digest cadence, and per-topic preferences.

## 9. REST API and realtime

### REST conventions
- Prefix all routes with `/api/v1`.
- Resources use plural nouns; nesting limited to one level.
- Collection responses use `{data, meta}`; single resources use `{data}`.
- Empty collections return `{data: [], meta: {total: 0, page, per_page, total_pages}}`.
- Errors follow RFC 7807 Problem Details with status codes 400, 401, 403, 404, 409, 422, 429, 500.
- POST create endpoints accept `Idempotency-Key`; repeat within 24 hours returns original response.
- GET, PUT, DELETE are idempotent.

### Required endpoints
| Method/path | Purpose |
| --- | --- |
| `GET /api/health` | Store status, workspace path, schema version, app version. |
| `GET/POST /api/v1/topics` | List/create monitored topics. |
| `GET/PUT/DELETE /api/v1/topics/{id}` | Manage topic intent, cadence, source families, exclusions. |
| `POST /api/v1/topics/{id}/runs` | Start monitoring run. |
| `GET /api/v1/monitoring-runs` | Filter by topic/status/date. |
| `GET /api/v1/signals` | Filter, sort, paginate signals. |
| `POST /api/v1/signals/{id}/triage` | Mark useful/irrelevant/duplicate/handled/watch-later/convert. |
| `GET/POST /api/v1/cards` | List/create cards. |
| `GET/PUT/DELETE /api/v1/cards/{id}` | Read/update/archive card. |
| `POST /api/v1/cards/{id}/move` | Board transition with validation and side effects. |
| `POST /api/v1/cards/{id}/decisions` | Create decision record. |
| `POST /api/v1/cards/{id}/actions` | Create committed/suggested action. |
| `POST /api/v1/cards/{id}/delegations` | Create delegation. |
| `GET/POST /api/v1/output-surfaces` | List/create typed output surfaces. |
| `POST /api/v1/output-surfaces/{id}/approve` | Approve output. |
| `GET /api/v1/activity-events` | Paginated activity stream. |
| `GET/POST /api/v1/watch-rules` | Manage alert/watch rules. |
| `GET/POST /api/v1/alerts` | Notification center and alert status updates. |
| `POST /api/v1/exports` | Create workspace export. |
| `POST /api/v1/imports` | Import workspace bundle. |

### WebSocket
- Endpoint: `ws(s)://host/ws`.
- First message or query param carries auth/session token for local runtime.
- Message format: `{type, payload, id}`.
- Server acknowledges every client message with `{type: "ack", id}`.
- Heartbeat: server sends `{type: "ping"}` every 30s; client responds `{type: "pong"}` within 10s.
- Reconnect backoff: 1s, 2s, 4s, 8s, max 30s.
- Resume message: `{type: "resume", payload: {last_event_id}}`; server replays missed persisted events up to 1000 events or 5 minutes.
- Message types: `card_created`, `card_updated`, `card_moved`, `signal_triaged`, `decision_created`, `delegation_updated`, `output_surface_updated`, `alert_fired`, `watch_rule_updated`, `activity_appended`, `presence`, `error`.
- Persist events before broadcasting when the stream is an audit source.

## 10. Failure states and recovery

| Failure | Required behavior |
| --- | --- |
| Missing workspace | Deterministically initialize after user confirms/chooses path. |
| Unreadable/unwritable workspace | Show recoverable settings/diagnostics error with path and permission guidance. |
| Locked DB | Show retry/close-other-process guidance; do not corrupt or overwrite. |
| Corrupted DB | Offer backup restore/repair; preserve original damaged DB when possible. |
| Future schema version | Refuse startup and explain app upgrade requirement. |
| Failed migration | Keep backup, show failure, do not partially start. |
| Disk full | Roll back transaction, show space guidance, preserve prior state. |
| Network/source failure | Record monitoring gap; keep existing data usable. |
| AI failure/rate limit | Show AI unavailable badge; use rule-based fallback. |
| Duplicate/invalid move | Prevent or roll back; explain reason in card/board UI. |
| Stale output | Mark surface stale and show inputs changed since generation. |
| Alert noise | Allow mute, threshold edit, cooldown, feedback, and digest-only mode. |
| Console/runtime browser error | Treat as validation defect before acceptance. |

## 11. Testing and validation

### Automated tests
- Unit: Vitest with happy-dom for application logic and components.
- Storage/API: Vitest using temporary SQLite files and isolated data directories.
- E2E: Playwright for critical local user flows.
- Coverage: minimum 80% line coverage for application logic.
- Required cases:
  - first-run initialization and restart persistence;
  - workspace export/import with attachments and manifest checksums;
  - backup/restore and migration backup;
  - rollback for failed multi-entity writes;
  - unsupported future schema refusal;
  - locked/corrupt/disk-full handling where practical;
  - monitoring run creates signals with provenance and gaps;
  - deduplication preserves primary and duplicate history;
  - signal converted into card/action/delegation/output;
  - invalid board transition explanation and rollback;
  - alert cooldown/deduplication;
  - AI unavailable fallback;
  - WebSocket reconnect/resume and event replay.

### Playwright MCP browser validation
The implementing agent must use a build-run-observe-improve loop:
1. Inspect spec, repository structure, package scripts, tests, and framework conventions.
2. Implement the smallest coherent browser-testable slice.
3. Start the app with the existing dev/preview command or add the minimal appropriate command.
4. Open the running URL with Playwright MCP and interact as a real user: create workspace, add topic, run/import monitoring sample, triage signal, drag/move card with keyboard alternative, create decision/action/delegation, generate/attach output, approve/ship, inspect alert/watch-rule update, export workspace.
5. Observe rendered page, accessibility tree, console output, network behavior, screenshots/traces, and persisted state.
6. Fix defects and repeat until the main loop works with no high-value improvement remaining.
7. Final report states command, URL, flows exercised, screenshots/traces if visual, console/network/runtime errors found and resolved, verified behavior, and remaining limitations. Do not claim browser validation if Playwright MCP or equivalent was unavailable; install/configure it when possible, commonly via `npx @playwright/mcp@latest`.

## 12. Acceptance proof: complete signal-to-output session

The build is complete only when a user can perform and verify this session locally:

1. Create/select a workspace and see the active path plus healthy SQLite status.
2. Add at least one monitored topic from the provided topic families with intent, source families, exclusions, cadence, and lookback window.
3. Run or import a monitoring cycle that records run date, lookback, source coverage, gaps, and at least three candidate signals.
4. Inspect a signal with source, title, author/org when known, URL/local reference, retrieved/published time, claim classification, evidence quality, and score breakdown.
5. Deduplicate two repeated signals while preserving duplicate history.
6. Convert one useful signal into a work card and reject/watch-later another with feedback that changes future filtering or alerts.
7. Move the card through Triage → Investigate → Decide with visible transition validation.
8. Record a decision with rationale, alternatives, owner, confidence, triggering inputs, and revisit condition.
9. Create either:
   - a committed action with owner, priority, timing, dependency, and definition of done; or
   - a delegation with owner, request, expected deliverable, due/check-in window, status evidence, blockers, follow-up cadence, and handoff context.
10. Produce a typed output surface linked to the contributing signal/card/decision/action/delegation.
11. Review and approve or revise the output, then move the card to Shipped or Archived with activity history intact.
12. Fire or update an in-app alert/watch rule that explains why the item matters, what changed, confidence, next action, cooldown/digest behavior, and tuning variants.
13. Confirm dashboard metrics update: signal volume, conversion rate, stale ideas, delegated work awaiting response, high-confidence warnings, pending decisions, and outputs produced.
14. Refresh/restart the app and confirm persisted board state, activity stream, output surface, alerts, and workspace settings.
15. Export the workspace and verify manifest checksums include DB, artifacts, schema version, app version, and referenced files.
