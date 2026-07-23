# Knowledge Cards

Write an implementation-ready specification for a polished mobile-first web app that turns the familiar one-card-at-a-time social feed into cumulative learning. The app runs entirely as static HTML, CSS, and JavaScript ES modules with no backend, no server routes, no serverless functions, no separately installed local service, and no runtime LLM calls.

The specification MUST be concrete enough for a programmer to build, test, and validate the system. Use RFC 2119 keywords precisely. Every requirement MUST be testable; name concrete data structures, schemas, algorithms, files, commands, UI states, validation gates, error states, and acceptance criteria. Preserve exact literal paths and identifiers such as `content/packs/<pack-id>/`, `content/packs/index.json`, `manifest.json`, `IndexedDB`, `runtime LLM`, and `outputs/implementations/knowledge-cards/`.

The final answer MUST start with `# Knowledge Cards`, then contain exactly eight H2 sections in this order and with these exact names. Do not add a preface, extra H2 sections, a repeated outline, or source-composition commentary.

## Product promise, learning model, and non-goals

Specify the product as a focused, inviting, tactile learning app: warm paper, deep ink, one restrained accent per pack, excellent typography, and illustrations only when they teach. Treat social-feed familiarity as an interaction shortcut, not permission for dark patterns, fake popularity, autoplay, manipulative streaks, randomized rewards unrelated to learning, forced sharing, notification pressure, fake urgency, or attention extraction.

Define the learning model around coherent knowledge-card packs for these four topics:

1. Banking Industry and Central Banks
2. Economics
3. Children Rearing, Development and Care
4. Personal Investments for Total Beginners

Each pack MUST contain exactly 50 cards. Each card teaches exactly one meaningful concept. The complete pack MUST teach the important shape of its field rather than a bag of trivia. Require a concept map before cards are authored: foundations, mechanisms, applications, misconceptions, limitations, bridges, and advanced horizons. Assign every candidate concept importance, prerequisite depth, difficulty, novelty, and relationship metadata. Select by importance before randomness; favor foundations early, then interleave mechanisms, applications, misconceptions, and occasional surprising bridges.

State non-goals explicitly: no account system, no analytics profile, no remote sync, no ads, no notification permission requirement, no engagement optimization, no backend content generation, no runtime LLM, no executable HTML or JavaScript inside content packs, and no claim that automated validation proves factual correctness unless a recorded semantic review actually supports that claim.

Include topic-sensitive education boundaries. Health, child-development, financial, legal, or safety-sensitive cards MUST remain educational, avoid individualized advice, date stale-prone claims, distinguish consensus from simplification or uncertainty, and direct users toward qualified professional or primary guidance when action could cause harm.

## Static architecture, mobile shell, and offline lifecycle

Specify a static browser architecture using semantic HTML, modern CSS, and standards-based JavaScript ES modules. The deployable root MUST include an `index.html` that works under a repository subpath such as GitHub Pages. All asset URLs MUST be relative. Required JavaScript, CSS, WebAssembly, fonts, schemas, example packs, and media MUST be hosted with the application; core behavior MUST NOT depend on a mutable third-party CDN.

Define the deliverable under `outputs/implementations/knowledge-cards/`, including GitHub Pages-ready checked-in assets, example packs, schemas, deterministic validation/index tooling, local-state repository code, tests, and README.

Require a small, typed module boundary even in plain JavaScript. UI modules MUST NOT issue raw storage queries. Keep domain state behind repository/service interfaces. Validate every imported file before it reaches domain state. Use Web Workers for CPU-heavy pack parsing, validation, indexing, search, migration, export/import validation, or transformation work so the main thread remains responsive.

Design mobile-first from a 320 CSS-pixel viewport outward. Desktop layouts MAY add context, columns, and shortcuts, but MUST NOT contain capabilities unavailable on mobile. Respect safe-area insets, dynamic viewport units, virtual keyboards, orientation changes, text zoom, reduced motion, and standalone installed-display mode. Keep the primary task reachable with one thumb, with frequent actions near the lower-middle interaction zone without colliding with browser or OS chrome.

Specify offline behavior. Core reading, navigation, loaded pack content, local edits, preferences, progress, notes, and saved cards SHOULD continue offline after the static application and required content have loaded. Define cache keys for immutable content by pack ID, content version, and checksum. A bad pack MUST fail in isolation with a useful message while valid packs remain available. Preserve user state across compatible pack updates by stable card ID and report removed or incompatible items instead of silently attaching old state to different content.

