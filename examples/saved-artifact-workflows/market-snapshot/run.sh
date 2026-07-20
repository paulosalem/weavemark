#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

VARS_FILE="examples/saved-artifact-workflows/market-snapshot/inputs/vars.json"
OUTPUT_DIR="examples/saved-artifact-workflows/market-snapshot/outputs"

mkdir -p "$OUTPUT_DIR"

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

section "VALE3 market snapshot: research to HTML dashboard"
printf 'Vars file: %s\n' "$VARS_FILE"
printf 'Output dir: %s\n\n' "$OUTPUT_DIR"

# The market snapshot is a promplet; the Python runner is only a richer
# integration transcript for people studying companion APIs directly.
weavemark promplets/catalog/executable/market-snapshot.weavemark.md \
  --vars-file "$VARS_FILE" \
  --run \
  --no-protections \
  --output "$OUTPUT_DIR/execution-output.md" \
  --show-output \
  --no-file-summary \
  --trace-output "$OUTPUT_DIR/execution-trace.md" \
  --verbose \
  --batch-only \
  --open

section "Artifacts written"
find "$OUTPUT_DIR" -type f | sort | sed 's#^#- #'
