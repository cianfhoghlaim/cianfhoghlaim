#!/usr/bin/env bash
set -euo pipefail

# Limit to first 5 skills
count=0
for d in .agents/skills/*/; do
  skill_path="${d%/}"
  skill_name="${skill_path##*/}"

  case "$skill_name" in
    _*|.*) continue ;;
  esac

  if [ ! -f "$skill_path/SKILL.md" ]; then
    continue
  fi

  count=$((count + 1))
  if [ $count -gt 6 ]; then
    break
  fi

  echo "=== $count: $skill_name ===" >&2

  if ! python3 - "$skill_path" "$skill_name" << 'PYEOF'
import sys, re

skill_path, skill_name = sys.argv[1], sys.argv[2]
errors = []

with open(f"{skill_path}/SKILL.md") as f:
    content = f.read()

m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
if not m:
    print(f"ERROR: {skill_name} has no YAML frontmatter (rule 1)"); sys.exit(1)

fm = m.group(1)

m_name = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
if not m_name:
    print(f"ERROR: {skill_name} has no name: in frontmatter (rule 2)")
    sys.exit(1)
declared_name = m_name.group(1)
if declared_name != skill_name:
    print(f"ERROR: {skill_name} has name='{declared_name}' but directory is '{skill_name}' (rule 2)")
    sys.exit(1)

m_desc = re.search(
    r"^description:\s*(?:\|\s*\n((?:[ \t]+[^\n]*\n)+)|(.*?))(?=\n[a-zA-Z_-]|\n---|\Z)",
    fm,
    re.MULTILINE | re.DOTALL,
)
if not m_desc:
    print(f"ERROR: {skill_name} has no description: in frontmatter (rule 3)")
    sys.exit(1)

desc = (m_desc.group(1) or m_desc.group(2) or "").strip()
if len(desc) < 40:
    print(f"ERROR: {skill_name} has description with {len(desc)} chars (< 40) (rule 3)")
    sys.exit(1)
print(f"  OK {skill_name} {len(desc)}")
PYEOF
  then
    echo "  FAILED"
  fi
done
echo "DONE"
