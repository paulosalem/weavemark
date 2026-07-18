# Fathom — Passive-Income Planning Dashboard Specification

Write an implementation-ready software specification for **Fathom**, a local-first web application for people pursuing financial independence through passive income and disciplined capital growth.

The specification MUST be concrete, testable, and build-ready for a programmer. Use RFC 2119 keywords precisely. Every requirement MUST be verifiable through unit, integration, API/storage, component, or end-to-end tests. Prefer named entities, schemas, algorithms, states, validation rules, error messages, and acceptance criteria over abstract product language.

## 1. Product promise and explicit non-goals

Fathom helps a user answer this monthly planning question:

> How much passive income can I use this month without compromising taxes, reserves, reinvestment, or my capital-growth policy?

Fathom is a planning and evidence tool. It MUST help users understand passive-income availability, capital-growth tradeoffs, safe-to-use amounts, confirmation status, forecast assumptions, and principal drawdown risk.

Fathom MUST NOT be described or implemented as:

- a brokerage, bank, trading terminal, or transaction execution system;
- a tax calculator or provider of individualized tax, legal, financial, or investment advice;
- a generic household-budget app;
- a tool that guarantees yield, payment timing, asset value, tax treatment, capital growth, or financial independence;
- a system that requests brokerage credentials or executes financial transactions.

Outputs MUST be labelled as planning support, not individualized financial, tax, legal, or investment advice.

## 2. Technical stack and runtime boundaries

The implementation MUST use:

- **Framework:** Next.js 14+ with App Router.
- **Language:** TypeScript 5+ with strict mode and no `any`.
- **Styling:** Tailwind CSS with design tokens in `tailwind.config.ts`.
- **State:** React Server Components by default; Zustand MAY be used for local UI state.
- **Forms:** react-hook-form with zod validation schemas shared across UI, Server Actions, and API handlers.
- **Data fetching:** Server Actions for mutations and `fetch` in Server Components for reads.
- **Runtime:** Node.js runtime only. Routes and actions that touch SQLite MUST NOT use Edge runtime.
- **ORM:** Prisma with SQLite provider.
- **Validation:** zod schemas shared between client and server.
- **Configuration:** environment variables validated at startup through `env.mjs` using zod.
- **Health check:** `GET /api/health` MUST return local store status, schema version, app version, writable/readable status, and migration state.

The default target MUST be a local Node.js process, self-hosted single-user service, or optional Electron/Tauri wrapper. Serverless deployments whose filesystem is ephemeral or shared across users MUST NOT be the default target.

## 3. Local-first architecture and workspace model

Fathom MUST be useful without a hosted multi-tenant backend. The local machine is the source of truth. Browser `localStorage`, IndexedDB, memory, and cache files MAY improve UX, but they MUST NOT be canonical storage for financial planning data.

The app MUST define one default local workspace and allow the user to choose or create a different workspace directory. Durable data, imported statement files, derived artifacts, backups, repair logs, and exports MUST live under the workspace directory or an OS user-data directory. The active workspace path MUST be visible in settings and diagnostics.

`DATABASE_URL` MUST point to a local SQLite file, normally under the workspace or OS user-data directory. The development default SHOULD be easy to inspect, such as `.local-data/app.sqlite`; packaged local apps SHOULD use the OS user-data directory.

The app MUST work offline for entry, review, forecasting, export, historical inspection, and local dashboard use. Optional backup/sync MAY exist, but backup/sync MUST NOT be required for the core workflow. External network calls MUST be explicit in the UI and configuration, and the app MUST continue to load and display existing local data when external services fail.

Before sending any local content to an external AI, web, backup, sync, or integration service, the UI MUST show the destination, purpose, data categories, and user-controlled confirmation. Logs MUST avoid secrets, API keys, refresh tokens, brokerage credentials, full statement payloads, and sensitive financial details unless the user explicitly enables diagnostic capture.

## 4. SQLite persistence and migrations

SQLite is the authoritative store for sources, income events, confirmations, assumptions, scenario versions, policy changes, review decisions, notifications, imports, corrections, and audit trails.

SQLite MUST run in WAL mode. Prisma Migrate MUST manage deterministic versioned migrations. On startup, the app MUST:

1. validate that the workspace is readable and writable;
2. initialize a missing store deterministically;
3. detect current schema version;
4. create a timestamped backup before running pending migrations when existing data is present;
5. refuse to start on an unsupported future schema version instead of silently rewriting the database;
6. show recoverable guidance for locked, corrupted, too-new, unreadable, or disk-full stores.

Every durable table MUST have:

- a stable primary key;
- `createdAt DateTime @default(now())`;
- `updatedAt DateTime @updatedAt`;
- `deletedAt DateTime?` for recoverable entities unless the table is append-only audit/event history;
- clear deletion, archival, or retention behavior;
- indexes for lookup, timeline ordering, dependency recalculation, event replay, filtering, and search.

Prisma schema names SHOULD use camelCase mapped to snake_case table and column names where practical. All monetary values MUST use integer cents or the smallest currency unit; floats MUST NOT be used for money. All timestamps MUST be UTC ISO 8601 with timezone offset. Multi-entity updates MUST use explicit SQLite transactions. Event insertion and visible state updates MUST be persisted in the same transaction when the event explains the state change.

Large imported statement files and generated artifacts SHOULD be stored as files under the data directory, not as large database blobs by default. SQLite MUST store metadata, content hash, MIME type, byte size, origin, and relative file path. Content hashes MUST be used to detect duplicate attachments and corrupted files.

Exports MUST include the SQLite database, referenced files, schema version, app version, and manifest checksums. Restore and repair tools MUST report what changed and preserve the original damaged database when possible.

## 5. Financial data model and calculation provenance

Define explicit relational models for at least the following durable entities. Each model MUST specify field name, type, nullability, uniqueness, range constraints, defaults, indexes, lifecycle, and deletion/archive behavior.

### Core entities

- `Workspace`: id, name, workspacePath, baseCurrency, locale, schemaVersion, appVersion, createdAt, updatedAt.
- `PassiveIncomeSource`: id, name, sourceType, currency, expectedAmountMinor, paymentCadence, nextExpectedPaymentDate, confidenceLevel, marketSensitivity, lastConfirmationDate, status, notes, createdAt, updatedAt, deletedAt.
- `CapitalPool`: id, name, currentValueMinor, currency, growthTargetType, growthTargetRateBps, reinvestmentRuleId, principalDrawdownAllowed, principalDrawdownLimitMinor, valuationDate, createdAt, updatedAt, deletedAt.
- `IncomeEvent`: id, sourceId, eventType, expectedDate, actualDate, expectedAmountMinor, confirmedAmountMinor, currency, confirmationStatus, confidenceLevel, evidenceId, scenarioVersionId, createdAt, updatedAt, deletedAt.
- `Confirmation`: id, incomeEventId, confirmedAt, confirmedAmountMinor, confirmedDate, evidenceId, method, userNote, createdAt, updatedAt.
- `Assumption`: id, key, label, valueJson, unit, source, freshnessStatus, lastReviewedAt, validFrom, validTo, userOverride, overrideReason, createdAt, updatedAt, deletedAt.
- `ScenarioVersion`: id, label, scenarioType, generatedAt, assumptionHash, sourceSnapshotHash, warningFlagsJson, createdAt, updatedAt.
- `MonthlyPlan`: id, month, scenarioVersionId, expectedIncomeMinor, confirmedIncomeMinor, taxEstimateMinor, reserveTargetMinor, plannedReinvestmentMinor, capitalProtectionBufferMinor, safeToUseMinor, actualConsumptionMinor, capitalErosionRisk, createdAt, updatedAt.
- `PolicyChange`: id, policyType, previousValueJson, newValueJson, reason, effectiveMonth, createdAt, updatedAt.
- `ReviewDecision`: id, month, reviewedAt, decisionType, safeToUseMinor, rationale, linkedScenarioVersionId, createdAt, updatedAt.
- `Correction`: id, entityType, entityId, fieldName, previousValueJson, newValueJson, reason, acceptedAt, createdAt.
- `ImportBatch`: id, fileName, fileHash, mappingJson, previewStatus, validationStatus, importedAt, rollbackStatus, createdAt.
- `NotificationRule`: id, eventType, scopeJson, conditionJson, thresholdMinor, operator, severity, channel, cooldownMinutes, enabled, createdAt, updatedAt, deletedAt.
- `Notification`: id, ruleId, ruleVersion, eventId, deduplicationKey, channel, severity, title, body, actionUrl, deliveryState, attempts, lastAttemptAt, terminalFailureReason, createdAt, updatedAt.
- `Evidence`: id, sourceType, label, origin, capturedAt, freshnessAt, filePath, contentHash, mimeType, sizeBytes, createdAt, updatedAt.

