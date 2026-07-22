#!/usr/bin/env bash
# scripts/install-hooks.sh
#
# Point git at the in-repo `.githooks/` directory. Idempotent.
# Run once after cloning or after merging the hooks into a new branch.

set -euo pipefail

cd "$(dirname "$0")/.." || exit 1

# Make all hooks executable.
chmod +x .githooks/* 2>/dev/null || true

# Tell git to use them.
git config core.hooksPath .githooks

echo "✔ git hooks installed (core.hooksPath = .githooks)" >&2
echo "  active hooks:" >&2
for hook in .githooks/*; do
  [[ -f "$hook" && -x "$hook" ]] && echo "    - $(basename "$hook")" >&2
done
