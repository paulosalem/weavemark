@promplet version: 0.7

@module weavemark.domains.programming.modules.snap_card_feed

# Module: Snap Card Feed

Use this module for a focused, single-card-at-a-time browsing surface where each
item should receive meaningful attention rather than appear in a dense list.

## Feed contract

- Present one primary card per viewport with stable previous/next continuity.
- Use CSS scroll snap or an equivalent native-feeling mechanism. Scrolling MUST
  remain responsive, interruptible, and free from scroll traps.
- Use one vertical scroll owner. When the feed is the primary page experience,
  the document/main window MUST scroll and each card MUST expand to its full
  content; do not nest the card inside an internally scrolling feed or card pane.
- Support touch scroll, wheel/trackpad, Page Up/Down, arrow keys, and explicit
  Previous/Next controls. Preserve normal browser back behavior.
- Deep-link the active item when useful and restore the user's last position
  without unexpectedly jumping after content loads.
- Virtualize or incrementally render long feeds while keeping the active card and
  immediate neighbors stable and accessible.
- When snapping settles, update the active item, deep link, header, and progress
  exactly once. Re-rendering an action or note MUST NOT count as another view.

## Selection and ordering

- Define a deterministic, testable ranking policy with an optional seed. Persist
  enough state to reconstruct the session order.
- Avoid accidental immediate repetition. If an item returns for review, label why
  it returned and present a deeper or recall-oriented treatment.
- Allow an explicit ordered mode in addition to an adaptive or shuffled mode.
- Never let engagement metrics silently override the refining product's declared
  quality, safety, or learning objective.

## Card actions

- Keep frequent actions reachable without covering the primary content.
- Actions MUST expose selected state, accessible names, success/failure feedback,
  persistence behavior, and undo where appropriate.
- Notes or comments MUST preserve drafts when the keyboard, sheet, route, or app
  closes unexpectedly.
- Do not trigger an action merely because scrolling crossed a threshold; distinguish
  viewed, engaged, completed, and intentionally dismissed states.
- Serialize overlapping local mutations for one item so rapid Like, Save, Revisit,
  note, or understanding actions cannot overwrite one another.
- Sticky or fixed action and navigation trays MUST reserve layout space and remain
  non-overlapping at the smallest supported viewport.

## Attention safeguards

- Show progress and elapsed session time without interrupting every card.
- Offer a natural stopping point after a configurable interval or completed set.
  Continuing is a conscious action, not an obstructed default.
- Avoid autoplay media, fake social proof, infinite loading spinners, manipulative
  streak loss, or notification prompts unrelated to the user's goal.

## Acceptance

Test rapid direction changes, momentum scrolling, accidental taps, action-state
persistence, note drafts, restored position, assistive technology, reduced motion,
and feeds large enough to activate incremental rendering.
