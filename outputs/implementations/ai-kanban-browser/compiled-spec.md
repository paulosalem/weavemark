# AI Kanban — Browser Workspace for Human-AI Work

Write an implementation-ready specification for a polished static JavaScript application that runs directly from GitHub Pages with no backend. The specification MUST be concrete enough for a programmer to build, test, and validate the system without further product discovery.

Use RFC 2119 keywords precisely. Every requirement MUST be testable. Prefer concrete schemas, module boundaries, state machines, worker message contracts, SQLite transactions, typed errors, and acceptance criteria over abstract intentions. Preserve exact literal identifiers, file extensions, enum values, field names, browser API names, and output paths.

Return an implementation specification with exactly these sections:

1. Architecture and file lifecycle
2. SQLite schema and repository operations
3. Domain behavior and AI handoff protocol
4. Interface states and interactions
5. Security, compatibility, and recovery
6. File tree and implementation sequence
7. Test and acceptance matrix

## Product constraints to operationalize

AI Kanban is a local, file-backed board where cards are active workspaces for human-AI collaboration. A user opens an existing `.aikanban.sqlite` file or authorizes a new one; that selected file is the canonical board state.

The useful core MUST NOT require an AI provider. Users can organize work, edit plans, preserve activity, capture outputs, and exchange versioned handoff packets with any assistant. Direct provider integration is an optional adapter.

The deliverable MUST be a complete static implementation under `outputs/implementations/ai-kanban-browser/`, including vendored SQLite WASM, worker/repository modules, sample data, documentation, deterministic tests, and a GitHub Pages live-demo entry.

## 1. Architecture and file lifecycle

Specify a static browser architecture using semantic HTML, modern CSS, and standards-based JavaScript ES modules. The production artifact MUST run from static hosting without Node.js, server routes, server actions, serverless functions, or a separately installed local service. All asset URLs MUST be relative so `index.html` works under a repository subpath such as GitHub Pages.

Define these required layers and boundaries:

- UI modules for board, card detail, dialogs, toasts, workspace shell, and output renderers.
- Domain services for cards, columns, plan items, dependencies, outputs, activities, handoff packets, filters, ordering, and validation.
- Typed repository/service interfaces; UI modules MUST NOT issue raw SQL or receive the raw database object.
- A dedicated SQLite Web Worker that owns the only live database connection.
- File lifecycle service for open/create/save/save-as/close/reconnect/import/download.
- Optional `AIProviderAdapter` boundary that is replaceable and never required for core behavior.

Specify the file lifecycle in detail:

- First run MUST foreground three honest choices: Open board, Create board, or Try demo. The demo MUST be clearly labeled memory-only and MUST NOT imply durable persistence.
- On supporting browsers, use `showOpenFilePicker()` and `showSaveFilePicker()` only from explicit user gestures in a secure context.
- Store a granted `FileSystemFileHandle` in IndexedDB solely to offer recent workspace reconnection. On return, query permission and request it again only from a user gesture.
- Show the active file name, connection mode, dirty/saving/saved state, and last successful save time. Never imply data is durable while no writable handle exists.
- Provide Close workspace and Save As. Close MUST clear in-memory domain state after dirty-work confirmation or successful save.
- Before Open, Create, Try demo, reconnect, or Close replaces a dirty workspace, require confirmation or a successful save. Cancellation MUST preserve the current workspace unchanged.
- Serialize writes through one save queue. Coalesce rapid edits without dropping the final state. Explicit Save MUST flush pending mutations immediately.
- Before overwriting, compare the selected file's latest size, modification time, and content fingerprint with the last-read signature. If another program changed it, stop and offer reload, Save As, or explicit overwrite. Never overwrite a conflict silently.
- Keep previous database bytes in memory until a write closes successfully. Failed or cancelled writes MUST leave the UI dirty and recoverable.
- Coordinate tabs with Web Locks when available and `BroadcastChannel` for ownership/status messages. Only one tab may write one workspace at a time; a second tab may open the same file only read-only unless it acquires the workspace lock.
- On unsupported browsers, allow ordinary file import and explicit download of the updated `.aikanban.sqlite` file. Label this mode `import/download`, not `connected` or `autosaved`.

