@promplet version: 0.7

@module weavemark.domains.programming.modules.activity_stream

# Module: Activity Stream

@note
  Reusable programming module for chronological event histories attached to
  cards, records, users, agents, workflows, documents, or entire applications.

Use this module when users need to understand how something changed over time,
audit decisions, follow live progress, or reconstruct a sequence of human and
system actions.

## Event model

Each activity event MUST define:

- `id`: stable event identifier.
- `type`: semantic event type.
- `actor`: human, agent, integration, system, or automation that caused the event.
- `target`: entity affected by the event.
- `timestamp`: server-authoritative time.
- `summary`: short human-readable description.
- `payload`: structured details needed to render or replay the event.
- `visibility`: public, team-only, private, internal, or redacted as applicable.
- `correlation_id` or `trace_id` when events belong to a larger operation.

## Stream behavior

- The stream SHOULD be append-only unless the product has a strong reason to
  allow edits.
- If events can be redacted or hidden, preserve enough audit metadata to explain
  that something was removed.
- Support pagination, incremental loading, and live append behavior for long
  streams.
- Provide filters for event type, actor, severity, source, and errors when the
  stream is operationally important.
- Important events SHOULD be linkable, copyable, and referenceable from other
  parts of the application.

## Rendering

- Use compact entries for routine events and richer cards or expandable detail
  for significant events.
- Distinguish human actions, agent actions, automation, errors, decisions, and
  output updates visually but calmly.
- Show relative time for scanning and exact timestamp in detail.
- Preserve chronological clarity when events arrive out of order or are replayed
  after reconnecting.

## Reliability and auditability

- Persist events before broadcasting live updates when the stream is an audit
  source.
- Define retention, export, and privacy behavior.
- Avoid logging secrets, sensitive payloads, or excessive raw internals.
- For agentic systems, record enough event lineage to connect prompts, tool
  calls, artifacts, questions, answers, and final outputs.
