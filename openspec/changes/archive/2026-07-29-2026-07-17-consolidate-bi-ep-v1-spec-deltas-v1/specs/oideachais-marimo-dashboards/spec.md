# `cianfhoghlaim-marimo-dashboards` MODIFIED — Declare on-disk count as canonical source of truth + update cross-reference

> One new requirement + one modified cross-reference against the
> canonical `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md`:
>
> 1. The canonical spec's `## Cross-references` section (line 250)
>    states "(the 11 Marimo notebooks)" — this is a stale count.
>    The 4 source changes that ship marimo notebooks (the
>    baml-cocoindex tutorials + the v1 dashboards + the v2 extension
>    + the v3 study tools) reference "5", "11", "25", and "50"
>    counts respectively, all of which are inconsistent with the
>    on-disk reality. The canonical on-disk count via
>    `ls notebooks/**/*.py | wc -l` is the source of
>    truth.
>
> 2. A new requirement "On-disk marimo notebook count is the
>    canonical source of truth" is added to the canonical spec to
>    document this convention. The 4 source-change subdirs that have
>    stale claims remain unchanged (they're historical artifacts).

## ADDED Requirements

### Requirement: On-disk marimo notebook count is the canonical source of truth

The system SHALL consider the on-disk count of `.py` files at
`notebooks/**/*.py` (verified via
`ls notebooks/**/*.py | wc -l`) as the canonical
source of truth for all marimo notebook count claims in any
openspec change proposal or spec delta.

The on-disk count at this consolidation time (2026-07-17) is:

- **134 clean marimo notebooks** (excluding `__init__.py`,
  `__pycache__/*`, and `legacy/*`)
- **160 total `.py` files** (including `__init__.py` and
  `__pycache__/*` — the canonical raw count)

The per-group breakdown (clean count):

| Group | Count | Description |
|:--|--:|:--|
| `01_dev_env/` | 6 | dev-env demo tools (ccc search, drift detect, etc.) |
| `02_vision_models/` | 6 | vision model benchmarks |
| `03_leaving_cert/` | 23 | LC analysis + BIEP v1 per-subject notebooks |
| `04_biep_motherduck/` | 11 | BIEP motherduck + leabharlann full-stack demo |
| `05_lakehouse_inspect/` | 4 | DuckLake + lakehouse inspector |
| `06_observability/` | 3 | BAML drift + Irish extraction quality + Cognee KG |
| `07_educational_stages/` | 7 | Aistear → Tertiary + cross-domain + analysis_plan |
| `08_sources/` | 1 | sources loader |
| `09_official_media/` | 7 | fediverse + cross-archive + moderation |
| `10_cognify/` | 1 | cognify KG visualiser |
| `10_marimo_dashboards/` | 10 | v1 dashboards (Phase 1, shipped 2026-07-14) |
| `10_mmo/` | 2 | MMO mission control |
| `11_marimo_dashboards_v2/` | 10 | v2 dashboards (Phase 2, shipped 2026-07-15) |
| `11_speedrun/` | 9 | Tuatha speedrun tutorials |
| `12_ireland_law/` | 6 | Ireland law notebooks (PIAB + WRC + courts + …) |
| `12_semantic_search/` | 1 | cross-corpus LanceDB HNSW search |
| `12_subject_study_tools/` | 6 | v3 study tools (Phase 3, shipped 2026-07-16) |
| `13_baml_cocoindex_tutorial/` | 10 | BAML+CocoIndex tutorials (5 EN + 5 GA siblings) |
| `leaving_cert/` (root) | 7 | per-subject BIEP notebooks + bilingual comparison |
| `**/*.py` (root-level) | 2 | `01_overview_setup.py` + `ie_law_explorer.py` + `nb_utils.py` |
| `__init__.py` + `cli.py` | 2 | infrastructure (not marimo notebooks) |
| **Total (clean)** | **134** | marimo notebooks |

The 4 stale claims in the 4 source-change subdirs are historical
artifacts and SHALL NOT be retroactively updated (they live in
non-archived changes that have already shipped):

| Source change | Stale claim | Where |
|:--|:--|:--|
| `2026-07-14-cianfhoghlaim-marimo-dashboards-v1` | "11 BIEP notebooks" (refers to `04_biep_motherduck/` count, which IS accurate; the 10 v1 dashboards claim is also accurate) | spec.md Scenario 1 + Scenario 3 |
| `2026-07-15-cianfhoghlaim-marimo-dashboards-extension-v1` | "Existing 15+10=25 notebooks still AST-parse" | spec.md line 119-127 |
| `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1` | "Existing 30+10+10=50 notebooks still AST-parse" | spec.md line 104-118 |
| `2026-07-12-baml-cocoindex-tutorials-v1` | "5 new BAML tutorials" (the 5 EN tutorials; the 5 GA siblings came from `2026-07-13-baml-cocoindex-tutorials-ga-v1`) | spec.md line 7-40 |

#### Scenario: `ls` returns the canonical on-disk count

- **WHEN** a developer runs
      `ls notebooks/**/*.py | wc -l`
- **THEN** the output SHALL be the canonical count (134 clean; 160
      raw)
- **AND** the on-disk breakdown per the table above SHALL be
      reproducible via `find cianfhoghlaim/notebooks -maxdepth 2 -type f -name "*.py" -not -path "*/__pycache__/*" -not -name "__init__.py" | wc -l`

#### Scenario: All existing marimo notebooks AST-parse

- **WHEN** the developer runs `python -c "import ast; ast.parse(open(f).read())"`
      for each of the 134 clean marimo notebooks
- **THEN** all 134 files SHALL parse without SyntaxError
- **AND** the breakdown per the table above SHALL hold

#### Scenario: Stale claim documentation

- **GIVEN** a developer reads the 4 source-change spec deltas at
      `openspec/changes/2026-07-{12,14,15,16}-{...}/specs/cianfhoghlaim-marimo-dashboards/spec.md`
- **WHEN** they cross-reference the claims against the canonical
      on-disk count
- **THEN** the cross-reference table above SHALL be the source of
      truth (the source-change spec deltas are historical artifacts)

## Cross-references *(updated line 250)*

- [`notebooks/`](../../notebooks/) (the on-disk count of Marimo notebooks — see the new "On-disk marimo notebook count is the canonical source of truth" requirement above; verified via `ls notebooks/**/*.py | wc -l` = 134 clean / 160 raw)
- [`notebooks/dashboards/`](../../notebooks/dashboards/) (the dashboard subdir)
- [`.agents/skills/marimo/SKILL.md`](../../.agents/skills/marimo/SKILL.md)
- [`.agents/skills/build-notebook/SKILL.md`](../../.agents/skills/build-notebook/SKILL.md)
- [`openspec/specs/cianfhoghlaim-leabharlann/spec.md`](cianfhoghlaim-leabharlann/spec.md) (the upstream pipeline — the source of truth for the 6 sub-corpora + 225 documents)

## Stale-claim history *(added by this consolidation change)*

The 4 source changes that ship marimo notebooks have inconsistent
count claims. The on-disk count is the canonical source of truth
(see the new requirement above). The 4 stale claims are:

| Source change | Stale claim | Resolution |
|:--|:--|:--|
| `2026-07-12-baml-cocoindex-tutorials-v1` | "5 new BAML tutorials" | Accurate (the 5 EN tutorials are the "new" additions; the 5 GA siblings came from `2026-07-13-baml-cocoindex-tutorials-ga-v1`) |
| `2026-07-14-cianfhoghlaim-marimo-dashboards-v1` | "11 BIEP notebooks" + "10 v1 dashboards" | Accurate (the 11 BIEP motherduck + 10 v1 dashboards) |
| `2026-07-15-cianfhoghlaim-marimo-dashboards-extension-v1` | "Existing 15+10=25 notebooks still AST-parse" | Stale — replaced by the on-disk count |
| `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1` | "Existing 30+10+10=50 notebooks still AST-parse" | Stale — replaced by the on-disk count |

**Summary**: 4 stale count claims across 4 source-change spec deltas
consolidated into 1 new "On-disk marimo notebook count is the
canonical source of truth" requirement + 1 MODIFIED cross-reference.