Use Web Workers for CPU-heavy parsing, database, search, export, import, and transformation work so the main thread remains responsive. The selected external file is canonical. In-memory SQLite, OPFS, IndexedDB, and caches are working state only. Never silently fall back from a connected external file to an unrelated OPFS database.

## 2. SQLite schema and repository operations

Specify a browser SQLite file store using a pinned, locally hosted SQLite WASM distribution that can import an existing database from `Uint8Array` and export the complete database bytes. Saves MAY serialize and rewrite the complete database; document a practical workspace-size limit and keep UI responsive while exporting.

Define the schema with field name, type, constraints, default value, indexes, and lifecycle rules for every table. Include at minimum:

- `metadata`: schema version, application name, created/updated timestamps, workspace id, and migration state.
- `columns`: stable text `id`, display `name`, integer `position`, optional description, archived flag, timestamps. Default columns in order MUST be `Inbox`, `Planning`, `In Progress`, `Review`, `Blocked`, `Done`.
- `cards`: stable text `id`, `column_id`, integer `position`, `title`, Markdown `description`, `priority` enum `P0`/`P1`/`P2`/`P3`, optional `assignee`, lifecycle state, archived flag, created/updated timestamps.
- `plan_items`: stable text `id`, `card_id`, integer `position`, text label/body, state enum `pending`/`running`/`done`/`failed`, optional timestamps and failure note.
- `outputs`: stable text `id`, `card_id`, integer `position`, `type` enum `text`/`status`/`link`/`program`/`table`, `title`, structured content JSON or text payload, `schema_version`, `status` enum `draft`/`streaming`/`complete`/`failed`/`stale`/`superseded`/`approved`, source enum, lineage fields, created/updated timestamps.
- `activities`: stable text `id`, event `type`, `actor`, target entity fields, timestamp, summary, structured payload JSON, visibility, optional `correlation_id` or `trace_id`. The stream SHOULD be append-only.
- `dependencies`: stable text `id`, source card id, target card id, dependency type, timestamps, uniqueness constraints, and cycle-prevention behavior.
- Optional search or denormalized tables only if their refresh rules and rebuild behavior are specified.

All timestamps MUST be UTC ISO 8601 with timezone offset. If any monetary field is ever added, it MUST use integer cents or the smallest currency unit, never floats.

Specify deterministic, transactional migrations:

- Store schema version in `metadata`.
- Enable foreign keys.
- Reject unsupported future versions and preserve original bytes before migration.
- Use explicit transactions for multi-table mutations.
- Use stable text identifiers and integer ordering keys.
- Define indexes for common board, search, event, dependency, ordering, and card-detail queries.
- Keep append-only activity/events separate from current entity snapshots.

Define the worker-owned repository API as a small message contract with operation name, request schema, response schema, typed errors, and side effects. Include create, open, snapshot/query, mutation, export, close, and health operations. Required operations include:

- create new database with default columns and sample/demo seed option;
- open and validate existing bytes;
- migrate supported prior versions;
- load board snapshot with columns, cards, counts, filters, and selected-card detail;
- create/edit/archive cards;
- create/edit/reorder/delete plan items;
- create/update/reorder/delete output surfaces;
- append activity events;
- move and reorder cards;
- set dependencies and reject invalid/self/cyclic dependencies;
- search/filter/sort board state;
- export complete database bytes;
- close and dispose the live database connection;
- health check SQLite/WASM readiness.

