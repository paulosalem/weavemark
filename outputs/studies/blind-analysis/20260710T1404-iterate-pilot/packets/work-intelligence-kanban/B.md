# Blind evaluation packet

Study: Intelligence-to-Execution Kanban
Variant: B
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# @{app_name}: Framework-X Work-Intelligence variant

@iterate 1
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

# Work Intelligence Kanban: Framework-X Work-Intelligence variant

# Work Intelligence Kanban — First-Build Implementation Blueprint

Design **Work Intelligence Kanban** as a focused local-first Next.js/TypeScript/Prisma/SQLite product that converts monitored work-intelligence signals into reviewed kanban cards, decisions, actions, delegations, output artifacts, alerts, and updated watch rules. Every requirement below must support the lifecycle: **signal → card → triage → decision/action/delegation/output → watch rule/alert → resolved or archived**.

## 1. First-build scope

| Area | First-build requirement | Lifecycle support |
|---|---|---|
| Product intent | Calm command center for recurring work-intelligence monitoring and project follow-through. | Keeps each `Signal` inspectable until it becomes a `WorkCard`, `Decision`, `ActionPlan`, `Delegation`, `OutputArtifact`, `WatchRule`, or `Alert`. |
| User/workspace | One local user or one local team workspace. Local machine is source of truth. | All lifecycle records belong to one durable local `Workspace`. |
| External calls | External AI, web, email, push, or integration calls are disabled unless explicitly configured and disclosed with provider, destination, purpose, and approximate payload scope. | Protects signal/card/output content during enrichment, output generation, alert delivery, and provider-backed monitoring. |
| Topic families | Framework-X/prompt languages; local-first AI tools; agentic programming validation; calm productivity UI; research automation/signal-to-action workflows; personal opportunities, risks, deadlines, and follow-ups. | Seed `TopicFamily` and `Topic` records used by capture, scoring, watch rules, dashboard filters, and alerts. |
| Tech stack | Next.js 14+ App Router, TypeScript 5 strict with no `any`, React Server Components by default, client components only for board/forms/charts/live UI, Tailwind tokens, Zustand for local UI state only, react-hook-form plus shared zod, Server Actions for appropriate mutations, Node.js runtime only, Prisma SQLite, Prisma Migrate, Vitest, happy-dom, Playwright, Playwright MCP. | Implements, validates, and browser-tests the complete loop. |
| In scope | Local workspace setup; durable SQLite; topic configuration; compact signal capture; API-backed ingestion stubs; monitoring runs; provenance; dedupe; scoring; classification; lifecycle board; cards/details; typed outputs; activity; dashboard; alerts; provider-agnostic AI; REST; WebSocket; validation. | End-to-end signal-to-output session. |
| Out of scope | Subscriptions, billing, hosted multi-tenant onboarding, tenant isolation, serverless filesystem defaults, browser-only canonical storage, invisible external calls, required external calls for existing data. Optional Electron/Tauri later only. | Prevents generic SaaS/platform drift. |

The first build must let the user answer: what came in; why it mattered; what changed since the last run; what was decided; who owns what; what is blocked; what changed because of the signal; which outputs were produced; and which alert/watch rule keeps the loop alive.

## 2. Local workspace, storage, and operations

| Component | Requirement | Lifecycle entity/transition |
|---|---|---|
| Workspace directory | User can choose/create workspace. Show active path in settings/diagnostics. | `Workspace` owns all lifecycle records. |
| Data directory | Store SQLite file, attachments, generated artifacts, backups, exports, repair logs, diagnostics under workspace or OS user-data directory. Development default SHOULD be `.local-data/app.sqlite`. | Preserves evidence, outputs, and audit trail. |
| SQLite | SQLite 3 WAL mode is canonical. `DATABASE_URL` points to a local SQLite file. One local Node.js app server owns writes. | Prevents conflicting lifecycle writes. |
| Startup | Validate workspace read/write, local store health, schema version, app version, migration state, and environment through `env.mjs`. Initialize missing stores deterministically. Refuse unsupported future schemas. | Guarantees signal/card history is safe before board loads. |
| Migration safety | Before pending migrations on existing data, create timestamped backup. Show recoverable guidance for locked, corrupted, too-new, failed migration, interrupted write, or disk-full stores. | Protects historical signals, decisions, outputs, and alerts. |
| Persistence rules | Stable primary keys; `createdAt`; `updatedAt`; `deletedAt DateTime?` for recoverable entities; explicit transactions for multi-entity updates; optimistic concurrency via `version` or `updatedAt` for agent/conflict-prone records. | Ensures card move plus activity event, output generation plus lineage, and alert fire plus notification are atomic. |
| Indexes | Board order, search filters, event replay, dependency lookup, topic/run lookup, unread notification counts, source dedupe. | Keeps board/dashboard responsive with thousands of cards/signals. |
| Attachments | Large attachments and artifacts are files, not blobs by default. Store metadata, hash, MIME type, size, origin, relative path. | Preserves source evidence and output artifacts. |
| Export/import | Export SQLite, referenced files, schema version, app version, manifest checksums. Repair preserves damaged originals and reports changes. | Moves the complete signal-to-output history between machines. |
| Caches | Browser `localStorage`, IndexedDB, memory, and caches are disposable unless explicitly documented. Existing local data loads when AI/web/integrations fail. | Local-first continuity. |

## 3. Lifecycle state machine

Required lifecycle states: `new_signal`, `card_created`, `triaged`, `decided`, `actioned`, `delegated`, `output_generated`, `watch_rule_created`, `alert_triggered`, `resolved`, `archived`.

