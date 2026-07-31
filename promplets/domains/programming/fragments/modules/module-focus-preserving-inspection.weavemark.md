@promplet version: 0.7

@module weavemark.domains.programming.modules.focus_preserving_inspection

# Module: Focus-Preserving Inspection

@note
  Reusable interaction layer for collections, canvases, galleries, games,
  dashboards, maps, and workspaces where users inspect one item while retaining
  spatial awareness of the surrounding set.

Use this module when item details, generated explanations, or final synthesis
must appear without navigating away from the collection or forcing avoidable
scroll jumps.

## Entity-owned progressive disclosure

- Each inspectable entity owns a compact semantic disclosure for its durable
  details. The disclosure heading stays near its entity, is absent or disabled
  until meaningful content exists, and is collapsed by default unless the user
  explicitly left it open.
- Opening one disclosure MUST NOT automatically close unrelated disclosures
  unless density or exclusivity is an explicit product rule.
- Disclosure state changes do not navigate, replace the entity, steal focus from
  editable content, or auto-scroll. Native `<details>` / `<summary>` is preferred
  when its semantics fit.
- Details render untrusted or generated values as data, never executable markup.
  Pending, complete, failed, stale, and retryable states remain distinguishable.

## Anchored contextual inspection

- Selecting an entity preserves it in its original spatial position and keeps it
  visually readable. Present contextual detail by using the space occupied by
  sibling entities, a bounded overlay, or an adjacent adaptive region rather than
  moving the selected entity into an unrelated page.
- The surrounding set MAY dim, soften, or become covered, but its geometry remains
  stable enough that users understand where the selected entity belongs.
- A contextual overlay MUST fit its intended viewport without increasing document
  height or triggering automatic scrolling. It provides Close/Collapse actions,
  a clear title, and an accessible relationship to the selected entity.
- While modal, prevent sibling and background activation, manage focus, support
  Escape, and restore focus to the selected entity on close. If nonmodal, provide
  equivalent keyboard reachability without trapping focus.
- Re-selecting another entity updates the anchored detail in place without
  flashing the collection or leaving stale asynchronous content visible.

## Asynchronous inspection state

- Long-running inspection or explanation keeps the selected entity visible and
  marks work locally around it. Use restrained progress cues tied to that entity,
  never a global blocking loader when the collection remains usable.
- Completion MUST NOT auto-open large detail, move focus, scroll the page, or
  navigate. Announce readiness accessibly and let the user choose when to inspect.
- Cancellation, retry, replacement, and stale-result suppression are explicit.
  Results from an old selection or workspace generation MUST NOT mutate the
  current inspection.
- Reduced motion replaces traveling, pulsing, or morphing indicators with a
  static high-contrast pending treatment.

## Focus layout for synthesis

- When users explicitly request aggregate explanation or synthesis, the
  collection MAY enter a focus layout: preserve every entity while reducing its
  visual footprint enough to make the aggregate detail visible in the same
  viewport where practical.
- Entering focus layout is an explicit action, not an automatic consequence of
  collection completion. Keep a visible path back to the normal collection.
- Provide an explicit Restore action for keyboard, touch, reduced-motion,
  assistive-technology, and short-page users.
- A scroll-linked restoration MAY gradually return entities to normal size as the
  user scrolls upward, while the aggregate detail settles into normal document
  flow below. Treat this as progressive enhancement: use bounded progress,
  requestAnimationFrame or native scroll timelines where appropriate, no layout
  thrashing, and no reversal that surprises ordinary downward reading.
- At full restoration, preserve the aggregate result below the collection rather
  than hiding or discarding it.

## Responsive and accessibility contract

- Maintain spatial relationships on wide screens and a comprehensible ordered
  sequence on narrow screens. Do not require horizontal page scrolling.
- Entity selection, disclosures, overlays, focus layout, and restoration all have
  keyboard and touch paths, visible focus, meaningful names, status
  announcements, and 44 CSS-pixel targets.
- Respect reduced motion, high contrast, forced colors, 200% zoom, dynamic
  viewport changes, focus loss, and backgrounding.
- Tests cover selection, disclosure, asynchronous completion, close/reopen,
  retry/cancel, stale result suppression, focus restoration, compact synthesis,
  explicit restoration, scroll enhancement, and narrow viewports.

## Acceptance criteria

Inspection is complete when users can understand one entity and an aggregate
result without losing the collection's spatial context; no completion causes
navigation or scroll jumps; durable details remain progressively disclosed;
pending and failure states are local and recoverable; and focus-layout
restoration is both beautiful and fully optional.

