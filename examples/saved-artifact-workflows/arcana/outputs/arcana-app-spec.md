# Arcana — browser application implementation specification

## Product intent and scope

Build Arcana as a private, untimed, noncompetitive static browser game for adults exploring problems, tensions, choices, and possible futures through archetypal card readings. It offers structured chance and reflective interpretation; it MUST NOT claim prediction, diagnosis, certainty, supernatural authority, therapy, or professional advice.

Arcana is a reflective game for imagining possibilities. Its scientific and humanistic concepts are models and metaphors, not predictions, diagnoses, pseudoscience, or replacements for professional guidance.

This is the implementation source of truth. Build the application; do not generate card content, artwork, deck artifacts, a prototype, or a replacement deck.

In scope: a complete accessible static browser app, manual readings, optional OpenAI Responses reflections, optional OpenAI speech, local saved readings/history, export, Guide, Gallery, privacy controls, and browser-grounded validation.

Out of scope: frameworks, build systems, package managers, backends, server routes/actions, serverless functions, CDNs, remote fonts/styles/scripts, analytics, uploads, service workers, accounts, or any claim that implementation or validation occurred before it actually did.

## Required deliverables and static runtime

The workspace already contains authoritative deck-generation artifacts:

- `deck-data.js`;
- `assets/cards/prototype.png`;
- `assets/cards/card-1.png` through the validated final non-prototype number; and
- `assets/card-back.png`.

Inspect and reuse them exactly. Do not regenerate, redraw, rename, reinterpret, replace, duplicate, fetch, embed, or omit them.

Deliver at least `index.html`, a complete runnable app; `README.md`, covering serving, browser support, validation, privacy, manual play, optional-provider use, and known limitations; and only focused support/test files justified by validation.

`index.html` MUST run from static HTTP hosting and repository subpaths. All asset URLs MUST be relative. Load exactly one classic same-origin `<script src="deck-data.js">` before inline application JavaScript. Do not duplicate, fetch, embed, or recreate deck data in HTML. Manual play makes zero network requests.

Use semantic HTML, modern CSS, and standards-based browser JavaScript. Keep domain state behind explicit service/repository boundaries; UI code MUST NOT issue raw storage operations. Validate every imported file and external response before it reaches domain state. If future CPU-heavy work is added, run it in a Web Worker without changing static deployment.

## Deck initialization and integrity

Before rendering interactive UI, completely validate `globalThis.ARCANA_DECK`. If data, cryptography, or an asset is unavailable or invalid, render one blocking recovery surface. Never partially render, guess, silently repair invalid records, or begin a reading with unvalidated data.

Validate schema and deck identity; prototype identity; unique IDs; consecutive explicit card numbers; total/category counts; exactly 15 Major and 40 Minor cards; `major_count * 2 < minor_count`; suits, ranks, motifs, concept sources, formations, and unique position IDs; all `draw_from` policies and formation feasibility; experience fields; maximum question length; provider, speech, and reflection-depth configuration; controlled relative asset paths; and successful usable image dimensions.

Normalize `prototype_card` plus `Object.values(deck.cards)`, sorted by explicit `number`. Associate `assets/cards/prototype.png`, then `assets/cards/card-1.png` through `assets/cards/card-N.png`, plus `assets/card-back.png`; derive `N` from validated non-prototype count.

`deck.cards` keys MUST be consecutive strings `1` through `N`. Validate each key, bind it to `assets/cards/card-<key>.png`, then sort records by explicit `number` for display. Never infer artwork from object iteration order or display position.

Accept only relative `.png` paths with no scheme, host, leading slash, backslash, query, fragment, control character, or `.`/`..` segment. A structurally compatible replacement deck MUST work without code changes.

Render Arcana; subtitle `Fifty-five archetypal models for reflective, instructive play`; total cards 55; Major Arcana 15; Minor Arcana 40; default formation `lantern`.

## State, lifecycle, persistence, and cancellation

