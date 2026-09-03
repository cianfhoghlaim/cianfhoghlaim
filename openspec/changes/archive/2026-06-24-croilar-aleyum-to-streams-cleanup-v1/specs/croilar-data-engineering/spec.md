## ADDED Requirements

### Requirement: Aleyum-to-croilar cleanup mandate

The Croílár data-engineering layer SHALL NOT reference the
legacy `aleyum` name in code, env vars, config defaults, or
documentation (with the exception of the `aleyum` persona
identifier in `sruth/croilar/config/personas.yaml` + the persona
site routes, which are 1-persona identifiers, not 5-alias
registry entries). The 5 collapsed aliases are:

1. **Env prefix** — `ALEYUM_*` env vars SHALL be renamed to
   `STREAMS_*` (already partially retired in
   `sruth/croilar/_shared/config/settings.py`)
2. **DuckDB file** — the `./data/aleyum.duckdb` default SHALL
   be renamed to `./data/croilar.duckdb`
3. **R2 bucket** — the `aleyum-data` R2 bucket default SHALL
   be renamed to `croilar-data` (plus the legacy
   `aleyum-assets` R2 bucket constant in
   `sruth/croilar/pipelines/shared/r2_client.py` SHALL be removed)
4. **DLT pipeline names** — the 4 `aleyum_local` /
   `aleyum_ducklake` / `aleyum_vectors` pipeline names SHALL
   be renamed to `croilar_local` / `croilar_ducklake` /
   `croilar_vectors`
5. **DuckLake catalog path** — the `./data/aleyum_catalog.duckdb`
   default SHALL be renamed to `./data/croilar_catalog.duckdb`

Plus: the deprecated `AleyumSettings` alias in
`sruth/croilar/_shared/config/settings.py` SHALL be removed (the
`StreamSettings` Pydantic BaseSettings is the only API).
Plus: the `ALEYUM_ENV` env var SHALL be renamed to
`CROILAR_ENV`.

#### Scenario: A pipeline name no longer references aleyum

- **WHEN** a developer greps the croilar data engineering
  layer for `aleyum` (case-insensitive)
- **THEN** no matches SHALL be found in code, env vars, or
  config defaults (only the `aleyum` persona identifier in
  `sruth/croilar/config/personas.yaml` + the persona site routes
  SHALL match)

### Requirement: Stream-registry canonical config surface

The Croílár data-engineering layer SHALL expose a canonical
config surface via the `StreamSettings` Pydantic BaseSettings
class at `sruth/croilar/_shared/config/settings.py`. The
`StreamSettings` class:

- Loads stream definitions from `sruth/croilar/config/sources.yaml`
- Exposes a typed `streams()` accessor + a `stream(id)` lookup
- Uses a `STREAMS_` env prefix (the canonical env var namespace)
- Caches the result via `@lru_cache` (the `get_settings()`
  factory)

The `Stream` Pydantic model at `sruth/croilar/_shared/streams.py`
defines the per-stream contract:

- `id: str` — the stream id (e.g. "music__spotify")
- `name: str` — the stream name (e.g. "Spotify Catalogue")
- `description: str` — a 1-line description
- `cron: str` — the cron schedule (e.g. "0 3 * * *")
- `source_module: str` — the Python module path
- `source_factory: str` — the factory function name
- `baml_function: str` — the BAML extraction function
- `dataset_name: str` — the DuckDB dataset name
- `local_only: bool` — True for sensitive corpora (CV PDFs,
  identity documents)
- `embedding_required: bool` — True for semantic-search streams

The 12 default streams SHALL be declared in
`sruth/croilar/config/sources.yaml`:

- 4 music: `music__spotify`, `music__soundcloud`,
  `music__labels`, `music__artwork`
- 3 teaching: `teaching__github`, `teaching__linkedin`,
  `teaching__researchgate`
- 3 CV: `cv__cv`, `cv__filesystem`, `cv__search_index`
- 2 research: `research__os`, `research__identity`

#### Scenario: A developer adds a new stream via the YAML

- **WHEN** a developer adds a new stream id to
  `sruth/croilar/config/sources.yaml`
- **THEN** `StreamSettings.streams()` returns the new stream
  in the list
- **AND** `StreamSettings.stream("<new-id>")` returns the
  new `Stream` instance
- **AND** the corresponding Dagster asset materializes the
  new stream on its cron schedule
