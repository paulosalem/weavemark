@promplet version: 0.7

@module weavemark.domains.programming.modules.browser_ai_handoff

# Module: Browser AI Handoff

Use this module when a backend-free application should collaborate with AI tools
without pretending it can safely host an autonomous agent service.

## Provider-neutral handoff

- Export one selected work item as a compact, versioned JSON and Markdown packet
  containing intent, context, plan, relevant activity, and requested response
  shape.
- Copy or download the packet so the user can send it to any assistant.
- Import a versioned AI response packet through paste or file selection.
- Validate the packet completely before previewing changes. The user MUST approve
  the proposed plan, outputs, status changes, and activity events before commit.
- Preserve the imported packet and resulting activity entry for provenance.

## Optional direct provider adapter

- Define a replaceable `AIProviderAdapter`; do not couple domain code to one
  vendor SDK.
- A browser-only provider credential is session-memory only, never written to
  localStorage, IndexedDB, logs, URLs, analytics, or workspace files.
- Before sending, show the provider, endpoint, model, exact selected content, and
  purpose. Require explicit confirmation.
- Network failure MUST leave the workspace unchanged and retain a retryable draft.

## Boundaries

- The useful core workflow must remain available without a configured provider.
- Do not claim background execution, WebSockets, secure secret storage, or
  multi-user coordination in a static browser deployment.
- Treat imported AI text and structured values as untrusted data, never HTML or
  executable instructions.
