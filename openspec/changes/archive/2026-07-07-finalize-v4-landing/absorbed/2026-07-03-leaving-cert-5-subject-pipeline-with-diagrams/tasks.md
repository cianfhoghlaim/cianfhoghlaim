# Tasks: 2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams

## Phase 1 — File authoring (30 min)

- [x] 1.1 Create `cianfhoghlaim/baml_src/education/lc_extraction/curriculum_syllabus.baml`
- [x] 1.2 Create `cianfhoghlaim/baml_src/education/lc_extraction/exam_paper_layout.baml`
- [x] 1.3 Create `cianfhoghlaim/baml_src/education/lc_extraction/marking_scheme.baml`
- [x] 1.4 Create `cianfhoghlaim/baml_src/education/lc_extraction/cross_linguistic.baml`
- [x] 1.5 Create `cianfhoghlaim/baml_src/education/lc_extraction/syllabus_diagram.baml`
- [x] 1.6 Create `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py` (5-subject DLT source)
- [x] 1.7 Create 3 defs.yaml: L1 ingestion, L2 materials, L3 model lifecycle
- [x] 1.8 Create `cianfhoghlaim/dagster/defs/2_materials/lc_extraction/lc5_assets.py` (5 L1 + 20 L2 + 5 L3 assets)
- [x] 1.9 Create 16 dev marimo notebooks under `notebooks/dashboards/leaving_cert/`
- [x] 1.10 Write `proposal.md` + `tasks.md` + 1 spec delta

## Phase 2 — Validate (2 min)

- [ ] 2.1 `openspec validate 2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams --strict`
- [ ] 2.2 `python -c "import ast; ast.parse(open('...'))"` for all 26 new files

## Phase 3 — Smoke tests (5 min)

- [ ] 3.1 `python cianfhoghlaim/dlt/filesystem/leaving_cert_source.py` — scan the 5 subjects (72 PDFs total)
- [ ] 3.2 `marimo parse notebooks/dashboards/leaving_cert/01_chemistry_analysis.py` — parses
- [ ] 3.3 `dagster asset materialize --select '*lc5*'` — runs all 30 assets

## Phase 4 — Stage commits (5 min)

- [ ] 4.1 `git add cianfhoghlaim/baml_src/education/lc_extraction/`
- [ ] 4.2 `git commit -m "feat(baml): create 5 LC education BAML files (curriculum/exam/marking/cross-ling/diagram)"`
- [ ] 4.3 `git add cianfhoghlaim/dlt/filesystem/leaving_cert_source.py`
- [ ] 4.4 `git commit -m "feat(dlt): add leaving_cert_source.py (5 LC subjects × 2 languages + JPG fallback)"`
- [ ] 4.5 `git add cianfhoghlaim/dagster/defs/`
- [ ] 4.6 `git commit -m "feat(dagster): add LC5 5-layer asset module + 3 defs.yaml (1_ingestion/2_materials/3_model_lifecycle)"`
- [ ] 4.7 `git add cianfhoghlaim/notebooks/dashboards/leaving_cert/`
- [ ] 4.8 `git commit -m "feat(notebooks): create 16 LC dev notebooks (5 per-subject + 5 cross + 5 model + 1 side-by-side)"`
- [ ] 4.9 `git add openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/`
- [ ] 4.10 `git commit -m "docs(openspec): 2026-07-03-leaving-cert change (proposal + tasks + 1 spec delta)"`
