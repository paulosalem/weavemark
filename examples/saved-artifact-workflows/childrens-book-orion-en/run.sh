#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

OUT=examples/saved-artifact-workflows/childrens-book-orion-en/outputs
mkdir -p "$OUT"

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

# Stage 0 — Inspect the compiled chain. childrens-book.weavemark.md is an
# @execute chain: an `author` stage @refines the shared illustrated-story core
# (promplets/domains/creative/fragments/illustrated-story-core.weavemark.md, picture-book
# format) to emit a strict JSON book, then a `page` stage is REPEATED once per
# page to render each illustration. The heavy lifting (characters, consistency
# doctrine, art styles, age adaptation, per-page JSON output contract, and the
# text_in_image toggle) lives in the core.
section "Children's book: compiled authoring chain"
weavemark library builtin:catalog/executable/childrens-book \
  --vars-file examples/saved-artifact-workflows/childrens-book-orion-en/inputs/vars.json \
  --output "$OUT/compiled-prompt.md" \
  --show-output \
  --no-file-summary \
  --batch-only

# Stage 1 — Run the whole book FULLY IN WEAVEMARK. `--run` executes the chain:
# the `author` stage writes the JSON book; the `page` stage renders one full
# illustration per page and PERSISTS each via `@output file: pages/page-N.png`;
# then the two `@package` steps assemble the deliverables — a print-ready
# book.html (a packaging-template promplet fills a skeleton with the produced
# page images, a semantic assembly) and book.pdf (converted from the HTML via
# headless Chromium). No external script. With text_in_image on (default) each
# page's narration is lettered into its illustration, so every image is a
# complete printable page — no screen needed for the child.
#   -> outputs/pages/*.png (one illustration per page)
#   -> outputs/book.html   (print-ready HTML, references pages/)
#   -> outputs/book.pdf    (the printable book)
section "Children's book: run + package (fully in WeaveMark)"
weavemark library builtin:catalog/executable/childrens-book \
  --run \
  --vars-file examples/saved-artifact-workflows/childrens-book-orion-en/inputs/vars.json \
  --output-dir "$OUT" \
  --batch-only

section "Artifacts written"
find "$OUT" -maxdepth 2 -type f | sort | sed 's#^#- #'
