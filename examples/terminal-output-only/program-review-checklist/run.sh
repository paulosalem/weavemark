#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

# A plain, realistic single-spec run: no saved files, wrappers, or demo summary.
weavemark library builtin:catalog/standalone/program-review-checklist \
  --vars-file examples/terminal-output-only/program-review-checklist/inputs/vars.json \
  --verbose \
  --batch-only
