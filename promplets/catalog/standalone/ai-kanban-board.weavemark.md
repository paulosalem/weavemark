@promplet version: 0.7

@refine module:weavemark.domains.programming.foundations.software_spec
@refine module:weavemark.domains.programming.stacks.browser_static_esmodules
@refine module:weavemark.domains.programming.types.browser_folder_backed_webapp
@refine module:weavemark.domains.programming.modules.browser_sqlite_file_store
@refine module:weavemark.domains.programming.modules.browser_agent_workspace_coordination
@refine module:weavemark.domains.programming.modules.workflow_board
@refine module:weavemark.domains.programming.modules.card
@refine module:weavemark.domains.programming.modules.execution_turns
@refine module:weavemark.domains.programming.modules.human_agent_decision_loop
@refine module:weavemark.domains.programming.modules.activity_stream
@refine module:weavemark.domains.programming.modules.output_surfaces
@refine module:weavemark.domains.programming.modules.browser_ai_handoff
@refine module:weavemark.domains.research.recurring_topic_monitor

# AI Kanban — Browser Workspace for Human-AI Work

This implementation-ready specification defines a polished static JavaScript application for GitHub Pages with no backend.

## Product
AI Kanban is a local, folder-backed board where cards are active workspaces for
human-AI collaboration. A user opens or creates a Board Workspace folder. Its
`board.sqlite`, manifest, artifacts, attachments, and private coordination files
form one portable workspace, agent working directory, and local trust boundary.
The useful core does not require an AI provider. Users can organize work, edit
plans, preserve activity, capture outputs, and use versioned handoff packets.
A provider-neutral Python skill lets Copilot CLI, Claude Code, and similar agents
read and update the same workspace directly without a backend.

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
- task, question, or result presentation with human/AI attention state;
- immutable execution turns and a checklist plan with explicit states;
- typed text, status, link, program, table, diff, image, and file surfaces;
- append-only human, AI, movement, output, and error activity;
- dated/versioned output history, research memory, dependencies, relative artifact
  paths, provenance, and last-change actor.

Moving or reordering a card and appending its activity event is one SQLite
transaction. Moving completed work back to Inbox confirms Run again and creates a
new queued turn without changing prior turns. Cards last changed by an agent carry
a calm, accessible cue until reviewed.

## Essential flows
- First run: Open Board Workspace, Create Board Workspace, or Try demo without
  misleading durability or permission language. Try demo opens exactly two
  explicit choices. Visually prefer Create a real demo workspace: invoke the same
  folder picker and safety checks as normal creation, create the complete
  folder-backed Board Workspace and agent bootstrap, and immediately seed it with
  the Personal Research demo so compatible agents started there can interact at
  once. The secondary Try in memory path creates no folder and must state before
  activation that local agents cannot read or update it and that export is
  required to retain changes. When folder access is unsupported, keep the
  in-memory choice available and explain why durable demo creation is disabled.
- Quick start: both demo paths instantly load the same bundled Personal Research
  board with recurring cards for a macroeconomic pulse, things to do with a
  four-year-old in São Paulo, family trips, a collaborative vacation planner, and
  age-appropriate activities.
- Vacation loop: the human edits candidate destinations and constraints in Inbox;
  Planning runs broad AI comparison and feedback rounds. A confirmed move to In
  Progress queues deep research of the chosen destination and dated itineraries;
  Review presents the result for revision or acceptance.
- Active workspace: show folder/permission/save status, board search, attention
  filters, New card, Save, agent control, AI handoff, and Close workspace.
- Card detail: edit metadata and description, manage plan items and outputs,
  inspect turns, memory, history, activity, and provenance, reply to agent
  questions, Run again, archive, and publish polished result cards.
- Agent startup: create `AGENTS.md`, `CLAUDE.md`, and a canonical
  `.agents/skills/ai-kanban/` bundle in every workspace. After create or reopen,
  tell the user to start Copilot CLI or Claude Code in that folder and confirm its
  heartbeat before presenting it as connected.
- Continuous work: generated instructions tell the agent to poll, claim, work,
  yield, and resume watching indefinitely while its host remains alive. State
  plainly that a skill cannot force a terminated host runtime to act.
- Agent turns read prior reports and memory, highlight new or materially changed
  facts, use the single-writer baton, and preserve copy/import handoff as fallback.
- Reconnection: remember the recent file handle, request permission from a user
  gesture, detect external changes, and never overwrite a conflict silently.
- Compatibility: connected folder autosave on supporting Chromium browsers;
  explicit workspace archive import/download fallback elsewhere.

## Experience
The board should feel calm, capable, and trustworthy rather than like an
operations console. Keep raw database details behind an About workspace panel.
Use restrained navy, mineral teal, warm paper, and coral attention accents.
Use violet/teal for unreviewed AI changes and amber for Needs you, always with
icons and text rather than color alone. Prioritize readable cards, obvious save
and control state, useful empty columns, strong keyboard focus, reduced motion,
and responsive desktop/mobile layouts.

Make global actions state-aware: show Open/Create before activation, then
Save/New card/Agent control/Workspace menu. Foreground Needs you, AI working, and
AI updated counts without adding an operations console or global chat pane. Give
the latest result a rich preview and keep every older dated version one action away.

Add a quiet footer linking the source promplet, compiled implementation
specification, and public tutorial so the live result remains traceable to the
intent and generation path that produced it.

## Deliverable
Produce a complete static implementation under
`outputs/implementations/ai-kanban-browser/`, including vendored SQLite WASM,
worker/repository modules, the dependency-free Python skill and launchers, a sample
Board Workspace and browser templates for its root agent instructions,
documentation, deterministic tests, and a GitHub Pages live-demo entry.

@structural_constraints strict: true
  The specification MUST contain exactly these sections in order:
  1. Architecture and Board Workspace lifecycle
  2. SQLite schema and repository operations
  3. Human-agent coordination and skill protocol
  4. Cards, decision loops, execution turns, memory, and output surfaces
  5. Interface states and interactions
  6. Security, compatibility, and recovery
  7. File tree, implementation sequence, and test matrix