| State | Allowed transitions | Actor/driver | Triggering event | Required fields | Validation checks |
|---|---|---|---|---|---|
| `new_signal` | `card_created`, `archived` | user, automation, AI-suggested, provider job | compact capture, monitoring run, configured ingestion | `Signal.title`, `topicFamily`, `sourceFamily`, `sourceId` or `localReference`, `retrievedAt`, `summary` | provenance exists; external fetch disclosed; duplicate check queued; topic active or compact override |
| `card_created` | `triaged`, `archived`, `watch_rule_created` | user, AI-suggested | normalize signal into `WorkCard` | `WorkCard.title`, `signalId`, `status`, `stageKey`, scores, `suggestedNextStep` | card links to signal; stage is `intake`; source/evidence visible |
| `triaged` | `decided`, `watch_rule_created`, `archived` | user confirms; AI suggests | review provenance, classification, scores, dedupe | `claimType`, `confidence`, `urgency`, `triageStatus`, `triageRationale` | useful/irrelevant/duplicate/muted/watch-later reason captured; rejected history preserved |
| `decided` | `actioned`, `delegated`, `output_generated`, `watch_rule_created`, `archived` | user, AI-assisted | decision drawer submitted | `Decision.type`, `decision`, `rationale`, `owner`, `confidence`, `triggeringInputIds` | alternatives/rationale present; output/action/delegation route valid |
| `actioned` | `output_generated`, `watch_rule_created`, `resolved`, `archived` | user | action plan committed | `ActionPlan.nextStep`, `owner`, `dueDate`, `definitionOfDone`, `validationSignal` | committed action visually distinct from suggestion; confirmation required if external side effect |
| `delegated` | `output_generated`, `watch_rule_created`, `resolved`, `archived` | user, agent, collaborator, future self | delegation sent or scheduled | `Delegation.owner`, `request`, `expectedDeliverable`, `dueOrCheckInWindow`, `reviewCriteria` | handoff context and blocker/status evidence captured |
| `output_generated` | `watch_rule_created`, `resolved`, `archived` | user, AI-assisted, automation | output composer creates artifact | `OutputArtifact.type`, `title`, `content` or `filePath`, `lineage`, `status` | artifact traces to signal/card/decision/action/delegation; failed/stale outputs explain recovery |
| `watch_rule_created` | `alert_triggered`, `resolved`, `archived` | user, AI-suggested, automation | rule accepted from card/output/action/delegation | `WatchRule.name`, `frequency`, `criteria`, `dedupeKey`, `cooldownWindow` | quiet hours/calm constraints valid; rule explains why it exists |
| `alert_triggered` | `new_signal`, `card_created`, `resolved`, `archived` | system/realtime | scheduler or rule evaluation | `Alert.severity`, `ruleId`, `matchedRecordIds`, `dedupeKey`, `message` | no duplicate in cooldown; alert category set; conversion target chosen |
| `resolved` | `archived`, `watch_rule_created` | user, system with confirmation | validation passes or user marks done | `resolutionSummary`, `resolvedAt`, `outcomeEvidence` | all required linked actions/delegations/output checks satisfied |
| `archived` | restore to prior active state | user | archive, reject, supersede, mute expiry review | `archiveReason`, `archivedAt` | history retained; restoration target known |

Driver types: **user-driven** decisions are final by default; **AI-suggested** changes require inspection/override; **automation-driven** changes are limited to configured watch/alert/scheduler operations; **realtime/system-driven** changes broadcast persisted activity after database commit.

## 4. Core entities and schema tables

Use zod schemas shared by UI, Server Actions, API routes, and services. Preserve exact literals in code and tests. Required first-build names map to durable model names as follows: `WorkCard` maps to/extends `BoardCard`; `OutputArtifact` maps to/extends `OutputSurface`; `WatchRule` maps to/extends `NotificationRule`; `Alert` maps to/extends `Notification`; `ActionPlan` uses `ActionItem` plus checklist/validation fields.

### 4.1 Required enums

| Enum | Values |
|---|---|
| `topicFamily` | `Framework-X`, `local_first_ai`, `agentic_programming`, `calm_productivity_ui`, `research_automation`, `personal_project_followup` |
| `sourceFamily` | `official_page`, `feed`, `newsletter`, `journal`, `repository`, `social_post`, `community_forum`, `calendar`, `press_release`, `podcast`, `video`, `saved_file`, `compact`, `integration` |
| `MonitoringRun.mode` | `news`, `events`, `research`, `releases`, `discussions`, `mixed` |
| `MonitoringRun.status` | `queued`, `running`, `complete`, `failed`, `canceled` |
| `Signal.claimType` | `confirmed_fact`, `reported_claim`, `announcement`, `opinion`, `forecast`, `rumor`, `repeated_background`, `speculative_lead` |
| `Signal.triageStatus` | `new`, `triaged`, `useful`, `irrelevant`, `duplicate`, `muted`, `watch_later`, `converted_to_action`, `archived` |
| `WorkCard.status` | `new_signal`, `card_created`, `triaged`, `decided`, `actioned`, `delegated`, `output_generated`, `watch_rule_created`, `alert_triggered`, `resolved`, `archived` |
| `WorkCard.kind` | `signal`, `insight`, `idea`, `action`, `decision`, `delegation`, `risk`, `warning`, `watch_item`, `output` |
| `Decision.type` | `do_now`, `defer`, `delegate`, `research`, `generate_output`, `create_watch_rule`, `merge`, `split`, `discard`, `archive` |
| `urgency` | `low`, `medium`, `high`, `critical` |
| `confidence` | `low`, `medium`, `high`, `verified` |
| `ActionPlan.kind` | `committed`, `suggested` |
| `ActionPlan.status` | `suggested`, `committed`, `in_progress`, `waiting`, `blocked`, `done`, `canceled`, `archived` |
| `Delegation.status` | `draft`, `sent`, `waiting`, `blocked`, `received`, `reviewed`, `closed`, `canceled` |
| `OutputArtifact.type` | `text`, `program`, `table`, `diff`, `image`, `chart`, `status`, `log`, `terminal`, `form`, `canvas`, `file`, `custom` |
| `OutputArtifact.status` | `draft`, `streaming`, `complete`, `failed`, `stale`, `superseded`, `approved` |
| `WatchRule.frequency` | `compact`, `hourly`, `daily`, `weekly`, `monthly`, `custom` |
| `WatchRule.comparisonOperator` | `>`, `>=`, `<`, `<=`, `==`, `between` |
| `Alert.category` | `reminder`, `opportunity`, `risk`, `deadline`, `validation`, `recurring_topic_monitoring` |
| `Alert.severity` | `info`, `warning`, `critical` |
| `Notification.channel` | `in_app`, `email`, `push` |
| `Notification.status` | `unread`, `read`, `dismissed`, `sent`, `failed` |
| `ActivityEvent.actor` | `human`, `agent`, `integration`, `system`, `automation` |
| `ActivityEvent.visibility` | `public`, `team_only`, `private`, `internal`, `redacted` |
| `AiRun.purpose` | `summarize`, `triage`, `suggest_action`, `natural_language_query`, `digest`, `insight_generation` |
| `AiRun.status` | `queued`, `running`, `complete`, `failed`, `canceled` |
| `AiRun.dataPolicy` | `no_training`, `local_only`, `provider_default` |
| `ValidationRun.result` | `passed`, `failed`, `warning`, `blocked`, `not_run` |

