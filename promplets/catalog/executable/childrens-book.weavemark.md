@promplet version: 0.7

@note
  Children's picture-book pipeline expressed FULLY in WeaveMark — authoring,
  per-page image rendering, AND packaging into print-ready deliverables, with no
  external script.

  Stage `author` refines the shared illustrated-story core (picture-book format
  pinned via a @refine binding) and emits the STRICT JSON book: a title plus N
  pages, each with a self-contained illustration prompt and its narration.

  Stage `page` is then REPEATED once per page (repeat: page, count: @{page_count}).
  Each iteration renders ONE full illustration for page @{index} from the authored
  book (seen via @{author}) and PERSISTS it via `@output file:` to a per-page path.
  With text_in_image on (the default) the narration is lettered directly into each
  illustration, so every image is a COMPLETE page ready to print.

  The two `@package` steps then assemble the deliverables: a print-ready HTML book
  (a packaging-template promplet fills a skeleton with the produced page images —
  a semantic assembly, no external code), and a PDF converted from that HTML.

  Companion vars set page_count, audience, art_style, characters, lessons, tone,
  text_in_image, and the image controls image_size / image_quality / image_model.
  This spec also owns the book-specific `pages` beat sheet: `pages` is a JSON
  object keyed by page number ("1".."@{page_count}"), each with a `.scene` (what
  the illustration shows) and a `.text` (the narration to letter onto that page).
  The author stage reads them via dotted paths (@{pages.1.scene}, @{pages.1.text},
  …) so the whole arc is deliberately authored, page by page.

@execute chain
  repeat: page
  count: @{page_count}

@prompt author
  @refine module:weavemark.domains.creative.illustrated_story_core
    with story_format: "picture-book"

  ## Page beat sheet — exactly what happens on each page

  Build the book to this exact page-by-page spine, in order — one entry per page.
  For each page, turn `.scene` into a full, on-model illustration prompt (restating
  every character's visual anchor), and use `.text` as that page's narration —
  keep its meaning and any distinctive words, refining only lightly for read-aloud
  rhythm. Do not skip, reorder, merge, or invent pages.

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

@prompt page
  @output type: image
    file: pages/page-@{index}.png
    size: @{image_size}
    quality: @{image_quality}
    model: @{image_model}
  You are the illustrator for the picture book below. Render page @{index} of
  @{count} as ONE finished illustration.

  Follow that page's `illustration` prompt EXACTLY — its art style and every
  character's restated visual anchor — so the page stays perfectly on-model with
  the rest of the book. If the page's prompt asks for narration text to be
  lettered into the image, render those exact words large and legibly, clear of
  faces. Output ONLY the image, no commentary.

  The full authored book (JSON), for story context and cross-page consistency:
  @{author}

@package template: module:weavemark.domains.creative.picture_book_html file: book.html
@package from: book.html file: book.pdf
