#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

OUT=examples/saved-artifact-workflows/comic-strip-en/outputs
mkdir -p "$OUT"

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

# Stage 0 — Inspect the compiled pipeline. comic-strip.weavemark.md is an
# @execute reflection spec (a production chain followed by a critique -> revise
# loop). The `author` stage @refines the shared illustrated-story core
# (promplets/domains/creative/fragments/illustrated-story-core.weavemark.md, comic-strip format,
# references on); the five reference images (style-reference comic + four
# character sheets) are Markdown image references, so the compiler lifts them into
# multimodal inputs for BOTH the author (vision) and the render (image edit).
section "Comic strip: compiled pipeline"
weavemark library builtin:catalog/executable/comic-strip \
  --vars-file examples/saved-artifact-workflows/comic-strip-en/inputs/vars.json \
  --output "$OUT/compiled-prompt.md" \
  --show-output \
  --no-file-summary \
  --batch-only

# Stage 1 — Generate the comic FULLY IN WEAVEMARK, no external script. `--run`
# executes the reflection pipeline: the `author` stage reads the references and
# writes one detailed, on-model image-generation prompt; the `generate` stage
# renders the strip from that prompt, conditioning the image model DIRECTLY on the
# references (`edit: on`), and persists it via `@output file: comic-strip.png`;
# then the `critique` role vision-inspects the RENDERED strip and `revise` edits
# it to fix defects, repeating until it passes (rounds: 3). A Markdown trace of
# every step (authored prompt + per-round critiques) is written to inspection-log.
#   -> outputs/comic-strip.png    (the final strip)
#   -> outputs/inspection-log.md  (authored prompt + per-round visual critique)
section "Comic strip: run (author + reference-conditioned self-inspecting render)"
weavemark library builtin:catalog/executable/comic-strip \
  --run \
  --vars-file examples/saved-artifact-workflows/comic-strip-en/inputs/vars.json \
  --output-dir "$OUT" \
  --trace-output "$OUT/inspection-log.md" \
  --batch-only

section "Artifacts written"
find "$OUT" -maxdepth 2 -type f | sort | sed 's#^#- #'
