"""Per-board England CocoIndex v1 Embedding Apps (BIEP v2).

Per the 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 change.

3 CocoIndex v1 Apps (one per awarding body):
    - england_aqa_education_embedding.py
    - england_ocr_education_embedding.py
    - england_edexcel_education_embedding.py

Each App conforms to the R1–R4 v1 conformance contract:
- **R1** — `from .._shared._lifespan import shared_lifespan`
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- **R3** — `app = coco.App(coco.AppConfig(name=...))` at module scope
- **R4** — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

The 3 Apps share the `_lifespan` from `cocoindex/_shared/_lifespan.py`
(per REFACTORING.md item 12). Each App's `app` is its own coco.App instance
so they can be materialised independently by the 81 Dagster assets.
"""
