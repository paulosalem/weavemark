#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

# Open a final prompt spec in the interactive TUI with example variables loaded.
weavemark library builtin:catalog/standalone/program-review-checklist \
  --ui \
  --verbose \
  --vars-file examples/interactive-ui-and-handoff-demos/prompt-tui/inputs/vars.json
