# Tasks: sync-skills-from-docs-round-10

## 1. OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `MERGE_MAP.md` (Phase 0 reconnaissance).
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 1 spec delta (agent-observability).
- [x] Validate `--strict`.

## 2. Phase 10.A: bulk delete 08-mirrors (175 MB)
- [x] `git rm -rf docs/08-mirrors/marimo docs/08-mirrors/marimo-docs`
- [x] `rmdir docs/08-mirrors/` (now empty)
- [x] Pre-deletion sanity checks passed

## 3. Phase 10.B: new skills (3) + KCG doc moves (~16)
- [x] `.agents/skills/kcg-deploy-runbooks/SKILL.md`
      (~180 lines) + 5 references
- [x] `.agents/skills/agent-docs-patterns/SKILL.md`
      (~100 lines) + 1 reference
- [x] `.agents/skills/kcg-docs-consolidation/SKILL.md`
      (~150 lines) + 2 references
- [x] 5 deploy plans moved
- [x] 5 02-audit files moved
- [x] 2 02-architecture files moved
- [x] 3 03-agents files moved
- [x] 1 03-pipelines file moved
- [x] 1 00_index.md moved
- [x] 2 08-screenshots main files moved

## 4. Phase 10.C: Cognee stack moves + expansions (~11)
- [x] 11 01-cognee files moved to cognee/agent-observability/ccc
- [x] `cognee` skill expanded (+4 sections)
- [x] `agent-observability` skill expanded (+6 sections)
- [x] `ccc` skill expanded (+2 sections)

## 5. Phase 10.D: tombstones + untracked + external (~25)
- [x] 27 `docs_examples_consolidated/` files deleted
- [x] 3 `docs/hackathons/` MD files moved to
      `upstream-mirrors/references/clippings/`
- [x] 1 `docs/hmgcc/` TRL MD file moved to clippings
- [x] 5 `docs/openspec/` research files deleted
- [x] 2 `docs/07-standards/` files moved + skill
      expansions
- [x] 1 `08-screenshots/TEAM_HANDOFF.md` skill
      expansion
- [x] 1 `08-screenshots/UI_INSPIRATION_GUIDE.md` moved
      + ui-components skill expanded

## 6. Phase 10.X: misc expansions
- [x] `tuatha-mmo` skill expanded (KCG quadrant
      reference)
- [x] `agentic-frontend-frameworks` skill expanded (MCP
      protocol, MCP servers, Agent framework index)
- [x] `celtic-asset-generation` skill expanded (KCG
      AI/ML pipeline, KCG critical constraints, KCG
      docs taxonomy)
- [x] `kcg-convergence` skill expanded (Team-workflow
      stack + migration report)
- [x] `ui-components` skill expanded (KCG UI design
      language)

## 7. Verify
- [ ] Re-validate `--strict`.
- [ ] `git status --short | wc -l` is reasonable
      (~5000 staged = 4346 08-mirrors + ~700 others).

## 8. Archive
- [ ] `openspec archive sync-skills-from-docs-round-10
      --yes`.

## 9. Land the plane
- [ ] `git add` only my changes (avoid the pre-existing
      .gitignore, .infisical.env, stirling-pdf,
      cocoindex_flows, untracked top-level docs, etc.).
- [ ] `git commit -m "..."`.
- [ ] `git push`.
