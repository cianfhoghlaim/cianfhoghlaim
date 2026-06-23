# Tasks: sync-skills-from-docs-round-6

## 1. Create OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 1 spec delta (oideachais-pipeline).
- [x] Validate `--strict`.

## 2. New skills (4)
- [x] Create `.agents/skills/cross-domain-registry/SKILL.md`.
- [x] Create `.agents/skills/oideachais-storage/SKILL.md`.
- [x] Create `.agents/skills/frontend-topology/SKILL.md`.
- [x] Create `.agents/skills/ui-components/SKILL.md`.

## 3. Skills expanded (3)
- [x] Expand `.agents/skills/oideachas-pipeline/SKILL.md`
      (Tripartite Data Landscape + BAML schemas).
- [x] Expand `.agents/skills/browser/SKILL.md` (KCG decision tree).
- [x] Expand `.agents/skills/irish-edtech/SKILL.md`
      (Product vision: Agentic Academy).

## 4. Delete the 12 docs
- [x] `rm docs/02-data-platform/DATA_ARCHITECTURE.md`
- [x] `rm docs/02-data-platform/data-architecture.md`
- [x] `rm docs/02-data-platform/cross-domain-registry.md`
- [x] `rm docs/02-data-platform/LANGUAGE_ARCHITECTURE.md`
- [x] `rm docs/02-data-platform/STORAGE.md`
- [x] `rm docs/03-agents/browser-automation.md`
- [x] `rm docs/03-agents/IRISH_EDUCATION_PLATFORM_BLUEPRINT.md`
- [x] `rm docs/05-web/FRONTEND_STACK.md`
- [x] `rm docs/05-web/frontend-topology.md`
- [x] `rm docs/05-web/frontend-stack.md`
- [x] `rm docs/05-web/ui-components.md`

## 5. Verify
- [ ] Re-validate `--strict`.

## 6. Archive
- [ ] `openspec archive sync-skills-from-docs-round-6 --yes`.

## 7. Land the plane
- [ ] `git add` only my changes.
- [ ] `git commit -m "..."`.
- [ ] `git push`.
