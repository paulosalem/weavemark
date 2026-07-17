@promplet version: 0.7

@module weavemark.domains.programming.validation.playwright_mcp_browser_validation

# Browser Validation with Playwright MCP

@note
  Reusable programming-validation layer for web-based software, games, dashboards,
  reports, and other browser-visible interfaces. Refine this when an AI
  programming agent should both implement and prove the result in a real browser.

Use Playwright MCP as the preferred browser-observation surface whenever the
software has a web UI or browser-rendered interaction model.

## Tool availability and setup

- Before claiming browser validation, check whether Playwright MCP or equivalent
  browser automation tools are available in the agent environment.
- If Playwright MCP is not available, explicitly install or configure the official
  Playwright MCP server before browser validation. Prefer the host environment's
  standard MCP setup path; when Node/npm are available, the server command is
  commonly `npx @playwright/mcp@latest`.
- If the project itself needs Playwright tests, add Playwright through the
  project's package manager and install required browsers with the existing
  ecosystem command. Do not add duplicate or unrelated test tooling.
- If MCP setup cannot be completed, state the exact blocker and do not pretend
  browser validation happened.

## Browser-grounded implementation loop

The implementing agent MUST use a repeated build-run-observe-improve loop:

1. Inspect the specification, repository structure, package scripts, existing
   tests, and framework conventions.
2. Implement the smallest coherent slice that should be visible or testable in
   the browser.
3. Start the application with an existing development or preview command. If no
   command exists, add the minimal project-appropriate command and document it.
4. Open the running URL with Playwright MCP and interact as a real user: click,
   type, drag, resize, navigate, start a game round, lose/win/restart, submit
   forms, and exercise important empty, loading, success, and error states.
5. Observe the rendered page, accessibility tree, console output, network
   behavior, screenshots, and any persisted state that affects the user
   experience.
6. Compare observed behavior against the specification and against professional
   product quality: clarity, responsiveness, stability, accessibility, visual
   polish, and absence of console/runtime errors.
7. Inspect relevant source files when browser behavior reveals a defect or
   design weakness.
8. Improve the implementation, then repeat the browser pass until the main
   experience works and no high-value improvement remains obvious.

## Evidence requirements

Each validation pass SHOULD leave concrete evidence:

- the command used to run the application;
- the URL tested;
- the user flows exercised;
- screenshots or trace artifacts when the interface is visual or spatial;
- console/network/runtime errors found and resolved;
- remaining limitations or follow-up opportunities.

For games, browser validation MUST include at least one playable smoke test that
starts from first load, reaches active play, exercises controls and collisions or
core interactions, observes scoring/progress feedback, and verifies restart or
replay without a full page reload.

## Quality bar

- Never stop at "the app builds" when the intended artifact is visual or
  interactive. A browser-based result is incomplete until it has been exercised in
  the browser.
- Prefer real interaction over static screenshots alone. Screenshots are evidence,
  not a substitute for using the interface.
- Treat awkward first-run UX, broken focus, unreadable layout, unresponsive input,
  invisible state changes, jank, and console errors as implementation defects.
- When an improvement is obvious from browser use, make it rather than merely
  reporting it, unless it is outside the requested scope or would require a major
  product decision.
- Final reporting MUST distinguish verified behavior from unverified assumptions.
