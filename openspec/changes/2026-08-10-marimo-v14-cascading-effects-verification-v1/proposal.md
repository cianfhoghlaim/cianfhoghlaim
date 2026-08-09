# Change: Marimo v14 cascading effects verification + fixes

## Why

The 2026-08-10 marimo-v14 refactor trilogy (the Ireland+England flagship,
the Tier 3 grouped consolidation, the sync-health consolidation) was a
**partial refactor** that correctly created 3 helper modules
(`marimo_patterns.py`, `area_shims/biiep_v3_dashboard.py`,
`ragas_gauge.py`) + 2 educative notebooks + 9 BIEP jurisdiction
dashboards + 7 Tier 3 grouped dashboards + 1 sync_health.py + 17 mise
tasks — but it **failed to cascade** to:

1. **CI workflows** — 0 of 8 relevant workflows now run `marimo check`
   or `biep:v3:*:gate` (the refactor is invisible to CI)
2. **PEP 723 / `__generated_with`** — 30+ notebooks still on the OLD
   PEP 723 deps (16 BIEP lakehouse explorers + 7 official-media + 2
   Tier-4 + the `24_deployment_control_panel.py` regression)
3. **Spec drift** — 4 ADDED Requirements from the BIEP v3 proposal are
   missing from the canonical `cianfhoghlaim-marimo-dashboards/spec.md`;
   4 sync-loop specs reference deprecated sub-dashboards
4. **Skill drift** — 5 of 8 skill files reference the deprecated
   sub-dashboards (29_agents, 30_notebooks, 27_stacks, 25_dagster,
   26_baml); 3 don't mention any new helper modules
5. **Doc drift** — `notebooks/AGENTS.md` claims 108 notebooks (actual:
   53 + 13 shared) + references the legacy `nb_utils.py` as canonical;
   `README.md` doesn't mention the 3 openspec changes or any of the
   new gates
6. **Mise tasks** — 2 broken (`biep:v3:m-aistear`, `biep:v3:m-primary`
   point to non-existent scripts); 7 missing (`*:check` variants for
   the 7 grouped dashboards); the `marimo_wasm_export.py` only exports
   7 hardcoded dashboards (not the 7 grouped + sync_health)
7. **Scripts** — `notebooks/cli.py` **broken post-v7** (NB_ROOT.parents[2]
   should be parents[1]); `notebooks/nb_utils.py` overlapping;
   `notebooks/LEGACY_ALIASES.md` stale; `notebooks/__init__.py` doesn't
   re-export the new helpers; `scripts/cianfhoghlaim-cli.ts` has no
   `notebook:check` subcommand
8. **OpenSpec archive** — all 3 v14 changes are still pending
   (0/93, 0/107, 0/36 tasks) — should be archived after this change
   closes the cascading effects gap

This change implements a **single combined change** (per user decision)
with 100+ tasks across 8 sub-domains + a dedicated 40-notebook end-to-end
CLI verification matrix + 11 doc/skill/spec updates + CI gate addition.

## What changes

### Phase 1 — Pre-flight baseline (0.5 day)
- `stedding/cascading-baseline-2026-08-08.md` (the baseline snapshot)

### Phase 2 — Fix the 2 broken mise tasks (0.5 day)
- DELETE `[tasks."biep:v3:m-aistear"]` + `[tasks."biep:v3:m-primary"]`
  from `mise.toml` (both point to non-existent `scripts/m_aistear.py` +
  `scripts/m_primary.py`)
- Update `openspec/changes/2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1/tasks.md`
  to mark the deleted tasks as `replaced by the dual-mode CLI gate`

### Phase 3 — Fix `notebooks/cli.py` + `__init__.py` + `LEGACY_ALIASES.md` (1 day)
- Rewrite `notebooks/cli.py` for the post-v7 flat layout
  (NB_ROOT.parents[1] + flat glob + drop the 12-entry GROUPS tuple)
- Rewrite `notebooks/__init__.py` to re-export the 3 new v14 helpers
- Add `@deprecated` docstring to `notebooks/nb_utils.py` (kept as back-compat)
- DELETE `notebooks/LEGACY_ALIASES.md` (stale pre-v7 docs)

### Phase 4 — Fix `01_overview_setup.py` + `ie_law_explorer.py` (1 day)
- Rewrite `01_overview_setup.py` to use `setup_biep_registry_header()`
  + `cli_main_if_argv()` + bump PEP 723 to v14
- Rewrite `ie_law_explorer.py` to drop the `from nb_utils import` +
  use `connect_md` + bump PEP 723 to v14 + add `_cli_main()`

### Phase 5 — Fix the 7 `13_official_media_*.py` PEP 723 blocks (1 day)
- Bump all 7 to v14 (`marimo>=0.13` + `anywidget>=0.9` +
  `traitlets>=5.14`)
- Add the missing PEP 723 block to `13_official_media_01_official_media.py`
- Fix the `__generated_with_marimo__` typo on
  `13_official_media_02_email_inbox_triage.py`

### Phase 6 — Bump PEP 723 on the 16 BIEP lakehouse explorers (1 day)
- Add `anywidget>=0.9, traitlets>=5.14` to all 16 PEP 723 blocks
  (per user decision: bump all 16 unconditionally)
- Add the missing PEP 723 blocks to the 3 that don't have them
- Bump `__generated_with = "0.14.10"` on all 17 (where missing)

### Phase 7 — Restore `24_deployment_control_panel.py` PEP 723 block (0.25 day)
- Prepend the PEP 723 block (regression fix from the refactor)

### Phase 8 — Add 7 missing `biep:v3:marimo:<domain>:check` mise tasks (0.5 day)
- Add 7 new tasks for the 7 grouped dashboards (`meaisin`,
  `celtic`, `corpus`, `speedrun`, `academic`, `irish_law`, `sync`)
- Add a combined `biep:v3:marimo:grouped:check` task

### Phase 9 — Update `scripts/marimo_wasm_export.py` (0.5 day)
- Rewrite `DASHBOARD_NOTEBOOKS` to include all 16 refactored dashboards
  (the 6 BIEP v3 + 23 + 24 + 26 + 27 + 40 + 7 grouped + sync_health)
- Delete the stale `default="notebooks/leaving_cert/03_leaving_cert"`
  comment

### Phase 10 — Update `scripts/cianfhoghlaim-cli.ts` (0.5 day)
- Add `notebook:check` subcommand (dispatches to
  `mise run biep:v3:marimo:all`)
- Add `notebook:gate --milestone=mN --jurisdiction=<j>` subcommand
  (dispatches to `mise run biep:v3:<jurisdiction>:gate`)
- Add `notebook:wasm-export` subcommand (dispatches to
  `mise run biep:v3:marimo:wasm:export`)
- Update the help text

### Phase 11 — Cascade doc + skill + spec updates (1.5 days)
- Update `notebooks/AGENTS.md` (108 → 53 + 13 shared; nb_utils → 3 new
  helpers; add the dual-mode CLI docs)
- Update `README.md` (root) (LITELLM_BASE_URL + 3 openspec changes +
  new gates)
- Update 11 openspec specs (fold the 4 ADDED Requirements into
  `cianfhoghlaim-marimo-dashboards/spec.md`; fix 4 sync-loop spec
  stale references)
- Update 8 skill files (5 sync-loop skills → `sync_health.py`;
  3 skills → 3 new helper modules)

### Phase 12 — Add CI gate + archive the 3 openspec changes (0.5 day)
- Add `marimo-lint` job to `.github/workflows/ci.yaml`
- Add `marimo check` to `.github/workflows/marimo-wasm-publish.yaml`
- Update `.github/workflows/openspec-validate.yaml`
- Re-run `mise run sync:notebooks` to refresh the stale report
- Run `openspec archive` on the 3 v14 changes (Ireland+England
  flagship + Tier 3 + sync_health)
- Final `mise run lint:*` pass (all 3 must be green)

## Out of scope

- The 6 BIEP v3 jurisdiction dashboards themselves (already refactored)
- The 17 BIEP lakehouse explorers' content (only the PEP 723 blocks)
- The 7 Tier 3 grouped dashboards + sync_health content (already done)
- Cross-repo changes (`leabharlann/` is read-only consumer)
- New features (only fixes + cascading updates)

## Dependencies

```markdown
## Dependencies

`Blocked by (soft): 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1` +
`2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1` +
`2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1` — the
3 v14 changes that this verification closes the cascading effects
gap for.

`Blocked by (soft): 2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1` —
the Aistear + Primary rollout that left the 2 broken mise tasks.

`Affected repos: cianfhoghlaim`
```

## Impact

- **Affected specs**: `cianfhoghlaim-marimo-dashboards/spec.md` (4 ADDED Requirements
  folded in) + 10 other specs (references updated)
- **Affected code/config**:
  - `mise.toml` (2 broken tasks deleted + 8 new tasks added)
  - `notebooks/cli.py` (rewritten post-v7)
  - `notebooks/__init__.py` (rewritten to re-export 3 new helpers)
  - `notebooks/LEGACY_ALIASES.md` (deleted)
  - `notebooks/nb_utils.py` (marked @deprecated)
  - `notebooks/01_overview_setup.py` (refactored to v14)
  - `notebooks/ie_law_explorer.py` (refactored to v14)
  - 7 `notebooks/13_official_media_*.py` (PEP 723 bumped)
  - 16 `notebooks/10_biep_pipeline_lakehouse_*.py` (PEP 723 bumped)
  - `notebooks/24_deployment_control_panel.py` (PEP 723 restored)
  - `scripts/marimo_wasm_export.py` (DASHBOARD_NOTEBOOKS rewritten)
  - `scripts/cianfhoghlaim-cli.ts` (3 new subcommands added)
  - 3 `.github/workflows/*.yaml` files (CI gate added)
  - `notebooks/AGENTS.md` + `README.md` (root) (doc cascade)
  - 8 `.agents/skills/*/SKILL.md` files (skill cascade)
  - 10 `openspec/specs/*/spec.md` files (spec cascade)
- **LOC saved/gained**: ~1,800 LOC of cleanups + ~400 LOC of new CI/doc/skill text
- **No secret values written to disk**: all `infisical://dev-baile/...`
  refs hydrated by mise + Locket

## Cross-references

- `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md` — the
  capability this change extends (4 ADDED Requirements folded in)
- `openspec/specs/british-isles-education-pipeline-v3/spec.md` — the
  BIEP v3 spec that drives the dashboard layout
- `openspec/specs/centralized-model-registry/spec.md` — the
  litellm proxy + `model_for()` helper (referenced for P3)
- `openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/`
  — the flagship change this verifies
- `openspec/changes/2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1/`
  — the Tier 3 change this verifies
- `openspec/changes/2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1/`
  — the sync_health change this verifies
- `openspec/changes/2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1/`
  — the 4-stage rollout with the 2 broken tasks
- `notebooks/_shared/marimo_patterns.py` — the canonical v14 helpers
- `notebooks/_shared/area_shims/biiep_v3_dashboard.py` — the R2/R3
  dashboard builder
- `notebooks/_shared/ragas_gauge.py` — the P5 RAGAS gauge widget
- `.agents/skills/marimo/SKILL.md` — the marimo skill (cascaded)
- `.agents/skills/centralized-registry/SKILL.md` — the registry skill
  (cascaded)
- `.agents/skills/{agents,notebooks,stacks,dagster-asset,baml-schema}-sync/SKILL.md`
  — the 5 sync-loop skills (cascaded to `sync_health.py`)
- https://docs.marimo.io/guides/scripts/ — the canonical dual-mode
  CLI pattern