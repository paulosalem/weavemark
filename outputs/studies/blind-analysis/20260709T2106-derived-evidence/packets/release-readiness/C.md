# Blind derived-evidence packet

Study: Release Readiness Workbench
Variant: C
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 68
- Variable payload words: 84
- Output words: 1069
- Local leverage: 15.72x
- Candidate facts: 98
- Counted facts: 98
- Discounted fact units: 97.75
- Information density per 1k output words: 91.4
- Information yield per 1k source words: 1437.5

## Extracted fact candidates

- This is the coherent implementation-ready specification for Release Readiness Workbench.
- Treat this specification as the source of truth for a programming agent or human engineer.
- Include first-build scope, out-of-scope items, architecture, domain model,
- durable records, workflows, UI surfaces, automation rules, validation plan,
- failure handling, privacy/provenance rules, and acceptance criteria.
- Distinguish required first-build behavior from optional later enhancements.
- Avoid separate support prompts, prompt packs, or artifact manifests.
- Every major requirement should have an observable user-facing or validation
- Use concrete field names, states, events, screens, checks, and recovery paths
- instead of generic quality advice.
- Design Release Readiness Workbench, a local-first public-release command center that turns release notes, issue lists, pull request summaries, docs gaps, example runs, test results, package artifacts, screenshots, risks, blockers, waivers, and launch decisions into one auditable go/no-go workspace.
- Use Next.js with TypeScript strict mode, Prisma, and SQLite.
- Keep authoritative workspace state local by default in a user-selectable
- Use SQLite WAL mode, schema versioning, deterministic migrations, startup
- diagnostics, explicit transaction boundaries, backups before risky migrations,
- Store large attachments and generated artifacts as files; store metadata,
- content hash, MIME type, size, origin, relative path, and provenance in SQLite.
- Durable records should have stable IDs, created/updated timestamps, status,
- owner or actor when relevant, provenance links, optimistic versioning for
- conflicting writes, and archive or soft-delete behavior.
- Exports should include database, referenced files, schema version, application
- Imports should validate checksums and require
- explicit confirmation before overwriting a workspace.
- External providers are optional. Existing local data must remain usable when
- AI, search, feeds, or integrations are unavailable.
- Logs must avoid secrets, tokens, private payloads, and full sensitive artifacts
- unless diagnostic capture is explicitly enabled.
- The product should transform messy release material into release candidates,
- gates, evidence items, validation checks, docs/example readiness, risks,
- blockers, waivers, actions, release notes, decisions, exports, and post-launch
- Release gates should cover product behavior, documentation, examples, tests,
- build/package/install, security/privacy, accessibility, performance, rollback,
- support, migration notes, and release communication.
- Gate states should include not started, collecting evidence, ready, ready with
- caveat, blocked, waived, deferred, and not applicable.
- Evidence items should record type, source path or URL, command or flow,
- environment, artifact reference, freshness, scope, reviewer, quality,
- limitations, linked claim, and release impact.
- Critical gates should block release unless explicitly waived with rationale,
- owner, approver, expiry, accepted risk, and revisit trigger.
- Validation checks need expected proof, owner, status, last run, failure meaning,
- rerun requirement, release impact, and supersession history.
- Failed validation should create actions while preserving failed evidence until
- Release decisions should support ship, ship with caveat, wait, fix first,
- defer scope, rollback, or cancel.
- Release notes should distinguish verified behavior, known limitations,
- deferred work, migration notes, support guidance, and rollback/monitoring
- Apply release readiness to these surfaces: Framework-X public README, docs, examples, generated outputs, study results, release notes, package artifacts, extension builds, CLI behavior, installation checks, browser-facing examples, screenshots, traces, issues, PR notes, local TODOs, deferred work, waivers, and known limitations.
- Use cards as durable bounded records, not only tasks.
- Cards need type, title, summary, status, owner, priority, tags, due or review
- window, source links, dependencies, next action, blocked reason, output links,
- Boards should support explicit stages, meaningful transition rules, keyboard
- movement, drag movement, invalid-move explanations, saved views, search,
- filters, sorting, and detail panes.
- Provide typed output surfaces for text, tables, structured records, reports,
- status, forms, images or screenshots when relevant, terminal logs, and audit
- Each surface should preserve payload or file reference, schema version, source,
- lineage, status, revision history, comments, approvals, pin/minimize/pop-out
- state, and export/apply actions.
- Streaming or generated surfaces must visibly distinguish draft, partial, final,
- ... 38 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/release-readiness/C.json`
