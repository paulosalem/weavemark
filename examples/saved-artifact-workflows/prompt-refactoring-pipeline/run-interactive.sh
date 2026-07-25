#!/usr/bin/env bash
set -euo pipefail

PROMPT_FILE="${1:-}"
if [[ -z "$PROMPT_FILE" ]]; then
  printf 'Usage: %s PATH_TO_PROMPT\n' "${0##*/}" >&2
  exit 2
fi
if [[ "$PROMPT_FILE" != /* ]]; then
  PROMPT_FILE="$PWD/$PROMPT_FILE"
fi
if [[ ! -s "$PROMPT_FILE" ]]; then
  printf 'Prompt file is missing or empty: %s\n' "$PROMPT_FILE" >&2
  exit 2
fi

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="examples/saved-artifact-workflows/prompt-refactoring-pipeline/outputs/interactive/$RUN_ID"

mkdir -p "$OUTPUT_DIR"

weavemark library builtin:catalog/standalone/prompt-refactoring-pipeline \
  --vars-file examples/saved-artifact-workflows/prompt-refactoring-pipeline/inputs/interactive-defaults.yaml \
  --var "raw_prompt=$(<"$PROMPT_FILE")" \
  --output "$OUTPUT_DIR/compiled-prompt.md" \
  --show-output \
  --verbose

printf '\nPersonalized artifact: %s/compiled-prompt.md\n' "$OUTPUT_DIR"
