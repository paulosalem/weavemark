# Knowledge Cards

## Product promise, learning model, and non-goals

Build a polished mobile-first static web app that turns a familiar one-card-at-a-time social feed into cumulative learning. The app runs entirely as static HTML, CSS, and JavaScript ES modules with no backend, no account system, no analytics profile, no remote sync, no ads, and no notification permission requirement.

The first build MUST deliver a complete static implementation under `outputs/implementations/knowledge-cards/`, including GitHub Pages-ready assets, example content packs, schemas, validation/indexing tools, local-state persistence, tests, and README documentation.

The product promise is focused learning, not engagement extraction:

- Learners browse coherent curriculum packs one full-height knowledge card at a time.
- Each card teaches exactly one meaningful concept.
- Feed mechanics are used only as an interaction shortcut: fast, familiar, tactile navigation through a curated sequence.
- The system MUST make no runtime LLM calls. Pack content and optional explanatory media are pre-generated, reviewed, versioned, validated, and checked in.
- Adding a conforming `content/packs/<pack-id>/` directory and regenerating the static pack index MUST make the pack discoverable without application-code changes.

Pre-generate one coherent pack for each topic below, with exactly 50 cards per pack:

1. Banking Industry and Central Banks
2. Economics
3. Children Rearing, Development and Care
4. Personal Investments for Total Beginners

The maintained example inputs are checked in beside this promplet as `knowledge-cards.vars.json`.

Non-goals for the first build:

- No server routes, server actions, serverless functions, installed local service, mutable CDN dependency for core behavior, or runtime content generation.
- No personalized financial, medical, legal, child-development, or safety advice. Sensitive cards are educational, bounded, and point to qualified professional or primary guidance when action could cause harm.
- No fake popularity, infinite-scroll manipulation, autoplay engagement loops, shame, loss-framed streaks, forced sharing, randomized rewards unrelated to learning, or deceptive urgency.
- No assumption that likes, dwell time, or self-rated understanding prove mastery.

The specification is the source of truth for implementation. Every requirement should be testable through code, content validation, browser tests, manual checks, or documented acceptance criteria.

## Static architecture, mobile shell, and offline lifecycle

Use semantic HTML, modern CSS, and standards-based JavaScript ES modules. Prefer browser standards over frameworks. A small deterministic build step is allowed, but the deployable application MUST run from static hosting without Node.js at runtime.

Required runtime shape:

- Deployable root contains `index.html` that works under a repository subpath such as GitHub Pages.
- All asset URLs are relative.
- Required JavaScript, CSS, WebAssembly, fonts, icons, example data, schemas, and media are hosted with the application, not pulled from mutable third-party CDNs for core behavior.
- Browser storage, content loading, validation, repository access, ordering, and UI state live behind typed repository/service interfaces. UI modules MUST NOT issue raw storage queries.
- Web Workers SHOULD be used for CPU-heavy pack validation, checksum work, indexing support, import/export validation, search, or large transformations so the main thread remains responsive.
- External network calls are out of scope for core behavior. If any optional external link or share target is opened, it requires explicit user action and visible destination/purpose.

Mobile shell requirements:

- Design from a 320 CSS-pixel viewport outward.
- Desktop layouts MAY add context, columns, and keyboard shortcuts, but MUST NOT contain capabilities unavailable on mobile.
- Primary reading and navigation are reachable with one thumb. Frequent controls sit near the lower-middle interaction zone without colliding with browser or OS chrome.
- Respect safe-area insets, dynamic viewport units, virtual keyboards, orientation changes, and standalone installed-display mode.
- Preserve context when a sheet, dialog, keyboard, detail view, route, or browser backgrounding event opens and closes.
- Use progressive disclosure instead of dense dashboards.

Offline lifecycle:

- Core reading, navigation, progress tracking, notes, likes, saves, revisit choices, text-size preferences, onboarding state, and import/export SHOULD continue offline after the static app and required pack content have loaded.
- Load the pack index first, then manifests and content files on demand.
- Cache immutable bundled content by pack ID, content version, and checksum.
- A bad pack MUST fail in isolation with a useful message while valid packs remain available.
- Never confuse user progress with bundled pack content.
- Preserve user state across compatible pack updates by stable card ID. Report removed or incompatible items rather than silently attaching old state to changed content.

Performance budgets for the first build:

