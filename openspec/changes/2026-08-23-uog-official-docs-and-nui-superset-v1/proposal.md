# 2026-08-23-uog-official-docs-and-nui-superset-v1

> Lift the University of Galway exam-papers pipeline (the prior
> `2026-08-23-uog-exam-papers-sso-v1` change) to **full feature-parity
> with the primary/secondary education pipelines**.
>
> Adds the NUI federation, the UoG Students' Union, the UoG official
> documents source, the British-Isles tertiary factory (QUB +
> Ulster + generalisable to the wider subnations), and the
> DuckLake + LanceDB + Cognee + marimo dashboards that close the
> gap with `ncca.ie / oide.ie / curriculumonline.ie / examinations.ie`.

## Why

The Cianfhoghlaim platform already has:

- A **public** UoG deep-extraction pipeline
  (`openspec/changes/2026-07-15-cianfhoghlaim-university-deep-extraction-v1` /
  `dlt_sources/british_isles/ireland/education/_university_deep_factory.py`).
- An **authenticated** UoG exam-papers pipeline
  (`openspec/changes/2026-08-23-uog-exam-papers-sso-v1` /
  `dlt_sources/british_isles/ireland/education/university/exam_papers/`)
  with VLM extraction, CocoIndex embeddings, Cognee cross-archive edges.

The **remaining gap** between UoG and the prior primary/secondary
corpus — and between UoG and the British Isles tertiary surface
more broadly — has three facets:

1. **No analogue to `ncca.ie / oide.ie / curriculumonline.ie / examinations.ie`.** The
   primary/secondary corpus has 4 official-doc sources per
   jurisdiction. The tertiary side has only the
   `UniversityDeepExtractionConfig` factory (public catalogue +
   modules + programmes + handbooks + lecturers) and the UoG
   exam-papers source from the prior change. Missing: NUI
   federation, UoG Students' Union, NUI historic archive, the
   **generalised** British Isles tertiary factory that covers all
   university-level institutions across the islands.
2. **No Stage 0 audit.** The existing SEC change uses
   Firecrawl `/agent` to discover the dropdown structure of the
   `examinations.ie` page, but the UoG universe still has only the
   hand-curated `school_subdomain_paths` / `catalogue_paths`. The
   user has called out
   `https://www.universityofgalway.ie/course-information/module/` and
   `https://www.universityofgalway.ie/colleges-and-schools/` as
   examples of the URL surfaces Firecrawl should discover.
3. **No DuckLake destination.** The DLT sources write to local
   DuckDB via the existing `pyproject.toml :: [tool.dlt]` default.
   The Bonneagar `lakehouse` stack (Garage + Lakekeeper + Postgres)
   already exists as `bonneagar/stacks/lakehouse/`; the MotherDuck
   endpoint is wired in the existing marimo notebooks via
   `mo.sql(engine=md:cianfhoghlaim)`. We need to lift the new
   sources onto **all three** destinations with a per-source
   `destination: Literal["local","motherduck","bonneagar"]` flag.

## What changes

| Layer | New artefact |
|---|---|
| Openspec contract | this change (5 sub-specs + design notes) |
| DLT sources | `dlt_sources/.../university/official_docs/uog_official_docs_source.py`, `nui_federation_source.py`, `uog_students_union_source.py` |
| DLT factory | `dlt_sources/british_isles/university/british_isles_tertiary_factory.py` (the British Isles generalisation) |
| BAML schema | `baml_src/british_isles/ireland/education/university/uog_official_docs_extraction.baml` (4 new classes + 4 new enums + 4 new functions) |
| Secret resolver | `bonneagar/.../core/secrets.py` lifts `UoGSsoConfig` to `UniversitySsoConfig` with the same Infisical → `.env` → `op` priority chain |
| Dagster assets | `orchestration/defs/uog_official_docs.py`, `orchestration/defs/nui_federation.py`, `orchestration/defs/uog_students_union.py`, `orchestration/defs/british_isles_tertiary.py` (~15 new assets across 4 sub-groups) |
| VLM extractor | `dlt_sources/.../university/exam_papers/uog_exam_vlm.py::UniversityOfficialDocVLMExtractor` |
| DuckLake destination | `dlt_sources/_lakehouse/destinations.py` (3 destinations: LocalDuckDB, MotherDuck, BonneagarLakehouse) |
| CocoIndex apps | `cocoindex_flows/british_isles/ireland/education/university/{uog_official_docs,nui_federation,uog_students_union}_embedding.py` (3 new v1 Apps — bump app count from 14 → 17) |
| Cognee edges | 4 new cognify rules: `uog_official_doc_describes_module.py`, `uog_su_covers_service.py`, `nui_member_connects.py`, plus the existing `uog_exam_cross_archive.py` |
| Marimo notebooks | 3 sibling marimo dashboards (12_uog_exam_papers.py, 13_nui_federation.py, 14_uog_students_union.py) following the canonical 8-tab BIEP pattern |
| Tests | `tests/uog_official_docs/`, `tests/nui_federation/`, `tests/students_union/`, `tests/british_isles_tertiary/` — 12+ test modules |
| Per-institution runner | `scripts/uog_official_docs_stage0.py` — one-liner for thesis reviewers |

## Non-goals

- **No GDPR / ethics signoff change.** The Stage 0 audit, NUI
  federation, and Students' Union policies are all **publicly
  available authoritative documents** — no auth required.
- **No Mandrake/MCP orchestration changes.** The Stage 0 audit
  calls `BackendRouter.pre_research(base_url, goal, budget_hint=2)`
  per the existing `_university_deep_factory.py` Stage 0 pattern.
- **No change to the existing `2026-08-23-uog-exam-papers-sso-v1`
  capability.** This change adds 5 new BAML classes, 4 new
  enums, 4 new DLT sources, etc. — the prior change's surface is
  unchanged.

## Receipt of approver feedback

N/A — first proposal.
