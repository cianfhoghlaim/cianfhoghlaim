---
name: data-engineering-pipeline-documentation
description: Router for the data engineering pipeline documentation. The single source of truth for the BAML × DLT × Dagster × CocoIndex matrix is `sruth/oideachais/STATUS.md`; the refactor backlog is `sruth/oideachais/REFACTORING.md`; the per-area READMEs (`sruth/oideachais/README.md`, `sruth/oideachais/api/README.md`, etc.) document specific subsystems. Use when you need to add a new BAML extraction, wire a new DLT source, add a new Dagster asset, check the per-source status, or find the right README for a question. Triggers: 'BAML × dlt × Dagster matrix', 'STATUS.md', 'REFACTORING.md', 'pipeline status', 'data engineering doc', 'extraction schema', 'where is the lakehouse README', 'pipeline architecture doc', 'celtic-asset-generation'.
---

# Data Engineering Pipeline Documentation — Router

The Cianfhoghlaim data platform has a canonical set of
documentation files. This skill is the router — find the right
doc for the question.

## The 4 canonical docs

| File | What it is | When to use |
|:--|:--|:--|
| `sruth/oideachais/STATUS.md` | The single source of truth for the BAML × dlt × Dagster × CocoIndex matrix. Every source has a status (DONE / TODO / BLOCKED) and a notes column. | "What's the status of source X?" "Which BAML extractions are wired?" "Which dlt sources have Dagster asset wrappers?" |
| `sruth/oideachais/REFACTORING.md` | The refactor backlog. Every proposed change has a status, an owner, and a deadline. | "What's on the roadmap?" "Who owns refactor Y?" "What's blocked on what?" |
| `sruth/oideachais/README.md` | The quadrant-level overview. Architecture layers, data contracts, the 4 storage layers, the 7 Quick navigation table. | "Where do I add a new DLT source?" "What are the data contracts?" "How does the lakehouse work?" |
| `sruth/oideachais/api/README.md` (and per-area READMEs) | Per-subsystem documentation. | "How do I add a new FastAPI route?" "How does the Dagster webserver start?" |

## The 4 status columns in STATUS.md

Every row in the matrix has these 4 columns:

1. **BAML** — the BAML extraction schema status (DONE / TODO / BLOCKED / DRAFT)
2. **DLT** — the DLT source status (DONE / TODO / BLOCKED / DRAFT)
3. **Dagster** — the Dagster asset wrapper status (DONE / TODO / BLOCKED / DRAFT)
4. **Notes** — free text (the link to the source file, the known issue, the owner)

A row with all 4 columns = DONE means the source is fully
wired and materialising into the lakehouse. Any other row
means there's work to do.

## The 5-stage Celtic asset generation pipeline

The KCG-canonical pipeline for taking a Celtic PDF
(curriculum, exam paper, leabharlann) from raw text to a
queryable, time-aware, vector-indexed dataset is the
5-stage flow in `celtic-asset-generation/SKILL.md`:

1. **BAML extraction** — `sruth/oideachais/baml_src/`
2. **CocoIndex v1 embedding** — `sruth/oideachais/cocoindex_flows/`
3. **Cognee cognify** — `sruth/oideachais/cognee_integration/`
4. **Graphiti temporal memory** — `sruth/oideachais/memory/`
5. **LanceDB vector search** — `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`

The KCG-leabharlann variant adds 1 stage (the secret injection
+ SHA-256 dedup) at the front; see
`kcg-leabharlann-pipeline/SKILL.md`.

## The 4 kinds of "what changed" notes

Every change to the data platform SHOULD update one of:

1. **STATUS.md** — if a source moves from TODO → DONE, or
   vice versa.
2. **REFACTORING.md** — if a new refactor is proposed, an
   existing one is done, or the priority changes.
3. **openspec/changes/<id>/** — if the change is large enough
   to warrant a spec delta (see the openspec workflow).
4. **The README of the affected subsystem** — if the change
   affects the user-facing API or the developer experience.

## Pair this skill with

- `celtic-asset-generation/SKILL.md` — the 5-stage pipeline
- `kcg-leabharlann-pipeline/SKILL.md` — the KCG-leabharlann
  variant
- `oideachais-storage/SKILL.md` — the storage mental model
- `celtic-language-ai/SKILL.md` — the Celtic-language model
  catalog
- `dagster/SKILL.md` — the Dagster asset pattern
- `dlt/SKILL.md` — the DLT source pattern
- `baml/SKILL.md` — the BAML extraction pattern
- `cocoindex/SKILL.md` — the CocoIndex v1 flow pattern

## Cross-references

- `sruth/oideachais/STATUS.md` — the matrix
- `sruth/oideachais/REFACTORING.md` — the backlog
- `sruth/oideachais/README.md` — the quadrant overview
- `openspec/AGENTS.md` — the change-management workflow