### 4.2 Schema tables

| Entity | Field | Type | Req | Example | Supports transition |
|---|---|---:|:---:|---|---|
| `Signal` | `id` | string | yes | `sig_001` | all signal lineage |
| `Signal` | `workspaceId` | string | yes | `ws_local` | local ownership |
| `Signal` | `topicId` | string | yes | `topic_promplet` | `new_signal` |
| `Signal` | `topicFamily` | enum | yes | `Framework-X` | scoring/filtering |
| `Signal` | `sourceFamily` | enum | yes | `repository` | provenance |
| `Signal` | `sourceId` | string nullable | no | `src_github` | provenance |
| `Signal` | `title` | string | yes | `Framework-X adds structured compression guidance` | capture |
| `Signal` | `summary` | string | yes | `A new technique improves prompt compiler output.` | card creation |
| `Signal` | `url` | string nullable | no | `https://example.dev/Framework-X` | evidence |
| `Signal` | `localReference` | string nullable | no | `notes/2025-02-01.md` | compact evidence |
| `Signal` | `retrievedAt`, `publishedAt` | datetime | yes/no | `2025-02-01T10:00:00Z` | freshness |
| `Signal` | `evidenceQuality` | enum/string | yes | `primary_source` | triage |
| `Signal` | `claimType` | enum | yes | `announcement` | triage |
| `Signal` | score fields | number 0–100 | yes | `relevanceScore: 91` | ranking |
| `Signal` | `dedupeKey`, `dedupeGroupId` | string nullable | no | `Framework-X-compiler-compress` | dedupe |
| `Signal` | `triageStatus` | enum | yes | `new` | lifecycle |
| `Signal` | `rawPayloadJson` | JSON | no | `{...}` | audit with privacy limits |
| `WorkCard` | `id`, `workspaceId`, `signalId` | string | yes | `card_001` | `card_created` |
| `WorkCard` | `kind` | enum | yes | `signal` | board rendering |
| `WorkCard` | `status` | enum | yes | `card_created` | board state |
| `WorkCard` | `stageKey` | enum/string | yes | `intake` | column |
| `WorkCard` | `title`, `summary`, `body` | string | yes | `Evaluate Framework-X technique` | scanning/detail |
| `WorkCard` | `topicFamily`, `sourceFamily` | enum | yes | `Framework-X`, `repository` | filtering |
| `WorkCard` | `confidence`, `urgency`, `relevance`, `novelty`, `actionability` | enum/number | yes | `high`, `medium`, `92` | triage |
| `WorkCard` | `owner`, `nextStep`, `statusEvidence` | string nullable | no | `Draft adoption checklist` | decision/action |
| `WorkCard` | `outputLinkageJson`, `linksJson`, `badgesJson`, `uiStateJson` | JSON | no | `{"outputs":["out_001"]}` | output/board UI |
| `Decision` | `id`, `workspaceId`, `cardId` | string | yes | `dec_001` | `decided` |
| `Decision` | `type` | enum | yes | `generate_output` | route choice |
| `Decision` | `decision`, `rationale` | string | yes | `Create internal adoption memo` | audit |
| `Decision` | `alternativesJson` | JSON | yes | `["archive","watch"]` | quality |
| `Decision` | `owner`, `confidence`, `deadline`, `revisitCondition` | string/enum/date | yes/no | `Alex`, `high` | follow-up |
| `ActionPlan` | `id`, `workspaceId`, `cardId`, `decisionId` | string | yes | `act_001` | `actioned` |
| `ActionPlan` | `kind`, `status` | enum | yes | `committed`, `in_progress` | action tracking |
| `ActionPlan` | `nextStep`, `owner`, `dueDate`, `checklistJson` | string/date/JSON | yes | `Test technique on one prompt` | execution |
| `ActionPlan` | `definitionOfDone`, `validationSignal`, `needsConfirmation` | string/bool | yes | `Output accepted by user`, `true` | validation |
| `Delegation` | `id`, `workspaceId`, `cardId`, `linkedIdeaId` | string | yes/no | `del_001` | `delegated` |
| `Delegation` | `owner`, `request`, `expectedDeliverable` | string | yes | `Agent: draft checklist` | handoff |
| `Delegation` | `dueOrCheckInWindow`, `status`, `statusEvidence`, `blockers`, `followUpCadence`, `handoffContext`, `reviewCriteria` | string/enum | yes/no | `tomorrow`, `waiting` | waiting/review |
| `OutputArtifact` | `id`, `workspaceId`, `hostId`, `cardId` | string | yes | `out_001` | `output_generated` |
| `OutputArtifact` | `type`, `title`, `content`, `filePath`, `schemaVersion`, `status`, `source` | enum/string | yes/no | `text`, `Framework-X adoption memo` | output |
| `OutputArtifact` | `lineageJson`, `actionsJson`, `versionHistoryJson` | JSON | yes/no | `{"signals":["sig_001"]}` | audit |
| `WatchRule` | `id`, `workspaceId`, `cardId` | string | yes | `rule_001` | `watch_rule_created` |
| `WatchRule` | `name`, `frequency`, `criteriaJson`, `threshold`, `comparisonOperator`, `cooldownWindow`, `quietHoursJson`, `escalationJson`, `isActive` | string/enum/JSON/bool | yes | `Watch related Framework-X releases` | alert loop |
| `Alert` | `id`, `workspaceId`, `ruleId`, `cardId` | string | yes | `alert_001` | `alert_triggered` |
| `Alert` | `category`, `severity`, `title`, `body`, `matchedRecordIdsJson`, `dedupeKey`, `status` | enum/string/JSON | yes | `opportunity`, `warning` | alert routing |
| `ActivityEvent` | `id`, `workspaceId`, `type`, `actor`, `targetType`, `targetId`, `timestamp`, `summary`, `payloadJson`, `visibility`, `correlationId`, `traceId` | mixed | yes | `card.state_changed` | audit/live replay |
| `TopicFamily` | `id`, `key`, `displayName`, `whyItMatters`, `defaultSourcesJson`, `defaultCadence`, `seeded` | mixed | yes | `Framework-X` | monitoring setup |
| `ValidationRun` | `id`, `workspaceId`, `cardId`, `targetType`, `targetId`, `result`, `checksJson`, `errorsJson`, `startedAt`, `completedAt` | mixed | yes | `passed` | release/readiness |

