# 2026-07-25-flatten-notebooks-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Changes 1, 2, 3 merged on `feat/iac-ify-arm1-oci-control-plane`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`
- [ ] Read `marimo_dashboards/06_per_subject_analytics.py` for the
  parameterised-by-subject pattern

## Stage 1 — Create the 7-tab grouped LC panel

- [ ] CREATE `notebooks/40_leaving_cert_subject_panel.py` (~650 LOC)
  - Import `from nb_utils import connect_md, BIEP_SUBJECTS`
  - 7 tabs via `mo.ui.tabs([...])`:
    1. Mathematics
    2. Chemistry
    3. Geography
    4. Gaeilge (bilingual EN+GA)
    5. English (bilingual EN/GA)
    6. Computer Science
    7. EN/GA Comparison
  - Each tab queries the per-subject LC LanceDB table via `connect_md()`
  - `## KCG patterns used` docstring block at the top

## Stage 2 — Delete the 7 LC notebooks

- [ ] DELETE `notebooks/leaving_cert/chemistry.py`
- [ ] DELETE `notebooks/leaving_cert/computer_science.py`
- [ ] DELETE `notebooks/leaving_cert/english.py`
- [ ] DELETE `notebooks/leaving_cert/gaeilge.py`
- [ ] DELETE `notebooks/leaving_cert/geography.py`
- [ ] DELETE `notebooks/leaving_cert/mathematics.py`
- [ ] DELETE `notebooks/leaving_cert/06_en_vs_ga_comparison.py`
- [ ] (Keep `notebooks/leaving_cert/` directory empty for now — Change 5
  deletes the stale `03_leaving_cert/` subtree inside it)

## Stage 3 — Flatten 168 other notebooks

For each notebook in the 20 subdirectories (excluding the 7 LC files
deleted in Stage 2):
- [ ] Move + rename to top-level `<area>_<NN>_<topic>.py`
- [ ] Update the `## KCG patterns used` docstring with the new path
- [ ] Replace any `duckdb.connect(...)` calls with `nb_utils.connect_md()`
- [ ] Update the `--subject chemistry` CLI flag (if any) to reflect the
  new grouped panel location
- [ ] Verify `marimo edit <new_path>` opens the notebook correctly

## Stage 4 — Update docs

- [ ] UPDATE `notebooks/README.md` — rewrite the area table for the
  flat layout (17 top-level categories instead of 21 subdirectories)
- [ ] UPDATE `notebooks/LEGACY_ALIASES.md` — add the v8-flatten entry
  with all 168 old-path → new-path aliases

## Stage 5 — Verify the layout

- [ ] `find notebooks -mindepth 1 -maxdepth 1 -type d` — exactly 2 dirs:
  `_shared/` + `legacy/`
- [ ] `ls notebooks/` — exactly 17 top-level `.py` notebooks
- [ ] `grep -r "duckdb\.connect(" notebooks/ | grep -v _shared` — zero matches
- [ ] `grep -r "KCG patterns used" notebooks/` — every notebook has it

## Stage 6 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-25-flatten-notebooks-v1/specs/oideachais-marimo-dashboards/spec.md`
  with 2 new requirements (flat layout + 7-tab LC panel)
- [ ] Run `openspec validate 2026-07-25-flatten-notebooks-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-25-flatten-notebooks-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-25-flatten-notebooks-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/notebooks/v8-flatten.md` with the migration notes
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol