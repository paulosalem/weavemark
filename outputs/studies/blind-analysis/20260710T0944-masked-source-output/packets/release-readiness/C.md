# Blind evaluation packet

Study: Release Readiness Workbench
Variant: C
Mode: source-and-output

Evaluate only the anonymous artifact content. Do not use filenames, marker guesses, known study history, or presumed authoring condition.

## Source material

# @{app_name}: Framework-X Single-Output Release Readiness Spec

@directive-c target: structure preserve: hard
  @directive-a programming/foundations/software-spec
    Mingle refinements into one release workspace; no appendices.

  @directive-a programming/stacks/stack-typescript-nextjs-prisma-sqlite
  @directive-a programming/types/type-local-first-webapp

  Design @{app_name}: a local-first release command center that turns messy
  release material into gates, evidence, validation, risks, actions, notes, and
  go/no-go records. Produce one implementation spec only.

  @directive-b mode: intention focus: "gate -> evidence -> validation -> decision -> launch audit"
    Release notes, docs, examples, validation commands, screenshots, package
    artifacts, risks, waivers, and confidence.

  ## Gates and evidence

  @directive-a product/release-readiness-gate
    Release readiness is the central domain model.
  @directive-a guidelines/release-evidence-quality
  @directive-a programming/validation/release-validation-matrix
  @directive-a programming/validation/playwright-mcp-browser-validation

  ## Inputs and artifacts

  @directive-a reasoning/unstructured-input-normalization
    Messy material becomes structured release facts.
  @directive-a product/release-artifact-readiness
    Apply to @{release_surfaces}.
  @directive-a guidelines/prompt-quality
  @directive-a guidelines/context-sufficiency
  @directive-a guidelines/evidence-quality

  ## Decisions and actions

  @directive-a decision/strategy-selection
  @directive-a decision/forecast-uncertainty
  @directive-a decision/values-tradeoff
  @directive-a lenses/decision-gate
  @directive-a reasoning/action-planning
    Gaps, failed checks, risks, blockers, and waivers become owned actions.

  ## Workspace and UI

  @directive-a programming/modules/module-card
  @directive-a programming/modules/module-workflow-board
  @directive-a programming/modules/module-output-surfaces
  @directive-a programming/modules/module-dashboard
  @directive-a programming/modules/module-notifications
  @directive-a programming/modules/module-activity-stream
  @directive-a programming/modules/module-local-sqlite-storage
  @directive-a programming/modules/module-ai-features
    Evidence-link every material AI claim.
  @directive-a programming/modules/module-rest-api
  @directive-a programming/modules/module-realtime
  @directive-a programming/debugging/root-cause-debugging
    Failed checks become diagnose, fix, retest, and prevention loops.
  @directive-a product/product-validation-surface
    Prove messy import -> gate -> validation -> fix/rerun -> note -> decision
    -> audit export.

  ## Required output

  Produce one implementation spec covering architecture, local storage, release
  gates, validation, evidence, artifacts, risks, waivers, decisions, board,
  outputs, dashboards, notifications, APIs, events, AI rules, privacy,
  root-cause loops, release notes, rollback/monitoring, failures, scripts, and
  acceptance.


## Variable payload

{
  "app_name": "Release Readiness Workbench",
  "release_surfaces": "- Framework-X public README, docs, examples, generated outputs, study results, and release notes;\n- package artifacts, extension builds, CLI behavior, and installation checks;\n- single-output validation studies, qualitative evidence, and score explanations;\n- browser-facing examples, screenshots, traces, and console/runtime findings;\n- issues, PR notes, local TODOs, deferred work, waivers, and known limitations."
}


## Compiled output

# Release Readiness Workbench — Implementation Specification

Build **Release Readiness Workbench**, a local-first release command center that turns messy release material into structured gates, evidence, validation, risks, actions, notes, and go/no-go records. This is a directly implementable TypeScript/Next.js/Prisma/SQLite application specification for an AI programming agent. The result is a single local workspace for proving whether a release is ready across Framework-X public README, docs, examples, generated outputs, study results, release notes, package artifacts, extension builds, CLI behavior, installation checks, single-output validation studies, qualitative evidence, score explanations, browser-facing examples, screenshots, traces, console/runtime findings, issues, PR notes, local TODOs, deferred work, waivers, and known limitations.

## 1. Product intent

- Target user: maintainers preparing a public software/prompt/tooling release who need inspectable confidence rather than optimistic launch prose.
- Core job: import fragmented release material, normalize it into facts, map it to release gates and artifacts, run or record validation, attach evidence, triage failures, track actions, decide go/no-go/limited release, and export an audit-ready release record.
- First-build value: one user can run the app locally, create or import a release candidate workspace, see readiness by gate, preserve evidence, fix/rerun failures, write accurate release notes, and produce a final release decision.
- The specification is implementation guidance, not an interview script. Make safe assumptions where needed and expose only genuinely blocking open decisions.

