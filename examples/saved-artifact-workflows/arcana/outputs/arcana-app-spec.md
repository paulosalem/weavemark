# Arcana — browser application implementation specification

## 1. Product intent and delivery boundary

Build Arcana as a private, untimed, noncompetitive browser game for adults exploring problems, tensions, choices, and possible futures through structured chance and reflective archetypal models. Arcana MUST present possibilities rather than prediction, diagnosis, certainty, supernatural authority, therapy, or professional advice.

The implementation deliverable is a static browser application, not generated cards, images, runtime data, source-code prose, or a prototype. The workspace already contains the authoritative outputs from the card-generation pipeline:

- `deck-data.js`;
- `assets/cards/prototype.png`;
- `assets/cards/card-1.png` through the validated final non-prototype number; and
- `assets/card-back.png`.

Inspect and reuse those artifacts. Do not regenerate, redraw, rename, reinterpret, replace, duplicate, fetch, embed, or omit them.

Deliver at least:

- `index.html`, the complete runnable application;
- `README.md`, documenting serving, supported browsers, validation, privacy, manual play, optional-provider use, and known limitations; and
- only focused support or test files justified by validation.

Do not add a framework, build system, package manager, backend, serverless function, CDN, analytics, remote font, remote stylesheet/script, upload system, service worker, account system, or mutable third-party dependency. The production artifact MUST run from static hosting, including a repository subpath such as GitHub Pages. Use only relative local asset URLs.

`index.html` MUST load exactly one classic same-origin `<script src="deck-data.js">` before its inline application JavaScript. Do not duplicate, fetch, embed, or recreate deck data in HTML. Manual play MUST make zero network requests.

## 2. Product metadata and non-negotiable boundary

- Title: Arcana
- Subtitle: Fifty-five archetypal models for reflective, instructive play
- Total cards: 55
- Major Arcana: 15
- Minor Arcana: 40
- Default formation: `lantern`
- Default reversals: enabled
- OpenAI guide default: disabled
- AI reflection model: `gpt-5.4-mini`
- AI Responses endpoint: `https://api.openai.com/v1/responses`
- Speech endpoint: `https://api.openai.com/v1/audio/speech`
- Speech model and voice: `gpt-4o-mini-tts`, `onyx`

Use this boundary once in Guide and once in the footer:

> Arcana is a reflective game for imagining possibilities. Its scientific and humanistic concepts are models and metaphors, not predictions, diagnoses, pseudoscience, or replacements for professional guidance.

The deck may approach grief, mortality, shame, obsession, domination, loneliness, sacrifice, exclusion, and meaninglessness without gore, sexualization, sensationalism, or claims of occult causation.

## 3. Architecture and startup validation

Use semantic HTML, modern CSS, and standards-based browser JavaScript. Keep domain logic behind explicit repository/service boundaries even in plain JavaScript; UI code MUST NOT issue raw storage queries. Validate all imported data and external responses before they reach domain state. Do not use `eval`, dynamic code construction, remote code, user-editable provider endpoints, redirects, uploads, service workers, or third-party storage.

Before any rendering setup, completely validate `globalThis.ARCANA_DECK`:

- schema and deck identity;
- prototype identity;
- unique ids and consecutive explicit numbers;
- total/category counts: exactly 15 Major and 40 Minor;
- `major_count * 2 < minor_count`;
- suits, ranks, motifs, concept sources, formations, unique position ids, and formation feasibility;
- each position `draw_from` policy;
- experience configuration, maximum question length, provider configuration, speech configuration, and reflection-depth configuration; and
- controlled relative asset paths and successful image loading.

Normalize `prototype_card` plus `Object.values(deck.cards)`, sort by explicit `number`, and bind artwork as follows: `assets/cards/prototype.png`, then `assets/cards/card-1.png` through `assets/cards/card-N.png`, and `assets/card-back.png`. Derive `N` from the validated non-prototype count.

`deck.cards` uses consecutive string keys `1` through `N` as stable generated-artifact indices. Validate every key, bind each record to `assets/cards/card-<key>.png`, then sort by explicit `number` only for display. Never infer art binding from object iteration order or a sorted position.

Accept only relative `.png` paths without a scheme, host, leading slash, backslash, query, fragment, control character, or `.`/`..` path segment. Verify usable image dimensions. If deck data, cryptography, or required assets are unavailable, render exactly one blocking recovery surface with a clear cause and recovery guidance; never partially render, silently substitute content, or guess.

