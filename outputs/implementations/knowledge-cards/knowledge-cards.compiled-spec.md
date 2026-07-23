# Knowledge Cards

## Product promise, learning model, and non-goals

Write an implementation-ready specification for a polished mobile-first static web app named Knowledge Cards. The app MUST turn a familiar one-card-at-a-time social feed into cumulative learning while avoiding engagement extraction. It MUST run entirely as checked-in static HTML, CSS, and JavaScript ES modules with no backend, no server routes, no serverless functions, no separately installed local service, and no runtime LLM calls.

Use RFC 2119 keywords precisely. Every requirement MUST be testable; name concrete files, schemas, algorithms, validation gates, browser states, storage keys, and acceptance checks wherever possible. The resulting specification MUST be sufficient for a developer to build, test, validate, and deploy the full app under `outputs/implementations/knowledge-cards/`.

The product promise is: learners choose a coherent topic pack, read one high-density knowledge card at a time, keep notes and saved concepts locally, and leave each short session with a clearer map of the field. The social-feed familiarity is only an interaction shortcut; it MUST NOT justify fake popularity, autoplay, infinite dark-pattern loops, randomized rewards unrelated to learning, streak shame, forced sharing, deceptive urgency, ads, analytics profiling, notification prompts, or attention optimization.

The learning model MUST be cumulative and prerequisite-safe:

- Before cards are written, each pack MUST have a concept map covering foundations, mechanisms, applications, misconceptions, limitations, bridges, and advanced horizons.
- Every candidate concept MUST have declared importance, prerequisite depth, difficulty, novelty, category, and relationships.
- The complete pack MUST teach the important shape of the field rather than a bag of trivia.
- Each card MUST teach exactly one meaningful concept, with deliberate revisits used only to deepen, connect, contrast, apply, or test recall.
- User signals such as likes, saves, notes, revisit requests, and self-rated understanding MUST be tracked separately and MUST NOT be treated as proof of mastery.

The initial content edition MUST pre-generate one coherent pack for each topic below, with exactly 50 cards per pack:

- Banking Industry and Central Banks
- Economics
- Children Rearing, Development and Care
- Personal Investments for Total Beginners

The maintained example inputs MUST be checked in beside the promplet as `knowledge-cards.vars.json`. Pack content and optional explanatory media MUST be reviewed, versioned, validated, and checked in. Adding a conforming `content/packs/<pack-id>/` directory and regenerating the static pack index MUST make the pack discoverable without application-code changes.

Health, child-development, financial, legal, and safety-sensitive cards MUST state their educational boundary, avoid individualized advice, distinguish consensus from uncertainty or simplification, date stale-prone claims, and point to qualified professional or primary guidance when action could cause harm. Cards MUST NOT invent citations or imply that a source supports more than it does.

## Static architecture, mobile shell, and offline lifecycle

Specify a deployable static browser architecture using semantic `index.html`, modern CSS, and standards-based JavaScript ES modules. The production artifact MUST work from static hosting, including a repository subpath such as GitHub Pages, with all asset URLs relative. Required JavaScript, CSS, fonts, images, schemas, workers, and optional WebAssembly assets MUST be hosted with the application; core behavior MUST NOT depend on a mutable third-party CDN.

The implementation MUST include at minimum:

- `index.html` as the deployable root.
- `src/main.js` or equivalent ES-module entrypoint.
- UI modules for the pack library, feed shell, card renderer, action bar, note editor, progress/stopping-point surfaces, settings, saved cards, notes, history, import/export, and recovery states.
- Domain modules for pack loading, curriculum validation helpers, feed ordering, session planning, progress, notes, local-state repositories, import/export validation, and URL/deep-link handling.
- Versioned schemas under a stable path such as `schemas/`.
- Content packs under `content/packs/<pack-id>/` and a generated `content/packs/index.json`.
- A deterministic pack-index and validation command suitable for local use and CI.
- Tests and README.

Keep domain state behind typed repository/service interfaces even in plain JavaScript. UI modules MUST NOT issue raw IndexedDB queries, mutate bundled content, or parse unvalidated pack files directly. Validate every imported file and external input before it reaches domain state. Treat all pack text and imported metadata as untrusted data rendered through safe DOM APIs; content items MUST NOT embed executable HTML or JavaScript.

