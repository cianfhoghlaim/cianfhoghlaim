#!/usr/bin/env bash
# Layer 4: validate 57 agent skills
# Per the 2026-08-15-knowledge-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/skills-$(date +%Y-%m-%d).md"
{
  echo "# Skills Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Frontmatter Lint (canonical 53+ pass)"
  echo '```'
  bash .agents/skills/lint-skills.sh
  echo '```'
  echo ""
  echo "## Path Reference Validation"
  echo '```'
  uv run python scripts/validate_skill_references.py
  echo '```'
  echo ""
  echo "## Stale Skills (>90 days since last update)"
  stale=$(find .agents/skills -name 'SKILL.md' -mtime +90 2>/dev/null | wc -l | tr -d ' ')
  total=$(find .agents/skills -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
  echo "- Stale: $stale / $total skills (>90 days)"
} > "$REPORT"
cat "$REPORT"
