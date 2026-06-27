#!/usr/bin/env bash
# install-hooks.sh — idempotent installer for the project's git hooks.
#
# Copies scripts/templates/* into .git/hooks/ and marks them executable.
# Re-running this script is safe — it overwrites any existing hook with
# the version from scripts/templates/.
#
# Usage:
#   bash scripts/install-hooks.sh
#   mise run hooks:install
#
# Bypass: install hooks manually by copying individual files.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TEMPLATES_DIR="$REPO_ROOT/scripts/templates"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [[ ! -d "$TEMPLATES_DIR" ]]; then
  echo "install-hooks: ERROR — $TEMPLATES_DIR does not exist" >&2
  exit 1
fi

if [[ ! -d "$HOOKS_DIR" ]]; then
  echo "install-hooks: ERROR — $HOOKS_DIR does not exist (not a git repo?)" >&2
  exit 1
fi

# Discover every file in scripts/templates/ (non-recursive; hooks are flat).
shopt -s nullglob
templates=("$TEMPLATES_DIR"/*)
shopt -u nullglob

if [[ ${#templates[@]} -eq 0 ]]; then
  echo "install-hooks: no templates found in $TEMPLATES_DIR" >&2
  exit 0
fi

installed=0
skipped=0
for src in "${templates[@]}"; do
  if [[ -d "$src" ]]; then
    continue
  fi
  name="$(basename "$src")"
  dest="$HOOKS_DIR/$name"

  # Idempotent: overwrite the destination with the source contents.
  cp "$src" "$dest"
  chmod +x "$dest"
  echo "install-hooks: installed $name"
  installed=$((installed + 1))
done

echo
echo "install-hooks: done ($installed installed, $skipped skipped)"
echo "  Hooks dir:    $HOOKS_DIR"
echo "  Templates:    $TEMPLATES_DIR"
echo
echo "  Verify:   ls -l $HOOKS_DIR"
echo "  Bypass:   git commit --no-verify"