- Meaningful first content appears quickly on a mid-range phone.
- Initial JavaScript and CSS stay small enough to make static hosting and mobile loading credible; document exact measured sizes in the README.
- Lazy-load nonessential media and later content without layout shift. Reserve media dimensions and show useful placeholders.
- Browser validation finishes with no uncaught page errors and no unexpected console errors or warnings.

## Pack convention, schemas, discovery, and build-time validation

Each learning pack is immutable application content stored under `content/packs/<pack-id>/`.

Directory convention:

- Each pack directory MUST contain `manifest.json`.
- Each pack directory MUST contain one or more JSON content files named by its manifest.
- Optional local media lives below the same pack directory.
- The application ships a generated `content/packs/index.json` for static-host-compatible discovery. Browsers cannot enumerate deployed directories.
- Adding a valid `content/packs/<pack-id>/` directory and running the documented content-index command MUST make the pack available without editing application source.

Publish versioned, closed JSON Schemas for:

- `content/packs/index.json`
- pack `manifest.json`
- card content files
- optional media metadata
- export/import files for local user state

Reject unknown schema versions, malformed required fields, unknown properties, duplicate IDs, unsafe paths, and unsupported content versions.

Pack identity requirements:

- Pack IDs and card IDs are stable, URL-safe, unique, and independent of display titles or file order.
- A manifest defines at least: schema version, pack ID, title, description, language, audience, level, content version, item count, ordered content files, optional media root, authorship/provenance, source policy, license, content checksum, and publication/review metadata.
- Content items MUST NOT embed executable HTML or JavaScript. Treat all text and imported metadata as untrusted data rendered through safe DOM APIs.
- Item-level `source_refs` MUST be curated to the claims on that item. Never attach every pack-level source mechanically when their declared scopes differ.

Provide one deterministic validation/index command suitable for local use and CI. It MUST:

- scan `content/packs/*/manifest.json`;
- validate every referenced file against the correct schema;
- verify stable unique pack and card IDs;
- verify exact card counts, including exactly 50 cards for each required example pack;
- reject path traversal, absolute paths, undeclared files, orphan content, missing media, unsupported schema versions, broken references, duplicate IDs, checksum drift, and count mismatches;
- compute content checksums;
- write a stably sorted `content/packs/index.json`;
- produce reproducible output from the pack directories;
- fail CI when generated indexes or checksums are stale.

Validation reports MUST distinguish deterministic structural checks from source-aware editorial review. Automation MUST NOT claim that facts are correct, citations support claims, or concepts are nonduplicative unless it actually performs and records that semantic review.

## Knowledge-card model, curriculum rules, and example-pack requirements

Before writing cards for a topic, construct a concept map covering foundations, mechanisms, applications, misconceptions, limitations, bridges, and advanced horizons. Assign each candidate concept importance, prerequisite depth, difficulty, novelty, and relationship sets. The complete pack MUST teach the important shape of the field rather than a bag of trivia.

Each pack contains exactly 50 cards. Each card teaches exactly one meaningful concept and uses this closed content model:

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

Every sentence MUST teach. Avoid filler, motivational copy, encyclopedic detail, long biography, excessive jargon, disconnected definitions, and repeated sentence templates added merely to satisfy paragraph-length checks.

Curriculum rules:

- Select concepts by importance before randomness.
- Favor foundations early, then interleave mechanisms, applications, misconceptions, and occasional surprising bridges so the sequence stays varied without becoming incoherent.
- Never duplicate a concept.
- A deliberate revisit MUST deepen, connect, contrast, or test recall and MUST name the earlier card relationship.
- Validate each complete pack for concept coverage, prerequisite violations, accidental repetition, unsupported claims, difficulty distribution, useful cross-links, and sensitive-domain boundaries before publication.

Teaching style:

- Concise, insightful, approachable, conversational without being casual, and intellectually honest.
- Prefer intuition and mechanisms over memorization.
- Explain why the idea matters, where it fails, and what common belief it corrects.
- Introduce advanced ideas briefly only when explained intuitively.
- Use concrete memorable examples. Images clarify; they never decorate.

Evidence and safety:

- Use a declared source policy for each pack and retain pack-level references with stable IDs.
- Do not invent citations or imply that a source supports more than it does.
- Date claims that can become stale.
- Distinguish consensus, useful simplification, debated interpretation, and uncertainty.
- Banking, economics, personal-investment, child-development, health, legal, and safety-sensitive cards MUST state their educational boundary, avoid individualized advice, and point to qualified professional or primary guidance when action could cause harm.
- Review packs for bias, stereotypes, age/culture assumptions, financial promises, medical overreach, and examples that confuse correlation with cause.

