# Evidence-to-Decision Workspace Implementation Specification

Build **Evidence-to-Decision Workspace**: a local-first web application where messy sources become traceable claims, evidence, contradictions, explanations, decisions, actions, alerts, and reusable outputs. The product is an evidence command center for:

- personal notes and transcripts;
- saved articles, newsletters, and links;
- research papers, documentation, and official pages;
- GitHub issues, releases, and technical discussions;
- market, product, competitor, and community signals;
- manually added observations and conversations.

The workspace supports decisions across:

- product and research priorities;
- prompt-language and agent-workflow design choices;
- investment or business opportunities that need evidence discipline;
- personal project commitments;
- risks, warnings, and wait-versus-act judgments.

The specification below is the source of truth for implementation. Use concrete requirements, safe assumptions, and testable acceptance criteria. The first build MUST be useful as a single-user local workspace without a hosted multi-tenant backend.

## 1. Product Intent

### User job

The user needs to collect messy information from many sources, normalize it into explicit claims and evidence, compare competing interpretations, and make revisitable decisions with clear provenance. The app must prevent “confident but untraceable” conclusions by keeping raw sources, extracted facts, claims, evidence ratings, contradictions, hypotheses, decision gates, actions, and outputs connected.

### Core value

The app turns source chaos into a durable evidence-and-decision graph:

1. intake sources and attachments;
2. extract source facts without inventing unsupported content;
3. form claims and hypotheses;
4. link evidence for and against each claim;
5. surface contradictions, gaps, and uncertainty;
6. compare options and forecasts;
7. decide to act, wait, investigate, delegate, monitor, or revisit;
8. generate reusable outputs that cite their inputs;
9. preserve a local audit trail.

### First-build scope

MUST include:

- local workspace creation and diagnostics;
- SQLite-backed source, claim, evidence, decision, action, output, notification, and activity storage;
- source intake for text, URL, file metadata, manual observation, transcript/note, and saved article references;
- attachment handling with previews for supported types;
- source normalization into facts, inferred structure, decisions, risks, questions, and confidence notes;
- evidence graph with claims, evidence ratings, contradictions, hypotheses, and provenance;
- ACH-style hypothesis comparison;
- decision graph with option comparison, forecast uncertainty, values tradeoffs, decision gates, and action planning;
- board/card UI for source review, evidence review, decision review, actions, alerts, and outputs;
- dashboards, search, filters, typed output surfaces, notifications, activity stream, REST API, and live events;
- local-first privacy controls and explicit external AI/network consent;
- validation through a first successful user session.

MAY defer:

- hosted collaboration;
- billing and subscriptions;
- organization onboarding;
- push notifications outside local browser support;
- deep file parsers for all rich document types;
- desktop packaging, if the local Node app flow is complete.

Out of scope for the first build:

- multi-tenant SaaS architecture;
- serverless deployment with ephemeral/shared filesystem as the default;
- silent cloud sync;
- external writes to repositories, CRMs, brokers, or productivity systems without explicit future integration design.

## 2. Technology and Architecture

### Required stack

- Next.js 14+ with App Router.
- TypeScript 5+ strict mode; no `any`.
- Tailwind CSS with design tokens in `tailwind.config.ts`.
- React Server Components by default.
- Zustand only for local client UI state that cannot live in URL/search params/server data.
- react-hook-form with zod schemas shared by UI, Server Actions, and API handlers.
- Node.js runtime only for routes/actions touching SQLite.
- Prisma with SQLite provider.
- SQLite 3 in WAL mode.
- Vitest with happy-dom for unit/component tests.
- Vitest using temporary SQLite files for API/storage tests.
- Playwright for critical local user flows.
- Minimum 80% line coverage for application logic.

### Local-first process model

- One local app server owns SQLite writes.
- `DATABASE_URL` MUST point to a local SQLite file under the active workspace directory or OS user-data directory.
- The app MUST expose the configured data directory and active workspace path in settings and diagnostics.
- Browser storage MAY cache disposable UI state, but SQLite is the canonical durable store.
- Existing local data MUST remain readable when external AI, search, or integration calls fail.

### Recommended project structure

- `app/`: App Router routes, layouts, Server Components, route handlers.
- `components/`: shared UI primitives, cards, boards, surfaces, charts, forms.
- `features/`: domain feature modules:
  - `sources`;
  - `attachments`;
  - `facts`;
  - `claims`;
  - `evidence`;
  - `hypotheses`;
  - `decisions`;
  - `actions`;
  - `outputs`;
  - `notifications`;
  - `activity`;
  - `workspace`;
  - `ai`;
- `lib/db/`: Prisma client, migrations helpers, transaction helpers, backup/repair.
- `lib/domain/`: zod schemas, state machines, scoring, ACH, decision gates, evidence grading.
- `lib/files/`: attachment and artifact file storage.
- `lib/events/`: activity event append/replay and live broadcast.
- `lib/api/`: REST envelope, RFC 7807 errors, idempotency.
- `lib/ai/`: provider abstraction, redaction, prompt builders, cost tracking.
- `tests/`: unit, integration, fixtures, Playwright specs.

### Data flow

1. User creates or selects a local workspace.
2. App validates workspace read/write permissions, schema version, migrations, and attachment directory.
3. User imports or creates sources.
4. Source normalization extracts facts, inferred relationships, decisions, tasks, risks, blockers, questions, and confidence notes.
5. User or AI turns facts into claims and links evidence.
6. Evidence is graded for relevance, specificity, freshness, independence, contradictions, and decision impact.
7. Contradictions and hypotheses are evaluated using ACH.
8. Decisions compare options, uncertainties, values, gates, and action plans.
9. Outputs render typed surfaces such as Markdown briefs, tables, gate summaries, ACH matrices, action plans, and reports.
10. Activity events record every material change.
11. Notifications and dashboards surface stale evidence, open questions, contradictions, due reviews, and triggered alerts.

## 3. Domain Model

