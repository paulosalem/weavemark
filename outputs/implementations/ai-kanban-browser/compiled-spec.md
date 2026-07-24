# AI Kanban — Browser Workspace for Human-AI Work

Build a complete, polished static JavaScript application under `outputs/implementations/ai-kanban-browser/`. The application runs directly from GitHub Pages with no backend, no Node.js runtime, no server routes, no server actions, no serverless functions, and no separately installed local service. It uses semantic HTML, modern CSS, standards-based JavaScript ES modules, a dedicated SQLite WASM worker, and relative asset URLs so it works under a repository subpath.

AI Kanban is a local, file-backed board where cards are active workspaces for human-AI collaboration. The selected `.aikanban.sqlite` file is the canonical board state. The core workflow must work without any AI provider: users organize work, edit plans, preserve activity, capture outputs, and exchange versioned handoff packets with any assistant. Direct provider integration is an optional adapter.

## 1. Architecture and file lifecycle

### Static application architecture

- Deliver a static browser application rooted at `outputs/implementations/ai-kanban-browser/index.html`.
- Use semantic HTML, modern CSS, and JavaScript ES modules. Prefer browser standards over frameworks.
- All production asset URLs must be relative and must work when hosted from a GitHub Pages repository subpath.
- Host required JavaScript and WebAssembly assets with the application. Core behavior must not depend on a mutable third-party CDN.
- Include vendored SQLite WASM assets and pin deterministic dependency versions.
- Keep domain state behind typed repository/service interfaces. UI modules must not issue raw SQL or receive a raw database object.
- Run SQLite and any CPU-heavy parsing, import/export, search indexing, migration, or transformation work in Web Workers so the main thread remains responsive.
- Treat the native `hidden` attribute as authoritative; component display rules must not reveal inactive states.
- The useful core must be offline-capable after the static assets load. External network calls are optional features and require explicit user action, visible destination, purpose, progress, failure, and retry states.

### File lifecycle

The application has three honest first-run choices:

1. **Open board**: open an existing `.aikanban.sqlite` workspace file.
2. **Create board**: authorize creation of a new `.aikanban.sqlite` workspace file with the default board, schema, and sample starter content if requested.
3. **Try demo**: use a clearly labeled memory-only demo that never implies durable storage.

On supporting Chromium browsers in secure contexts:

- Use `showOpenFilePicker()` and `showSaveFilePicker()` only from explicit user gestures.
- Store a granted `FileSystemFileHandle` in IndexedDB only to offer recent workspace reconnection.
- On return, query permission and request permission again only from a user gesture.
- Display active file name, connection mode, save mode, dirty/saving/saved state, and last successful save time.
- Provide **Close workspace** and **Save As** actions.
- Clear in-memory domain state when the workspace closes.

On unsupported browsers:

- Feature-detect the File System Access API.
- Support ordinary file import and explicit download of the updated `.aikanban.sqlite` file.
- Label this mode exactly as `import/download`, not `connected` or `autosaved`.
- Never imply data is durable while no writable handle exists.

### Save integrity and conflict handling

- The selected external file is canonical. In-memory SQLite, OPFS, IndexedDB, and caches are working state only.
- Serialize writes through one save queue. Coalesce rapid edits without dropping the final state.
- Export the complete SQLite database bytes after committed mutations. Explicit Save must flush pending mutations immediately.
- Before overwriting a connected file, compare the latest file size, modification time, and content fingerprint with the last-read signature.
- If another program or tab changed the file, stop and offer reload, Save As, or explicit overwrite. Never overwrite a conflict silently.
- Keep previous bytes in memory until a write closes successfully. Failed or cancelled writes leave the UI dirty and recoverable.
- Before Open, Create, Try demo, reconnect, or Close replaces a dirty workspace, require confirmation or a successful save. Cancellation preserves the current workspace unchanged.
- Coordinate tabs with Web Locks when available and `BroadcastChannel` for ownership/status messages. Only one tab may write one workspace at a time.
- A second tab may open the same file read-only unless it acquires the workspace lock.
- Never silently fall back from a connected external file to an unrelated OPFS database.