### Required distinctions

The model and UI MUST distinguish:

- income generated by capital from selling capital;
- confirmed income from expected/projected income;
- cash income from principal sales or drawdown;
- recurring passive income from one-time inflows;
- actual values from assumptions, forecasts, overrides, and stale values;
- safe-to-use income from gross income, reserves, taxes, reinvestment, and capital-protection buffers.

A plan that depends on reducing principal MUST be labelled as principal drawdown unless that drawdown is explicitly modelled and allowed by policy.

### Provenance

Every derived amount MUST expose:

- formula inputs;
- source records;
- assumption set;
- scenario label;
- generated timestamp;
- freshness status;
- user overrides and override reasons;
- warning flags;
- change since previous forecast.

A forecasted number is incomplete without its assumptions. The UI MUST show the assumption, source, freshness, and user override behind every derived amount.

## 6. Forecasting and safe-to-use calculation rules

Fathom MUST forecast monthly gross income, deductions, reinvestment, and safe-to-use amounts for at least the next 12 months.

The forecasting engine MUST compute conservative, expected, and optimistic scenarios. These scenarios MUST be displayed as planning ranges, never as guarantees.

For each month and scenario, compute:

1. expected passive income by source;
2. confirmed income received;
3. variance between planned and actual income;
4. taxes or withholding estimates;
5. required reserves;
6. required reinvestment to preserve the selected capital-growth target;
7. capital-protection buffer;
8. safe-to-use amount;
9. capital erosion risk;
10. warning flags.

The safe-to-use calculation MUST be represented as:

`safeToUse = passiveIncomeAvailable - taxes - requiredReserves - plannedReinvestment - capitalProtectionBuffer`

Where:

- `passiveIncomeAvailable` MUST NOT include principal sales unless explicitly modelled as principal drawdown;
- unconfirmed expected payments MUST remain projected and MUST NOT be treated as confirmed;
- missed or delayed income MUST reduce confidence and MAY reduce safe-to-use depending on scenario rules;
- taxes, reserves, reinvestment, and buffers MUST be calculated in integer minor currency units;
- rounding MUST be deterministic and documented by currency;
- negative safe-to-use values MUST be shown as a shortfall, not hidden or clamped without explanation.

Capital erosion risk MUST be flagged when spending, taxes, fees, missed income, delayed income, or insufficient reinvestment would require principal drawdown or violate the capital-growth policy.

Unused monthly income MUST be assigned one of the following treatments: reinvested, reserved, carried forward, or consumed. The chosen treatment MUST be visible and auditable.

Time, currency, locale, and rounding choices MUST be explicit because they affect result meaning.

## 7. Dashboard, timeline, scenarios, attention, and quiet/error/offline states

Fathom’s dashboard MUST be decision-oriented, not a wall of vanity metrics. The information hierarchy MUST put the current decision answer first, followed by exceptions and attention items, then trends and supporting detail.

### Primary card

The primary card MUST show:

- this month’s safe-to-use amount;
- confidence and freshness;
- decisive deductions;
- the condition most likely to change the amount;
- whether the amount depends on projected, confirmed, stale, or overridden data;
- a path to calculation details and evidence.

### Timeline

The timeline MUST distinguish expected, confirmed, late, changed, missing, and corrected income events. Timeline items MUST show amount, currency, source, expected date, actual date when present, confidence, freshness, and evidence link.

### Scenario comparison

Scenario views MUST compare conservative, expected, and optimistic monthly paths. They MUST show assumptions, warning flags, projected safe-to-use amounts, reserve status, reinvestment status, and capital erosion risk. No scenario may be presented as guaranteed.

### Capital-policy card