## 2. Platform and technical constraints

### Stack

- Next.js 14+ with App Router.
- TypeScript 5+ strict mode; no `any`.
- Tailwind CSS with design tokens in `tailwind.config.ts`.
- React Server Components by default; client components only for interactive boards, filters, forms, charts, browser-only variants, and live updates.
- Zustand only for local UI state that should not be canonical.
- `react-hook-form` plus shared `zod` schemas for forms, Server Actions, and API routes.
- Node.js runtime only for routes/actions touching SQLite; do not use Edge runtime for storage paths.
- Prisma with SQLite provider.
- SQLite 3 in WAL mode.
- Prisma Migrate for deterministic versioned migrations.
- Vitest with happy-dom for component tests.
- Vitest with temporary SQLite files and isolated data directories for API/storage tests.
- Playwright for critical local user flows.
- Minimum 80% line coverage for application logic.
- Target: local Node.js process, self-hosted single-user service, or optional Electron/Tauri wrapper.
- Not supported by default: serverless deployments with ephemeral or shared filesystem state.

### Local-first boundaries

- The app MUST be useful without a hosted multi-tenant backend.
- Do not add billing, subscriptions, tenant isolation, organization onboarding, or hosted accounts.
- The local machine is the source of truth.
- Browser `localStorage`, IndexedDB, memory, and cache files MAY improve UX but MUST NOT be canonical for user data.
- External network calls, including AI calls, MUST be explicit in UI and configuration; existing local data must remain viewable when those calls fail.
- Keep private release material local by default.
- Before sending any release material to an external AI, web, or integration service, show destination, purpose, payload scope, and data policy.
- Logs must avoid secrets, API keys, refresh tokens, and full sensitive payloads unless the user explicitly enables diagnostic capture.

## 3. Workspace and storage model

### Workspace

- Provide one default local workspace and allow the user to choose/create another workspace directory.
- Store the SQLite database, attachments, generated artifacts, evidence files, screenshots, traces, validation logs, backups, repair logs, and exports under the workspace directory or OS user-data directory.
- Show active workspace path, database path, schema version, app version, and storage health in Settings and Diagnostics.
- Development default SHOULD be inspectable, e.g. `.local-data/app.sqlite`.
- Packaged apps SHOULD use the OS user-data directory.
- Provide backup, restore, import, and export flows so workspaces can move between machines without hidden server state.

### Startup and migrations

- Validate workspace readability, writability, schema version, available disk, and attachment directory access at startup.
- If the local store is missing, initialize deterministically with migrations.
- If existing data is present, create a timestamped backup before running pending migrations unless the database is unreadable.
- Refuse to start on unsupported future schema versions; show a recoverable error.
- If the store is locked, corrupted, too new, disk-full, or migration-failed, show backup, repair, upgrade, retry, and export guidance.
- Repair tools must report changes and preserve the original damaged database when possible.

### Persistence rules

- Every durable table must include stable primary key, `createdAt DateTime @default(now())`, `updatedAt DateTime @updatedAt`, and recoverable deletion/archive behavior such as `deletedAt DateTime?`.
- Use camelCase in Prisma schema, mapped to snake_case table/column names where practical.
- Multi-entity updates MUST run in explicit transactions.
- Event insertion and visible state updates MUST be persisted in the same transaction when the event explains the state change.
- Use optimistic concurrency fields such as `version` or `updatedAt` for records that may be edited by the user and AI/automation.
- Large attachments and generated artifacts should live as files under the workspace, not database blobs by default.
- Store attachment metadata: content hash, MIME type, byte size, origin, relative file path, created/updated timestamps, and integrity status.
- Deleting a record must define whether referenced files are retained, archived, garbage-collected, or moved to a trash area.
- Exports MUST include SQLite database, referenced files, schema version, app version, and manifest checksums.

## 4. Domain model

Define explicit relational tables and TypeScript/Zod domain schemas for these entities.

### Core entities

- `Workspace`
  - `id`, `name`, `path`, `schemaVersion`, `appVersion`, `settings`, `createdAt`, `updatedAt`.
- `ReleaseCandidate`
  - `id`, `workspaceId`, `name`, `version`, `description`, `status`, `targetDate`, `createdAt`, `updatedAt`, `deletedAt`.
  - Status enum: `draft`, `normalizing`, `validating`, `blocked`, `ready_with_caveat`, `ready`, `released`, `archived`.