### Core entities

Use CUID or UUID stable identifiers for all durable entities. Every durable table MUST include:

- `id`;
- `createdAt`;
- `updatedAt`;
- `deletedAt` where recovery/archive is useful;
- optimistic concurrency via `version` or equivalent for records that humans and AI can both update.

#### Workspace

Represents the active local evidence workspace.

Fields:

- `id`;
- `name`;
- `workspacePath`;
- `dataDir`;
- `schemaVersion`;
- `appVersion`;
- `settingsJson`;
- `aiPolicyJson`;
- `createdAt`;
- `updatedAt`.

Behavior:

- One default workspace exists after first run.
- User can create or choose another workspace directory.
- Settings show active path, database path, attachment directory, backup directory, schema version, app version, and health status.

#### Source

A raw or referenced information unit.

Fields:

- `id`;
- `workspaceId`;
- `sourceType`: `note`, `transcript`, `article`, `newsletter`, `link`, `paper`, `documentation`, `official_page`, `github_issue`, `release`, `technical_discussion`, `market_signal`, `product_signal`, `competitor_signal`, `community_signal`, `manual_observation`, `conversation`, `other`;
- `title`;
- `summary`;
- `rawText`;
- `url`;
- `author`;
- `publisher`;
- `publishedAt`;
- `capturedAt`;
- `sourceDateConfidence`: `low`, `medium`, `high`;
- `freshnessRequirement`;
- `credibilityNotes`;
- `ingestStatus`: `draft`, `queued`, `processing`, `normalized`, `failed`, `archived`;
- `provenanceJson`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Rules:

- Preserve raw wording where nuance, emotion, stakeholder intent, or exact phrasing matters.
- Do not convert fragments into false certainty.
- Source snippets and crawled text must be distinguished if web discovery is used.
- URLs, titles, dates, quotes, and source names MUST NOT be fabricated.

#### Attachment

Supporting material attached to a source, claim, decision, action, output, or activity event.

Fields:

- `id`;
- `workspaceId`;
- `hostType`;
- `hostId`;
- `type`: `file`, `url`, `text`, `image`, `table`, `artifact`, `reference`, `related_entity`, `other`;
- `title`;
- `source`: `upload`, `generated`, `external_link`, `integration`, `clipboard`, `system`;
- `contentRef`;
- `mimeType`;
- `format`;
- `sizeBytes`;
- `checksum`;
- `relativePath`;
- `createdBy`;
- `permissionsJson`;
- `provenanceJson`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Rules:

- Store large files under the data directory, not as large SQLite blobs by default.
- Store metadata, content hash, MIME type, size, origin, and relative path in SQLite.
- Use checksums to detect duplicates and corrupted files.
- Attachment-derived summaries, extracted text, thumbnails, embeddings, and AI outputs are traceable artifacts.
- Sensitive attachments are never silently sent to external AI.

#### NormalizationRun

Records a source normalization pass.

Fields:

- `id`;
- `workspaceId`;
- `sourceId`;
- `status`: `queued`, `running`, `complete`, `failed`, `superseded`;
- `method`;
- `modelProvider`;
- `modelName`;
- `inputRefsJson`;
- `outputJson`;
- `errorJson`;
- `startedAt`;
- `completedAt`;
- `createdAt`;
- `updatedAt`.

Output structure MUST include:

- source facts;
- inferred structure;
- decisions present in the source;
- action candidates;
- risks and blockers;
- open questions;
- confidence notes;
- duplicates;
- contradictions;
- ambiguities;
- stale items;
- named entities, owners, dates, assumptions, and provenance references when present.

#### Fact

An explicit statement or cautiously inferred unit extracted from a source.

Fields:

- `id`;
- `workspaceId`;
- `sourceId`;
- `normalizationRunId`;
- `text`;
- `factType`: `explicit_statement`, `inference`, `quote`, `metric`, `date`, `owner`, `commitment`, `risk`, `question`, `assumption`, `observation`;
- `rawQuote`;
- `locationRef`;
- `confidence`: `low`, `medium`, `high`;
- `isStale`;
- `provenanceJson`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Rules:

- Explicit statements and inferences must be visibly separated.
- Low-confidence interpretations must be marked.
- Absence of evidence may be represented only when the missing evidence should reasonably exist and be observable.

#### Claim

A proposition that can be supported, challenged, qualified, or used in a decision.

Fields:

- `id`;
- `workspaceId`;
- `claimText`;
- `claimType`: `descriptive`, `causal`, `forecast`, `comparative`, `normative`, `decision_relevant`, `risk`, `opportunity`, `constraint`;
- `status`: `draft`, `active`, `contested`, `accepted`, `rejected`, `stale`, `archived`;
- `scope`;
- `assumptionsJson`;
- `confidence`: `low`, `medium`, `high`;
- `evidenceGrade`: `strong`, `adequate`, `weak`, `insufficient`;
- `mainGap`;
- `decisionImpact`: `act`, `wait`, `investigate`, `delegate`, `monitor`, `revisit`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

#### EvidenceLink

Connects facts/sources/attachments to claims, hypotheses, options, or decisions.

Fields:

- `id`;
- `workspaceId`;
- `targetType`;
- `targetId`;
- `sourceId`;
- `factId`;
- `attachmentId`;
- `relationship`: `supports`, `challenges`, `qualifies`, `contradicts`, `context`, `source_for`, `missing_expected`;
- `relevance`: `high`, `medium`, `low`;
- `specificity`: `high`, `medium`, `low`;
- `freshness`: `high`, `medium`, `low`;
- `independence`: `high`, `medium`, `low`;
- `contradictionHandling`: `surfaced`, `explained`, `unresolved`, `ignored`;
- `reliability`: `high`, `medium`, `low`;
- `diagnosticValue`: `high`, `medium`, `low`;
- `notes`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Rules:

- Evidence grade is based on available evidence, not plausibility of the conclusion.
- Contradictory evidence must be surfaced instead of smoothed away.
- Same-source syndicated or mirrored evidence must not be counted as independent.
- Evidence must preserve source title, URL, date when available, and whether it came from raw source, snippet, crawled text, user note, or generated artifact.

#### Contradiction

A conflict, tension, or incompatibility between claims, facts, sources, hypotheses, or decisions.

Fields:

- `id`;
- `workspaceId`;
- `title`;
- `description`;
- `entityAType`;
- `entityAId`;
- `entityBType`;
- `entityBId`;
- `severity`: `low`, `medium`, `high`;
- `status`: `open`, `explained`, `resolved`, `accepted_uncertainty`, `archived`;
- `resolutionNotes`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

#### HypothesisSet and Hypothesis

Support ACH analysis.

HypothesisSet fields:

- `id`;
- `workspaceId`;
- `analyticQuestion`;
- `status`: `draft`, `active`, `ranked`, `stale`, `archived`;
- `assumptionsJson`;
- `biasNotes`;
- `uncertaintyNotes`;
- `nextEvidenceQuestionsJson`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Hypothesis fields:

- `id`;
- `hypothesisSetId`;
- `label`;
- `description`;
- `rank`;
- `leastInconsistentScore`;
- `status`: `active`, `downgraded`, `eliminated`, `needs_revision`;
- `strongestDisconfirmingEvidenceJson`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

#### ACHMatrixCell

Represents one evidence item’s relationship to one hypothesis.

Fields:

- `id`;
- `hypothesisSetId`;
- `hypothesisId`;
- `evidenceLinkId`;
- `rating`: `C`, `I`, `N`, `M`;
- `reliability`: `high`, `medium`, `low`;
- `diagnosticValue`: `high`, `medium`, `low`;
- `notes`;
- `createdAt`;
- `updatedAt`.

ACH rules:

- Compare hypotheses in parallel.
- Prioritize disconfirming evidence over confirming evidence.
- Weight diagnostic value more heavily than raw evidence count.
- Revise the hypothesis set if options are incomplete, overlapping, or poorly framed.
- Rank hypotheses from least inconsistent to most inconsistent.
- If no hypothesis fits, introduce a better alternative.

#### Decision

A choice point, gate, recommendation, or revisitable judgment.

Fields:

- `id`;
- `workspaceId`;
- `title`;
- `decisionDomain`;
- `decisionShape`: `reversible`, `irreversible`, `adversarial`, `forecast_heavy`, `portfolio`, `values_heavy`, `option_preserving`, `routine`, `mixed`;
- `status`: `draft`, `investigating`, `ready_for_gate`, `decided`, `waiting`, `monitoring`, `revisit_due`, `archived`;
- `contextStatus`: `sufficient`, `limited`, `insufficient`;
- `chosenMethod`;
- `decisiveUncertaintiesJson`;
- `recommendedNextMove`;
- `reviewCadence`;
- `reversalTriggersJson`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Rules:

- Classify decision shape before recommending a method.
- Preserve optionality when information value is high and delay is cheap.
- Recommend commitment when delay is costly and uncertainty cannot be resolved.
- Make the next action proportional to stakes and reversibility.
- If context is insufficient, avoid confident action recommendations and identify the smallest next evidence step.

#### Option

A possible action, strategy, investment, project, commitment, delegation, deferral, probe, hybrid, or no-action baseline.

Fields:

- `id`;
- `decisionId`;
- `label`;
- `description`;
- `optionType`: `act`, `wait`, `investigate`, `delegate`, `monitor`, `revisit`, `no_action`, `hybrid`;
- `bestIf`;
- `avoidIf`;
- `sacrifices`;
- `rank`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

#### DecisionCriterion

Fields:

- `id`;
- `decisionId`;
- `name`;
- `threshold`;
- `currentRead`;
- `gateStatus`: `pass`, `fail`, `unknown`;
- `confidence`: `low`, `medium`, `high`;
- `whyItMatters`;
- `createdAt`;
- `updatedAt`.

#### ForecastScenario

Fields:

- `id`;
- `decisionId`;
- `scenarioType`: `base`, `upside`, `downside`, `custom`;
- `description`;
- `probabilityRange`;
- `triggersJson`;
- `indicatorsJson`;
- `robustAction`;
- `contingentAction`;
- `createdAt`;
- `updatedAt`.

Forecast rules:

- Separate known facts, assumptions, forecasts, and preferences.
- Use ranges/scenarios instead of false precision.
- Track leading indicators, signposts, base rates when relevant, and dependency between uncertainties.
- Compare robust choices against best-case optimized choices.

#### ValuesTradeoff

Fields:

- `id`;
- `decisionId`;
- `valueName`;
- `optionFavored`;
- `risk`;
- `acceptableCompromise`;
- `boundaryCondition`;
- `regretNotes`;
- `createdAt`;
- `updatedAt`.

Values rules:

- Name values or principles in tension.
- Do not collapse all tradeoffs into one score.
- State what the chosen option sacrifices.
- Include reversible experiments or conversations when useful before commitment.

#### ActionItem

Fields:

- `id`;
- `workspaceId`;
- `decisionId`;
- `sourceId`;
- `claimId`;
- `title`;
- `description`;
- `actionType`: `act`, `investigate`, `delegate`, `monitor`, `revisit`, `escalate`, `validate`, `communicate`;
- `status`: `candidate`, `needs_confirmation`, `committed`, `in_progress`, `blocked`, `done`, `cancelled`;
- `owner`;
- `priority`: `low`, `medium`, `high`, `urgent`;
- `timing`;
- `dueAt`;
- `dependencyJson`;
- `definitionOfDone`;
- `validationMethod`;
- `reviewPoint`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Rules:

- Separate committed actions from suggested actions.
- Flag actions needing confirmation before execution.
- Keep the first next step small enough to start immediately.
- Include validation, escalation, and review points for high-risk or blocked work.

#### OutputSurface