Define explicit shell, reading, per-position, inspection, provider, media, final-focus, drawer, dialog, accessibility-live-status, persistence, and recovery state. Include setup/active shell states; reading lifecycle; face-down, turning, revealed, AI pending/ready/failed, voice preparing/ready/failed, cancelled, and stale position states; selected card; top interpretation stage; final synthesis; key/session state; consent; eligibility; depth; and canonical media state.

Every async operation MUST use reading-generation and per-card or named-channel tokens, finite timeouts, `AbortController`, and stale-result suppression. New reading, replacement, cancellation, Forget key, `pagehide`, question changes, retries, and final-synthesis invalidation MUST abort superseded work so stale requests cannot continue billable execution.

Persist only validated non-secret preferences and explicit saved readings, notes, and history in a versioned deck-ID namespace. Never persist plaintext keys, unlock passphrases/derived keys, unaccepted private questions, provider request history, generated audio, Blob URLs, pending work, transient selection, or per-reading consent. Reflection depth is the only persisted AI preference. Saved AI content may record model/depth but never key/audio; history never reruns AI.

Encrypted key persistence is optional and session-only remains the default. When the user opts in, store only a compact versioned AES-256-GCM envelope in a host-only `arcana-openai-key-v1` cookie scoped to the current app directory, with `SameSite=Strict`, `Secure` on HTTPS, no `Domain`, and at most 30 days. Derive a non-extractable key from a minimum 12-character passphrase using PBKDF2-HMAC-SHA-256 with a unique 128-bit salt and at least 310000 iterations; use a fresh 96-bit IV for every encryption and authenticate origin, Arcana context, version, and cookie name. Never persist the passphrase or derived key. Finding ciphertext never connects OpenAI or implies consent. Unlock only on user action; expose tamper, expiry, wrong-passphrase, Web Crypto, size/quota, and replacement errors without plaintext fallback. Replacement preserves the prior envelope unless the new authenticated write succeeds. Forget key deletes both page-memory state and the cookie with matching attributes.

## Setup and home hierarchy

The first screen is a calm invitation, never a dashboard or catalog. The dominant ritual surface owns identity, formation, optional private question, reversals, card sound, and **Shuffle & enter**. A quieter subordinate **Optional OpenAI guide** inset progressively discloses key, consent, fixed model, speech, and depth controls. Wide layouts are approximately two-thirds ritual and one-third guide; narrow layouts place ritual first. The guide has no competing primary action.

Place **Question inspiration** and its textarea before formations. Its default is **Choose a deep question…**, followed exactly by:

- What am I not seeing clearly about the choice before me?
- What pattern is asking to change in my life?
- What deserves my courage right now?
- What must I release to move forward with integrity?
- How can I meet this relationship more honestly?
- What would a wiser relationship with my work look like?
- Where am I confusing safety with stagnation?
- What part of myself needs attention rather than judgment?
- What possibility becomes visible if I stop forcing certainty?
- How can I realize my true calling if my job underuses and ignores my talents?
- How can I love without losing myself when my feelings are not returned?
- What is this unrequited love asking me to grieve, learn, or release?
- How can I distinguish devotion from attachment to an unavailable person?
- How can I move through loss without closing myself to life?
- How can I meet loneliness without treating it as proof that I am unlovable?
- How can I honor my family without abandoning who I am?
- What would forgiveness mean here without denying the harm?
- What would courage look like if certainty never comes?
- How can I make peace with time passing and choices I cannot undo?
- Write my own question…

A preset copies into the editable textarea. **Write my own question…** clears and focuses it. Presets are inspiration only: do not persist them as questions or treat them as provider instructions.

On fresh profile initialize reversals from `deck.experience.reversals_enabled_by_default`; an explicit saved player preference may override it. Initialize **Read reflections aloud** enabled. When encrypted key ciphertext exists, initialize **Use OpenAI guide for this reading** enabled but do not connect or transmit until explicit unlock. Retain the non-extractable derived CryptoKey and accepted page-session API key across drawers, setup/active navigation, and New reading while the page remains alive; never retain the raw passphrase.