- `SourceMaterial`
  - `id`, `releaseCandidateId`, `kind`, `title`, `rawText`, `fileRef`, `sourceUri`, `sourceLabel`, `freshnessDate`, `importedAt`, `confidence`, `createdAt`, `updatedAt`.
  - Kinds include notes, README, docs, examples, generated output, package artifact, extension build, CLI output, screenshot, trace, console finding, issue, PR note, TODO, waiver, limitation, study, release note.
- `NormalizedFact`
  - `id`, `releaseCandidateId`, `sourceMaterialId`, `factType`, `statement`, `sourceQuote`, `inferenceLevel`, `confidence`, `contradictionGroupId`, `staleness`, `createdAt`, `updatedAt`.
  - Preserve source fidelity: explicit facts, inferred structure, decisions, action candidates, risks/blockers, open questions, and confidence notes must be distinguishable.
- `Gate`
  - `id`, `releaseCandidateId`, `track`, `title`, `criteria`, `owner`, `status`, `confidence`, `dueDate`, `releaseImpact`, `createdAt`, `updatedAt`.
  - Tracks: product behavior, documentation, examples, tests, packaging, install, security/privacy, performance, accessibility, support, rollback/monitoring, browser validation, AI/prompt quality, release notes.
  - Status enum: `ready`, `ready_with_caveat`, `needs_fix`, `defer`, `not_applicable`, `not_checked`, `blocked`.
- `GateCriterion`
  - `id`, `gateId`, `threshold`, `currentRead`, `status`, `confidence`, `evidenceRequirement`, `createdAt`, `updatedAt`.
- `Evidence`
  - `id`, `releaseCandidateId`, `gateId`, `artifactId`, `validationCheckId`, `claimId`, `type`, `title`, `summary`, `fileRef`, `command`, `environment`, `scope`, `freshnessDate`, `limitations`, `qualityLevel`, `createdAt`, `updatedAt`.
  - Evidence types: passing command, inspected output, screenshot, trace, source review, user-flow run, package artifact, security check, documentation review, console/network/runtime observation, reviewer note, explicit waiver.
  - Quality levels: `verified`, `partial`, `proxy`, `waived`, `missing`, `stale`.
- `Artifact`
  - `id`, `releaseCandidateId`, `surface`, `audience`, `purpose`, `owner`, `status`, `freshnessDate`, `risk`, `dependency`, `releaseImpact`, `createdAt`, `updatedAt`.
  - Statuses: `draft`, `verified`, `stale`, `waived`, `deferred`, `blocked`.
- `PublicClaim`
  - `id`, `releaseCandidateId`, `artifactId`, `claimText`, `source`, `evidenceStatus`, `caveat`, `reviewer`, `signoffAt`, `createdAt`, `updatedAt`.
- `ValidationCheck`
  - `id`, `releaseCandidateId`, `category`, `name`, `commandOrFlow`, `environment`, `expectedProof`, `owner`, `status`, `failureMeaning`, `releaseImpact`, `lastRunAt`, `createdAt`, `updatedAt`.
  - Categories include unit, integration, type, lint, build, packaging, install, browser/UI, example, documentation, migration, import/export, performance, accessibility, security/privacy, rollback, first-run, repeated-run, upgrade, downgrade/rollback, offline, corrupt state, missing dependency, partial-failure.
- `ValidationAttempt`
  - `id`, `validationCheckId`, `startedAt`, `finishedAt`, `status`, `command`, `exitCode`, `logFileRef`, `screenshotRefs`, `traceRefs`, `consoleFindings`, `notes`, `createdAt`, `updatedAt`.
  - Preserve failed and passed attempts; never overwrite history.
- `Risk`
  - `id`, `releaseCandidateId`, `title`, `severity`, `likelihood`, `impact`, `mitigation`, `owner`, `trigger`, `decision`, `status`, `createdAt`, `updatedAt`.
- `Waiver`
  - `id`, `releaseCandidateId`, `scope`, `reason`, `riskAccepted`, `decisionMaker`, `expiresAt`, `revisitTrigger`, `linkedEvidenceId`, `createdAt`, `updatedAt`.
- `ActionItem`
  - `id`, `releaseCandidateId`, `sourceType`, `sourceId`, `title`, `description`, `owner`, `priority`, `status`, `dueDate`, `dependency`, `definitionOfDone`, `verificationStep`, `createdAt`, `updatedAt`.
  - Source types include gap, failed check, risk, blocker, waiver, stale artifact, prompt-quality issue, docs gap, package problem, browser finding.
- `DecisionRecord`
  - `id`, `releaseCandidateId`, `gate`, `reason`, `confidence`, `decision`, `rationale`, `decisiveUncertainties`, `valuesTradeoffs`, `forecastScenario`, `changeTrigger`, `reviewCadence`, `createdAt`, `updatedAt`.
  - Decision values: `go`, `no_go`, `wait`, `investigate`, `limited_release`.