Include measurable performance budgets for initial JavaScript, CSS, images, and time-to-interactive on a mid-range phone and constrained network. Lazy-load nonessential media and later content without layout shift; reserve dimensions and provide useful placeholders.

## Pack convention, schemas, discovery, and build-time validation

Specify a manifest-discovered static content convention. Each pack lives in `content/packs/<pack-id>/`. Each pack directory MUST contain `manifest.json` and one or more JSON content files named by the manifest. Optional media lives below the same directory. A generated `content/packs/index.json` MUST act as the static-host-compatible pack index because deployed browsers cannot enumerate directories.

Adding a conforming `content/packs/<pack-id>/` directory and running the documented deterministic content-index command MUST make the pack discoverable without application-code changes. The generated index MUST be stably sorted, reproducible from the pack directories, and checked in for zero-build static hosting.

Publish versioned, closed JSON Schemas for the pack index, pack manifest, and card/content files. Reject unknown schema versions and malformed required fields. Pack IDs and card IDs MUST be stable, URL-safe, unique, and independent of display titles or file order.

A manifest MUST define at least: schema version, ID, title, description, language, audience, level, content version, exact item count, ordered content files, optional media root, authorship/provenance, source policy, license, content checksum, accent/theme metadata, and editorial review metadata. Content items MUST not embed executable HTML or JavaScript; render all text and imported metadata as untrusted data through safe DOM APIs.

Provide one deterministic validation/index command suitable for local use and CI. It scans `content/packs/*/manifest.json`, validates every referenced file, verifies unique IDs and exact counts, rejects path traversal and missing media, computes checksums, and writes `content/packs/index.json`. Validation MUST fail on orphan content, duplicate IDs, undeclared files, checksum drift, unsupported schemas, broken references, missing media, count mismatches, invalid prerequisites, malformed references, unsafe HTML/script fields, or schema-version incompatibility.

Validation reports MUST distinguish deterministic structural checks from source-aware editorial review. Automation MUST NOT claim that facts are correct, citations support claims, or concepts are nonduplicative unless it actually performs and records that semantic review.

Mention that maintained example inputs are checked in beside this promplet as `knowledge-cards.vars.json`, and require the implementation repository to document how those inputs were used to generate or verify the example packs.

## Knowledge-card model, curriculum rules, and example-pack requirements

Define the knowledge-card schema as a specialized card model. Each card MUST include:

- `id`: stable identifier within the pack.
- `title`: short descriptive title.
- `core_idea`: two to five concise paragraphs emphasizing intuition, mechanism, importance, limitations, and relationships.
- `example`: a short practical example, analogy, diagram description, or thought experiment when it improves understanding.
- `key_takeaway`: one memorable sentence capturing the concept.
- `connections`: zero or more related concepts, prepared-for topics, common misconceptions, or real-world applications, preferably using stable card IDs.
- `difficulty`: a small declared scale centered on educated beginners.
- `prerequisites`: stable IDs of cards whose ideas are assumed.
- `source_refs`: references supporting factual or safety-sensitive claims.
- `media`: optional local image or illustration metadata only when it materially clarifies the idea.
- `review_prompts`: optional checked-in recall, comparison, application, or connection questions for deliberate revisits without a runtime model.
- `importance`, `foundational_priority`, `category`, `coverage_tags`, and any deterministic ordering signals required by the feed policy.

Every sentence MUST teach. Avoid filler, motivational copy, encyclopedic detail, long biography, excessive jargon, disconnected definitions, and repeated sentence templates merely to satisfy paragraph-length checks. Teaching style MUST be concise, insightful, approachable, conversational without being casual, and intellectually honest. Prefer intuition and mechanisms over memorization. Explain why the idea matters, where it fails, and what common belief it corrects. Introduce advanced ideas briefly only when they are explained intuitively.

Require each of the four example packs to contain exactly 50 cards, validated prerequisites, no duplicate concepts, and balanced difficulty distribution. A deliberate revisit MUST deepen, connect, contrast, or test recall and MUST name the earlier card relationship. Images clarify; they never decorate.

Define evidence rules. Use a declared source policy for each pack and retain pack-level references with stable IDs. Curate each card's `source_refs` to sources whose declared claim scope fits that card; pack-wide source fan-out is not evidence. Do not invent citations or imply that a source supports more than it does. Review the whole pack for bias, stereotypes, age/culture assumptions, financial promises, medical overreach, and examples that confuse correlation with cause.