Every mutation MUST validate worker messages and SQL parameters, MUST NOT concatenate user content into SQL, MUST run in a transaction when it affects multiple tables, and MUST return the updated domain snapshot or a precise change record. Every committed mutation MUST mark the external file dirty. Moving or reordering a card and appending its activity event MUST be one SQLite transaction. Column/card order MUST remain stable after save and reopen.

Surface migration, corruption, lock, conflict, invalid input, dependency-cycle, future-schema, quota/storage, and export failures as typed errors with user-actionable recovery guidance.

## 3. Domain behavior and AI handoff protocol

Define cards as active workspaces, not just task summaries. Each card includes:

- title, Markdown description, priority `P0`-`P3`, assignee, and timestamps;
- a checklist plan with `pending`, `running`, `done`, and `failed` states;
- typed text, status, link, program, and table output surfaces;
- append-only human, AI, movement, output, and error activity;
- dependencies on other cards.

Specify card lifecycle: creation, editing, movement, dependency changes, output changes, archive, restore if supported, permanent deletion if allowed, export handoff, import AI response packet, and close detail view. Define which fields are required at creation, which are computed, and which changes append activity events.

Specify board behavior:

- Users can create, edit, archive, search, filter, reorder, and move cards with pointer and keyboard controls.
- Columns have stable identifiers, display names, ordering, optional descriptions, useful empty states, and optional customization only if the spec defines persistence and validation.
- Drag-and-drop MUST have accessible keyboard alternatives.
- Movement rules, invalid-move reasons, optimistic-update rollback, and persistence behavior MUST be specified.
- Board state MUST persist consistently across refreshes and sessions according to the selected file mode.
- Board scanning SHOULD include counts, WIP indicators, overdue indicators, blocked indicators, dependency indicators, and attention states where useful.

Specify activity events as audit-grade records. Each event MUST define `id`, `type`, `actor`, `target`, `timestamp`, `summary`, `payload`, `visibility`, and optional `correlation_id` or `trace_id`. Distinguish human actions, AI actions, movement, output updates, errors, decisions, imports, and provider interactions visually but calmly. Show relative time for scanning and exact timestamp in detail. Avoid logging secrets, sensitive payloads, or excessive raw internals. Important events SHOULD be linkable, copyable, and referenceable.

Specify typed output surfaces rather than one undifferentiated text area:

- Text: rendered Markdown or rich text with safe formatting.
- Status: key-value state, progress, health, and decision indicators.
- Link: URL, title, description, validation state, open/copy actions.
- Program: syntax-highlighted code with language, optional file path, copy/download actions, and no execution by default.
- Table: structured rows/columns with sorting, filtering, export, and schema validation.

Each output surface MUST define `id`, `host_id`, `type`, `title`, `content`, `schema_version`, `status`, `source`, `created_at`, `updated_at`, lineage, and actions. Multiple surfaces SHOULD be orderable, pinnable, minimizable, and openable in a larger detail view. Failed or stale surfaces MUST explain what happened and what the user can do.

Specify the provider-neutral AI handoff protocol:

- Export one selected card as a compact, versioned JSON and Markdown packet containing intent, context, plan, relevant activity, outputs, dependencies, and requested response shape.
- Copy or download the packet so the user can send it to any assistant.
- Import a versioned AI response packet through paste or file selection.
- Validate the packet completely before previewing changes.
- Treat imported AI text and structured values as untrusted data, never HTML or executable instructions.
- The user MUST approve proposed plan changes, outputs, status changes, dependencies, and activity events before commit.
- Preserve the imported packet and resulting activity entry for provenance.

Define exact packet schemas with `schema_version`, `packet_id`, `created_at`, app identifier, selected card snapshot, board context, activity excerpt limits, requested actions, response schema, validation errors, and provenance. Define import preview states, diff rendering, approval/rejection behavior, and rollback on failure.

Specify optional direct provider integration as an adapter:

- Define a replaceable `AIProviderAdapter`; do not couple domain code to one vendor SDK.
- A browser-only provider credential is session-memory only, never written to localStorage, IndexedDB, logs, URLs, analytics, or workspace files.
- Before sending, show provider, endpoint, model, exact selected content, purpose, progress, failure, retry state, and require explicit confirmation.
- Network failure MUST leave the workspace unchanged and retain a retryable draft.
- External network calls require explicit user action and visible destination, purpose, progress, failure, and retry states.
- Do not claim background execution, WebSockets, secure secret storage, or multi-user coordination in a static browser deployment.

## 4. Interface states and interactions

The board should feel calm, capable, and trustworthy rather than like an operations console. Use restrained navy, mineral teal, warm paper, and coral attention accents. Prioritize readable cards, obvious save state, useful empty columns, strong keyboard focus, reduced motion, and responsive desktop/mobile layouts down to 320 CSS pixels.

Define the workspace shell states:

- first-run: Open board, Create board, Try demo;
- loading SQLite/WASM;
- opening/importing/migrating;
- active connected workspace;
- active `import/download` workspace;
- dirty, saving, saved, save failed, conflict detected;
- unsupported browser;
- permission revoked;
- corrupted or unsupported file;
- read-only second-tab mode;
- recovery and close confirmation.

Make global actions state-aware: show Open/Create before a workspace is active, then Save/New card/Workspace menu after activation. Active workspace MUST show file/permission/save status, board search, filters, New card, Save, Save As, AI handoff, and Close workspace.

Define board interactions:

- default columns in order: Inbox, Planning, In Progress, Review, Blocked, Done;
- cards are scannable at rest and reveal deeper detail through a detail panel or route-like state;
- create, view, edit, duplicate if supported, archive, search, filter, sort, and reorder behavior;
- pointer drag-and-drop with keyboard-complete movement controls;
- visible drop targets, drag preview, focus styles, cancellation behavior, rollback on failed persistence;
- useful empty board and empty column states with creation or filter recovery actions;
- responsive desktop and mobile layouts.

Define card detail interactions:

- edit metadata and Markdown description;
- manage plan items and output surfaces;
- inspect activity;
- move with keyboard-accessible controls;
- archive;
- export handoff;
- preview/import an AI response packet;
- show dependencies and dependency errors;
- keep Cancel and Save reachable while plan, output, and activity sections scroll.

Accessibility requirements MUST include accessible native controls where possible, semantic labels, visible focus, sufficient contrast, screen-reader text for icon-only controls, reduced-motion support, keyboard-complete operation, and unambiguous click/double-click/drag/context-menu/inline-edit behavior. Treat the native `hidden` attribute as authoritative; component display rules MUST NOT accidentally reveal inactive states.

## 5. Security, compatibility, and recovery

Specify privacy boundaries:

- The selected file remains local unless another explicit feature sends selected content elsewhere.
- Never upload workspace bytes for analytics, diagnostics, previews, crash reporting, or provider calls without explicit user confirmation of exact selected content.
- Browser-only provider credentials are session-memory only and never persisted.
- Imported files, handoff packets, provider responses, Markdown, links, table values, and program outputs are untrusted data.
- Do not render imported AI content as raw HTML. Sanitize or safely render Markdown.
- Program output surfaces are displayed and copied/downloaded; they are not executed by default.

Specify compatibility:

- Feature-detect the File System Access API, secure context, Web Workers, WebAssembly, IndexedDB, Web Locks, and `BroadcastChannel`.
- Connected autosave is allowed only on supporting Chromium browsers with permission.
- Elsewhere, use import/download fallback with honest durability language.
- File-picker cancellation is a neutral outcome, not an error toast.
- Local JavaScript and WebAssembly assets MUST be hosted with the application; core behavior MUST NOT depend on a mutable third-party CDN.

Specify recovery guidance for incognito/private browsing limitations, revoked permission, unreadable files, invalid schemas, unsupported future versions, corrupt SQLite input, quota/storage failures, worker crashes, save conflicts, lock contention, export failure, provider/network failure, and reload during dirty state.