- `ActivityEvent`
  - `id`, `type`, `actor`, `targetType`, `targetId`, `timestamp`, `summary`, `payload`, `visibility`, `correlationId`, `traceId`.
  - Actor values: human, agent, integration, system, automation.
  - Visibility values: public, team-only, private, internal, redacted where applicable.
- `OutputSurface`
  - `id`, `hostId`, `type`, `title`, `contentRef`, `schemaVersion`, `status`, `source`, `lineage`, `createdAt`, `updatedAt`.
  - Surface types: text, program, table, diff, image, chart, status, log, terminal, form, canvas, file, release-audit, release-notes.
  - Status values: draft, streaming, complete, failed, stale, superseded, approved.
- `NotificationRule`
  - `id`, `name`, `condition`, `threshold`, `operator`, `channel`, `template`, `cooldown`, `lastFiredAt`, `enabled`, `createdAt`, `updatedAt`.
  - Operators: `>`, `>=`, `<`, `<=`, `==`, `between`.
- `AiRun`
  - `id`, `releaseCandidateId`, `purpose`, `provider`, `model`, `inputSummary`, `payloadPolicy`, `outputSurfaceId`, `tokenUsage`, `estimatedCost`, `status`, `createdAt`, `updatedAt`.

### Indexes

Add indexes for:

- release candidate status/date queries;
- gate status/track/owner queries;
- evidence by gate, artifact, claim, quality, and freshness;
- action board columns, owner, priority, due date, status;
- validation check status/category/release impact;
- activity stream target/timestamp/correlation;
- full-text search over source material, normalized facts, claims, actions, decisions, and notes where practical;
- attachment hash lookups;
- dependency lookups.

## 5. Core workflows

### First successful session

A new user must be able to:

1. Start the app and see workspace diagnostics.
2. Create a release candidate named and versioned by the user.
3. Paste or import messy release material: README excerpts, docs notes, package output, CLI install checks, study notes, screenshots/traces, issue/PR snippets, TODOs, known limitations, waivers.
4. Normalize material into source facts, inferred structure, decisions, action candidates, risks/blockers, open questions, and confidence notes without inventing facts.
5. Review extracted facts and correct low-confidence interpretations.
6. Generate a default release gate matrix and artifact inventory.
7. Add or link evidence to gates, artifacts, validation checks, and public claims.
8. Run or record validation attempts.
9. See failures become owned actions with verification steps.
10. Fix or mark actions, rerun affected checks, and preserve failed/passed history.
11. Draft release notes that distinguish verified behavior from known limitations.
12. Produce a final gate decision: go, no-go, wait, investigate, or limited release.
13. Export an audit bundle including gate matrix, evidence ledger, validation matrix, risk register, action board, release notes, decision record, activity stream, and referenced artifacts.

### Messy input normalization

- Preserve source fidelity; never invent facts, owners, dates, commitments, dependencies, or causal links.
- Separate explicit statements from reasonable inferences.
- Identify duplicates, contradictions, ambiguity, missing context, stale items, and low-confidence interpretations before downstream analysis.
- Keep raw wording when it carries nuance, stakeholder intent, or uncertainty.
- Convert fragments into clear units without making them falsely certain.
- UI must show:
  - Source facts.
  - Inferred structure.
  - Decisions.
  - Action candidates.
  - Risks and blockers.
  - Open questions.
  - Confidence notes.
- If context is insufficient for a confident readiness conclusion, show context status near the top: sufficient, limited, or insufficient; list missing context, impact, safe output, and next evidence.

### Gate workflow

- Create system default gates per release candidate and allow user customization.
- Each gate shows criteria, owner, status, evidence, blocker, risk, decision, due date, confidence, and release impact.
- A gate cannot be marked ready without objective evidence or an explicit waiver.
- Distinguish claimed readiness from verified readiness.
- Treat not checked, not reproducible, unknown, waived, partial, stale, and verified as distinct states.
- Blockers must create or link to an action with owner, verification step, and release consequence.
- Deferred work must preserve rationale and revisit trigger.
- The final release review must explain go, no-go, wait, investigate, or limited release.

### Evidence workflow

- Every readiness claim links to evidence type, freshness, environment, scope, limitations, and quality level.
- Flag evidence that is stale, partial, proxy-only, manually asserted, not reproducible, tied to a different version, or contradicted by newer material.
- Do not smooth failed checks into success language.
- Release notes must distinguish verified behavior, partial coverage, known limitations, migration notes, deferred work, and support guidance.
- Evidence grading must assess relevance, specificity, freshness, independence, and contradictions; end with evidence grade, main gap, and decision impact.

### Validation workflow

