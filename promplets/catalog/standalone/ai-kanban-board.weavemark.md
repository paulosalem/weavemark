@promplet version: 0.7


# AI Kanban — Task Board for Human-AI Collaboration

@refine module:weavemark.domains.programming.foundations.base_spec_author
@refine module:weavemark.domains.programming.stacks.typescript_nextjs_prisma_sqlite
@refine module:weavemark.domains.programming.types.local_first_webapp

Write this implementation specification for a senior full-stack developer:
be precise, implementation-ready, and interaction-design-conscious.

## Product Vision

AI Kanban is a **task board designed for human-AI collaboration**. Unlike
traditional Kanban boards where humans do all the work, here the user defines
tasks for an AI agent system to execute. Cards are not passive sticky notes —
they are **live workspaces** where the AI streams progress, surfaces outputs,
and the user steers direction in real time.

The key insight: AI work is not linear. An AI might explore 3 approaches in
parallel, produce intermediate artifacts, encounter ambiguities that need human
input, and generate outputs in multiple formats simultaneously. The board must
make all of this visible and navigable.

## Board Architecture

@refine module:weavemark.domains.programming.modules.workflow_board

The board specializes the reusable workflow-board and card modules: in this
application, cards represent live AI workspaces, but the card implementation must
remain general enough to render other card kinds later.

### Columns (Default Pipeline)
- **Inbox**: user drafts tasks (plain language or structured).
- **Planning**: AI decomposes task into sub-steps, estimates complexity, identifies needed tools/data. User reviews and approves plan.
- **In Progress**: AI actively executing. Card shows live status.
- **Review**: AI finished. User reviews outputs, can request revisions.
- **Done**: accepted deliverables. Archived after 30 days.
- **Blocked**: AI encountered an issue requiring human input.

Users MAY create custom columns. Moving a card to a column triggers the
corresponding lifecycle hook (see Card Lifecycle below).

### AI Kanban Card Specialization

@refine module:weavemark.domains.programming.modules.card
@refine module:weavemark.domains.programming.modules.activity_stream
@refine module:weavemark.domains.programming.modules.context_attachments

Each AI Kanban card extends the generic card model with:
- **Header**: title, priority badge (P0–P3), assignee (AI agent name or "Unassigned").
- **Description**: markdown body with the user's intent. Supports `@mention` of other cards for dependencies.
- **AI Plan Panel**: collapsible section showing the AI's decomposition:
  sub-tasks as a checklist, each with status indicator (⏳ pending, 🔄 running, ✅ done, ❌ failed).
- **Output Surfaces**: typed surfaces for intermediate and final results.
- **Activity Stream**: chronological log of AI actions, user edits, status changes,
  questions, answers, and output updates. Filterable by: AI events, human events,
  errors only.
- **Context Attachments**: files, URLs, program snippets, or references to other cards
  that the AI should use as input.
- **Metadata sidebar**: created date, last updated, time in current column,
  estimated tokens used, cost estimate.

### Typed Output Surfaces — The Core Innovation

@refine module:weavemark.domains.programming.modules.output_surfaces

AI outputs are NOT buried in a single text block. Instead, each card has
multiple typed output surfaces that display results in purpose-built views:

@match output_surface_level
  "standard" ==>
    Required card surfaces:
    1. **Text**: rendered markdown for explanations, plans, and summaries.
    2. **Program**: syntax-highlighted program artifacts with language tag, copy
       button, and "Apply to file" action when repository integration exists.
    3. **Table**: structured data rendered as sortable/filterable rows.
    4. **Diff**: before/after comparison view.
    5. **Image**: generated images or diagrams.
    6. **Status**: key-value dashboard such as "Tests Passing: 47/50" or
       "Coverage: 82%".

  "advanced" ==>
    Required card surfaces:
    1. **Text** with collapsible sections for long outputs.
    2. **Program** with multi-file tabs, inline comments, and "Apply All".
    3. **Table** with column resize, CSV export, and chart-from-table.
    4. **Diff** with inline commenting and hunk approval.
    5. **Image** gallery with expand and side-by-side comparison modes.
    6. **Status** with sparklines and threshold coloring.
    7. **Canvas** for mind maps, architecture diagrams, and flowcharts.
    8. **Terminal** for build/test/run logs with ANSI color and pinned auto-scroll.
    9. **Form** for structured user decisions.

Each card can have multiple surfaces. Surfaces are ordered by the AI (most
important first) but the user can reorder, pin, minimize, or pop out into a
floating window.

### Board-Level Dashboards

Beyond individual cards, the board itself has **aggregate views**:

- **Progress Dashboard**: total cards by column (bar chart), throughput over time
  (cards completed per day), average time-in-column, cost tracker.
- **Surface Aggregator**: a single view that collects all Status surfaces across
  all In Progress cards into one unified dashboard. Filters by tag or agent.
- **Dependency Graph**: visual DAG of card dependencies (from `@mention` links).
  Highlights critical path and blocked chains.
- **Agent Activity**: which AI agents are working on what, their queue depth,
  recent errors, and token usage per agent.

## Local Storage & Persistence

@refine module:weavemark.domains.programming.modules.local_sqlite_storage

AI Kanban is a **local-first board**. Its authoritative state lives in a local
SQLite database, not in a hosted PostgreSQL service, remote SaaS backend, or
browser-only storage.

### Local Data Directory

- The app MUST use a configurable local data directory.
- Development default: `.local-data/ai-kanban.sqlite` relative to the project
  root.
