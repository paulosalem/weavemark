@promplet version: 0.9

# Arcana — browser application specification

@note
  Non-executable software-specification promplet for Arcana. It compiles the
  complete browser-application contract into Markdown for an interactive
  programming agent. It does not generate card content or images, emit runtime
  data, implement source code, run tests, or claim that implementation happened.

  `cards.weavemark.md`, beside this file, is the independent executable
  artifact-generation pipeline. The build runner may reuse its validated outputs,
  but this application specification is recompiled on every build.

@refine module:weavemark.domains.programming.foundations.software_spec
  Treat this document as the authoritative implementation contract for an
  interactive programming agent, not as an instruction to emit the app itself.

@refine module:weavemark.domains.programming.stacks.browser_static_esmodules
  Build Arcana as static browser files beside the pre-generated deck artifacts.

@refine module:weavemark.domains.programming.modules.browser_encrypted_value_storage
  Configure the imported selectors as follows:
  - requirement: `@{secret_crypto_requirement}`;
  - backend: `@{secret_storage_backend}`;
  - unlock: `@{secret_unlock_mode}`;
  - cookie name/path/lifetime: `@{secret_cookie_name}`,
    `@{secret_cookie_path}`, @{secret_cookie_days} days;
  - KDF: @{secret_kdf_iterations} iterations, minimum passphrase length
    @{secret_min_passphrase_length};
  - authenticated context: `@{secret_context}`;
  - replacement: `@{secret_allow_replacement}`.
  Session-only use remains the default and plaintext persistence is forbidden.

@refine module:weavemark.domains.programming.modules.adaptive_workspace_shell
  Apply the reusable shell to Arcana's dominant home ritual and immersive active
  table. Guide, OpenAI, Sound, and New reading become compact destinations.

@refine module:weavemark.domains.programming.modules.focus_preserving_inspection
  Treat the formation as the collection and each card as an inspectable entity.
  A compact trigger opens one spacious Card reflection surface; complete-reading
  synthesis uses the explicit focus layout.

@refine module:weavemark.domains.programming.validation.playwright_mcp_browser_validation
  The implementing agent MUST inspect the real app repeatedly, exercise complete
  manual and mocked-provider flows, capture evidence, and fix defects before
  reporting completion.

@output enforce: strict
  Return one complete Markdown software implementation specification beginning
  exactly with `# Arcana — browser application implementation specification`.
  Do NOT emit HTML, CSS, JavaScript, source code, a prototype, commentary,
  implementation claims, tool-availability complaints, or requests for workspace
  access. The declared artifacts and requirements below are authoritative inputs;
  a later interactive programming agent will inspect and implement them.

# Arcana — browser application implementation specification

You are the specification compiler, not the programming agent. Transform every
requirement below and every applicable refined-module obligation into a
self-contained, developer-ready Markdown specification. Use normative
MUST/SHOULD/MAY language, concrete state transitions, data flow, algorithms,
failure behavior, privacy/security boundaries, acceptance criteria, and
verification steps. Preserve exact labels, models, paths, budgets, timings, and
counts. Never perform, simulate, defer, or refuse the future implementation.

Arcana is a private, untimed, noncompetitive adult archetypal reading game. It
explores possibilities and never claims prediction, diagnosis, certainty,
supernatural authority, therapy, or professional advice.

Product metadata:

- Title: @{deck.title}
- Subtitle: @{deck.subtitle}
- Boundary: @{deck.experience.boundary_statement}
- Total cards: @{deck.card_count}
- Major Arcana: @{deck.arcana.major.count}
- Minor Arcana: @{deck.arcana.minor.count}
- Default formation: @{deck.experience.default_formation_id}

## Pre-generated artifacts and deliverables

The implementation workspace already contains the authoritative products of
`cards.weavemark.md`:

- `deck-data.js`;
- `assets/cards/prototype.png`;
- `assets/cards/card-1.png` through the validated final non-prototype number; and
- `assets/card-back.png`.

The implementation agent MUST inspect and reuse these artifacts. It MUST NOT
regenerate, redraw, rename, reinterpret, replace, duplicate, or omit them.

Deliver at least:

- `index.html`, the complete runnable application;
- `README.md`, covering serving, browsers, validation, privacy, manual play,
  optional-provider use, and known limitations; and
- only focused test/support files justified by validation.

Do not add a framework, build system, package manager, backend, CDN, analytics,
remote font, remote stylesheet/script, upload system, service worker, or account
system.

`index.html` MUST load exactly one classic same-origin
`<script src="deck-data.js">` before inline application JavaScript. Never
duplicate, fetch, embed, or recreate deck data inside HTML. Manual play makes
zero network requests.

## Deck initialization

Validate `globalThis.ARCANA_DECK` completely before rendering setup:

- schema, deck identity, prototype identity, unique ids, consecutive numbers;
- total and category counts, exactly 15 Major and 40 Minor for this deck;
- `major_count * 2 < minor_count`;
- suits, ranks, motifs, concept sources, formations, unique position ids;
- `draw_from` policies and formation feasibility;
- experience, maximum question length, provider, speech, and reflection depth;
- controlled relative artifact paths and successful image loading.

Normalize `prototype_card` plus `Object.values(deck.cards)`, sorted by explicit
`number`. Assign `assets/cards/prototype.png`, then
`assets/cards/card-1.png` through `card-N.png`, plus
`assets/card-back.png`. Derive `N` from the validated non-prototype count.

`deck.cards` uses consecutive string keys `1` through `N` as stable generated
artifact indices. Validate every key, bind each record to
`assets/cards/card-<key>.png`, and only then sort by the card's explicit `number`
for display. Never infer artwork from object iteration or sorted position.

Accept only relative `.png` paths with no scheme, host, leading slash,
backslash, query, fragment, control character, or `.`/`..` segment. Verify each
image has usable dimensions. If data, crypto, or assets are unavailable, render
one blocking recovery surface; never partially render or guess.

A structurally compatible replacement deck MUST work without code changes.

## State, storage, and cancellation

Define explicit shell, reading, per-position, inspection, provider, media, and
complete-focus state. Distinguish face-down, turning, revealed, AI text pending,
AI ready/failed, voice preparing/ready/failed, cancelled, and stale.

Every asynchronous operation uses a reading generation token, per-card token,
finite timeout, `AbortController`, and stale-result suppression. New reading,
replacement, cancellation, Forget key, and `pagehide` abort relevant work.
Card retries and final-synthesis invalidation MUST also abort the superseded
named request channel so stale work cannot continue billable execution.

Persist only non-secret preferences and explicitly saved readings/notes/history
in a versioned deck-id namespace. Validate restored data and recover visibly.
Never persist plaintext keys, unlock passphrases/derived keys, unsaved private
questions, provider request history, generated audio, Blob URLs, pending
requests, or transient selections. Optional key persistence MUST follow the
refined encrypted-secret-storage contract and remain disabled by default.
If the browser or password manager restores a key from protected credential
storage, detect the prefilled field without connecting or transmitting it,
state clearly that the browser restored it rather than Arcana, and offer
**Use restored key**. Once connected, say the restored key remains usable for
this page session and let the user keep it or enter and connect a replacement
without retyping the existing key. Forget key still clears page memory and
cancels provider/media work; never claim Arcana persisted the credential.

## Home hierarchy and entry

The page opens as a calm invitation, never a dashboard or catalog.

- The dominant ritual surface owns identity, formation, optional private
  question, reversals, card sound, and **Shuffle & enter**.
- A quieter subordinate **Optional OpenAI guide** inset contains progressively
  disclosed key, consent, model, speech, and depth controls.
- Wide layout is roughly two-thirds ritual and one-third optional guide. Narrow
  layout places ritual first. Never render equal competing panels.
- The guide has no competing primary action.

Provide a **Question inspiration** select beside the private-question field on
setup and in the active OpenAI drawer. Its default option is
**Choose a deep question…**, followed by these exact high-impact presets:

- What am I not seeing clearly about the choice before me?
- What pattern is asking to change in my life?
- What deserves my courage right now?
- What must I release to move forward with integrity?
- How can I meet this relationship more honestly?
- What would a wiser relationship with my work look like?
- Where am I confusing safety with stagnation?
- What part of myself needs attention rather than judgment?
- What possibility becomes visible if I stop forcing certainty?
- Write my own question…

