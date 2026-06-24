# Tasks: consolidate-motherduck-skills

## 1. Create the 4 new consolidated skills

- [x] Create `.agents/skills/motherduck-architecture/SKILL.md` (merges 5 skills)
- [x] Create `.agents/skills/motherduck-data-modeling/SKILL.md` (merges 2 skills)
- [x] Create `.agents/skills/motherduck-analytics/SKILL.md` (merges 6 skills)
- [x] Create `.agents/skills/motherduck-connections/SKILL.md` (merges 5 skills)

## 2. Update the router

- [x] Update `.agents/skills/motherduck/SKILL.md` to delegate to the
      4 new skills (router table) + keep the MCP section verbatim

## 3. Delete the 18 sub-skill directories

- [x] `git rm -r .agents/skills/motherduck-build-data-pipeline`
- [x] `git rm -r .agents/skills/motherduck-build-cfa-app`
- [x] `git rm -r .agents/skills/motherduck-build-dashboard`
- [x] `git rm -r .agents/skills/motherduck-connect`
- [x] `git rm -r .agents/skills/motherduck-create-dive`
- [x] `git rm -r .agents/skills/motherduck-duckdb-sql`
- [x] `git rm -r .agents/skills/motherduck-ducklake`
- [x] `git rm -r .agents/skills/motherduck-enable-self-serve-analytics`
- [x] `git rm -r .agents/skills/motherduck-explore`
- [x] `git rm -r .agents/skills/motherduck-load-data`
- [x] `git rm -r .agents/skills/motherduck-migrate-to-motherduck`
- [x] `git rm -r .agents/skills/motherduck-model-data`
- [x] `git rm -r .agents/skills/motherduck-partner-delivery`
- [x] `git rm -r .agents/skills/motherduck-pricing-roi`
- [x] `git rm -r .agents/skills/motherduck-query`
- [x] `git rm -r .agents/skills/motherduck-rest-api`
- [x] `git rm -r .agents/skills/motherduck-security-governance`
- [x] `git rm -r .agents/skills/motherduck-share-data`

## 4. Validate

- [x] `openspec validate consolidate-motherduck-skills --strict`
- [x] Verify `motherduck` router still has frontmatter
- [x] Verify no orphan references to deleted skill names

## 5. Commit + push

- [x] Commit with message
      `consolidate-motherduck-skills: 19 → 5 (router + 4 task-specific)`
- [x] `git pull --rebase` then `git push`
