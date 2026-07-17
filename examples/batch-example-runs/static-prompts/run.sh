#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

mkdir -p \
  examples/batch-example-runs/static-prompts/outputs/market-research-brief \
  examples/batch-example-runs/static-prompts/outputs/tutorial-generator \
  examples/batch-example-runs/static-prompts/outputs/consulting-proposal \
  examples/batch-example-runs/static-prompts/outputs/knowledge-base-article \
  examples/batch-example-runs/static-prompts/outputs/adaptive-interview \
  examples/batch-example-runs/static-prompts/outputs/multi-persona-debate \
  examples/batch-example-runs/static-prompts/outputs/prompt-refactoring-pipeline \
  examples/batch-example-runs/static-prompts/outputs/support-ticket-prompt-pack \
  examples/batch-example-runs/static-prompts/outputs/creative-ideation-scamper \
  examples/batch-example-runs/static-prompts/outputs/creative-ideation-six-hats \
  examples/batch-example-runs/static-prompts/outputs/creative-ideation-reverse

section() {
  printf '\n\n%s\n' "================================================================================"
  printf '%s\n' "$1"
  printf '%s\n\n' "================================================================================"
}

artifact_summary() {
  section "Artifacts written"
  find \
    examples/batch-example-runs/static-prompts/outputs/market-research-brief \
    examples/batch-example-runs/static-prompts/outputs/tutorial-generator \
    examples/batch-example-runs/static-prompts/outputs/consulting-proposal \
    examples/batch-example-runs/static-prompts/outputs/knowledge-base-article \
    examples/batch-example-runs/static-prompts/outputs/adaptive-interview \
    examples/batch-example-runs/static-prompts/outputs/multi-persona-debate \
    examples/batch-example-runs/static-prompts/outputs/prompt-refactoring-pipeline \
    examples/batch-example-runs/static-prompts/outputs/support-ticket-prompt-pack \
    examples/batch-example-runs/static-prompts/outputs/creative-ideation-scamper \
    examples/batch-example-runs/static-prompts/outputs/creative-ideation-six-hats \
    examples/batch-example-runs/static-prompts/outputs/creative-ideation-reverse \
    -type f | sort | sed 's#^#- #'
}

# 1. Basic semantic composition: @refine, @match, @if, and variables.
section "1. Basic semantic composition: @refine, @match, @if, and variables"
weavemark library builtin:catalog/standalone/market-research-brief \
  --vars-file examples/batch-example-runs/static-prompts/inputs/market-research-example.json \
  --output examples/batch-example-runs/static-prompts/outputs/market-research-brief/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 2. Escaping literal @ symbols with @@.
section "2. Escaping literal @ symbols with @@"
weavemark library builtin:catalog/standalone/tutorial-generator \
  --vars-file examples/batch-example-runs/static-prompts/inputs/tutorial-fastapi.json \
  --output examples/batch-example-runs/static-prompts/outputs/tutorial-generator/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 3. Nested directives: @summarize inside a selected @match branch.
section "3. Nested directives: @summarize inside a selected @match branch"
weavemark library builtin:catalog/standalone/consulting-proposal \
  --vars-file examples/batch-example-runs/static-prompts/inputs/consulting-proposal-example.json \
  --output examples/batch-example-runs/static-prompts/outputs/consulting-proposal/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 4. Content pipeline: @extract -> @summarize -> @compress.
section "4. Content pipeline: @extract -> @summarize -> @compress"
weavemark library builtin:catalog/standalone/knowledge-base-article \
  --vars-file examples/batch-example-runs/static-prompts/inputs/knowledge-base-article-example.json \
  --output examples/batch-example-runs/static-prompts/outputs/knowledge-base-article/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 5. Deep nesting: @match -> @match -> @if -> @compress.
section "5. Deep nesting: @match -> @match -> @if -> @compress"
weavemark library builtin:catalog/standalone/adaptive-interview \
  --vars-file examples/batch-example-runs/static-prompts/inputs/adaptive-interview-senior-backend.json \
  --output examples/batch-example-runs/static-prompts/outputs/adaptive-interview/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 6. Prompt growth and repair with @expand and @revise.
section "6. Prompt growth and repair with @expand and @revise"
weavemark library builtin:catalog/standalone/multi-persona-debate \
  --vars-file examples/batch-example-runs/static-prompts/inputs/multi-persona-debate-agi.json \
  --output examples/batch-example-runs/static-prompts/outputs/multi-persona-debate/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 7. Prompt refactoring as a semantic program transformation.
section "7. Prompt refactoring as a semantic program transformation"
weavemark library builtin:catalog/standalone/prompt-refactoring-pipeline \
  --vars-file examples/batch-example-runs/static-prompts/inputs/prompt-refactoring-example.json \
  --output examples/batch-example-runs/static-prompts/outputs/prompt-refactoring-pipeline/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 8. Multi-file prompt packs with @emit.
section "8. Multi-file prompt pack with @emit"
weavemark library builtin:catalog/standalone/support-ticket-prompt-pack \
  --vars-file examples/batch-example-runs/static-prompts/inputs/support-ticket-prompt-pack-example.json \
  --output examples/batch-example-runs/static-prompts/outputs/support-ticket-prompt-pack/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

# 9. Semantic @refine mingling: one ideation spec, three reusable methods.
section "9a. Semantic @refine mingling: SCAMPER"
weavemark library builtin:catalog/standalone/creative-ideation \
  --vars-file examples/batch-example-runs/static-prompts/inputs/creative-ideation-scamper.json \
  --output examples/batch-example-runs/static-prompts/outputs/creative-ideation-scamper/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

section "9b. Semantic @refine mingling: Six Thinking Hats"
weavemark library builtin:catalog/standalone/creative-ideation \
  --vars-file examples/batch-example-runs/static-prompts/inputs/creative-ideation-six-hats.json \
  --output examples/batch-example-runs/static-prompts/outputs/creative-ideation-six-hats/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

section "9c. Semantic @refine mingling: Reverse Brainstorming"
weavemark library builtin:catalog/standalone/creative-ideation \
  --vars-file examples/batch-example-runs/static-prompts/inputs/creative-ideation-reverse.json \
  --output examples/batch-example-runs/static-prompts/outputs/creative-ideation-reverse/compiled-prompt.md \
  --show-output \
  --no-file-summary \
  --batch-only --verbose

artifact_summary