Typed rendered output owned by a source, claim, decision, run, or workspace.

Fields:

- `id`;
- `workspaceId`;
- `hostType`;
- `hostId`;
- `type`: `text`, `program`, `table`, `diff`, `image`, `chart`, `status`, `log`, `terminal`, `form`, `canvas`, `file`, `custom`;
- `title`;
- `contentJson`;
- `contentRef`;
- `schemaVersion`;
- `status`: `draft`, `streaming`, `complete`, `failed`, `stale`, `superseded`, `approved`;
- `source`: `human`, `agent`, `integration`, `import`, `system`;
- `lineageJson`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Required surface types for first build:

- normalized source summary;
- evidence table;
- contradiction report;
- ACH matrix;
- claim explanation;
- decision gate;
- comparative alternatives table;
- forecast scenario table;
- values tradeoff table;
- action plan;
- exportable Markdown report.

#### NotificationRule and Notification

NotificationRule fields:

- `id`;
- `workspaceId`;
- `name`;
- `conditionJson`;
- `thresholdJson`;
- `operator`: `>`, `>=`, `<`, `<=`, `==`, `between`;
- `channelJson`;
- `cooldownSeconds`;
- `lastFiredAt`;
- `enabled`;
- `createdAt`;
- `updatedAt`;
- `deletedAt`.

Notification fields:

- `id`;
- `workspaceId`;
- `ruleId`;
- `type`;
- `severity`: `info`, `warning`, `critical`;
- `title`;
- `body`;
- `targetType`;
- `targetId`;
- `status`: `unread`, `read`, `dismissed`, `resolved`;
- `createdAt`;
- `updatedAt`.

Required alert examples adapted to this product:

- evidence grade drops to weak/insufficient for an active decision;
- contradiction remains unresolved past a due date;
- review cadence is due;
- source is stale for a forecast-heavy decision;
- decision gate changes from go to wait/investigate/no-go;
- action item becomes blocked or overdue;
- external AI failed while producing a required surface.

#### ActivityEvent

Fields:

- `id`;
- `workspaceId`;
- `type`;
- `actorType`: `human`, `agent`, `integration`, `system`, `automation`;
- `actorId`;
- `targetType`;
- `targetId`;
- `timestamp`;
- `summary`;
- `payloadJson`;
- `visibility`: `private`, `internal`, `redacted`;
- `correlationId`;
- `traceId`;
- `createdAt`.

Rules:

- Persist audit events before broadcasting live updates.
- Event insertion and visible state update must happen in the same transaction when the event explains the state change.
- Avoid logging secrets, API keys, refresh tokens, or full sensitive payloads.
- Record enough lineage to connect prompts, tool calls, artifacts, questions, answers, and final outputs.

#### AIRun

Fields:

- `id`;
- `workspaceId`;
- `purpose`: `normalize_source`, `extract_claims`, `grade_evidence`, `detect_contradictions`, `run_ach`, `draft_decision`, `generate_output`, `answer_query`;
- `provider`;
- `model`;
- `temperature`;
- `maxTokens`;
- `inputRefsJson`;
- `redactionSummaryJson`;
- `outputRefsJson`;
- `tokenUsageJson`;
- `estimatedCost`;
- `status`: `queued`, `running`, `complete`, `failed`, `cancelled`;
- `errorJson`;
- `createdAt`;
- `updatedAt`.

Rules:

- All external AI input must be sanitized and previewable.
- Include `data_policy: no_training` in provider calls where supported.
- Log token usage and estimated cost per request.
- Retry 429/500/503 with exponential backoff of 1s, 2s, 4s, max 3 retries.
- If AI is unavailable, show an “AI unavailable” badge and offer rule-based/manual fallback.

## 4. SQLite Schema Requirements

Use Prisma with SQLite provider. Map tables and columns to clear snake_case names where practical while keeping TypeScript model fields idiomatic.

Minimum tables:

- `workspaces`;
- `sources`;
- `attachments`;
- `normalization_runs`;
- `facts`;
- `claims`;
- `evidence_links`;
- `contradictions`;
- `hypothesis_sets`;
- `hypotheses`;
- `ach_matrix_cells`;
- `decisions`;
- `options`;
- `decision_criteria`;
- `forecast_scenarios`;
- `values_tradeoffs`;
- `action_items`;
- `output_surfaces`;
- `notification_rules`;
- `notifications`;
- `activity_events`;
- `ai_runs`;
- `idempotency_keys`;
- `user_preferences`;
- `saved_views`;
- `workspace_exports`;
- `schema_migrations_audit`.

Indexes MUST cover:

- workspace-scoped queries on every entity;
- source type/status/date filters;
- claim status/confidence/evidence grade;
- evidence target lookups;
- contradiction status/severity;
- decision status/domain/review due;
- action status/owner/due date;
- output host lookups;
- notification unread/status;
- activity event target/timestamp/correlation;
- idempotency key lookup;
- full-text or LIKE-backed search for source title/text, claim text, decision title, and output titles.

Storage behavior:

- SQLite file, attachments, generated artifacts, backups, repair logs, and export manifests live under the active data directory.
- Use WAL mode.
- Run pending migrations at startup after creating a backup when existing data is present.
- Refuse to start on unsupported future schema versions.
- Use explicit transactions for multi-entity updates.
- Backup before destructive migrations or repair attempts unless the database is unreadable.
- Exports include SQLite database, referenced files, schema version, app version, and manifest checksums.
- Repair tools report what changed and preserve the original damaged database when possible.

## 5. Source Intake and Normalization Workflow

### Intake methods

MUST support:

- paste text;
- create manual note/observation;
- add URL reference;
- upload or attach file metadata and stored file;
- import transcript text;
- save article/newsletter/link metadata;
- add GitHub issue/release/discussion reference manually.

MAY later support automated crawling, browser extensions, inbox ingestion, RSS, GitHub API, or PDF extraction.

### Intake UI

