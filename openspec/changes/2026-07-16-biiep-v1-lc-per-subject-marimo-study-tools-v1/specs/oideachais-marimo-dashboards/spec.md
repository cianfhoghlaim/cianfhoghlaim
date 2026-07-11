# Spec Delta: oideachais-marimo-dashboards

> Parent change: [../proposal.md](../../proposal.md)

## ADDED Requirements

### Requirement: Phase 3 complete — per-subject interactive marimo study tools for the 6 BIEP v1 LC subjects

The system SHALL provide **6 per-subject interactive marimo study tools**
at `cianfhoghlaim/notebooks/12_subject_study_tools/<subject>.py` for
the 6 BIEP v1 LC subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science). These extend the 20 operator-facing
dashboards shipped by the Phase-1 + Phase-2 changes
(`2026-07-14-oideachais-marimo-dashboards-v1` commit `44cabc151` and
`2026-07-15-oideachais-marimo-dashboards-extension-v1` commit
`c536f7f79`) by adding a student-facing study tool surface.

Each Phase-3 study tool:

- Uses the PEP 723 inline dependency header (`# /// script` block)
  declaring `marimo>=0.13.0`, `duckdb>=1.0`, `pandas>=2.0`,
  `altair>=5.0`
- Connects to `md:oideachais` (MotherDuck + DuckLake) via
  `connect_biep_lakehouse()` with a graceful local-DuckDB fallback
- Falls back to a synthetic-data corpus when the lakehouse is
  unreachable (so notebooks render meaningfully offline)
- Invokes the per-subject `qpack_<subject>.baml` BAML functions
  (`Generate<Subj>FormativeItem`, `Generate<Subj>QuestPack`) via
  `from cianfhoghlaim.baml_client import b; b.<fn>(...)`, wrapped in
  try/except so the notebook renders offline
- Ships 5 study-tool cells per notebook (see below)

The 6 Phase-3 study tools are:

| # | File | Subject | Per-subject qpack BAML |
|:--|:--|:--|:--|
| 01 | `mathematics.py` | Mathematics | `qpack_mathematics.baml` |
| 02 | `chemistry.py` | Chemistry | `qpack_chemistry.baml` |
| 03 | `geography.py` | Geography | `qpack_geography.baml` |
| 04 | `gaeilge.py` | Gaeilge | `qpack_gaeilge.baml` |
| 05 | `english.py` | English | `qpack_english.baml` |
| 06 | `computer_science.py` | Computer Science | `qpack_computer_science.baml` |

The 5 study-tool cells in each Phase-3 notebook are:

1. **Flashcards** — renders 10 flashcards generated from the
   per-subject NCCA learning outcomes
   (`oideachais.leaving_cert.<subject>_topics`) with bilingual EN+GA
   front/back (Gaeilge: GA-front + GA-back).
2. **Practice questions** — three per-subject difficulty levels
   (1=easy, 3=medium, 5=hard) via the same per-subject BAML function
   `Generate<Subj>FormativeItem`.
3. **Mock exam** — queries the per-subject past exam paper ingestion
   (`oideachais.leaving_cert.<subject>_papers`) and renders the
   per-year × per-level question count + avg-difficulty table.
4. **Study plan** — per-subject lectionary + per-student progress,
   synthesised from the per-subject topic frequency table
   (`oideachais.leaving_cert.<subject>_topics`) with a `mastery_pct`
   column and `next_revision_days` column.
5. **Per-subject BAML function** — invokes the per-subject
   `Generate<Subj>QuestPack` directly from
   `qpack_<subject>.baml`, plus `Generate<Subj>FormativeItem` for a
   single-formative-item invocation (deferred for the quest pack —
   the full quest-pack BAML call needs the full syllabus +
   past_papers + marking_schemes inputs, which the pipeline runner
   provides).

#### Scenario: Mathematics study tool renders

- **GIVEN** `notebooks/12_subject_study_tools/mathematics.py`
- **WHEN** the user runs `marimo edit mathematics.py` (or
  `uv run cianfhoghlaim-marimo edit 12_subject_study_tools/mathematics`)
- **THEN** the notebook SHALL render with 5 study-tool cells
  (flashcards, practice questions, mock exam, study plan, BAML call)
- **AND** the flashcards SHALL be generated from
  `oideachais.leaving_cert.mathematics_topics` with 10 NCCA-coded
  cards (LC-MATHS-LO-*)
