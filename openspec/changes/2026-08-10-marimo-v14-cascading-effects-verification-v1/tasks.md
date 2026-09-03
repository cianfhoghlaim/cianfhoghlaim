# Tasks: Marimo v14 cascading effects verification + fixes

> **Phase plan**: 12 phases, ~12 days work.
> **Branch**: `token-plan-lc-pipeline-2026-08` (current working branch).
> **OpenSpec change**: `2026-08-10-marimo-v14-cascading-effects-verification-v1`.

## Phase 1 — Pre-flight baseline capture (0.5 day)

### T1.1 — Run all 3 quality gates

- [ ] Run `mise run lint:skills` — confirm 61 skills pass.
- [ ] Run `mise run lint:registry` — confirm 0 hardcoded model strings.
- [ ] Run `mise run lint:drift-docs` — confirm 0 number drift claims.

### T1.2 — Capture the notebooks-sync report

- [ ] Run `mise run sync:notebooks` if it exists; else inspect
  `stedding/sync-reports/notebooks-2026-07-30.md`.

### T1.3 — Capture the openspec state

- [ ] Run `openspec list --specs > /tmp/before-specs.txt`.
- [ ] Run `openspec list > /tmp/before-changes.txt`.

### T1.4 — Verify all 3 v14 openspec changes validate --strict

- [ ] Run `openspec validate 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 --strict` — expect VALID.
- [ ] Run `openspec validate 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1 --strict` — expect VALID.
- [ ] Run `openspec validate 2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1 --strict` — expect VALID.

### T1.5 — Capture the current mise.toml biep:v3 section

- [ ] Run `grep -A 5 'biep:v3:marimo' mise.toml > /tmp/before-mise.txt`.

### T1.6 — Write the baseline snapshot

- [ ] Write `stedding/cascading-baseline-2026-08-08.md` containing the 5 captured artifacts + the current openspec status.

## Phase 2 — Fix the 2 broken mise tasks (0.5 day)

### T2.1 — Delete the 2 broken mise tasks

- [ ] Open `mise.toml` and DELETE lines for `[tasks."biep:v3:m-aistear"]` +
  `[tasks."biep:v3:m-primary"]` (they point to non-existent scripts).

### T2.2 — Verify the dual-mode CLI gates work

- [ ] Run `mise run biep:v3:aistear:gate` — expect exit code 0 (deferred status for the Aistear pipeline).
- [ ] Run `mise run biep:v3:primary:gate` — expect exit code 0.

### T2.3 — Update the Aistear + Primary tasks doc

- [ ] Open `openspec/changes/2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1/tasks.md`.
- [ ] Find the task entries for `scripts/m_aistear.py` + `scripts/m_primary.py` and mark them as
  `deleted (replaced by the dual-mode CLI gate)`.

## Phase 3 — Fix notebooks/cli.py + __init__.py + LEGACY_ALIASES.md (1 day)

### T3.1 — Rewrite notebooks/cli.py for the post-v7 flat layout

- [ ] Open `notebooks/cli.py`.
- [ ] Fix line 32: `NB_ROOT = Path(__file__).resolve().parents[2]` →
  `parents[1]`.
- [ ] DELETE the 12-entry `GROUPS` tuple (lines 39-86) — it references
  pre-v7 numbered subdirs that don't exist.
- [ ] REPLACE the `find_notebook` function (lines 89-130) with a flat glob:
  ```python
  def find_notebook(name: str) -> Path | None:
      """Find a notebook by name in the post-v7 flat layout."""
      matches = list(NB_ROOT.glob(f"{{0*_,*}}/{name}.py"))
      matches = [m for m in matches if "legacy" not in str(m)]
      return matches[0] if matches else None
  ```
- [ ] REPLACE the `list_notebooks` function (lines 133-153) to use the
  flat layout (filter out legacy + shared + cli + nb_utils).

### T3.2 — Rewrite notebooks/__init__.py to re-export the new v14 helpers

- [ ] Open `notebooks/__init__.py` (68 LOC).
- [ ] Add the re-exports from `notebooks._shared.marimo_patterns` +
  `notebooks._shared.area_shims.biiep_v3_dashboard` +
  `notebooks._shared.ragas_gauge` + `notebooks._shared.area_shims.leaving_cert`
  (per the §11 of the plan).

### T3.3 — Mark notebooks/nb_utils.py as @deprecated

