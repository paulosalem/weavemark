@promplet version: 0.7

@note
  MAIN STORY FILE (English) — "Baby Bug and the Lost Library of Questions", the
  English edition of the 15-page picture book, expressed FULLY in WeaveMark (authoring,
  an illustrated COVER, per-page rendering, and packaging into a print-ready book),
  with no external script.

  This is the SAME story as its Portuguese original
  (`book-pt.weavemark.md`): it reuses ALL the same
  input promplets — it @refines the shared illustrated-story-core (picture-book
  format, pinned), the local named Bebê Fusquinha universe module, and a local
  path-based story fragment. Only the companion vars are translated. The reader-facing language is
  chosen ENTIRELY by the `language` var (here "English"): the core and every
  prompt below letter reader-facing words in @{language}, so flipping that one
  var flips the whole book's language.

  Stage `author` emits the STRICT JSON book (title + 15 pages, each with a
  self-contained illustration prompt and its narration). The narration text of
  every page is FIXED — it must be lettered verbatim, in @{language}, into each
  illustration (text_in_image on).

  Stage `cover` renders ONE illustrated book cover (not part of the script) and
  persists it to `cover.png`. Stage `page` is REPEATED once per page
  (repeat: page, count: @{page_count}), rendering each page's full illustration to
  `pages/page-@{index}.png`. The two `@package` steps then assemble a print-ready
  HTML book (opening with the illustrated cover) and a PDF converted from it.

  Companion vars (`../en/inputs/vars.json` from this example family) set language,
  page_count, audience, tone, art_style, premise, lessons, the image controls,
  title, and cover_image — AND the page-by-page `pages` beat sheet: a JSON object
  keyed by page number ("1".."@{page_count}"), each with a `.scene` (what the
  illustration shows) and a `.text` (the fixed narration to letter onto that page).
  The author stage reads them via dotted paths (@{pages.1.scene}, @{pages.1.text},
  …). The reusable universe lives beside this entrypoint as the local module
  `examples.baby_bug.universe`.

@execute chain
  repeat: page
  count: @{page_count}

@prompt author
  @refine module:weavemark.domains.creative.illustrated_story_core
    with story_format: "picture-book"

  ## Character universe — canonical source

  Use the bible below as the canonical source for the cast, the world, the visual
  style, and the production rules of this story. Restate, in full, each character's
  visual anchor in EVERY illustration in which they appear; do not rewrite
  personalities, do not alter colors or proportions, and do not introduce villains.

  The bible is written in Portuguese: treat it purely as REFERENCE for identity and
  look. Write the illustration and staging instructions in English, and write every
  reader-facing word — the title and the narration lettered into each page — in
  @{language}.

  @refine module:examples.baby_bug.universe mingle: false

  @refine ./library-of-questions-en.weavemark.md mingle: false

@prompt cover
  @output type: image
    file: cover.png
    size: @{image_size}
    quality: @{image_quality}
    model: @{image_model}
  You are the illustrator of the COVER of this children's book. Render ONE
  illustrated cover — enchanting and perfectly on-model — in the visual style of the
  canonical universe below.

  @refine module:examples.baby_bug.universe mingle: false

  In this English edition the cast is named: **Baby Bug** (the light-blue Beetle car,
  the bible's "Bebê Fusquinha"), **Baleen** (the whale-shaped boat, "Barco Baleião"),
  and **Forkwing** (the winged fork-carrier, "Garfudo"). Only the names change — every
  visual anchor stays exactly as the bible describes.

  The cover must:
  - bring together the three friends — Baby Bug, Baleen, and Forkwing — restating in
    full the visual anchor of each exactly as described above;
  - evoke the Library of Questions in the background — towers among enormous trees,
    golden light, and glowing floating books — without revealing the story's ending;
  - keep the universe palette (light blue, deep blue, turquoise, emerald green, gold,
    warm yellow, cream) and a warm, cinematic light;
  - letter the book's TITLE INSIDE the art, large and legible, in @{language}, with
    correct spelling, accents, and punctuation, well clear of the faces, exactly as:
    "@{title}".

  Produce ONLY the cover image, with no commentary.

@prompt page
  @output type: image
    file: pages/page-@{index}.png
    size: @{image_size}
    quality: @{image_quality}
    model: @{image_model}
  You are the illustrator of the children's book below. Render page @{index} of
  @{count} as ONE finished illustration.

  Follow that page's `illustration` prompt EXACTLY — its art style and the restated
  visual anchor of every character — so the page stays perfectly on-model with the
  rest of the book. Since the prompt asks for the narration to be lettered into the
  image, write those exact words, large and legible, in @{language} and well clear of
  the faces. Render any Markdown emphasis as visual emphasis, never as symbols: words
  wrapped in **double asterisks** must be lettered as BOLD words, and words in
  *single asterisks* as slightly emphasized words — do NOT draw the asterisks or any
  other Markdown characters into the image. Produce ONLY the image, with no commentary.

  The full authored book (JSON), for context and cross-page consistency:
  @{author}

@package template: module:weavemark.domains.creative.picture_book_html file: book.html
@package from: book.html file: book.pdf
