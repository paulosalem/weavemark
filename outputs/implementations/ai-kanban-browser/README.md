# AI Kanban

AI Kanban is a static, backend-free browser workspace for durable human–AI
work. A user-selected **Board Workspace folder** is the canonical workspace,
agent working directory, and trust boundary. The core board, decisions,
execution turns, research memory, typed outputs, and provider-neutral handoff
all work without an AI provider.

## Run

```bash
npm install
npm run serve
```

Open `http://127.0.0.1:4173/`. All deployable URLs are relative, so the same
files work beneath a GitHub Pages repository subpath.

## Test

```bash
npm test                 # deterministic JS units + vendored-asset hashes
npm run test:python      # dependency-free workspace agent protocol
npm run test:ui          # Chromium Playwright integration and responsive UI
```

From the WeaveMark repository root, the directly related contract test is:

```bash
python -m pytest tests/test_ai_kanban_browser.py -q
```

## Canonical data boundary

Connected mode uses `showDirectoryPicker()` from an explicit user gesture.
The selected folder contains:

```text
manifest.json
board.sqlite
attachments/
artifacts/
exports/
.ai-kanban/coordination/
AGENTS.md
CLAUDE.md
.agents/skills/ai-kanban/
```

`board.sqlite` is canonical. A dedicated Web Worker owns the browser's only
live SQLite connection and exposes typed repository operations; UI code never
receives a connection or issues SQL. IndexedDB stores only the recent
`FileSystemDirectoryHandle`. The app does not upload workspace bytes for
analytics, diagnostics, previews, or crash reporting.
Every browser open and native-agent mutation verifies the exact SQLite SHA-256,
workspace id, and revision against `manifest.json`; a matching revision number
alone is never sufficient.

The manifest versions the format, protocol, schema, owned paths, reserved
directories, and fingerprints. Paths are validated as relative. AI Kanban
preserves unrecognized files and asks before replacing a user-modified
bootstrap file.

## Saving and recovery

- One serialized save queue coalesces rapid browser writes.
- Each connected save exports and rewrites the complete SQLite database.
- Before replacement, manifest revision and database fingerprint are compared
  with the loaded signature.
- An external change stops the save and offers reload, comparison,
  draft export, or explicit recovery; it is never silently overwritten.
- Web Locks and `BroadcastChannel` make competing tabs read-only where
  supported.
- Archive mode imports/downloads a versioned JSON archive when connected
  folder access is unavailable. Referenced attachments and artifacts are
  preserved with validated paths, fingerprints, a 50 MB per-file limit, and the
  250 MB total limit. Demo mode is visibly memory-only.
- Migration failures preserve the original input bytes in the Worker session
  and return typed recovery errors.
- Workspace creation preflights every bootstrap path. Existing instruction
  files remain untouched unless their exact observed content is explicitly
  confirmed for replacement.
- Creation holds a directory-identity lock until the workspace-id lock is
  established. Bootstrap repairs require that writable lock, flush pending
  saves, and revalidate both workspace and compared file content immediately
  before replacement.
- A verified `reconcile-manifest` agent command can republish exactly one
  committed SQLite revision after manifest publication fails. It requires the
  matching durable outbox record and refuses ambiguous revision gaps.
- Agent mutations persist canonical request fingerprints and a coordination
  marker outbox in the same commit. Exact retries can republish a missing marker
  without repeating work.

## Browser and size support

Connected folder autosave requires a secure context and the File System Access
API, currently best supported by Chromium desktop browsers. Other modern
browsers use explicitly labeled archive import/download. Native dialogs,
keyboard movement, visible focus, reduced motion, and layouts down to 320 CSS
pixels are supported.

Use Board Workspaces up to **250 MB**. This is a practical safety limit, not a
SQLite limit: browser saving serializes and replaces the complete database, so
larger workspaces increase memory, fingerprinting, and write costs.

## Agent coordination

The root instruction files point to exactly one canonical skill bundle.
Compatible agents announce identity, wait for a durable browser grant, verify
revision/generation/holder on every `BEGIN IMMEDIATE` mutation, close the
transaction before reasoning, publish checkpoints, and yield control
explicitly. The browser is read-only while an agent owns the cooperative writer
baton.
After every agent SQLite commit, the CLI atomically publishes the matching
revision and database fingerprint to `manifest.json` before its coordination
marker.

The dependency-free CLI uses only `sqlite3`, `argparse`, JSON, and filesystem
APIs:

```bash
python .agents/skills/ai-kanban/ai_kanban.py --help
```

A skill cannot keep a terminated runtime alive, consume future output, or start
future model turns. Continuous autonomy requires a host-supported scheduler.
Lease expiry is recovery evidence, never overwrite permission.
The browser accepts returned control only after a stopped/yielded final marker,
journal stabilization, integrity checks, and exact generation/revision
agreement.
Failed grants roll back before publication. Once publication may have begun,
the browser stays read-only and requires cooperative reclamation rather than
overwriting agent state.
While an agent holds the writer baton, a separate immutable in-memory
repository keeps cards, turns, outputs, and history inspectable. Optional direct
provider credentials and reviewed requests are cleared or invalidated whenever
their card, payload, configuration, credential, workspace, or dialog changes.

## Architecture

- `src/sqlite-worker.js` — schema, migrations, queries, transactional mutations
- `src/repository.js` — typed UI-facing repository
- `src/file-workspace.js` — folder/archive lifecycle, manifests, conflicts
- `src/coordination.js` — validated mailbox polling and control signals
- `src/packets.js` / `src/provider-adapter.js` — neutral handoff boundary
- `src/surfaces.js` / `src/markdown.js` — safe output rendering
- `templates/` — generated root instructions and canonical agent skill
- `sample-board-workspace/` — openable portable example

See [`docs/product-design.md`](docs/product-design.md) for interface direction
and [`docs/recovery.md`](docs/recovery.md) for concrete failure handling.

## Known limitations

- The cooperative protocol cannot protect against malicious local software or
  an agent that deliberately ignores it.
- The optional direct provider adapter supports a conservative generic HTTPS
  request shape; provider-specific payload translation belongs in an explicit
  adapter. Credentials are session-memory only and are not secure storage.
- Archive files are versioned JSON containers rather than ZIP files. They are
  portable and inspectable but can be larger than compressed archives.
- Static browser code has no background runner, server, WebSocket, or secret
  vault.
