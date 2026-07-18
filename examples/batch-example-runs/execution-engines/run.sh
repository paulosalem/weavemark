#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p \
  examples/batch-example-runs/execution-engines/outputs/tree-of-thought-solver \
  examples/batch-example-runs/execution-engines/outputs/self-consistency-solver \
  examples/batch-example-runs/execution-engines/outputs/reflection-writer \
  examples/batch-example-runs/execution-engines/outputs/self-consistency-solver-json \
  examples/batch-example-runs/execution-engines/outputs/recurring-topic-monitor-ai-news

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

artifact_summary() {
  section "Artifacts written"
  find \
    examples/batch-example-runs/execution-engines/outputs/tree-of-thought-solver \
    examples/batch-example-runs/execution-engines/outputs/self-consistency-solver \
    examples/batch-example-runs/execution-engines/outputs/reflection-writer \
    examples/batch-example-runs/execution-engines/outputs/self-consistency-solver-json \
    examples/batch-example-runs/execution-engines/outputs/recurring-topic-monitor-ai-news \
    -type f | sort | sed 's#^#- #'
}

# Tree of Thought: compile the prompt, then run the generate/evaluate/synthesize engine.
section "Tree of Thought: compiled prompt"
weavemark library builtin:catalog/executable/tree-of-thought-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/tree-of-thought-solver-example.json \
  --output examples/batch-example-runs/execution-engines/outputs/tree-of-thought-solver/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "Tree of Thought: generate/evaluate/synthesize execution"
weavemark library builtin:catalog/executable/tree-of-thought-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/tree-of-thought-solver-example.json \
  --run \
  --output examples/batch-example-runs/execution-engines/outputs/tree-of-thought-solver/execution-output.md \
  --show-output \
  --no-file-summary \
  --trace-output examples/batch-example-runs/execution-engines/outputs/tree-of-thought-solver/execution-trace.md \
  --verbose

# Self-consistency: compile the prompt, then run multiple samples plus majority vote.
section "Self-consistency: compiled prompt"
weavemark library builtin:catalog/executable/self-consistency-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/self-consistency-solver-example.json \
  --output examples/batch-example-runs/execution-engines/outputs/self-consistency-solver/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "Self-consistency: sample/vote execution"
weavemark library builtin:catalog/executable/self-consistency-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/self-consistency-solver-example.json \
  --run \
  --output examples/batch-example-runs/execution-engines/outputs/self-consistency-solver/execution-output.md \
  --show-output \
  --no-file-summary \
  --trace-output examples/batch-example-runs/execution-engines/outputs/self-consistency-solver/execution-trace.md \
  --verbose

# Reflection: compile the prompt, then run generate/critique/revise iterations.
section "Reflection: compiled prompt"
weavemark library builtin:catalog/executable/reflection-writer \
  --vars-file examples/batch-example-runs/execution-engines/inputs/reflection-writer-example.json \
  --output examples/batch-example-runs/execution-engines/outputs/reflection-writer/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "Reflection: generate/critique/revise execution"
weavemark library builtin:catalog/executable/reflection-writer \
  --vars-file examples/batch-example-runs/execution-engines/inputs/reflection-writer-example.json \
  --run \
  --output examples/batch-example-runs/execution-engines/outputs/reflection-writer/execution-output.md \
  --show-output \
  --no-file-summary \
  --trace-output examples/batch-example-runs/execution-engines/outputs/reflection-writer/execution-trace.md \
  --verbose

# JSON pipeline: same engine shape, but saved as machine-readable JSON.
section "JSON pipeline: compiled prompt"
weavemark library builtin:catalog/executable/self-consistency-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/self-consistency-solver-example.json \
  --format json \
  --output examples/batch-example-runs/execution-engines/outputs/self-consistency-solver-json/compiled-prompt.json \
  --show-output \
  --no-file-summary \
  --verbose \
  --batch-only

section "JSON pipeline: execution output"
weavemark library builtin:catalog/executable/self-consistency-solver \
  --vars-file examples/batch-example-runs/execution-engines/inputs/self-consistency-solver-example.json \
  --run \
  --format json \
  --output examples/batch-example-runs/execution-engines/outputs/self-consistency-solver-json/execution-output.json \
  --show-output \
  --no-file-summary \
  --trace-output examples/batch-example-runs/execution-engines/outputs/self-consistency-solver-json/execution-trace.md \
  --verbose

# Bound tools: the regular CLI runs a model-directed search/crawl loop.
# This automated runner disables prompts only for this trusted checked-in promplet.
section "Recurring topic monitor: native bound-tool execution"
weavemark library builtin:catalog/executable/recurring-topic-monitor \
  --vars-file examples/batch-example-runs/execution-engines/inputs/recurring-topic-monitor-ai-news.json \
  --run \
  --no-protections \
  --output examples/batch-example-runs/execution-engines/outputs/recurring-topic-monitor-ai-news/execution-output.md \
  --no-file-summary \
  --trace-output examples/batch-example-runs/execution-engines/outputs/recurring-topic-monitor-ai-news/execution-trace.md \
  --verbose

artifact_summary