Use Web Workers for CPU-heavy parsing, validation, search, checksum verification, import/export preview, or transformation work when those tasks could block a mid-range phone. Define measurable performance budgets for first content, time-to-interactive, initial JavaScript, CSS, images, and card-to-card interaction latency. Render meaningful first content quickly on constrained mobile networks. Lazy-load nonessential media and later content without layout shift by reserving dimensions and showing useful placeholders.

The app MUST work offline after first load of the static shell and after a pack has been loaded, within explicit browser storage limits. The offline lifecycle MUST include first-run, loading, loaded, offline-ready, pack-unavailable, stale-cache, unsupported-browser, storage-quota, recovery, and update-detected states. A bad pack MUST fail in isolation with a useful message while valid packs remain available. Browser validation MUST finish with no uncaught page errors and no unexpected console errors or warnings.

External network calls, if any optional documentation links are opened, MUST require explicit user action and show destination, purpose, progress, failure, and retry states. The core reading, navigation, local edits, import/export, and loaded-pack review flows MUST NOT require the network after initial application and pack loading.

## Pack convention, schemas, discovery, and build-time validation

Define the static pack convention precisely. Each pack MUST live in `content/packs/<pack-id>/`. Each pack directory MUST contain `manifest.json` and one or more JSON content files named by that manifest. Optional media MUST live below the same pack directory. Browsers cannot enumerate deployed directories, so a build/check script MUST discover pack directories and regenerate a deterministic `content/packs/index.json` for static hosting.

Pack IDs and card IDs MUST be stable, URL-safe, unique, and independent of display titles or file order. Publish closed, versioned JSON Schemas for the pack index, pack manifest, card files, media metadata, source references, and any review prompt structures. Unknown schema versions, unknown fields where the schema is closed, malformed required fields, and invalid enum values MUST be rejected.

The pack manifest MUST define at least:

- `schema_version`
- `id`
- `title`
- `description`
- `language`
- `audience`
- `level`
- `purpose`
- `content_version`
- `card_count`
- `ordered_content_files`
- `optional_media_root`
- `authors`
- `provenance`
- `source_policy`
- `license`
- `accent_color`
- `content_checksum`
- `created_at` and `updated_at` as UTC ISO 8601 timestamps with timezone offset

The generated pack index MUST include stable sorted entries with enough metadata for the library: pack ID, title, description, language, audience, level, purpose, card count, content version, checksum, accent color, and manifest path. Load the index first, then manifests and content on demand. Cache immutable content by pack ID, content version, and checksum. Never confuse user progress with bundled pack content.

The deterministic validation/index command MUST scan `content/packs/*/manifest.json`, validate every referenced file, verify exact card counts, reject path traversal and missing media, compute checksums, and write a stably sorted `content/packs/index.json`. It MUST fail on orphan content, duplicate IDs, undeclared files, checksum drift, unsupported schemas, broken references, malformed source refs, missing required review prompts where the schema requires them, prerequisite cycles, unsatisfied prerequisite IDs, concept duplication, unsupported claims, count mismatches, and media outside the pack root.

Adding a valid pack directory and running the documented command MUST make the pack available without editing application source. Generated indexes MUST be reproducible from the pack directories and checked in for zero-build static hosting. Preserve user state across a compatible pack update by stable card ID; report removed or incompatible items rather than silently attaching old state to new content.

## Knowledge-card model, curriculum rules, and example-pack requirements

Define a knowledge-card schema specialized from the general card primitive. A knowledge card is an informational, navigational, and lightly interactive card whose domain meaning is a single concept. Each card MUST have a clear purpose, scannable hierarchy, accessible controls, and a compact view that can open or reveal deeper supporting detail without losing the one-card focus.

Each card MUST contain:

- `id`: stable identifier within the pack.
- `title`: short descriptive title.
- `core_idea`: two to five concise paragraphs emphasizing intuition, mechanism, importance, limitations, and relationships.
- `example`: a short practical example, analogy, diagram description, or thought experiment when it improves understanding.
- `key_takeaway`: one memorable sentence capturing the concept.
- `connections`: zero or more related concepts, prepared-for topics, common misconceptions, or real-world applications, preferably using stable card IDs.
- `difficulty`: a small declared scale centered on educated beginners.
- `importance`: normalized or declared value used by the ordering policy.
- `foundational_priority`: declared value used by the ordering policy.
- `category` or equivalent concept-map bucket.
- `prerequisites`: stable IDs of cards whose ideas are assumed.
- `source_refs`: references supporting factual or safety-sensitive claims.
- `media`: optional local image or illustration metadata only when it materially clarifies the idea.
- `review_prompts`: optional checked-in recall, comparison, application, or connection questions for deliberate revisits without a runtime model.

