#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p examples/saved-artifact-workflows/investment-brief/outputs

weavemark library builtin:catalog/standalone/investment-brief \
  --vars-file examples/saved-artifact-workflows/investment-brief/inputs/vars.json \
  --output examples/saved-artifact-workflows/investment-brief/outputs/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only
