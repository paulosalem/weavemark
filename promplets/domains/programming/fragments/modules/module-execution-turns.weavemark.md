@promplet version: 0.7

@module weavemark.domains.programming.modules.execution_turns

# Module: Execution Turns

Use this module when one durable work item may be executed repeatedly while users
need every attempt, input snapshot, result, and failure to remain inspectable.

## Turn model

The work item is durable intent; an execution turn is one bounded attempt to act
on that intent. Each turn MUST define:

- stable `id`, parent item id, and monotonic display number;
- `queued`, `claimed`, `running`, `needs_input`, `review`, `complete`, `failed`,
  or `cancelled` status;
- trigger and requester, assigned actor, agent run id, idempotency key, and the
  item revision and instruction snapshot from which execution began;
- queued, claimed, started, updated, and completed timestamps as applicable;
- plan/checkpoint state, final summary, error details, output ids, and memory read
  and write lineage.

Completed turn identity and history are immutable. Corrections, retries, and
superseding reports create explicit revisions or later turns rather than rewriting
what a previous turn produced.

## Lifecycle and requeue

- Permit at most one active turn per item by default. Claim queued work
  atomically using expected revision and idempotency checks.
- Initial placement does not have to execute automatically; expose an explicit
  Ready for agent state so loading a template cannot unexpectedly start costly
  work.
- Provide a first-class Run again or Requeue action. Moving a completed item back
  to its configured starting column MUST ask for confirmation and invoke that same
  operation.
- Requeue creates a new queued turn with a fresh id and number, links the previous
  successful turn, snapshots current instructions, and preserves every prior turn.
  It MUST NOT reopen, clear, or silently mutate the previous turn.
- A turn that needs human input remains the active turn. Resume it after the
  answer; create a new turn only when the user requests another execution.
- Cancellation stops future mutation for that turn but retains partial outputs,
  activity, and the reason for cancellation.

## Outputs and projection

- Every generated output MUST belong to an execution turn and carry its own
  version, status, timestamps, actor, provenance, and optional artifact path.
- Keep all dated output versions accessible from the parent item. Feature the
  latest successful result with a useful preview, status, age, and Open action;
  place older results in a clearly ordered History view.
- The compact item may project current turn status, latest-result preview, turn
  count, and attention state, but those projections never replace turn history.
- Support comparison between turns when the output type permits it. Clearly label
  new, changed, unchanged, superseded, and failed results.

## Agent and activity behavior

- Agents read and claim a specific turn, not an undifferentiated parent item.
  Mutations and artifacts MUST cite both item id and turn id.
- Record queue, claim, start, checkpoint, question, answer, output, completion,
  failure, cancellation, and requeue events in append-only activity.
- Completing or failing a turn updates the parent item's projection and workflow
  position transactionally with the final activity event.

## Acceptance criteria

Test initial readiness, atomic claim, duplicate idempotency keys, requeue by action
and confirmed movement, preservation of completed turns, question/resume without a
new turn, cancellation with partial output, latest-result projection, history
ordering, comparison, and concurrent attempts to create or claim another turn.