A structurally compatible replacement deck MUST work without code changes.

## 4. State, lifecycle, storage, concurrency, and cancellation

Define explicit shell, reading, per-position, inspection, provider, media, completion-focus, drawer, and persistence state. At minimum, represent:

- shell state: `setup` or `active`;
- position/card state: face-down, turning, revealed, AI text pending, AI text ready, AI text failed, voice preparing, voice ready, voice failed, cancelled, and stale;
- selected card and reflection-surface state;
- per-reading guide consent and voice consent;
- accepted session key state, private-question state, reflection depth, request generations, and pending ownership;
- media state: preparing, ready, playing, paused, completed, replayable, or stopped; and
- complete-interpretation eligibility, pending, ready, failed, cancelled, and focus-layout state.

Every asynchronous operation MUST use a reading generation token, a per-card token where applicable, finite timeout, `AbortController`, and stale-result suppression. New reading, card replacement, cancellation, Forget key, private-question change/clear, and `pagehide` MUST abort relevant work. A result may mutate UI only if it still owns its reading, card, request, and media tokens.

Persist only non-secret preferences and explicitly saved readings, notes, and history under a versioned namespace keyed by deck id. Validate restored data before use and recover visibly from invalid data. Never persist API keys, unsaved private questions, provider request history, generated audio, Blob URLs, pending requests, transient selections, per-reading AI consent, or voice consent. Reflection depth is the only AI preference that may persist. Saved AI text records model and depth but never key or audio. Never rerun AI from history.

## 5. Home hierarchy and setup flow

Open on a calm invitation, never a dashboard or card catalog.

- The dominant ritual surface owns product identity, formation selection, optional private question, reversals, card-sound preference, and **Shuffle & enter**.
- A quieter subordinate **Optional OpenAI guide** inset progressively discloses key, consent, fixed model, speech, and depth controls.
- On wide viewports, ritual is approximately two-thirds and guide approximately one-third. On narrow viewports, ritual comes first. Never render equal competing panels.
- The guide has no competing primary action.

On first profile use, initialize reversals from `deck.experience.reversals_enabled_by_default`. A saved explicit player reversal preference may override that default.

If the player starts without both an accepted key and enabled guide, show exactly one calm confirmation dialog:

- title: **Enter without the OpenAI guide?**;
- actions: **Enter without guide** and **Set up OpenAI**;
- Close, Escape, and backdrop return to setup without shuffling;
- explain that manual reading remains complete and private and OpenAI can be enabled later;
- preserve typed but unaccepted key text and state that it is not connected; and
- after manual confirmation, shuffle exactly once and do not ask again for that start.

## 6. Secure deal and active-table behavior

Use cryptographically secure Fisher–Yates shuffling with `crypto.getRandomValues`; never use `Math.random`. Validate formation feasibility before mutating the table. Predeal exactly one unique face-down card into each formation position, respecting `any`, `major`, and `minor` without replacement, and establish reversals during the deal.

Deal category-constrained positions before `any` positions, then restore the formation’s declared display order. This MUST reserve category quotas so an early `any` position cannot consume a card needed by a later constrained position.

There is no Draw next control, empty active position, or Reveal all action. Each face-down card is its own direct reveal action. Reversed art rotates 180 degrees while written meaning remains upright. New reading MUST cancel work and audio, clear the table, and return to setup without navigation.

Guide content MUST explain that Major Arcana are rarer, suitless reading-reframing forces, while Minor Arcana locate lived mechanisms through suit domain and rank process.

## 7. Card turn, reflection, and inspection

Implement a stable card-turn scene with separate front/back faces, `transform-style: preserve-3d`, `backface-visibility`, explicit 2:3 geometry, and no reflow. The choreography is approximately 650–850 ms: subtle press, small lift and deeper shadow, decisive 180-degree turn, restrained edge-light sweep, then gentle settle. Animate only compositor-safe transform, opacity, filter, and shadow. Do not use bounce, wobble, particles, neon, screen shake, or casino spectacle.

Synchronize a local Web Audio paper hush with lift and two quiet resonant tones near midpoint and settle. Lock only the turning card. Double-click, key repeat, hover, focus, resize, rerender, or asynchronous updates MUST NOT reverse a card, expose both faces, replay sound, leave it edge-on, or alter layout. Reveal accessible title and metadata and begin eligible AI work only after settling. Reduced motion uses immediate face swap plus static highlight while preserving state, focus, announcement, and sound preference.

