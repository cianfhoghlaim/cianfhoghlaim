## REMOVED Requirements

### Requirement: Nested legacy `oideachais.data_platform` shim

**Reason**: The nested directory `sruth/oideachais/oideachais/` containing the
`core/` and `data_platform/` sub-packages has zero importers across the entire
Cianfhoghlaim monorepo (verified via `grep -rEn "from oideachais\.oideachais|
from sruth\.oideachais\.oideachais" sruth/ infrastructure/ scripts/` — 0 matches
outside `__pycache__`). The PEP 562 `__getattr__` registration in
`sruth/oideachais/__init__.py:30-44` is itself dead code (will be removed in
phase 5 — `oideachais-audit-phase-5-align-pyproject`).

**Migration**: Any future caller that needs the legacy `oideachais.data_platform`
import path must use the canonical `sruth.oideachais.<sub>` path directly (e.g.,
`sruth.oideachais.dagster_defs.definitions`, `sruth.oideachais.dlt_utils.*`,
`sruth.oideachais.cocoindex_flows.*`). The nested shim was a backward-compat
artifact of the predecessor `bonneagar` project's Python package and is no
longer needed post-`refactor-quadrants-to-sruth` change.

### Requirement: Decoupled `embedding_service` FastAPI microservice

**Reason**: The FastAPI service at `sruth/oideachais/services/embedding_service/main.py`
(8 KB) was superseded by the in-process `oideachais/clients/embedding_client.py`
(local BGE-M3 fallback per the embedding-pipeline skill). Zero importers
across the monorepo. The microservice pattern was abandoned in favour of
in-process embedding at the start of the 2026 stack-align round.

**Migration**: Any caller that needs to generate embeddings MUST use
`sruth.oideachais.clients.embedding_client.EmbeddingClient` (the canonical
in-process client). The local-first fallback chain is documented in
`.agents/skills/embedding-pipeline/SKILL.md`.

### Requirement: Standalone `marimo/ocr_comparison_enhanced.py` notebook

**Reason**: The notebook at `sruth/oideachais/marimo/ocr_comparison_enhanced.py`
(15 KB) is a 1-file stub with zero importers. It was superseded by the
2 notebook collection at `sruth/meaisinfhoghlaim/marimo/` (the
`01_leabharlann_descriptive.py` and `02_dpre_lag_analysis.py` notebooks).

**Migration**: Any caller that needs OCR comparison outputs MUST use
`sruth/meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py` (the canonical
descriptive stats notebook) or the new OCR comparison dagster asset at
`sruth/oideachais/dagster_defs/assets/ocr_comparison_assets.py`.

### Requirement: Standalone `exam_scraper` retry scripts

**Reason**: The 2 scripts at `sruth/oideachais/exam_scraper/{retry_failed.py,
scrape_exam_stats.py}` (8 KB total) were superseded by the DLT source at
`sruth/oideachais/dlt_sources/ireland/examinations.py` (the canonical SEC
examinations ingestion pipeline). Zero importers across the monorepo.

**Migration**: Any caller that needs SEC exam paper ingestion MUST use the
`ireland_examinations` DLT source via
`sruth.oideachais.dlt_sources.ireland.examinations` and the
`ireland/education/exam_materials_assets.py` Dagster asset group.

### Requirement: `PIPELINE_OPERATIONS.md` operations runbook

**Reason**: The 3.7 KB runbook at `sruth/oideachais/PIPELINE_OPERATIONS.md`
(last updated 2026-06-03) is orphaned documentation. It has been superseded by
the canonical operations documentation in `sruth/oideachais/STATUS.md`,
`sruth/oideachais/REFACTORING.md`, and the per-area READMEs (`sruth/oideachais/
api/README.md`, `sruth/oideachais/dagster_defs/README.md`, etc.).

**Migration**: Operators MUST consult `sruth/oideachais/STATUS.md` (the
single source of truth) and `sruth/oideachais/REFACTORING.md` (the refactor
backlog) for current pipeline operations. The openspec workflow
(`openspec list` + `openspec validate`) is the canonical change-management
surface.

### Requirement: Root-level test scripts (`test_api.py`, `test_crawl.py`,
`test_crawl2.py`, `test_full_crawl.py`, `test_all_sources.py`)

**Reason**: The 5 root-level test scripts (1-2 KB each, total 5.7 KB) are
orphaned. They predate the canonical `sruth/oideachais/tests/` test directory
(which has 30+ pytest files and proper conftest). Zero importers; not
discovered by pytest in the canonical test run.

**Migration**: Test authors MUST add new tests under `sruth/oideachais/tests/`
following the existing pattern (per-test-file or per-test-module with
`conftest.py` fixtures). The 5 deleted scripts have no canonical counterpart
because they were ad-hoc smoke tests for one-off crawls.
