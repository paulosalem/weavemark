#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

# Run the collaborative writer example with AI-agent-authored editor turns.
python examples/interactive-ui-and-handoff-demos/collaborative-writer/run.py \
  --agent-collaborator
