#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/_lib/example-env.sh"

weavemark examples/terminal-output-only/reference-context/promplets/reference-aware-release-note.weavemark.md \
  --verbose \
  --batch-only
