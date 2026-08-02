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
- First run: Open Board Workspace, Create Board Workspace, or Try demo. Try demo
  offers two explicit choices: visually prefer Create a real demo workspace,
  which uses normal folder checks, installs the agent bootstrap, and seeds the
  Personal Research board for immediate local-agent use. Try in memory creates no
  folder, disables local-agent integration, and requires export to retain changes.
  When folder access is unsupported, explain why only the in-memory path works.
  Open, Create, demo, reconnect, and import transitions are single-flight: disable
  competing entry actions until the current picker/activation finishes.
- Quick start: both paths load the same Personal Research board for a macroeconomic pulse,
  activities with a four-year-old in São Paulo, family trips, a collaborative vacation planner, and other age-appropriate activities.
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
  heartbeat before presenting it as connected. When several agent records exist,
  show the durable SQLite control holder rather than an unrelated newer heartbeat.
  Freeze the user-confirmed grant target and revalidate that exact actor/run after
  pending saves before transferring control.
- Continuous work: generated instructions tell the agent to poll, claim, work,
  yield, and resume watching indefinitely while its host remains alive. State
  plainly that a skill cannot force a terminated host runtime to act. Concurrent
  mutations fail fast with a typed busy result and require fresh preflight values.
  Announce/watch publication failures are typed; an exact post-commit retry with
  the same idempotency key republishes the durable coordination outbox.
- Agent turns read prior reports and memory, highlight new or materially changed
  facts, use the single-writer baton, and preserve copy/import handoff as fallback.
- Recovery: keep cooperative request-return primary. For a stale controlling
  agent, offer a copyable guarded recovery command bound to revision/generation
  only after the user confirms the old process is stopped; preserve partial work
  by cancelling an interrupted active turn before yielding. Never treat
  staleness as permission to overwrite.
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

Add a quiet footer linking source, compiled specification, and tutorial so the
live result remains traceable to its intent and generation path.

## Deliverable
Under `outputs/implementations/ai-kanban-browser/`, deliver vendored SQLite WASM,
worker/repository modules, the dependency-free Python skill and launchers, sample
workspace, root-instruction templates, docs, tests, and a Pages live demo. Include
a real-filesystem browser bridge that runs the actual Python CLI through
grant, claim, question, human answer, regrant, resume, completion, and yield, plus
real concurrent claim subprocess coverage.

@structural_constraints strict: true
  Begin with `# AI Kanban — Browser Workspace for Human-AI Work`, then exactly:
  1. Architecture and Board Workspace lifecycle
  2. SQLite schema and repository operations
  3. Human-agent coordination and skill protocol
  4. Cards, decision loops, execution turns, memory, and output surfaces
  5. Interface states and interactions
  6. Security, compatibility, and recovery
  7. File tree, implementation sequence, and test matrix