### Workspace status states

The shell must show a state-aware global action area:

- Before activation: Open board, Create board, Try demo.
- After activation: file/permission/save status, board search, filters, New card, Save, Save As, AI handoff, Workspace menu, Close workspace.
- File-picker cancellation is neutral and must not show an error toast.
- Incognito mode, revoked permission, unreadable files, invalid schemas, unsupported future versions, quota/storage failures, corrupt input, and export failures require specific recovery guidance.

## 2. SQLite schema and repository operations

### SQLite worker and repository contract

- Run SQLite in a dedicated worker, e.g. `src/workers/sqlite.worker.js`.
- Use a pinned, locally hosted SQLite WASM distribution that can import an existing database from `Uint8Array` and export the complete database bytes.
- The worker owns the only live database connection.
- The worker exposes a small message-based repository API with validated request/response envelopes.
- UI modules call repository services only; they never concatenate SQL or send raw SQL.
- Validate worker messages and SQL parameters. Do not concatenate user content into SQL.
- Every mutation returns an updated domain snapshot or precise change record and marks the external file dirty.
- Surface migration, corruption, lock, conflict, validation, and export failures as typed errors with user-actionable recovery.

Required repository operations:

- `createWorkspace(options)`
- `openWorkspace(bytes)`
- `getSnapshot(queryOptions)`
- `searchCards(query, filters)`
- `createCard(input)`
- `updateCard(cardId, patch)`
- `archiveCard(cardId)`
- `restoreCard(cardId)`
- `moveCard(cardId, targetColumnId, targetOrderKey)`
- `reorderColumn(columnId, orderedCardIds)`
- `createColumn(input)`
- `updateColumn(columnId, patch)`
- `archiveColumn(columnId)`
- `createPlanItem(cardId, input)`
- `updatePlanItem(planItemId, patch)`
- `reorderPlanItems(cardId, orderedPlanItemIds)`
- `createOutputSurface(cardId, input)`
- `updateOutputSurface(surfaceId, patch)`
- `appendActivity(input)`
- `exportDatabase()`
- `closeWorkspace()`
- `healthCheck()`

### Schema rules

- Store schema version in `metadata`.
- Enable foreign keys with `PRAGMA foreign_keys = ON`.
- Use deterministic, transactional migrations.
- Reject unsupported future versions and preserve original bytes before migration.
- Use stable text identifiers and integer ordering keys.
- Store timestamps as UTC ISO 8601 strings with timezone offsets.
- Keep append-only activity/events separate from current entity snapshots.
- Use explicit transactions for multi-table mutations, especially movement/reordering plus activity insertion.
- Define indexes for board, search, event, output, and dependency queries.
- Document a practical workspace-size limit because saves rewrite the complete database.

### Required tables

#### `metadata`

- `key TEXT PRIMARY KEY`
- `value TEXT NOT NULL`

Required keys:

- `schema_version`: current integer version as text.
- `workspace_id`: stable text identifier.
- `created_at`: UTC ISO 8601 timestamp.
- `updated_at`: UTC ISO 8601 timestamp.
- `app_name`: `AI Kanban`.

#### `columns`

- `id TEXT PRIMARY KEY`
- `name TEXT NOT NULL`
- `description TEXT NOT NULL DEFAULT ''`
- `order_key INTEGER NOT NULL`
- `is_system INTEGER NOT NULL DEFAULT 0`
- `archived_at TEXT NULL`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Constraints and indexes:

- `name` must be non-empty after trim.
- Active column order is stable by `order_key`, then `created_at`, then `id`.
- Index `idx_columns_active_order` on `(archived_at, order_key)`.

Default columns in order:

1. Inbox
2. Planning
3. In Progress
4. Review
5. Blocked
6. Done

#### `cards`