Example-pack content requirements:

- Banking Industry and Central Banks: include money creation, deposits, lending, reserves, central-bank tools, payment systems, regulation, bank runs, deposit insurance, inflation links, financial stability, and everyday banking misconceptions.
- Economics: include scarcity, incentives, opportunity cost, supply and demand, markets, firms, labor, inflation, unemployment, trade, externalities, public goods, measurement limits, and policy trade-offs.
- Children Rearing, Development and Care: include developmental stages, attachment, sleep, feeding, language, play, boundaries, safety, childcare choices, neurodiversity-aware framing, caregiver wellbeing, and when to seek qualified help.
- Personal Investments for Total Beginners: include risk, return, diversification, fees, compounding, time horizon, emergency funds, index funds, asset allocation, inflation, taxes at a high level, behavioral mistakes, scams, and the boundary between education and individualized financial advice.

## Feed ordering, interactions, notes, progress, and attention safeguards

Start in a pack library showing each pack's purpose, level, card count, progress, and last position. Opening a pack resumes or starts a session.

Feed contract:

- Show one full-height knowledge card at a time.
- Vertical touch scrolling is primary.
- CSS scroll snap or an equivalent native-feeling mechanism MUST keep previous/next continuity stable.
- Scrolling remains responsive, interruptible, and free from scroll traps.
- The document/main window MUST be the only vertical scroll container. A knowledge card expands to its full content and MUST NOT use an internal scroll pane.
- Support touch scroll, wheel/trackpad, Page Up/Down, arrow keys, and explicit Previous/Next controls.
- Preserve normal browser back behavior.
- Deep-link the active card when useful and restore the user's last position without unexpectedly jumping after content loads.
- Virtualize or incrementally render long feeds only if the active card and immediate neighbors remain stable, accessible, and testable.
- When snapping settles, update the active item, deep link, header, and progress exactly once. Re-rendering an action or note MUST NOT count as another view.

Ordering policy:

- Support ordered mode and deterministic mixed mode.
- Persist enough state to reconstruct the session order.
- Order unseen cards with a deterministic, prerequisite-safe mix of importance, foundational value, variety, and bounded randomness.
- Never optimize for likes or dwell time.
- Importance MUST weigh more than random jitter.
- Avoid accidental immediate repetition.
- Explain deliberate revisits.

Default deterministic mixed-mode algorithm:

1. Exclude unseen cards with unsatisfied prerequisites.
2. Normalize each eligible card's declared signals to `[0, 1]`.
3. Score each eligible card as `0.50 * importance + 0.20 * foundational_priority + 0.15 * coverage_gap + 0.10 * recent_category_diversity + 0.05 * seeded_jitter`.
4. Choose the highest score.
5. Break exact ties by stable card ID.
6. Use a persisted pack/session seed so order is reconstructable.

Revisit policy:

- User-selected Revisit MAY schedule a concept again.
- Repeated interactions use recall, comparison, application, or deeper connection prompts from `review_prompts` rather than replaying identical text without explanation.
- Schedule at most one revisit among five new-card interactions by default unless the user explicitly opens a review-only session.

Actions and notes:

- Support Like, Save, Revisit, Add/edit note, Share/copy link, and optional “I understand this” self-rating.
- Keep frequent actions reachable without covering primary content.
- Actions MUST expose selected state, accessible names, success/failure feedback, persistence behavior, and undo where appropriate.
- Notes MUST preserve drafts when the keyboard, sheet, route, or app closes unexpectedly.
- Keep note entry reachable above the mobile keyboard.
- Do not trigger actions merely because scrolling crossed a threshold; distinguish viewed, engaged, completed, intentionally revisited, liked, saved, and self-rated states.
- Serialize overlapping local mutations for one card so rapid Like, Save, Revisit, note, or understanding actions cannot overwrite one another.
- Sticky or fixed action/navigation trays MUST reserve layout space and remain non-overlapping at the smallest supported viewport.

Progress and attention safeguards:

- Show subtle pack progress and session time.
- After 10 cards or 10 minutes, offer a calm stopping point with what was learned and where to resume.
- Continuing is a conscious action, not an obstructed default.
- Never shame the user for stopping, losing a streak, or taking time.
- Avoid autoplay media, fake social proof, infinite loading spinners, manipulative streak loss, notification prompts unrelated to learning, randomized rewards, and engagement patterns that obscure elapsed time.