Every sentence MUST teach. Avoid filler, motivational copy, encyclopedic detail, long biography, excessive jargon, disconnected definitions, and decorative media. Teaching style MUST be concise, insightful, approachable, conversational without being casual, intellectually honest, and mechanism-oriented. Advanced ideas MAY appear only when explained intuitively and when the learner should finish stretched rather than overwhelmed.

For every pack, require a curriculum map and validation report covering foundations, mechanisms, applications, misconceptions, limitations, bridges, advanced horizons, difficulty distribution, prerequisite graph, source policy, bias/safety review, and cross-links. Select concepts by importance before randomness. Favor foundations early, then interleave mechanisms, applications, misconceptions, and occasional surprising bridges so the sequence remains varied without becoming incoherent. Never duplicate a concept. A deliberate revisit MUST name the earlier card relationship and use recall, comparison, application, or deeper connection rather than replaying identical text.

The four checked-in example packs MUST each contain exactly 50 valid cards and a coherent beginner-friendly progression:

- Banking Industry and Central Banks: include commercial banking, deposits, lending, reserves, payments, interbank settlement, central-bank mandates, monetary policy tools, inflation, interest rates, lender-of-last-resort concepts, bank runs, regulation, and common misconceptions.
- Economics: include scarcity, opportunity cost, incentives, marginal thinking, supply and demand, markets, externalities, public goods, inflation, unemployment, productivity, trade, business cycles, institutions, and limits of models.
- Children Rearing, Development and Care: include developmental stages, attachment, language, play, sleep, nutrition boundaries, safety, discipline, emotion regulation, learning differences, caregiver wellbeing, and professional-guidance boundaries without individualized medical advice.
- Personal Investments for Total Beginners: include saving versus investing, risk, diversification, index funds, bonds, inflation, compounding, fees, liquidity, time horizon, tax-advantaged accounts at a high level, behavioral mistakes, scams, and educational boundaries without individualized financial advice.

## Feed ordering, interactions, notes, progress, and attention safeguards

Specify a snap-card feed that presents one primary card per viewport with stable previous/next continuity. Use CSS scroll snap or an equivalent native-feeling mechanism. Scrolling MUST remain responsive, interruptible, and free from scroll traps. The feed MUST support touch scroll, wheel/trackpad, Page Up/Down, arrow keys, explicit Previous/Next controls, deep links to the active card when useful, and restoration of the user's last position without unexpected jumps after content loads.

The app MUST start in a pack library showing purpose, level, card count, progress, and last position. Opening a pack resumes or starts a session. The full-height card view MUST keep frequent actions reachable without covering primary content. Touch targets MUST be at least 44 by 44 CSS pixels with adequate spacing. Every gesture MUST have an obvious control alternative and keyboard equivalent; swipe, long-press, pinch, or drag MUST NOT be the only way to complete an action.

Support Like, Save, Revisit, Add/edit note, Share/copy link, and optional `I understand this` self-rating. Actions MUST expose selected state, accessible names, success/failure feedback, persistence behavior, and undo where appropriate. Do not trigger actions merely because scrolling crossed a threshold; distinguish viewed, engaged, completed, and intentionally dismissed states.

The note editor MUST remain reachable above the mobile keyboard, respect safe-area insets and dynamic viewport units, preserve drafts when the keyboard, sheet, route, backgrounding, reload, or app close occurs unexpectedly, and restore focus and scroll context when dismissed. Saved cards, notes, history, per-pack progress, ordered/shuffled modes, text-size controls, reduced motion, and a resettable onboarding explanation MUST be present.

Define a deterministic, testable ranking policy with an optional seed. Persist enough state to reconstruct the session order. Default ordering for eligible unseen cards MUST be:

1. Exclude cards with unsatisfied prerequisites.
2. Normalize each eligible card's declared signals to `[0, 1]`.
3. Score `0.50 * importance + 0.20 * foundational_priority + 0.15 * coverage_gap + 0.10 * recent_category_diversity + 0.05 * seeded_jitter`.
4. Choose the highest score and break exact ties by stable card ID.

