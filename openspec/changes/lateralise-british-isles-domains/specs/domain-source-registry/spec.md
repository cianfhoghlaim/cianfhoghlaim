# Domain Source Registry — Capability Spec

## ADDED Requirements

### Requirement: `sources.yaml` Schema

`oideachais/sources.yaml` SHALL be the single source of truth for every DLT
source in the platform, and `oideachais/dlt_utils/source_factory.py` SHALL
be the single point that turns a YAML entry into runtime artefacts.

The YAML file SHALL have the following top‑level keys:

- `version` (int, currently `2`).
- `defaults` — destination, embedding model, firecrawl, browserbase, schedule, compliance, tests, sensors.
- `nations` — list of `{code, name, jurisdiction}`.
- `kinds` — list of supported DLT source `kind` enum values.
- `sources` — list of source entries (see below).

Each `sources[]` entry SHALL have:

| Key | Required | Type | Notes |
|---|---|---|---|
| `id` | yes | string | `{nation}.{domain}.{entity}` |
| `name` | yes | string | human label |
| `domain` | yes | enum | `education`/`medicine`/`law`/`statistics` |
| `nation` | yes | enum | one of the `nations` codes |
| `kind` | yes | enum | one of the `kinds` |
| `urls` | yes | list[string] | absolute URLs |
| `crawl` | no | object | `include_paths`, `exclude_paths`, `max_pages`, `max_depth` |
| `pagination` | no | object | `kind` ∈ {`offset`,`cursor`,`page_number`}, `page_size` |
| `incremental` | no | object | `cursor_path`, `field`, `initial` |
| `asset_key` | yes | list[string] | `["{nation}","{domain}","{entity_slug}",...]` |
| `embedding` | no | object | `table`, `kind` |
| `kg` | no | object | `dataset`, `edges` |
| `schedule` | no | object | `cron`, `timezone` |
| `sensors` | no | list[string] | sensor names to attach |
| `compliance` | no | object | `licence`, `contact`, `robots_txt` |

#### Scenario: A valid entry parses
- **GIVEN** the canonical entry in `oideachais/sources.yaml` for `ni.education.ccea`
- **WHEN** `SourceFactory.from_yaml(...)` is called
- **THEN** the entry is parsed and `factory.source("ni.education.ccea")` returns a callable DLT source

#### Scenario: An invalid entry is rejected
- **GIVEN** an entry whose `id` is `xy.education.foo` (unknown `nation`)
- **WHEN** `SourceFactory.from_yaml(...)` is called
- **THEN** a `pydantic.ValidationError` is raised listing the offending field

### Requirement: SourceFactory Contract

The factory SHALL expose the following methods:

```python
SourceFactory.from_yaml(path: Path) -> SourceFactory
factory.source(id: str) -> Callable              # dlt source
factory.dlt_asset(id: str) -> Any                # @dlt_assets decorator
factory.dagster_asset(id: str) -> Any            # @asset
factory.lance_table(id: str) -> str              # lance namespace.table
factory.cognee_dataset(id: str) -> str          # cognee dataset name
factory.marimo_path(id: str) -> Path             # notebooks/dashboards/...
factory.tests_path(id: str) -> Path              # tests/dlt_sources/...
```

#### Scenario: All seven methods return coherent values for the same id
- **GIVEN** a valid `id`
- **WHEN** each of the seven methods is called
- **THEN** the returned values are mutually consistent (same `nation`, same `domain`, same `entity_slug`)

#### Scenario: A coverage report shows missing artefacts
- **GIVEN** a source in YAML but no corresponding DLT source file
- **WHEN** the operator runs `python -m oideachais.sources.sources_validation`
- **THEN** the report flags the missing file
