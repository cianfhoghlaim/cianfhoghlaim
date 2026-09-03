# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: Legacy flat files consolidated at canonical paths

The `dlt_sources/` package MUST NOT contain flat `.py` files at its root
that define `@dlt.source` functions or shared utility modules. Every
DLT source MUST live at a country-first canonical path
`dlt_sources/{nation}/{domain}/{entity}.py`. Every shared utility
module MUST live at either `dlt_sources/common/{name}.py` (for DLT
helpers) or `dlt_utils/{name}.py` (for pipeline config).

#### Scenario: tearma source split into per-source files

- **WHEN** the `tearma` corpus is queried
- **THEN** the `tearma_source` function MUST be importable from
  `dlt_sources.ie.culture.tearma`
- **AND** the `tearma_search_source` function MUST be importable from
  `dlt_sources.ie.culture.tearma_search`
- **AND** shared private state + module constants + helpers MUST live at
  `dlt_sources.ie.culture._tearma_helpers`
- **AND** the legacy `dlt_sources/tearma.py` flat file MUST NOT exist

#### Scenario: utility modules live at dlt_sources/common/

- **WHEN** a downstream DLT source needs `crawl_utils`, `http_client`, or
  `pagination`
- **THEN** those modules MUST be importable from
  `dlt_sources.common.{crawl_utils,http_client,pagination}`
- **AND** the legacy flat files at `dlt_sources/{crawl_utils,http_client,
  pagination}.py` MUST NOT exist
- **AND** the modules MUST sit alongside the existing
  `dlt_sources/common/` siblings (`_http_factories.py`, `incremental.py`,
  `content_deduplication.py`, `curriculum_registry.py`,
  `firecrawl_source.py`, `source_adapters.py`,
  `_shared_utils_stub.py`)

#### Scenario: pipeline config lives at dlt_utils/

- **WHEN** a DLT source needs `apply_dlthub_wrappers`
- **THEN** it MUST be importable from `dlt_utils.dlthub_projects`
- **AND** the legacy `dlt_sources/dlthub_projects.py` flat file MUST NOT
  exist
- **AND** the `dlt_utils/` package MUST re-export
  `apply_dlthub_wrappers` from its `__init__.py`

#### Scenario: importers rewire to canonical paths

- **WHEN** the 4 importers
  (`dlt_sources/ie/education/curriculum.py`,
  `dlt_sources/ie/education/curriculum_source.py`,
  `dlt_sources/ie/education/exam_source_update.py`,
  `dlt_sources/dagster_defs/factories.py`,
  `dlt_sources/tests/dlt_sources/test_integration.py`)
  reference the moved modules
- **THEN** they MUST import from the canonical paths
  (`dlt_utils.dlthub_projects`,
  `dlt_sources.ie.culture.tearma`,
  `dlt_sources.common.crawl_utils`)
- **AND** the legacy `dlt_sources.{dlthub_projects,tearma,crawl_utils,
  http_client,pagination}` paths MUST NOT be referenced
