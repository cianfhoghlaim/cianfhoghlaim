# Tasks: docs-skills-canonical-reference

## 1. Spec deltas (infrastructure-stacks)

- [x] Add 3 Requirements to the `infrastructure-stacks` spec:
      - "Skill metadata hygiene" (rules 1-4)
      - "Skill consolidation conventions" (rules 5-8)
      - "Skill + openspec alignment" (rules 9-10)
- [x] 6 Scenarios total (2 per Requirement)

## 2. The lint script

- [x] Create `.agents/skills/lint-skills.sh` with the 4 metadata
      checks (frontmatter, name match, description length, line
      count)

## 3. Wire to mise

- [x] Add `[tasks.lint-skills]` to `mise.toml`:
      `run = "bash .agents/skills/lint-skills.sh"`

## 4. Validate + commit + push

- [x] `openspec validate docs-skills-canonical-reference --strict`
- [x] Commit with message
      `docs-skills-canonical-reference: add 3 Requirements for skill metadata + lint:skills task`
- [x] Archive the openspec change
- [x] `git push`
