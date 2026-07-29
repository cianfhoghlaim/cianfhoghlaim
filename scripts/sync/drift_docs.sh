#!/usr/bin/env bash
# Layer 7: AGENTS.md drift detection.
# Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
# (the `centralize-cross-cutting-docs` spec).
#
# Validates every AGENTS.md number claim (specs/skills/stacks/models/notebooks)
# against ground truth. Writes JSON + Markdown reports to
# stedding/sync-reports/docs-drift-{date}.{json,md}.
#
# Usage:
#   bash scripts/sync/drift_docs.sh              # CI mode (exit 1 on drift)
#   bash scripts/sync/drift_docs.sh --dry-run    # exit 0 always

set -uo pipefail
mkdir -p stedding/sync-reports
DRY_RUN="${1:-}"

.venv/bin/python3 scripts/lint_drift_docs.py $DRY_RUN
exit $?