Also implement larger durable records where needed: `Workspace`, `Topic`, `MonitoringRun`, `Source`, `Insight`, `Idea`, `BoardStage`, `Attachment`, `Notification`, and `AiRun` with the field names from this specification. Each workspace-owned entity includes `workspaceId` unless explicitly global.

## 5. First-build architecture

| Component | Lifecycle responsibility | Inputs | Outputs | Persisted entities | Failure modes/recovery |
|---|---|---|---|---|---|
| Browser/compact capture | Creates `new_signal`. | title, summary, URL/local reference, topic family, source family, evidence notes | `Signal` and draft `WorkCard` | `Signal`, `Source`, `Attachment`, `ActivityEvent` | validation errors; duplicate suggestion; source unavailable |
| Monitoring runner | Creates signals from configured topics. | active `Topic`, cadence, lookback, provider config | `MonitoringRun`, new/still-important signals, gaps | `MonitoringRun`, `Signal`, `Source`, `ActivityEvent` | provider disabled/failure; partial gaps preserved |
| Local storage service | Commits lifecycle changes atomically. | domain commands | durable records | all entities | rollback on failed multi-entity write; backup/repair guidance |
| AI enrichment service | Suggests summary, classification, scores, next step, watch rule, output. | sanitized signal/card fields and purpose prompt | structured suggestion with confidence | `AiRun`, activity, optional candidate fields | AI unavailable badge; rule fallback; no hidden external call |
| Kanban board service | Moves `WorkCard` across lifecycle stages. | card, target stage, transition command | updated card, activity, realtime event | `WorkCard`, `ActivityEvent` | invalid transition reason; optimistic rollback |
| Decision drawer service | Converts triage into route choice. | card evidence, alternatives, owner, deadline | `Decision` | `Decision`, `ActivityEvent` | missing rationale/owner/confidence |
| Action/delegation service | Creates executable work. | decision, next step or handoff | `ActionPlan` or `Delegation` | `ActionPlan`, `Delegation`, `ActivityEvent` | missing definition of done/review criteria |
| Output composer | Produces typed artifact. | signal/card/decision/action/delegation lineage | `OutputArtifact` | `OutputArtifact`, `Attachment`, `ActivityEvent` | streaming failure; stale output; explicit apply required |
| Watch-rule scheduler | Keeps loop alive. | accepted `WatchRule`, cadence, criteria | `Alert` or new `Signal` | `WatchRule`, `Alert`, `Notification`, `ActivityEvent` | cooldown suppression; quiet hours delay; dedupe |
| Alert surface | Shows follow-up/opportunity/risk/deadline/validation alerts. | fired alert | notification center/toast/action | `Alert`, `Notification` | delivery failure logged; in-app remains |
| Activity log | Explains every visible state change. | transaction events | audit stream and replay | `ActivityEvent` | redaction metadata preserved |
| Validation runner | Proves readiness before state moves/releases. | card/output/rule/test scenario | `ValidationRun` | `ValidationRun`, `ActivityEvent` | blocked state with diagnostics |

## 6. Board lifecycle and monitoring triage

Default `BoardStage.key` values: `intake`, `triage`, `investigate`, `decide`, `execute`, `waiting`, `review`, `shipped`, `watch_later`, `archived`.

| Stage | Shows | Primary transition | Validation |
|---|---|---|---|
| `intake` | `new_signal` and `card_created` cards | start triage | provenance visible; duplicate status known |
| `triage` | scored/classified signals | mark useful/irrelevant/duplicate/muted/watch later | reason required for discard/mute; scores editable |
| `investigate` | useful but uncertain cards | create insight or request research | open question or evidence gap named |
| `decide` | cards needing route | create `Decision` | type, rationale, owner, confidence |
| `execute` | committed action/output work | create action/output/delegation | definition of done or expected deliverable |
| `waiting` | blocked/delegated/follow-up cards | check in, unblock, alert | status evidence/check-in window |
| `review` | outputs/actions needing acceptance | approve, revise, ship | validation run passes or override rationale |
| `shipped` | accepted outputs/done actions | create watch rule or resolve | output lineage and outcome evidence |
| `watch_later` | deferred monitored items | activate rule or archive | revisit condition |
| `archived` | resolved/rejected/superseded | restore | archive reason retained |

Cards must support create, view, edit, duplicate, archive/delete, search, filter, sort, saved views, bulk selection, counts, WIP, overdue, blocked, unread, high-confidence warning, stale-work, and attention indicators. Movement only occurs through allowed transitions; blocked movement shows the reason at the point of interaction. Reordering persists and rolls back on optimistic failure. Drag-and-drop has keyboard alternatives, focus styles, selection affordance, drag preview, drop targets, cancellation, persistence, and undo.