## Feed ordering, interactions, notes, progress, and attention safeguards

Specify a snap-card feed that presents one full-height knowledge card at a time with stable previous/next continuity. Vertical touch scrolling is primary; wheel/trackpad, Page Up/Down, arrow keys, and explicit Previous/Next controls MUST be equivalent. Use CSS scroll snap or an equivalent native-feeling mechanism. Scrolling MUST remain responsive, interruptible, and free from scroll traps.

The document/main window MUST be the only vertical scroll container. A knowledge card expands to its full content and MUST NOT use an internal scroll pane. When snapping settles, update the active item, deep link, header, and progress exactly once. Re-rendering an action or note MUST NOT count as another view. Deep-link the active card when useful and restore the user's last position without unexpectedly jumping after content loads. Virtualize or incrementally render long feeds while keeping the active card and immediate neighbors stable and accessible.

Start in a pack library showing purpose, level, card count, progress, and last position. Opening a pack resumes or starts a session. Provide ordered and shuffled/adaptive modes. Persist enough state to reconstruct the session order.

Define the default deterministic, prerequisite-safe ordering policy:

1. Exclude cards with unsatisfied prerequisites.
2. Normalize eligible cards' declared signals to `[0, 1]`.
3. Score `0.50 * importance + 0.20 * foundational_priority + 0.15 * coverage_gap + 0.10 * recent_category_diversity + 0.05 * seeded_jitter`.
4. Choose the highest score and break exact ties by stable card ID.

Importance MUST remain greater than random jitter. Do not optimize for likes, saves, dwell time, or engagement. Avoid accidental immediate repetition. If a card returns for review, label why it returned and present recall, comparison, application, or a deeper connection from `review_prompts` rather than replaying identical text without explanation. Schedule at most one revisit among five new-card interactions by default unless the user explicitly opens a review-only session.

Support Like, Save, Revisit, Add/edit note, Share/copy link, and optional "I understand this" self-rating. Keep frequent actions reachable without covering primary content. Actions MUST expose selected state, accessible names, success/failure feedback, persistence behavior, and undo where appropriate. Notes MUST preserve drafts when the keyboard, sheet, route, app, or browser closes unexpectedly; note entry MUST remain reachable above the mobile keyboard. Distinguish viewed, engaged, completed, intentionally dismissed, liked, saved, revisit, note, and self-rated understanding states; none of these alone proves mastery.

Serialize overlapping local mutations for one card so rapid Like, Save, Revisit, note, or understanding actions cannot overwrite one another. Sticky or fixed action and navigation trays MUST reserve layout space and remain non-overlapping at the smallest supported viewport. Do not trigger actions merely because scrolling crossed a threshold.

Show subtle pack progress and session time. After 10 cards or 10 minutes, offer a calm stopping point with what was learned and where to resume. Continuing must be a conscious action. Never shame the user for stopping, losing a streak, forgetting, or pausing.

## IndexedDB state, export/import, privacy, and recovery

Bundled packs are immutable application content. Store preferences, progress, session order, likes, saves, revisit choices, understanding signals, notes, draft notes, history, onboarding status, text-size controls, reduced-motion preference, and per-pack progress locally in IndexedDB under versioned schemas. Browser storage may cache preferences, permissions, and performance data, but IndexedDB is the canonical durable store for user state.

Define a versioned IndexedDB schema with stores, keys, indexes, defaults, migrations, and lifecycles. Every entity MUST have creation, valid states, update rules, and deletion/reset/archive behavior where applicable. Include concurrency handling for shared mutable state. UI modules MUST access state only through typed repository/service interfaces; raw IndexedDB queries belong in the local-state repository layer.

Preserve scroll position, selected item, unfinished input, note drafts, focus, and session state across navigation, rotation, backgrounding, reload, and offline reload when appropriate. Treat bundled content and user progress as separate data domains. Cache immutable content by pack ID, content version, and checksum; never confuse user progress with bundled pack content.

Provide explicit JSON export/import. Export MUST include schema version, app version, generated timestamp in UTC ISO 8601 with timezone offset, pack progress, session orders, saved cards, likes, revisit choices, understanding signals, notes, preferences, and enough metadata to validate compatibility. Import MUST validate before mutation, show a preview, handle duplicates, detect incompatible pack/content versions, support merge/replace choices, and provide rollback on failure. Destructive reset and import replace operations MUST require confirmation or undo.

