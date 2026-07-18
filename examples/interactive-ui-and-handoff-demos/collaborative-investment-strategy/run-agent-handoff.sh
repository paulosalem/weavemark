#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

# Run the collaborative examples with AI-agent-authored human/editor turns.
python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py --agent-collaborator

python examples/interactive-ui-and-handoff-demos/collaborative-investment-strategy/run.py \
  --spec promplets/catalog/executable/collaborative-writer.weavemark.md \
  --vars examples/interactive-ui-and-handoff-demos/collaborative-writer/inputs/vars.json \
  --output-dir examples/interactive-ui-and-handoff-demos/collaborative-writer/outputs \
  --agent-collaborator
