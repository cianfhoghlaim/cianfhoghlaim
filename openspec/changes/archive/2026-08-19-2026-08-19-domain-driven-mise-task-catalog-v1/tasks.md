# Tasks — 2026-08-19 Domain-Driven mise.toml Task Catalog

Ordered for incremental validation. Each phase ends with a quality gate.

## Phase 0 — Baseline (READ-ONLY)

- [x] `git status` clean (modulo pre-existing dirty state)
- [x] `openspec validate --all --strict --no-interactive` → 130 items pass
- [x] `bash .agents/skills/lint-skills.sh` → 65 skills pass
- [x] Confirmed 119 tasks in current `mise.toml`

## Phase 1 — Scaffold openspec change

- [x] `mkdir -p openspec/changes/2026-08-19-domain-driven-mise-task-catalog-v1/specs/dev-tooling-surfaces/`
- [x] Write `proposal.md` (MUST include `## Dependencies`, `## Why`, `## What changes`, `## Acceptance criteria`, `## Rollback plan`)
- [x] Write `tasks.md` (this file)
- [x] Write `specs/dev-tooling-surfaces/spec.md` delta (6 ADDED Requirements)
- [ ] `openspec validate 2026-08-19-domain-driven-mise-task-catalog-v1 --strict` → pass

## Phase 2 — Write new `mise.toml` (the big swap)

- [ ] Drop the 37 dead tasks (per the audit in proposal.md)
- [ ] Add 6 namespaces: `core`, `openspec`, `devops`, `data`, `ml`, `web`
- [ ] Add all back-compat `alias = [...]` for tasks referenced in CI/docs
- [ ] Add omnibus tasks: `core`, `core:ci`, `devops`, `data`, `ml`, `web`
- [ ] Add 3 `[task_templates]` blocks: `ml:ocr:test`, `ml:converter:test`, `ml:agent:test`
- [ ] Verify TOML parses with `python3 -c "import tomllib; tomllib.loads(open('mise.toml').read())"`
- [ ] Verify `mise tasks --all` shows the new namespace layout

## Phase 3 — Create `mise-tasks/{core,devops,data,ml,web}/` file scripts (~22 files)

### core/ (3 scripts)
- [ ] `mise-tasks/core/ci` — omnibus CI gate (lint + test + openspec + stack-doctor)
- [ ] `mise-tasks/core/install` — uv sync + bun install
- [ ] `mise-tasks/core/lint` — aggregate lint (ruff + skills + registry + drift-docs + guides-yml)

### devops/ (7 scripts)
- [ ] `mise-tasks/devops/bootstrap` — Pulumi → Infisical → Pangolin → Komodo → Newt
- [ ] `mise-tasks/devops/plan` — IaC diff (no mutation)
- [ ] `mise-tasks/devops/health` — Komodo + Pangolin + Infisical state consistency
- [ ] `mise-tasks/devops/stack` — `<name> <up|down|logs>` per-stack lifecycle
- [ ] `mise-tasks/devops/preflight` — `arm-oci | lakehouse | iac` dispatch
- [ ] `mise-tasks/devops/deploy-full` — 7-phase state machine
- [ ] `mise-tasks/devops/validate-stacks` — 89 stacks × GOLD_STANDARD

### data/ (7 scripts)
- [ ] `mise-tasks/data/up` — lakehouse stack bring-up (16 services)
- [ ] `mise-tasks/data/down` — lakehouse stack teardown
- [ ] `mise-tasks/data/biep-setup` — BIEP v3 full setup
- [ ] `mise-tasks/data/biep-status` — BIEP v3 full status
- [ ] `mise-tasks/data/biep-registry-seed` — seed the BIEP registry
- [ ] `mise-tasks/data/biep-marimo-wasm-export` — export 14 BIEP dashboards to WebAssembly
- [ ] `mise-tasks/data/cocoindex-conformance` — R1-R4 conformance audit

### ml/ (3 scripts)
- [ ] `mise-tasks/ml/registry-audit` — HF Hub liveness on all 24 VISION_MODELS
- [ ] `mise-tasks/ml/litellm-regenerate` — regenerate litellm config from MODEL_REGISTRY
- [ ] `mise-tasks/ml/agents-reproduce` — 12-agent fleet cold→green reproducer

### web/ (2 scripts)
- [ ] `mise-tasks/web/dev` — per-app dev server (`bunx turbo run dev --filter=<app>`)
- [ ] `mise-tasks/web/cf-deploy` — Cloudflare Pages deploy

## Phase 4 — Validate

- [ ] `python3 -c "import tomllib; tomllib.loads(open('mise.toml').read())"` → VALID
- [ ] `mise tasks --all | wc -l` → ≥ 80 (target: 107)
- [ ] `mise run core:doctor` → exits 0
- [ ] `mise run core:lint` → exits 0
- [ ] `mise run openspec:validate-all` → exits 0 with 130+ items
- [ ] `mise run data:dagster:up --help` → shows Dagster help
- [ ] `mise run ml:registry:list` → prints MODEL_REGISTRY entries
- [ ] `mise run web:install` → exits 0 (or graceful fail with bun not installed)
- [ ] All CI workflows (`.github/workflows/ci.yaml`, `baml-test.yaml`, `cocoindex-conformance.yaml`) still work via aliases
- [ ] `openspec validate --all --strict` → exits 0 with 131 items (130 + new spec)

## Phase 5 — Update docs

- [ ] Update `AGENTS.md` priority mise tasks list (root AGENTS.md)
- [ ] Update `openspec/AGENTS.md` priority mise tasks list
- [ ] Update `.agents/skills/mise/SKILL.md` to document the 6-namespace shape
- [ ] Update `.cocoindex_code/guides.yml#mise-task-search` if needed
- [ ] Update `.agents/skills/baml/SKILL.md` if it references dropped tasks
- [ ] Update `.agents/skills/dagster/SKILL.md` if it references dropped tasks

## Phase 6 — openspec archive + commit + push

- [ ] `openspec validate 2026-08-19-domain-driven-mise-task-catalog-v1 --strict` → exits 0
- [ ] `openspec archive 2026-08-19-domain-driven-mise-task-catalog-v1 --yes` → archives the change
- [ ] Verify `openspec list --specs` shows `dev-tooling-surfaces` (with the 6 new ADDED Requirements merged in)
- [ ] `openspec validate --all --strict` → exits 0 with 131 items
- [ ] `git status` shows only the intended changes
- [ ] User explicitly requests `git push`
- [ ] `git push` to `origin/token-plan-lc-pipeline-2026-08`
- [ ] Verify `git ls-remote` matches local commit hash

## Post-phase validation

- [ ] All 14 acceptance criteria from `proposal.md` pass
- [ ] No secrets written to disk
- [ ] No `mise run` mutations outside the scope of this change
