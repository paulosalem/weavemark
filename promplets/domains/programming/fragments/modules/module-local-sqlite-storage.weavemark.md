@promplet version: 0.7

@module weavemark.domains.programming.modules.local_sqlite_storage

# Module: Local SQLite Storage

Use this module when durable application state must live in a local relational
database, with SQLite as the default embedded store.

## Storage contract

- SQLite is the canonical durable store for user data.
- Browser `localStorage`, IndexedDB, memory, and cache files MAY improve UX, but
  they MUST be treated as disposable caches unless the refining spec says
  otherwise.
- The app MUST expose a configured data directory. The SQLite file, attachments,
  derived artifacts, backups, and repair logs MUST live under that directory.
- The default development path SHOULD be easy to inspect, such as
  `.local-data/app.sqlite`; packaged local apps SHOULD use the OS user-data
  directory.

## Schema and migrations

- Define explicit relational tables for every durable entity.
- Every table MUST have a stable primary key, creation timestamp, update
  timestamp, and clear deletion/archive behavior.
- Migrations MUST be versioned, deterministic, and tested against an existing
  database file.
- The app MUST refuse to start on an unsupported future schema version instead
  of silently rewriting the database.
- Use indexes for board/order queries, search filters, event replay, and
  dependency lookups.

## Transactions and consistency

- Multi-step changes that must appear atomically to the user MUST run in one
  SQLite transaction.
- Use optimistic concurrency fields such as `version` or `updatedAt` for
  collaborative or agent-written records.
- Event insertion and visible state updates MUST be ordered consistently. If an
  event explains a state change, persist both in the same transaction.
- Define how to recover from interrupted writes, locked database files, failed
  migrations, and disk-full errors.

## Files and large payloads

- Store large attachments and generated artifacts as files under the data
  directory, not as large database blobs by default.
- Store metadata, content hash, MIME type, size, origin, and relative file path in
  SQLite.
- Use content hashes to detect duplicate attachments and corrupted files.
- Deleting a record MUST define whether referenced files are retained, archived,
  garbage-collected, or moved to a trash area.

## Backup, export, and repair

- Provide explicit backup, restore, import, and export flows.
- Before destructive migrations or repair attempts, create a timestamped backup
  unless the database is unreadable.
- Exports MUST include the SQLite database, referenced files, schema version, app
  version, and manifest checksums.
- Repair tools MUST report what was changed and preserve the original damaged
  database when possible.

## Tests

- Test first-run initialization and restart persistence.
- Test migrations from at least one older schema fixture once the schema evolves.
- Test backup/restore and export/import with attachments.
- Test transactional rollback for failed multi-entity writes.
- Test database locking, disk-full handling where practical, and corrupted-file
  detection.
