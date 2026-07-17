@promplet version: 0.7

@module weavemark.domains.programming.modules.context_attachments

# Module: Context Attachments

@note
  Reusable programming module for attaching files, URLs, records, snippets,
  images, source references, generated artifacts, or related entities to a host
  object such as a card, task, document, case, conversation, or workflow run.

Use this module when a user or agent needs to gather supporting material and make
that material available for later review, automation, search, or execution.

## Attachment model

Each attachment MUST define:

- `id`: stable identifier.
- `host_id`: entity the attachment belongs to.
- `type`: file, URL, text, image, table, artifact, reference, related entity, or
  domain-specific type.
- `title`: user-facing label.
- `source`: upload, generated, external link, integration, clipboard, or system.
- `content_ref`: storage key, URL, entity reference, or inline payload according
  to size and security constraints.
- `mime_type` or format when applicable.
- `size` and checksum for uploaded or generated files when useful.
- `created_by`, `created_at`, and optional provenance metadata.
- `permissions`: who can view, edit, remove, or use the attachment.

## User experience

- Provide previews for common attachment types without forcing downloads.
- Show unsupported or unavailable previews gracefully.
- Users SHOULD be able to rename, reorder, remove, download, copy link, and open
  attachments according to permissions.
- Related-entity attachments SHOULD navigate to the related object and make the
  relationship direction clear.
- Large uploads, failed uploads, virus scans, broken URLs, and expired references
  MUST have visible states.

## Agent and automation use

- If agents consume attachments, define exactly which attachment types they may
  read and how they receive content.
- Preserve source provenance so generated answers can cite or reference the
  material used.
- Do not silently include sensitive attachments in agent context; require clear
  permission or policy.
- If attachments are transformed into extracted text, thumbnails, embeddings, or
  summaries, store those derivatives as traceable artifacts.

## Validation

- Test upload/link/add/remove flows.
- Test permission-limited users.
- Test missing, deleted, expired, and oversized attachments.
- Test that attachment-derived context is visible in audit/activity history when
  it affects user-visible output.