Starting without accepted key plus enabled guide consent opens one calm dialog. When encrypted ciphertext exists but remains locked, title it **Unlock your saved OpenAI key?**, explain that the browser has an encrypted but disconnected key, and offer **Enter password** plus **Continue without AI**. Enter password opens OpenAI controls and focuses the encryption passphrase; Continue without AI shuffles once without provider work and leaves later unlock available. Otherwise use **Enter without the OpenAI guide?**, **Enter without guide**, and **Set up OpenAI**. Close, Escape, and backdrop return without shuffling. Preserve typed unaccepted key text as not connected.

## Secure deal and card turn

Use cryptographically secure Fisher-Yates with `crypto.getRandomValues`; never `Math.random`. Validate formation feasibility before mutation. Predeal exactly one unique face-down card per position, respecting `any`, `major`, and `minor` without replacement; establish reversals during the deal. Deal constrained positions before `any`, then restore declared display order. There is no Draw next, empty active position, or Reveal all. New reading cancels work/audio, clears the table, and returns to setup.

Explain in Guide that Major Arcana are rarer, suitless, reading-reframing forces, while Minor Arcana locate lived mechanisms through suit domain and rank process.

Use separate card front/back faces, `transform-style: preserve-3d`, `backface-visibility`, stable 2:3 geometry, and no reflow. Choreograph approximately 650–850ms: subtle press, lift/deeper shadow, decisive 180-degree turn, restrained edge-light sweep, and settle. Animate only compositor-safe transform, opacity, filter, and shadow. No bounce, wobble, particles, neon, screen shake, or casino spectacle.

Synchronize local Web Audio paper hush at lift and two quiet resonant tones near midpoint/settle. Lock only the turning card. Double-click, key repeat, hover, focus, resize, rerender, and async completion MUST NOT reverse it, replay sound, expose both faces, leave it edge-on, or move layout. Reveal accessible metadata and begin AI work only after settle. Reduced motion uses immediate face swap plus static highlight while preserving state, focus, announcement, and sound preference.

## Card reflection and inspection

Every revealed card owns compact **Card reflection**. Art click selects; only its trigger opens detail. Do not expand meanings inline or grow the formation.

Use one spacious anchored reflection surface: 440–640 CSS-pixel side/editorial veil on wide screens with selected card visible, near-full-width sheet with selected-card preview/reserved region on narrow screens, stable page geometry/scroll, and internal reflection-body scrolling only. Close, Escape, and backdrop restore trigger focus.

On rerender, remap invokers and focused controls to replacement DOM nodes with `preventScroll`. Never retain detached triggers or drop focus to `<body>` during async work. Render generated/untrusted values only as text data. Pending, complete, failed, stale, cancelled, and retryable states remain distinct and local.

Manual meaning appears first: position; essence; generative/destructive/orientation meanings; emotional register; question; category/purpose; concept source, factual anchor, and boundary; reflective bridge; lineage; motifs; and Minor suit/rank or explicit Major suitlessness. The surface is manual-only, hidden until explicitly opened, and never auto-opens for AI or completion.

## Optional OpenAI guide

Use `https://api.openai.com/v1/responses` with fixed `gpt-5.4-mini`; use `https://api.openai.com/v1/audio/speech` with fixed `gpt-4o-mini-tts`, `onyx`, and `mp3`.

Setup and active OpenAI drawer include unchecked **Use OpenAI guide for this reading**, password input with `autocomplete="current-password"`, **Use key this session**, optional **Save encrypted key in this browser**, passphrase/unlock controls, **Forget key**, session/storage status, fixed model, complete consent summary, unchecked **Read reflections aloud**, and **Reflection depth**. If a browser or password manager prefills a key from protected credential storage, detect it without connecting or transmitting it, state that the browser restored it rather than Arcana, and offer **Use restored key**. If an encrypted Arcana cookie exists, state that it is saved but disconnected and offer **Unlock saved key**. Once connected, let the user keep using that restored page-session key or enter and connect a replacement without retyping the existing key.

