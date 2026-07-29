#!/usr/bin/env bash
# Layer 8: per-spec AGENTS.md generator.
# Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
# (the `repo-hygiene-agent-routing` spec).
#
# Walks `openspec/specs/`, reads each `spec.md` first line, emits a
# sibling `AGENTS.md` per spec (if missing or older than `spec.md`).
# Idempotent: re-running never breaks existing files.
#
# Usage:
#   bash scripts/sync/spec_agents.sh              # idempotent
#   bash scripts/sync/spec_agents.sh --dry-run    # print what would be emitted
#   bash scripts/sync/spec_agents.sh --force      # overwrite even if AGENTS.md is newer

set -uo pipefail
.venv/bin/python3 scripts/sync/spec_agents.py "$@"
exit $?
