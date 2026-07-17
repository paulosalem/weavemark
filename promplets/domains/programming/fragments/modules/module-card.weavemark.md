@promplet version: 0.7

@module weavemark.domains.programming.modules.card

# UI Primitive: Card

@note
  Reusable programming module for card-shaped interface units. A card is a
  compact, self-contained presentation and interaction container. Cards can
  summarize people, products, records, tasks, alerts, media, metrics, artifacts,
  recommendations, or any other bounded unit of information.

Use this module whenever an application presents repeated, well-formatted
information units that need a consistent data model, visual hierarchy, and
interaction contract.

## Card semantics

- A card MUST have a clear purpose: summary, selection, navigation, action,
  monitoring, comparison, preview, or status display.
- The domain meaning of a card MUST be supplied by the refining spec. Do not
  assume that every card represents a task, ticket, or workflow object.
- Cards SHOULD be scannable at rest and reveal deeper detail through expansion,
  navigation, or a detail panel.
- Cards MAY be static summaries, interactive controls, draggable objects,
  editable containers, or live updating views.

## Card data model

Define a card schema with the fields that apply:

- `id`: stable unique identifier.
- `kind` or `type`: semantic card category when multiple card families share one
  surface.
- `title`: short primary label.
- `subtitle` or `summary`: optional secondary label.
- `body`: primary content, supporting rich text or structured rendering when
  needed.
- `media`: optional icon, thumbnail, avatar, chart, image, or preview.
- `badges`: compact labels for priority, state, category, source, risk, or other
  domain-specific metadata.
- `metadata`: structured key-value attributes shown in a sidebar, footer, tooltip,
  or detail view.
- `actions`: explicit operations available from the card.
- `links`: related records, parent/child relationships, dependencies, references,
  or navigation targets.
- `state`: UI state such as selected, focused, expanded, disabled, loading, error,
  stale, or unread.
- `timestamps`: created, updated, seen, due, archived, or other temporal fields
  only when meaningful for the domain.

## Layout and presentation

- Establish visual hierarchy: title first, then the highest-value summary,
  metadata, and actions.
- Keep density appropriate to the use case: summary cards should be compact;
  operational cards may expose richer controls.
- Provide empty, loading, error, stale, and permission-limited states.
- Support responsive behavior: cards MUST remain legible in narrow columns,
  dense grids, and detail panes.
- Avoid visual noise. Use borders, shadows, color, badges, and icons only when
  they clarify grouping, status, or action.

## Interaction contract

- Cards with primary actions MUST expose both pointer and keyboard access.
- Click, double-click, drag, context menu, checkbox selection, and inline editing
  behaviors MUST be unambiguous and should not conflict.
- If cards are selectable or draggable, define focus styles, selection affordance,
  drag preview, drop targets, and cancellation behavior.
- If cards can expand, pin, archive, dismiss, or reorder, define persistence and
  undo behavior.
- Accessibility MUST include semantic labels, visible focus, sufficient contrast,
  and screen-reader text for icon-only controls.

## Specialization guidance

When refining this module:

- Add domain fields in the specific spec rather than overloading generic card
  fields.
- State whether cards are informational, operational, navigational, or mixed.
- Define which fields are required at creation and which can be computed.
- Define the relationship between compact card view and full detail view.
- Define card lifecycle only if the domain has one.
