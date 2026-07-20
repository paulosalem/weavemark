@promplet version: 0.7

# Children's Picture Book

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
  (reusable package instructions semantically assemble the produced page images,
  with no external glue code), and a PDF converted from that HTML.

  Companion vars set page_count, audience, art_style, characters, lessons, tone,
  text_in_image, and the image controls image_size / image_quality / image_model.
  This spec also owns the book-specific `pages` beat sheet: `pages` is supplied
  as JSON with one ordered entry per page, each carrying the exact scene and
  narration. The author stage receives that complete value so any `page_count`
  can be grounded without a fixed enumeration.

@execute chain
  repeat: page
  count: @{page_count}

@prompt author
  @refine module:weavemark.domains.creative.illustrated_story_core
    with story_format: "picture-book"

  ## Page beat sheet — exactly what happens on each page

  Build the book to this exact page-by-page spine, in order — one entry per page.
  For each supplied entry, turn its `scene` into a full, on-model illustration
  prompt (restating every character's visual anchor), and use its `text` as that
  page's narration. Preserve the exact provided text and distinctive staging;
  refine only surrounding illustration detail and read-aloud rhythm. Do not skip,
  reorder, merge, truncate, or invent entries, and ensure all @{page_count}
  authored beats are represented.

  Supplied `pages` beat sheet:

  @{pages}

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

@package instructions: module:weavemark.domains.creative.picture_book_html file: book.html
@package from: book.html file: book.pdf
