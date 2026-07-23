@promplet version: 0.7

@module weavemark.domains.programming.types.mobile_first_webapp

# Software Type: Mobile-First Web Application

Use this type when the primary experience must feel natural on a phone while
remaining complete on tablets and desktop browsers.

## Product surface

- Design from a 320 CSS-pixel viewport outward. Desktop layouts MAY add context,
  columns, and shortcuts, but MUST NOT contain capabilities unavailable on mobile.
- Keep the primary task reachable with one thumb. Put frequent actions near the
  lower-middle interaction zone without colliding with browser or OS chrome.
- Respect safe-area insets, dynamic viewport units, virtual keyboards, orientation
  changes, and standalone installed-display mode.
- Prefer progressive disclosure over dense dashboards. Preserve context when a
  sheet, dialog, keyboard, or detail view opens and closes.
- Primary reading content SHOULD use the document as its single vertical scroll
  owner. Avoid nested vertical scroll panes that trap touch gestures or clip
  headings, content, and reachable controls.

## Navigation and interaction

- Use a small, stable information architecture. Primary navigation MUST remain
  understandable without hover, right-click, or precision pointing.
- Touch targets MUST be at least 44 by 44 CSS pixels with adequate spacing.
- Every gesture MUST have an obvious control alternative and keyboard equivalent.
  Never make swipe, long-press, pinch, or drag the only way to complete an action.
- Preserve scroll position, selected item, unfinished input, and focus across
  navigation, rotation, backgrounding, and reload when appropriate.
- Avoid accidental destructive actions near common scrolling gestures. Require
  confirmation or undo for consequential changes.

## Performance and resilience

- Render meaningful first content quickly on a mid-range phone and a constrained
  network. Define measurable budgets for initial JavaScript, CSS, images, and
  time-to-interactive.
- Lazy-load nonessential media and later content without layout shift. Reserve
  dimensions and provide useful placeholders.
- Core reading, navigation, and local edits SHOULD continue offline after the
  static application and required content have loaded.
- Test touch scrolling, virtual-keyboard input, reduced motion, text zoom, screen
  readers, offline reload, and widths from 320 CSS pixels through desktop.

## Attention and wellbeing

- Engagement MUST serve the product outcome rather than obscure elapsed time.
- Do not use fake urgency, deceptive notifications, shame, loss-framed streaks,
  forced sharing, or randomized rewards unrelated to user value.
- Make session time, progress, pause, and exit controls easy to find. Respect
  reduced-motion and user-selected session limits.
