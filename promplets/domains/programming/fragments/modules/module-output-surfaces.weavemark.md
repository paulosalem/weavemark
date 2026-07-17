@promplet version: 0.7

@module weavemark.domains.programming.modules.output_surfaces

# Module: Typed Output Surfaces

@note
  Reusable programming module for rendering multiple kinds of generated or
  user-created output as purpose-built, typed surfaces rather than one undifferentiated
  text area.

Use this module in agent consoles, report builders, review tools, task boards,
analysis workspaces, dashboards, and any application where outputs have distinct
formats, interactions, or evidence requirements.

## Surface model

Each output surface MUST define:

- `id`: stable surface identifier.
- `host_id`: card, record, run, document, or workspace that owns the surface.
- `type`: renderer type such as text, program, table, diff, image, chart, status,
  log, terminal, form, canvas, file, or custom domain surface.
- `title`: human-readable label.
- `content`: payload or reference to payload.
- `schema_version`: version for structured payloads.
- `status`: draft, streaming, complete, failed, stale, superseded, or approved.
- `source`: human, agent, integration, import, or system.
- `created_at`, `updated_at`, and optional lineage to prompts, tools, files, or
  upstream artifacts.
- `actions`: copy, download, approve, comment, apply, export, open, compare, pin,
  minimize, or domain-specific operations.

## Common surface types

- **Text**: rendered Markdown or rich text with safe formatting.
- **Program**: syntax-highlighted program artifacts with language, file path,
  copy, and apply actions when repository integration exists.
- **Table**: structured rows and columns with sorting, filtering, export, and
  schema validation.
- **Diff**: before/after comparison with inline comments and approval workflow.
- **Image/Media**: preview, gallery, zoom, download, alt text, and provenance.
- **Status**: key-value metrics, thresholds, progress, health, and trend
  indicators.
- **Log/Terminal**: streaming output, ANSI handling, search, pause, and auto-scroll
  controls.
- **Form**: structured questions or decisions with validation and submission
  state.
- **Canvas/Diagram**: spatial nodes, edges, layout controls, zoom, and export.

## Rendering and interaction

- Surfaces SHOULD use the renderer best suited to their type instead of flattening
  everything into prose.
- Multiple surfaces SHOULD be orderable, pinnable, minimizable, and openable in a
  larger detail view.
- Streaming surfaces MUST distinguish partial output from final output.
- Failed or stale surfaces MUST explain what happened and what the user can do.
- Comments, approvals, and revisions MUST preserve version history when they
  affect downstream decisions.

## Evidence and provenance

- Generated surfaces SHOULD carry lineage to the inputs, prompts, tools,
  attachments, and agent steps that produced them.
- User-visible reports SHOULD distinguish verified output from draft or
  speculative output.
- Applying a surface to an external system, repository, database, or file MUST be
  explicit and auditable.