Importance MUST remain greater than random jitter. Provide explicit ordered mode in addition to adaptive or shuffled mode. Avoid accidental immediate repetition. If a card returns for review, label why it returned and present a deeper or recall-oriented treatment from `review_prompts`. Schedule at most one revisit among five new-card interactions by default unless the user explicitly opens a review-only session. Never let likes, dwell time, saves, or other engagement metrics silently override prerequisite safety, learning value, source policy, or attention safeguards.

Show subtle pack progress and elapsed session time without interrupting every card. After 10 cards or 10 minutes, offer a calm stopping point with what was learned and where to resume. Continuing MUST be a conscious action, not an obstructed default. The app MUST never shame the user for stopping, losing a streak, skipping, forgetting, or not completing a pack.

## IndexedDB state, export/import, privacy, and recovery

Bundled packs are immutable application content. Store preferences, progress, session order, likes, saves, revisit choices, understanding signals, note drafts, committed notes, history, onboarding state, cache metadata, and import/export recovery records locally in IndexedDB under versioned schemas. Use repository/service interfaces; UI code MUST NOT perform raw storage queries.

Specify an IndexedDB database name, versioning strategy, migrations, object stores, indexes, unique constraints, nullable fields, defaults, lifecycle states, and recovery behavior. All timestamps MUST be UTC ISO 8601 with timezone offset. Every mutable entity MUST have a lifecycle: creation, valid states, update rules, deletion or archival, export/import handling, and migration behavior.

At minimum, define stores for:

- Pack cache metadata keyed by pack ID, content version, and checksum.
- Per-pack progress keyed by pack ID.
- Session order snapshots keyed by pack ID and session ID.
- Card interaction state keyed by pack ID and card ID.
- Notes and note drafts keyed by pack ID and card ID.
- Saved cards and revisit queue entries.
- History events with bounded retention.
- Preferences including text size, reduced motion preference, ordered/shuffled mode, and onboarding reset.
- Import/export transactions and rollback snapshots.

Handle concurrency and race conditions for shared mutable state. Specify transaction boundaries for note saves, draft preservation, session-order creation, import rollback, pack update reconciliation, and destructive reset. Avoid accidental destructive actions near common scrolling gestures; require confirmation or undo for consequential changes.

Provide explicit JSON export/import. Export MUST include user-owned local state and enough metadata to validate compatibility without bundling immutable pack content unnecessarily. Import MUST validate schema version, preview changes, detect duplicates, show conflicts, support merge/replace choices where safe, reject incompatible pack IDs or card IDs unless the user explicitly accepts orphan handling, and provide rollback on failure. Duplicate handling MUST be deterministic and explained before commit.

No account, analytics profile, remote sync, ads, or notification permission is required. Do not send notes, progress, understanding signals, or content interactions to a server. State privacy plainly in the README and onboarding. Provide recovery states for IndexedDB unavailable, quota exceeded, corrupted import file, failed migration, incompatible pack update, and unsupported browser.

## Interface states, accessibility, responsive behavior, and visual direction

Design from a 320 CSS-pixel viewport outward. Desktop layouts MAY add context, columns, and shortcuts, but MUST NOT contain capabilities unavailable on mobile. Keep the primary task reachable with one thumb and place frequent actions near the lower-middle interaction zone without colliding with browser or OS chrome. Respect safe-area insets, dynamic viewport units, virtual keyboards, orientation changes, and standalone installed-display mode.

Use a small, stable information architecture: pack library, active pack feed, card detail or expansion, notes, saved cards, history, settings, import/export, and help/onboarding. Primary navigation MUST remain understandable without hover, right-click, or precision pointing. Preserve scroll position, active card, selected item, unfinished input, and focus across navigation, rotation, backgrounding, and reload where appropriate. Progressive disclosure SHOULD be used instead of dense dashboards.

Accessibility MUST include semantic HTML, accessible native controls where possible, visible focus, keyboard-complete interactions, sufficient contrast, screen-reader labels for icon-only controls, reduced-motion support, text zoom, logical heading order, landmark regions, and status messages for asynchronous changes. Component display rules MUST treat the native `hidden` attribute as authoritative and MUST NOT accidentally reveal inactive states.

