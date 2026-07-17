@promplet version: 0.7

@module weavemark.domains.programming.modules.workflow_board

# Module: Workflow Board

@note
  Reusable programming module for board-style interfaces that arrange cards or
  records into columns, lanes, groups, timelines, or other progress/status
  layouts.

Use this module for Kanban boards, review queues, editorial pipelines, CRM
funnels, moderation queues, sprint boards, project planners, triage surfaces, and
other interfaces where users scan many cards across meaningful stages or groups.

## Board structure

- A board MUST define its unit type: cards, records, artifacts, alerts, leads,
  cases, jobs, or another domain object.
- A board MUST define its grouping model: columns, swimlanes, sections, timeline
  bands, priority groups, owner groups, or saved filters.
- Columns or groups MUST have stable identifiers, display names, ordering, and
  optional descriptions.
- Boards SHOULD support both a default system-defined layout and user or team
  customization when the product needs it.
- Empty columns and empty boards MUST have useful states and creation or filter
  recovery actions.

## Movement and transitions

- If items move between groups, define allowed transitions, validation rules, and
  side effects.
- Drag-and-drop MUST have accessible keyboard alternatives.
- Reordering within a group MUST define persistence, conflict handling, and
  optimistic-update rollback behavior.
- Transitions MAY trigger hooks such as assignment, notification, automation,
  review, approval, archive, or escalation.
- If movement is not allowed for some items, the reason MUST be visible at the
  point of interaction.

## Board operations

- Provide create, view, edit, duplicate, archive/delete, search, filter, sort,
  and bulk-selection behavior when the domain calls for them.
- Define saved views and filters if users need repeated board perspectives.
- Support quick scanning with counts, WIP indicators, overdue indicators, blocked
  indicators, or aggregate metrics as appropriate.
- Board-level dashboards SHOULD summarize flow, throughput, bottlenecks, aging,
  ownership, and attention needs when those metrics change user decisions.

## Collaboration and persistence

- Define how simultaneous edits and movements are resolved.
- Real-time boards SHOULD broadcast item movement, content updates, comments,
  and presence changes.
- Board state MUST persist consistently across refreshes, sessions, and devices
  according to the product scope.
- Activity history SHOULD explain who changed what, when, and why when the board
  coordinates shared work.

## Acceptance criteria

A workflow board is complete when a user can understand the grouping model,
create or import items, move or update them according to the rules, recover from
invalid moves, filter to the items they need, and trust that visible board state
matches persisted state.
