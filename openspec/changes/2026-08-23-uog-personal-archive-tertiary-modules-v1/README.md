# 2026-08-23-uog-personal-archive-tertiary-modules-v1

Lift `leabharlann/ollscoil_na_gaillimhe/` (the user's three UoG
courses' artefacts: BA Maths & Education, HDip Software Design,
Diploma in Irish C1) + `cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf`
to **full feature parity with the Leaving Cycle subject pipeline**.

The source is the folder as-is, auto-discovered (no curated drop-PDF
UI as primary entry). The pipeline produces typed artefacts →
assignments → questions → topics → code cells → reading items →
CA marks → transcript rows at **F-granularity** (per-question), joins
to the transcript for ground truth, embeds in LanceDB, draws typed
Cognee edges, and surfaces via marimo + Convex + CopilotKit + Genie
+ ADK agent — **transferable to any user** (the same factory runs
against any other student's `leabharlann/<university>/` corpus).

## Directory layout

```
openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
├── README.md                                       ← you are here
├── proposal.md                                     ← openspec proposal (Why / What changes / Non-goals)
├── tasks.md                                        ← the 12-workstream task checklist
└── specs/
    └── cianfhoghlaim-personal-archive-typed-modules/
        └── spec.md                                ← the canonical spec (14 Requirements + Scenarios)
```

## Status

`openspec validate 2026-08-23-uog-personal-archive-tertiary-modules-v1 --strict` → **passes**

`uv run pytest tests/personal_archive/ -v` → **12 passed, 0 skipped**

## Layered artefacts (delivered)

| Layer | Path | Count |
|---|---|---|
| BAML schema | `baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml` | 3 enums + 10 classes + 7 functions |
| DLT source | `dlt_sources/filesystem/uog_personal_archive.py` | 8 `@dlt.resource`s |
| HTR ensemble | `dlt_sources/filesystem/_htr_ensemble.py` | 6 backends + `route_htr` + `htr_extract_pages` |
| Generic factory | `dlt_sources/british_isles/ireland/education/university/personal_archive/` | 1 Pydantic config + 1 factory |
| DuckLake tables | `dlt_sources/_lakehouse/personal_archive_destinations.py` | 9 tables |
| CocoIndex Apps | `cocoindex_flows/british_isles/ireland/education/university/personal_archive_embedding.py` | 4 v1 Apps (artefacts / questions / topics / lecture-notes) |
| Cognee edges | `scripts/graph_storage/cognify/rules/personal_archive_typed_edges.py` | 10 emitters |
| Marimo notebook | `notebooks/15_personal_archive.py` | 8 tabs + CS4423 worked-example sidebar |
| Dagster assets | `orchestration/defs/uog_personal_archive.py` | 6 `@asset`s |
| Convex | `web/apps/cianfhoghlaim/convex/personalArchive.ts` | 5 actions/queries |
| CopilotKit | `web/apps/cianfhoghlaim/components/AskMyArchive.tsx` | 1 component |
| Genie UI | `web/apps/cianfhoghlaim/genie/personal_archive_browser.ts` | 1 tile |
| ADK agent | `agents/adk/personal_archive_module_assistant.py` | 1 LlmAgent + 10 FunctionTools + 3 sub-agents |
| Thesis figures | `orchestration/defs/uog_personal_archive_figures.py` | 6 PDFs via matplotlib |
| Observability | `observability/dashboards/personal_archive.json` | 1 Grafana dashboard (6 panels) |
| Tests | `tests/personal_archive/` | 12 pytest modules |
| Env vars | `.env.example` | 9 new vars (`UNIVERSITY_*` + `DUCKLAKE_DESTINATION`) |

## F-granularity destination (what "per-question" means here)

`UoGQuestion` is the F-granularity chain end. Each row carries:

```python
class UoGQuestion:
    question_id: str            # e.g. "cs4423-a1-q1"
    question_number: str        # "Q1", "Q2a", "Q4(ii)"
    question_text: str          # the question as written
    expected_topic: str         # the topic it targets
    max_marks: int?
    my_answer_text: str?        # verbatim OCR/pymupdf-extracted answer
    my_answer_latex: str?       # LaTeX form if mathematical
    my_mark: int?               # the mark I got
    my_mark_breakdown: str?     # free-form "3/5 — correct setup, arithmetic error"
    is_handwritten: bool
    htr_backend_used: HTRBackend?  # which of the 6 backends OCR'd this
    htr_confidence: float?
    answer_topic_tags: string[]
    confidence: float
```

Every `my_answer_text` for handwritten PDFs (`*.pages`, Goodnotes
exports, scanned) goes through the HTR ensemble
(`meaisinfhoghlaim.ocr.ensemble.ensembled_extractor.EnsembledExtractor`).

## Quick verification

```bash
# The openspec change validates
openspec validate 2026-08-23-uog-personal-archive-tertiary-modules-v1 --strict

# All 12 personal-archive tests pass
uv run pytest tests/personal_archive/ -v

# DuckLake tables register cleanly
uv run python -c "
import duckdb
from dlt_sources._lakehouse import register_personal_archive_tables
con = duckdb.connect(':memory:')
register_personal_archive_tables(con)
print(sorted(t[0] for t in con.execute('SHOW TABLES').fetchall()))
"

# Auto-classify a sample artefact
uv run python -c "
from pathlib import Path
from dlt_sources.filesystem.uog_personal_archive import _classify_file
print(_classify_file(Path('leabharlann/ollscoil_na_gaillimhe/mata/networks/CS4423 - Networks/cian_mac_liathain_assignment_3.pdf')))
"

# Smoke-test the HTR router
uv run python -c "
from pathlib import Path
from dlt_sources.filesystem._htr_ensemble import route_htr, auto_extract
backend, conf = route_htr(Path('foo.goodnotes.pdf'), 0.0)
print(f'goodnotes -> {backend.value}, confidence={conf}')
backend, conf = route_htr(Path('typed_lecture.pdf'), 1200.0)
print(f'typed lecture -> {backend.value}, confidence={conf}')
"
```

## Transferability (the user-facing promise)

Any university student can point this pipeline at their own
`leabharlann/<university>/` corpus by setting the 9 env vars and
calling `personal_archive_source(UniversityPersonalArchiveConfig(...))`.
The same 8 DLT resources, 7 BAML functions, 4 CocoIndex Apps, 10
Cognee edges, 6 Dagster assets, 8 Marimo tabs, 5 Convex queries,
1 CopilotKit component, 1 Genie tile, 1 ADK agent, 12 tests run
unchanged.

## Reference

- Spec: `specs/cianfhoghlaim-personal-archive-typed-modules/spec.md`
- Proposal: `proposal.md`
- Tasks: `tasks.md`
- Companion changes (in flight): `../2026-08-23-uog-exam-papers-sso-v1/`, `../2026-08-23-uog-official-docs-and-nui-superset-v1/`
