# Tasks: sync-skills-from-docs-round-3

## 1. Create OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 1 spec delta (tuatha-platform).
- [x] Validate `--strict`.

## 2. New skills (3)
- [x] Create `.agents/skills/modal/SKILL.md`.
- [x] Create `.agents/skills/babylonjs/SKILL.md`.
- [x] Create `.agents/skills/tuatha-platform/SKILL.md`.

## 3. Skill expansions (4)
- [x] Append KCG section to `.agents/skills/ducklake/SKILL.md`
      (DuckLake ATTACH, MotherDuck, kcg-cocoindex, stedding/).
- [x] Append KCG context to `.agents/skills/dagster/SKILL.md`
      (from docs/02-data-platform/dagster.md:79-117 + 763-794).
- [x] Append KCG blurb to `.agents/skills/sqlmesh/SKILL.md`.
- [x] Append KCG blurb to `.agents/skills/hono/SKILL.md`.

## 4. Delete the listed docs
- [x] `rm docs/02-data-platform/duckdb.md`
- [x] `rm docs/02-data-platform/dlt.md`
- [x] `rm docs/02-data-platform/dagster.md`
- [x] `rm docs/02-data-platform/sqlmesh.md`
- [x] `rm docs/01-platform-architecture/hono.md`
- [x] `rm docs/01-platform-architecture/modal.md`
- [x] `rm docs/06-product/babylonjs.md`
- [x] `rm docs/06-product/TUATH_QUICKSTART.md`

## 5. Verify
- [ ] Re-validate `--strict`.
- [ ] Re-index codebase.

## 6. Archive
- [ ] `openspec archive sync-skills-from-docs-round-3 --yes`.

## 7. Land the plane
- [ ] `git add` only my changes.
- [ ] `git commit -m "..."`.
- [ ] `git push`.
