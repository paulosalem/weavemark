@promplet version: 0.7

@module weavemark.domains.programming.types.local_first_webapp

# Software Type: Local-First Web Application

Use this type when the application runs primarily for one local user or one local
team workspace, keeps its authoritative data on the user's machine, and may call
external services only for explicitly requested capabilities.

## Product boundaries

- The app MUST be useful without a hosted multi-tenant backend.
- Do not add subscriptions, billing, tenant isolation, or organization onboarding
  unless the refining spec explicitly asks for them.
- The local machine is the source of truth. Browser-only storage MAY cache UI
  state, but it MUST NOT be the canonical store for user data.
- External network calls MUST be explicit in the UI and configuration. The app
  MUST continue to load and display existing local data when those calls fail.

## Local workspace model

- Define one default local workspace and allow the user to choose or create a
  different workspace directory.
- Store durable data, attachments, generated artifacts, and backups under the
  workspace directory or an OS user-data directory.
- Show the active workspace path in settings and diagnostics.
- Provide export and import flows so the user can move a workspace between
  machines without hidden server state.

## Privacy and safety

- Keep private user data local by default.
- Before sending any local content to an external AI, web, or integration service,
  the UI MUST make the destination and purpose clear.
- Logs MUST avoid storing secrets, API keys, refresh tokens, or full sensitive
  payloads unless the user explicitly enables diagnostic capture.

## Operations

- Startup MUST validate that the workspace is readable, writable, and on a
  supported schema version.
- If the local store is missing, initialize it deterministically with migrations.
- If the local store is locked, corrupted, or too new for the app version, show a
  recoverable error with backup, repair, or upgrade guidance.
- Include automated tests for first-run initialization, restart persistence,
  export/import, backup restore, and offline operation.
