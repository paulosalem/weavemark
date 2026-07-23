@promplet version: 0.7

@module weavemark.domains.programming.modules.browser_sqlite_file_store

# Module: Browser SQLite File Store

Use SQLite compiled to WebAssembly when a browser application needs relational
transactions while preserving a user-selected SQLite file as its canonical
portable store.

## Architecture

- Run SQLite in a dedicated Web Worker.
- Use a pinned, locally hosted SQLite WASM distribution that can import an
  existing database from `Uint8Array` and export the complete database bytes.
- The worker owns the only live database connection and exposes a small
  message-based repository API. UI modules never receive the raw database object.
- The selected external file is canonical. In-memory SQLite, OPFS, IndexedDB, and
  caches are working state only.
- Accept that saves serialize and rewrite the complete database. Document a
  practical workspace-size limit and keep UI responsive while exporting.

## Schema

- Store a schema version in a metadata table.
- Use deterministic, transactional migrations. Reject unsupported future
  versions and preserve the original bytes before migration.
- Enable foreign keys and use explicit transactions for multi-table mutations.
- Use stable text identifiers and integer ordering keys; define indexes for
  common board, search, event, and dependency queries.
- Keep append-only activity/events separate from current entity snapshots.

## Repository contract

- Provide create, open, snapshot/query, mutation, export, close, and health
  operations.
- Every mutation returns the updated domain snapshot or a precise change record,
  then marks the external file dirty.
- Validate worker messages and SQL parameters. Do not concatenate user content
  into SQL.
- Surface migration, corruption, lock, conflict, and export failures as typed
  errors with user-actionable recovery.

## Persistence and concurrency

- Export after committed mutations through the file lifecycle's serialized save
  queue. Explicit Save MUST flush pending mutations immediately.
- Use transaction boundaries for movement/reordering plus activity insertion.
- A second tab may open the same file only read-only unless it acquires the
  workspace lock.
- Never silently fall back from a connected external file to an unrelated OPFS
  database.

## Tests

- Test new-database creation, existing-file reopen, migrations, rollback,
  ordering, deletion rules, export/reimport equivalence, corrupt input, future
  schema rejection, save conflict, and worker error propagation.
