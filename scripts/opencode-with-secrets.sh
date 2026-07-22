#!/usr/bin/env bash
# scripts/opencode-with-secrets.sh
#
# Canonical agent-runtime launcher for this repo. Wraps OpenCode with the
# Infisical/Locket secrets layer so MCP servers (Firecrawl, Hugging Face,
# MotherDuck, etc.) inherit the right env vars at runtime.
#
# USAGE:  ./scripts/opencode-with-secrets.sh [opencode args...]
#
# This replaces scripts/claude-with-secrets.sh (retired 2026-07-21, see
# openspec/changes/2026-07-21-purge-claude-coauthor-trailer). Claude Code is
# NOT an approved runtime for this repo — see
# openspec/specs/agent-runtime-and-attribution/spec.md.

set -euo pipefail

cd "$(dirname "$0")/.." || exit 1

# Fail fast with a helpful message if mise is not on PATH.
if ! command -v mise >/dev/null 2>&1; then
  echo "Error: mise is not on PATH. Install: https://mise.jdx.dev" >&2
  exit 1
fi

# Use the repo's pinned mise tasks. `locket:exec` injects the Locket secret
# sidecar's env into the inner command; mise ensures the right OpenCode binary
# (managed via mise) is the one actually invoked.
exec mise run locket:exec -- opencode "$@"
