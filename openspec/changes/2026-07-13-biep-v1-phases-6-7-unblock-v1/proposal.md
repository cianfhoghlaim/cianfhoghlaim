# BIEP v1 Phases 6+7 Unblock — 6 per-subject marimo notebooks + MotherDuck Flight

## Why

The `pick-4-biep-v1` branch has shipped Phases 0–5 of the British-Isles
Education Pipeline v1 (`openspec/changes/archive/2026-07-09-2026-07-06-british-isles-education-pipeline-v1/`,
archived 2026-07-09): the 6 priority LC subjects are wired end-to-end
(NCCA + SEC + gov.ie DLT sources, BAML extraction, 7 v1 CocoIndex
flows, 42+ Dagster assets, 4 MotherDuck Dives), and 6 thin marimo
notebook stubs already live at `cianfhoghlaim/notebooks/leaving_cert/`
(committed by an earlier agent during T6 work). The canonical
`british-isles-education-pipeline` spec already references both the
6 per-subject notebooks and the `lc_pdf_sync_flight` daily Flight
(see Requirements: "BIEP Subject Notebooks — ibis-first wiring to local
lakehouse" and "Daily MotherDuck Flight for BAML backfill").

What remains to land **Phase 6 (per-subject marimo notebooks) and
Phase 7 (MotherDuck Flight)**:

1. **Enhance the 5 existing stub notebooks** at
   `cianfhoghlaim/notebooks/leaving_cert/{chemistry,computer_science,gaeilge,geography,mathematics}.py`
   from ~150-LOC table-only stubs (~150 LOC) to ~300–400 LOC BIEP v1
   dashboards with: 5 altair visualisations per notebook (topic
   frequency line chart, exam paper difficulty bar chart, marking
   scheme complexity heatmap, cross-subject or cross-linguistic
   mapping for `gaeilge`/`en_vs_ga`, asset generator), live
   `connect_biep_lakehouse("md:oideachais")` wiring, and BAML
   `ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` +
   `ExtractMarkingSchemeGuideline` + `ExtractSyllabusDiagram` +
   per-subject `qpack_<subject>.baml` calls.
2. **Add the missing cross-subject notebook**
   `06_en_vs_ga_comparison.py` (the 6th BIEP subject notebook
   required by the spec — bilingual EN ↔ GA competency comparison
   across the 5 EN/GA subjects).
3. **Create the MotherDuck `lc_pdf_sync_flight`** at
   `cianfhoghlaim/motherduck/flights/lc_pdf_sync_flight.py`
   + the flight `config.yaml` (cron `0 4 * * *` = 04:00 UTC daily)
   that runs `cocoindex update lc_subjects` + `dagster asset materialize
   --select '*lc*'` and writes a status row to
   `md:oideachais.lc_ops.daily_sync_status`.

This change is the canonical "Phase 6 + 7 unblock" tracker: it
augments the existing 5 stub notebooks, adds the 6th cross-subject
notebook, lands the MotherDuck Flight, and refreshes the canonical
spec to confirm the Phase 6 / Phase 7 deliverables are live.

## What changes

1. **Phase 6 — 6 per-subject marimo notebooks (~6h, ~300-400 LOC each)**
   - Enhance `cianfhoghlaim/notebooks/leaving_cert/chemistry.py`:
     5 altair visualisations over `oideachais.leaving_cert.chemistry_*`
     + BAML `ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` +
     `ExtractMarkingSchemeGuideline` + `ExtractSyllabusDiagram` calls.
   - Enhance `computer_science.py`, `gaeilge.py`, `geography.py`,
     `mathematics.py` (and the already-thin `english.py`) with the
     same 5-viz + 4-BAML pattern.
   - Add `06_en_vs_ga_comparison.py`: cross-subject EN ↔ GA competency
     heatmap + bilingual coverage matrix + asset generator for the
     English/Gaeilge shared topics.

2. **Phase 7 — MotherDuck `lc_pdf_sync_flight` (~2h)**
   - Create `cianfhoghlaim/motherduck/flights/lc_pdf_sync_flight.py`:
     daily Python job that runs `cocoindex update lc_subjects` +
     `dagster asset materialize --select '*lc*'` and writes a status
     row to `md:oideachais.lc_ops.daily_sync_status`.
   - Create `cianfhoghlaim/motherduck/flights/config.yaml`:
     registers `lc_pdf_sync_flight` with cron `0 4 * * *` (04:00 UTC).

3. **Spec deltas (2 ADDED Requirements)**
   - Add `Phase 6 — 6 per-subject marimo notebooks` requirement to
     `openspec/specs/british-isles-education-pipeline/spec.md`
     confirming the 6 notebooks at `notebooks/leaving_cert/` each
     render 5 visualisations against live lakehouse data.
   - Add `Phase 7 — MotherDuck lc_pdf_sync_flight` requirement
     confirming the daily Flight at
     `cianfhoghlaim/motherduck/flights/lc_pdf_sync_flight.py`
     + cron `0 4 * * *` writes a status row to
     `md:oideachais.lc_ops.daily_sync_status`.

## Dependencies

`Blocked by: none` (all upstream work has shipped in T0–T5).

`Blocked by (soft): 2026-07-09-2026-07-06-british-isles-education-pipeline-v1`
(the archived BIEP v1 change that owns the canonical spec — this
change augments the already-shipped Phase 0–5 with Phase 6 + 7).

`Affected repos: cianfhoghlaim` (single-repo change; no
`cross-repo-sync.md` required).

## Out of scope

- Do NOT touch the 50+ archived openspec changes under
  `openspec/changes/archive/*`.
- Do NOT push to `main`.
- Do NOT modify the 7 `baml/education/lc_extraction/*.baml` files
  (owned by the BIEP v1 change — that work has already shipped).
- Do NOT modify the legacy `notebooks/03_leaving_cert/` 23 old
  notebooks (preserve unchanged).
- Do NOT modify the existing `cianfhoghlaim/motherduck/`
  (the 4 Dives + 1 daily Flight + 2 `__init__.py` + 1 flight
  `config.yaml` were re-homed here from the prior
  `infrastructure/stacks/motherduck/` path on 2026-07-10).

## Validation plan

- `openspec validate 2026-07-13-biep-v1-phases-6-7-unblock-v1 --strict` — passes.
- 6 per-subject marimo notebooks at `notebooks/leaving_cert/{01..06}_*.py`
  exist + AST-parse cleanly (the actual filenames are
  `chemistry.py`, `computer_science.py`, `gaeilge.py`, `geography.py`,
  `mathematics.py`, `english.py`, plus the new
  `06_en_vs_ga_comparison.py`).
- `cianfhoghlaim/motherduck/flights/lc_pdf_sync_flight.py`
  exists + AST-parses.
- `cianfhoghlaim/motherduck/flights/config.yaml` has the
  `lc_pdf_sync_flight` entry with cron `0 4 * * *`.
- 2 ADDED spec deltas on `british-isles-education-pipeline` are
  well-formed.
- Pushed to `origin/pick-4-biep-v1` (NOT `main`).