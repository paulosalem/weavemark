#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

# Open the collaborative investment-strategy prompt in the interactive TUI.
weavemark library builtin:catalog/executable/collaborative-investment-strategy \
  --ui \
  --verbose \
  --vars-file examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/inputs/vars.json