Keep accepted plaintext key only in private JavaScript memory; clear input after acceptance; never store plaintext, export, log, render, or send key as request content. A browser-restored credential remains owned by protected browser storage; Arcana must never claim it persisted that key. An unlocked encrypted cookie yields a page-session key only after passphrase authentication. AI requires explicit per-reading guide consent, accepted key, and nonempty private question no longer than 1800 characters. Guide/speech consent starts unchecked each new reading and never persists. A page-session key may remain until Forget key or exit but never implies later consent.

The active drawer provides page-memory-only private question. When consent, key, and question become available later, reconcile all revealed idle/cancelled cards: mark each pending before rerender and start exactly one eligible request. Question changes/clears increment generation, abort dependent text/speech, clear question-grounded reflections and final synthesis, remove pending glow, and reconcile only for a new nonempty question.

Forget key aborts text/speech, invalidates media ownership, stops narration, revokes Blob URLs, clears voice UI, and leaves manual play unchanged. Unchecking consent immediately aborts corresponding pending work. A post-revocation response MUST NOT update UI or start speech. Every request/retry rechecks eligibility immediately before sending. Hide or disable unavailable retries with explanation. Consent revocation preserves completed page-memory/save/export text and only cancels pending work.

### Reflection depth and provider validation

Render `deck.ai_guide.reflection_depth` as accessible five-step range with visible label/description, endpoint labels, default 3, and `aria-valuetext`.

1. **Whisper**: exactly one sentence, at most 30 words; no tension/question.
2. **Brief**: one 60–90-word paragraph; no extra section.
3. **Balanced**: one 120–180-word paragraph plus one concise question.
4. **Deep**: two/three paragraphs, one tension, one question, 250–400 words.
5. **Immersive**: several paragraphs, developed tension, one question, 500–800 words.

Scale final synthesis proportionally: Whisper at most two sentences; Brief one paragraph; Balanced two/three short paragraphs and one question; Deep structured multi-section; Immersive developed pattern, counterpoint, and two or three questions.

Use strict JSON Schema with unavailable sections nullable. Depth is trusted developer configuration, never user content. Validate budgets and shape after parsing: Whisper one/two sentences; Brief one paragraph; Balanced two/three paragraphs; Deep/Immersive nonempty synthesis, pattern, counterpoint, and configured question counts; Brief/Balanced exactly one reflection paragraph; Deep two/three; Immersive at least three. Do not render empty headings. Depth changes apply only to future requests/final synthesis.

On reveal, send only private question as separate untrusted user role plus formation, position, selected card written fields/motifs/orientation. Never send PNGs, art, key, history, notes, unrelated cards, or audio. Use `store:false`, structured output, timeout, cancellation, and stale suppression. Render output only as text. Failure preserves manual play, gives precise explanation, and offers eligibility-aware retry; never invent fallback text.

### Glow and automatic side interpretation stage

During text work, show restrained ivory/mineral-blue/oxidized-gold tracer around exactly that settled card. It remains when reflection closes. Voice transitions continuously to calmer warm-gold through request, decode, Blob creation, and metadata readiness; never flicker. Cards glow independently; final synthesis uses coordinated low-intensity formation glow. Reduced motion uses static luminous frames and explicit phase labels.

Automatic AI interpretation uses one composite foreground overlay beneath sticky navigation for the most recently revealed AI-enabled card. Magnify that exact revealed card with its art, title, position, and orientation beside a tall editorial interpretation pane. Preserve deck geometry underneath rather than pushing/reflowing it; the composite may sit over other cards because the interpreted card itself remains enlarged and fully appreciable. A later reveal replaces content in place; older completion cannot reclaim it. Multiple cards may compute independently. Do not steal focus, navigate, scroll, or open Card reflection. Pending shows title/position/depth and restrained mineral-blue/oxidized-gold orbit/sweep/breathing-light treatment; reduced motion uses static constellation/status. Ready shows only permitted depth content; failure shows precise error/retry. When narration belongs to the card, show icon-only Play/Pause, Replay, and Stop controls with accessible names/tooltips, mirrored from canonical media state. Include **Close interpretation**; closing is respected until a newly revealed eligible card opens it. Use polite live announcements without focus movement.

