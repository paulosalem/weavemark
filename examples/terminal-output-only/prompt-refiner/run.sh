#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

weavemark library builtin:catalog/standalone/prompt-refiner \
  --vars-file examples/terminal-output-only/prompt-refiner/inputs/vars.json \
  --verbose \
  --batch-only
