# Blind derived-evidence packet

Study: Intelligence-to-Execution Kanban
Variant: C
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 65
- Variable payload words: 74
- Output words: 1066
- Local leverage: 16.4x
- Candidate facts: 97
- Counted facts: 97
- Discounted fact units: 96.75
- Information density per 1k output words: 90.8
- Information yield per 1k source words: 1488.5

## Extracted fact candidates

- This is the coherent implementation-ready specification for Work Intelligence Kanban.
- Treat this specification as the source of truth for a programming agent or human engineer.
- Include first-build scope, out-of-scope items, architecture, domain model,
- durable records, workflows, UI surfaces, automation rules, validation plan,
- failure handling, privacy/provenance rules, and acceptance criteria.
- Distinguish required first-build behavior from optional later enhancements.
- Avoid separate support prompts, prompt packs, or artifact manifests.
- Every major requirement should have an observable user-facing or validation
- Use concrete field names, states, events, screens, checks, and recovery paths
- instead of generic quality advice.
- Design Work Intelligence Kanban, a local-first workspace that connects information intake with project execution.
- The user follows selected work topics, receives relevant signals, captures ideas, decides what to do, delegates or executes work, tracks status, and turns useful inputs into concrete outputs.
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
- The product should turn monitored topics, external signals, personal ideas,
- decisions, delegations, actions, warnings, and generated outputs into one
- Monitor these initial topic families: Framework-X and prompt languages; local-first AI tools; agentic workflows; research automation; UI/UX examples; personal project opportunities; selected competitors and communities..
- Each topic should define watch intent, source families, cadence, exclusions,
- thresholds, muted patterns, review cadence, and failure behavior.
- Signals should preserve title, source, URL or local reference, author or
- organization when known, retrieved time, published time, topic match, source
- family, evidence quality, novelty, confidence, relevance, and summary.
- Signals may become insights, ideas, questions, warnings, decisions,
- delegations, actions, watch items, outputs, or deliberate archive records.
- Ideas should carry hypothesis, expected value, owner, status, next action,
- dependencies, output links, review cadence, and evidence that the idea was
- Delegations should track owner, request, expected deliverable, due or check-in
- window, status evidence, blockers, handoff context, and follow-up cadence.
- Recommendations should preserve alternatives, rationale, uncertainty,
- confidence, source trace, and revisit condition.
- Notifications should be explainable, deduplicated, cooldown-aware, thresholded
- by topic, and tied to meaningful card conversions or status changes.
- The system should answer: what came in, why it mattered, what was decided, who
- is doing what, what is blocked, what changed, and what output was produced.
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
- ... 37 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/work-intelligence-kanban/C.json`