Monitoring runs must record run date, cadence, lookback window, topic, mode, new developments, still-important context, source coverage, and gaps. News mode prioritizes material changes, official announcements, primary documents, credible reporting with dates/entities, decision-relevant analysis, and contradictory evidence. Events mode prioritizes upcoming/current events with official page, venue/organizer, date, time, location, cost, booking, cancellation, and safety details. Avoid SEO posts, duplicate syndication, thin commentary, untraceable claims, stale events without recurrence, vague activities, and unsuitable options.

## 7. UI and interaction flow

A user must move one signal through the loop in fewer than ten deliberate steps:

1. Open Signal Inbox and add/import a signal.
2. Review normalized card in `intake`.
3. Confirm/edit AI summary, classification, scores, and duplicate suggestion.
4. Choose decision route in drawer.
5. Commit action or delegation, or generate output.
6. Review and approve typed output.
7. Accept proposed watch rule.
8. Simulate or wait for alert.
9. Resolve or archive card with outcome evidence.

| Surface | Visible fields | Primary actions | States | Acceptance criteria |
|---|---|---|---|---|
| Signal inbox | title, topic family, source, URL/local ref, retrieved/published time, evidence quality, duplicate badge | add signal, import, create card, archive | empty, loading, validation error, provider unavailable | creates `Signal`, `WorkCard`, activity |
| Work-intelligence kanban board | lifecycle columns, card title/summary/scores/owner/next step/status badges | move, keyboard move, filter, bulk archive, open drawer | empty board, empty column, loading, move error, stale | valid transitions persist; invalid moves rollback |
| Card detail drawer | provenance, source, summary, claim type, scores, linked entities, activity | edit fields, mark useful/duplicate/muted/watch later, decide | loading, not found, stale, permission-limited | all required triage fields visible/editable |
| Decision/action/delegation panel | alternatives, decision type, rationale, owner, deadline, next step, handoff, validation | decide, create action, create delegation, defer/archive | missing-field error, blocked, AI unavailable | produces `Decision`, `ActionPlan` or `Delegation` |
| Output composer/artifact preview | artifact type, title, content, lineage, status, actions, version history | draft, regenerate, approve, export, archive | streaming, failed, stale, complete | creates typed `OutputArtifact` with lineage |
| Watch-rule builder | criteria, frequency, threshold, comparison, dedupe, cooldown, quiet hours, escalation | accept proposal, edit, test, activate | invalid criteria, duplicate suppressed, disabled provider | creates active `WatchRule` |
| Alerts/follow-up view | category, severity, matched records, due/check-in, dedupe status | convert to signal/card, dismiss, snooze, resolve | empty, quiet-hours delayed, delivery failed | `Alert` can feed loop again |
| Activity timeline | actor, type, target, summary, timestamp, trace/correlation | filter, copy link, expand, export | paginated, live append, replay after reconnect | every user-visible change has event |
| Validation/debug panel | validation runs, browser checks, console/network findings, schema checks | run validation, inspect failure, retry | not run, running, failed, passed | release gates and loop proof visible |
| Dashboard | topic health, signal volume, conversion, stale work, warnings, decisions, outputs, gaps, AI cost | filter date, export chart, open records | skeleton, error with retry, no data | metrics link to lifecycle records |

Application shell includes workspace selector/status, Dashboard, Board, Topics, Signals, Ideas, Decisions, Delegations, Outputs, Activity, Settings, global search, date/filter variants, notification center, AI/provider status, local workspace/offline status. Every major screen has empty, loading, error with recovery, offline/provider-unavailable, permission-limited/unavailable, and stale-data states. Accessibility includes keyboard access for board movement, primary actions, dialogs, filters, card variants; semantic labels; visible focus; sufficient contrast; screen-reader text; responsive narrow/dense/detail layouts.

## 8. AI behavior and guardrails

AI suggests; the user can inspect evidence, edit fields, reject suggestions, and see why an alert/watch rule exists. External AI calls must be explicit and sanitized. Store credentials outside logs. Rate-limit defaults to prevent runaway usage. Use backoff 1s, 2s, 4s and max 3 retries on 429, 500, 503. Track token usage, estimated cost, provider/model, purpose, input/output summaries, and `dataPolicy`. Existing local data remains visible offline.

| AI task | Input fields | Prompt purpose | Output schema | Confidence/override | Safety/failure |
|---|---|---|---|---|---|
| signal summarization | title, source excerpt, URL/local ref, topic intent | concise card summary and why it matters | `{summary, whyItMatters, evidenceNotes}` | confidence shown; user edits | no full sensitive payload unless diagnostics enabled |
| topic classification | signal text, topic families | choose `topicFamily` and source family | `{topicFamily, sourceFamily, rationale}` | low confidence requires user confirm | rule fallback |
| entity extraction | signal/source text | extract people/orgs/projects/deadlines | `{entities, dates, deadlines, risks}` | editable chips | strip PII not needed |
| confidence scoring | provenance, evidence quality, claim type | score confidence/relevance/novelty/freshness/urgency/impact/actionability | numeric scores plus explanation | user can override scores | failed AI leaves compact scoring |
| urgency estimation | timing, deadline, topic intent | determine urgency | `{urgency, dueWindow, rationale}` | critical requires confirmation | no auto-escalation unless rule active |
| next-action suggestion | card, decision alternatives | propose smallest useful next step | `{nextStep, ownerSuggestion, definitionOfDone}` | remains `suggested` until committed | external effects require confirmation |
| delegation drafting | card and expected outcome | draft handoff | `{request, expectedDeliverable, reviewCriteria}` | user edits before sent | no hidden send |
| output drafting | card lineage and chosen type | draft artifact | `{type, title, content, lineage}` | approve before complete/apply | failed output marked recoverable |
| watch-rule proposal | card/output/action | propose recurring rule | `{criteria, frequency, threshold, cooldown, quietHours}` | user accepts/edits | dedupe/calm constraints enforced |
| duplicate detection | dedupe keys, source/title/body | suggest duplicate group | `{duplicateOf, confidence, reason}` | user confirms merge | history preserved |
| validation critique | card/output/rule | check readiness to move/ship | `{result, blockers, warnings, fixes}` | override requires rationale | blocks state if required checks fail |

