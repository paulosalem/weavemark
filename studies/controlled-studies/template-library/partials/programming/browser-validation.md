## Browser validation and evidence

- Validate the actual browser experience, not only static source inspection.
- Record command used to run the app, URL tested, browser flows exercised,
  screenshots or traces when available, console errors found and resolved, and
  remaining limitations.
- Browser validation should cover first load, primary user flow, invalid inputs,
  persistence across restart or reload, responsive layout, keyboard/focus
  behavior, recovery states, and absence of runtime console errors.
- Prefer Playwright MCP or an equivalent real-browser tool when available. If the
  browser tool cannot run, report the exact blocker and do not claim browser
  validation happened.
- Acceptance requires a first-session path that proves the product is usable,
  understandable, recoverable, and backed by saved evidence.