- [ ] Open `notebooks/nb_utils.py`.
- [ ] Add a `@deprecated` docstring at the top:
  ```
  """DEPRECATED — kept for back-compat only.

  New code should use notebooks._shared.marimo_patterns (P1-P6 + R1 helpers).
  This module will be removed once notebooks/01_overview_setup.py +
  notebooks/ie_law_explorer.py (the only remaining consumers) are refactored.
  """

  import warnings
  warnings.warn(
      "notebooks.nb_utils is deprecated; use notebooks._shared.marimo_patterns instead",
      DeprecationWarning,
      stacklevel=2,
  )
  ```

### T3.4 — Delete notebooks/LEGACY_ALIASES.md

- [ ] Run `git rm notebooks/LEGACY_ALIASES.md`.

### T3.5 — Verify Phase 3

- [ ] Run `python3 -c "from notebooks import list_active_notebooks; print(len(list_active_notebooks()))"` — expect 53.
- [ ] Run `python3 -c "from notebooks import build_biep_v3_dashboard, setup_biep_registry_header; print(build_biep_v3_dashboard, setup_biep_registry_header)"` — expect both function objects.

## Phase 4 — Fix 01_overview_setup.py + ie_law_explorer.py (1 day)

### T4.1 — Rewrite notebooks/01_overview_setup.py

- [ ] Open `notebooks/01_overview_setup.py`.
- [ ] Update the PEP 723 block (lines 1-6):
  ```
  # /// script
  # requires-python = ">=3.12"
  # dependencies = [
  #   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
  #   "anywidget>=0.9", "traitlets>=5.14",
  # ]
  # ///
  ```
- [ ] Replace the 14-line try/except header (lines 41-66) with `_ctx = setup_biep_registry_header()`.
- [ ] Update `__generated_with = "0.13.0"` → `"0.14.10"`.
- [ ] Replace the hand-rolled dual-mode CLI guard (lines 371-376) with `cli_main_if_argv(_cli_main, app)`.
- [ ] Add an LLM tab via `llm_chat_with_prompts()`.

### T4.2 — Rewrite notebooks/ie_law_explorer.py

- [ ] Open `notebooks/ie_law_explorer.py`.
- [ ] Update the PEP 723 block:
  ```
  # /// script
  # requires-python = ">=3.12"
  # dependencies = [
  #   "marimo>=0.13", "duckdb>=1.0", "ibis-framework[duckdb]>=9.0", "pandas>=2.2",
  #   "altair>=5.0", "pyarrow>=15", "anywidget>=0.9", "traitlets>=5.14",
  # ]
  # ///
  ```
- [ ] DELETE the `sys.path.insert(0, str(repo_root))` hack (lines 73-75).
- [ ] REPLACE `from nb_utils import connect_biep_lakehouse` (line 78) with `from notebooks._shared.db import connect_md`.
- [ ] DELETE the 14-line try/except header block, REPLACE with `_ctx = setup_biep_registry_header()`.
- [ ] Add `_cli_main()` + `if __name__ == "__main__":` block.

### T4.3 — Verify Phase 4

- [ ] Run `uv run marimo check notebooks/01_overview_setup.py` — expect 0 errors.
- [ ] Run `uv run marimo check notebooks/ie_law_explorer.py` — expect 0 errors.

## Phase 5 — Fix the 7 13_official_media_*.py PEP 723 blocks (1 day)

### T5.1 — Update all 7 PEP 723 blocks

For each of the 7 `notebooks/13_official_media_*.py` files:
- [ ] Replace the PEP 723 block with:
  ```
  # /// script
  # requires-python = ">=3.12"
  # dependencies = [
  #   "marimo>=0.13", "duckdb>=1.0", "ibis-framework[duckdb]>=9.0", "pandas>=2.2",
  #   "altair>=5.0", "pyarrow>=15", "anywidget>=0.9", "traitlets>=5.14",
  # ]
  # ///
  ```

### T5.2 — Fix the 13_official_media_01_official_media.py missing PEP 723 block

- [ ] Prepend the PEP 723 block (this file has NO PEP 723 block currently).

### T5.3 — Fix the 13_official_media_02_email_inbox_triage.py __generated_with typo

- [ ] Replace `__generated_with_marimo__ = "0.9.0"` with `__generated_with = "0.14.10"`.

### T5.4 — Verify Phase 5

- [ ] Run `uv run marimo check notebooks/13_official_media_*.py` — all 7 pass.

## Phase 6 — Bump PEP 723 on the 16 BIEP lakehouse explorers (1 day)

### T6.1 — Update all 16 BIEP lakehouse explorers' PEP 723 blocks

