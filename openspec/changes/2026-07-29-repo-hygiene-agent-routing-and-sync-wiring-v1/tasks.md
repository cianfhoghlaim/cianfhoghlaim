# Tasks: 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1

## Phase 1 — OpenSpec change scaffolding (4 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1/proposal.md` (the why + what changes)
- [ ] **T1.2**: Create `openspec/changes/2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/changes/2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1/cross-repo-sync.md` (single-repo; documented no-op)
- [ ] **T1.4**: Create `openspec/changes/2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1/specs/{repo-hygiene-agent-routing,centralize-cross-cutting-docs,knowledge-sync-loop,infrastructure-stacks}/spec.md` (the 4 spec deltas)

## Phase 2 — Drift correction (5 tasks)

- [ ] **T2.1**: Create `scripts/lint_drift_docs.py` — the anti-drift lint that walks the 10 in-repo `AGENTS.md` + `openspec/AGENTS.md` + root `AGENTS.md`, regex-extracts `(\d+) (specs|skills|stacks|models|notebooks)` claims, validates against ground truth (`openspec list --specs`, `find .agents/skills -name SKILL.md`, `ls -d bonneagar/stacks/*/`, `MODEL_REGISTRY.summary()["total"]`, `find notebooks -name "*.py"`), writes a JSON + MD report to `stedding/sync-reports/docs-drift-{date}.md`, exits 1 on any mismatch
- [ ] **T2.2**: Add `mise run lint:drift-docs` task to `mise.toml` (description: "Validate every AGENTS.md number claim against ground truth; exits 1 on any mismatch; per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change")
- [ ] **T2.3**: Fix the 6 stale number claims in `AGENTS.md` (`75→78 specs`, `153→155 skills`, `88→89 stacks`, `7 of 153→7 of 155`, `11 of 75→12 of 78`, `153 skills pass→155 skills pass`)
- [ ] **T2.4**: Create 5 per-area `AGENTS.md` files in `orchestration/`, `baml_src/`, `meaisinfhoghlaim/`, `notebooks/`, `web/` (each follows the 6-section outline from `openspec/specs/repo-hygiene-agent-routing/templates/spec-AGENTS.md.tmpl`)
- [ ] **T2.5**: Create `web/README.md` (a 20-line bridge so the `web/` directory is not a black box) and refresh `openspec/AGENTS.md` to reference the 3 new specs

## Phase 3 — Knowledge-sync wiring (4 tasks)

- [ ] **T3.1**: Create `orchestration/automation/sync_schedules.py` with `@schedule(cron_schedule="0 */4 * * *", job=define_asset_job(name="sync_health_job", selection=AssetSelection.groups("3_model_lifecycle/sync_health")))` (attaches the cron that the existing `sync_health` asset docstring already promises)
- [ ] **T3.2**: Create `scripts/sync/dagster.sh` (Layer 6 per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change) — walks the 5-layer `defs/` tree, parses each `.py` with `ast`, validates ≥200 `@asset` decorators + ≥16 sensors + working imports, writes per-group report to `stedding/sync-reports/dagster-{date}.md`
- [ ] **T3.3**: Update `scripts/sync/all.sh` to source `scripts/sync/dagster.sh` + `scripts/sync/drift_docs.sh` (a thin wrapper that calls `mise run lint:drift-docs` and pipes the JSON report into the unified report)
- [ ] **T3.4**: Add `mise run sync:drift-docs` task to `mise.toml`; update `sync:dagster` task description to mention the new unified report

## Phase 4 — Per-spec AGENTS.md convention (4 tasks)

- [ ] **T4.1**: Create `openspec/specs/repo-hygiene-agent-routing/templates/spec-AGENTS.md.tmpl` (the canonical 6-section outline: routing sentence, quick start, key sources, adjacent specs, DO NOT, skill pointers; 30 lines max + the `<!-- generated: ISO date; do not hand-edit -->` footer)
- [ ] **T4.2**: Create `scripts/sync/spec_agents.py` — the generator. Walks `openspec/specs/`, reads each `spec.md` first line (the one-line purpose), emits a sibling `AGENTS.md` per spec if missing or older than its `spec.md`. Dry-run support via `--dry-run` flag
- [ ] **T4.3**: Run `uv run python scripts/sync/spec_agents.py` to bootstrap 78 per-spec `AGENTS.md` files; verify the 6-section outline is consistent across all 78 by spot-checking 5 (the 3 priority specs + 2 random picks)
- [ ] **T4.4**: Add the generator to `scripts/sync/all.sh` so `mise run sync:all` keeps the per-spec AGENTS.md files fresh

## Phase 5 — Cross-cutting anti-drift contract (4 tasks)

- [ ] **T5.1**: Create `scripts/lint_drift_docs.py` unit test (a sample AGENTS.md fixture with 3 mixed correct + 1 wrong claim; verify the lint flags the wrong one and exits 1)
- [ ] **T5.2**: Create `.github/workflows/lint-drift-docs.yaml` (install mise → `mise run lint:drift-docs` → fail on exit 1)
- [ ] **T5.3**: Create `.forgejo/workflows/lint-drift-docs.yaml` (the Forgejo mirror — same 8 lines, different runner hostname)
- [ ] **T5.4**: Update `scripts/registry_audit.py` to call `lint_drift_docs.py` as a step (the cross-cutting lint inherits the audit-pattern exit codes + JSON report structure)

## Phase 6 — Validation (3 tasks)

- [ ] **T6.1**: Run `openspec validate 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 --strict` and verify it exits 0 (the 4 spec deltas must all pass `--strict`)
- [ ] **T6.2**: Run `mise run lint:drift-docs` and verify it exits 0 (the post-change state passes the new lint)
- [ ] **T6.3**: Run `mise run sync:all` and verify it exits 0 in <60s on the M4 MacBook (the 7-layer orchestrator wires correctly)

## Phase 7 — Documentation (3 tasks)

- [ ] **T7.1**: Add a `## Priority sync commands` block to root `AGENTS.md` listing `mise run sync:all`, `mise run lint:drift-docs`, `mise run openspec:validate`
- [ ] **T7.2**: Update `openspec/AGENTS.md` priority-quick-reference to include the 3 new specs in the priority table
- [ ] **T7.3**: Run `./scripts/sync_agent_docs.sh` to refresh the README telemetry blocks per the agent-protocol Habit #4

## Phase 8 — Commit (1 task)

- [ ] **T8.1**: Commit all 28 files with the conventional message format:
  ```
  feat(repo-hygiene): drift lint + spec-AGENTS + cron (28 files, 4 phases)

  Implements the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1
  openspec change. Adds:
  - mise run lint:drift-docs (Phase 2)
  - 5 per-area AGENTS.md (orchestration/ baml_src/ meaisinfhoghlaim/ notebooks/ web/)
  - 78 per-spec AGENTS.md (Phase 4)
  - 4 spec deltas (repo-hygiene-agent-routing, centralize-cross-cutting-docs,
    knowledge-sync-loop +1 Layer 6 req, infrastructure-stacks +1 req)
  - Daily sync_health cron (Phase 3)
  - 2 CI workflows (Phase 5)

  Validates: openspec validate --strict, lint:drift-docs, sync:all.
  ```
