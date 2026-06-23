# Tasks: sync-skills-from-docs-round-5

## 1. Create OpenSpec change scaffolding
- [x] Create change directory.
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 2 spec deltas (infrastructure-stacks, agent-observability).
- [x] Validate `--strict`.

## 2. New skills (5)
- [x] Create `.agents/skills/embedding-pipeline/SKILL.md`.
- [x] Create `.agents/skills/agent-observability/SKILL.md`.
- [x] Create `.agents/skills/kubernetes/SKILL.md`.
- [x] Create `.agents/skills/monorepo/SKILL.md`.
- [x] Create `.agents/skills/secrets-management/SKILL.md`.

## 3. Skills rewritten (2)
- [x] Rewrite `.agents/skills/komodo/SKILL.md` (KCG-specific).
- [x] Rewrite `.agents/skills/pangolin/SKILL.md` (KCG-specific).

## 4. Skills expanded (5)
- [x] Append KCG context to `.agents/skills/stack-ops/SKILL.md`.
- [x] Append Forms section to `.agents/skills/tanstack-start/SKILL.md`.
- [x] Append m2m-100 row to `.agents/skills/celtic-language-ai/SKILL.md`.
- [x] Append BGE-M3 note to `.agents/skills/lancedb/SKILL.md`.
- [x] Append framework comparison to `google-adk` + `agno` skills.

## 5. Delete the 17 docs
- [x] `rm docs/01-patterns/AGENTS.md`
- [x] `rm docs/01-patterns/DATA_PIPELINE.md`
- [x] `rm docs/01-patterns/EMBEDDINGS.md`
- [x] `rm docs/01-patterns/OBSERVABILITY.md`
- [x] `rm docs/01-patterns/WEB.md`
- [x] `rm docs/01-platform-architecture/BONNEAGAR_OVERVIEW.md`
- [x] `rm docs/01-platform-architecture/DEPLOYMENT_STATUS.md`
- [x] `rm docs/01-platform-architecture/infrastructure-stacks.md`
- [x] `rm docs/01-platform-architecture/komodo-gitops.md`
- [x] `rm docs/01-platform-architecture/kubernetes-deployment.md`
- [x] `rm docs/01-platform-architecture/m2m-100.md`
- [x] `rm docs/01-platform-architecture/monorepo-strategy.md`
- [x] `rm docs/01-platform-architecture/pangolin-networking.md`
- [x] `rm docs/01-platform-architecture/platform-overview.md`
- [x] `rm docs/01-platform-architecture/secrets-management.md`
- [x] `rm docs/01-platform-architecture/services-roadmap.md`
- [x] `rm docs/01-platform-architecture/TECH_STACK.md`

## 6. Verify
- [ ] Re-validate `--strict`.

## 7. Archive
- [ ] `openspec archive sync-skills-from-docs-round-5 --yes`.

## 8. Land the plane
- [ ] `git add` only my changes.
- [ ] `git commit -m "..."`.
- [ ] `git push`.
