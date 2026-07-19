# Tasks: 2026-07-19-fix-cianchoghlaim-typo-v1

> Note: the change-id folder name intentionally retains the typo token
> `cianchoghlaim` to make the change self-documenting in `openspec list`
> and search.

## Phase 0 — Pre-flight (10 min)

- [x] 0.1 Snapshot fresh grep count: `rg -ci cianchoghlaim .` (baseline = 3,633 across 176 files)
- [x] 0.2 Confirm `.cocoindex_code/` is gitignored + regenerated lazily

## Phase 1 — Package metadata (T1, 15 min)

- [x] 1.1 `pyproject.toml:2` — `name = "cianchoghlaim"` → `name = "cianfhoghlaim"`
- [x] 1.2 `pyproject.toml:75-2819` — rewrite all `cianchoghlaim/...` `force-include` mappings to `cianfhoghlaim/...` (~3,270 lines)
- [x] 1.3 `dg.toml:23` — `code_location_name = "cianchoghlaim"` → `"cianfhoghlaim"`
- [x] 1.4 `dg.toml:19` — comment `cianchoghlaim.assets.definitions` → `cianfhoghlaim.assets.definitions`
- [x] 1.5 `mise.toml:154-155` — rewrite comment block (historical path references the old sub-directory; preserve semantics)
- [x] 1.6 `cli.py:56,58` — `cianchoghlaim.orchestration` → `cianfhoghlaim.orchestration`; `cianchoghlaim-cocoindex` → `cianfhoghlaim-cocoindex`
- [x] 1.7 `clio.py:5` — rewrite docstring

## Phase 2 — Dagger module rename (T1, 20 min)

- [x] 2.1 `git mv bonneagar/dagger/cianchoghlaim_dagger bonneagar/dagger/cianfhoghlaim_dagger`
- [x] 2.2 In `bonneagar/dagger/cianfhoghlaim_dagger/__init__.py`: rename class `CianchoghlaimDagger` → `CianfhoghlaimDagger` (1 class def + 3 `__all__`/docstring refs across 1473 lines)
- [x] 2.3 `bonneagar/dagger/pyproject.toml`: `name`, `main_object`, `packages` fields
- [x] 2.4 `bonneagar/dagger/dagger.json:2` — `"name": "cianchoghlaim_dagger"` → `"cianfhoghlaim_dagger"`
- [x] 2.5 `bonneagar/dagger/README.md` — rewrite 4 occurrences
- [x] 2.6 `bonneagar/dagger/templates/{secrets,secrets.data,secrets.web}.env.template` — rewrite `# rendered-by:` header
- [x] 2.7 `tests_pkg_temp/test_openspec_compliance.py:12` — fix dagger dir reference

## Phase 3 — CocoIndex docstrings (T2, 10 min)

- [x] 3.1 Bulk rewrite 70+ `cocoindex/**/__init__.py` files via the case-preserving fix script

## Phase 4 — Agent prompts (T2, 5 min)

- [x] 4.1 `opencode.json` — rewrite the typo in all 7 subagent prompts

## Phase 5 — Skills (T2, 15 min)

- [x] 5.1 `.agents/skills/dlt/SKILL.md` — path comment
- [x] 5.2 `.agents/skills/motherduck/SKILL.md` — `md:cianchoghlaim` → `md:cianfhoghlaim`
- [x] 5.3 `.agents/skills/agent-observability/SKILL.md` + `references/ingestion/INGESTION.md` — docker ps filter
- [x] 5.4 `.agents/skills_backup/kcg-infrastructure-audit/SKILL.md` — 2 occurrences
- [x] 5.5 `.agents/skills_backup/kcg-locket-sidecar/SKILL.md` — bulk rewrite (~11 occurrences)
- [x] 5.6 Plus 6 additional skill files discovered during the script run:
  `.agents/skills/INDEXING_AND_COGNITION.md`,
  `.agents/skills/agent-fleet-orchestration/SKILL.md`,
  `.agents/skills/agno/SKILL.md`,
  `.agents/skills/cocoindex/SKILL.md`,
  `.agents/skills/dagster/SKILL.md`,
  `.agents/skills/google-adk/SKILL.md`,
  `.agents/skills/marimo/references/ai-chat.md`,
  `.agents/skills/pangolin/SKILL.md`

## Phase 6 — OpenSpec (T2, 20 min)