- Provide a validation matrix with rows for relevant unit, integration, type, lint, build, packaging, install, browser/UI, example, documentation, migration, import/export, performance, accessibility, security/privacy, rollback, offline, corrupt state, missing dependency, and partial-failure checks.
- Each row records command/compact flow, environment, expected proof, owner, status, failure meaning, release impact, and fix loop.
- Save or reference validation evidence in the workspace.
- Critical checks block release unless waived through an explicit waiver path.
- After fixes, rerun affected checks and retain history of failed and passed attempts.
- Failure triage must record observed behavior, expected behavior, failure surface, evidence summary, ranked root-cause hypotheses, fastest diagnostic step, minimal fix, verification plan, and prevention task.

### Decision workflow

- Classify decision shape before recommending a gate outcome: reversible, irreversible, forecast-heavy, values-heavy, option-preserving, portfolio, or adversarial where relevant.
- Define gate criteria and thresholds before classifying the decision.
- Required final decision surface starts with:
  - `Gate: go | no-go | wait | investigate`
  - `Reason: one-sentence rationale`
  - `Confidence: low | medium | high`
- Include a criterion table with threshold, current read, gate status, and confidence.
- Include blockers, next evidence, and change trigger.
- For forecast-sensitive releases, capture base case/upside/downside, leading indicators, robust action, contingent action, and review cadence.
- For values tradeoffs, capture values in tension, acceptable compromises, regrets the decision-maker will or will not accept, boundary conditions, and what the chosen option sacrifices.

## 6. User interface

### Information architecture

Implement these primary routes:

- `/` dashboard for current release candidate or workspace overview.
- `/releases` list/create/import release candidates.
- `/releases/{id}` release command center overview.
- `/releases/{id}/import` source material import and normalization review.
- `/releases/{id}/gates` gate matrix board/table.
- `/releases/{id}/evidence` evidence ledger.
- `/releases/{id}/artifacts` artifact inventory and public-claim ledger.
- `/releases/{id}/validation` validation matrix and attempt history.
- `/releases/{id}/actions` action workflow board.
- `/releases/{id}/risks` risk register and waivers.
- `/releases/{id}/notes` release notes and support guidance.
- `/releases/{id}/decision` final decision record.
- `/releases/{id}/activity` activity stream.
- `/releases/{id}/export` audit export preview.
- `/settings` workspace, AI provider, privacy, notifications, backup/restore, diagnostics.

### Cards

Cards represent gates, artifacts, evidence, validation checks, actions, risks, waivers, claims, decisions, and activity highlights.

Each card must define:

- `id`, `kind`, `title`, `summary`, `body`, `badges`, `metadata`, `actions`, `links`, `state`, and relevant timestamps.
- Required creation fields and computed fields per card family.
- Compact card view and full detail panel.
- Empty, loading, error, stale, disabled, and permission-limited states.
- Pointer and keyboard access for primary actions.
- Visible focus, semantic labels, sufficient contrast, and screen-reader text for icon-only variants.
- Unambiguous click, drag, context menu, checkbox selection, inline edit, expand, archive, dismiss, reorder, undo, and navigation behavior.

### Workflow board

- Use a board for actions and optionally for gates/artifacts.
- Define unit type and grouping model explicitly.
- Default action columns: inbox, needs owner, in progress, blocked, ready for retest, verified, deferred.
- Gate board columns: not checked, needs fix, blocked, ready with caveat, ready, not applicable.
- Columns have stable identifiers, display names, ordering, optional descriptions, counts, WIP indicators, overdue indicators, and blocked indicators.
- Drag-and-drop must have accessible keyboard alternatives.
- Movement rules must validate allowed transitions and show the reason when movement is blocked.
- Reordering persists with optimistic rollback on failure.
- Movement may trigger assignment, notification, review, approval, archive, escalation, or affected-check rerun prompts.
- Users can create, view, edit, duplicate, archive/delete, search, filter, sort, bulk-select, and save views.
- Board state persists across refresh and app restart.

### Output surfaces

Render distinct outputs through typed surfaces instead of one undifferentiated text area:

- Text: release notes, decision records, review notes.
- Program/log/terminal: command outputs, validation logs, CLI behavior.
- Table: gate matrix, evidence ledger, validation matrix, action table, public-claim ledger.
- Diff: release-note edits, README/doc claim changes.
- Image/media: screenshots, traces, browser captures.
- Status: readiness summary, health, confidence, evidence coverage.
- Form: decision, waiver, validation attempt, notification rule.
- File: package artifacts, exports, study outputs.
- Canvas/diagram only if useful for dependency or flow visualization.

Surfaces must support copy, download, approve, comment, apply, export, open, compare, pin, minimize, lineage, failed/stale explanations, and version history where decisions depend on them.

### Dashboard and visualizations

