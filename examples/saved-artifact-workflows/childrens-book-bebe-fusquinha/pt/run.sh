#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/_lib/example-env.sh"

ROOT=examples/saved-artifact-workflows/childrens-book-bebe-fusquinha
PROMPLETS="$ROOT/promplets"
OUT="$ROOT/pt/outputs"
mkdir -p "$OUT"

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

# Stage 0 — Inspect the compiled chain as structured JSON.
# bebe-fusquinha-biblioteca-das-perguntas.weavemark.md
# is an @execute chain whose `author` stage @refines the shared illustrated-story-core
# (picture-book format), the local named Bebê Fusquinha universe module, and a local
# path fragment in the example's flat promplets folder.
# The 15-page Portuguese script lives in vars.json under `pages` (one entry per page,
# each with a `.scene` and a `.text`); the author stage reads them via dotted paths
# (@{pages.1.scene}, @{pages.1.text}, …) — the same convention as the English book.
# `language: "Portuguese"` (in vars.json) makes all reader-facing text — narration
# and the title lettered into the cover — Portuguese, with correct accents.
section "Bebê Fusquinha (PT): compiled authoring chain"
weavemark library book-pt --library-dir "$PROMPLETS" \
  --vars-file "$ROOT/pt/inputs/vars.json" \
  --format json \
  --output "$OUT/compiled-chain.json" \
  --no-file-summary \
  --batch-only

# Stage 1 — Run the whole book FULLY IN WEAVEMARK. `--run` executes the chain:
# the `author` stage writes the JSON book; the `cover` stage renders ONE illustrated
# book cover (with the title lettered in Portuguese) and PERSISTS it to cover.png;
# the `page` stage renders one full illustration per page and PERSISTS each via
# `@output file: pages/page-N.png`; then the two `@package` steps assemble a
# print-ready book.html (opening full-bleed with cover.png, then one page per image)
# and book.pdf (converted from the HTML via headless Chromium). No external script.
# With text_in_image on, each page's narration is lettered into its illustration,
# so every image is a complete printable page.
#   -> outputs/cover.png    (illustrated book cover — not part of the script)
#   -> outputs/pages/*.png   (one illustration per page)
#   -> outputs/book.html     (print-ready HTML, cover + pages)
#   -> outputs/book.pdf      (the printable book)
section "Bebê Fusquinha (PT): run + package (fully in WeaveMark)"
weavemark library book-pt --library-dir "$PROMPLETS" \
  --run \
  --vars-file "$ROOT/pt/inputs/vars.json" \
  --output-dir "$OUT" \
  --batch-only

section "Artifacts written"
find "$OUT" -maxdepth 2 -type f | sort | sed 's#^#- #'
