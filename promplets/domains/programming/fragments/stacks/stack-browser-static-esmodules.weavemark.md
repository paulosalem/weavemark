@promplet version: 0.7

@module weavemark.domains.programming.stacks.browser_static_esmodules

# Tech Stack: Static Browser JavaScript

Use this stack for applications that must deploy as static files and execute
entirely inside the browser.

## Runtime

- Ship semantic HTML, modern CSS, and standards-based JavaScript ES modules.
- The production artifact MUST run from static hosting without Node.js, server
  routes, server actions, serverless functions, or a separately installed local
  service.
- Use Web Workers for CPU-heavy parsing, database, search, or transformation work
  so the main thread remains responsive.
- Prefer browser standards over frameworks. A small build step is acceptable,
  but checked-in deployable assets and deterministic dependency versions are
  required.
- Host required JavaScript and WebAssembly assets with the application. Do not
  make core behavior depend on a mutable third-party CDN.

## State and boundaries

- Keep domain state behind typed repository/service interfaces even in plain
  JavaScript. UI modules MUST NOT issue raw storage queries.
- Validate every imported file and external response before it reaches domain
  state.
- Browser storage may cache preferences, permissions, and performance data, but
  the refining specification decides the canonical durable store.
- External network calls require explicit user action and visible destination,
  purpose, progress, failure, and retry states.

## Quality

- Use accessible native controls, visible focus, keyboard-complete interactions,
  reduced-motion support, and responsive layouts down to 320 CSS pixels.
- Provide meaningful first-run, loading, empty, active, dirty, saved, conflict,
  unsupported-browser, and recovery states.
- Treat the native `hidden` attribute as authoritative; component display rules
  MUST NOT accidentally reveal inactive states.
- Browser validation MUST finish with no uncaught page errors or unexpected
  console errors/warnings.
- Unit-test domain/storage modules and use Playwright for critical browser flows,
  including narrow viewports and offline/static-host behavior.

## Delivery

- The deployable root MUST contain an `index.html` that works under a repository
  subpath such as GitHub Pages. All asset URLs MUST be relative.
- Include a short README naming the local development command, test command,
  canonical data boundary, browser support, and known limitations.