For each of the 16 `notebooks/10_biep_pipeline_lakehouse_*.py` files (excluding
the already-bumped `01_ducklake_explorer.py`):
- [ ] Add `anywidget>=0.9, traitlets>=5.14` to the PEP 723 deps list.
- [ ] Update `__generated_with = "0.13.0"` → `"0.14.10"` (where applicable).

### T6.2 — Add the missing PEP 723 blocks

For `02_lakehouse_inspector.py` + `03_dlt_pipeline_overview.py` + `04_cocoindex_embedding_coverage.py`:
- [ ] Prepend the PEP 723 block (these 3 files have NO PEP 723 block currently).

### T6.3 — Verify Phase 6

- [ ] Run `uv run marimo check notebooks/10_biep_pipeline_lakehouse_*.py` — all 17 pass.
- [ ] Run `grep -L "anywidget>=0.9" notebooks/10_biep_pipeline_lakehouse_*.py` — expect 0 files.

## Phase 7 — Restore 24_deployment_control_panel.py PEP 723 block (0.25 day)

### T7.1 — Prepend the PEP 723 block

- [ ] Open `notebooks/24_deployment_control_panel.py`.
- [ ] Prepend the PEP 723 block (currently NO PEP 723 block; regression from the refactor):
  ```
  # /// script
  # requires-python = ">=3.12"
  # dependencies = [
  #   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
  #   "anywidget>=0.9", "traitlets>=5.14",
  # ]
  # ///
  ```

## Phase 8 — Add 7 missing biep:v3:marimo:<domain>:check mise tasks (0.5 day)

### T8.1 — Add the 7 new biep:v3:marimo:<domain>:check tasks

In `mise.toml`, AFTER the existing `biep:v3:marimo:irish_law:dev` task:
- [ ] Add `[tasks."biep:v3:marimo:meaisin:check"]` — runs `uv run marimo check notebooks/meaisin_ops_console.py`.
- [ ] Add `[tasks."biep:v3:marimo:celtic:check"]` — runs `uv run marimo check notebooks/celtic_languages.py`.
- [ ] Add `[tasks."biep:v3:marimo:corpus:check"]` — runs `uv run marimo check notebooks/corpus_overview.py`.
- [ ] Add `[tasks."biep:v3:marimo:speedrun:check"]` — runs `uv run marimo check notebooks/speedrun_mmo.py`.
- [ ] Add `[tasks."biep:v3:marimo:academic:check"]` — runs `uv run marimo check notebooks/academic_history.py`.
- [ ] Add `[tasks."biep:v3:marimo:irish_law:check"]` — runs `uv run marimo check notebooks/irish_law.py`.
- [ ] Add `[tasks."biep:v3:marimo:sync:check"]` — runs `uv run marimo check notebooks/sync_health.py`.

### T8.2 — Add the combined biep:v3:marimo:grouped:check task

- [ ] Add `[tasks."biep:v3:marimo:grouped:check"]` — runs `marimo check` on all 8 grouped dashboards in one shell command.

### T8.3 — Verify Phase 8

- [ ] Run `mise run biep:v3:marimo:meaisin:check` — expect exit code 0.
- [ ] Run `mise run biep:v3:marimo:sync:check` — expect exit code 0.

## Phase 9 — Update scripts/marimo_wasm_export.py (0.5 day)

### T9.1 — Rewrite DASHBOARD_NOTEBOOKS

- [ ] Open `scripts/marimo_wasm_export.py`.
- [ ] REPLACE the `DASHBOARD_NOTEBOOKS` list (line 119) with:
  ```python
  DASHBOARD_NOTEBOOKS = [
      "19_ireland_pipeline_dashboard",
      "20_england_pipeline_dashboard",
      "21_sct_wls_ni_pipeline_dashboard",
      "22_crown_dependencies_dashboard",
      "23_8_jurisdiction_overview",
      "24_deployment_control_panel",
      "26_aistear_dashboard",
      "27_primary_dashboard",
      "40_leaving_cert_subject_panel",
      "meaisin_ops_console",
      "celtic_languages",
      "corpus_overview",
      "speedrun_mmo",
      "academic_history",
      "irish_law",
      "sync_health",
  ]
  ```

### T9.2 — Delete the stale comment

- [ ] DELETE the stale `default="notebooks/leaving_cert/03_leaving_cert"` comment at line 119.

### T9.3 — Verify Phase 9

- [ ] Run `python3 scripts/marimo_wasm_export.py --dry-run` — expect 16 dashboards listed.

