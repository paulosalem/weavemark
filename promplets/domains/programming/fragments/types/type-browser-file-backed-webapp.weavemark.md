@promplet version: 0.7

@module weavemark.domains.programming.types.browser_file_backed_webapp

# Software Type: Browser File-Backed Application

Use this type when a static web application must work on a durable file selected
or created by the user rather than hidden server state.

## File lifecycle

- First run MUST foreground three honest choices: open an existing workspace
  file, create a new workspace file, or try a clearly labeled memory-only demo.
- On supporting browsers, use `showOpenFilePicker()` and
  `showSaveFilePicker()` only from explicit user gestures in a secure context.
- Keep the granted `FileSystemFileHandle` in IndexedDB solely to offer recent
  workspace reconnection. Query permission on return and request it again only
  from a user gesture.
- Show the active file name, connection mode, dirty/saving/saved state, and last
  successful save. Never imply data is durable while no writable handle exists.
- Provide Close workspace and Save As actions. Clear in-memory domain state when
  a workspace closes.
- Before Open, Create, Try demo, reconnect, or Close replaces a dirty workspace,
  require confirmation or a successful save. Cancellation MUST preserve the
  current workspace unchanged.

## Save integrity

- Serialize writes through one save queue. Coalesce rapid edits without dropping
  the final state.
- Before overwriting, compare the selected file's latest size, modification time,
  and content fingerprint with the last-read signature. If another program
  changed it, stop and offer reload, Save As, or explicit overwrite.
- Keep the previous bytes in memory until a write closes successfully. Failed or
  cancelled writes MUST leave the UI dirty and recoverable.
- Coordinate tabs with Web Locks when available and `BroadcastChannel` for
  ownership/status messages. Only one tab may write one workspace at a time.

## Compatibility

- Feature-detect the File System Access API.
- On unsupported browsers, allow ordinary file import and explicit download of
  the updated file. Label this mode "import/download", not "connected" or
  "autosaved."
- File-picker cancellation is a neutral outcome, not an error toast.
- Incognito, revoked permission, unreadable files, invalid schemas, unsupported
  future versions, and quota/storage failures require specific recovery guidance.

## Privacy

- The selected file remains local unless another explicit feature sends selected
  content elsewhere.
- Never upload workspace bytes for analytics, diagnostics, previews, or crash
  reporting.
