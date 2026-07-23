@promplet version: 0.7

@module weavemark.domains.programming.modules.static_content_packs

# Module: Manifest-Discovered Static Content Packs

Use this module when a static application ships coherent, pre-generated content
collections and must discover new collections without application-code changes or
runtime generation.

## Directory convention

- Keep each pack in `content/packs/<pack-id>/`.
- Each pack directory MUST contain `manifest.json` and one or more JSON content
  files named by that manifest. Optional media lives below the same directory.
- Keep a generated `content/packs/index.json` as the static-host-compatible pack
  index. Browsers cannot enumerate a deployed directory; a build/check script MUST
  discover pack directories and regenerate this index deterministically.
- Adding a valid pack directory and running the documented content-index command
  MUST make the pack available without editing application source.

## Schemas and identity

- Publish versioned, closed JSON Schemas for the pack index, pack manifest, and
  content items. Reject unknown schema versions and malformed required fields.
- Pack IDs and item IDs MUST be stable, URL-safe, unique, and independent of
  display titles or file order.
- A manifest defines at least: schema version, ID, title, description, language,
  audience, content version, item count, ordered content files, optional media
  root, authorship/provenance, source policy, license, and content checksum.
- Content items MUST not embed executable HTML or JavaScript. Treat all text and
  imported metadata as untrusted data rendered through safe DOM APIs.
- Item-level source references MUST be curated to the claims on that item. Never
  attach every pack-level source mechanically when their declared scopes differ.

## Build-time validation

- Provide one deterministic validation/index command suitable for local use and
  CI. It scans `content/packs/*/manifest.json`, validates every referenced file,
  verifies unique IDs and exact counts, rejects path traversal and missing media,
  computes checksums, and writes a stably sorted `index.json`.
- Validation MUST fail on orphan content, duplicate IDs, undeclared files,
  checksum drift, unsupported schemas, broken references, or count mismatches.
- Generated indexes MUST be reproducible from the pack directories and checked in
  for zero-build static hosting.
- Validation reports MUST distinguish deterministic structural checks from
  source-aware editorial review. Automation MUST NOT claim that facts are correct,
  citations support claims, or concepts are nonduplicative unless it actually
  performs and records that semantic review.

## Runtime loading and updates

- Load the index first, then manifests and content on demand. A bad pack MUST fail
  in isolation with a useful message while valid packs remain available.
- Cache immutable content by pack ID, content version, and checksum. Never confuse
  user progress with bundled pack content.
- Preserve user state across a compatible pack update by stable item ID. Report
  removed or incompatible items rather than silently attaching old state to new
  content.
- Support offline use after a pack has been loaded, within explicit storage and
  cache limits.
