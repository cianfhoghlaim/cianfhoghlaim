# Per-subject interactive marimo study tools for the 6 BIEP v1 LC subjects (Phase 3)

## Why

The `oideachais-marimo-dashboards` capability has shipped two
operator-facing dashboards waves:
- **Phase 1** — `2026-07-14-oideachais-marimo-dashboards-v1` (commit
  `44cabc151`) — the 10 cross-cutting dashboards at
  `notebooks/10_marimo_dashboards/` (corpus overview, cognify KG,
  cross-archive, lakehouse table browser, BAML extraction log viewer,
  per-subject analytics, Gaeilge language coverage, CocoIndex v1
  conformance, agent memory, Dagster asset lineage).
- **Phase 2** — `2026-07-15-oideachais-marimo-dashboards-extension-v1`
  (commit `c536f7f79`) — the 10 follow-up dashboards at
  `notebooks/11_marimo_dashboards_v2/` (leabharlann corpus +
  university extraction + cross-archive edges + K-12 → university
  pipeline coverage).

Both waves are operator-facing. There is **no student-facing study
tool surface** that consumes the per-subject `qpack_*.baml` functions
in `cianfhoghlaim/baml/education/subjects/`. The 6 BIEP v1 LC
subjects (Mathematics, Chemistry, Geography, Gaeilge, English,
Computer Science) each have:
- A per-subject NCCA syllabus (BIEP lakehouse tables under
  `oideachais.leaving_cert.<subject>_topics` + `<subject>_papers` +
  `<subject>_marking`)
- A per-subject `qpack_<subject>.baml` file with 5-6 functions
  (`Generate<Subj>QuestPack`, `Generate<Subj>FormativeItem`,
  `Score<Subj>FormativeResponse`, `Validate<Subj>QuestPack`, plus
  `Extract<Subj>LOStatement` / `Extract<Subj>GaStatement`)

This change ships **6 per-subject interactive marimo study tools**
(one per BIEP v1 LC subject) at
`cianfhoghlaim/notebooks/12_subject_study_tools/`. Each notebook is
student-facing and ships 5 study-tool cells:

1. **Flashcards** — generated from the per-subject NCCA learning
   outcomes via `qpack_<subject>.baml::Generate<Subj>FormativeItem`
2. **Practice questions** — three difficulty levels (1=easy, 3=medium,
   5=hard) via the same per-subject BAML function
3. **Mock exam** — queries the per-subject past exam paper ingestion
   (`oideachais.leaving_cert.<subject>_papers`)
4. **Study plan** — per-subject lectionary + per-student progress
   (synthesised from the per-subject topic frequency table)
5. **Per-subject BAML function** — invokes the per-subject
   `Generate<Subj>QuestPack` directly from `qpack_<subject>.baml`
   (the lc6 extraction stage)

Each notebook is 366-376 LOC, follows the same PEP 723 inline-deps
pattern as the Phase-1 / Phase-2 dashboards, and connects to
`md:oideachais` (MotherDuck + DuckLake) with a graceful local-DuckDB
fallback via `connect_biep_lakehouse()`.

## What changes

- New subdir `cianfhoghlaim/notebooks/12_subject_study_tools/` with
  **6 per-subject marimo study tools** (one per BIEP v1 LC subject):
  - `mathematics.py` — Math: Algebra / Calculus / Statistics /
    Geometry flashcards + practice questions + mock exam + study
    plan + `qpack_mathematics.baml::GenerateMathFormativeItem`
  - `chemistry.py` — Chem: Atomic Structure / Bonding / Stoichiometry
    / Acids & Bases flashcards + practice + mock + study plan +
    `qpack_chemistry.baml::GenerateChemFormativeItem`
  - `geography.py` — Geog: Plate Tectonics / Climate / Population /
    Urban Geography flashcards + practice + mock + study plan +
    `qpack_geography.baml::GenerateGeogFormativeItem`
  - `gaeilge.py` — Gael: Litríocht / Gramadach / Léamhthuiscint /
    Scríbhneoireacht flashcards (GA-front + GA-back) + practice + mock
    + study plan + `qpack_gaeilge.baml::GenerateGaelFormativeItem`
  - `english.py` — Engl: Reading / Writing / Comprehension /
    Composition flashcards + practice + mock + study plan +
    `qpack_english.baml::GenerateEnglFormativeItem`
  - `computer_science.py` — Comp: Algorithms / Programming / Data
    Structures / Databases flashcards + practice + mock + study plan +
    `qpack_computer_science.baml::GenerateCompFormativeItem`
