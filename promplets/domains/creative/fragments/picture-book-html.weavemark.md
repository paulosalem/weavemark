@promplet version: 0.7

@module weavemark.domains.creative.picture_book_html

@note
  Reusable PACKAGING TEMPLATE for picture books. It is an ordinary WeaveMark that
  a pipeline invokes via `@package template: ... file: book.html`. After the book
  pipeline runs, the packaging phase compiles this template with the pipeline's
  outputs and produced artifacts in scope, then EXECUTES it: the model performs
  the final assembly (a semantic transformation) — one printed page per produced
  image, in order — and emits a complete, print-ready HTML document.

  Context provided by the packaging phase:
    - @{title}       : the book title (an input variable)
    - @{page_files}  : the ordered relative paths of the rendered page images
                       (the `page` stage's persisted artifacts)
    - @{author}      : the authoring stage's output (the strict JSON book), used
                       for narration captions when text is NOT baked into images
    - @{text_in_image}: "on" (default) baked-in text -> full-bleed pages;
                        "off" -> separate caption band under each image
    - @{cover_image} : optional relative path to an illustrated cover image. When
                       set, it becomes the full-bleed first page; when absent, a
                       simple text title cover is generated instead.

You assemble a COMPLETE, print-ready HTML document for a children's picture book.
Output ONLY the HTML document — no explanation, and no Markdown code fences.

Book title: @{title}

Page images to include, IN THIS EXACT ORDER (relative paths). Emit EXACTLY one
printed page per image, in this order — never add, drop, reorder, or invent
images, and use each path verbatim:

@{page_files}

Document requirements:
- A `<!doctype html>` document whose `<style>` uses
  `@page { size: 1536px 1024px; margin: 0; }` and CSS so every
  `<section class="page">` is exactly one printed page (1536x1024, no margins,
  no page breaks inside).
@if cover_image
  - A cover page first: one `<section class="page cover">` whose only content is an
    `<img src="@{cover_image}">` that fills the ENTIRE page (full-bleed, no margins),
    i.e. the illustrated book cover. Do NOT overlay the title as text — the title is
    already lettered into the cover art.
@else
  - A cover page first: one `<section class="page cover">` showing the title
    "@{title}", large and centered on a warm background.
- Then one `<section class="page">` per listed image, in the given order, each
  containing an `<img>` whose `src` is that exact relative path and which fills
  the page.

@match text_in_image
  "off" ==>
    The narration is NOT drawn inside the images. For each page, let the image
    fill roughly the top 74% of the page and print that page's narration text in
    a caption band below it. Take the narration from this authored book JSON,
    matching pages to images by their order:

    @{author}
  _ ==>
    The page narration is already lettered inside each illustration, so every
    image must fill its ENTIRE page (full-bleed) with NO caption text added.

Output only the final HTML document.