- [x] 6.1 `openspec/specs/infrastructure-stacks/spec.md` — 3 refs
- [x] 6.2 `openspec/specs/agent-platform-cluster/spec.md` — 2 refs
- [x] 6.3 `openspec/specs/dagster-5-layer-component-architecture/spec.md` — 2 refs
- [x] 6.4 `openspec/changes/2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow/specs/agent-platform-cluster/spec.md`
- [x] 6.5 `openspec/changes/2026-08-04-skill-and-mcp-migration-v1/{proposal,tasks}.md`
- [x] 6.6 `openspec/research/2026-06-28-browserbase-program-2/agent-22-openchamber.md`
- [x] 6.7 All `openspec/changes/archive/**/{proposal,tasks,spec}.md` (~25 files)

## Phase 7 — Docs (T2, 10 min)

- [x] 7.1 `docs/stacks/{pangolin,backrest,komodo,infisical}.md` — bridge network sentence
- [x] 7.2 `docs/lakehouse/deployment-status-2026-07-19.md` — PG DB + `.pth` file ref
- [x] 7.3 `docs/p3-skill-mcp-migration-status.md` — `sruth/cianchoghlaim/` grep pattern
- [x] 7.4 `web/apps/croilar-web/README.md` — 2 dagger module refs

## Phase 8 — Root files (T1, 5 min)

- [x] 8.1 `clio.py:5` (done in Phase 1)
- [x] 8.2 `tests_pkg_temp/test_openspec_compliance.py:12` (done in Phase 2)
- [x] 8.3 `.github/workflows/skill-refs-check.yaml:12` — fix regex

## Phase 9 — Runtime identifiers (T3, 30 min edits)

- [x] 9.1 **DLT sources** (`dlt_sources/__init__.py`, `dlt_sources/common/destinations_*.py`, `dlt_sources/british_isles/_cross/registry_api.py`, `dlt_sources/british_isles/_cross/registry_loader.py`)
- [x] 9.2 **Scripts** (`scripts/setup_local_ducklake_registry.py`, `scripts/verify_ducklake_population.py`, `scripts/export_cohorts_to_lance.py`, `scripts/run_all_jurisdiction_pipelines.py`, `scripts/dev.sh`, `scripts/8_jurisdiction_overview.py`, `scripts/fix_v7_imports.py`)
- [x] 9.3 **Bonneagar** (`bonneagar/__init__.py`, `bonneagar/GOLD_STANDARD.md`, `bonneagar/komodo/stacks/openchamber-arm1-oci.toml`, `bonneagar/komodo/procedures/{deploy-logfire,deploy-lancedb}-bunchloch.toml`)
- [x] 9.4 **Docker Compose** (12 stacks): `oideachais/{compose,pangolin,sidecar}.yaml` + README; `openchamber/{compose,compose.dev}.yaml` + `.env.example` + README; `openclaw/{compose,compose.dev}.yaml`; `hermes/{compose,compose.dev}.yaml` + README; `langfuse/compose.dev.yaml`; `wave2/{letta,siyuan,mealie,outline,khoj,immich,kavita}/compose.yaml`

## Phase 10 — Runtime data migration (T3, 60 min — operator only)

Execute the operator runbook from the proposal's "Runtime migration" section:

- [ ] 10.1 Stop affected stacks
- [ ] 10.2 Recreate the network `cianfhoghlaim` + volume `cianfhoghlaim_locket_secrets`
- [ ] 10.3 `ALTER DATABASE ducklake_cianchoghlaim RENAME TO ducklake_cianfhoghlaim` + rewrite the `ducklake_metadata.ducklake_schema` rows
- [ ] 10.4 Mirror `s3://ducklake-cianchoghlaim/` → `s3://ducklake-cianfhoghlaim/` via `mc mirror`
- [ ] 10.5 Update Infisical `dev-baile` entries
- [ ] 10.6 Restart every stack; verify `docker network ls | grep cianfhoghlaim` + `docker volume ls | grep cianfhoghlaim_locket_secrets`

## Phase 11 — Validation

- [x] 11.1 `rg -i cianchoghlaim .` returns **0 matches** in tracked files
- [x] 11.2 `openspec validate 2026-07-19-fix-cianchoghlaim-typo-v1 --strict` passes
- [ ] 11.3 `mise run lint:skills` (53/53 still pass — to be verified)
- [ ] 11.4 `bun run validate-stacks` (GOLD_STANDARD compliance — to be verified)
- [ ] 11.5 `uv sync` + `python -c "import cianfhoghlaim.cli; print(cianfhoghlaim.cli.main.__module__)"` (to be verified)
- [ ] 11.6 `dg list defs` (Dagster code-location loads under new name — to be verified)
- [ ] 11.7 `git push`
- [ ] 11.8 `openspec archive 2026-07-19-fix-cianchoghlaim-typo-v1 --yes`
