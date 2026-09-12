# Tasks: KCG Path References Port

## Stage 0 — Per-file replacement (no batching)

For each of the 12 live-code files below:

- [x] F1 — `bonneagar/iac/commands/bootstrap-control-plane.ts`
      (lines 87, 139) — replaced + grep-verified clean
- [x] F2 — `dlt_sources/filesystem/pdf_download_source.py`
      (line 69) — replaced (already used env-var indirection
      via `CIANFHOGHLAIM_ROOT`; just updated the fallback) +
      grep-verified clean
- [x] F3 — `dlt_sources/jobs/government_circulars_job.py`
      (line 42) — replaced (already used env-var indirection
      via `STEDDING_OIDE_DIR`) + grep-verified clean
- [x] F4 — `dlt_sources/british_isles/ireland/education/gov_ie_circulars.py`
      (line 96) — replaced (already used env-var indirection
      via `STEDDING_OIDE_DIR`) + grep-verified clean
- [x] F5 — `dlt_sources/british_isles/ireland/education/curriculumonline_syllabi.py`
      (line 255) — replaced + ADDED env-var indirection via
      `BIEP_SAMPLES_DIR` + grep-verified clean
- [x] F6 — `dlt_sources/british_isles/ireland/education/curriculum.py`
      (line 92) — replaced + ADDED env-var indirection via
      `BIEP_SAMPLES_DIR` + grep-verified clean
- [x] F7 — `dlt_sources/british_isles/england/education/gcse/england_gcse_sources.py`
      (line 140) — replaced (already used env-var indirection
      via `STEDDING_INGEST_QUEUE`) + grep-verified clean
- [x] F8 — `dlt_sources/british_isles/england/education/a_level/england_a_level_sources.py`
      (line 139) — replaced (already used env-var indirection
      via `STEDDING_INGEST_QUEUE`) + grep-verified clean
- [x] F9 — `orchestration/defs/2_materials/lc_extraction/lc_subjects.py`
      (lines 103, 252, 264) — replaced 3 occurrences
      (STEDDING_INGEST_QUEUE fallback, scripts/load_lc_chemistry_pilot.py,
      .venv/bin/python3) + grep-verified clean
- [x] F10 — `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/lineage-registry.ts`
      (~109 pdf_path entries) — bulk-replaced + 5/5 spot-checked
      files EXIST on disk + grep-verified clean
- [x] F11 — `cocoindex_flows/corpus/unified_embedding.py`
      (line 122) — replaced (already used env-var indirection
      via `UNIFIED_DUCKDB_CONNECTION`) + grep-verified clean;
      fallback points at `crypteolas/storage/data/ducklake.ducklake`
      which does NOT exist on disk (acceptable: the env var
      `UNIFIED_DUCKDB_CONNECTION` always overrides this in real
      usage; the fallback is just a default)
- [x] F12 — `web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/design-system-server.py`
      (line 19, docstring) — replaced in docstring; the
      referenced skill path `/Users/.../mcp-apps-builder/SKILL.md`
      does NOT exist on disk (acceptable: this is a docstring,
      not runtime code, and the skill has been removed/renamed in
      the current `.agents/skills/` tree)

## Stage 1 — Spec delta

- [x] T1.1 — Add MODIFIED requirement to
      `openspec/changes/2026-09-12-kcg-port-path-references-v1/specs/infrastructure-stacks/spec.md`
      extending the "Identical absolute repository mount" requirement
      with a sub-requirement that all canonical source paths SHALL be
      expressed relative to `/Users/cianmacandeisigh/dev/cianfhoghlaim`
      (the canonical post-v7 host repository root).

## Stage 2 — Validation

- [x] T2.1 — Run
      `openspec validate 2026-09-12-kcg-port-path-references-v1 --strict`
      and confirm exit 0 (output: `Change '2026-09-12-kcg-port-path-references-v1' is valid`)
- [x] T2.2 — Run
      `rg '/Users/cianmacandeisigh/dev/kings_college_galway' cianfhoghlaim/{dlt_sources,orchestration,bonneagar/iac,web/apps,cocoindex_flows}/`
      and confirm the 12 live-code file matches are GONE
      (only docs / openspec / research files remain, by design)

## Stage 3 — Archive

- [ ] T3.1 — Run
      `openspec archive 2026-09-12-kcg-port-path-references-v1 --yes`
      so the MODIFIED delta folds back into the canonical
      `openspec/specs/infrastructure-stacks/spec.md`

## Stage 4 — Commit

- [ ] T4.1 — Single-purpose commit scoped to the 12 live-code files
      only (no docs, no openspec research files)
- [ ] T4.2 — Confirm
      `rg kings_college_galway cianfhoghlaim/{dlt_sources,orchestration,bonneagar/iac,web/apps,cocoindex_flows}/`
      returns nothing

## Stage 5 — Final deletion (the actual KCG retirement)

- [ ] T5.1 — `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/`
- [ ] T5.2 — Verify `ls /Users/cianmacandeisigh/dev/kings_college_galway`
      fails with `No such file or directory`

## Stage 6 — Post-deletion smoke checks

- [ ] T6.1 — `mise run lint:drift-docs` (if available)
- [ ] T6.2 — `python -c "from dlt_sources.filesystem.pdf_download_source import *"` — import smoke
- [ ] T6.3 — Smoke-run a representative DLT source end-to-end
      (offline / `USE_LOCAL_SCRAPES=true`)