- `id TEXT PRIMARY KEY`
- `column_id TEXT NOT NULL REFERENCES columns(id)`
- `title TEXT NOT NULL`
- `description_markdown TEXT NOT NULL DEFAULT ''`
- `priority TEXT NOT NULL DEFAULT 'P3'`
- `assignee TEXT NOT NULL DEFAULT ''`
- `order_key INTEGER NOT NULL`
- `status TEXT NOT NULL DEFAULT 'active'`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`
- `archived_at TEXT NULL`

Constraints and indexes:

- `priority` is one of `P0`, `P1`, `P2`, `P3`.
- `status` is one of `active`, `blocked`, `done`, `archived`.
- `title` must be non-empty after trim.
- Index `idx_cards_column_order` on `(column_id, archived_at, order_key)`.
- Index `idx_cards_updated` on `(updated_at)`.
- Search covers title, description, priority, assignee, column, plan text, output titles, and activity summaries.

#### `plan_items`

- `id TEXT PRIMARY KEY`
- `card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE`
- `text TEXT NOT NULL`
- `state TEXT NOT NULL DEFAULT 'pending'`
- `order_key INTEGER NOT NULL`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Constraints and indexes:

- `state` is one of `pending`, `running`, `done`, `failed`.
- `text` must be non-empty after trim.
- Index `idx_plan_items_card_order` on `(card_id, order_key)`.

#### `output_surfaces`

- `id TEXT PRIMARY KEY`
- `card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE`
- `type TEXT NOT NULL`
- `title TEXT NOT NULL`
- `content TEXT NOT NULL DEFAULT ''`
- `schema_version INTEGER NOT NULL DEFAULT 1`
- `status TEXT NOT NULL DEFAULT 'draft'`
- `source TEXT NOT NULL DEFAULT 'human'`
- `lineage_json TEXT NOT NULL DEFAULT '{}'`
- `order_key INTEGER NOT NULL`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Constraints and indexes:

- `type` is one of `text`, `status`, `link`, `program`, `table` for the first build; schema allows future renderer types.
- `status` is one of `draft`, `streaming`, `complete`, `failed`, `stale`, `superseded`, `approved`.
- `source` is one of `human`, `ai`, `integration`, `import`, `system`.
- `content` for `table` surfaces is JSON with columns and rows.
- `content` for `program` surfaces is JSON with language, optional file path, and source text.
- Index `idx_output_surfaces_card_order` on `(card_id, order_key)`.

#### `activity_events`

- `id TEXT PRIMARY KEY`
- `type TEXT NOT NULL`
- `actor TEXT NOT NULL`
- `target_type TEXT NOT NULL`
- `target_id TEXT NOT NULL`
- `timestamp TEXT NOT NULL`
- `summary TEXT NOT NULL`
- `payload_json TEXT NOT NULL DEFAULT '{}'`
- `visibility TEXT NOT NULL DEFAULT 'local'`
- `correlation_id TEXT NULL`
- `created_at TEXT NOT NULL`

Constraints and indexes:

- Events are append-only. Do not edit or delete events in normal operation.
- `type` includes `human`, `ai`, `movement`, `output`, `error`, `system`, `handoff_export`, `handoff_import`.
- `actor` is a human, AI, integration, system, or automation label.
- `timestamp` is an app-generated UTC ISO 8601 timestamp with timezone offset, and `payload_json` may include clock/source notes when relevant.
- Avoid secrets, provider credentials, excessive raw internals, and sensitive payloads.
- Index `idx_activity_target_time` on `(target_type, target_id, timestamp)`.
- Index `idx_activity_type_time` on `(type, timestamp)`.

#### `card_dependencies`

- `card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE`
- `depends_on_card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE CASCADE`
- `created_at TEXT NOT NULL`
- Primary key `(card_id, depends_on_card_id)`.

Constraints:

- `card_id` must not equal `depends_on_card_id`.
- Prevent direct duplicate dependencies.
- Warn and block cycles when the user creates a dependency that would make a card depend on itself through a chain.

### Transactional behavior

- Moving or reordering a card and appending its movement activity event is one SQLite transaction.
- Creating a card inserts the card and an activity event in one transaction.
- Updating plan items, output surfaces, dependencies, and card metadata must update `updated_at` on the owning card and append activity where user-visible history matters.
- Failed transactions must rollback completely and preserve the prior snapshot.
- Column/card order must remain stable after save, export, import, close, and reopen.

## 3. Domain behavior and AI handoff protocol

### Board behavior

- Users can create, edit, archive, search, filter, sort, reorder, and move cards.
- Users can create, edit, archive, reorder, and describe columns, while the default six columns remain available in new boards.
- Empty columns and empty boards must show useful states and creation/filter recovery actions.
- Board scanning should include counts, priority badges, blocked/dependency indicators, and updated timestamps.
- Reordering uses persistent `order_key` values and supports rollback after invalid moves or save failures.
- Movement rules are permissive in the first build, but movement must remain auditable and reversible through visible state and activity history.
- If movement is blocked by validation, the reason appears at the point of interaction.

### Card model and lifecycle

Cards are operational workspaces, not only summaries. Each card has:

- stable `id`;
- `title`;
- Markdown description;
- priority `P0`, `P1`, `P2`, or `P3`;
- assignee;
- timestamps;
- current column;
- stable order within the column;
- checklist plan items with `pending`, `running`, `done`, and `failed` states;
- typed output surfaces;
- append-only activity;
- dependencies on other cards;
- archived state.

Lifecycle:

1. Created in a selected column, defaulting to Inbox.
2. Edited in compact card view or detail workspace.
3. Moved/reordered by pointer or keyboard controls.
4. Enriched with plan items, outputs, dependencies, and activity.
5. Exported to AI handoff packets when needed.
6. Archived, restored, or left active.

Compact card view must be scannable and reveal deeper detail through expansion or a detail panel. The full card detail view is the authoritative editing surface for description, plan, outputs, activity, dependencies, and handoff.

### Activity stream behavior

- Activity is chronological, append-only, and attached primarily to cards, with workspace-level system events where useful.
- Render compact entries for routine events and expandable details for significant events.
- Visually distinguish human actions, AI actions, movement, output updates, system events, and errors calmly.
- Show relative time for scanning and exact timestamp in detail.
- Provide filters for event type and source in long streams.
- Preserve enough lineage to connect handoff exports, imported packets, proposed changes, approvals, outputs, and final committed events.
- Important events should be copyable or referenceable from card detail.

### Typed output surfaces

The first build supports these surface types:

- **Text**: rendered Markdown with safe formatting.
- **Status**: key-value progress, health, or decision indicators.
- **Link**: URL or local reference with label, notes, and copy action.
- **Program**: syntax-highlighted program artifacts with language, optional file path, copy, and download actions.
- **Table**: structured rows and columns with sorting, filtering, and CSV export.

Surface requirements:

- Use the renderer best suited to the type instead of flattening everything into prose.
- Surfaces are orderable, openable in detail, copyable, and exportable where applicable.
- Failed or stale surfaces explain what happened and what the user can do.
- Comments, approvals, and revisions preserve version history when they affect downstream decisions.
- Generated or imported surfaces carry provenance in `lineage_json`.
- Applying an output to the workspace is explicit and auditable.

### Provider-neutral AI handoff

AI collaboration must work without hosting an autonomous agent service.

Export one selected card as both JSON and Markdown handoff packets containing:

- packet version;
- workspace/app identity;
- card id, title, column, priority, assignee, description, dependencies, plan, selected outputs, and relevant activity;
- user-selected intent and requested response shape;
- constraints that imported content is untrusted and must be previewed before commit;
- timestamp and packet id.

Required actions:

- Copy packet as Markdown.
- Download packet as `.json`.
- Download packet as `.md`.
- Import AI response packet by paste or file selection.
- Validate the full packet before previewing changes.
- Preview proposed plan changes, output surfaces, status changes, card edits, and activity events.
- Require explicit user approval before commit.
- Preserve the imported packet and resulting activity entry for provenance.

Imported AI text and structured values are untrusted data, never HTML and never executable instructions. A failed import leaves the workspace unchanged and displays field-level validation errors.

### Optional direct provider adapter

The application may include a disabled-by-default provider adapter seam:

- Define a replaceable `AIProviderAdapter` interface.
- Do not couple domain code to a vendor SDK.
- Browser-only provider credentials are session-memory only and must never be written to `localStorage`, IndexedDB, logs, URLs, analytics, or workspace files.
- Before sending, show provider, endpoint, model, exact selected content, and purpose; require explicit confirmation.
- Network failure leaves the workspace unchanged and retains a retryable draft.
- Do not claim background execution, WebSockets, secure secret storage, or multi-user coordination in a static browser deployment.

## 4. Interface states and interactions

### Visual and interaction tone

- The board should feel calm, capable, and trustworthy rather than like an operations console.
- Use restrained navy, mineral teal, warm paper, and coral attention accents.
- Prioritize readable cards, obvious save state, useful empty columns, strong keyboard focus, reduced motion, and responsive desktop/mobile layouts.
- Keep raw database details behind an About workspace panel.
- Add a quiet footer linking the source promplet, compiled implementation specification, and public tutorial so the live result remains traceable to the intent and generation path that produced it.

### Required screens and states

Implement these major interface states:

1. **First run**: Open board, Create board, Try demo; explains durability honestly.
2. **Loading/opening**: parses file, validates schema, migrates if needed, and reports progress.
3. **Active workspace**: board columns, cards, search, filters, save status, New card, Save, Save As, AI handoff, Workspace menu, Close workspace.
4. **Dirty workspace**: visible unsaved state with queued save progress.
5. **Saved workspace**: last successful save displayed.
6. **Conflict**: external change detected with Reload, Save As, and Explicit overwrite options.
7. **Unsupported browser**: import/download fallback with clear limitations.
8. **Recovery**: specific guidance for revoked permission, invalid schema, corrupt file, future schema, quota failure, worker failure, and failed export.
9. **Empty board/column/search**: useful explanations and recovery actions.
10. **Card detail workspace**: metadata, description, plan, outputs, activity, dependencies, archive/export/import controls.

### Board interactions

- Users can move cards with pointer and keyboard controls.
- Drag-and-drop must include accessible keyboard alternatives.
- Reordering has visible drop targets, focus styles, cancellation behavior, optimistic rollback, and persistence.
- Search and filters must not destroy board order; clearing filters restores the full board.
- Bulk selection may be omitted from the first build unless implemented completely.
- Global actions are state-aware: Open/Create before activation, Save/New card/Workspace menu after activation.

### Card interactions

- Compact cards show title, priority, assignee, column/status cues, dependency/blocking cues, plan progress, output count, and recent activity cue.
- Cards with primary actions expose pointer and keyboard access.
- Click, double-click, drag, context menu, checkbox selection, and inline editing behavior must be unambiguous and non-conflicting.
- Detail view supports editing metadata and Markdown description, managing plan items and outputs, inspecting activity, moving with keyboard-accessible controls, archiving, exporting handoff, and previewing/importing AI response packets.
- In long card workspaces, keep Cancel and Save reachable while plan, output, and activity sections scroll.
- Provide visible focus, semantic labels, sufficient contrast, and screen-reader text for icon-only controls.

### Responsive and accessibility requirements

- Support responsive layouts down to 320 CSS pixels.
- Cards remain legible in narrow columns, dense grids, and detail panes.
- Use accessible native controls where possible.
- Provide visible focus and keyboard-complete interactions.
- Support `prefers-reduced-motion`.
- Browser validation must finish with no uncaught page errors or unexpected console errors/warnings.

## 5. Security, compatibility, and recovery

### Privacy and data boundaries

- The selected `.aikanban.sqlite` file remains local unless the user explicitly chooses an export, handoff, or provider-send action.
- Never upload workspace bytes for analytics, diagnostics, previews, or crash reporting.
- Do not log provider credentials, packet contents, workspace bytes, secrets, or excessive raw internals.
- Browser storage may cache preferences, recent handles, permissions hints, and performance data, but the selected file is the canonical durable store.
- Validate every imported file and external response before it reaches domain state.

### Browser compatibility

- Connected autosave is available only on supporting Chromium browsers with File System Access API in a secure context.
- Import/download fallback is available elsewhere.
- Reconnection must remember the recent file handle where supported, request permission from a user gesture, detect external changes, and never overwrite a conflict silently.
- File-picker cancellation is not an error.
- The README must name browser support and known limitations.

### Security posture

- Render Markdown safely. Do not execute scripts from card descriptions, imported packets, outputs, or activity payloads.
- Treat imported AI content as untrusted data.
- Do not use `innerHTML` with unsanitized workspace content.
- Provider adapter requests require explicit confirmation and show destination, endpoint, model, selected content, and purpose.
- Do not claim secure browser secret storage for provider credentials.
- Direct provider credentials remain in session memory only.

### Recovery requirements

Typed error states must cover:

- invalid file type or unreadable file;
- corrupt SQLite database;
- missing schema version;
- unsupported future schema version;
- failed migration;
- permission denied or revoked handle;
- save cancelled;
- external file conflict;
- quota/storage failure;
- worker initialization failure;
- SQLite WASM load failure;
- export failure;
- invalid handoff packet;
- direct provider network failure.

Each recovery state must state what happened, what remains safe, and what the user can do next. Failed or cancelled writes leave the current workspace dirty and recoverable.

## 6. File tree and implementation sequence

### Required file tree

Create the implementation under `outputs/implementations/ai-kanban-browser/` with at least:

```text
outputs/implementations/ai-kanban-browser/
  index.html
  README.md
  docs/
    tutorial.md
    implementation-spec.md
  assets/
    sqlite/
      sqlite3.js
      sqlite3.wasm
    icons.svg
  src/
    main.js
    app.js
    config.js
    styles/
      base.css
      layout.css
      board.css
      card.css
      outputs.css
      dialogs.css
    domain/
      ids.js
      schema.js
      validation.js
      ordering.js
      handoff.js
      markdown.js
    services/
      workspace-service.js
      file-lifecycle.js
      save-queue.js
      lock-service.js
      repository-client.js
      provider-adapter.js
    repository/
      migrations.js
      sql.js
      sqlite-repository.js
      seed.js
    workers/
      sqlite.worker.js
    ui/
      shell.js
      board-view.js
      column-view.js
      card-view.js
      card-detail.js
      plan-editor.js
      output-surfaces.js
      activity-stream.js
      handoff-dialog.js
      workspace-dialogs.js
      toasts.js
      focus.js
  sample-data/
    ai-kanban-demo.aikanban.sqlite
    handoff-request.example.json
    handoff-response.example.json
  tests/
    unit/
      ordering.test.js
      validation.test.js
      handoff.test.js
      migrations.test.js
      repository.test.js
      save-queue.test.js
    e2e/
      first-run.spec.js
      board-flow.spec.js
      file-lifecycle.spec.js
      handoff.spec.js
      responsive.spec.js
  package.json
  playwright.config.js