Each revealed card owns a compact **Card reflection** trigger. Clicking artwork selects the card; only the trigger opens detail. Do not expand meanings inline or grow the formation.

Use one spacious anchored reflection surface:

- wide view: 440–640 px side/editorial veil over sibling space while keeping the selected card visible;
- narrow view: near-full-width sheet with selected-card preview or reserved region;
- stable page geometry and scroll; only reflection body may scroll as needed; and
- Close, Escape, and backdrop restore focus to the trigger.

Manual content appears first and includes position, essence, generative/destructive and orientation meanings, emotional register, question, category/purpose, concept source/factual anchor/boundary, reflective bridge, lineage, motifs, and Minor suit/rank or explicit Major suitlessness. Render generated or untrusted values as text data, never executable markup. AI content appears in this same surface after manual meaning. Completion MUST NOT auto-open it, move focus, or scroll.

When cards, reflection, or completion surfaces rerender, remap stored invokers and focused controls to replacement DOM nodes with `preventScroll`. Never retain a detached trigger or drop keyboard focus to `<body>`. Re-selecting another card updates the surface in place without flashing the formation or showing stale content. Pending, ready, failed, stale, cancelled, and retryable states remain distinguishable and local to the relevant card.

## 8. Adaptive workspace shell and drawers

Maintain distinct `setup` and `active` shell states. Setup foregrounds onboarding and the start action; active foregrounds the table. Move existing guide controls into their active destination without duplicating them, and preserve values, validation, status, semantic ownership, selection, scroll, entered text, and ongoing local work unless an explicit action requires reset.

In active state, provide a slim sticky navigation surface containing product identity and Guide, OpenAI, Sound, New reading, and conditional media transport. It must respect safe-area insets, text zoom, dynamic viewport changes, and content scrolling without obscuring anchored content or consuming disproportionate space.

Guide, OpenAI, Sound, and other global secondary surfaces use one mutually exclusive accessible drawer/sheet over the unchanged workspace. Switching destinations replaces the current drawer without flashing through an empty state. Drawers require explicit close controls, Escape, permitted backdrop/outside activation, focus trapping, inert or otherwise noninteractive background, robust focus restoration, no nested drawers, and no background pointer activation or scroll. Their header and close action remain reachable when content scrolls. Resize, orientation change, background refresh, and asynchronous completion MUST NOT close a user-opened drawer or reset its internal state. Reduced motion uses direct state changes.

## 9. Optional OpenAI guide and consent

Use the exact configured OpenAI Responses endpoint and fixed `gpt-5.4-mini` model. Setup and active OpenAI drawer MUST include:

- unchecked **Use OpenAI guide for this reading**;
- password input with `autocomplete="off"`;
- **Use key this session**, **Forget key**, session status, and fixed model;
- the complete consent summary;
- unchecked **Read reflections aloud**; and
- **Reflection depth**.

Keep the key only in a private JavaScript variable and clear the input after acceptance. Never store, export, log, render, or send the key as request content. AI mode requires explicit consent, accepted key, and a nonempty private question.

Guide consent and voice consent are per-reading choices: both begin unchecked on every new reading and are never persisted. A connected page-session key may remain available until Forget key or page exit, but it cannot imply consent for any later reading. The active drawer MUST offer a page-memory-only private-question field so a manual reading can become eligible later.

When consent, key, and question become available, reconcile every already revealed card whose reflection is idle or cancelled. Start exactly one request per eligible card, mark it pending before completion rerenders, and refresh final-action availability. Changing or clearing the question MUST increment request generation, abort dependent text/speech work, clear question-grounded reflections and final synthesis, remove pending glow, and reconcile only against the new nonempty question.

Forget key MUST abort text and speech, invalidate media ownership, stop narration, revoke Blob URLs, clear voice UI, and preserve manual play. Unchecking either consent control immediately invalidates and aborts corresponding pending work. A response arriving after consent revocation MUST NOT update UI or start speech. Every request/retry entry point MUST recheck consent, key, and question before provider data is sent; unavailable retry actions must be hidden or disabled with an explanation. Revocation preserves already-completed reflections and complete interpretation in page memory, UI, save, and export; only pending work is cancelled.

