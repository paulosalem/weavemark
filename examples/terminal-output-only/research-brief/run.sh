#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

weavemark library builtin:catalog/standalone/research-brief \
  --vars-file examples/terminal-output-only/research-brief/inputs/vars.json \
  --verbose \
  --batch-only
