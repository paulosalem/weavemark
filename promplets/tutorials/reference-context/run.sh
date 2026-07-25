#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/examples/_lib/example-env.sh"

weavemark promplets/tutorials/reference-context/reference-aware-release-note.weavemark.md \
  --verbose \
  --batch-only