## 10. Reflection depth, request contracts, and glow

Render `deck.ai_guide.reflection_depth` as an accessible five-step range with visible label/description, endpoint labels, configured default, and `aria-valuetext`:

1. **Whisper**: exactly one sentence, at most 30 words; no tension/question.
2. **Brief**: one 60–90-word paragraph; no extra section.
3. **Balanced**: one 120–180-word paragraph plus one concise question; measure paragraph budget independently from the question.
4. **Deep**: two or three paragraphs, one tension, one question, 250–400 words.
5. **Immersive**: several paragraphs, developed tension, one question, 500–800 words.

Scale final synthesis proportionally: Whisper at most two sentences; Brief one paragraph; Balanced two or three short paragraphs and one question; Deep structured multi-section; Immersive developed pattern, counterpoint, and two or three questions.

Use strict JSON Schema and explicitly nullable unavailable sections. Treat depth as trusted developer configuration, not user content. After parsing, validate output structure and budgets: Whisper one or two sentences; Brief exactly one paragraph; Balanced exactly two or three paragraphs; Deep/Immersive require nonempty synthesis, pattern, counterpoint, and configured question counts; Brief/Balanced have exactly one reflection paragraph; Deep has two or three; Immersive at least three. Reject nonconforming output visibly, do not render empty headings, and never regenerate existing text when depth changes; depth affects future requests and synthesis only.

For each card request, send only the private question as separate untrusted user-role content plus formation, position, selected card written fields, motifs, and orientation. Do not send PNGs, art, key, history, notes, unrelated cards, or audio. Use `store:false`, structured output, finite timeout, cancellation, stale suppression, and text-only rendering.

During text work, animate an ivory/mineral-blue/oxidized-gold tracer around exactly that settled card. It remains visible while reflection closes. If voice is enabled, transition continuously into calmer warm-gold through request, decode, Blob creation, and metadata readiness; do not flicker. Multiple cards may glow independently. Final synthesis uses coordinated low-intensity formation glow. Reduced motion uses static luminous frames and explicit phase labels. Failures preserve manual play, explain the precise failure, and offer retry; never invent fallback text.

## 11. Speech and canonical media transport

Speech is separately opt-in. Display the configured disclosure. Send only visible title, position, and generated reflection fields to `gpt-4o-mini-tts`, `onyx`, and MP3 with the configured speaking instructions. Never send original question or notes.

Keep audio only in page-memory Blob/Object URLs and revoke them on replacement, new reading, Forget key, and exit. Attempt autoplay only after text is visible; when blocked, retain a visible Play control. Failure retains text and offers Retry narration.

The Speech API accepts at most 4096 input characters. Split longer Deep/Immersive narration at sentence or word boundaries into chunks no larger than 3900 characters. Fetch sequentially under one voice/media ownership token and play as one logical playlist with combined elapsed/total progress. Never truncate, omit, overlap, reorder, or expose competing per-chunk transports.

Route turn sound and narration through one media controller; a new source replaces the previous source. Reserve navbar geometry so transport appearance never moves the table. Every media request owns a monotonically increasing token. A speech response may install audio only while it owns the narration-preparing slot. Starting a turn, newer narration, Forget key, New reading, or Stop invalidates older tokens and aborts in-flight speech before stale work can replace active audio or continue billable work.

Whenever media is preparing, ready, playing, paused, completed, or replayable, expose a slim navbar transport with source/card label, Play/Pause, Replay, Stop, semantic progress, elapsed, and total `m:ss`. Use real metadata/events. Before duration is known, show labelled indeterminate progress; never show `NaN` or fake duration. Turn sound uses known duration and remains briefly replayable. Sound drawer mirrors canonical state and independently controls effects and voice.

## 12. Complete interpretation, notes, history, and export

Never synthesize automatically. After every card reveals, expose **Contemplate the whole**. Only this action sends ordered positions, cards, orientations, and successful per-card reflections.

When AI is enabled, expose synthesis only after every per-card text request has settled as ready, failed, or cancelled. Pending reflections remain visibly pending and MUST NOT be frozen as `null` by early synthesis. `requestFinal` MUST repeat this guard immediately before payload construction. Forget key and every eligibility change MUST rerender completion immediately so a stale action cannot remain visible.