Each new source card shows:

- title;
- source family/type;
- provenance summary;
- captured date and optional published date;
- processing status;
- evidence count;
- linked claims/decisions;
- open contradictions or questions;
- primary actions: normalize, review facts, link to decision, archive.

Empty state:

- explain what sources are;
- offer paste text, add URL, upload file, and create manual observation;
- include a sample “first session” path.

Error states:

- invalid URL;
- unsupported file preview;
- failed normalization;
- missing workspace write permissions;
- duplicate source warning;
- external fetch unavailable.

### Normalization obligations

For each source, the app MUST:

- preserve source fidelity;
- distinguish explicit statements from inferences;
- identify duplicates, contradictions, ambiguities, missing context, and stale items;
- extract named entities, owners, dates, decisions, tasks, risks, blockers, questions, evidence, and assumptions when present;
- keep raw wording when nuance matters;
- mark low-confidence interpretations visibly;
- avoid inventing facts, commitments, dates, owners, or causal links.

The normalized working set MUST display:

| Section | Purpose |
| --- | --- |
| Source facts | What the input explicitly says. |
| Inferred structure | Relationships or categories inferred from the input. |
| Decisions | Choices already made or still needed. |
| Action candidates | Potential tasks, follow-ups, or commitments. |
| Risks and blockers | Things that could prevent progress. |
| Open questions | Missing inputs or ambiguities that matter. |
| Confidence notes | Places where interpretation is uncertain. |

## 6. Evidence Graph Workflow

### Claim creation

Claims can be:

- manually created;
- extracted from facts;
- proposed by AI;
- derived from a decision option;
- imported from an output surface.

A claim cannot be marked accepted without at least one evidence review or explicit user override recorded in activity history.

### Evidence grading

Every active claim SHOULD show:

| Criterion | Rating | Required interpretation |
| --- | --- | --- |
| Relevance | high/medium/low | Directly supports or challenges the claim vs adjacent/generic. |
| Specificity | high/medium/low | Concrete facts, numbers, examples, observations vs vague assertions. |
| Freshness | high/medium/low | Current enough for the domain vs stale/undated. |
| Independence | high/medium/low | Multiple independent sources/methods vs repeated same family. |
| Contradictions | high/medium/low | Tensions surfaced and explained vs ignored. |

The claim summary MUST include:

- evidence grade: `strong`, `adequate`, `weak`, or `insufficient`;
- main gap;
- decision impact: `act`, `wait`, `investigate`, `delegate`, `monitor`, or `revisit`.

### Context sufficiency

Before action-oriented decisions or recommendations, classify context as:

- `sufficient`: inputs support the conclusion;
- `limited`: the app can help, but conclusions need caveats;
- `insufficient`: avoid confident recommendations and show what is needed.

When context is limited or insufficient, show:

| Field | Content |
| --- | --- |
| Context status | sufficient / limited / insufficient |
| Missing context | highest-impact missing inputs |
| Impact | how gaps change confidence or permissible output |
| Safe output | what can still be said responsibly |
| Next evidence | smallest evidence/input that would improve the answer |

### News and research quality

When a source or decision uses news/research-like material, the app MUST:

- favor primary/official, recent, expert/practitioner, technical/reference, local/domain-specific, skeptical/contrary, and source-rich roundup materials when available;
- distinguish facts, reported claims, analysis, estimates, and speculation;
- surface contradictory evidence;
- explain freshness needs;
- avoid fabricated citations, publication dates, URLs, quotes, or source names;
- show highest-value next searches/documents when evidence is thin.

For deep discovery features, design the workflow around query families:

1. recent/breaking;
2. primary/official;
3. expert/practitioner;
4. local/domain-specific;
5. skeptical/contrary;
6. roundup/index.

Crawl-depth discipline:

- depth 1: selected search results;
- depth 2: selected links from first-level crawls;
- depth 3: only when it materially improves evidence quality.

The goal is deeper evidence, not more pages.

## 7. ACH and Explainability

### ACH workflow

For each hypothesis set, the app MUST support the full ACH workflow:

1. define the analytic question in one sentence;
2. construct 3–7 mutually distinguishable hypotheses when the situation supports it;
3. break available information into discrete evidence items or indicators;
4. rate each evidence item against each hypothesis:
   - `C` = consistent;
   - `I` = inconsistent;
   - `N` = neutral/non-diagnostic;
   - `M` = missing but expected;
5. mark reliability and diagnostic value as high/medium/low;
6. highlight evidence that most strongly disconfirms each hypothesis;
7. eliminate or downgrade hypotheses materially inconsistent with strongest evidence;
8. rank remaining hypotheses from least inconsistent to most inconsistent;
9. state uncertainty, assumptions, possible biases, and data-quality limits;
10. identify next evidence questions or collection actions that would most reduce uncertainty or flip the ranking.

Guardrails:

- do not choose a hypothesis because it is intuitive, familiar, or convenient;
- do not treat assumptions, rumors, or unverified reports as confirmed facts;
- do not rely on evidence volume alone;
- do not hide deception, selection bias, measurement error, or reporting lag;
- do not force certainty when evidence is sparse, ambiguous, or conflicting.

### Explainability surface

Every generated conclusion, recommendation, decision gate, or report MUST be able to show:

| Step | Claim or inference | Evidence or basis | Confidence |
| --- | --- | --- | --- |
| 1 | claim/inference | source, calculation, assumption, or observation | low/medium/high |

Also include:

- key assumptions;
- checks performed;
- limits;
- simplest plain-language explanation.

## 8. Decision Graph Workflow

### Strategy selection

Each decision starts by classifying its shape:

- reversible;
- irreversible;
- adversarial;
- forecast-heavy;
- portfolio;
- values-heavy;
- option-preserving;
- routine;
- mixed.

Decision surface MUST include:

1. decision shape with reasons;
2. chosen method and why it fits;
3. decisive uncertainties;
4. option set including choices, hybrids, deferrals, probes, and no-action baseline;
5. reversal or escalation triggers;
6. recommended next move with action, evidence to gather, and review point.

### Comparative alternatives

For option comparisons, start with:

- `Leading option: <option>`;
- `Runner-up: <option>`;
- `Decisive criterion: <criterion>`;
- `Confidence: low | medium | high`.

Then show:

| Criterion | Option A | Option B | Option C | Winner | Why it matters |
| --- | --- | --- | --- | --- | --- |

End with:

- best-if conditions;
- avoid-if conditions;
- ranking trigger.

### Decision gate

Each gate MUST define criteria and thresholds before classification.

Display:

- `Gate: go | no-go | wait | investigate`;
- `Reason: <one-sentence rationale>`;
- `Confidence: low | medium | high`.

Then show:

| Criterion | Threshold | Current read | Gate status | Confidence |
| --- | --- | --- | --- | --- |

End with:

- blockers;
- next evidence;
- change trigger.

### Forecasting

Forecast-heavy decisions MUST include:

1. forecast variables;
2. base/upside/downside scenarios with triggers;
3. indicators to watch;
4. robust action;
5. contingent action;
6. review cadence.

### Values tradeoffs

Values-heavy decisions MUST include:

1. values map;
2. tension table with value, option favored, risk, and acceptable compromise;
3. regret test;
4. boundary conditions;
5. experiment or conversation where useful;
6. recommendation with sacrifice.

### Action planning

Each decision can produce an action plan with:

1. immediate next step;
2. action table: action, owner, priority, timing, dependency, definition of done;
3. decision list: decision needed, owner, deadline, input needed;
4. risk register: risk, impact, mitigation, trigger;
5. open questions;
6. review cadence.

## 9. User Interface

### Main navigation

Required top-level sections:

- Inbox / Sources;
- Evidence Graph;
- Claims;
- Hypotheses;
- Decisions;
- Actions;
- Outputs;
- Dashboard;
- Activity;
- Settings.

### Cards

Use cards as compact, scannable units for sources, claims, contradictions, decisions, actions, notifications, and outputs.

Each card MUST define:

- stable id;
- semantic type;
- title;
- summary/body;
- badges for status, evidence grade, confidence, source type, risk, due/review state;
- metadata;
- primary and secondary actions;
- links to related records;
- UI state: selected, focused, expanded, disabled, loading, error, stale, unread.

Card requirements:

- clear visual hierarchy;
- responsive readability in narrow columns, grids, and detail panes;
- empty, loading, error, stale, and permission-limited states;
- pointer and keyboard access;
- visible focus;
- sufficient contrast;
- screen-reader labels for icon-only actions;
- unambiguous click, drag, context menu, selection, and inline edit behavior.

### Workflow boards

Required boards:

1. Source Review Board:
   - Inbox;
   - Needs Normalization;
   - Needs Fact Review;
   - Ready for Claims;
   - Archived.

2. Evidence Board:
   - Unlinked Facts;
   - Claims Needing Evidence;
   - Contested Claims;
   - Evidence Gaps;
   - Accepted/Ready.

3. Decision Board:
   - Draft;
   - Investigating;
   - Ready for Gate;
   - Decided;
   - Monitoring;
   - Revisit Due.

4. Action Board:
   - Candidate;
   - Needs Confirmation;
   - Committed;
   - In Progress;
   - Blocked;
   - Done.

Board behavior:

- stable column identifiers, display names, ordering, descriptions;
- accessible drag-and-drop with keyboard alternatives;
- allowed transitions and validation rules;
- visible reason when movement is not allowed;
- optimistic-update rollback;
- create, view, edit, duplicate, archive/delete, search, filter, sort, and bulk selection;
- saved views and filters;
- counts, overdue indicators, blocked indicators, evidence gap indicators, review due indicators;
- persisted board state across refreshes.

### Dashboards and visualizations

Dashboard layout:

- responsive grid: 1 column mobile, 2 tablet, 3–4 desktop;
- each widget is a card with title bar, content area, optional action menu;
- loading skeleton and error state with retry;
- drag-to-reorder and show/hide persisted to preferences.

Required widgets:

- Evidence Health: strong/adequate/weak/insufficient counts.
- Open Contradictions by severity.
- Decisions by status and domain.
- Review Due / Stale Evidence.
- Actions by status and due date.
- Source Intake over time.
- AI Runs and failures.
- Recent Activity.

Charts/tables:

- line chart for source/decision/action activity over time;
- bar chart for evidence grades by domain/source family;
- donut chart for decision statuses;
- sparklines for weekly trends;
- sortable/filterable/paginated data tables;
- row actions and bulk export;
- global date range picker with presets and custom range;
- accessible palettes, responsive resize, tooltips, dark/light mode, export as PNG.

### Typed output surfaces

Do not flatten all generated artifacts into one text area. Use purpose-built surfaces:

- Markdown report surface;
- evidence table surface;
- ACH matrix surface;
- decision gate surface;
- comparison table surface;
- forecast scenario surface;
- values tradeoff surface;
- action plan surface;
- log/status surface.

Surfaces support:

- copy;
- download/export;
- approve;
- comment;
- compare versions;
- pin/minimize/open detail;
- stale/failed explanations;
- lineage to inputs, prompts, tools, attachments, and agent steps.

## 10. Notifications and Activity

### Notifications

Required channels:

- in-app toast;
- persistent notification center.

Optional later:

- email digest;
- web push using Service Worker and VAPID keys.

Rules:

- Same alert rule must not fire more than once per evaluation period.
- Track last-fired timestamp and cooldown.
- Notification templates support variable substitution and locale-aware formatting.
- Notifications must link to the relevant source, claim, contradiction, decision, action, or output.

### Activity stream

Activity stream MUST:

- be append-oriented;
- support pagination and incremental loading;
- live-append new events;
- filter by event type, actor, severity, source, errors;
- distinguish human actions, agent actions, automation, errors, decisions, and output updates;
- show relative time for scanning and exact timestamp in detail;
- preserve chronological clarity after reconnect/replay;
- make important events linkable and copyable;
- support export and privacy behavior.

Record activity for:

- workspace creation;
- source intake;
- normalization;
- fact/claim/evidence edits;
- evidence grading;
- contradiction creation/resolution;
- ACH ranking;
- decision gate changes;
- action status changes;
- output generation/approval;
- notification firing;
- AI runs and failures;
- migrations, backup, restore, import, export, and repair.

## 11. REST API

Expose a local REST API under `/api/v1`.

### Standards

- Resources use plural nouns.
- Nesting limited to one level.
- Filtering, sorting, pagination use query params:
  - `?status=active&sort=-created_at&page=1&per_page=20`.
- Content-Type is `application/json`.
- Collections return `{"data": [...], "meta": {...}}`.
- Single resources return `{"data": ...}`.
- Empty collections return `{"data": [], "meta": {"total": 0, ...}}`.

### Errors

Use RFC 7807 Problem Details:

json
{
  "type": "https://local.evidence-workspace/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "field 'claimText' is required",
  "errors": [{"field": "claimText", "message": "is required"}]
}
Status codes:

- 400 bad input;
- 401 not authenticated, if local auth is enabled later;
- 403 forbidden;
- 404 not found;
- 409 conflict;
- 422 validation;
- 429 rate limit;
- 500 server error.

### Idempotency

- POST create endpoints accept `Idempotency-Key`.
- Same key within 24 hours returns the original response.
- GET, PUT, DELETE are idempotent.

### Required endpoints

Minimum:

- `GET /api/health`;
- `GET /api/v1/workspace`;
- `PUT /api/v1/workspace`;
- `GET /api/v1/sources`;
- `POST /api/v1/sources`;
- `GET /api/v1/sources/{id}`;
- `PUT /api/v1/sources/{id}`;
- `DELETE /api/v1/sources/{id}`;
- `POST /api/v1/sources/{id}/normalize`;
- `GET /api/v1/attachments`;
- `POST /api/v1/attachments`;
- `GET /api/v1/facts`;
- `POST /api/v1/facts`;
- `GET /api/v1/claims`;
- `POST /api/v1/claims`;
- `GET /api/v1/evidence-links`;
- `POST /api/v1/evidence-links`;
- `GET /api/v1/contradictions`;
- `POST /api/v1/contradictions`;
- `GET /api/v1/hypothesis-sets`;
- `POST /api/v1/hypothesis-sets`;
- `POST /api/v1/hypothesis-sets/{id}/rank`;
- `GET /api/v1/decisions`;
- `POST /api/v1/decisions`;
- `POST /api/v1/decisions/{id}/gate`;
- `GET /api/v1/actions`;
- `POST /api/v1/actions`;
- `GET /api/v1/output-surfaces`;
- `POST /api/v1/output-surfaces`;
- `GET /api/v1/notifications`;
- `POST /api/v1/notifications/{id}/read`;
- `GET /api/v1/activity-events`;
- `GET /api/v1/search`;
- `POST /api/v1/export`;
- `POST /api/v1/import`.

Health check returns:

- local store status;
- schema version;
- app version;
- workspace path;
- attachment directory status;
- WAL status;
- pending migrations;
- latest backup status.

## 12. Real-Time Events

Use WebSocket endpoint:

- `ws://host/ws` or `wss://host/ws` when TLS is present.

Message format:

json
{"type": "...", "payload": {}, "id": "uuid"}
Protocol:

- server sends `{"type": "ack", "id": "..."}` for client messages;
- heartbeat: server sends `{"type": "ping"}` every 30 seconds;
- client responds with `{"type": "pong"}` within 10 seconds;
- client reconnects with exponential backoff: 1s, 2s, 4s, 8s, max 30s;
- reconnect sends `{"type": "resume", "payload": {"last_event_id": "..."}}`;
- server replays missed events up to 1000 events or 5 minutes.

Required event types:

- `source.created`;
- `source.updated`;
- `source.normalized`;
- `claim.created`;
- `claim.updated`;
- `evidence.linked`;
- `contradiction.created`;
- `contradiction.resolved`;
- `hypothesis.ranked`;
- `decision.updated`;
- `decision.gate_changed`;
- `action.updated`;
- `output.created`;
- `output.updated`;
- `notification.created`;
- `activity.appended`;
- `ai_run.updated`;
- `workspace.health_changed`;
- `error`.

Presence is optional for first build. If implemented, use local session identity and broadcast:

json
{"type": "presence", "payload": {"user_id": "...", "status": "online|offline"}}
## 13. AI Automation

### Provider abstraction

Implement provider-agnostic interface supporting:

- OpenAI;
- Anthropic;
- local models.

Configuration per use case:

- provider;
- model name;
- temperature;
- max tokens;
- system prompt;
- redaction policy;
- external-send consent requirement.

### Required AI-assisted features

AI features MUST be optional and have manual fallback.

1. Source normalization:
   - extract facts, inferred structure, decisions, actions, risks, questions, confidence notes.
2. Claim extraction:
   - propose claims from facts and sources.
3. Evidence grading:
   - suggest ratings with cited basis.
4. Contradiction detection:
   - identify conflicting facts/claims/sources.
5. ACH drafting:
   - propose hypotheses and matrix entries for user review.
6. Decision drafting:
   - propose decision shape, options, gates, forecasts, values, and action plan.
7. Natural language query:
   - parse user question into structured local query, execute locally, then format answer.
8. Output generation:
   - create traceable reports and summaries from selected entities.

### Safety and privacy

- External network calls must be explicit in UI and configuration.
- Before sending local content to external AI/search/integration, show destination and purpose.
- Sanitize inputs and strip secrets/PII where possible.
- Never use private data for training where provider supports `data_policy: no_training`.
- Show exactly which sources/attachments/claims/decisions are included in AI context.
- Logs avoid secrets, API keys, refresh tokens, and full sensitive payloads unless diagnostic capture is explicitly enabled.
- If AI is unavailable, degrade gracefully with manual workflows and rule-based checks.

