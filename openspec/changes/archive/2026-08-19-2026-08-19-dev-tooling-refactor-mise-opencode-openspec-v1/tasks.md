# Tasks — 2026-08-19 Dev Tooling Refactor

Ordered for incremental validation. Each phase ends with a quality gate
that must pass before the next phase begins.

## Phase 0 — Baseline preflight (READ-ONLY)

- [x] `git status` baseline — confirmed dirty but expected
- [x] `mise --version` baseline — 2026.5.6 (latest 2026.8.8 available)
- [x] `opencode --version` baseline — 1.18.16
- [x] `openspec --version` baseline — 1.4.1
- [x] `openspec validate --all --strict` baseline — 129 items pass
- [x] `bash .agents/skills/lint-skills.sh` baseline — 62 skills pass

## Phase 1 — Add 3 new skills (zero risk, additive)

- [x] Write `.agents/skills/openspec/SKILL.md`
- [x] Write `.agents/skills/mise/SKILL.md`
- [x] Write `.agents/skills/opencode/SKILL.md`
- [x] `bash .agents/skills/lint-skills.sh` exits 0 (target: ≥65 skills)

## Phase 2 — Add 3 new CCC concept guides (zero risk, additive)

- [x] Append `opencode-agent-search` to `.cocoindex_code/guides.yml`
- [x] Append `mise-task-search` to `.cocoindex_code/guides.yml`
- [x] Append `openspec-change-search` to `.cocoindex_code/guides.yml`
- [x] `mise run lint:guides-yml` exits 0 (target: ≥30 guides)

## Phase 3 — Update `openspec/AGENTS.md` (zero risk, additive)

- [x] Add 3 new priority commands (`view`, `status`, `validate --all`)
- [x] Add 1 new priority skill row (`openspec`)
- [x] Add 1 new priority task (`openspec:validate-all`)
- [x] Add "OPSX vs legacy schema" section
- [x] Smoke check: cross-references still resolve

## Phase 4 — Refactor opencode agents (medium risk — agent behavior)

- [x] Write `.opencode/agents/data-platform.md`
- [x] Write `.opencode/agents/infrastructure.md`
- [x] Write `.opencode/agents/agent-platform.md`
- [x] Write `.opencode/agents/frontend-apps.md`
- [x] Write `.opencode/agents/notebooks.md`
- [x] Write `.opencode/agents/baml.md`
- [x] Write `.opencode/agents/dagster.md`
- [x] Write `.opencode/agents/mise.md`
- [x] Write `.opencode/agents/proposal-author.md`
- [x] Migrate every `tools:` block to `permission:` in opencode.json
- [x] Reduce inline agents to 4 (build, plan, research, orchestrator)
- [x] Set `subagent_depth: 2`
- [x] Set `watcher.ignore` array
- [x] Set `compaction.{auto,prune,reserved}`
- [x] Set `instructions` array
- [x] Set `hidden: true` on dev-env-demo + deep-cuts
- [x] Verify `grep -E '"tools":\s*\{' opencode.json` returns 0
- [x] Verify `find .opencode/agents -name "*.md" | wc -l` returns ≥9
- [x] `mise run lint` exits 0

## Phase 5 — Refactor `mise.toml` (highest risk — every CI gate)

- [x] Identify all 50+ single-line Python entrypoints
- [x] Generate `mise-tasks/meaisin/ocr-*.sh` files (templates)
- [x] Generate `mise-tasks/meaisin/converter-*.sh` files (templates)
- [x] Generate `mise-tasks/meaisin/agent-*.sh` files (templates)
- [x] Move 41 `sync:*` tasks → 7 `mise-tasks/sync/*.sh` file tasks
- [x] Move 11 `biep:v3:m<n>` tasks → 11 `mise-tasks/biep/m-<n>.sh` files
- [x] Move iac / preflight / stack tasks → `mise-tasks/{iac,preflight,stack}/*.sh`
- [x] Add `[task_templates]` block for OCR/converter/agent/biep/marimo
- [x] Collapse `cic:*` ↔ bare aliases (5 duplicates removed)
- [x] Collapse `iac-*` ↔ `iac:*` aliases (via `alias =`)
- [x] Collapse `preflight-arm-oci` ↔ `preflight:arm-oci` (via `alias =`)
- [x] Add `depends = [...]` to all quality gates
- [x] Add `usage = '''arg "..."'''` to all entrypoint templates
- [x] Add `mise run openspec:validate-all` task
- [x] Add `mise run opencode:{index,search,validate}` tasks
- [x] `mise run doctor` exits 0
- [x] `mise run lint` exits 0
- [x] `mise run sync:all` exits 0
- [x] `mise run openspec:validate-all` exits 0 (new task)
- [x] `mise run cic:stack-doctor` exits 0

## Phase 6 — openspec change lifecycle

- [x] `openspec validate 2026-08-19-dev-tooling-refactor-mise-opencode-openspec-v1 --strict` exits 0
- [x] `openspec archive 2026-08-19-dev-tooling-refactor-mise-opencode-openspec-v1 --yes` exits 0
- [x] Verify `openspec list --specs` shows `dev-tooling-surfaces`

## Post-phase validation

- [x] All 10 acceptance criteria from `proposal.md` pass
- [x] No secrets written to disk
- [x] No `mise run` mutations outside the scope of this change
- [x] User review + explicit `git push` request before any push