## IndexedDB state, export/import, privacy, and recovery

Bundled packs are immutable application content. Store user state locally in IndexedDB under versioned schemas. No account, analytics profile, remote sync, ads, or notification permission is required.

Persist at least:

- preferences;
- onboarding state;
- selected text size and reduced-motion preference where app-specific;
- per-pack progress;
- session order and seed;
- last active pack/card position;
- seen history;
- likes;
- saves;
- revisit choices;
- understanding signals;
- notes and note drafts;
- ordered/shuffled mode selection;
- import/export metadata;
- recovery markers for interrupted writes.

Storage design:

- Keep IndexedDB access behind a repository layer.
- Use versioned object stores and deterministic migrations.
- Define every persisted field with type, constraints, default, lifecycle, and indexing needs in code comments or schema docs.
- Store timestamps as UTC ISO 8601 values with timezone offsets.
- Serialize mutations for a single pack/card/user-state record to prevent race conditions.
- Treat browser storage quota, private browsing limitations, blocked IndexedDB, and corrupted state as recoverable conditions with clear UI.
- Never attach state for one content version to incompatible content without an explicit compatibility rule.

Export/import:

- Provide explicit JSON export and import.
- Export includes schema version, app version, creation timestamp, pack IDs, content versions/checksums, preferences, progress, likes, saves, revisit choices, understanding signals, notes, and history.
- Import validates schema version, pack identity, content version/checksum compatibility, duplicate entries, malformed notes, unsafe sizes, and unknown fields before modifying state.
- Import flow shows a preview, duplicate handling choices, and a rollback path.
- Failed import leaves existing state unchanged.
- Successful import records an audit summary visible to the user.

Privacy:

- All learning state stays local unless the user explicitly exports or shares it.
- Share/copy link copies only a pack/card reference and any explicit user-selected text, not private notes by default.
- Do not collect analytics or create a remote identity.
- Do not request notification permission.

Recovery states:

- First run with no packs loaded.
- Valid pack unavailable because of cache/storage failure.
- Unsupported browser or disabled IndexedDB.
- Corrupted local state with reset/export-before-reset options where possible.
- Import conflict.
- Pack update removes or changes cards that have user state.

## Interface states, accessibility, responsive behavior, and visual direction

The app should feel focused, inviting, and tactile rather than academic or gamified: warm paper, deep ink, one restrained accent per pack, excellent typography, and illustrations only when they teach.

Required interface states:

- first-run onboarding explaining packs, one-card feed navigation, local-only state, notes, revisits, and stopping points;
- pack library with loading, empty, error, active, and progress states;
- pack detail/preview where useful;
- active card feed;
- saved cards view;
- notes view;
- history view;
- review-only session view;
- calm stopping-point summary;
- import/export preview and result states;
- reset confirmation and recovery state;
- unsupported-browser state;
- offline-ready and offline-limited states.

Accessibility requirements:

- Use accessible native controls whenever possible.
- Touch targets are at least 44 by 44 CSS pixels with adequate spacing.
- Every gesture has an obvious control alternative and keyboard equivalent.
- Swipe, long-press, pinch, or drag MUST NOT be the only way to complete an action.
- Provide visible focus, semantic labels, screen-reader text for icon-only controls, sufficient contrast, and reduced-motion support.
- Preserve focus and scroll position across navigation, rotation, reload, backgrounding, sheets, dialogs, and keyboard open/close when appropriate.
- Avoid accidental destructive actions near common scrolling gestures; provide confirmation or undo for consequential changes.
- The native `hidden` attribute is authoritative; component display rules MUST NOT accidentally reveal inactive states.
- Test with keyboard, screen readers, text zoom, reduced motion, offline reload, virtual keyboard input, and widths from 320 CSS pixels through desktop.

Responsive behavior:

- Mobile is complete, not a reduced feature set.
- Desktop may add a wider pack library, side context, or keyboard shortcut hints without changing the core information architecture.
- Primary reading content uses the document as its single vertical scroll owner.
- Cards remain legible in narrow columns and on larger screens.
- Fixed or sticky controls reserve layout space and respect safe-area insets.
- Media placeholders reserve dimensions to avoid layout shift.

Visual direction:

- Warm paper background, deep ink text, and strong readable contrast.
- One restrained accent per pack, derived from pack metadata.
- Typography prioritizes reading comfort, rhythm, and hierarchy.
- Badges and metadata are compact and meaningful.
- Motion is subtle, interruptible, and disabled or simplified under reduced motion.
- Illustrations, diagrams, and media appear only when they clarify the concept.

