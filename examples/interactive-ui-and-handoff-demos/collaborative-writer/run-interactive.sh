#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="examples/interactive-ui-and-handoff-demos/collaborative-writer/outputs/interactive/$RUN_ID"

python examples/interactive-ui-and-handoff-demos/collaborative-writer/run.py \
  --vars examples/interactive-ui-and-handoff-demos/collaborative-writer/inputs/interactive-defaults.json \
  --output-dir "$OUTPUT_DIR" \
  --guided-inputs