Selecting a preset copies it into the private-question textarea while preserving
the ability to edit it. **Write my own question…** clears and focuses the
textarea. Presets are inspiration, never persisted questions, instructions, or
special provider authority.

On setup, place Question inspiration and its textarea before the formation list
so this immediate starting path is visible without first scrolling past every
formation.

On a fresh profile, initialize the reversal control from
`deck.experience.reversals_enabled_by_default`. A subsequently saved explicit
player preference may override that default.

Starting without both an accepted key and enabled guide opens one calm dialog:

- title **Enter without the OpenAI guide?**;
- actions **Enter without guide** and **Set up OpenAI**;
- Close/Escape/backdrop return without shuffling;
- explain that manual reading remains complete/private and OpenAI may be enabled
  later;
- preserve typed but unaccepted key text and state that it is not connected;
- after manual confirmation, shuffle once and never ask twice for that start.

## Secure deal and ritual

Use cryptographically secure Fisher-Yates with `crypto.getRandomValues`; never
`Math.random`. Validate feasibility before mutating the table. Predeal exactly
one unique face-down card into every position, respecting `any`, `major`, and
`minor` without replacement. Establish reversals during the deal.

Deal category-constrained positions before `any` positions, then restore the
formation's declared display order. This reserves category quotas so an early
`any` position cannot consume a card required by a later constrained position.

There is no Draw next, empty active position, or Reveal all. Each face-down card
is its direct reveal action. Reversed art rotates 180 degrees while written
meaning remains upright. New reading cancels work/audio, clears the table, and
returns to setup without navigation.

Major Arcana are rarer, suitless, reading-reframing forces. Minor Arcana locate
lived mechanisms through suit domain and rank process. Explain this in the Guide.

## Signature card turn

Build a stable perspective scene with separate front/back faces,
`transform-style: preserve-3d`, `backface-visibility`, explicit 2:3 geometry,
and no reflow.

Choreograph approximately 650-850ms: subtle press, small lift/deeper shadow,
decisive 180-degree turn, restrained edge-light sweep, gentle settle. Animate
only compositor-safe transform, opacity, filter, and shadow. No bounce, wobble,
particles, neon, screen shake, or casino spectacle.

Synchronize a local Web Audio paper hush with lift and two quiet resonant tones
near midpoint/settle. Lock only the turning card. Double click, key repeat,
hover, focus, resize, rerender, or async updates MUST NOT reverse it, expose both
faces, replay sound, leave it edge-on, or move layout. Reveal accessible
title/metadata and start AI work only after settle.

Reduced motion uses immediate face swap plus static highlight, preserving state,
focus, announcement, and sound preference.

## Card reflection

Every revealed card owns a compact **Card reflection** trigger. Do not expand
meanings inline or grow the formation. Clicking art selects; only the trigger
opens detail.

Use one spacious anchored reflection surface:

- wide: 440-640px side/editorial veil over sibling space, selected card visible;
- narrow: near-full-width sheet with selected-card preview/reserved region;
- page geometry and scroll remain stable; only reflection body scrolls as needed;
- Close, Escape, and backdrop restore trigger focus.

When a card or reflection/completion surface rerenders, remap stored invokers and
focused controls to replacement DOM nodes with `preventScroll`. Never retain a
detached reflection trigger or drop keyboard focus to `<body>` during async work.

Manual meaning appears first: position, essence, generative/destructive and
orientation meanings, emotional register, question, category/purpose, concept
source/factual anchor/boundary, reflective bridge, lineage, motifs, and
Minor suit/rank or explicit Major suitlessness.

The Card reflection surface remains manual-only and hidden until the player
activates its trigger. It MUST NOT contain or auto-open for AI interpretation.
Completion never auto-opens the surface, moves focus, or scrolls.

## Optional OpenAI guide

Use the exact configured OpenAI Responses endpoint and fixed `gpt-5.4-mini`.
Setup and active OpenAI drawer include:

- unchecked **Use OpenAI guide for this reading**;
- password input with `autocomplete="off"`;
- **Use key this session**, **Forget key**, session status, fixed model;
- complete consent summary;
- unchecked **Read reflections aloud**; and
- **Reflection depth**.

