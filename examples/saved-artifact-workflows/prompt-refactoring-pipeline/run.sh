#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p examples/saved-artifact-workflows/prompt-refactoring-pipeline/outputs

weavemark library builtin:catalog/standalone/prompt-refactoring-pipeline \
  --vars-file examples/saved-artifact-workflows/prompt-refactoring-pipeline/inputs/vars.yaml \
  --output examples/saved-artifact-workflows/prompt-refactoring-pipeline/outputs/compiled-prompt.md \
  --show-output \
  --verbose \
  --batch-only
