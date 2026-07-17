# Blind derived-evidence packet

Study: Intelligence-to-Execution Kanban
Variant: B
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 208
- Variable payload words: 54
- Output words: 3934
- Local leverage: 18.91x
- Candidate facts: 292
- Counted facts: 291
- Discounted fact units: 287.75
- Information density per 1k output words: 73.1
- Information yield per 1k source words: 1383.4

## Extracted fact candidates

- Use this implementation-ready software specification to build **Work Intelligence Kanban**, a local-first Kanban application where monitored signals, ideas, decisions, delegations, actions, outputs, future watch rules, alerts, reviews, and archives share one traceable card/board model.
- Use this specification as the source of truth for a programming agent.
- Use concrete program/programming terms.
- State safe assumptions and the smallest set of genuinely blocking open decisions.
- Separate product behavior from implementation details while making both precise enough to build.
- Define Work Intelligence Kanban as a local-first work-intelligence workspace that turns recurring monitoring into execution:
- Topic monitoring becomes board intake, not a separate feed.
- Every important signal needs a disposition: reject, mute, watch later, investigate, convert to idea, convert to decision input, delegate, act, output, archive, or create/update a watch rule.
- Ideas carry origin, owner, status, next action, review point, evidence, and proof of outcome.
- The app must answer: “What came in?”, “Why did it matter?”, “What did I decide?”, “Who is doing what?”, “What is blocked?”, “What changed because of this?”, and “Which outputs did this produce?”
- Initial monitored topic families:
- Framework-X, prompt languages, and specification-driven prompting.
- Local-first AI tools and personal agent workspaces.
- Agentic programming workflows, validation practices, and release-readiness examples.
- UI/UX ideas for calm productivity and project command centers.
- Research automation, recurring topic monitoring, and signal-to-action workflows.
- Personal project opportunities, risks, deadlines, and follow-up items.
- Specify a credible first build:
- Local-first, single-user or one local workspace by default.
- No hosted multi-tenant backend, subscriptions, billing, organization onboarding, or tenant isolation unless explicitly marked later.
- The local machine is the source of truth. Browser-only storage may cache UI state but must not be canonical for user data.
- Existing local data must remain loadable when external AI, search, or integration calls fail.
- External network calls must be explicit in the UI and configuration; before sending local content to external AI/web services, show destination and purpose.
- Private data stays local by default. Logs must not store secrets, API keys, refresh tokens, or full sensitive payloads unless the user enables diagnostic capture.
- TypeScript 5+ strict mode, no `any`.
- Tailwind CSS with design tokens in `tailwind.config.ts`.
- React Server Components by default; Zustand only for local client UI state that needs it.
- react-hook-form with zod validation schemas shared with API and Server Actions.
- Server Actions for mutations; `fetch` in Server Components for reads.
- Node.js runtime only for routes/actions that touch SQLite; do not use Edge runtime for SQLite paths.
- `DATABASE_URL` pointing to a local SQLite file under the active workspace or OS user-data directory.
- One local app server owns SQLite writes; if packaged for desktop use, the desktop shell starts and supervises that server.
- Environment validation via `env.mjs` with zod at startup.
- `GET /api/health` returning local store status, schema version, and app version.
- Include major components, data flow, extension points, local server boundaries, and failure behavior.
- One default local workspace; user can choose/create another workspace directory.
- Store SQLite database, attachments, generated artifacts, backups, exports, derived files, repair logs, and manifests under the workspace/data directory.
- Show active workspace path in settings and diagnostics.
- Provide export/import so a workspace moves between machines without hidden server state.
- Startup validates readability, writability, schema version, migration status, and SQLite availability.
- Missing store initializes deterministically with migrations.
- Locked, corrupted, disk-full, unreadable, or future-version store shows recoverable backup/repair/upgrade guidance.
- Specify SQLite/Prisma rules:
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
- Define entities, fields, relations, identifiers, indexes, lifecycle states, and invariants for at least:
- Cards are typed work-intelligence records, not generic tasks.
- Define required and optional card fields:
- priority, urgency, relevance, novelty, confidence, impact, actionability, evidence quality, source family, status, owner, due/check-in window, blocked state, unread/stale state, and review cadence
- timestamps: created, updated, seen, due, archived
- provenance links to signals, evidence, decisions, actions, delegations, outputs, attachments, AI runs, and activity events
- UI state: selected, focused, expanded, disabled, loading, error, stale, unread
- ... 232 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/work-intelligence-kanban/B.json`
