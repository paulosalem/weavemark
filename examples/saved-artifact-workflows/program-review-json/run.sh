#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p examples/saved-artifact-workflows/program-review-json/outputs

printf '\n%s\n' "================================================================================"
printf '%s\n' "Machine-readable JSON output for downstream automation"
printf '%s\n\n' "================================================================================"

weavemark library builtin:catalog/standalone/program-review-checklist \
  --vars-file examples/saved-artifact-workflows/program-review-json/inputs/vars.json \
  --format json \
  --output examples/saved-artifact-workflows/program-review-json/outputs/compiled-prompt.json \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

printf '\n%s\n' "================================================================================"
printf '%s\n' "Artifacts written"
printf '%s\n\n' "================================================================================"
find examples/saved-artifact-workflows/program-review-json/outputs -type f | sort | sed 's#^#- #'
