#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="examples/python-runtime-integrations/financial-independence-goal-plan/outputs/interactive/$RUN_ID"

python examples/python-runtime-integrations/financial-independence-goal-plan/run.py \
  --vars examples/python-runtime-integrations/financial-independence-goal-plan/inputs/interactive-defaults.json \
  --output-dir "$OUTPUT_DIR" \
  --guided-inputs
