@promplet version: 0.7

@module weavemark.domains.work_intelligence.idea_execution_workspace

# Idea Execution Workspace

@refine module:weavemark.std.reasoning.action_planning mingle: true

@note
  Reusable domain layer for applications that capture ideas, shape them into
  decisions or actions, delegate work, and track execution status.

Use this layer when an application must help a person move from loose ideas,
notes, insights, and project impulses to concrete outcomes.

## Idea capture and shaping

- Ideas MUST preserve origin: manual entry, imported note, signal, conversation,
  meeting, artifact, source link, or generated suggestion.
- Support idea states such as raw, clarified, researched, decided, delegated,
  in progress, waiting, blocked, shipped, archived, and rejected.
- Distinguish idea, task, decision, experiment, question, opportunity, risk,
  delegation, reminder, project, and output artifact rather than forcing all of
  them into a single task model.
- Every actionable idea SHOULD expose the smallest useful next step, expected
  outcome, owner, timing, dependencies, uncertainty, and definition of done.

## Decision and delegation

- Make it easy to decide whether to do, defer, delegate, research, merge,
  split, schedule, or discard an idea.
- Delegations MUST track owner, request, expected deliverable, due or check-in
  window, status evidence, blockers, follow-up cadence, and handoff context.
- Decisions MUST preserve rationale, alternatives considered, triggering inputs,
  decision owner, confidence, and revisit condition.
- Blocked work MUST show the blocker, who can unblock it, and what evidence
  would change status.

## Execution tracking

- Track committed actions separately from suggestions.
- Support status check-ins, stale-work detection, reminders, review queues, and
  progress summaries.
- Link actions to source signals, related ideas, decisions, projects, people,
  attachments, and generated artifacts.
- Show whether work produced a concrete output: report, prompt, document,
  issue, message, task list, prototype, plan, decision record, or project update.

## Review and learning loop

- The workspace SHOULD help the user review what became useful, what stalled,
  what was delegated, what was discarded, and which inputs produced outcomes.
- Repeatedly ignored ideas, stale delegations, and unresolved decisions SHOULD
  become visible without creating notification noise.
- The system SHOULD learn from user choices by improving suggestions, routing,
  topic priorities, and default workflows while keeping user control explicit.