The capital-policy card MUST show reinvestment target, reserve status, principal-drawdown risk, capital-growth target, threshold changes, and material policy violations.

### Attention queue

The attention queue MUST foreground only decision-changing items, including stale assumptions, missing confirmations, projected shortfalls, tax-reserve gaps, policy violations, safe-to-use threshold changes, income delays, and capital erosion risks.

### Quiet state

The quiet state MUST show the current answer, what is monitored, last review, next expected payment, next scheduled review, and last successful local refresh without filling the screen with unnecessary charts.

### Error, empty, loading, partial-failure, and offline states

- **Loading:** preserve the last valid result when possible and label its age; use skeletons only for content that has never loaded.
- **Partial failure:** keep healthy widgets usable and explain which source or calculation failed, the effect, and retry path.
- **Empty:** explain which source, assumption, policy, or confirmation is missing and offer the next useful action.
- **Offline:** show locally available evidence and last sync/backup state without pretending external data is current.
- **Store failure:** show backup, repair, export, retry, or upgrade guidance depending on cause.

Every card MUST have a purpose, title, current state, freshness indicator, and path to details. Charts MUST only be used when shape, trend, comparison, or distribution is easier to understand visually than prose or a table. Every visualization MUST have an accessible text/table equivalent, descriptive labels, keyboard access, responsive sizing, and non-color-only distinctions. Tooltips MUST show exact values, units, time period, source, and freshness.

Responsive behavior MUST be:

- mobile: one primary answer, attention queue, and progressive disclosure;
- tablet: primary answer plus the most important comparison or timeline;
- desktop: multi-column overview with a dedicated detail surface.

Compact layouts MUST NOT reduce critical labels to unexplained icons or hide active warnings.

## 8. Entry, CSV import, correction, and review workflows

### Manual entry

Manual entry MUST support careful creation and editing of sources, expected payments, confirmations, assumptions, capital pools, reserve rules, reinvestment rules, and review decisions. Forms MUST use react-hook-form and shared zod validation. Validation errors MUST identify the field, rule, and remediation.

The app MUST never infer a confirmed payment from an expected schedule. A payment becomes confirmed only through explicit user confirmation, imported evidence accepted by the user, or another documented confirmation action.

### CSV import

CSV import MUST include:

1. file selection under the local workspace;
2. content hashing and duplicate import detection;
3. preview before write;
4. column mapping;
5. zod validation;
6. duplicate detection against existing events and sources;
7. user review of proposed creates, updates, and ignored rows;
8. transactional commit;
9. rollback for the import batch;
10. import audit trail.

Invalid rows MUST be reported with row number, column, validation rule, and proposed fix. No imported row may silently overwrite a confirmed value.

### Corrections

Users MUST be able to correct classifications, dates, amounts, sources, assumptions, and policy settings while preserving previous value, new value, reason, timestamp, and affected entity. Corrections MUST be transactional and MUST immediately recompute affected scenarios, dashboard cards, attention items, and notifications.

### Review workflow

A monthly review MUST let the user inspect expected versus confirmed income, stale assumptions, reserves, reinvestment, capital erosion risk, and safe-to-use recommendation. The review decision MUST persist the chosen safe-to-use amount, rationale, scenario version, and linked evidence.

## 9. Notification policy

Fathom MUST notify only for decision-changing events:

- confirmed payment;
- missed payment;
- projected shortfall;
- reserve breach;
- stale critical assumption;
- safe-to-use threshold change;
- policy violation;
- material capital erosion risk.

Every notification MUST explain what changed, why it matters, observed value, relevant threshold, period, source/freshness, and action URL linking to the underlying evidence.

Notification rules MUST include triggering event or state transition, optional scope, condition, threshold, comparison operator, severity, recipients or local destination, channel, and cooldown. Numeric conditions MAY use `>`, `>=`, `<`, `<=`, `==`, and `between`; state rules MAY match transitions such as `expected -> confirmed` or `expected -> missed`.

The same semantic event MUST NOT notify the same recipient and channel more than once within its cooldown or evaluation period. Notifications MUST track stable deduplication keys, rule version, event, values, evaluation time, delivery state, attempts, and terminal failure reason. Retries MUST be bounded and MUST NOT create duplicate notifications.

