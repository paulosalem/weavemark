#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="examples/saved-artifact-workflows/recurring-topic-monitor/outputs/interactive/$RUN_ID"

mkdir -p "$OUTPUT_DIR"

weavemark library builtin:catalog/executable/recurring-topic-monitor \
  --vars-file examples/saved-artifact-workflows/recurring-topic-monitor/inputs/interactive-defaults.json \
  --var "run_date=$(date +%F)" \
  --run \
  --no-protections \
  --output "$OUTPUT_DIR/execution-output.md" \
  --trace-output "$OUTPUT_DIR/execution-trace.md" \
  --show-output \
  --no-file-summary \
  --verbose

printf '\nPersonalized artifacts: %s\n' "$OUTPUT_DIR"