## 14. Search, Filters, and Saved Views

Search MUST cover:

- sources;
- facts;
- claims;
- decisions;
- actions;
- outputs;
- activity summaries.

Filters MUST include:

- source type;
- source date/captured date;
- evidence grade;
- confidence;
- contradiction severity/status;
- decision domain/status/shape;
- action owner/status/due date;
- output type/status;
- notification severity/status.

Saved views store:

- name;
- target surface;
- filters;
- sort;
- visible columns/widgets;
- date range;
- board layout preferences.

## 15. Privacy, Security, and Local Operations

### Local workspace operations

Startup MUST:

- validate workspace readability and writability;
- initialize missing store deterministically;
- run migrations when safe;
- create backup before migrating existing data;
- detect locked, corrupted, or too-new stores;
- show recoverable errors with backup, repair, or upgrade guidance.

Settings MUST expose:

- workspace path;
- SQLite path;
- attachments path;
- backup path;
- schema version;
- app version;
- external AI settings;
- export/import controls;
- diagnostic capture toggle.

### Backup, restore, export, import

- Backups are timestamped.
- Export includes database, files, schema version, app version, and manifest checksums.
- Import validates manifest, checksums, schema compatibility, and file references.
- Restore preserves current workspace backup before replacing.
- Repair preserves original damaged database when possible and reports changes.

### Failure handling

Must handle:

- failed migration;
- locked database;
- disk full;
- corrupted attachment;
- missing file;
- unsupported preview;
- failed AI request;
- invalid source URL;
- stale source;
- failed export/import;
- WebSocket disconnect;
- optimistic update conflict;
- idempotency replay;
- validation error.

Each error must provide:

- human-readable summary;
- technical detail in diagnostics where safe;
- recovery action;
- activity event when relevant.

## 16. Validation Plan

### First successful user session

A new user can:

1. start the local app;
2. create or accept the default local workspace;
3. see the active workspace path and healthy store status;
4. paste a messy note/transcript and add a URL reference;
5. normalize the source;
6. review extracted facts, questions, risks, and confidence notes;
7. create at least two claims from the source;
8. link evidence to each claim;
9. create one contradiction or evidence gap;
10. create a decision in a selected domain;
11. classify decision shape;
12. compare at least two options;
13. run a decision gate;
14. create one action item with owner, timing, dependency, and definition of done;
15. generate a traceable output report;
16. view activity history proving the sequence;
17. export the workspace;
18. restart the app and confirm persistence.

### State coverage

Test:

- empty workspace;
- active workspace with multiple sources/claims/decisions;
- failed normalization;
- weak/insufficient evidence;
- unresolved contradiction;
- stale source;
- blocked action;
- AI unavailable;
- database locked;
- missing attachment file;
- restore from backup;
- repeated use after restart.

### Evidence checklist

A credible demo must show:

- source card with provenance;
- normalized working set;
- claim with evidence grade;
- evidence table with ratings;
- contradiction surface;
- ACH matrix;
- decision gate;
- comparative alternatives table;
- action plan;
- dashboard widget changes;
- notification fired;
- activity event chain;
- exported workspace manifest.

### Automated tests

Unit tests:

- zod schemas;
- evidence grading logic;
- context sufficiency classification;
- ACH ranking helpers;
- decision gate logic;
- notification deduplication;
- REST envelope and errors;
- redaction helpers.

Storage/API tests:

- first-run initialization;
- migrations;
- transaction rollback;
- idempotency;
- backup/restore;
- export/import with attachments;
- locking and corrupted-file handling where practical;
- search/filter queries.

Component tests:

- cards;
- boards;
- tables;
- charts;
- output surfaces;
- notification center;
- activity stream;
- settings diagnostics.

Playwright E2E:

- first successful user session;
- restart persistence;
- source normalization to decision gate;
- action workflow board;
- export/import;
- AI unavailable fallback;
- error recovery for invalid input.

## 17. Acceptance Criteria

The first build is complete when:

- the app runs locally with Next.js, TypeScript strict mode, Prisma, and SQLite WAL;
- the active workspace is stored locally and visible in settings;
- startup initializes, migrates, backs up, and diagnoses the local store safely;
- sources can be created, edited, archived, normalized, and searched;
- attachments can be added, previewed where supported, removed, and traced;
- facts, claims, evidence links, contradictions, hypotheses, decisions, options, actions, outputs, notifications, and activity events persist in SQLite;
- evidence grades are calculated or reviewed using relevance, specificity, freshness, independence, and contradiction criteria;
- context sufficiency is visible for action-oriented decisions;
- ACH supports hypotheses, evidence matrix cells, disconfirming evidence, ranking, uncertainty, and next evidence questions;
- decisions support strategy classification, comparative alternatives, gates, forecasts, values tradeoffs, and action plans;
- boards and cards make sources, evidence, decisions, and actions inspectable and movable according to rules;
- dashboards summarize evidence health, contradictions, decisions, actions, sources, AI runs, and activity;
- output surfaces render typed artifacts with lineage;
- notifications deduplicate alerts and link to affected entities;
- activity history records material human, agent, system, and automation events;
- REST API follows `/api/v1`, JSON envelopes, pagination meta, RFC 7807 errors, and idempotency for creates;
- WebSocket events broadcast persisted changes with heartbeat and resume;
- AI features are optional, explicit, redacted, cost-tracked, retried, and manually recoverable;
- external calls never silently send local private content;
- export/import and backup/restore work with attachments;
- tests cover unit, storage/API, component, and E2E first-session flows;
- the product can demonstrate a messy source becoming a traceable claim, evidence review, contradiction, decision gate, action plan, output report, notification, and persisted audit trail.
