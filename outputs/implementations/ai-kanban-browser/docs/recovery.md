# Workspace recovery

AI Kanban never substitutes unrelated browser storage for a connected folder.

| Condition | Safe response |
|---|---|
| Permission revoked | Reconnect from a user gesture and grant read/write access. |
| Missing or invalid manifest | Preserve the folder; repair from a trusted archive or open a different workspace. |
| Future schema | Open with the newer compatible AI Kanban version. |
| Corrupt SQLite | Preserve `board.sqlite`; restore a known-good archive. |
| Migration failure | Keep the original bytes and fix the specific migration cause before retrying. |
| External revision/fingerprint change | Reload, compare, export the in-memory draft, or explicitly recover. |
| Partial save | Keep prior bytes where replacement rollback succeeds and export the draft. |
| Another tab owns the lock | Stay read-only or close the writer tab and reopen. |
| Stale/malformed coordination record | Ignore it; retry after a valid workspace-matched heartbeat. |
| Expired agent lease | Treat it as recovery evidence, not overwrite permission. |
| Journal or commit-marker delay | Wait for the native agent to close SQLite, then retry stabilization and integrity checks. |
| Agent crash | Request reclamation first; use explicit recovery only after inspecting the durable revision. |

Before destructive cleanup, distinguish manifest-recognized application files
from user files. Never delete or overwrite an unrecognized path.