- Responsive grid: 1 column mobile, 2 tablet, 3–4 desktop.
- Widgets are self-contained cards with title bar, content area, optional action menu, loading skeleton, error state, and retry.
- Drag-to-reorder and show/hide widgets, persisted to preferences.
- Release-specific widgets:
  - gate readiness by track;
  - evidence quality distribution;
  - stale/missing evidence count;
  - validation status over time;
  - action aging and blocked owners;
  - risk severity/likelihood matrix;
  - release decision confidence;
  - artifact readiness by surface;
  - public claim evidence coverage.
- Use a lightweight charting library such as Chart.js, Recharts, or Plotly.
- Required chart behaviors: dark/light theme, responsive resize, accessible palettes, hover tooltips with formatted values, export as PNG.
- Data tables support sortable columns, shift-click multi-sort, text/dropdown filters, pagination 10/25/50/100, total count, row actions, bulk actions, empty state, and export.

### Activity stream

- Append-only by default.
- Event model: `id`, `type`, `actor`, `target`, `timestamp`, `summary`, `payload`, `visibility`, `correlation_id` or `trace_id`.
- Persist events before broadcasting live updates.
- Support pagination, incremental loading, live append, filters by type/actor/severity/source/errors, link/copy/reference for important events.
- Render compact routine events and expandable significant events.
- Distinguish human, agent, automation, system, errors, decisions, and output updates.
- Show relative time for scanning and exact timestamp in detail.
- Preserve chronological clarity when events arrive out of order or replay after reconnect.
- Avoid secrets and excessive raw internals.
- Record enough lineage to connect prompts, AI runs, tool calls, artifacts, questions, answers, validation attempts, and final outputs.

### Notifications

- Users define alert rules with condition, threshold, comparison operator, and action.
- Evaluate rules after relevant gate/evidence/action/validation/risk changes.
- Channels:
  - in-app toast plus persistent notification center;
  - optional email digest only if configured locally;
  - optional web push via Service Worker + VAPID keys.
- Deduplicate: same rule MUST NOT fire more than once per evaluation period; track last-fired timestamp and cooldown.
- Templates support named release variables such as `{release}`, `{gate}`, `{status}`, `{owner}`, `{dueDate}`, `{risk}`, `{evidenceQuality}` with locale-aware date/number formatting.
- Example rules:
  - notify when a critical gate becomes blocked;
  - notify when evidence becomes stale;
  - notify when an action is overdue;
  - notify when final release decision changes.

## 7. AI features

### Provider abstraction

- Implement provider-agnostic LLM interface supporting OpenAI, Anthropic, and local models.
- Configuration per use case: provider, model name, temperature, max tokens, system prompt, data policy, enabled/disabled state.
- Retry policy: exponential backoff 1s, 2s, 4s; max 3 retries on 429/500/503.
- Cost tracking: prompt tokens, completion tokens, total tokens, estimated cost per request.
- Graceful degradation: show “AI unavailable” badge and use rule-based fallback when provider is unavailable.
- Include `data_policy: no_training` in API calls where supported.
- Do not use user data for training.
- Rate-limit local AI calls by configured workspace policy rather than subscription tiers.

### AI-supported workflows

- Normalize messy release material into explicit facts, inferred structure, risks, actions, evidence candidates, open questions, and confidence notes.
- Suggest gate criteria from imported source material.
- Suggest validation checks from release surfaces.
- Detect public claims in README/docs/release notes and require evidence links.
- Draft release notes with verified behavior separated from known limitations, deferred work, migration notes, and support guidance.
- Summarize failed validation attempts into root-cause hypotheses and retest actions.
- Generate decision drafts using gate, evidence, risk, action, validation, and waiver records.

### AI safety and evidence rules

- Every material AI claim MUST be evidence-linked or marked as inference with confidence.
- AI output must preserve uncertainty and source fidelity.
- AI may propose actions, not silently mutate release decisions.
- Before sending data externally, show destination, purpose, included fields, and privacy warning.
- Sanitize inputs by redacting secrets and sensitive local paths where possible.
- Store AI lineage: prompt/input summary, source record IDs, provider/model, created surface, token usage, cost estimate, and user approval state.
- Generated surfaces distinguish draft/speculative output from verified output.

## 8. API and server behavior

### REST standards

