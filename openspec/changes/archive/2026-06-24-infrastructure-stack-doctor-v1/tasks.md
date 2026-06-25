# Tasks: infrastructure-stack-doctor-v1

## 1. 3 new skills

- [x] Create `.agents/skills/kcg-pangolin-stack/SKILL.md` (155 lines, valid frontmatter)
- [x] Create `.agents/skills/kcg-locket-sidecar/SKILL.md` (201 lines, valid frontmatter)
- [x] Create `.agents/skills/kcg-infrastructure-audit/SKILL.md` (242 lines, valid frontmatter)

## 2. Openspec change

- [x] Create `openspec/changes/infrastructure-stack-doctor-v1/proposal.md`
- [x] Create `openspec/changes/infrastructure-stack-doctor-v1/tasks.md`
- [x] Create `openspec/changes/infrastructure-stack-doctor-v1/specs/infrastructure-stacks/spec.md`
  (1 MODIFIED + 1 ADDED + 5 supporting MODIFIED Requirements)
- [x] `openspec validate infrastructure-stack-doctor-v1 --strict`
- [x] `openspec archive infrastructure-stack-doctor-v1 --yes`

## 3. Refactor: 4 quadrant deploy quartets → `infrastructure/stacks/<quadrant>/`

- [x] Move `meaisinfhogmlaim/{compose.yaml, sidecar.yaml, blueprint.yaml, secrets.env}` → `infrastructure/stacks/sruth/meaisinfhoghlaim/`
- [x] Move `sruth/tuatha/{pangolin.yaml, docker-compose.yaml, compose.dev.yaml}` → `infrastructure/stacks/sruth/tuatha/`
- [x] Move `sruth/croilar/{compose.yaml, compose.dev.yaml, sidecar.yaml, secrets.env, Dockerfile.dagster}` → `infrastructure/stacks/sruth/croilar/`
- [x] Add thin re-export shims at the source locations for backward compat

## 4. Refactor: delete 5 legacy `.ts` files

- [x] `git rm infrastructure/legacy/ansible.ts`
- [x] `git rm infrastructure/legacy/cloudflare-dns.ts`
- [x] `git rm infrastructure/legacy/pangolin-setup.ts`
- [x] `git rm infrastructure/legacy/servers.ts`
- [x] `git rm infrastructure/legacy/taisce-deploy.ts`
- [x] Update `infrastructure/legacy/README.md` to keep only `LOCKET-MODES.md` + `ANALYSIS.md` references

## 5. Refactor: delete 5 deferred runbooks

- [x] `git rm infrastructure/deploy-runbooks/cal-diy.md`
- [x] `git rm infrastructure/deploy-runbooks/vikunja.md`
- [x] `git rm infrastructure/deploy-runbooks/n8n.md`
- [x] `git rm infrastructure/deploy-runbooks/changedetection.md`
- [x] `git rm infrastructure/deploy-runbooks/bytebase.md`
- [x] Update `infrastructure/deploy-runbooks/README.md` to point at the 4 active runbooks

## 6. 7 doc updates (1-line diffs each)

- [x] `infrastructure/AGENTS.md` — add the 7th bullet (image pinning)
- [x] `infrastructure/README.md` — update stack count to 93
- [x] `infrastructure/GOLD_STANDARD.md` — add the forbidden `:latest` rule
- [x] `infrastructure/audit/README.md` — add the 5th quick-start step (`stack-doctor`)
- [x] `infrastructure/komodo/README.md` — mark the 5 legacy `.ts` files as `STATUS: scheduled-for-deletion-2026-07`
- [x] `infrastructure/stacks/README.md` — update count
- [x] `openspec/specs/infrastructure-stacks/spec.md` — append the new "Image Pinning Policy" Requirement

## 7. Commit + push + archive

- [x] `git commit -m "refactor(infrastructure): add 3 skills + stack-doctor + 4 quadrant deploy quartets (round 7)"`
- [x] `git push origin q3-2026-oideachais-consolidation`
- [x] `openspec archive infrastructure-stack-doctor-v1 --yes`
- [x] `git commit -m "openspec(archive): 2026-06-24-infrastructure-stack-doctor-v1"`
- [x] `git push origin q3-2026-oideachais-consolidation`