## 9. API and realtime contract

REST uses plural nouns, one nesting level at most, `/api/v1/...`, query filtering/sorting/pagination, JSON content type, collection envelope `{"data": ..., "meta": {...}}`, single-resource envelope `{"data": ...}`, pagination `{"total": N, "page": P, "per_page": S, "total_pages": T}`, empty collection `{"data": [], "meta": {"total": 0, ...}}`, RFC 7807 errors for 400/401/403/404/409/422/429/500, create-route `Idempotency-Key` returning original response within 24 hours, idempotent GET/PUT/DELETE.

| Method/path | Request fields | Response fields | Affected entity | Realtime event | Validation errors |
|---|---|---|---|---|---|
| `GET /api/health` | none | store status, schema version, app version, workspace path health, migration state | `Workspace` diagnostics | none | store locked/corrupt/too new |
| `POST /api/v1/signals` | title, summary, topicFamily, sourceFamily, URL/local ref | `Signal`, optional `WorkCard` | `Signal` | `signal.created`, `card.created` | missing provenance, invalid topic |
| `POST /api/v1/monitoring-runs` | topicId, mode, lookbackWindow | `MonitoringRun`, created signals, gaps | `MonitoringRun`, `Signal` | `monitoring_run_update` | provider disabled, invalid topic |
| `POST /api/v1/board-cards` | signalId, title, stageKey | `WorkCard` | `WorkCard` | `card.created` | signal missing, duplicate card |
| `PUT /api/v1/board-cards/{id}/state` | targetStatus, stageKey, reason | updated `WorkCard` | `WorkCard`, `ActivityEvent` | `card.state_changed`, `card_move` | invalid transition, missing required fields |
| `POST /api/v1/decisions` | cardId, type, decision, rationale, owner, confidence | `Decision` | `Decision` | `decision.changed` | missing rationale/owner |
| `POST /api/v1/actions` | cardId, decisionId, nextStep, owner, dueDate, definitionOfDone | `ActionPlan` | `ActionPlan` | `action.created` | missing validation signal |
| `POST /api/v1/delegations` | cardId, request, owner, expectedDeliverable, checkInWindow | `Delegation` | `Delegation` | `delegation.created` | missing review criteria |
| `POST /api/v1/output-surfaces` | cardId, type, title, content/AI purpose | `OutputArtifact` | `OutputArtifact`, `AiRun` optional | `output.generated` | invalid type, missing lineage |
| `POST /api/v1/notification-rules` | cardId, criteria, frequency, threshold, cooldown, quietHours | `WatchRule` | `WatchRule` | `watch_rule.updated` | invalid criteria, duplicate active rule |
| `POST /api/v1/notifications/trigger-test` | ruleId, simulatedPayload | `Alert`, `Notification` | `Alert` | `alert.fired`, `notification` | cooldown, dedupe suppressed |
| `POST /api/v1/activity-events` | actor, target, summary, payload | `ActivityEvent` | `ActivityEvent` | `activity_append` | invalid target |
| `POST /api/v1/ai-runs` | purpose, targetType, targetId, provider/model | `AiRun` | `AiRun` | `ai_run_update` | provider disabled, rate limited |
| `POST /api/v1/validation-runs` | targetType, targetId, checks | `ValidationRun` | `ValidationRun` | `validation.completed` | unknown check |

Also implement/stub route families: `/api/v1/workspaces`, `/api/v1/topics`, `/api/v1/sources`, `/api/v1/insights`, `/api/v1/ideas`, `/api/v1/attachments`, `/api/v1/notifications`, `/api/v1/ai-runs`.

WebSocket endpoint: `ws(s)://host/ws` with JWT token in first message or query parameter. Message shape: `{"type":"...","payload":{...},"id":"uuid"}`. Server sends `{"type":"ack","id":"..."}` for every client message, `{"type":"ping"}` every 30 seconds, and closes if no `{"type":"pong"}` within 10 seconds. Reconnect: 1s, 2s, 4s, 8s, max 30s; client resumes with `last_event_id`; server replays up to 1000 events or 5 minutes. Presence broadcasts `presence` with `user_id` and `online|offline`; `presence_list` returns channel presence.

Lifecycle events and payloads:

| Event | Payload fields |
|---|---|
| `signal.created` | `signalId`, `topicFamily`, `sourceFamily`, `dedupeKey` |
| `card.created` | `cardId`, `signalId`, `stageKey`, `status` |
| `card.state_changed` | `cardId`, `fromStatus`, `toStatus`, `actor`, `validationRunId` |
| `card_move` | `cardId`, `fromStage`, `toStage`, `position`, `workspaceId` |
| `decision.changed` | `decisionId`, `cardId`, `type`, `owner`, `confidence` |
| `action.created` | `actionId`, `cardId`, `owner`, `dueDate` |
| `delegation.created` | `delegationId`, `cardId`, `owner`, `checkInWindow` |
| `output.generated` | `outputId`, `cardId`, `type`, `status`, `lineage` |
| `watch_rule.updated` | `ruleId`, `cardId`, `frequency`, `isActive` |
| `alert.fired` | `alertId`, `ruleId`, `category`, `severity`, `dedupeKey` |
| `validation.completed` | `validationRunId`, `targetType`, `targetId`, `result` |
| `activity_append` | `eventId`, `targetType`, `targetId`, `summary` |
| `monitoring_run_update` | `runId`, `status`, `createdSignalIds`, `gaps` |
| `ai_run_update` | `aiRunId`, `purpose`, `status`, `estimatedCost` |
| `output_surface_update` | `outputId`, `status`, `version` |
| `notification` | `notificationId`, `severity`, `title`, `status` |
| `error` | `code`, `message`, `correlationId` |

## 10. Notifications, alerts, and watch rules

