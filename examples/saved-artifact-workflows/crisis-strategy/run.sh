#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p examples/saved-artifact-workflows/crisis-strategy/outputs

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

# A tool-enabled strategic analysis prompt using the Google AI-threat scenario.
section "Crisis strategy: compiled prompt"
weavemark library builtin:catalog/executable/crisis-strategy-analyzer \
  --vars-file examples/saved-artifact-workflows/crisis-strategy/inputs/vars.json \
  --output examples/saved-artifact-workflows/crisis-strategy/outputs/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "Crisis strategy: execution"
weavemark library builtin:catalog/executable/crisis-strategy-analyzer \
  --vars-file examples/saved-artifact-workflows/crisis-strategy/inputs/vars.json \
  --run --verbose \
  --show-output \
  --no-file-summary \
  --output examples/saved-artifact-workflows/crisis-strategy/outputs/execution-output.md

section "Artifacts written"
find examples/saved-artifact-workflows/crisis-strategy/outputs -type f | sort | sed 's#^#- #'
