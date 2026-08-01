@promplet version: 0.9
@compile context: local

# Arcana — card and content generation

@note
  Executable artifact-generation promplet for Arcana. Its only job is to validate
  the supplied deck, render the titled card fronts and common back, and emit the
  inert runtime deck data. It does not specify or implement the browser
  application.

  Run this promplet only when this source or the concrete deck input changes.
  `app.weavemark.md`, beside this file, is the separate non-executable source that
  always compiles the browser-application specification for an interactive
  programming agent.

  Execution order:
  1. `author` audits the supplied deck and emits a compact production manifest.
  2. `prototype` renders the authoritative titled visual-reference card.
  3. `card` repeats once per non-prototype card, always editing from the prototype.
  4. `back` renders the shared orientation-hiding card back.
  5. `@emit` writes the complete inert runtime deck to `deck-data.js`.

@execute chain
  repeat: card
  items: @{deck.cards}

@emit file: deck-data.js
  "use strict";
  globalThis.ARCANA_DECK = @{deck};

@prompt author
  @output enforce: strict

  You are the author, symbologist, deck editor, and senior art director for an
  adult archetypal card game. Audit the supplied nested deck definition and emit
  one compact production manifest. The concrete input remains authoritative;
  never reconstruct, summarize away, or duplicate its card records.

  Supplied deck definition:

  @{deck}

  Return ONLY valid JSON, with no Markdown fence, preamble, or trailing text.
  Validate the declared card count, Major and Minor counts, prototype id,
  non-prototype count, unique card ids and numbers, category rules, Minor suit
  and rank references, concept-source fields, motif references, formation
  policies, AI-guide boundary, and value-key distribution. Major count MUST be
  strictly less than half Minor count: `major_count * 2 < minor_count`. Do not
  invent replacements for concrete supplied data.

  The returned object must contain exactly:

  - `schema_version`: integer `1`;
  - `deck_id`: supplied deck id;
  - `declared_card_count`: supplied total card count;
  - `major_count`: supplied Major Arcana count;
  - `minor_count`: supplied Minor Arcana count;
  - `prototype_id`: supplied prototype card id;
  - `render_ids`: ordered non-prototype card ids;
  - `value_key_counts`: object with `high`, `middle`, and `low` integer counts;
  - `warnings`: array of concrete validation warnings, empty only when consistent.

  Return no card meanings, illustration prompts, visual-bible copy, or other
  duplicated content.

@prompt prototype
  @output type: image
    file: assets/cards/prototype.png
    size: @{deck.production.image_size}
    quality: @{deck.production.image_quality}
    model: @{deck.production.image_model}

  You are the lead illustrator establishing the authoritative visual reference
  for a complete adult archetypal card deck.

  Complete visual bible:

  @{deck.visual_bible}

  Arcana ontology:

  @{deck.arcana}

  Minor suit vocabulary:

  @{deck.suits}

  Minor rank vocabulary:

  @{deck.ranks}

  Motif vocabulary:

  @{deck.motifs}

  Exact prototype card:

  @{deck.prototype_card}

  Follow the prototype's exact `image_brief`, category, meanings, motifs,
  concept source, reflective bridge, emotional register, and `value_key`.
  Produce one finished, gallery-quality
  vertical 2:3 PNG card-front illustration. It must feel profound, painterly,
  tactile, emotionally exact, and made for adults—not geometric placeholder art,
  vector iconography, a UI mockup, or a generic fantasy card.

  This PNG becomes the DIRECT visual reference for the rest of the deck. Resolve
  the house style at production quality: sophisticated figurative composition,
  authored architecture and objects, atmospheric depth, motivated light, nuanced
  material rendering, quiet symbolic detail, and a coherent hand-made surface.
  The prototype MUST have a balanced middle-key exposure with luminous blue
  daylight, visible architecture, and broad tonal range. It establishes craft,
  not a mandatory dark exposure for later cards.

  Include the border and nonlinguistic ornamental grammar. Letter the exact title
  **"@{deck.prototype_card.title}"** character-for-character inside the finished
  artwork, using the visual bible's `title_lettering` contract. The title must be
  elegant, materially integrated, correctly spelled, and readable at card size.
  Render NO other readable words, letters, numerals, caption, pseudo-lettering,
  signature, watermark, or logo. Output ONLY the image.

@prompt card
  @output type: image
    file: assets/cards/card-@{item_key}.png
    size: @{deck.production.image_size}
    quality: @{deck.production.image_quality}
    model: @{deck.production.image_model}
    edit: on
    edit_from: prototype:first

  You are rendering non-prototype card @{index} of @{count} for the deck below.
  The stable artifact index for this card is @{item_key}; the companion input
  requires consecutive string keys `1` through `@{count}`.
  The approved prototype PNG is supplied directly to the image model as the
  fixed visual reference for EVERY iteration. Preserve its medium, palette
  discipline, border geometry, material finish, mark-making, symbolic subtlety,
  tonal nuance, and emotional restraint—but replace its central scene completely
  and obey the current card's exact `value_key`. Do not copy the prototype's
  exposure, darkness level, color temperature, time of day, or weather when the
  current card specifies another expression.
  Do not preserve the prototype's figure, pose, object arrangement, camera, or
  dominant silhouette.

  Exact production-plan entry for this card:

  @{item}

  Complete visual bible:

  @{deck.visual_bible}

  Arcana ontology plus Minor suit, rank, and motif vocabularies:

  @{deck.arcana}

  @{deck.suits}

  @{deck.ranks}

  @{deck.motifs}

  Follow this entry's exact `image_brief`, category, meanings, concept source,
  reflective bridge, motifs, emotional register, and `value_key`. A Major card
  is suitless and uses the Major frame grammar. A Minor card must use its exact
  suit and rank plus the Minor frame grammar. Produce ONE finished,
  gallery-quality vertical 2:3 PNG card-front illustration. It must be a richly authored
  figurative or environmental illustration, never geometric placeholder art,
  vector iconography, a UI mockup, or generic fantasy-card filler.

  Make this card immediately distinguishable from every earlier card while
  unmistakably belonging to the same deck. Preserve its exact assigned motifs,
  emotional register, impossible image, focal hierarchy, and negative-space
  brief. Include the shared border and nonlinguistic ornamental grammar. Letter
  the exact supplied `title` from @{item} character-for-character inside the
  finished artwork, using the visual bible's `title_lettering` contract. The title
  must be elegant, materially integrated, correctly spelled, and readable at card
  size. Render NO other readable words, letters, numerals, caption,
  pseudo-lettering, signature, watermark, or logo. Output ONLY the image.

@prompt back
  @output type: image
    file: assets/card-back.png
    size: @{deck.production.image_size}
    quality: @{deck.production.image_quality}
    model: @{deck.production.image_model}
    edit: on
    edit_from: prototype:first

  Render ONE finished common back for the deck described below:

  @{deck.visual_bible}

  The approved prototype PNG is supplied directly as the house-style reference.
  Replace its scene with a formal, nonfigurative woven emblem built from all suit
  sigils around a deep central void. The back must be exactly invariant under
  180-degree
  rotation: vertically and horizontally balanced, with paired motifs, light,
  texture, wear, and ornament so no mark can reveal upright versus reversed
  orientation. Keep the same painterly material finish, border grammar, palette
  discipline, paper texture, and restrained metallic accents as the fronts.

  This is high-quality illustrated card-back artwork, not a flat vector pattern,
  geometric placeholder, logo, UI panel, or mockup. Render absolutely NO readable
  words, title, numeral, letters, caption, pseudo-lettering, signature, watermark,
  or logo. Output ONLY the image.
