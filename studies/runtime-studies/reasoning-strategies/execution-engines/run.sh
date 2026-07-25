#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/examples/_lib/example-env.sh"

mkdir -p \
  studies/runtime-studies/reasoning-strategies/execution-engines/outputs/tree-of-thought-solver \
  studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver \
  studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver-json

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

artifact_summary() {
  section "Artifacts written"
  find \
    studies/runtime-studies/reasoning-strategies/execution-engines/outputs/tree-of-thought-solver \
    studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver \
    studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver-json \
    -type f | sort | sed 's#^#- #'
}

# Tree of Thought: compile the prompt, then run the generate/evaluate/synthesize engine.
section "Tree of Thought: compiled prompt"
weavemark studies/runtime-studies/reasoning-strategies/promplets/tree-of-thought-solver.weavemark.md \
  --vars-file studies/runtime-studies/reasoning-strategies/execution-engines/inputs/tree-of-thought-solver-example.json \
  --output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/tree-of-thought-solver/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "Tree of Thought: generate/evaluate/synthesize execution"
weavemark studies/runtime-studies/reasoning-strategies/promplets/tree-of-thought-solver.weavemark.md \
  --vars-file studies/runtime-studies/reasoning-strategies/execution-engines/inputs/tree-of-thought-solver-example.json \
  --run \
  --output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/tree-of-thought-solver/execution-output.md \
  --show-output \
  --no-file-summary \
  --trace-output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/tree-of-thought-solver/execution-trace.md \
  --verbose

# Self-consistency: compile the prompt, then run multiple samples plus majority vote.
section "Self-consistency: compiled prompt"
weavemark studies/runtime-studies/reasoning-strategies/promplets/self-consistency-solver.weavemark.md \
  --vars-file studies/runtime-studies/reasoning-strategies/execution-engines/inputs/self-consistency-solver-example.json \
  --output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "Self-consistency: sample/vote execution"
weavemark studies/runtime-studies/reasoning-strategies/promplets/self-consistency-solver.weavemark.md \
  --vars-file studies/runtime-studies/reasoning-strategies/execution-engines/inputs/self-consistency-solver-example.json \
  --run \
  --output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver/execution-output.md \
  --show-output \
  --no-file-summary \
  --trace-output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver/execution-trace.md \
  --verbose

# JSON pipeline: same engine shape, but saved as machine-readable JSON.
section "JSON pipeline: compiled prompt"
weavemark studies/runtime-studies/reasoning-strategies/promplets/self-consistency-solver.weavemark.md \
  --vars-file studies/runtime-studies/reasoning-strategies/execution-engines/inputs/self-consistency-solver-example.json \
  --format json \
  --output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver-json/compiled-prompt.json \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "JSON pipeline: execution output"
weavemark studies/runtime-studies/reasoning-strategies/promplets/self-consistency-solver.weavemark.md \
  --vars-file studies/runtime-studies/reasoning-strategies/execution-engines/inputs/self-consistency-solver-example.json \
  --run \
  --format json \
  --output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver-json/execution-output.json \
  --show-output \
  --no-file-summary \
  --trace-output studies/runtime-studies/reasoning-strategies/execution-engines/outputs/self-consistency-solver-json/execution-trace.md \
  --verbose

artifact_summary
