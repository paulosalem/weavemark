# Blind derived-evidence packet

Study: Evidence-to-Decision Workspace
Variant: A
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 67
- Variable payload words: 111
- Output words: 1092
- Local leverage: 16.3x
- Candidate facts: 97
- Counted facts: 97
- Discounted fact units: 96.5
- Information density per 1k output words: 88.4
- Information yield per 1k source words: 1440.3

## Extracted fact candidates

- This is the coherent implementation-ready specification for Evidence-to-Decision Workspace.
- Treat this specification as the source of truth for a programming agent or human engineer.
- Include first-build scope, out-of-scope items, architecture, domain model,
- durable records, workflows, UI surfaces, automation rules, validation plan,
- failure handling, privacy/provenance rules, and acceptance criteria.
- Distinguish required first-build behavior from optional later enhancements.
- Avoid separate support prompts, prompt packs, or artifact manifests.
- Every major requirement should have an observable user-facing or validation
- Use concrete field names, states, events, screens, checks, and recovery paths
- instead of generic quality advice.
- Design Evidence-to-Decision Workspace, a local-first application for turning messy personal and professional source material into auditable decisions and follow-up actions.
- The user imports notes, documents, links, research snippets, meeting fragments, and news, then normalizes inputs, extracts claims, grades evidence, surfaces contradictions, compares explanations or options, decides whether to act, wait, or investigate, and converts decisions into tracked actions.
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
- The product should turn messy sources into auditable claims, evidence items,
- contradictions, hypotheses, options, decision gates, actions, review loops,
- Initial source families: documents, PDFs, notes, meeting transcripts, pasted snippets, URLs, newsletters, GitHub issues or releases, research papers, web pages, news items, calendars, and compact observations..
- Decision domains to support first: personal project choices, public-release decisions, technology adoption, vendor or tool selection, investment-like tradeoffs, operational incidents, and research-backed action plans..
- Sources should preserve title, author or organization when known, URL or local
- reference, source family, retrieved time, published time, checksum, import
- method, extraction status, and permission policy.
- Normalize inputs into source facts, inferred structure, existing decisions,
- action candidates, risks, blockers, open questions, contradictions, and
- Claims should be first-class records with statement, scope, status, source
- links, owner, confidence, decision relevance, tags, and review state.
- Evidence items should record relevance, specificity, freshness, independence,
- contradiction status, reliability, diagnostic value, direction, main gap, and
- Contradictions should remain visible with type, affected claims, source
- family, severity, resolution state, and decision consequence.
- ACH-style review should compare evidence rows against competing hypotheses
- with consistent, inconsistent, neutral, or missing-but-expected assessments.
- Decision gates should support act, wait, investigate, delegate, monitor,
- archive, or escalate with thresholds, blockers, confirmations, and revisit
- Actions should link back to sources, claims, evidence, hypotheses, options,
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

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/evidence-decision/A.json`
