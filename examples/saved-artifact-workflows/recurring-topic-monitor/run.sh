#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

VARS_FILE="${1:-examples/saved-artifact-workflows/recurring-topic-monitor/inputs/ai-news.json}"
RUN_NAME="$(basename "$VARS_FILE" .json)"
OUTPUT_DIR="examples/saved-artifact-workflows/recurring-topic-monitor/outputs/$RUN_NAME"

mkdir -p "$OUTPUT_DIR"

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

section "Recurring topic monitor: native bound-tool execution"
printf 'Vars file: %s\n' "$VARS_FILE"
printf 'Output dir: %s\n\n' "$OUTPUT_DIR"

# This checked-in example imports the promplet's declared Python bindings.
weavemark library builtin:catalog/executable/recurring-topic-monitor \
  --vars-file "$VARS_FILE" \
  --run \
  --no-protections \
  --output "$OUTPUT_DIR/execution-output.md" \
  --show-output \
  --no-file-summary \
  --trace-output "$OUTPUT_DIR/execution-trace.md" \
  --verbose \
  --batch-only

section "Artifacts written"
find "$OUTPUT_DIR" -type f | sort | sed 's#^#- #'
