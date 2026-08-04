#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/examples/_lib/example-env.sh"

study="studies/runtime-studies/audience-conditioned-release-decision"
model="gpt-5.6-terra"

python "$study/study.py" prepare

weavemark "$study/promplets/treatment.weavemark.md" \
  --vars-file "$study/outputs/prepared/implementation-team.json" \
  --model "$model" \
  --output "$study/outputs/prompts/treatment-implementation-team.md" \
  --provenance "$study/outputs/provenance/treatment-implementation-team.json" \
  --batch-only \
  --verbose

weavemark "$study/promplets/treatment.weavemark.md" \
  --vars-file "$study/outputs/prepared/release-team.json" \
  --model "$model" \
  --output "$study/outputs/prompts/treatment-release-team.md" \
  --provenance "$study/outputs/provenance/treatment-release-team.json" \
  --batch-only \
  --verbose

python "$study/study.py" sanitize-provenance

printf '\nPrepared prompts:\n'
find "$study/outputs/prompts" -type f -maxdepth 1 | sort | sed 's#^#- #'