Keep the key only in a private JavaScript variable. Clear the input after
acceptance. Never store, export, log, render, or include the key as request
content. AI mode requires explicit consent, accepted key, and nonempty private
question.

`Use OpenAI guide for this reading` and `Read reflections aloud` are per-reading
consent choices. They MUST start unchecked on every new reading and MUST NOT be
persisted. A connected page-session key MAY remain available until Forget key or
page exit, but it can never imply consent for a later reading. Reflection depth is
the only AI preference that may persist.

The player may enable the guide later from active navigation. When consent, key,
and private question become available, reconcile every already revealed card whose
reflection is idle or cancelled: start exactly one request for each, mark it
pending before completion rerenders, and refresh final-action availability.
The active OpenAI drawer MUST provide a page-memory-only private-question field so
a reading begun without a question can become eligible later.
Changing or clearing that question MUST increment the reading/request generation,
abort dependent text and speech work, clear question-grounded reflections/final
synthesis, remove pending glow, and reconcile fresh requests only for the new
nonempty question.

Forget key MUST abort text and speech requests, invalidate media ownership,
stop narration, revoke Blob URLs, clear voice UI, and leave manual play unchanged.
Unchecking either consent control MUST immediately invalidate and abort the
corresponding pending work. A text response accepted after AI consent is revoked
MUST NOT update UI or start speech.
Every initial request and retry entry point MUST recheck current consent, key, and
private-question requirements before sending provider data; unavailable retries
must be hidden or disabled with a clear explanation.
Revoking consent MUST preserve already completed per-card reflections and complete
interpretation in page memory, UI, save, and export; only pending work is cancelled.

### Reflection depth

Render `deck.ai_guide.reflection_depth` as an accessible five-step range with
visible label/description, endpoint labels, configured default, and
`aria-valuetext`. Persist only this preference.

1. **Whisper**: exactly one sentence, at most 30 words; no tension/question.
2. **Brief**: one 60-90-word paragraph; no extra section.
3. **Balanced**: one 120-180-word paragraph plus one concise question; measure
   the paragraph budget independently from the question.
4. **Deep**: two/three paragraphs, one tension, one question, 250-400 words.
5. **Immersive**: several paragraphs, developed tension, one question,
   500-800 words.

Scale final synthesis proportionally: Whisper at most two sentences; Brief one
paragraph; Balanced two/three short paragraphs and one question; Deep
structured multi-section; Immersive developed pattern, counterpoint, and two or
three questions.

Validate final output shape after parsing: Whisper has one or two sentences;
Brief has exactly one paragraph; Balanced has exactly two or three paragraphs;
Deep/Immersive require nonempty synthesis, pattern, counterpoint, and their
configured question counts. Reject nonconforming structure visibly.

Depth is trusted developer configuration, never user content. Use strict JSON
Schema with unavailable sections explicitly nullable. Validate budgets and
structure after parsing. Brief and Balanced require exactly one reflection
paragraph; Deep requires two or three; Immersive requires at least three. Do not
render empty headings. Depth changes affect
future requests/final synthesis only; never regenerate existing text.

### Requests and glow

On reveal, send only the private request in a separate untrusted user role,
formation, position, and selected card's written fields/motifs/orientation.
Never send PNGs, art, key as content, history, notes, unrelated cards, or audio.
Use `store:false`, strict structured output, finite timeout, cancellation, and
stale suppression. Render output only as text.

During text work, animate an elegant ivory/mineral-blue/oxidized-gold tracer
around that exact card after its turn settles. It remains visible if reflection
closes. If voice is enabled, transition continuously to a calmer warm-gold phase
through request, decode, Blob creation, and metadata readiness. Do not flicker.
Multiple cards may glow independently. Final synthesis uses a coordinated
low-intensity formation glow. Reduced motion uses static luminous frames and
explicit phase labels.

Failures preserve manual play, explain precisely, and offer retry. Never invent
fallback text.

### Automatic AI interpretation side stage

Per-card AI interpretation comes to the player automatically through one shallow
stage rather than waiting inside Card reflection:

- After a revealed card starts its AI request, slide a tall editorial side pane
  in from the viewport edge beneath the sticky navigation. On wide and iPad-size
  layouts, reserve sibling space for it so the full card formation remains
  visible and operable rather than sitting underneath the pane.
- The pane belongs to the most recently revealed AI-enabled card. A later reveal
  replaces its content in place; completion from an older card MUST NOT steal it
  back. Multiple cards may continue computing independently.
- Pending, ready, and failed states are visible without focus theft, navigation,
  page scroll, or opening the manual reflection surface.
- Pending shows the card title/position/depth plus a soothing magical animation:
  restrained mineral-blue and oxidized-gold orbit lines, a slow luminous sweep,
  and quiet breathing light. No flashing, particles, neon, or spectacle. Reduced
  motion uses one static luminous constellation and status text.
- Ready shows the generated reflection and only the tension/question sections
  permitted by the selected depth. Failure shows the precise error and an
  eligibility-aware retry.
- When narration belongs to this card, include icon-only Play/Pause, Replay, and
  Stop controls plus accessible names/tooltips and the canonical media status.
  These controls mirror the same media state shown in the navbar.
- Include a clear **Close interpretation** control. Closing is respected for the
  current request/result; a newly revealed AI-enabled card opens the stage again.
- Do not move keyboard focus when the pane opens or updates. Announce
  pending/ready/error through a polite live region. If the player activates a
  control inside the pane to close it, return focus without scrolling to the
  owning revealed card; programmatic closure and closure invoked from elsewhere
  do not move focus.
- Give the side pane most of the available dynamic viewport height, with a
  comfortably readable width and an independently scrolling interpretation body
  for Deep/Immersive text. At narrow mobile widths it may become a near-full-width
  non-modal side sheet, but it must remain dismissible and must not alter scroll
  or focus when it appears.
- Recompute placement after resize, orientation change, media-transport changes,
  and formation layout changes.

This automatic pane is only for per-card AI interpretation. The explicit
**Contemplate the whole** synthesis retains its dedicated compact-card focus
layout.

## Speech and canonical media transport

Speech is separately opt-in. Display configured AI-voice disclosure. Send only
visible title/position and generated reflection fields to the configured
`gpt-4o-mini-tts`, `onyx`, MP3 boundary with exact speaking instructions—never
original question or notes.

Keep audio in page-memory Blob/Object URLs and revoke on replacement, new
reading, Forget key, and exit. Attempt playback only after text is visible. If
blocked, retain Play; failure retains text and offers Retry narration.

For iOS/iPadOS WebKit, including Chrome on iPad, create one persistent
`HTMLAudioElement` and prime it synchronously from a user gesture before delayed
TTS is fetched. Reuse that same element across narration and sequential chunks;
do not create a new playback element after the gesture expires. Resume the Web
Audio context in the same gesture. If playback is still blocked, expose a clear
tap-to-play state without treating decoded narration as failed.

The Speech API accepts at most 4096 input characters. Split longer Deep or
Immersive narration at sentence/word boundaries into chunks of at most 3900
characters. Fetch chunks sequentially under one voice/media ownership token and
play them as one logical playlist with combined elapsed/total progress. Never
truncate, omit, overlap, reorder, or expose separate competing transports.

Route turn sound and narration through one media controller; a new source
replaces the previous. Reserve navbar geometry from active entry so transport
appearance never moves the table.

Every media request owns a monotonically increasing token. A speech response may
install audio only while its token owns the current narration-preparing slot.
Starting a card turn, newer narration, Forget key, New reading, or Stop invalidates
older media tokens and aborts in-flight speech before stale responses can replace
current audio or continue billable work.

Whenever media is preparing, ready, playing, paused, completed, or replayable,
expose a slim navbar transport with source/card label, semantic progress, elapsed
and total `m:ss`, and icon-only Play/Pause, Replay, and Stop controls with
accessible names and tooltips. Use real metadata/events; before duration is known
show labelled indeterminate state, never NaN or fake duration. Turn sound uses
known duration and remains replayable briefly. The interpretation pane mirrors
the same canonical narration controls; the Sound drawer independently controls
effects/voice.

## Complete interpretation