The interface MUST provide meaningful first-run, onboarding, loading, empty, active, dirty, saved, conflict, offline, unsupported-browser, error, stale, permission-limited, import-preview, rollback, and recovery states. Cards MUST remain legible in narrow columns, dense desktop contexts, and detail panes. If cards expand, pin, save, dismiss, revisit, or reorder, define persistence and undo behavior. Click, double-click, context menu, selection, inline editing, and scrolling behaviors MUST be unambiguous and non-conflicting.

Visual direction: focused, inviting, tactile, warm paper, deep ink, one restrained accent per pack, excellent typography, and illustrations only when they teach. Use borders, shadows, color, badges, and icons only when they clarify grouping, status, or action. Avoid academic sterility, gamified excess, fake social proof, noisy badges, and decorative media. Engagement indicators MUST serve learning and orientation rather than obscure elapsed time.

Test touch scrolling, virtual-keyboard input, reduced motion, text zoom, screen readers, offline reload, safe-area behavior, orientation changes, viewport widths from 320 CSS pixels through desktop, rapid direction changes, momentum scrolling, accidental taps, action-state persistence, note drafts, restored position, and feeds large enough to activate incremental rendering or virtualization.

## File tree, implementation sequence, tests, and acceptance criteria

The deliverable MUST be a complete static implementation under `outputs/implementations/knowledge-cards/`, including all example packs, schemas, deterministic pack-index/validation command, local-state repository, tests, README, and GitHub Pages-ready assets. Include a concrete file tree with paths and responsibilities. At minimum, cover:

- `index.html`
- `src/` ES modules for app bootstrap, routing, UI components, domain services, repositories, workers, utilities, and safe rendering.
- `styles/` or equivalent CSS for tokens, layout, cards, feed, dialogs/sheets, accessibility, and responsive behavior.
- `schemas/` for pack index, manifest, cards, source refs, review prompts, and export/import.
- `content/packs/index.json`
- `content/packs/<pack-id>/manifest.json`
- `content/packs/<pack-id>/cards/*.json` or an equivalent manifest-declared content layout.
- Optional `content/packs/<pack-id>/media/` files.
- `tools/` validation and index-generation command.
- `tests/` for unit, schema, content, storage, and Playwright browser flows.
- `README.md`

Specify an implementation sequence that reduces risk: static shell, schema definitions, content validation/index command, example pack generation and review, pack library, feed renderer, deterministic ordering, IndexedDB repositories, note/action flows, import/export, offline/cache behavior, accessibility pass, Playwright coverage, README, and GitHub Pages deployment check.

Testing MUST include unit tests for domain/storage modules, schema tests for every pack and export/import shape, deterministic ordering tests including the `0.50 * importance` scoring policy, validation-command tests, migration tests, import/export rollback tests, and Playwright tests for critical browser flows. Playwright coverage MUST include narrow viewports, keyboard navigation, screen-reader-relevant labels, offline/static-host behavior, note drafts above the mobile keyboard, saved cards, revisit explanations, stopping points after 10 cards or 10 minutes, reduced motion, text-size controls, deep links, reload restoration, and bad-pack isolation.

Acceptance criteria MUST be concrete and checkable:

- The app runs from static files with relative URLs under a repository subpath.
- No backend, runtime LLM, analytics profile, remote sync, ads, or notification permission is required.
- Adding a valid `content/packs/<pack-id>/` directory and regenerating `content/packs/index.json` makes the pack discoverable without application-code changes.
- All four required packs contain exactly 50 valid cards and pass curriculum, source, safety, prerequisite, duplicate, and schema validation.
- The feed is one-card-at-a-time, mobile-first, keyboard-complete, and gesture-alternative complete.
- Local state persists in IndexedDB under versioned schemas and supports validated JSON export/import with preview, duplicate handling, and rollback.
- Pack content is immutable application content and user state is never confused with bundled content.
- Attention safeguards are visible and testable, including stopping points and non-shaming progress.
- Browser tests pass with no uncaught page errors and no unexpected console errors/warnings.
- The README names the local development command, test command, content-index/validation command, canonical data boundary, browser support, deployment steps, privacy posture, and known limitations.

Return the final answer as `# Knowledge Cards` followed by exactly these eight H2 sections in this order, with no preface, no extra H2 sections, and no repeated outline.