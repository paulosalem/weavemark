#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p examples/benchmark-runners/strategy-comparison/outputs
export HF_DATASETS_VERBOSITY=error
export HF_HUB_DISABLE_PROGRESS_BARS=1
export TQDM_DISABLE=1

# Compare WeaveMark reasoning strategies on a tiny GSM8K smoke slice.
python examples/benchmark-runners/strategy-comparison/runner.py \
  --specs \
    promplets/stdlib/fragments/reasoning/chain-of-thought.weavemark.md \
    promplets/catalog/executable/self-consistency-solver.weavemark.md \
    promplets/catalog/executable/simplified-tree-of-thought-solver.weavemark.md \
    promplets/catalog/executable/reflection-solver.weavemark.md \
  --tasks gsm8k \
  --model gpt-5.5 \
  --limit 2 \
  --parallel 2 \
  --output examples/benchmark-runners/strategy-comparison/outputs/benchmark-results.json
