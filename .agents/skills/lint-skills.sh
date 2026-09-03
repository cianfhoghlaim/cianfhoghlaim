#!/usr/bin/env bash
# lint-skills.sh — enforce the 4 metadata rules for every skill under
# .agents/skills/. Run from the repo root.
#
# Rule 1: every skill MUST have a YAML frontmatter block (--- ... ---)
# Rule 2: the `name:` frontmatter field MUST equal the parent directory name
# Rule 3: the `description:` field MUST be at least 40 characters
# Rule 4: the SKILL.md body MUST be under 2,000 lines (split into a router
#         + reference files for larger content)
set -euo pipefail

SKILL_DIR="${1:-.agents/skills}"

if [ ! -d "$SKILL_DIR" ]; then
  echo "lint-skills: $SKILL_DIR is not a directory" >&2
  exit 2
fi

errors=0
skills=0

for d in "$SKILL_DIR"/*/; do
  skill_path="${d%/}"
  skill_name="${skill_path##*/}"

  # Skip non-skill directories: hidden (_*), backup, etc.
  case "$skill_name" in
    _*|.*) continue ;;
  esac

  # Skip directories without SKILL.md
  if [ ! -f "$skill_path/SKILL.md" ]; then
    continue
  fi

  skills=$((skills + 1))

  # Use Python to parse YAML frontmatter properly (handles multi-line,
  # pipe-block-scalar, continuation-indent, etc.)
  if ! python3 - "$skill_path" "$skill_name" << 'PYEOF'
import sys, re

skill_path, skill_name = sys.argv[1], sys.argv[2]
errors = []

with open(f"{skill_path}/SKILL.md") as f:
    content = f.read()

# Extract frontmatter
m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
if not m:
    print(f"ERROR: {skill_name} has no YAML frontmatter (rule 1)"); sys.exit(1)

fm = m.group(1)

# Rule 2: name match
m_name = re.search(r"^name:\s*(\S+)", fm, re.MULTILINE)
if not m_name:
    print(f"ERROR: {skill_name} has no name: in frontmatter (rule 2)")
    sys.exit(1)
declared_name = m_name.group(1)
if declared_name != skill_name:
    print(f"ERROR: {skill_name} has name='{declared_name}' but directory is '{skill_name}' (rule 2)")
    sys.exit(1)

# Rule 3: description length
# Match either `description: <text>` (possibly multi-line indented) or
# `description: |` (literal block scalar)
m_desc = re.search(
    r"^description:\s*(?:\|\s*\n((?:[ \t]+.*\n)+)|(.*?))(?=\n[a-zA-Z_-]|\n---|\Z)",
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
PYEOF
  then
    errors=$((errors + 1))
  fi

  # Rule 4: line count
  lines=$(wc -l < "$skill_path/SKILL.md")
  if [ "$lines" -gt 2000 ]; then
    echo "ERROR: $skill_name SKILL.md has $lines lines (> 2000) (rule 4)" >&2
    errors=$((errors + 1))
  fi
done

if [ "$errors" -gt 0 ]; then
  echo "" >&2
  echo "lint-skills: $errors errors in $skills skills" >&2
  exit 1
fi
echo "lint-skills: $skills skills pass"
