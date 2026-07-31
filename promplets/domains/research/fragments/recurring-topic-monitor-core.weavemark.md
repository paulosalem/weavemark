@promplet version: 0.7

@module weavemark.domains.research.recurring_topic_monitor

# Recurring Topic Monitor Core

@note
  Reusable research layer for a topic monitor that can be run every day, week,
  month, or custom interval to find what is new, relevant, and worth acting on.

Use this layer when the user wants a repeated scan of a topic rather than a
one-time explainer.

## Monitoring obligations

- Treat each run as a dated monitoring cycle with a clear lookback window.
- Separate genuinely new developments from background context, evergreen
  references, recycled commentary, and duplicate coverage.
- Prefer items that changed within the requested window.
- Track why each item matters to the user, not only why it appeared in search.
- Distinguish confirmed facts, reported claims, announcements, opinions,
  forecasts, and speculation.
- Include enough source detail that a future run can compare what changed.
- Record omissions and monitoring gaps, especially when search or crawl access
  is partial.

## Persistent research memory

- Before each monitoring cycle, read prior reports and a durable, inspectable
  memory scoped to the recurring topic. Never rely on hidden model-session memory
  as the record of what the user has already seen.
- Memory items SHOULD record a stable fingerprint, normalized subject, concise
  claim or event summary, source URL and publisher, evidence date, first-seen and
  last-seen cycles, content hash, relevance, and `current`, `updated`,
  `superseded`, `dismissed`, or `uncertain` state.
- Maintain a source and coverage ledger so later cycles know which source families,
  searches, dates, and access gaps were already examined.
- Classify findings against memory as new, materially updated, unchanged context,
  duplicate coverage, corrected, or no longer current. Cite the previous cycle or
  memory item when describing a change.
- Avoid repetition, not continuity: repeat older information when needed to
  understand a material update, but label it as retained context and explain the
  delta. Never suppress corrections or new evidence because a topic fingerprint
  already exists.
- Update memory only from committed, source-backed results. Preserve lineage from
  each memory change to the cycle, output, and evidence that caused it.
- Let users inspect, search, correct, dismiss, pin, export, and explicitly forget
  memory. Forgetting removes future comparison context but MUST NOT silently alter
  immutable historical reports.

## Required monitor output

When useful, include:

| Field | Content |
| --- | --- |
| Run date | Date or timestamp of the monitoring run. |
| Cadence | daily / weekly / monthly / custom |
| Lookback window | What period was searched. |
| Topic | The exact topic monitored. |
| Mode | news / events |
| New since last run | Items likely new in this window. |
| Still important | Older context that remains decision-relevant. |
| Source coverage | Source families searched and crawled. |
| Gaps | What the monitor could not verify. |

Every completed cycle remains available as a dated, versioned report. Present the
latest successful report prominently with its recency and a preview, while keeping
all earlier cycles in chronological history for opening and comparison.