A watch rule is created from a card, action, delegation, output, or alert when future changes, deadlines, confirmations, or recurrence matter. It stores `criteriaJson`, `frequency`, `threshold`, `comparisonOperator`, `actionJson`, `cooldownWindow`, `quietHoursJson`, `lastFiredAt`, and `isActive`.

| Alert category | Rule input | Matching criteria | Escalation | Conversion back into loop |
|---|---|---|---|---|
| `reminder` | action/delegation due window | no status evidence by check-in | info → warning after missed window | update card or create follow-up signal |
| `opportunity` | high actionability/relevance | new signal matching topic and threshold | toast; optional digest | create new `Signal` and linked `WorkCard` |
| `risk` | risk/watch item | confidence and urgency exceed threshold | warning → critical if repeated | create warning card |
| `deadline` | date entity | deadline within lookback/lead time | critical when near | create action or alert card |
| `validation` | validation run | failed or blocked readiness check | warning until resolved | move card to `review` or `waiting` |
| `recurring_topic_monitoring` | topic cadence | scheduled run finds new material or gaps | digest or immediate for high severity | create signals/cards |

Deduplication uses `dedupeKey`, matched record IDs, rule ID, and evaluation period. Suppress duplicates within cooldown. Quiet hours delay non-critical alerts. Critical alerts can bypass quiet hours only when explicitly configured. Notification templates support named variables such as `{{topic}}`, `{{confidence}}`, `{{period}}`, `{{owner}}`, and locale-aware number/date/currency formatting. Noise variants: thresholds, mute rules, feedback, digest cadence, cooldown, and rule-level pause. In-app notification center is always available; email and push require explicit setup.

## 11. Validation and release-readiness

| Scenario | Test data | Expected UI | Persisted records | Realtime events | Failure diagnostics |
|---|---|---|---|---|---|
| Capture signal | Framework-X technique URL, topic `Framework-X` | Signal Inbox shows new item and card | `Signal`, `Source`, `WorkCard`, `ActivityEvent` | `signal.created`, `card.created` | validation error for missing source |
| Convert to card | same signal | `intake` card with scores/provenance | updated `WorkCard` | `card.created` | duplicate warning if matched |
| Triage | set useful, claim `announcement`, confidence high | card moves to `triage`/`investigate` | updated `Signal`, `ActivityEvent` | `card.state_changed` | missing reason for discard |
| Decide | choose `generate_output` | decision drawer shows rationale | `Decision` | `decision.changed` | missing owner/confidence |
| Action/delegation | create committed action or delegation | execute/waiting column updates | `ActionPlan` or `Delegation` | `action.created` or `delegation.created` | missing definition/review criteria |
| Generate output | text/table/status/log artifact | output preview renders typed surface | `OutputArtifact`, optional `AiRun` | `output.generated` | failed/stale output with retry |
| Create watch rule | watch related releases weekly | rule builder shows active rule | `WatchRule` | `watch_rule.updated` | invalid criteria/cooldown |
| Trigger alert | simulate matching future signal | toast and notification center item | `Alert`, `Notification`, `ActivityEvent` | `alert.fired`, `notification` | dedupe/cooldown suppression shown |
| Loop back | convert alert to signal/card | new linked signal/card visible | `Signal`, `WorkCard`, links | `signal.created`, `card.created` | conversion target required |

Release gates: schema integrity; no TypeScript `any`; zod/API/UI schema parity; local-first persistence; WAL and migration backup; unsupported future schema refusal; AI output validity; accessibility and keyboard board movement; calm notification behavior; REST envelopes and RFC 7807 errors; WebSocket ack/heartbeat/resume; export/import with checksums; offline external-provider failure; complete signal-to-output loop.

Vitest covers card rendering/states, board stages/filters, forms/zod validation, notification rules, topic configuration, score display, triage variants, output renderers, activity rendering, storage/API with temporary SQLite, first-run initialization, restart persistence, migrations, backup/restore, export/import with attachments, transaction rollback, database locking/disk-full where practical, corruption detection, idempotency, pagination, empty collections, and health check. Playwright covers first run, topic edit, monitoring run, signal capture/triage, conversion to idea/action/delegation/output, board move with persisted order, keyboard movement, notification rule creation/firing, dashboard filters/date ranges, output export, activity lineage, import/export round trip, and offline/provider failure.

Before claiming browser validation, check Playwright MCP or equivalent. If unavailable, install/configure official Playwright MCP, commonly `npx @playwright/mcp@latest` when Node/npm are available. Browser validation must report command, URL, flows, screenshots/traces when useful, console/network/runtime errors, resolved findings, verified behavior, and remaining limitations. Do not stop at “the app builds.”

## 12. Concrete example: one signal through the loop

Example signal: a new Framework-X compression pattern appears in a repository note and suggests a better way to preserve exact schema/route details while reducing prompt size.

