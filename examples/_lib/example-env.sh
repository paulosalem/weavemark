# Lets example scripts be run from any working directory.
EXAMPLES_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$EXAMPLES_ROOT/.." && pwd)"
cd "$REPO_ROOT"
