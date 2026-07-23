@promplet version: 0.7

@refine module:weavemark.domains.programming.foundations.base_spec_author
@refine module:weavemark.domains.programming.stacks.browser_static_esmodules
@refine module:weavemark.domains.programming.types.mobile_first_webapp
@refine module:weavemark.domains.programming.modules.card
@refine module:weavemark.domains.programming.modules.snap_card_feed
@refine module:weavemark.domains.programming.modules.static_content_packs
@refine module:weavemark.domains.education.knowledge_card_curriculum

# Knowledge Cards

Write an implementation-ready specification for a polished mobile-first web app
that turns the familiar one-card-at-a-time social feed into cumulative learning.
It runs entirely as static HTML, CSS, and JavaScript with no backend.

## Content edition

Pre-generate one coherent pack for each topic in:

@{topics}

Each pack contains exactly @{cards_per_pack} cards. The maintained example inputs
are checked in beside this promplet as `knowledge-cards.vars.json`.

The app MUST make no runtime LLM calls. Pack content and optional explanatory
media are reviewed, versioned, validated, and checked in. Adding a conforming
`content/packs/<pack-id>/` directory and regenerating the static pack index makes
the pack discoverable without application-code changes.

## Learning experience

- Start in a pack library showing purpose, level, card count, progress, and last
  position. Opening a pack resumes or starts a session.
- Show one full-height knowledge card at a time. Vertical touch scrolling is
  primary; explicit controls and keyboard navigation are equivalent.
- The document/main window MUST be the only vertical scroll container. A knowledge
  card expands to its full content and MUST NOT use an internal scroll pane.
- Support Like, Save, Revisit, Add/edit note, Share/copy link, and an optional
  "I understand this" self-rating. Keep note entry reachable above the mobile
  keyboard and preserve drafts.
- Order unseen cards with a deterministic, prerequisite-safe mix of importance,
  foundational value, variety, and bounded randomness. Do not optimize for likes
  or dwell time. Explain deliberate revisits.
- Show subtle pack progress and session time. After 10 cards or 10 minutes, offer
  a calm stopping point with what was learned and where to resume; never shame the
  user for stopping or losing a streak.
- Provide saved cards, notes, history, per-pack progress, ordered/shuffled modes,
  text-size controls, reduced motion, and a resettable onboarding explanation.

## Local state

Bundled packs are immutable application content. Store preferences, progress,
session order, likes, saves, revisit choices, understanding signals, and notes
locally in IndexedDB under versioned schemas. Work offline after first load.
Provide explicit JSON export/import with validation, preview, duplicate handling,
and rollback. No account, analytics profile, remote sync, ads, or notification
permission is required.

## Product character

Make it feel focused, inviting, and tactile rather than academic or gamified:
warm paper, deep ink, one restrained accent per pack, excellent typography, and
illustrations only when they teach. The social-feed familiarity is an interaction
shortcut, not permission for dark patterns, fake popularity, autoplay, or
attention extraction.

## Deliverable

Produce a complete static implementation under
`outputs/implementations/knowledge-cards/`, including all example packs, schemas,
the deterministic pack-index/validation command, local-state repository, tests,
README, and GitHub Pages-ready assets.

@output enforce: strict
  Return `# Knowledge Cards`, then exactly eight H2 sections in this order, named
  by the list below. Do not add a preface, extra H2 sections, or a repeated outline.
  1. Product promise, learning model, and non-goals
  2. Static architecture, mobile shell, and offline lifecycle
  3. Pack convention, schemas, discovery, and build-time validation
  4. Knowledge-card model, curriculum rules, and example-pack requirements
  5. Feed ordering, interactions, notes, progress, and attention safeguards
  6. IndexedDB state, export/import, privacy, and recovery
  7. Interface states, accessibility, responsive behavior, and visual direction
  8. File tree, implementation sequence, tests, and acceptance criteria

@assert contains: "content/packs"
@assert contains: "IndexedDB"
@assert contains: "runtime LLM"
@assert contains: "attention"