## Phase 10 — Update scripts/cianfhoghlaim-cli.ts (0.5 day)

### T10.1 — Add the notebook:check subcommand

- [ ] Open `scripts/cianfhoghlaim-cli.ts`.
- [ ] Add a new `notebook:check` case in the main switch statement (around line 60):
  ```typescript
  case "notebook:check": {
    await runMiseTask("biep:v3:marimo:all", nonInteractive);
    return { ok: true, action: "notebook:check", task: "biep:v3:marimo:all" };
  }
  ```

### T10.2 — Add the notebook:gate subcommand

- [ ] Add a new `notebook:gate` case:
  ```typescript
  case "notebook:gate": {
    const milestone = (argv.m ?? argv.milestone ?? "m1").toLowerCase();
    const jurisdiction = (argv.j ?? argv.jurisdiction ?? "ireland").toLowerCase();
    const task = `biep:v3:${jurisdiction}:gate`;
    await runMiseTask(task, nonInteractive, { milestone });
    return { ok: true, action: "notebook:gate", task, milestone };
  }
  ```

### T10.3 — Add the notebook:wasm-export subcommand

- [ ] Add a new `notebook:wasm-export` case:
  ```typescript
  case "notebook:wasm-export": {
    await runMiseTask("biep:v3:marimo:wasm:export", nonInteractive);
    return { ok: true, action: "notebook:wasm-export", task: "biep:v3:marimo:wasm:export" };
  }
  ```

### T10.4 — Update the help text

- [ ] Update the help text at line 15-31 to document the 3 new subcommands.

### T10.5 — Verify Phase 10

- [ ] Run `bun scripts/cianfhoghlaim-cli.ts notebook:check` — expect exit code 0.

## Phase 11 — Cascade doc + skill + spec updates (1.5 days)

### T11.1 — Update notebooks/AGENTS.md

- [ ] Open `notebooks/AGENTS.md`.
- [ ] Line 3: replace "108 active marimo notebooks" with "53 active marimo notebooks + 13 shared helpers".
- [ ] Line 20: verify `mise run notebook:list` works after Phase 3 fixes.
- [ ] Line 30: replace `nb_utils.py` reference with the 3 new v14 helper modules.
- [ ] Add a new section "v14 Helper Modules" documenting the 3 helper modules + their public symbols.
- [ ] Add a new section "Dual-mode CLI per https://docs.marimo.io/guides/scripts/" with the canonical `cli_argparser_biep` + `cli_main_if_argv` + `cli_payload_to_output` pattern.
- [ ] Document `LITELLM_BASE_URL`.
- [ ] Add the 7 Tier 3 grouped dashboards + sync_health to the inventory.

### T11.2 — Update README.md (root)

- [ ] Open `README.md`.
- [ ] Add a new section in "Centralized Registries" documenting `LITELLM_BASE_URL` + the 3 helper modules + the dual-mode CLI.
- [ ] Add a new section "Marimo v14 Refactor Trilogy" documenting the 3 openspec changes.
- [ ] Add `00_marimo_patterns_tour.py` to the "Quick start" commands.
- [ ] Add a "CI Gates" section documenting the 11 new `biep:v3:*:gate` + 7 new `biep:v3:marimo:<domain>:dev` mise tasks.

### T11.3 — Update openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md

- [ ] Add the 4 ADDED Requirements (per §11 of the plan):
  1. 8-cell BIEP v3 surface consolidates into `mo.ui.tabs`
  2. LLM-assisted analysis tab via `mo.ui.chat` + `mo.ai.llm`
  3. Dual-mode (marimo + CLI) per https://docs.marimo.io/guides/scripts/
  4. RAGAS gauge widget (anywidget)

### T11.4 — Update 10 other openspec specs

For each of:
- `british-isles-education-pipeline-v3/spec.md`
- `centralized-model-registry/spec.md`
- `deployment-control-panel/spec.md`
- `notebooks-sync-loop/spec.md`
- `knowledge-sync-loop/spec.md`
- `stacks-sync-loop/spec.md`
- `baml-sync-loop/spec.md`
- `agent-definitions-sync-loop/spec.md`
- `dagster-5-layer-component-architecture/spec.md`
- `centralized-schema-registry/spec.md`

- [ ] Update the references to the deprecated sub-dashboards + add references to `build_biep_v3_dashboard()` + `LITELLM_BASE_URL` + the new grouped dashboards + `sync_health.py`.

### T11.5 — Update 8 skill files

