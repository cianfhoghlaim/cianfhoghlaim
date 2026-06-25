# Oideachais Audit Phase 1 — Delete Dead Code

## Why

Round 11 of the multi-quadrant sprawl audit identified confirmed-dead
code in `sruth/oideachais/`:

- **Nested legacy shim dir** `sruth/oideachais/oideachais/` containing `core/` + `data_platform/` subdirs — the source of the legacy `oideachais.data_platform` PEP 562 `sys.modules` registration in `sruth/oideachais/__init__.py:30-44`. **Zero importers across the entire monorepo.** The PEP 562 shim is itself dead code.
- **Dead FastAPI embedding microservice** at `sruth/oideachais/services/embedding_service/` (8 KB) — superseded by `oideachais/clients/embedding_client.py` (local BGE-M3 fallback). **Zero importers.**
- **Dead 1-file marimo stub** `sruth/oideachais/marimo/ocr_comparison_enhanced.py` (15 KB) — superseded by `sruth/meaisinfhoghlaim/marimo/`. **Zero importers.**
- **Dead 2-script exam scraper** at `sruth/oideachais/exam_scraper/` (8 KB) — replaced by `oideachais/dlt_sources/ireland/examinations.py`. **Zero importers.**
- **Empty `downloads/curriculum_pdfs/`** mount point.
- **Orphaned binary** `sruth/oideachais/leaving_cert_timetable.pdf` (270 KB) — no importers.
- **5 orphaned root-level test scripts** (`test_api.py`, `test_crawl.py`, `test_crawl2.py`, `test_full_crawl.py`, `test_all_sources.py`) — all 0-byte to 2 KB; replaced by `tests/`.
- **Orphaned doc** `sruth/oideachais/PIPELINE_OPERATIONS.md` (3.7 KB) — last updated 2026-06-03, superseded by `STATUS.md`.

**Total: ~100 KB of code/docs + 270 KB binary deleted, 0 LOC moved.**

## What changes

### Deletions (10 items)

| # | Path | Size | Confirmed dead because |
|:-:|:--|--:|:--|
| 1 | `sruth/oideachais/oideachais/` | 4 dirs | 0 importers; legacy shim registration in `__init__.py:30-44` |
| 2 | `sruth/oideachais/services/embedding_service/` | 8 KB | 0 importers; superseded by `clients/embedding_client.py` |
| 3 | `sruth/oideachais/marimo/` | 15 KB | 0 importers; superseded by `sruth/meaisinfhoghlaim/marimo/` |
| 4 | `sruth/oideachais/exam_scraper/` | 8 KB | 0 importers; superseded by `dlt_sources/ireland/examinations.py` |
| 5 | `sruth/oideachais/downloads/curriculum_pdfs/` | 0 B | empty dir |
| 6 | `sruth/oideachais/leaving_cert_timetable.pdf` | 270 KB | 0 importers |
| 7 | `sruth/oideachais/PIPELINE_OPERATIONS.md` | 3.7 KB | orphaned doc |
| 8 | `sruth/oideachais/test_api.py` | 71 B | orphaned test |
| 9 | `sruth/oideachais/test_crawl.py` | 1.0 KB | orphaned test |
| 10 | `sruth/oideachais/test_crawl2.py` | 1.1 KB | orphaned test |
| 11 | `sruth/oideachais/test_full_crawl.py` | 1.6 KB | orphaned test |
| 12 | `sruth/oideachais/test_all_sources.py` | 1.9 KB | orphaned test |

### Deferred to later phases (NOT deleted in this change)

- `sruth/oideachais/dashboard/` — full Vite + Convex app, ~1 MB. Needs separate user decision (delete vs migrate to `croilar/apps/portal/` pattern).
- `sruth/oideachais/settings.py` — **NOT dead**: imported by `infrastructure/observability/logging.py:21`. Migration to canonical env prefix deferred to phase 5.
- `sruth/oideachais/agent_os/` — **LIVE**: FastAPI A2A middleware (referenced by `infrastructure/stacks/agent-os/`).
- `sruth/oideachais/apps/web/` — **LIVE**: canonical TanStack Start frontend per `sruth/oideachais/AGENTS.md`.
- `sruth/oideachais/samplaí/` — **LIVE**: Celtic language samples (6 dirs + 1 yaml).
- `sruth/oideachais/subjects/` — **LIVE**: UoG subject manifest + baml_context.

## Out of scope

- Phase 2 (consolidate 5 duplicate surface pairs)
- Phase 3 (relocate 14 misplaced dlt sources)
- Phase 4 (consolidate 15 legacy dirs)
- Phase 5 (align pyproject.toml + drop legacy data_platform shim)
- All meaisinfhoghlaim/tuatha/croilar/infrastructure/spaces refactors (changes #6-18 in the Round 11 audit)

## Risk

**LOW.** All deletions are confirmed 0-importer. No DAG asset, no FastAPI route, no Dagster sensor depends on them. The only consumer of the nested `oideachais/oideachais/` shim was the now-removed PEP 562 registration which itself is also dead (verified).

## Validation

- `mise run lint:skills` — must still pass 108/108
- `python -c "import sruth.oideachais"` — must still succeed (the deleted dirs are NOT on the import path)
- `openspec validate oideachais-audit-phase-1-delete-dead-code --strict` — must pass
- `grep -rEn "oideachais.oideachais|data_platform\.dagster_defs" sruth/ infrastructure/` — must return 0 matches after the change (the data_platform reference in `__init__.py:30-44` will be dropped in phase 5)

## Impact

- **Repository size**: -310 KB (270 KB PDF + ~40 KB code/docs)
- **Directory count**: 61 → 56 (-5 dirs)
- **File count**: -8 top-level files
- **Build time**: negligible (no rebuild needed; deleted files are not imported)
- **Test coverage**: -5 orphaned root-level tests (already uncovered; not in `tests/`)