- Use `/api/v1/...` for versioned app APIs.
- Resources are plural nouns.
- Nesting limited to one level.
- Use query parameters for filtering, sorting, pagination: `?status=active&sort=-created_at&page=1&per_page=20`.
- Content-Type: `application/json`.
- Collection response envelope: `{"data": ..., "meta": {...}}`.
- Single-resource envelope: `{"data": ...}`.
- Pagination meta: `{"total": N, "page": P, "per_page": S, "total_pages": T}`.
- Empty collections return `{"data": [], "meta": {"total": 0, ...}}`, never 404.
- Error responses MUST follow RFC 7807 Problem Details:
  json
  {
    "type": "https://api.example.com/errors/validation",
    "title": "Validation Error",
    "status": 422,
    "detail": "field 'amount' must be a positive integer",
    "errors": [{"field": "amount", "message": "must be a positive integer"}]
  }
  - Status codes: 400 bad input, 401 not authenticated if local auth is enabled, 403 forbidden, 404 not found, 409 conflict, 422 validation, 429 rate limit, 500 server error.
- POST creates MUST accept `Idempotency-Key`; repeated key within 24 hours returns original response.
- GET, PUT, DELETE are inherently idempotent.

### Required endpoints

- `GET /api/health`
  - returns local store status, schema version, app version, workspace path hash, migration status, attachment directory status.
- Release candidates:
  - `GET /api/v1/releases`
  - `POST /api/v1/releases`
  - `GET /api/v1/releases/{id}`
  - `PUT /api/v1/releases/{id}`
  - `DELETE /api/v1/releases/{id}`
- Source material and normalization:
  - `GET /api/v1/releases/{id}/sources`
  - `POST /api/v1/releases/{id}/sources`
  - `POST /api/v1/releases/{id}/normalize`
- Gates, evidence, artifacts, claims:
  - `GET /api/v1/releases/{id}/gates`
  - `PUT /api/v1/gates/{id}`
  - `GET /api/v1/releases/{id}/evidence`
  - `POST /api/v1/releases/{id}/evidence`
  - `GET /api/v1/releases/{id}/artifacts`
  - `GET /api/v1/releases/{id}/claims`
- Validation:
  - `GET /api/v1/releases/{id}/validation-checks`
  - `POST /api/v1/validation-checks/{id}/attempts`
  - `POST /api/v1/validation-attempts/{id}/evidence`
- Actions, risks, waivers, decisions:
  - `GET /api/v1/releases/{id}/actions`
  - `PUT /api/v1/actions/{id}`
  - `GET /api/v1/releases/{id}/risks`
  - `GET /api/v1/releases/{id}/waivers`
  - `POST /api/v1/releases/{id}/decision`
- Activity/export:
  - `GET /api/v1/releases/{id}/activity`
  - `POST /api/v1/releases/{id}/export`

### Real-time updates

- Use WebSocket or Server-Sent Events for local live updates. If WebSocket is used:
  - Endpoint: `ws(s)://host/ws`.
  - Message format: JSON with `{"type": "...", "payload": {...}, "id": "uuid"}`.
  - Server sends `{"type": "ack", "id": "..."}` for every client message.
  - Heartbeat: server sends `{"type": "ping"}` every 30 seconds.
  - Client responds with `{"type": "pong"}` within 10 seconds or connection closes.
  - Client reconnection uses exponential backoff: 1s, 2s, 4s, 8s, max 30s.
  - On reconnect, client sends `{"type": "resume", "payload": {"last_event_id": "..."}}`.
  - Server replays missed events since `last_event_id`, up to 1000 events or 5 minutes.
- Message types:
  - `state_update` for entity changes with `entity_id` and JSON patch changes.
  - `error` for server error with `errorKey` and `message`.
  - `presence` only if multi-window or shared local usage is implemented.
- Persist events before broadcasting.

## 9. Browser validation and implementation loop

The implementing agent MUST prove the app through browser-observed behavior, not only builds.

### Setup

- Before claiming browser validation, check whether Playwright MCP or equivalent browser automation is available.
- If Playwright MCP is not available, install or configure the official Playwright MCP server; when Node/npm are available, the common command is `npx @playwright/mcp@latest`.
- If the project needs Playwright tests, add Playwright through the project package manager and install browsers with the ecosystem command.
- Do not add duplicate/unrelated test tooling.
- If MCP setup cannot be completed, state the exact blocker and do not pretend browser validation happened.

### Build-run-observe-improve loop

Repeat until main flows work and no high-value obvious improvement remains:

1. Inspect specification, repository structure, package scripts, existing tests, framework conventions.
2. Implement the smallest coherent visible/testable slice.
3. Start the app with an existing development or preview command; if none exists, add a minimal appropriate command and document it.
4. Open the running URL with Playwright MCP.
5. Interact as a real user: create release, import material, review normalization, update gates, attach evidence, run/record validation, move actions, create waiver, draft notes, make decision, export audit.
6. Observe rendered page, accessibility tree, console output, network behavior, screenshots/traces, and persisted state.
7. Compare against spec and product quality: clarity, responsiveness, stability, accessibility, visual polish, no console/runtime errors.
8. Inspect source when browser behavior reveals a defect.
9. Improve implementation and rerun affected browser checks.