- [ ] Update `.agents/skills/marimo/SKILL.md` — add a "v14 Helper Modules" section.
- [ ] Update `.agents/skills/marimo/marimo-notebook/SKILL.md` — add a "Dual-mode CLI" section.
- [ ] Update `.agents/skills/centralized-registry/SKILL.md` — add a "Marimo v14 Helper Modules" section.
- [ ] Update `.agents/skills/agents-sync/SKILL.md` — replace line 58 reference to `sync_health.py`.
- [ ] Update `.agents/skills/notebooks-sync/SKILL.md` — replace line 57 reference to `sync_health.py`.
- [ ] Update `.agents/skills/stacks-sync/SKILL.md` — replace line 105 reference to `sync_health.py`.
- [ ] Update `.agents/skills/dagster-asset-sync/SKILL.md` — replace line 104 reference to `sync_health.py`.
- [ ] Update `.agents/skills/baml-schema-sync/SKILL.md` — replace line 80 reference to `sync_health.py`.

### T11.6 — Verify Phase 11

- [ ] Run `grep -L "RAGASGaugeWidget\|setup_biep_registry_header\|build_biep_v3_dashboard\|LITELLM_BASE_URL" .agents/skills/marimo/*.md .agents/skills/*/SKILL.md` — expect 0 files.
- [ ] Run `grep -L "sync_health" openspec/specs/*/spec.md` — expect 0 files.

## Phase 12 — Add CI gate + archive the 3 openspec changes (0.5 day)

### T12.1 — Add the marimo-lint job to .github/workflows/ci.yaml

- [ ] Open `.github/workflows/ci.yaml`.
- [ ] Add a new `marimo-lint` job:
  ```yaml
  marimo-lint:
    name: marimo lint
    runs-on: ubuntu-latest
    if: |
      contains(github.event.pull_request.changed_files, 'notebooks/') ||
      contains(github.event.pull_request.changed_files, 'mise.toml') ||
      contains(github.event.pull_request.changed_files, 'scripts/')
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v2
      - run: mise run biep:v3:marimo:all
      - run: mise run biep:v3:lint
  ```

### T12.2 — Add marimo check to .github/workflows/marimo-wasm-publish.yaml

- [ ] Open `.github/workflows/marimo-wasm-publish.yaml`.
- [ ] INSERT `mise run biep:v3:marimo:all` BEFORE the `python scripts/marimo_wasm_export.py` step.

### T12.3 — Update .github/workflows/openspec-validate.yaml

- [ ] Open `.github/workflows/openspec-validate.yaml`.
- [ ] Add a `marimo check` follow-up step for PRs that touch `openspec/changes/2026-08-10-*` files.

### T12.4 — Re-run the notebooks-sync orchestrator

- [ ] Run `mise run sync:notebooks` to generate a fresh `notebooks-2026-08-08.md` report.

### T12.5 — Archive the 3 v14 openspec changes

- [ ] Run `openspec archive 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 --yes`.
- [ ] Run `openspec archive 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1 --yes`.
- [ ] Run `openspec archive 2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1 --yes`.
- [ ] Run `openspec validate 2026-08-10-marimo-v14-cascading-effects-verification-v1 --strict` — expect VALID.

### T12.6 — Run all 3 quality gates

- [ ] Run `mise run lint:skills` — expect 61 skills pass.
- [ ] Run `mise run lint:registry` — expect 0 hardcoded model strings.
- [ ] Run `mise run lint:drift-docs` — expect 0 number drift claims.

### T12.7 — Update AGENTS.md + openspec/AGENTS.md

- [ ] Update the AGENTS.md spec count from 90 → 91 (this change adds 4 ADDED Requirements to cianfhoghlaim-marimo-dashboards/spec.md).
- [ ] Update openspec/AGENTS.md to reflect the 3 archived v14 changes.

## Acceptance gates

- [ ] All 40 notebooks parse + pass `marimo check`.
- [ ] All 11 docs/skills/specs are updated.
- [ ] All 3 quality gates are green.
- [ ] The 40-notebook CLI verification matrix produces a
  `stedding/cascading-cli-verification-2026-08-08.md` report with
  status for each notebook.
- [ ] All 4 openspec changes (this one + the 3 to archive) are valid.
- [ ] `mise run biep:v3:marimo:all` passes.
- [ ] `mise run biep:v3:lint` passes (no raw `duckdb.connect()` in any BIEP v3 path).
- [ ] No `nb_utils.py` or `LEGACY_ALIASES.md` references remain in active code.
- [ ] CI workflow now fails if any refactored notebook fails `marimo check`.