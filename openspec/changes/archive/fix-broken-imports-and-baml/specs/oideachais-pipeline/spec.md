## MODIFIED Requirements

### Requirement: DLT sources use the canonical HttpClientFactory
The oideachais quadrant SHALL use a single canonical `HttpClientFactory`
class for all HTTP client construction. The canonical class lives at
`oideachais.dlt_sources.common._http_factories.HttpClientFactory`
and MUST be imported via:
```python
from oideachais.dlt_sources.common._http_factories import HttpClientFactory
```

The legacy `oideachais.http_utils` module SHALL NOT exist.
The legacy `oideachais.http_utils.HttpClientFactory` import path
SHALL NOT be used in any new code.

#### Scenario: A new DLT source needs HTTP client construction
- **WHEN** a contributor adds a new `@dlt.source` that requires
  rate-limited HTTP fetching
- **THEN** they MUST import `HttpClientFactory` from
  `oideachais.dlt_sources.common._http_factories`
- **AND** they MUST NOT attempt to import from the non-existent
  `oideachais.http_utils` module

### Requirement: BAML functions use canonical clients from clients.baml
The oideachais quadrant SHALL use the canonical clients declared in
`sruth/oideachais/baml_src/clients.baml` for all BAML function signatures.
The canonical clients are:
- `LitellmClient` (deepseek-chat via `http://litellm:4000/v1`)
- `DeepSeekClient` (deepseek-v4-pro)
- `MiniMaxClient` (minimax-m3)
- `LitellmLongContext` (deepseek-chat, long context)
- `Extractor` (gpt-4o-mini, temperature 0.1)

The legacy `client "litellm"` (lowercase) reference SHALL NOT be used
in any new BAML file.

#### Scenario: A new BAML function is added
- **WHEN** a contributor adds a new BAML function to any
  `sruth/oideachais/baml_src/*.baml` file
- **THEN** the function MUST use one of the canonical clients from
  `clients.baml` via the `client <Name>` syntax
- **AND** it MUST NOT define a new inline `client<llm> ... { ... }`
  block unless adding a new canonical client to `clients.baml`

### Requirement: BAML function ClassifyOfficialMedia is defined
The oideachais quadrant SHALL provide a BAML function
`ClassifyOfficialMedia(ig_username, ig_bio, ig_external_url)` in
`sruth/oideachais/baml_src/site_analysis.baml`. The function MUST return
a boolean or structured classification indicating whether the given
Instagram profile is an official-media account.

#### Scenario: The official-media classifier is invoked
- **WHEN** `dlt_sources/official_media/classifier.py` calls
  `_baml_client.ClassifyOfficialMedia(ig_username, ig_bio, ig_external_url)`
- **THEN** the BAML function MUST exist and MUST return a
  classification
- **AND** the function MUST use `client LitellmClient`

### Requirement: Core utilities SHALL live in dlt_utils, not in the oideachais.core shim
The system MUST define `HNSW_DROP_THRESHOLD = 50` and `get_executor(name="duckdb")`
as canonical constants/functions in `oideachais.dlt_utils.batching` and
`oideachais.dlt_utils.safety` respectively. The shim
`sruth/oideachais/sruth/oideachais/core/__init__.py` MAY exist as a
backward-compat re-export for one release, but new code MUST import
directly from `dlt_utils`.

#### Scenario: A dlt source or Dagster asset needs HNSW_DROP_THRESHOLD
- **WHEN** a contributor needs the HNSW drop threshold constant
- **THEN** they MUST import from `oideachais.dlt_utils.batching`:
  `from oideachais.dlt_utils.batching import HNSW_DROP_THRESHOLD`
- **AND** they MUST NOT import from `oideachais.core` (the shim)

#### Scenario: A Dagster asset needs get_executor
- **WHEN** a contributor needs a single-thread DuckDB executor
- **THEN** they MUST import from `oideachais.dlt_utils.safety`:
  `from oideachais.dlt_utils.safety import get_executor`
- **AND** they MUST NOT import from `oideachais.core` (the shim)
