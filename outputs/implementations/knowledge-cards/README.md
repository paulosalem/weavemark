# Knowledge Cards

Knowledge Cards is a static, mobile-first learning app: one coherent knowledge card at a time, local notes and saves, deterministic pack validation, and no backend, accounts, analytics, ads, notification prompts, remote sync, or runtime LLM calls.

## Product and interface

The interface keeps learning primary: a compact pack library, one full-page card,
post-reading actions, and an explicit stopping point after 10 cards or 10 minutes.
The document is the only vertical scroll surface; cards never trap reading inside
an internal scroll pane. Touch scrolling, Previous/Next controls, and keyboard
navigation are equivalent. Onboarding, notes, Saved, History, settings,
import/export, recovery, and offline states use progressive disclosure rather
than competing with the active lesson.

## Run locally

```bash
npm run validate:packs
npm test
npm run smoke
npm start
```

Open the printed local URL, usually `http://127.0.0.1:4173/`. The app is plain checked-in HTML, CSS, and ES modules, so it can also be deployed from a repository subpath such as GitHub Pages. Use the static project root as the published directory.

## Content and validation

The four checked-in packs live under `content/packs/<pack-id>/`; each has `manifest.json`, `cards/cards.json`, `curriculum-map.json`, `validation-report.json`, and an optional `media/` root. `content/packs/index.json` is generated for static hosting because browsers cannot enumerate deployed directories.

Run:

```bash
npm run generate:content
npm run validate:packs
```

`tools/validate-packs.mjs --write-index` scans pack directories, validates schema versions and closed fields, rejects path traversal and orphan JSON, checks exact card counts, duplicate IDs, prerequisite cycles, missing prerequisites, curriculum category coverage, source references, sidecars, and checksum drift, then writes a deterministic sorted pack index. Adding a valid pack directory and rerunning the command makes it discoverable without editing application source.

## Data boundary and privacy

Bundled packs are immutable application content. User-owned state stays in browser IndexedDB database `knowledge-cards-local` version 1: preferences, progress, session orders, card states, notes, drafts, saved cards, revisit queue entries, bounded history, cache metadata, and import/export transactions. Export/import JSON contains local state only and validates before merge with rollback records.

The app does not send notes, saves, progress, understanding signals, or content interactions to any server. Optional source links open only after explicit user action in the browser.

## Browser support

The app targets current evergreen mobile and desktop browsers with ES modules, IndexedDB, CSS scroll snap, dynamic viewport units, a web app manifest, and service workers. If IndexedDB is unavailable, the app shows a recovery warning and uses temporary in-memory state for the session. Service-worker offline caching and standalone installation work on HTTP(S), not `file://`.

## Verification

Available checks:

```bash
npm run validate:packs
npm test
npm run smoke
```

Browser smoke was also performed through a real Chromium page after starting `npm start`, including pack library load, pack opening, keyboard/card navigation, local save/note actions, settings, and import/export surface inspection.

## Known limitations

This implementation is complete for the compiled static-app scope, including all four 50-card packs. It intentionally keeps browser tests dependency-free in this directory; the live browser validation uses the available Playwright MCP path rather than a checked-in `@playwright/test` dependency.
