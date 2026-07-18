@promplet version: 0.7

@module weavemark.domains.programming.modules.dashboard

# Module: Decision-Oriented Dashboard

Use this module when a product must turn changing records, events, metrics, or
forecasts into a clear current answer and an inspectable path to evidence.
Domain specs supply the exact calculations, entities, thresholds, and actions.

## Information hierarchy

- Put the user's primary decision or status answer first: what matters now, why,
  confidence or freshness, and what could change it.
- Follow with exceptions and attention items, then trends and supporting detail.
- Keep assumptions, source timestamps, and calculation provenance near the values
  they affect.
- Distinguish observed, confirmed, inferred, projected, and stale values.
- Prefer a few decision-changing cards over a wall of vanity metrics.

## Dashboard states

- **Quiet:** show the current answer, what is being monitored, last successful
  refresh, and next scheduled refresh.
- **Attention:** foreground threshold crossings, material changes, failed checks,
  or records that need review.
- **Loading:** preserve the last valid result when possible and label its age;
  use skeletons only for content that has never loaded.
- **Partial failure:** keep healthy widgets usable and explain which source or
  calculation failed, the effect, and the retry path.
- **Empty:** explain what data or configuration is missing and offer the next
  useful action.
- **Offline:** show locally available evidence and the last sync state without
  pretending the data is current.

## Cards and widgets

- Every card MUST have a purpose, title, current state, freshness indicator, and
  a clear path to details.
- Status cards SHOULD pair a plain-language answer with the decisive value,
  threshold, or evidence.
- Timeline/calendar cards SHOULD distinguish expected events, confirmed events,
  missed events, and confidence.
- Scenario cards MAY compare conservative, expected, and optimistic assumptions
  when uncertainty changes the decision.
- Users MAY pin, hide, or reorder secondary cards; the primary answer and urgent
  attention items remain stable.
- Persist meaningful layout preferences without letting browser-only state become
  the source of truth for business data.

## Charts and tables

- Use a chart only when shape, trend, comparison, or distribution is easier to
  understand visually than in prose or a table.
- Every visualization MUST have an accessible text/table equivalent, descriptive
  labels, keyboard access, responsive sizing, and non-color-only distinctions.
- Tooltips MUST show exact values, units, time period, and source/freshness when
  relevant.
- Tables MUST support the filters and sorting needed for the user's actual
  decision; do not add generic bulk actions without a domain use case.
- Preserve active filters, selection, scroll, and focus across background
  refreshes.

## Interaction and explanation

- Let users inspect how a value was calculated and which evidence contributed.
- Let users change permitted assumptions inline and see the affected answer
  immediately, without silently persisting experimental values as canonical.
- Explain threshold changes and alerts in plain language before exposing advanced
  controls.
- Make destructive or high-impact actions explicit, reversible where practical,
  and attributable.
- Exports SHOULD include the visible answer, selected scope, assumptions,
  freshness, and source references.

## Responsive behavior

- Mobile: one primary answer, attention queue, and progressive disclosure.
- Tablet: primary answer plus the most important comparison or timeline.
- Desktop: multi-column overview with a dedicated detail surface.
- Compact layouts MUST not reduce critical labels to unexplained icons or hide
  active warnings.

## Acceptance criteria

A dashboard is complete when users can identify the current answer, understand
its freshness and evidence, find what needs attention, inspect why it changed,
recover from empty/error/offline states, and reach the relevant action without
reading raw implementation data.