Specify concurrency and race handling for shared mutable state:

- one worker-owned database connection;
- one serialized save queue;
- one writer per workspace file where possible;
- `BroadcastChannel` ownership/status messages across tabs;
- conflict detection by size, modification time, and content fingerprint;
- typed rollback/reload/Save As/explicit overwrite paths.

## 6. File tree and implementation sequence

Specify the required deliverable under `outputs/implementations/ai-kanban-browser/`. Include a concrete file tree with at least:

- `index.html` GitHub Pages live-demo entry;
- `assets/` for CSS, icons, and vendored SQLite WASM assets;
- `src/main.js` or equivalent ES module entry;
- UI modules for workspace shell, board, cards, card detail, dialogs, output surfaces, activity stream, and handoff preview;
- domain modules for cards, columns, plan items, outputs, activities, dependencies, validation, handoff packets, and sample data;
- worker modules for SQLite initialization, schema, migrations, repository operations, message validation, and export/import;
- file lifecycle modules for File System Access API, import/download fallback, recent handles, save queue, conflict detection, locks, and close/reconnect;
- optional provider adapter interface and disabled-by-default example adapter stub;
- deterministic tests and fixtures;
- README and GitHub Pages deployment notes.

Specify deterministic dependency versions and checked-in deployable assets. Include local development command, test command, canonical data boundary, browser support, known limitations, and sample data instructions in README requirements.

Provide an implementation sequence that builds in safe increments:

1. static shell, styling tokens, and first-run states;
2. SQLite WASM worker boot and health check;
3. schema, migrations, seed data, and repository tests;
4. file open/create/import/download/save queue;
5. board snapshot rendering and default columns;
6. card CRUD, ordering, movement transaction, and activity append;
7. card detail, plan items, dependencies, and output surfaces;
8. search/filter and responsive/accessible interactions;
9. AI handoff export/import/preview/commit;
10. conflict detection, reconnection, locks, and recovery states;
11. deterministic tests, Playwright flows, documentation, and GitHub Pages entry.

## 7. Test and acceptance matrix

Provide a test and acceptance matrix that names test type, fixture/setup, steps, expected result, and acceptance criteria. Include unit tests for domain/storage modules and Playwright tests for critical browser flows, including narrow viewports and offline/static-host behavior.

Required coverage:

- new database creation with default columns;
- existing `.aikanban.sqlite` reopen and export/reimport equivalence;
- deterministic migrations and rollback;
- unsupported future schema rejection;
- corrupt input rejection with recovery guidance;
- ordering persistence for columns/cards/plan items/outputs;
- movement/reordering plus activity insertion in one transaction;
- dependency validation including self-dependency and cycle rejection;
- append-only activity behavior and event rendering;
- typed output surface rendering for text, status, link, program, and table;
- search, filters, archive behavior, and empty states;
- keyboard movement, focus order, reduced motion, and screen-reader labels;
- responsive layouts down to 320 CSS pixels;
- File System Access connected save path on supporting browsers;
- import/download fallback path on unsupported browsers;
- Save As, Close workspace, dirty confirmation, cancellation neutrality;
- conflict detection by changed file signature;
- Web Locks or read-only second-tab behavior;
- permission revocation and recent-handle reconnection;
- worker error propagation and UI recovery;
- handoff export packet schema, copy/download, import validation, preview, approval, commit, and provenance activity;
- optional provider adapter disabled core behavior, confirmation before send, session-only credentials, network failure leaving workspace unchanged;
- GitHub Pages relative asset loading and no backend dependency;
- browser validation with no uncaught page errors or unexpected console errors/warnings.

The final specification MUST be strict, implementation-ready, and limited to the seven required sections above. It MUST not include vague placeholders, unresolved questions, backend assumptions, or claims of durability/security that the static browser architecture cannot provide.