Give the composite most of the available dynamic viewport height, a generous 2:3 card preview, and an independently scrolling Deep/Immersive interpretation body. At narrow mobile widths retain side-by-side columns with a compact card preview and readable non-modal pane. It remains dismissible and must not alter focus or scroll when it appears. Recompute after resize, orientation, media transport, and formation layout changes.

## Speech and media transport

Speech is separately controllable and enabled by default on every fresh or new reading. It sends nothing unless guide consent, connected key, private question, and generated reflection are all present. Display: **The optional spoken interpretation uses an AI-generated OpenAI voice, not a human voice.** Send only visible title/position/generated reflection fields or visible final complete-interpretation fields, never question/notes. Use exact instruction: **Speak in a low, mysterious, warm, soothing voice. Slow the pace slightly, with calm natural pauses, never theatrical, ominous, breathy, or melodramatic.**

After explicit **Contemplate the whole** succeeds, automatically narrate the complete interpretation when narration remains enabled. Use the same persistent iPad-safe media element, cancellation token, navbar transport, and icon-only Play/Pause, Replay, and Stop controls. Mirror those controls beside the visible final interpretation and retain tap-to-play recovery when autoplay is blocked. Question/key/consent changes, Forget key, New reading, card retries, and newer media ownership abort or invalidate final narration.

Keep audio only in page-memory Blob/Object URLs; revoke on replacement, New reading, Forget key, and exit. Attempt playback only after text visible. Blocked autoplay retains Play narration; failure retains text and Retry narration.

For iOS/iPadOS WebKit, including Chrome on iPad, create one persistent `HTMLAudioElement`, prime it synchronously from a reveal or speech-consent user gesture before delayed TTS fetch, resume Web Audio in that gesture, and reuse that same playback element across sequential narration chunks. Never create a fresh playback element after gesture activation expires. If playback remains blocked, expose a clear tap-to-play state without treating decoded narration as failed.

Speech input is at most 4096 characters. Split long Deep/Immersive text at sentence/word boundaries into chunks no longer than 3900; fetch sequentially under one ownership token and play one logical playlist with combined elapsed/total progress. Never truncate, omit, overlap, reorder, or expose separate transports.

Route turn sound/narration through one media controller; new source replaces old. Reserve navbar geometry. Each media request has monotonically increasing token; card turn, newer narration, Forget key, New reading, and Stop invalidate older requests before stale audio can install or continue billable work. Show slim navbar transport while preparing/ready/playing/paused/completed/replayable with source/card label, semantic progress, elapsed/total `m:ss`, and icon-only Play/Pause, Replay, and Stop controls with accessible names/tooltips. Before duration, show labeled indeterminate state; never `NaN` or fake duration. The interpretation side pane mirrors canonical narration controls; Sound independently controls effects/voice.

## Complete interpretation, Guide, gallery, history, export

Never synthesize automatically. After every reveal expose **Contemplate the whole**. Only it sends ordered positions/cards/orientations and successful per-card reflections. With AI enabled, reveal it only after each per-card request settles ready/failed/cancelled; pending results cannot become `null`. Recheck immediately before final payload construction.

Starting/retrying a card invalidates pending/completed final synthesis, stale-suppresses its result, clears final glow/focus, and requires fresh explicit action after settlement. Forget key and all eligibility changes rerender completion immediately. Focus layout preserves all cards while reducing them enough to show final text where practical; expose **Restore full-size cards** during pending, success, failure, cancellation, retry, and consent revocation. Approximately first 240 CSS pixels of deliberate upward scroll may progressively restore cards; keyboard/touch/reduced-motion have explicit restoration. Final text remains below restored cards; cancellation/failure clears formation pending glow.

