@promplet version: 0.7

@refine module:weavemark.domains.programming.foundations.base_spec_author
@refine module:weavemark.domains.programming.stacks.browser_static_esmodules
@refine module:weavemark.domains.programming.types.browser_file_backed_webapp
@refine module:weavemark.domains.programming.modules.browser_sqlite_file_store
@refine module:weavemark.domains.programming.modules.workflow_board
@refine module:weavemark.domains.programming.modules.card
@refine module:weavemark.domains.programming.modules.activity_stream
@refine module:weavemark.domains.programming.modules.output_surfaces
@refine module:weavemark.domains.programming.modules.browser_ai_handoff

# AI Kanban — Browser Workspace for Human-AI Work

Write an implementation-ready specification for a polished static JavaScript
application that runs directly from GitHub Pages with no backend.

## Product

AI Kanban is a local, file-backed board where cards are active workspaces for
human-AI collaboration. A user opens an existing `.aikanban.sqlite` file or
authorizes a new one; that selected file is the canonical board state.

The useful core does not require an AI provider. Users can organize work, edit
plans, preserve activity, capture outputs, and exchange versioned handoff packets
with any assistant. Direct provider integration is an optional adapter.

## Board

Use these ordered default columns:

1. Inbox
2. Planning
3. In Progress
4. Review
5. Blocked
6. Done

Users can create, edit, archive, search, filter, reorder, and move cards with
pointer and keyboard controls. Each card includes:

- title, Markdown description, priority P0-P3, assignee, and timestamps;
- a checklist plan with pending, running, done, and failed states;
- typed text, status, link, program, and table output surfaces;
- append-only human, AI, movement, output, and error activity;
- dependencies on other cards.

Moving or reordering a card and appending its activity event is one SQLite
transaction. Column/card order remains stable after save and reopen.

## Essential flows

- First run: Open board, Create board, or Try demo without misleading durability.
- Active workspace: show file/permission/save status, board search, filters, New
  card, Save, Save As, AI handoff, and Close workspace.
- Card detail: edit metadata and description, manage plan items and outputs,
  inspect activity, move with keyboard-accessible controls, archive, export
  handoff, and preview/import an AI response packet.
- Reconnection: remember the recent file handle, request permission from a user
  gesture, detect external changes, and never overwrite a conflict silently.
- Compatibility: connected autosave on supporting Chromium browsers;
  import/download fallback elsewhere.

## Experience

The board should feel calm, capable, and trustworthy rather than like an
operations console. Keep raw database details behind an About workspace panel.
Use restrained navy, mineral teal, warm paper, and coral attention accents.
Prioritize readable cards, obvious save state, useful empty columns, strong
keyboard focus, reduced motion, and responsive desktop/mobile layouts.

Make global actions state-aware: show Open/Create before a workspace is active,
then Save/New card/Workspace menu after activation. In long card workspaces, keep
Cancel and Save reachable while plan, output, and activity sections scroll.

## Deliverable

Produce a complete static implementation under
`outputs/implementations/ai-kanban-browser/`, including vendored SQLite WASM,
worker/repository modules, sample data, documentation, deterministic tests, and a
GitHub Pages live-demo entry.

@output enforce: strict
  Return an implementation specification with exactly these sections:
  1. Architecture and file lifecycle
  2. SQLite schema and repository operations
  3. Domain behavior and AI handoff protocol
  4. Interface states and interactions
  5. Security, compatibility, and recovery
  6. File tree and implementation sequence
  7. Test and acceptance matrix