- **AND** the BAML cell SHALL invoke
  `qpack_mathematics.baml::GenerateMathFormativeItem` wrapped in
  try/except (offline-friendly)

#### Scenario: Gaeilge study tool renders with Gaeilge-front flashcards

- **GIVEN** `notebooks/12_subject_study_tools/gaeilge.py`
- **WHEN** the user runs `marimo edit gaeilge.py`
- **THEN** the flashcards SHALL use Gaeilge front-side prompts (e.g.
  "Mínigh agus cuir i bhfeidhm LC-GAEL-LO-1.1 (Litríocht)") and
  Gaeilge back-side answers
- **AND** the practice questions SHALL be in Gaeilge

#### Scenario: CLI discovers all 6 Phase-3 study tools

- **GIVEN** the `GROUPS` tuple in
  `cianfhoghlaim/notebooks/cli.py` includes
  `"12_subject_study_tools"`
- **WHEN** the user runs
  `uv run cianfhoghlaim-marimo list 12_subject_study_tools`
- **THEN** the CLI SHALL list all 6 new study tools
  (`mathematics.py`, `chemistry.py`, `geography.py`, `gaeilge.py`,
  `english.py`, `computer_science.py`)
- **AND** each notebook SHALL AST-parse cleanly (verified by
  `python -c "import ast; ast.parse(open(...).read())"`)

#### Scenario: Existing 30+10+10=50 notebooks still AST-parse

- **WHEN** the 30 existing dashboards at
  `notebooks/10_marimo_dashboards/` (Phase 1) and
  `notebooks/11_marimo_dashboards_v2/` (Phase 2) plus the 20+
  BIEP / leaving_cert / semantic_search notebooks are AST-parsed
  after the new subdir is added
- **THEN** every existing notebook SHALL AST-parse cleanly
  (the 8 pre-existing parse failures in
  `notebooks/04_biep_motherduck/0[1-9]_*.py` are owned by the BIEP
  MotherDuck notebooks workstream and are out of scope for this
  change)
- **AND** the 10+10 existing dashboards SHALL be unchanged
  (no file modifications to `notebooks/10_marimo_dashboards/` or
  `notebooks/11_marimo_dashboards_v2/`)

## Cross-references

- [`openspec/specs/oideachais-marimo-dashboards/spec.md`](../../specs/oideachais-marimo-dashboards/spec.md)
  (the capability spec this delta modifies — the 11 prior
  requirements ship the 10 Phase-1 + 10 Phase-2 dashboards from
  commits `44cabc151` and `c536f7f79`)
- [`openspec/changes/2026-07-14-oideachais-marimo-dashboards-v1/`](../../2026-07-14-oideachais-marimo-dashboards-v1/)
  (the Phase-1 change that shipped the 10 prior dashboards)
- [`openspec/changes/2026-07-15-oideachais-marimo-dashboards-extension-v1/`](../../2026-07-15-oideachais-marimo-dashboards-extension-v1/)
  (the Phase-2 change that shipped the 10 follow-up dashboards)
- [`.agents/skills/marimo/SKILL.md`](../../../.agents/skills/marimo/SKILL.md)
  (the canonical marimo skill — PEP 723 inline deps,
  `@app.cell(column=N)`)
- [`.agents/skills/motherduck/SKILL.md`](../../../.agents/skills/motherduck/SKILL.md)
  (the MotherDuck `md:oideachais` connection contract)
- [`.agents/skills/baml/SKILL.md`](../../../.agents/skills/baml/SKILL.md)
  (the BAML extraction framework — covers `qpack_<subject>.baml`
  schema + `@function` patterns)
- [`openspec/specs/oideachais-pipeline/spec.md`](../../specs/oideachais-pipeline/spec.md)
  (the BIEP v1 flagship spec — defines the 6 BIEP v1 LC subjects,
  the 3 levels, the 2 working languages, and the 9-year window)
- [`openspec/specs/british-isles-education-pipeline/spec.md`](../../specs/british-isles-education-pipeline/spec.md)
  (the upstream BIEP v1 spec)
- [`openspec/specs/oideachais-baml-schemas/spec.md`](../../specs/oideachais-baml-schemas/spec.md)
  (the per-subject `qpack_<subject>.baml` schemas consumed by each
  study tool)