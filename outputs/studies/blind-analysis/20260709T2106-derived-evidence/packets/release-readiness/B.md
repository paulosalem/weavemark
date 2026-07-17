# Blind derived-evidence packet

Study: Release Readiness Workbench
Variant: B
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 241
- Variable payload words: 55
- Output words: 4762
- Local leverage: 19.76x
- Candidate facts: 342
- Counted facts: 342
- Discounted fact units: 322.0
- Information density per 1k output words: 67.6
- Information yield per 1k source words: 1336.1

## Extracted fact candidates

- Build **Release Readiness Workbench**, a local-first release command center that turns messy release material into structured gates, evidence, validation, risks, actions, notes, and go/no-go records.
- This is a directly implementable TypeScript/Next.js/Prisma/SQLite application specification for an AI programming agent.
- The result is a single local workspace for proving whether a release is ready across Framework-X public README, docs, examples, generated outputs, study results, release notes, package artifacts, extension builds, CLI behavior, installation checks, single-output validation studies, qualitative evidence, score explanations, browser-facing examples, screenshots, traces, console/runtime findings, issues, PR notes, local TODOs, deferred work, waivers, and known limitations.
- Target user: maintainers preparing a public software/prompt/tooling release who need inspectable confidence rather than optimistic launch prose.
- Core job: import fragmented release material, normalize it into facts, map it to release gates and artifacts, run or record validation, attach evidence, triage failures, track actions, decide go/no-go/limited release, and export an audit-ready release record.
- First-build value: one user can run the app locally, create or import a release candidate workspace, see readiness by gate, preserve evidence, fix/rerun failures, write accurate release notes, and produce a final release decision.
- The specification is implementation guidance, not an interview script. Make safe assumptions where needed and expose only genuinely blocking open decisions.
- TypeScript 5+ strict mode; no `any`.
- Tailwind CSS with design tokens in `tailwind.config.ts`.
- React Server Components by default; client components only for interactive boards, filters, forms, charts, browser-only variants, and live updates.
- Zustand only for local UI state that should not be canonical.
- `react-hook-form` plus shared `zod` schemas for forms, Server Actions, and API routes.
- Node.js runtime only for routes/actions touching SQLite; do not use Edge runtime for storage paths.
- Prisma Migrate for deterministic versioned migrations.
- Vitest with happy-dom for component tests.
- Vitest with temporary SQLite files and isolated data directories for API/storage tests.
- Playwright for critical local user flows.
- Minimum 80% line coverage for application logic.
- Target: local Node.js process, self-hosted single-user service, or optional Electron/Tauri wrapper.
- Not supported by default: serverless deployments with ephemeral or shared filesystem state.
- The app MUST be useful without a hosted multi-tenant backend.
- Do not add billing, subscriptions, tenant isolation, organization onboarding, or hosted accounts.
- The local machine is the source of truth.
- Browser `localStorage`, IndexedDB, memory, and cache files MAY improve UX but MUST NOT be canonical for user data.
- External network calls, including AI calls, MUST be explicit in UI and configuration; existing local data must remain viewable when those calls fail.
- Keep private release material local by default.
- Before sending any release material to an external AI, web, or integration service, show destination, purpose, payload scope, and data policy.
- Logs must avoid secrets, API keys, refresh tokens, and full sensitive payloads unless the user explicitly enables diagnostic capture.
- Provide one default local workspace and allow the user to choose/create another workspace directory.
- Store the SQLite database, attachments, generated artifacts, evidence files, screenshots, traces, validation logs, backups, repair logs, and exports under the workspace directory or OS user-data directory.
- Show active workspace path, database path, schema version, app version, and storage health in Settings and Diagnostics.
- Development default SHOULD be inspectable, e.g. `.local-data/app.sqlite`.
- Packaged apps SHOULD use the OS user-data directory.
- Provide backup, restore, import, and export flows so workspaces can move between machines without hidden server state.
- Validate workspace readability, writability, schema version, available disk, and attachment directory access at startup.
- If the local store is missing, initialize deterministically with migrations.
- If existing data is present, create a timestamped backup before running pending migrations unless the database is unreadable.
- Refuse to start on unsupported future schema versions; show a recoverable error.
- If the store is locked, corrupted, too new, disk-full, or migration-failed, show backup, repair, upgrade, retry, and export guidance.
- Repair tools must report changes and preserve the original damaged database when possible.
- Every durable table must include stable primary key, `createdAt DateTime @default(now())`, `updatedAt DateTime @updatedAt`, and recoverable deletion/archive behavior such as `deletedAt DateTime?`.
- Use camelCase in Prisma schema, mapped to snake_case table/column names where practical.
- Multi-entity updates MUST run in explicit transactions.
- Event insertion and visible state updates MUST be persisted in the same transaction when the event explains the state change.
- Use optimistic concurrency fields such as `version` or `updatedAt` for records that may be edited by the user and AI/automation.
- Large attachments and generated artifacts should live as files under the workspace, not database blobs by default.
- Store attachment metadata: content hash, MIME type, byte size, origin, relative file path, created/updated timestamps, and integrity status.
- Deleting a record must define whether referenced files are retained, archived, garbage-collected, or moved to a trash area.
- Exports MUST include SQLite database, referenced files, schema version, app version, and manifest checksums.
- Define explicit relational tables and TypeScript/Zod domain schemas for these entities.
- `id`, `name`, `path`, `schemaVersion`, `appVersion`, `settings`, `createdAt`, `updatedAt`.
- `id`, `workspaceId`, `name`, `version`, `description`, `status`, `targetDate`, `createdAt`, `updatedAt`, `deletedAt`.
- Status enum: `draft`, `normalizing`, `validating`, `blocked`, `ready_with_caveat`, `ready`, `released`, `archived`.
- `id`, `releaseCandidateId`, `kind`, `title`, `rawText`, `fileRef`, `sourceUri`, `sourceLabel`, `freshnessDate`, `importedAt`, `confidence`, `createdAt`, `updatedAt`.
- Kinds include notes, README, docs, examples, generated output, package artifact, extension build, CLI output, screenshot, trace, console finding, issue, PR note, TODO, waiver, limitation, study, release note.
- `id`, `releaseCandidateId`, `sourceMaterialId`, `factType`, `statement`, `sourceQuote`, `inferenceLevel`, `confidence`, `contradictionGroupId`, `staleness`, `createdAt`, `updatedAt`.
- Preserve source fidelity: explicit facts, inferred structure, decisions, action candidates, risks/blockers, open questions, and confidence notes must be distinguishable.
- `id`, `releaseCandidateId`, `track`, `title`, `criteria`, `owner`, `status`, `confidence`, `dueDate`, `releaseImpact`, `createdAt`, `updatedAt`.
- Tracks: product behavior, documentation, examples, tests, packaging, install, security/privacy, performance, accessibility, support, rollback/monitoring, browser validation, AI/prompt quality, release notes.
- Status enum: `ready`, `ready_with_caveat`, `needs_fix`, `defer`, `not_applicable`, `not_checked`, `blocked`.
- ... 282 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/release-readiness/B.json`