- `cianfhoghlaim/notebooks/cli.py` — added `12_subject_study_tools`
  to the `GROUPS` tuple (so `cianfhoghlaim-marimo list
  12_subject_study_tools` discovers the new entries)
- 1 MODIFIED spec delta on `oideachais-marimo-dashboards/spec.md` —
  adds requirement R-Phase-3 (Phase 3 complete: per-subject marimo
  study tools at `notebooks/12_subject_study_tools/<subject>.py`
  ship flashcards + practice questions + mock exams + study plans
  for the 6 BIEP v1 LC subjects)

## Out of scope

- The 6th BIEP v1 priority subjects (Applied Mathematics, History) —
  not part of the 6-subject lock per the user's plan; they continue
  to fall through to the existing per-subject notebooks under
  `notebooks/leaving_cert/` when added later.
- The existing 10+10+10 = 30 dashboards at
  `notebooks/10_marimo_dashboards/` and
  `notebooks/11_marimo_dashboards_v2/` — these are unchanged.
- The existing 6 per-subject visualisation notebooks at
  `notebooks/leaving_cert/<subject>.py` — these remain as the
  Phase-6 cross-subject visualisations; the new study tools live
  alongside them.

## Non-goals

- Do NOT touch the 10+10 existing dashboards at
  `notebooks/10_marimo_dashboards/` and
  `notebooks/11_marimo_dashboards_v2/`
- Do NOT touch the 50+ archived openspec changes under
  `openspec/changes/archive/*`
- Do NOT modify the 7 `baml/education/lc_extraction/*.baml` files
  (owned by the BIEP v1 change)
- Do NOT include App Math + Hist (out of scope per the user's
  locked plan — the 6 BIEP v1 LC subjects are Math, Chem, Geog,
  Gaeilge, Eng, CS)

## Dependencies

Blocked by: `2026-07-15-oideachais-marimo-dashboards-extension-v1`
(the Phase-2 commit `c536f7f79` that shipped the 10 v2 dashboards).
This change can archive only after the Phase-2 commit lands on the
remote `pick-4-biep-v1` branch.

## Reference

- `openspec/specs/oideachais-marimo-dashboards/spec.md` (the
  capability spec this delta modifies — the 11 prior requirements
  ship the 10 Phase-1 + 10 Phase-2 dashboards from commits
  `44cabc151` and `c536f7f79`)
- `openspec/changes/2026-07-14-oideachais-marimo-dashboards-v1/`
  (the Phase-1 change that shipped the 10 prior dashboards)
- `openspec/changes/2026-07-15-oideachais-marimo-dashboards-extension-v1/`
  (the Phase-2 change that shipped the 10 follow-up dashboards)
- `openspec/specs/oideachais-pipeline/spec.md` (the BIEP v1 flagship
  spec — defines the 6 BIEP v1 LC subjects, the 3 levels, the 2
  working languages, and the 9-year window)
- `openspec/specs/british-isles-education-pipeline/spec.md` (the
  upstream BIEP v1 spec)
- `cianfhoghlaim/baml/education/subjects/qpack_<subject>.baml` (the
  per-subject qpack BAML functions consumed by each study tool)
- `cianfhoghlaim/notebooks/nb_utils.py::connect_biep_lakehouse()` (the
  canonical MotherDuck + DuckLake connect helper)