Never synthesize automatically. After every card reveals, expose
**Contemplate the whole**. Only that action sends ordered positions, cards,
orientations, and successful per-card reflections.

When AI is enabled, expose the synthesis action only after every per-card text
request has settled as ready, failed, or cancelled. Pending reflections MUST
remain visibly pending and MUST NOT be frozen as `null` by an early synthesis.
`requestFinal` MUST repeat this guard immediately before constructing its payload.
Starting or retrying any card reflection MUST invalidate pending or completed
final synthesis, stale-suppress its response, clear final glow/focus, and require
a fresh explicit **Contemplate the whole** after the card request settles.
Forget key and every eligibility change MUST rerender completion immediately so a
stale synthesis action cannot remain visible.

Enter explicit focus layout: preserve all cards, reduce them enough to show
pending/final text in the same viewport where practical, and provide
**Restore full-size cards**. Approximately the first 240 CSS pixels of deliberate
upward scroll may progressively restore cards; reduced-motion/keyboard/touch
have explicit restoration. Keep final text below restored cards and never shrink
again without explicit focus.

While focus mode is active, **Restore full-size cards** MUST remain available
during synthesis pending, success, failure, cancellation, retry, and consent
revocation. Cancellation/failure MUST also clear the formation pending glow.

## Guide, gallery, history, export

Sticky active navigation exposes Guide, OpenAI, Sound, New reading, and
conditional media transport through one mutually exclusive accessible drawer.

Guide order: purpose/boundary; Major/Minor; two-minute reading; complete rules;
suits; ranks; every formation/position; generative/destructive; reversals;
collapsed Symbol concordance; adult-content/reflective-use note.

Gallery groups Major, then Minor by suit/rank, then common back. Completion
supports private notes, explicit local save/history/delete, JSON download, and
plain-text copy. Saved AI text records model/depth but never key/audio. Never
rerun AI from history.

JSON download and plain-text copy MUST both include successful per-card
reflections and the complete interpretation, including optional pattern,
counterpoint, tension, and questions.

## Visual and accessibility standard

Generated PNGs dominate. Do not duplicate integrated titles, recreate art, or
obscure cards. Use warm paper/daylight neutrals, mineral color, editorial system
serif display, readable system sans, quiet light, generous negative space, and
restrained texture. Browser chrome must not default to black.

Use semantic landmarks, labels, controls, dialogs/sheets, progress, and live
status; complete keyboard/pointer/touch; visible focus; 44px targets; 200% zoom;
forced colors; no drag-only path; no horizontal scroll at 320 CSS px.

Face-down cards expose no hidden title/category/description/meaning through alt,
accessible name, live region, DOM label, or focus. Preserve selection,
reflection, entered text, focus, and scroll across rerenders, resize, async
completion, and drawers. Never use color, orientation, image, or motion as sole
meaning.

## Security and validation

Use this CSP:
`default-src 'self'; img-src 'self'; media-src 'self' blob:;
style-src 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src
https://api.openai.com; object-src 'none'; base-uri 'none'; form-action 'none'`.
Omit ignored meta `frame-ancestors`.

No eval, dynamic code construction, upload, service worker, third-party storage,
user-editable endpoint, redirect, or remote URL beyond exact configured OpenAI
Responses/Speech endpoints.

The interactive implementation agent MUST:

1. inspect this compiled spec, raw deck data, representative Major/Minor art, and
   existing generated artifacts;
2. implement in a clean workspace/source file without copying a prior runtime;
3. serve the real static directory over HTTP;
4. iterate with Playwright MCP over home hierarchy, manual confirmation, secure
   category-aware deal, full/reduced turn, reflection geometry, every depth,
   text/voice glow, TTS success/failure/retry, media controls, final focus/restore,
   drawers/focus, privacy/storage, 320px, console, network, and restart;
5. fix observed defects and rerun syntax, tests, lint, and browser flows;
6. report concrete evidence and honest remaining limitations.

Completion requires runnable `index.html`, README, preserved artifacts, clean
validation, and browser evidence. A plausible code dump, compiled specification,
or screenshot alone is not completion.

Use this boundary once in Guide and once in footer:
"@{deck.experience.boundary_statement}"

Output only the final Markdown implementation specification.