Use setup/active shells. Transition existing controls rather than duplicate unrelated UI; preserve selection, scroll, focus, entered text, running work, status, validation, and semantic ownership unless initiating action resets them. Active navigation is slim, sticky, safe-area aware, and exposes Guide, OpenAI, Sound, New reading, and media transport through one mutually exclusive accessible drawer.

Drawers require close, Escape, and backdrop/outside close where suitable. Modal drawers trap focus, make background inert, block background pointer action, restore focus even after rerender, do not nest, and do not flash intermediate empty state when switching destinations. Headers/close controls remain reachable during internal scrolling. Resize/orientation/async work cannot close user-opened drawer or reset it.

Guide order: purpose/boundary; Major/Minor; two-minute reading; complete rules; suits; ranks; every formation/position; generative/destructive; reversals; collapsed Symbol concordance; adult-content/reflective-use note. Gallery groups Major, then Minor by suit/rank, then common back. Completion supports notes, explicit local save/history/delete, JSON download, and plain-text copy. Both export formats include successful per-card reflections and final interpretation including optional pattern, counterpoint, tension, and questions.

## Accessibility, security, acceptance, and verification

Generated PNGs dominate. Do not recreate integrated titles/art or obscure cards. Use warm paper/daylight neutrals, mineral color, editorial system serif, readable system sans, quiet light, generous negative space, and restrained texture; browser chrome must not default black.

Use semantic landmarks, controls, labels, dialogs/sheets, progress, and live status. Support keyboard, pointer, touch, visible focus, 44px targets, 200% zoom, forced colors, reduced motion, dynamic viewport changes, and 320 CSS-pixel layouts with no horizontal scrolling or drag-only path. Face-down cards expose no hidden title/category/description/meaning through alt, accessible name, DOM label, focus, or live region. Preserve selection/reflection/text/focus/scroll through rerender, resize, async work, and drawers. Color, orientation, image, and motion are never sole meaning. Treat native `hidden` as authoritative.

Set CSP exactly to `default-src 'self'; img-src 'self'; media-src 'self' blob:; style-src 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src https://api.openai.com; object-src 'none'; base-uri 'none'; form-action 'none'`. Omit ignored meta `frame-ancestors`. Do not use eval, dynamic code construction, upload, service worker, third-party storage, user-editable endpoints, redirects, or remote URL beyond configured OpenAI endpoints.

Completion requires runnable `index.html`, README, preserved artifacts, clean validation, and browser evidence. Validate via repeated build-run-observe-improve using Playwright MCP or approved equivalent. Before claiming it, check availability. Use existing approved integration; only install/configure explicitly pinned reviewed versions declared in checked-in configuration/lockfile through approved setup path. Never use floating/latest or invent versions. If no approved pinned version exists, report exact blocker and do not claim browser validation.

The implementing agent MUST inspect this spec, raw deck data, representative Major/Minor art, and artifacts; implement in clean source without copying prior runtime; serve real static directory over HTTP; inspect page, accessibility tree, console, network, screenshots/traces, and persistence; fix observed defects; and rerun syntax, tests, lint, and browser flows.

Test home hierarchy, manual confirmation, secure category-aware deal, full/reduced turn, reflection geometry, every depth, text/voice glow, TTS success/failure/retry, media controls, final focus/restore, drawers/focus, privacy/storage, 320px, console, network, restart, and static-host/offline behavior. Record commands, URL, exercised flows, evidence, defects resolved, and honest limitations. Browser validation is incomplete if it stops at build output or screenshots without real interaction.

Use this boundary once in Guide and once in footer:

"Arcana is a reflective game for imagining possibilities. Its scientific and humanistic concepts are models and metaphors, not predictions, diagnoses, pseudoscience, or replacements for professional guidance."