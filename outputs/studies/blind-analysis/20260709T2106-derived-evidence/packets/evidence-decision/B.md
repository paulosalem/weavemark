# Blind derived-evidence packet

Study: Evidence-to-Decision Workspace
Variant: B
Mode: derived-evidence

Evaluate this anonymous variant from automated measurements and extracted fact candidates only. Do not open raw source/output files or the private derandomization key.

## Derived metric summary

- Local authored source words: 249
- Variable payload words: 66
- Output words: 6632
- Local leverage: 26.63x
- Candidate facts: 427
- Counted facts: 420
- Discounted fact units: 396.5
- Information density per 1k output words: 59.8
- Information yield per 1k source words: 1592.4

## Extracted fact candidates

- Build **Evidence-to-Decision Workspace**: a local-first web application where messy sources become traceable claims, evidence, contradictions, explanations, decisions, actions, alerts, and reusable outputs.
- The product is an evidence command center for:
- saved articles, newsletters, and links;
- research papers, documentation, and official pages;
- GitHub issues, releases, and technical discussions;
- market, product, competitor, and community signals;
- manually added observations and conversations.
- The workspace supports decisions across:
- prompt-language and agent-workflow design choices;
- investment or business opportunities that need evidence discipline;
- risks, warnings, and wait-versus-act judgments.
- The specification below is the source of truth for implementation.
- Use concrete requirements, safe assumptions, and testable acceptance criteria.
- The first build MUST be useful as a single-user local workspace without a hosted multi-tenant backend.
- The user needs to collect messy information from many sources, normalize it into explicit claims and evidence, compare competing interpretations, and make revisitable decisions with clear provenance.
- The app must prevent “confident but untraceable” conclusions by keeping raw sources, extracted facts, claims, evidence ratings, contradictions, hypotheses, decision gates, actions, and outputs connected.
- The app turns source chaos into a durable evidence-and-decision graph:
- extract source facts without inventing unsupported content;
- surface contradictions, gaps, and uncertainty;
- decide to act, wait, investigate, delegate, monitor, or revisit;
- generate reusable outputs that cite their inputs;
- preserve a local audit trail.
- local workspace creation and diagnostics;
- SQLite-backed source, claim, evidence, decision, action, output, notification, and activity storage;
- source intake for text, URL, file metadata, compact observation, transcript/note, and saved article references;
- attachment handling with previews for supported types;
- source normalization into facts, inferred structure, decisions, risks, questions, and confidence notes;
- evidence graph with claims, evidence ratings, contradictions, hypotheses, and provenance;
- decision graph with option comparison, forecast uncertainty, values tradeoffs, decision gates, and action planning;
- board/card UI for source review, evidence review, decision review, actions, alerts, and outputs;
- dashboards, search, filters, typed output surfaces, notifications, activity stream, REST API, and live events;
- local-first privacy variants and explicit external AI/network consent;
- validation through a first successful user session.
- push notifications outside local browser support;
- deep file parsers for all rich document types;
- desktop packaging, if the local Node app flow is complete.
- Out of scope for the first build:
- serverless deployment with ephemeral/shared filesystem as the default;
- external writes to repositories, CRMs, brokers, or productivity systems without explicit future integration design.
- TypeScript 5+ strict mode; no `any`.
- Tailwind CSS with design tokens in `tailwind.config.ts`.
- React Server Components by default.
- Zustand only for local client UI state that cannot live in URL/search params/server data.
- react-hook-form with zod schemas shared by UI, Server Actions, and API handlers.
- Node.js runtime only for routes/actions touching SQLite.
- Vitest with happy-dom for unit/component tests.
- Vitest using temporary SQLite files for API/storage tests.
- Playwright for critical local user flows.
- Minimum 80% line coverage for application logic.
- One local app server owns SQLite writes.
- `DATABASE_URL` MUST point to a local SQLite file under the active workspace directory or OS user-data directory.
- The app MUST expose the configured data directory and active workspace path in settings and diagnostics.
- Browser storage MAY cache disposable UI state, but SQLite is the canonical durable store.
- Existing local data MUST remain readable when external AI, search, or integration calls fail.
- `app/`: App Router routes, layouts, Server Components, route handlers.
- `components/`: shared UI primitives, cards, boards, surfaces, charts, forms.
- `features/`: domain feature modules:
- `lib/db/`: Prisma client, migrations helpers, transaction helpers, backup/repair.
- `lib/domain/`: zod schemas, state machines, scoring, ACH, decision gates, evidence grading.
- `lib/files/`: attachment and artifact file storage.
- ... 367 additional facts in JSON evidence.

## Evidence file

Full derived evidence JSON: `outputs/studies/blind-analysis/20260709T2106-derived-evidence/derived-evidence/evidence-decision/B.json`
