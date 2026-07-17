## Local-first Next.js, Prisma, and SQLite foundation

- Use Next.js with TypeScript strict mode, Prisma, and SQLite.
- Keep authoritative workspace state local by default in a user-selectable
  directory.
- Use SQLite WAL mode, schema versioning, deterministic migrations, startup
  diagnostics, explicit transaction boundaries, backups before risky migrations,
  and visible repair guidance.
- Store large attachments and generated artifacts as files; store metadata,
  content hash, MIME type, size, origin, relative path, and provenance in SQLite.
- Durable records should have stable IDs, created/updated timestamps, status,
  owner or actor when relevant, provenance links, optimistic versioning for
  conflicting writes, and archive or soft-delete behavior.
- Exports should include database, referenced files, schema version, application
  version, manifest, and checksums. Imports should validate checksums and require
  explicit confirmation before overwriting a workspace.
- External providers are optional. Existing local data must remain usable when
  AI, search, feeds, or integrations are unavailable.
- Logs must avoid secrets, tokens, private payloads, and full sensitive artifacts
  unless diagnostic capture is explicitly enabled.
