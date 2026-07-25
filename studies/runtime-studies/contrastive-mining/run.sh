#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/examples/_lib/example-env.sh"

mkdir -p studies/runtime-studies/contrastive-mining/outputs

printf '\n%s\n\n' "Contrastive mining: compiled prompt"
weavemark studies/runtime-studies/contrastive-mining/promplets/contrastive-mining.weavemark.md \
  --vars-file studies/runtime-studies/contrastive-mining/inputs/vars.json \
  --model gpt-5.5 \
  --output studies/runtime-studies/contrastive-mining/outputs/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

printf '\n%s\n\n' "Contrastive mining: reflection execution"
weavemark studies/runtime-studies/contrastive-mining/promplets/contrastive-mining.weavemark.md \
  --vars-file studies/runtime-studies/contrastive-mining/inputs/vars.json \
  --model gpt-5.5 \
  --run \
  --output studies/runtime-studies/contrastive-mining/outputs/execution-output.md \
  --show-output \
  --no-file-summary \
  --trace-output studies/runtime-studies/contrastive-mining/outputs/execution-trace.md \
  --verbose

printf '\n%s\n\n' "Artifacts written"
find studies/runtime-studies/contrastive-mining/outputs \
  -type f | sort | sed 's#^#- #'