```

If a build step is used, checked-in deployable assets must still be deterministic and documented.

### Implementation sequence

1. **Static shell and styling**: create `index.html`, CSS, responsive layout, state containers, footer links, and accessible base components.
2. **Domain model**: implement IDs, ordering keys, validation, schema constants, Markdown sanitization, and handoff packet validation.
3. **SQLite worker**: vendor SQLite WASM, initialize worker, implement migrations, repository API, transactions, export/import, and typed errors.
4. **Workspace lifecycle**: implement open/create/demo, recent handle storage, permission flow, save queue, conflict fingerprinting, Web Locks, BroadcastChannel, Save As, Close workspace, and import/download fallback.
5. **Board UI**: implement columns, cards, search, filters, empty states, movement, keyboard reordering, stable persistence, and rollback.
6. **Card detail**: implement metadata editing, Markdown description, plan editor, dependencies, output surfaces, activity stream, archive/restore, and sticky Cancel/Save controls.
7. **AI handoff**: implement packet export/copy/download, response paste/file import, validation, preview, approval, activity preservation, and optional provider adapter seam.
8. **Documentation and sample data**: produce README, tutorial, compiled implementation spec copy, demo database, and packet examples.
9. **Tests**: implement deterministic unit tests and Playwright flows for critical behavior, narrow viewports, static hosting, fallback modes, and recovery states.
10. **GitHub Pages demo**: ensure `index.html` and relative assets run from the public static path.

### Documentation requirements

README must include:

- local development command;
- test command;
- deploy/static hosting notes;
- canonical data boundary: selected `.aikanban.sqlite` file;
- browser support matrix;
- connected mode vs `import/download` mode;
- known limitations;
- privacy notes;
- workspace-size guidance;
- AI handoff usage.

Tutorial must show:

- creating a board;
- opening/reconnecting a board;
- creating and moving cards;
- editing a plan;
- adding output surfaces;
- exporting a handoff packet;
- importing and approving an AI response packet;
- recovering from unsupported browser or conflict states.

## 7. Test and acceptance matrix

### Unit and repository tests

Implement deterministic tests for:

- new-database creation with default columns;
- existing-file reopen;
- schema version storage;
- migrations and rollback;
- unsupported future schema rejection;
- corrupt input handling;
- ordering key generation and stable ordering;
- card create/update/archive/restore;
- column create/update/archive/reorder;
- card movement plus activity insertion in one transaction;
- plan item state transitions: `pending`, `running`, `done`, `failed`;
- output surface validation for `text`, `status`, `link`, `program`, and `table`;
- dependency duplicate and cycle prevention;
- export/reimport equivalence;
- worker error propagation;
- save queue coalescing and final-state preservation;
- conflict fingerprint detection;
- handoff request export schema;
- handoff response import validation;
- Markdown sanitization.

### Browser and Playwright tests

Implement Playwright tests for:

- first-run choices and honest durability labels;
- create board, add card, save, close, reopen, and verify persistence;
- import/download fallback path;
- keyboard card movement and focus visibility;
- pointer movement or simulated drag/drop where stable in tests;
- search/filter and clearing filters;
- card detail editing with sticky Cancel/Save controls;
- output surface rendering and actions;
- activity event append and display;
- AI handoff export and response preview/approval;
- conflict state with Reload, Save As, and Explicit overwrite choices;
- unsupported-browser messaging by feature mock;
- narrow viewport at 320 CSS pixels;
- reduced-motion behavior;
- static-host behavior under a repository subpath;
- no uncaught page errors and no unexpected console errors/warnings.

### Manual acceptance criteria

The build is acceptable when:

- `outputs/implementations/ai-kanban-browser/index.html` runs as a static app from GitHub Pages.
- A user can create a `.aikanban.sqlite` board, create cards, move/reorder them, edit plans and outputs, save, close, reopen, and see stable state.
- Moving or reordering a card and appending movement activity happens atomically.
- The default columns appear in order: Inbox, Planning, In Progress, Review, Blocked, Done.
- Connected mode never implies durability before a writable handle exists.
- `import/download` mode is clearly labeled and usable on browsers without File System Access API.
- External file changes are detected and never overwritten silently.
- The app remains useful without any AI provider.
- Handoff export creates versioned JSON and Markdown packets.
- Handoff import validates, previews, and requires explicit approval before committing changes.
- Optional provider integration, if present, uses a replaceable `AIProviderAdapter`, requires explicit confirmation, and stores credentials only in session memory.
- Activity streams preserve human, AI, movement, output, error, system, handoff export, and handoff import events without leaking secrets.
- Typed output surfaces render as purpose-built views instead of one undifferentiated text area.
- The UI is accessible by keyboard, has visible focus, supports reduced motion, and works down to 320 CSS pixels.
- README, tutorial, sample data, deterministic tests, vendored SQLite WASM, worker/repository modules, and GitHub Pages live-demo entry are present.
- Browser validation finishes with no uncaught page errors or unexpected console errors/warnings.