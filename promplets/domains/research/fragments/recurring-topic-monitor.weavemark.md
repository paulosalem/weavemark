@promplet version: 0.7

@module weavemark.domains.research.recurring_topic_monitor

# Recurring Topic Monitor

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
