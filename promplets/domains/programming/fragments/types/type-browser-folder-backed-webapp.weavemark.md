@promplet version: 0.7

@module weavemark.domains.programming.types.browser_folder_backed_webapp

# Software Type: Browser Folder-Backed Application

Use this type when a static browser application treats a user-authorized folder
as a portable local workspace containing structured state, attachments,
artifacts, exports, and private coordination metadata.

## Workspace lifecycle

- First run MUST foreground three honest choices: open a Board Workspace folder,
  create one in a selected folder, or try a clearly labeled memory-only demo.
- On supporting browsers, call `showDirectoryPicker()` only from an explicit user
  gesture in a secure context and request read/write permission for that folder.
- Persist the `FileSystemDirectoryHandle` in IndexedDB solely for recent-workspace
  reconnection. Query permission on return and request it again only from a user
  gesture.
- A versioned manifest MUST identify the workspace, its format, the primary state
  file, reserved application directories, and application-owned files.
- Show the active folder name, permission mode, dirty/saving/saved state, and last
  successful durable write. Never imply durability without a writable handle.
- Provide Close workspace and an explicit portable export. Clear in-memory domain
  state when a workspace closes.
- Before Open, Create, Try demo, reconnect, or Close replaces dirty state, require
  confirmation or a successful save. Cancellation leaves the workspace unchanged.

## Workspace boundary

- The selected folder is the application's local trust, portability, and
  collaboration boundary; the application MUST NOT read or write outside it.
- Use fixed, documented relative paths for structured state, attachments,
  artifacts, exports, and a reserved coordination directory.
- Resolve and validate every application path against the workspace root. Reject
  absolute paths, `..` traversal, symlink escapes, and references outside the
  selected directory.
- Do not modify or delete unrecognized files. Track application-owned files in the
  manifest and require explicit confirmation before destructive cleanup.
- Treat workspace content from humans, agents, and external programs as untrusted.
  Render it safely and never execute generated files merely because they are
  inside an authorized workspace.

## Save integrity

- Serialize browser writes through one save queue and coalesce rapid edits without
  dropping the final state.
- Before replacing a file, compare its current revision and content fingerprint
  with the last-read signature. Abort and reload on unexpected external changes.
- Keep previous bytes until the replacement closes successfully. Failed or
  cancelled writes leave the UI dirty and recoverable.
- Coordinate browser tabs with Web Locks when available and `BroadcastChannel`.
  Only one tab may write one workspace at a time.

## Compatibility and privacy

- Feature-detect the File System Access API. On unsupported browsers, support an
  explicit workspace archive import/export flow and label it honestly as
  import/download rather than connected autosave.
- Permission revocation, missing files, invalid manifests, unsupported future
  versions, corrupt state, and partial exports require specific recovery guidance.
- Workspace bytes remain local unless another explicit feature shows exactly what
  will be sent and obtains confirmation.
- Never upload workspace files for analytics, diagnostics, previews, or crash
  reporting.