Entering complete focus layout is explicit. Preserve all cards, reduce them enough to show pending/final text in the same viewport where practical, and provide **Restore full-size cards**. Approximately the first 240 CSS pixels of deliberate upward scroll may progressively restore cards. This scroll behavior is progressive enhancement only: keyboard, touch, reduced-motion, assistive technology, and short pages require explicit restoration. Keep final text below restored cards and never shrink cards again without explicit focus. Restore remains available throughout synthesis pending, success, failure, cancellation, retry, and consent revocation. Failure/cancellation clears formation pending glow.

Provide private notes, explicit local save/history/delete, JSON download, and plain-text copy. Both export formats MUST include successful per-card reflections and complete interpretation, including optional pattern, counterpoint, tension, and questions.

Guide order MUST be: purpose/boundary; Major/Minor; two-minute reading; complete rules; suits; ranks; every formation/position; generative/destructive; reversals; collapsed Symbol concordance; adult-content/reflective-use note. Gallery order MUST be Major, then Minor grouped by suit/rank, then common back.

## 13. Visual, responsive, accessibility, privacy, and security requirements

Generated PNGs dominate. Do not duplicate integrated titles, recreate art, or obscure cards. Use warm paper/daylight neutrals, mineral color, editorial system serif display, readable system sans, quiet light, generous negative space, and restrained texture. Browser chrome must not default to black.

Use semantic landmarks, labelled native controls, dialogs/sheets, progress semantics, live status, visible focus, complete keyboard/pointer/touch access, 44 px targets, 200% zoom support, forced-colors support, reduced-motion support, no drag-only route, and no horizontal page scroll at 320 CSS px. Face-down cards must expose no hidden title, category, description, or meaning through alt text, accessible name, live region, DOM label, or focus. Never rely only on color, orientation, image, or motion to convey meaning.

Preserve selection, reflection state, entered text, focus, and scroll across rerenders, resize, async completion, and drawer transitions. Treat the native `hidden` attribute as authoritative; CSS must not accidentally reveal inactive states. Provide meaningful first-run, loading, empty, active, dirty, saved, conflict, unsupported-browser, and recovery states.

Apply this CSP exactly, omitting ignored meta `frame-ancestors`:

`default-src 'self'; img-src 'self'; media-src 'self' blob:; style-src 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src https://api.openai.com; object-src 'none'; base-uri 'none'; form-action 'none'`.

No network request is permitted except the exact configured OpenAI Responses and Speech endpoints after explicit consent. No API key may appear in storage, URL, export, analytics, log, rendered text, or request content.

## 14. Acceptance criteria and verification plan

The application is complete only when all requirements above are implemented in a runnable static `index.html`, with preserved deck artifacts and README, clean validation, and browser evidence.

The implementing agent MUST:

1. inspect this specification, raw deck data, representative Major/Minor art, and existing generated artifacts;
2. implement in a clean workspace/source file without copying a prior runtime;
3. serve the actual static directory over HTTP;
4. use an approved Playwright MCP integration where available to repeatedly inspect and exercise the real application;
5. validate home hierarchy, manual-confirmation flow, cryptographically secure category-aware deal, full and reduced-motion turn, reflection geometry, each depth, text/voice glow, TTS success/failure/retry, media controls, final focus/restore, drawers/focus, privacy/storage, 320 px layouts, console, network, and restart;
6. inspect rendered page, accessibility tree, console, network behavior, screenshots or traces, and relevant persisted state; fix observed defects and repeat browser validation;
7. rerun syntax checks, focused tests, lint where available, and browser flows; and
8. report commands, tested URL, exercised flows, evidence artifacts, resolved console/network/runtime issues, verified behavior, unverified assumptions, and honest remaining limitations.

If Playwright MCP or equivalent approved browser automation is unavailable, report the exact blocker and do not claim browser validation occurred. Do not provision an unpinned or unreviewed MCP version. Browser validation is not satisfied by a build, code dump, compiled specification, or screenshot alone. Treat awkward first-run behavior, broken focus, unreadable layout, unresponsive input, invisible state changes, jank, console errors, and unexpected console warnings as defects.

Completion requires a playable browser smoke test from first load through active reading, core controls, reveal/progress feedback, and New reading/replay without full page reload. Unit-test domain and storage services where practical; use Playwright for critical browser flows, narrow viewports, and static-host/offline behavior. A plausible code dump, specification, or screenshot alone is not completion.
