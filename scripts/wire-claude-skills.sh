#!/usr/bin/env bash
# scripts/wire-claude-skills.sh — symlink the curated .agents/skills/ subset
# into .claude/skills/ so Claude Code can discover this project's own
# technology skills (it does not read .agents/skills/ on its own).
#
# .claude/ is gitignored (per-developer dlthub-init artifact, regenerated
# on fresh clone — see .gitignore's comment above the /.claude/ rule), so
# this wiring has to be re-run per clone rather than committed directly.
# Idempotent — safe to re-run after `uvx dlthub-init@latest` or any other
# .claude/ regeneration step.
#
# Usage: bash scripts/wire-claude-skills.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SKILLS=(
  pangolin komodo ducklake lancedb iceberg-lakekeeper litellm motherduck
  dagster dlt marimo cocoindex secrets-management garage graphiti
  graphiti-core cognee ccc centralized-registry browser-tools
  agent-observability agent-memory-systems agent-fleet-orchestration baml
  duckdb falkordb memgraph langfuse ragas google-adk agno dignified-python
  hono tanstack-start ibis mlflow cloudflare better-auth convex firecrawl
)

mkdir -p .claude/skills
if [ ! -e .claude/skills/README.md ]; then
  ln -s ../../.agents/skills/README-claude-skills.md .claude/skills/README.md
fi

linked=0
skipped=0
for s in "${SKILLS[@]}"; do
  if [ -e ".claude/skills/$s" ]; then
    skipped=$((skipped + 1))
    continue
  fi
  if [ ! -d ".agents/skills/$s" ]; then
    echo "warning: .agents/skills/$s not found, skipping" >&2
    continue
  fi
  ln -s "../../.agents/skills/$s" ".claude/skills/$s"
  linked=$((linked + 1))
done

echo "linked $linked skills, $skipped already present"
echo "see .agents/skills/README-claude-skills.md (also linked at .claude/skills/README.md) for the curation rationale and how to add more"