Privacy requirements: no account, analytics profile, remote sync, ads, notification permission requirement, or hidden network sharing. External network calls, if any optional link opens or source view fetch is added, require explicit user action and visible destination, purpose, progress, failure, and retry states.

Define meaningful first-run, loading, empty, active, dirty, saved, conflict, unsupported-browser, quota-exceeded, migration-failed, import-invalid, offline, recovery, and reset-complete states. Treat the native `hidden` attribute as authoritative; component display rules MUST NOT accidentally reveal inactive states.

## Interface states, accessibility, responsive behavior, and visual direction

Specify the UI surfaces: pack library, onboarding explanation, active card feed, card detail or expanded content treatment if separate, saved cards, notes, history, settings, export/import, validation error display for local content problems, and recovery/reset views.

Design from 320 CSS pixels upward. Touch targets MUST be at least 44 by 44 CSS pixels with adequate spacing. Primary navigation MUST remain understandable without hover, right-click, or precision pointing. Every gesture MUST have an obvious control alternative and keyboard equivalent; swipe, long-press, pinch, drag, or snap scrolling MUST NOT be the only way to complete an action. Avoid accidental destructive actions near common scrolling gestures.

Require accessible native controls, semantic labels, visible focus, sufficient contrast, keyboard-complete interactions, screen-reader text for icon-only controls, correct heading structure, form labels, error descriptions, reduced-motion support, and responsive layouts through desktop. Support text-size controls and browser zoom without clipping content or hiding actions. Test with screen readers, keyboard-only navigation, reduced motion, text zoom, virtual keyboard input, orientation changes, and widths from 320 CSS pixels through desktop.

Preserve context when a sheet, dialog, keyboard, or detail view opens and closes. Prefer progressive disclosure over dense dashboards. Frequent actions should remain reachable but must not cover card content. Sticky/fixed UI MUST reserve layout space and respect safe-area insets.

Visual direction: focused, inviting, tactile, non-academic, and non-gamified. Use warm paper surfaces, deep ink, high-quality type scale, readable line length, generous spacing, and one restrained accent per pack. Use borders, shadows, badges, and icons only when they clarify grouping, status, or action. Illustrations and media MUST materially clarify a concept and include dimensions/placeholders to avoid layout shift.

## File tree, implementation sequence, tests, and acceptance criteria

Require a complete static implementation under `outputs/implementations/knowledge-cards/`. Specify a concrete file tree including at least:

- `index.html`
- application ES modules under an app/source directory
- CSS/theme files
- `content/packs/index.json`
- `content/packs/<pack-id>/manifest.json`
- JSON card files and optional media under each pack directory
- JSON Schemas for pack index, manifest, and card/content files
- deterministic validation/index command and supporting scripts
- IndexedDB repository/service modules and migrations
- tests for schemas, ordering, storage, import/export, UI flows, accessibility, offline behavior, and static-host deployment
- README with local development command, validation/index command, test command, deployment instructions, canonical data boundary, browser support, and known limitations

Provide an implementation sequence that starts with schemas and validation, then content pack scaffolding, static shell, repository layer, pack loading, feed ordering, card UI, interactions, notes, progress, export/import, offline caching, accessibility, visual polish, tests, and deployment verification.

Testing requirements MUST include unit tests for domain/storage modules, schema validation tests, deterministic ordering tests with fixed seeds, migration tests, import/export rollback tests, and Playwright tests for critical browser flows. Playwright coverage MUST include narrow viewports, touch-equivalent scrolling, keyboard navigation, note draft preservation above the mobile keyboard, rapid direction changes, momentum scrolling, accidental taps, action-state persistence, restored position, reduced motion, offline/static-host behavior, unsupported-browser and recovery states, and no uncaught page errors or unexpected console errors/warnings.

Acceptance criteria MUST be written as checkable bullets. Include that all four example packs contain exactly 50 cards, `content/packs/index.json` is generated deterministically, adding a valid pack requires no application-code changes, the app runs from static hosting under a repository subpath, all asset URLs are relative, the app works offline after first load of required content, document/main is the only vertical scroll container, cards do not have internal vertical scroll panes, IndexedDB stores versioned local state, export/import validates and rolls back safely, no runtime LLM calls occur, and attention safeguards prevent dark-pattern engagement optimization.