### Browser evidence

Each validation pass should save or reference:

- command used;
- URL tested;
- user flows exercised;
- screenshots or trace artifacts;
- console/network/runtime errors found and resolved;
- remaining limitations and follow-up opportunities.

Browser-facing release examples are incomplete until exercised in a real browser. Screenshots are evidence, not a substitute for interaction.

## 10. Release notes, rollback, monitoring, and support

### Release notes

- Release notes must distinguish:
  - verified behavior;
  - partial or proxy-validated behavior;
  - known limitations;
  - deferred work;
  - migration notes;
  - support guidance;
  - rollback guidance.
- Public claims must link to evidence, caveats, and reviewer sign-off.
- Prevent stale, insufficient, or proxy-only evidence from being presented as verified release success.
- Preserve waivers and accepted risk language without turning caveats into success language.

### Rollback and monitoring

- Track rollback checks in the validation matrix.
- Capture rollback steps for package artifacts, generated outputs, docs changes, examples, and extension builds where applicable.
- Add monitoring/support checklist for the software release window:
  - where to watch issues and PR feedback;
  - what evidence indicates launch health;
  - what triggers rollback, patch, documentation correction, or limited release;
  - who owns each response.

## 11. Acceptance criteria

### Product acceptance

- A user can create a release candidate and import messy release material.
- Normalization preserves explicit facts, inferences, contradictions, ambiguity, stale items, low-confidence interpretations, risks, blockers, decisions, and action candidates.
- Gate matrix shows tracks, criteria, evidence, owner, status, blocker, risk, decision, due date, confidence, and release impact.
- Gates cannot be marked ready without verified/partial evidence or explicit waiver.
- Evidence ledger records type, freshness, environment, scope, limitations, quality, linked claims, linked gates, and artifacts.
- Artifact inventory covers the configured release surfaces and shows audience, purpose, owner, status, evidence, freshness, risk, dependency, and release impact.
- Public-claim ledger prevents README/docs/release-note claims from becoming ready without evidence, caveat, or waiver.
- Validation matrix includes commands/compact flows, expected proof, owner, status, failure meaning, release impact, and attempt history.
- Failed checks create root-cause loops and owned actions with verification steps.
- Action board supports accessible movement, filtering, persistence, invalid-move recovery, and retest handoff.
- Risk register, waivers, and decision record support go/no-go/wait/investigate/limited release.
- Release notes export verified behavior separately from known limitations and deferred work.
- Audit export includes gate matrix, evidence ledger, validation matrix, risk register, action board, decision record, release notes, activity stream, and referenced files.
- Workspace survives restart and export/import.

### Technical acceptance

- TypeScript strict mode passes with no `any`.
- `GET /api/health` reports app version, schema version, local store status, and workspace diagnostics.
- SQLite runs in WAL mode.
- Migrations run on first start and upgrade with backup.
- Unsupported future schema version blocks startup safely.
- Transactions preserve consistency for linked gate/evidence/action/event updates.
- Activity events persist before live broadcasts.
- Attachment checksums detect duplicate/corrupted files.
- Tests cover first-run initialization, restart persistence, export/import, backup restore, offline operation, migrations from at least one older fixture once schema evolves, transactional rollback, corrupted-file detection, and database lock/disk-full handling where practical.
- API responses use JSON envelopes and RFC 7807 errors.
- WebSocket/SSE updates reconnect and replay missed events.
- AI features are disabled or local-safe by default, explicit before external calls, lineage-tracked, and evidence-linked.
- Browser validation covers first-session happy path, empty states, error/recovery states, repeated-use persistence, and export.

## 12. Verification plan

Run and preserve evidence for:

- `npm run typecheck`
- `npm run lint`
- `npm run test`
- `npm run test:coverage`
- `npm run build`
- Prisma migration generation/application against a temporary SQLite database.
- Startup with empty workspace.
- Restart persistence after creating a release candidate with gates, evidence, validation attempts, actions, risks, waiver, notes, and decision.
- Export/import with attachments and checksums.
- Backup/restore before migration.
- Offline use with existing data.
- Locked database, corrupted file, missing attachment, unsupported future schema, and disk-full simulation where practical.
- Playwright flow: first load -> create release -> import messy notes -> normalize -> generate gates -> add evidence -> record failed validation -> create action -> mark fixed -> rerun/record pass -> draft release notes -> final decision -> export audit.
- Accessibility checks for navigation, forms, cards, board movement, dialogs, tables, focus states, and color contrast.
- Browser console/network/runtime inspection with screenshots/traces for main flows.

Final implementation report must separate verified behavior from unverified assumptions, list exact commands run, link saved evidence, identify remaining limitations, and state whether the release candidate is go, no-go, wait, investigate, or limited release.
