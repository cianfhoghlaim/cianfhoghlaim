# Rename `dlt_sources/author_archive/` → `dlt_sources/leabharlann/`

## Why

`dlt_sources/author_archive/` is the **DLT source package** for the personal archive (books, Zotero, Google Takeout, University of Galway coursework, Gemini deep research). All source callables inside it already use the `leabharlann_*` prefix (e.g., `leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`) and the `oideachais-leabharlann` skill describes the package as "leabharlann (personal archive)" — but the directory itself is still named `author_archive/`, creating a name mismatch between the filesystem and the source callable names.

This is Round 11 phase 3a of the cross-quadrant sprawl audit. Phase 1 (delete dead code) + Phase 2A (remove pure duplicates) + Phase 2B (migrate legacy storage + dagster_assets) are complete and pushed.

This change ONLY renames the DLT source package directory. It does NOT rename the Dagster assets (`author_archive_assets.py`), Cognee cognify pass (`cognee_integration/author_archive_cognify.py`), cross-corpus rules (`cognify_rules/author_archive_cross_corpus.py`), OCR chain (`ocr/author_archive_ocr.py`), or pipeline/dataset name prefixes in `dlt_utils/target_factory.py` — those subsystem names are scoped separately and out of scope here.

## What changes

- `sruth/oideachais/dlt_sources/author_archive/` → `sruth/oideachais/dlt_sources/leabharlann/` (10 Python files + 1 config example, 1 `__init__.py`).
- All `from dlt_sources.author_archive import ...` → `from dlt_sources.leabharlann import ...` (test files only — no production code imports this package).
- All `from dlt_sources.author_archive.X import ...` → `from dlt_sources.leabharlann.X import ...` (sub-module imports).
- `sruth/oideachais/STATUS.md` references to the directory path updated.
- `sruth/oideachais/cocoindex_flows/README.md` references updated (if any).
- `openspec/specs/oideachais-pipeline/spec.md` references updated.

## What does NOT change

- `dlt_utils/target_factory.py` — pipeline/dataset name prefixes (`author_archive`, `author_archive_mata`, `author_archive_dev`, etc.) stay unchanged (semantic naming).
- `dagster_defs/assets/author_archive_assets.py` — Dagster asset module name stays.
- `dagster_defs/sensors/author_archive_sensors.py` — Dagster sensor module name stays.
- `ocr/author_archive_ocr.py` — OCR module name stays.
- `cognee_integration/author_archive_cognify.py` — cognify module name stays.
- `cognify_rules/author_archive_cross_corpus.py` — cognify rules module name stays.
- `cocoindex_flows/_v0_archive/author_archive_embedding.py` — already archived in Phase 1, stays.
- DLT source callable names (`leabharlann_books`, `leabharlann_zotero`, etc.) — already correct.
- Asset keys (`oideachais_author_archive`) — stays.
