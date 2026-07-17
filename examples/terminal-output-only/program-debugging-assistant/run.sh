#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

weavemark library builtin:catalog/standalone/program-debugging-assistant \
  --vars-file examples/terminal-output-only/program-debugging-assistant/inputs/vars.json \
  --verbose \
  --batch-only
