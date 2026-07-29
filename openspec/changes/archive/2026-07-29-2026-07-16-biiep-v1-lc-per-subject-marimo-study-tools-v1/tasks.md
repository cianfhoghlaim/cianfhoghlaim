# Tasks — Per-subject interactive marimo study tools for the 6 BIEP v1 LC subjects (Phase 3)

## 1. Audit the existing marimo dashboard infrastructure

- [x] Listed `notebooks/leaving_cert/` — the 6 existing
      per-subject visualisation notebooks (mathematics.py,
      chemistry.py, geography.py, gaeilge.py, english.py,
      computer_science.py)
- [x] Confirmed `notebooks/12_subject_*` does not exist
      (the new subdir was created)
- [x] Verified the 6 `qpack_<subject>.baml` files exist with 5-6
      functions per subject (mathematics: 6, chemistry: 6,
      geography: 6, gaeilge: 6, english: 5, computer_science: 5)

## 2. Ship the 6 per-subject marimo study tools

- [x] `12_subject_study_tools/mathematics.py` (376 LOC) — Math
      flashcards (per-subject qpack BAML) + practice questions
      (difficulty 1/3/5) + mock exam (per-subject past exam paper
      ingestion) + study plan (per-subject lectionary + per-student
      progress) + `qpack_mathematics.baml::GenerateMathFormativeItem`
- [x] `12_subject_study_tools/chemistry.py` (368 LOC) — Chem same 5
      study-tool cells, `qpack_chemistry.baml::GenerateChemFormativeItem`
- [x] `12_subject_study_tools/geography.py` (367 LOC) — Geog same 5
      study-tool cells, `qpack_geography.baml::GenerateGeogFormativeItem`
- [x] `12_subject_study_tools/gaeilge.py` (372 LOC) — Gael same 5
      study-tool cells (GA prompts), `qpack_gaeilge.baml::GenerateGaelFormativeItem`
- [x] `12_subject_study_tools/english.py` (366 LOC) — Engl same 5
      study-tool cells, `qpack_english.baml::GenerateEnglFormativeItem`
- [x] `12_subject_study_tools/computer_science.py` (374 LOC) — CS
      same 5 study-tool cells,
      `qpack_computer_science.baml::GenerateCompFormativeItem`

## 3. Register the new subdir in `cli.py`

- [x] Added `"12_subject_study_tools"` to the `GROUPS` tuple in
      `notebooks/cli.py` (with explanatory inline
      comment + openspec change reference)

## 4. Verify the 6 notebooks AST-parse

- [x] All 6 per-subject notebooks AST-parse cleanly (verified by
      `uv run python3 -c "import ast; ast.parse(...)"`)

## 5. Verify the CLI discovery

- [x] `uv run cianfhoghlaim-marimo list 12_subject_study_tools`
      discovers 6 entries (chemistry, computer_science, english,
      gaeilge, geography, mathematics)

## 6. Verify the existing notebooks still AST-parse

- [x] The 4 reference notebooks AST-parse cleanly
      (`03_leaving_cert/01_chemistry_analysis.py`,
      `leaving_cert/chemistry.py`,
      `10_marimo_dashboards/01_biep_corpus_overview.py`,
      `11_marimo_dashboards_v2/01_leabharlann_corpus_overview.py`)
- [x] 152 of 160 total notebooks AST-parse cleanly (the 8
      pre-existing failures are at `04_biep_motherduck/0[1-9]_*.py`,
      unrelated to this change — they are owned by the BIEP
      MotherDuck notebooks workstream)

## 7. Write the openspec change

- [x] `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1/proposal.md`
- [x] `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1/tasks.md`
- [x] `openspec/changes/2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1/specs/cianfhoghlaim-marimo-dashboards/spec.md`
      (MODIFIED delta — adds R-Phase-3 requirement)

## 8. Commit + push

- [ ] Commit on `pick-4-biep-v1` and push to
      `origin/pick-4-biep-v1`