Supported channels MUST include in-app transient feedback and a persistent notification center. Email MAY be supported for critical alerts and digests only if destination verification, quiet hours, disabled channels, and privacy-safe templates are implemented. Push MAY be optional through a Service Worker and VAPID keys.

Templates MUST use typed runtime fields such as subject, current state, threshold, observed value, period, reason, and action URL. Templates MUST NOT expose secrets, full statement contents, or sensitive financial details in previews. Missing required template fields MUST fail validation instead of producing malformed messages.

## 10. API, Server Actions, and route requirements

Every API endpoint or Server Action in the specification MUST define method or action name, path when applicable, request schema, response schema, validation errors, authorization/local access assumptions, transaction behavior, and test coverage.

At minimum specify read and mutation surfaces for:

- sources;
- income events;
- confirmations;
- assumptions;
- capital pools;
- scenarios and forecasts;
- dashboard summary;
- attention queue;
- CSV import preview/commit/rollback;
- corrections;
- notifications;
- export/import/backup/restore;
- health check.

Error responses MUST use stable codes and messages. Include recoverable errors for validation failure, duplicate import, stale write/version conflict, locked database, unsupported schema version, corrupted file, missing evidence file, disk-full, migration failure, and external service unavailable.

Concurrency MUST be addressed for shared mutable state. Use explicit transactions for multi-step writes and optimistic concurrency fields such as `version` or `updatedAt` where stale edits can occur.

## 11. Privacy, safety, and advice boundaries

Fathom MUST keep imported statements and planning data local by default. It MUST never request brokerage credentials. It MUST never execute trades, transfers, withdrawals, deposits, or other financial transactions.

The UI MUST avoid guarantee language. It MUST not state or imply that passive income, expected returns, payment timing, tax treatment, asset value, financial independence, or capital growth is guaranteed.

Negative outcomes MUST be named specifically: shortfall, capital erosion risk, stale assumption, income delayed, unsafe consumption, insufficient reserve, insufficient reinvestment, or principal drawdown.

If optional sync, backup, email, push, or AI features are introduced, they MUST be opt-in, explain destination and purpose, and preserve offline usefulness when unavailable.

## 12. Testing and acceptance criteria

Use Vitest with happy-dom for component tests, Vitest with temporary SQLite files and isolated data directories for API/storage tests, and Playwright for critical local user flows. Application logic MUST maintain at least 80% line coverage.

Tests MUST cover:

- first-run workspace initialization;
- restart persistence;
- SQLite WAL mode configuration;
- migrations from at least one older schema fixture once schema evolves;
- refusal to start on unsupported future schema version;
- backup before destructive migration or repair;
- export/import with attachments and manifest checksums;
- backup restore;
- transactional rollback for failed multi-entity writes;
- database locking, disk-full handling where practical, and corrupted-file detection;
- manual entry validation;
- CSV preview, mapping, validation, duplicate detection, commit, and rollback;
- corrections preserving previous values and reasons;
- immediate recomputation after accepted correction;
- confirmed versus expected income distinctions;
- safe-to-use calculations in integer minor units;
- conservative, expected, and optimistic forecasts over at least 12 months;
- principal drawdown and capital erosion risk detection;
- stale assumption detection;
- dashboard quiet, attention, loading, empty, partial-failure, offline, and store-failure states;
- accessible chart/table equivalents and keyboard navigation;
- notification rule evaluation, cooldown, deduplication, delivery failure, and template validation;
- health check output;
- offline operation.

Fathom is complete when a user can identify this month’s safe-to-use amount, understand confidence and freshness, inspect evidence and assumptions, distinguish confirmed from projected income, see principal drawdown risk, review capital-growth policy effects, correct data safely, import statements with rollback, work offline, export/restore a workspace, and receive only decision-changing notifications.

Return the final answer with these sections:

1. Product promise and explicit non-goals
2. Local-first architecture and SQLite persistence
3. Financial data model and calculation provenance
4. Dashboard, timeline, scenarios, attention, and quiet/error/offline states
5. Entry, CSV import, correction, and review workflows
6. Forecasting and safe-to-use calculation rules
7. Notification policy
8. Privacy, safety, and advice boundaries
9. Testing and acceptance criteria