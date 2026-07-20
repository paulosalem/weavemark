@promplet version: 0.7

@refine module:weavemark.domains.programming.foundations.base_spec_author mingle: true
@refine module:weavemark.domains.programming.stacks.typescript_nextjs_prisma_sqlite mingle: true
@refine module:weavemark.domains.programming.types.local_first_webapp mingle: true
@refine module:weavemark.domains.programming.modules.workflow_board mingle: true
@refine module:weavemark.domains.programming.modules.card mingle: true
@refine module:weavemark.domains.programming.modules.activity_stream mingle: true
@refine module:weavemark.domains.programming.modules.context_attachments mingle: true
@refine module:weavemark.domains.programming.modules.output_surfaces mingle: true
@refine module:weavemark.domains.programming.modules.local_sqlite_storage mingle: true
@refine module:weavemark.domains.programming.modules.dashboard mingle: true
@refine module:weavemark.domains.programming.modules.ai_features mingle: true
@refine module:weavemark.domains.programming.modules.notifications mingle: true
@refine module:weavemark.domains.programming.modules.realtime mingle: true
@refine module:weavemark.domains.programming.modules.rest_api mingle: true
@refine module:weavemark.domains.work_intelligence.topic_intelligence_monitor mingle: true
@refine module:weavemark.domains.research.news_quality mingle: true
@refine module:weavemark.std.guidelines.evidence_quality mingle: true

# News Intelligence Board

Design **@{app_name}**, a local-first news and events intelligence board for
people who need a high-signal view of changing topics without repeatedly seeing
the same story.

## Monitoring brief

- Topics: @{monitored_topics}
- Event types worth surfacing: @{event_types}
- Regions or jurisdictions: @{regions}
- Refresh cadence: @{refresh_cadence}
- Search lookback: @{lookback_window}
- Memory retention: @{memory_retention}
- Audience and decision context: @{audience_context}

The app searches configured public web/news providers on schedule and on demand.
It stores durable source and event memory locally. A new document is not a new
card merely because its title, publisher, or URL differs.

## Core model: sources, events, and presentations

Keep three concepts separate:

1. **Source document** — one fetched article, release, filing, bulletin, or event
   page with canonical URL, publisher, publication/update time, content hash,
   extracted entities, claims, and retrieval metadata.
2. **Event cluster** — the underlying real-world development represented by one
   or more source documents. Store event type, entities, location, time window,
   current status, material facts, uncertainty, and source-family coverage.
3. **Presentation history** — when and why the event was shown, dismissed,
   followed, muted, or resurfaced for the user.

Never infer “unseen” from browser state. SQLite is authoritative for source
fingerprints, event clusters, user decisions, and presentation history.

## Ingestion and memory pipeline

For each scheduled or manual refresh:

1. Build searches from the monitored topics, wanted event types, regions, and
   lookback window.
2. Fetch result metadata, then crawl only candidates that pass deterministic
   domain, date, and URL filters.
3. Canonicalize URLs; remove tracking parameters; hash normalized content.
4. Extract candidate event type, entities, action/change, location, effective
   date, claims, and source evidence.
5. Compare against source memory and event memory.
6. Store the source document even when it is not shown, with a reason code.
7. Create, update, suppress, or resurface an event cluster according to the rules
   below.

Use exact URL/content hashes and deterministic entity/date keys before semantic
similarity. The model may judge whether two documents describe the same event or
whether an update is material only after deterministic checks leave ambiguity.

## Repeat and resurface policy

Classify each candidate as exactly one of:

- **Exact duplicate:** same canonical URL or content hash. Attach retrieval
  metadata to the existing source; never show again.
- **Syndicated/near duplicate:** materially the same facts from another outlet.
  Add source coverage to the existing event; do not create a new card.
- **Same event, no material change:** wording or commentary changed, but status,
  decisive facts, or actionability did not. Append the source silently.
- **Material update:** a new confirmed fact, official action, corrected number,
  changed status, changed date/location, meaningful consequence, or new evidence
  that changes confidence or actionability. Update and resurface the existing
  event card with a visible “What changed” diff.
- **New event:** no existing cluster represents the development. Create a card.
- **Uncertain match:** hold in Needs Review; do not guess or notify.

An event the user dismissed MAY resurface only for a material update. A muted
topic/event type MUST remain suppressed until its mute expires or the user
changes it. Every suppression and resurface decision records the rule, evidence,
model judgment if any, and timestamp.

## Board and card experience

Use a workflow board with these default views:

- **New signal** — unseen event clusters that passed the display policy.
- **Following** — events the user wants updated.
- **Needs review** — uncertain clustering, weak evidence, or conflicting sources.
- **Read later** — intentionally deferred items.
- **Dismissed** — hidden from normal views but retained for memory/deduplication.
- **Archived** — closed or stale events beyond the active horizon.

Each event card MUST show:

- concise event statement and event type;
- why it matters to @{audience_context};
- current status, confidence, freshness, and region;
- source-family count and strongest primary/official source;
- first-seen and last-material-change timestamps;
- “What changed” since the previous presentation;
- actions: follow, read later, dismiss, mute topic/type, inspect evidence.

Use context attachments for source documents and typed output surfaces for the
summary, evidence table, timeline, claim comparison, and change diff. The
activity stream records ingestion, clustering, corrections, user decisions,
notifications, and resurface events.

## Dashboard

The quiet dashboard answers:

- What is being monitored?
- When did each monitor last complete?
- When is the next refresh?
- How many new events, material updates, suppressed duplicates, uncertain
  matches, and failed sources were found?
- Which followed events changed?

Do not foreground raw crawl volume. Foreground signal, attention, freshness, and
failed coverage that affects trust.

## Search/runtime boundary

- Provider credentials and model selection are host configuration, never stored
  as ordinary promplet variables or exposed in the UI.
- Search/crawl requests are bounded by per-refresh query, result, page, time, and
  cost budgets.
- Respect robots/provider terms and retain source URLs, timestamps, and retrieval
  outcomes.
- A failed provider or partial crawl produces a visible partial-coverage state;
  it does not make the refresh appear successful.
- The core application remains usable offline for browsing memory, decisions,
  evidence, and prior refresh reports.

## Notifications

Notify only for a new event or material update that matches the user's event-type
and importance policy. Notifications identify the event, what changed, why it
passed the threshold, and link to the existing card. Never notify once per
article.

## Testing and evaluation

Include deterministic fixtures for:

- exact URL duplicates and tracking-parameter variants;
- copied/syndicated articles;
- same event with no material change;
- official confirmation after an initial report;
- corrected numbers or dates;
- conflicting sources and uncertain clustering;
- dismissed and muted events;
- expired memory and retention boundaries;
- provider outage, partial crawl, and offline browsing;
- restart persistence, migration, backup/restore, and duplicate ingestion races.

Evaluate clustering and resurface quality on a labeled event corpus. Report
false new-event and missed-material-update rates separately; do not collapse
them into one accuracy score.

@output enforce: strict
  Return:
  1. Product promise and user jobs
  2. System architecture and bounded search pipeline
  3. SQLite data model and migration strategy
  4. Event clustering, memory, suppression, and resurface rules
  5. Board, card, dashboard, evidence, and quiet/error/offline states
  6. API and background refresh contracts
  7. AI judgment schemas, evidence, budgets, and human review
  8. Notification policy
  9. Security, privacy, source, and provider boundaries
  10. Testing, labeled evaluation, and acceptance criteria

@assert contains: "material update"
@assert contains: "presentation history"
@assert contains: "What changed"
@assert contains: "false new-event"
