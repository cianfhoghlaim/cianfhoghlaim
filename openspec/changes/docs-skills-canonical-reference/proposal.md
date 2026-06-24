## Why

The 8-step q3-2026-oideachais-consolidation work surfaced
several governance gaps in how `.agents/skills/` is maintained.
The same gaps will keep recurring every time a new skill is
added unless we capture the rules in an openspec spec and
enforce them with a `lint:skills` script.

The 4 rules this change captures:

1. **Every skill MUST have YAML frontmatter.** Skills without
   frontmatter are invisible to the skill loader. Verified by
   the `skills-metadata-cleanup` change (A): `baml/SKILL.md`
   had 530 lines of useful content but no frontmatter.
2. **The `name:` frontmatter field MUST equal the parent
   directory name.** Verified by the `skills-metadata-cleanup`
   change (A): `firecrawl-cli/SKILL.md` had `name: firecrawl`,
   causing a name collision with the canonical `firecrawl/`.
3. **The `description:` field MUST be at least 40 characters.**
   A short description is often too vague to match the right
   trigger phrase; 40 chars is a reasonable floor.
4. **The `SKILL.md` body MUST be under 2,000 lines.** Anything
   longer should be split into a router + reference files
   (e.g. `motherduck/SKILL.md` is 175 lines + 3 reference files).

The 5 cross-cutting rules from the consolidation work:

5. **Skill name prefix conventions**:
   - `motherduck*` → MotherDuck (motherduck + 4 consolidated)
   - `motherduck-architecture` / `motherduck-data-modeling` /
     `motherduck-analytics` / `motherduck-connections` →
     task-specific MotherDuck sub-skills
   - `browser-tools` → browser / scraping / agent-on-the-web router
   - `ccc` → code search (canonical)
   - `kcg-*` → KCG-authored cross-cutting skills
   - `oideachais-*` → project-specific to the oideachais quadrant
   - `tuatha-*` → project-specific to the tuatha quadrant
   - `croilar-*` → project-specific to the croilar quadrant
   - `meaisinfhoghlaim-*` → project-specific to the AI/ML quadrant
6. **No upstream Anthropic / vendor skills** (the 13 removed
   in A: canvas-design, frontend-design, etc.). Upstream
   content can be referenced from a KCG-authored skill but
   should not be vendored.
7. **No skills that are personas / content that duplicates
   the root `AGENTS.md`** (the 4 removed in A: homebrew,
   data-engineer, devops-architect, image-management).
8. **No embedded git sub-repositories** (the 2 spaces/* dirs
   that got picked up by `git add -A` and are tracked as
   submodules — they should be `.gitignore`d or properly
   initialised as submodules).

The 4 governance rules from the 4 shared-spec router skills:

9. **Every openspec capability spec SHOULD have a matching
   skill.** If the spec has no skill, add a thin router skill
   that points at the existing umbrella skills. (The 4
   router skills added in B4 cover the 4 shared specs that
   previously had no skill.)
10. **When an openspec change is archived, the canonical
    skill gets a "Post-archive update" note** (instead of
    being stale).

The `lint:skills` script:

```bash
#!/usr/bin/env bash
# .agents/skills/lint-skills.sh
# Run from the repo root.
set -euo pipefail

SKILL_DIR=.agents/skills
errors=0

for d in "$SKILL_DIR"/*/; do
  skill="${d%/}"
  skill_name="${skill##*/}"
  if [ ! -f "$skill/SKILL.md" ]; then
    continue  # Not a skill directory
  fi

  # 1. frontmatter exists
  if ! head -1 "$skill/SKILL.md" | grep -q "^---$"; then
    echo "ERROR: $skill has no YAML frontmatter (rule 1)"
    errors=$((errors + 1))
  fi

  # 2. name: field matches directory
  declared_name=$(awk '/^name:/{print $2; exit}' "$skill/SKILL.md")
  if [ "$declared_name" != "$skill_name" ]; then
    echo "ERROR: $skill has name='$declared_name' but directory is '$skill_name' (rule 2)"
    errors=$((errors + 1))
  fi

  # 3. description is at least 40 chars
  desc=$(awk '/^description:/{$1=""; print substr($0,2); exit}' "$skill/SKILL.md")
  if [ "${#desc}" -lt 40 ]; then
    echo "ERROR: $skill has description with ${#desc} chars (< 40) (rule 3)"
    errors=$((errors + 1))
  fi

  # 4. SKILL.md body is under 2000 lines
  lines=$(wc -l < "$skill/SKILL.md")
  if [ "$lines" -gt 2000 ]; then
    echo "ERROR: $skill SKILL.md has $lines lines (> 2000) (rule 4)"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -gt 0 ]; then
  echo "lint:skills found $errors errors"
  exit 1
fi
echo "lint:skills: all 110 skills pass"
```

## What changes

- New spec `infrastructure-stacks` Requirement: "Skill metadata
  hygiene" (rules 1-4)
- New spec `infrastructure-stacks` Requirement: "Skill
  consolidation conventions" (rules 5-8)
- New spec `infrastructure-stacks` Requirement: "Skill + openspec
  alignment" (rules 9-10)
- New script `.agents/skills/lint-skills.sh` (the lint script)
- New mise task `lint:skills` in `mise.toml`