- Packaged local app default: the OS user-data directory, with a visible setting
  showing the active path.
- The directory MUST contain:
  - `ai-kanban.sqlite`: canonical SQLite database.
  - `attachments/`: user-provided files and imported context.
  - `artifacts/`: AI-generated deliverables and intermediate outputs that are too
    large for relational rows.
  - `backups/`: timestamped database and workspace backups.
  - `exports/`: user-created portable workspace exports.

### Durable Entities

Persist at least these entities in SQLite:

- boards, columns, column ordering, and board settings.
- cards, card ordering, lifecycle state, dependencies, and metadata.
- output surfaces, surface versions, pinned/minimized state, and comments.
- activity events, questions, answers, human edits, AI events, and errors.
- context attachments with file metadata, content hash, MIME type, byte size, and
  relative path.
- agent definitions, local agent API keys as hashes, scopes, and revocation
  status.
- user preferences that must survive browser cache clearing.

### Consistency Rules

- Moving a card, creating an activity event, and updating derived dashboard state
  MUST be transactional when they describe one user-visible action.
- Activity events MUST be append-only except for explicit redaction metadata.
- Output surface revisions MUST keep version history so the user can compare or
  restore prior outputs.
- Card ordering MUST be stable across refreshes and restarts.
- Browser local storage MAY remember transient UI state such as expanded panels,
  but it MUST NOT be the source of truth for cards, surfaces, attachments, or
  events.
- Backup/restore and export/import MUST preserve the database and all referenced
  local files together.

## Card Lifecycle & AI Integration

@refine module:weavemark.domains.programming.modules.ai_features

### Lifecycle Hooks
When a card moves to a column, the system fires a hook:

| Column | Hook | AI Behavior |
|--------|------|-------------|
| Inbox | — | No AI action. User drafts. |
| Planning | `on_plan` | AI reads description + attachments, generates sub-task plan, estimates complexity. Creates AI Plan Panel. |
| In Progress | `on_start` | AI begins executing plan. Opens WebSocket channel for live updates. Creates output surfaces as needed. |
| Review | `on_review` | AI generates summary of what was done. Highlights decisions it made and any deviations from the plan. |
| Blocked | `on_block` | AI posts a Form surface with the specific question/decision it needs from the user. |
| Done | `on_complete` | AI archives intermediate artifacts. Final outputs pinned. |

### Real-Time Updates (WebSocket)

@refine module:weavemark.domains.programming.modules.realtime

- While a card is In Progress, the AI streams events via WebSocket:
  - `surface_update`: new content for an output surface (append or replace).
  - `subtask_status`: a sub-task changed status.
  - `attention_needed`: AI needs user input (auto-moves card to Blocked if no response in 5 min).
  - `progress`: percentage completion estimate.
- All events are also persisted to the Activity Stream.
- Client renders updates immediately — no polling.

### Parallel Execution
- A single card MAY have multiple sub-tasks running in parallel.
- Each sub-task gets its own output surface.
- The card's Status surface shows aggregate progress.
- If sub-tasks conflict (e.g., two approaches to the same problem), AI creates a
  Form surface asking the user to choose.

## AI Agent Protocol

### Agent Interface

@refine module:weavemark.domains.programming.modules.rest_api

- Agents connect via API: `POST /api/v1/cards/{id}/events` with event payloads.
- Authentication: per-agent local API keys with scoped permissions (read card,
  write surfaces, move columns). Store only hashed keys in SQLite.
- Do not add email/password accounts, OAuth, subscriptions, billing, tenants, or
  remote organization management unless a later spec explicitly requests them.
- Rate limit: 100 events/minute per card.

### Agent Types
@if multi_agent
  - **Planner**: decomposes tasks, no execution.
  - **Programmer**: writes and modifies programs. Outputs Program + Diff surfaces.
  - **Researcher**: searches web/docs, summarizes findings. Outputs Text + Table.
  - **Reviewer**: reviews outputs from other agents. Outputs Diff with comments.
  - **Orchestrator**: meta-agent that assigns sub-tasks to other agents and monitors progress.
  Agent assignment rules configurable per board (e.g., "all programming tasks go to Programmer agent").

## Keyboard & Power User Features

- `N`: new card in Inbox.
- `E`: edit current card description.
- `→` / `←`: move card to next/previous column.
- `/`: command palette (fuzzy search cards, actions, agents).
- `Ctrl+Shift+S`: toggle Surface Aggregator.
- Drag cards between columns. Drag to reorder within column.
- Card quick-filter: type to filter visible cards by title (instant, no submit).

@output "markdown"
  Structure the output as:
  1. Architecture Overview (system components, data flow)
  2. Local Storage & Persistence Model (SQLite file, data directory, migrations,
     backups, export/import, and transaction rules)
  3. Data Models (cards, surfaces, agents, events — full schemas)
  4. API Endpoints (card CRUD, surface management, agent events, board queries)
  5. WebSocket Protocol (all event types with JSON schemas)
  6. Frontend Pages (board view, card detail, dashboards — component breakdown)
  7. Agent Integration (protocol, local API keys, lifecycle)
  8. Testing Strategy

@assert contains: "Data Models (cards, surfaces, agents, events — full schemas)"
@assert contains: "WebSocket Protocol (all event types with JSON schemas)"
@assert contains: "Agent Integration (protocol, local API keys, lifecycle)"
@assert contains: "backups, export/import, and transaction rules"
