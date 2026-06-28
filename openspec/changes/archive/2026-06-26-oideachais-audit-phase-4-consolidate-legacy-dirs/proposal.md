# Phase 4 — Consolidate legacy flat files at `dlt_sources/` root

## Why

After Phases 3A-3E the `dlt_sources/` tree has 8 country-first subdirs (`ie/`,
`ni/`, `en/`, `sct/`, `wls/`, `iom/`, `jey/`, `ggy/`) plus `cross/bunchloch/`
— but 5 legacy flat files still sit at the package root:

- `dlt_sources/tearma.py` — 2 `@dlt.source` defs (`tearma_source`,
  `tearma_search_source`) — must split per Phase 3D pattern
- `dlt_sources/crawl_utils.py` — utility module (3 importers)
- `dlt_sources/http_client.py` — utility module (1 stub docstring reference)
- `dlt_sources/pagination.py` — utility module (1 internal importer)
- `dlt_sources/dlthub_projects.py` — 1 importer (`apply_dlthub_wrappers`)

The country-first `dlt_sources/{nation}/{domain}/{entity}.py` contract is
broken by these flat files. The split for `tearma.py` follows the same
template as Phase 3D (per-source file + sibling `_helpers.py` for shared
private state + module constants). The utility files move to their canonical
homes (`common/` for shared helpers, `dlt_utils/` for pipeline utilities).

## What changes

1. **`dlt_sources/tearma.py` → 3 canonical files** at `ie/culture/`:
   - `dlt_sources/ie/culture/tearma.py` (exports `tearma_source`)
   - `dlt_sources/ie/culture/tearma_search.py` (exports `tearma_search_source`)
   - `dlt_sources/ie/culture/_tearma_helpers.py` (shared:
     `_get_tearma_factory`, `_parse_tearma_tsv`, `_download_tearma_export`,
     `_search_tearma_api`, `_load_tearma_terms`, `TerminologyLinker`)

2. **`dlt_sources/crawl_utils.py` → `dlt_sources/common/crawl_utils.py`**
   (no domain-specific items — pure utility, sibling of `incremental.py`,
   `content_deduplication.py`, etc.)

3. **`dlt_sources/http_client.py` → `dlt_sources/common/http_client.py`**

4. **`dlt_sources/pagination.py` → `dlt_sources/common/pagination.py`**

5. **`dlt_sources/dlthub_projects.py` → `dlt_utils/dlthub_projects.py`**
   (matches the existing `dlt_utils/` package — already the home of
   `batching.py`, `destinations.py`, `mixins.py`, etc.)

## Impact

- 5 flat files removed from `dlt_sources/` root
- 4 utility files moved into `dlt_sources/common/` (sibling to existing
  `_http_factories.py`, `incremental.py`, etc.)
- 1 utility file moved to `dlt_utils/` (matches `batching.py`, `destinations.py`)
- 3 new canonical source files at `ie/culture/` (1 per source + 1 helpers)
- 6 importer files updated:
  - `dlt_sources/ie/education/curriculum.py:600`
  - `dlt_sources/ie/education/curriculum_source.py:600`
  - `dlt_sources/ie/education/exam_source_update.py:2`
  - `dlt_sources/dagster_defs/factories.py:325`
  - `dlt_sources/tests/dlt_sources/test_integration.py:100,111,123,135,148,168`
  - `dlt_sources/ie/culture/__init__.py` (re-exports new tearma sub-modules)

## Out of scope (deferred)

- Pre-existing absolute-namespace imports in
  `tests/dlt_sources/test_integration.py` (`from oideachais.dlt_sources.crawl_utils import …`) —
  these imports wouldn't work today (no `oideachais` package at root).
  Phase 4 only fixes the path; the absolute-namespace rewrite is a
  separate change (`fix-broken-imports-and-baml` in the queue).
- `from settings import settings` + `from shared.utils import …` in
  `http_client.py` — pre-existing fragility. The `_shared_utils_stub.py`
  already provides fallback types, so the module loads but the import
  itself still fails. **Not fixed in Phase 4** — defer to the same
  `fix-broken-imports-and-baml` change.
- `crown_dependencies/` (Phase 3E) — already done.
- `dlt_sources/law/`, `dlt_sources/site_analysis/`, `dlt_sources/official_media/`
  — pre-existing fragility, deferred indefinitely per Phase 3D decision.
- Top-level dirs at `sruth/oideachais/` (celtic/, subjects/, bunchloch/,
  geospatial/, etc.) — out of scope per original constraint.

## Validation

- `openspec validate oideachais-audit-phase-4-consolidate-legacy-dirs --strict` MUST pass
- 3/3 new `ie/culture/tearma*` source imports succeed
- 2/2 new `tearma_source` + `tearma_search_source` re-exports from `ie/culture/__init__.py` succeed
- 3/3 utility file imports succeed (`common.crawl_utils`, `common.http_client`, `common.pagination`)
- 1/1 `dlt_utils.dlthub_projects` import succeeds
- 4/4 importers (`curriculum.py`, `curriculum_source.py`, `exam_source_update.py`, `factories.py`) rewire correctly
- 25/25 Phase 3D imports + 3/3 Phase 3E imports + 3/3 Phase 4 imports = 31/31 canonical imports OK
- `mise run lint:skills` → 138/138 still pass (no skill changes)
