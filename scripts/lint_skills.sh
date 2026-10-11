#!/usr/bin/env bash
# scripts/lint_skills.sh — frontmatter conformance check for .agents/skills/*/SKILL.md
#
# Per the 2026-10-30-housekeeping-sprawl-cleanup-v1 umbrella of
# openspec/plans/2026-10-30-platform-reset-saga-v1.md. Promoted from the
# historical `_tmp_lint.sh` (now removed in this change).
# historical `_tmp_lint.sh` (now removed).
#
# Rules enforced (per the canonical _template/SKILL.md):
#   1. Every SKILL.md must have YAML frontmatter delimited by `---` lines.
#   2. The `name:` field must match the directory name.
#   3. The `description:` field must be ≥ 40 characters.
#
# Optional (not enforced here, the v1.11 skill frontmatter is loose):
#   - `location:` field (added by the media-intel change to match the
#     cianfhoghlaim skill catalog convention).
#
# Usage:
#   bash scripts/lint_skills.sh                       # check all 80 skills
#   bash scripts/lint_skills.sh --limit 5            # check the first 5
#   bash scripts/lint_skills.sh --strict             # fail on warnings too
#
# CI: wired as `mise run core:lint:skills` (added 2026-10-30).

set -euo pipefail

LIMIT=999999
STRICT=0
for arg in "$@"; do
  case "$arg" in
    --limit) shift; LIMIT="${1:-5}" ;;
    --limit=*) LIMIT="${arg#--limit=}" ;;
    --strict) STRICT=1 ;;
    --help|-h)
    sed -n '2,20p' "$0"
    exit 0
    ;;
      sed -n '2,20p' "$0"
      exit 0
      ;;
  esac
done

count=0
failures=0
warnings=0
for d in .agents/skills/*/; do
  skill_path="${d%/}"
  skill_name="${skill_path##*/}"

  case "$skill_name" in
    _*|.*) continue ;;  # skip _archive / .DS_Store / etc.
  esac

  if [ ! -f "$skill_path/SKILL.md" ]; then
    continue
  fi

  count=$((count + 1))
  if [ "$count" -gt "$LIMIT" ]; then
    break
  fi

  if ! python3 - "$skill_path" "$skill_name" << 'PYEOF'
import sys

skill_path, skill_name = sys.argv[1], sys.argv[2]
errors: list[str] = []
warnings: list[str] = []

with open(f"{skill_path}/SKILL.md") as f:
    content = f.read()

# Rule 1: YAML frontmatter exists
if not content.startswith("---"):
    print(f"ERROR  {skill_name}: no YAML frontmatter (rule 1)")
    sys.exit(1)

end = content.find("\n---\n", 3)
if end == -1:
    print(f"ERROR  {skill_name}: unterminated YAML frontmatter (rule 1)")
    sys.exit(1)

fm = content[3:end]

# Rule 2: name: matches dir
import re

m_name = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
if not m_name:
    print(f"ERROR  {skill_name}: no `name:` in frontmatter (rule 2)")
    sys.exit(1)
declared_name = m_name.group(1)
if declared_name != skill_name:
    print(f"ERROR  {skill_name}: name='{declared_name}' but dir is '{skill_name}' (rule 2)")
    sys.exit(1)

# Rule 3: description: is ≥ 40 chars
m_desc = re.search(
    r"^description:\s*(?:\|\s*\n((?:[ \t]+[^\n]*\n)+)|(.*?))(?=\n[a-zA-Z_-]|\n---|\Z)",
    fm,
    re.MULTILINE | re.DOTALL,
)
if not m_desc:
    print(f"ERROR  {skill_name}: no `description:` in frontmatter (rule 3)")
    sys.exit(1)
desc = (m_desc.group(1) or m_desc.group(2) or "").strip()
if len(desc) < 40:
    print(f"ERROR  {skill_name}: description is {len(desc)} chars (< 40) (rule 3)")
    sys.exit(1)

# Optional (warning, not error): location: field
m_loc = re.search(r"^location:\s*(\S+)", fm, re.MULTILINE)
if not m_loc:
    warnings.append(f"WARN   {skill_name}: no `location:` field (optional)")

print(f"OK     {skill_name} {len(desc)} chars")
if warnings:
    for w in warnings:
        print(w)
PYEOF
  then
    failures=$((failures + 1))
  fi
done

echo "DONE: checked=$count failures=$failures"
if [ "$failures" -gt 0 ]; then
  exit 1
fi
if [ "$STRICT" = "1" ]; then
  if [ "$warnings" -gt 0 ]; then
    echo "STRICT MODE: $warnings warnings present (see above)"
    exit 1
  fi
fi
