#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

weavemark library builtin:catalog/standalone/messy-notes-action-plan \
  --vars-file examples/terminal-output-only/messy-notes-action-plan/inputs/vars.json \
  --verbose \
  --batch-only
