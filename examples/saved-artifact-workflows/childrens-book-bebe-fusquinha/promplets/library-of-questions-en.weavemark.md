@promplet version: 0.7

### Cast names in this edition

  The bible names the cast in Portuguese; in THIS English edition they are called:
  - **Baby Bug** — the small, luminous light-blue Beetle car (the bible's "Bebê Fusquinha").
  - **Baleen** — the large deep-blue whale-shaped boat (the bible's "Barco Baleião").
  - **Forkwing** — the winged, fork-carrying flyer (the bible's "Garfudo").

  Use ONLY these English names in every reader-facing word — the title and the narration
  lettered into each page. Keep each character's visual anchor exactly as the bible
  describes it; only the name changes, never the look.

  ## Dramatic structure of this story

  - **Act 1 — The invitation (pages 1 to 4):** the friends find the map, locate the
    library, and go inside. Emotion: curiosity and anticipation.
  - **Act 2 — The questions come alive (pages 5 to 9):** small adventures tied to the
    questions inside the books. Emotion: wonder, participation, and discovery.
  - **Act 3 — The question with no answer (pages 10 and 11):** Baby Bug meets
    something he cannot solve. Emotion: a little tension and then relief.
  - **Act 4 — The world grows wider (pages 12 to 15):** the friends realize there are
    endless questions and that curious children help write the library. Emotion:
    inspiration and an opening for the imagination.

  ## Page-by-page script — exactly what happens

  The complete script of this story lives in the `pages` variables (one entry per
  page, with `.scene` and `.text`). Build the book to this exact spine, one entry
  per page, IN ORDER. For each page: (1) use that page's **narration** (`.text`) as
  that page's text, word for word — do NOT rewrite, summarize, reorder, merge, or
  invent pages; preserve the bold questions and the closing line; (2) turn the
  **scene** (`.scene`) into an on-model and COMPACT illustration prompt — at most
  about 800 characters per page — briefly restating only the essential visual anchor
  of each character who appears (the full canon is already in the bible above; do not
  copy the whole bible into every page); (3) since text_in_image is on, letter that
  page's narration INSIDE the illustration, in @{language}, with correct spelling,
  accents, and punctuation, large and legible, well clear of the faces — rendering any
  Markdown emphasis as visual emphasis (words in **double asterisks** lettered BOLD,
  words in *single asterisks* lightly emphasized), NEVER drawing the asterisks or any
  other Markdown characters into the art.

  Keep EACH `illustration` prompt lean and self-contained, so the whole book stays
  compact.

  - **Page 1** — scene: @{pages.1.scene} — narration: @{pages.1.text}
  - **Page 2** — scene: @{pages.2.scene} — narration: @{pages.2.text}
  - **Page 3** — scene: @{pages.3.scene} — narration: @{pages.3.text}
  - **Page 4** — scene: @{pages.4.scene} — narration: @{pages.4.text}
  - **Page 5** — scene: @{pages.5.scene} — narration: @{pages.5.text}
  - **Page 6** — scene: @{pages.6.scene} — narration: @{pages.6.text}
  - **Page 7** — scene: @{pages.7.scene} — narration: @{pages.7.text}
  - **Page 8** — scene: @{pages.8.scene} — narration: @{pages.8.text}
  - **Page 9** — scene: @{pages.9.scene} — narration: @{pages.9.text}
  - **Page 10** — scene: @{pages.10.scene} — narration: @{pages.10.text}
  - **Page 11** — scene: @{pages.11.scene} — narration: @{pages.11.text}
  - **Page 12** — scene: @{pages.12.scene} — narration: @{pages.12.text}
  - **Page 13** — scene: @{pages.13.scene} — narration: @{pages.13.text}
  - **Page 14** — scene: @{pages.14.scene} — narration: @{pages.14.text}
  - **Page 15** — scene: @{pages.15.scene} — narration: @{pages.15.text}

  ## Visual clues for re-readings (subtle)

  Scatter, discreetly and without explaining them in the text: a small red book that
  reappears on several pages; a fish that watches Baby Bug before the underwater
  adventure; an unusually shaped star that reappears on the cover of the white book; a
  root that crosses the floor already on page 3; a clock with no hands that appears on
  page 4 and starts working again on page 13; and loose letters that partly spell out
  the word for "why" on one of the pages.
