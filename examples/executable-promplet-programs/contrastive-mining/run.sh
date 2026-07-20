#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p examples/executable-promplet-programs/contrastive-mining/outputs

printf '\n%s\n\n' "Contrastive mining: compiled prompt"
weavemark library builtin:catalog/executable/contrastive-mining \
  --vars-file examples/executable-promplet-programs/contrastive-mining/inputs/vars.json \
  --model gpt-5.5 \
  --output examples/executable-promplet-programs/contrastive-mining/outputs/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

printf '\n%s\n\n' "Contrastive mining: reflection execution"
weavemark library builtin:catalog/executable/contrastive-mining \
  --vars-file examples/executable-promplet-programs/contrastive-mining/inputs/vars.json \
  --model gpt-5.5 \
  --run \
  --output examples/executable-promplet-programs/contrastive-mining/outputs/execution-output.md \
  --show-output \
  --no-file-summary \
  --trace-output examples/executable-promplet-programs/contrastive-mining/outputs/execution-trace.md \
  --verbose

printf '\n%s\n\n' "Artifacts written"
find examples/executable-promplet-programs/contrastive-mining/outputs \
  -type f | sort | sed 's#^#- #'