| Record | Exact first-build content |
|---|---|
| `Signal` | `id: sig_promplet_001`; `topicFamily: Framework-X`; `sourceFamily: repository`; `title: Structured compression pattern preserves prompt contracts`; `summary: A Framework-X technique keeps state machines, schema fields, routes, and acceptance checks during compression`; `url: https://example.dev/Framework-X/compress`; `retrievedAt: 2025-02-01T10:00:00Z`; `publishedAt: 2025-02-01T08:00:00Z`; `evidenceQuality: primary_source`; `claimType: announcement`; `relevanceScore: 94`; `noveltyScore: 88`; `freshnessScore: 97`; `confidenceScore: 82`; `urgencyScore: 61`; `impactScore: 79`; `actionabilityScore: 86`; `dedupeKey: Framework-X-structured-compress`; `triageStatus: new` |
| `WorkCard` | `id: card_promplet_001`; `signalId: sig_promplet_001`; `kind: signal`; `status: card_created`; `stageKey: intake`; `title: Evaluate structured Framework-X compression`; `summary: Test whether the pattern improves implementation-ready prompt specs`; `topicFamily: Framework-X`; `sourceFamily: repository`; `confidence: high`; `urgency: medium`; `relevance: 94`; `novelty: 88`; `actionability: 86`; `nextStep: Run the pattern on one product spec`; `statusEvidence: Source is primary but adoption value untested` |
| `Decision` | `id: dec_promplet_001`; `cardId: card_promplet_001`; `type: generate_output`; `decision: Create a short adoption checklist and test plan`; `rationale: Technique directly supports specification-driven prompting quality`; `alternativesJson: ["archive","watch","delegate research"]`; `owner: local_user`; `confidence: high`; `deadline: 2025-02-03`; `revisitCondition: if checklist fails to preserve exact routes/enums` |
| `ActionPlan` | `id: act_promplet_001`; `cardId: card_promplet_001`; `decisionId: dec_promplet_001`; `kind: committed`; `status: committed`; `nextStep: Apply pattern to Work Intelligence Kanban prompt and compare omitted fields`; `owner: local_user`; `dueDate: 2025-02-02`; `checklistJson: ["preserve lifecycle states","preserve schema fields","preserve API routes","preserve example records"]`; `definitionOfDone: Checklist catches all required prompt contracts`; `validationSignal: validation run passes with no omitted mandatory tables`; `needsConfirmation: true` |
| `OutputArtifact` | `id: out_promplet_001`; `cardId: card_promplet_001`; `type: text`; `title: Framework-X structured compression adoption checklist`; `status: complete`; `source: human`; `content: Checklist for preserving state machines, schemas, API contracts, realtime events, validation scenarios, and concrete examples`; `lineageJson: {"signals":["sig_promplet_001"],"decisions":["dec_promplet_001"],"actions":["act_promplet_001"]}` |
| `WatchRule` | `id: rule_promplet_001`; `cardId: card_promplet_001`; `name: Watch for Framework-X compression updates`; `frequency: weekly`; `criteriaJson: {"topicFamily":"Framework-X","keywords":["compression","schema preservation","Framework-X"],"minConfidence":70}`; `threshold: 1`; `comparisonOperator: ">="`; `cooldownWindow: 7d`; `quietHoursJson: {"start":"20:00","end":"08:00"}`; `isActive: true` |
| `Alert` | `id: alert_promplet_001`; `ruleId: rule_promplet_001`; `cardId: card_promplet_001`; `category: opportunity`; `severity: warning`; `title: New Framework-X compression update found`; `body: A related update exceeded confidence threshold and may improve the checklist`; `matchedRecordIdsJson: ["sig_promplet_002"]`; `dedupeKey: rule_promplet_001:sig_promplet_002`; `status: unread` |
| `ActivityEvent` | `id: evt_promplet_001`; `type: card.state_changed`; `actor: human`; `targetType: WorkCard`; `targetId: card_promplet_001`; `summary: Card moved from intake to output_generated after adoption checklist was approved`; `payloadJson: {"fromStatus":"card_created","toStatus":"output_generated","outputId":"out_promplet_001"}`; `visibility: public`; `correlationId: loop_promplet_001`; `traceId: trace_promplet_001` |
| `ValidationRun` | `id: val_promplet_001`; `targetType: OutputArtifact`; `targetId: out_promplet_001`; `result: passed`; `checksJson: ["lineage present","required sections present","watch rule active","no external call without disclosure"]`; `errorsJson: []` |

The example is accepted only when the UI shows the signal in the inbox, the card on the board, the decision/action in the drawer, the typed output artifact with lineage, the active watch rule, the alert in the notification center, and activity events linking every transition.

## 13. Final acceptance proof

The build is complete only when all are true:

1. User creates/selects a workspace and sees active workspace path.
2. SQLite initializes in WAL mode; migrations run safely; backup occurs before pending migrations; unsupported future schema is refused.
3. Default topic families and stages are seeded and editable.
4. User configures topic intent, source preferences, exclusions, cadence, lookback, watch conditions, alert thresholds, digest cadence, and `whyItMatters`.
5. Monitoring run records date, cadence, lookback, topic, mode, new items, still-important context, source coverage, and gaps.
6. Signal preserves provenance, evidence quality, retrieved/published times, classification, scores, dedupe, muted/rejected history.
7. User triages signal as useful, irrelevant, duplicate, watch later, muted, archived, or converted.
8. Signal becomes idea/decision/action/delegation/output or deliberate archive with lineage.
9. Decisions preserve rationale, alternatives, triggering inputs, owner, confidence, revisit condition.
10. Actions and delegations preserve owner, next step/request, due/check-in, definition/review criteria, blockers, status evidence.
11. Board cards represent mixed work-intelligence objects and include relevance, novelty, confidence, source family, actionability, owner, next step, status evidence, output linkage.
12. Board stages include `intake`, `triage`, `investigate`, `decide`, `execute`, `waiting`, `review`, `shipped`, `watch_later`, `archived`.
13. Card movement validates transitions, rolls back failed optimistic updates, emits activity, broadcasts realtime, and has keyboard alternative.
14. Output surfaces render at least text, table, status, and log with lineage, status, and actions.
15. Dashboard shows signal volume, conversion rate, stale ideas, delegated work awaiting response, high-confidence warnings, decisions pending, outputs produced, source gaps, AI usage/cost; charts support dark/light, responsive resize, accessible palettes, tooltips, PNG export.
16. Tables support sorting, shift-click multi-sort, search, filters, pagination 10/25/50/100, row actions, bulk actions, empty states.
17. Alert rules support `>`, `>=`, `<`, `<=`, `==`, `between`, dedupe, cooldown, quiet hours, escalation, toast, and persistent notification center.
18. AI is provider-agnostic, configurable, cost-tracked, rate-limited, inspectable, sanitized, user-overridable, and gracefully degraded offline.
19. `GET /api/health` returns local store status, schema version, app version, active workspace path health, and migration state.
20. REST envelopes, RFC 7807 errors, pagination, idempotency, WebSocket ack/heartbeat/resume/replay, export/import, backup/restore, and offline visibility are tested.
21. Playwright MCP or equivalent browser validation reports command, URL, flows, findings, screenshots/traces when useful, verified behavior, and remaining limitations.
22. Final implementation contains no TypeScript `any`; logs avoid secrets and sensitive payloads by default.