## File tree, implementation sequence, tests, and acceptance criteria

Deliver the complete implementation under `outputs/implementations/knowledge-cards/`.

Expected file tree:

```text
outputs/implementations/knowledge-cards/
  index.html
  README.md
  package.json
  playwright.config.js
  src/
    main.js
    app.js
    router.js
    state/
      db.js
      migrations.js
      repositories.js
      exportImport.js
    content/
      packLoader.js
      schemas.js
      validator.js
      ordering.js
    ui/
      packLibrary.js
      feed.js
      cardView.js
      actions.js
      notes.js
      stoppingPoint.js
      settings.js
      importExport.js
      recovery.js
    workers/
      validationWorker.js
    styles/
      base.css
      layout.css
      cards.css
      themes.css
  content/
    schemas/
      pack-index.schema.json
      manifest.schema.json
      cards.schema.json
      user-export.schema.json
    packs/
      index.json
      banking-industry-and-central-banks/
        manifest.json
        cards.json
        media/
      economics/
        manifest.json
        cards.json
        media/
      children-rearing-development-and-care/
        manifest.json
        cards.json
        media/
      personal-investments-for-total-beginners/
        manifest.json
        cards.json
        media/
  tools/
    validate-content.mjs
    build-pack-index.mjs
  tests/
    unit/
      ordering.test.js
      repositories.test.js
      validation.test.js
      exportImport.test.js
    e2e/
      pack-library.spec.js
      feed-navigation.spec.js
      notes-actions.spec.js
      import-export.spec.js
      offline-static.spec.js
      accessibility.spec.js
```

Implementation sequence:

1. Create the static shell, relative asset loading, CSS foundations, and route structure.
2. Define closed JSON Schemas for pack index, manifests, card files, and user export/import.
3. Implement deterministic content validation and pack-index generation.
4. Add the four required 50-card example packs and generated `content/packs/index.json`.
5. Implement pack loading, isolated bad-pack handling, checksums, and offline-friendly caching.
6. Implement IndexedDB repositories, migrations, serialized card mutations, and recovery states.
7. Implement the pack library, feed, card rendering, controls, notes, saved/history/review views, settings, and stopping point.
8. Implement deterministic ordering and revisit scheduling.
9. Implement JSON export/import with validation, preview, duplicate handling, and rollback.
10. Add unit tests for ordering, validation, repositories, migrations, and import/export.
11. Add Playwright tests for narrow viewports, scroll snap, keyboard navigation, action persistence, note drafts, restored position, offline static hosting, import/export, reduced motion, and accessibility smoke checks.
12. Write the README with local development command, validation/index command, test command, deployment instructions, canonical data boundary, browser support, content authoring process, and known limitations.

Test commands and checks MUST be documented in README. The project SHOULD include deterministic npm scripts such as:

```text
npm run validate:content
npm test
npm run test:e2e
```

Acceptance criteria:

- `index.html` runs from static hosting and under a repository subpath with only relative assets.
- The app makes no runtime LLM calls and requires no backend.
- The pack library lists all four required packs from `content/packs/index.json`.
- Each required pack contains exactly 50 valid cards.
- Adding a conforming `content/packs/<pack-id>/` directory and rerunning the index command updates discovery without application-code changes.
- Invalid packs fail in isolation with useful messages.
- One full-height card is shown at a time; the document/main window is the only vertical scroll container.
- Touch, wheel/trackpad, keyboard, and explicit controls all navigate the feed.
- Like, Save, Revisit, notes, Share/copy link, and optional understanding signals persist correctly in IndexedDB.
- Note drafts survive keyboard open/close, route changes, reload, and backgrounding where browser storage permits.
- Ordering is deterministic, prerequisite-safe, reconstructable, and not optimized for likes or dwell time.
- Progress and session time are visible without manipulation; after 10 cards or 10 minutes, the app offers a calm stopping point.
- Export/import validates data, previews changes, handles duplicates, and rolls back on failure.
- Offline reload works after the static app and selected content have loaded.
- Reduced motion, text-size controls, visible focus, keyboard completion, and 320 CSS-pixel layout are verified.
- Browser tests complete with no uncaught page errors or unexpected console errors/warnings.
- README explains development, validation, testing, deployment, content authoring, local-state boundaries, browser support, and known limitations.