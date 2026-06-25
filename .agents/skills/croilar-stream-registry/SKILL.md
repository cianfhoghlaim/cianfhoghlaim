---
name: croilar-stream-registry
description: The KCG Croílár Stream-registry pattern in `sruth/croilar/_shared/streams.py` + `sruth/croilar/_shared/config/settings.py`. Covers the 5 aleyum→croilar alias collapses (env prefix `ALEYUM_`→`STREAMS_`, `aleyum.duckdb`→`croilar.duckdb`, `aleyum-data`→`croilar-data` R2 bucket, `aleyum_local`→`croilar_local` pipeline name, `aleyum_catalog.duckdb`→`croilar_catalog.duckdb`), the `StreamSettings` Pydantic BaseSettings (the canonical config surface), the 12 stream-driven Dagster assets (music, teaching, cv, research), the `Stream` Pydantic model (id + name + cron + BAML extraction functions + local_only flag), the `sruth/croilar/config/sources.yaml` registry file (the declarative source-of-truth), and the add-a-new-stream workflow. Use when adding a new stream, debugging a pipeline name mismatch, onboarding a new croilar data source, or asking "what is the aleyum→croilar cleanup mandate?".
---

# Croílár Stream Registry

## Purpose

The `sruth/croilar/_shared/streams.py` + `sruth/croilar/_shared/config/settings.py`
files house the **Stream-registry pattern** — the canonical config
surface for the croilar portfolio. The pattern was introduced in
round 11 of the multi-quadrant refactor plan (the
`croilar-aleyum-to-streams-cleanup-v1` openspec change) to retire
the legacy `AleyumSettings` class + the `ALEYUM_` env prefix.

This skill captures the 5 aleyum→croilar alias collapses, the
`StreamSettings` Pydantic BaseSettings, the 12 stream-driven
Dagster assets, the `Stream` Pydantic model, the
`sruth/croilar/config/sources.yaml` registry file, and the
add-a-new-stream workflow.

## When to use this skill

Use when you need to:

- "Add a new stream to the croilar portfolio"
- "Debug a pipeline name mismatch"
- "Onboard a new croilar data source"
- "Understand the aleyum→croilar cleanup mandate"
- "Switch from `ALEYUM_*` env vars to `STREAMS_*` env vars"
- "Find the canonical config surface for the croilar pipelines"

## The 5 aleyum→croilar alias collapses (the round 11 mandate)

| Legacy name | Canonical name | File |
|:--|:--|:--|
| `ALEYUM_` env prefix | `STREAMS_` env prefix | `sruth/croilar/_shared/config/settings.py` |
| `aleyum.duckdb` (DB file) | `croilar.duckdb` | `sruth/croilar/pipelines/shared/destinations.py` |
| `aleyum-data` (R2 bucket) | `croilar-data` | `sruth/croilar/pipelines/shared/destinations.py` + `ducklake.py` |
| `aleyum_local` (DLT pipeline) | `croilar_local` | `sruth/croilar/pipelines/shared/destinations.py` |
| `aleyum_catalog.duckdb` | `croilar_catalog.duckdb` | `sruth/croilar/pipelines/shared/destinations.py` + `ducklake.py` |

Plus:

- `ALEYUM_ENV` env var → `CROILAR_ENV`
- `ALEYUM_R2_BUCKET = "aleyum-assets"` constant (in `r2_client.py`) → removed
- `AleyumSettings` deprecated alias (in `settings.py`) → removed

The 5 collapses retire the `aleyum` name in favour of `croilar`.
The `aleyum` persona name (in `sruth/croilar/config/personas.yaml` +
`sruth/croilar/apps/web/`) is preserved (it's a 1-persona identifier,
not a 5-alias registry).

## The `StreamSettings` Pydantic BaseSettings (the canonical config)

The `StreamSettings` class is the only API. It:

- Loads stream definitions from `sruth/croilar/config/sources.yaml`
- Exposes a typed `streams: list[Stream]` accessor
- Has a `STREAMS_` env prefix
- Caches the result via `@lru_cache` (the `get_settings()` factory)

```python
# sruth/croilar/_shared/config/settings.py
from croilar._shared.config.settings import StreamSettings, get_settings

settings = get_settings()
all_streams = settings.streams()  # list[Stream]
spotify = settings.stream("music__spotify")  # single Stream by id
```

The `StreamSettings` class has 14 fields:

| Field | Default | Purpose |
|:--|:--|:--|
| `sources_yaml_path` | `DEFAULT_SOURCES_PATH` | The YAML registry file |
| `r2_bucket` | `cianfhoghlaim-public` | The shared R2 bucket |
| `lancedb_uri` | `~/.lancedb/croilar` | The LanceDB root |
| `duckdb_root` | `~/.duckdb/croilar` | The DuckDB root |
| `default_agent_port` | `7774` | The croilar agent port |
| `embedding_model` | `BAAI/bge-m3` | The BGE-M3 embedding model |
| `embedding_batch_size` | `256` | The BGE-M3 batch size |
| `browser_backend` | `stagehand` | The browser automation backend |
| `browserbase_api_key` | (env) | The Browserbase API key |
| `browserbase_project_id` | (env) | The Browserbase project id |
| `default_agent_framework` | `adk` | `adk` or `agno` |
| `agent_complexity_threshold` | `0.5` | The complexity threshold |
| `datadog_enabled` | `False` | The Datadog observability toggle |
| `langfuse_enabled` | `False` | The Langfuse observability toggle |

## The `Stream` Pydantic model (the per-stream contract)

The `Stream` model lives in `sruth/croilar/_shared/streams.py`:

```python
# sruth/croilar/_shared/streams.py
from pydantic import BaseModel
from typing import Callable

class Stream(BaseModel):
    id: str                           # "music__spotify"
    name: str                         # "Spotify Catalogue"
    description: str                  # 1-line description
    cron: str                         # "0 3 * * *" (daily 03:00)
    source_module: str                # "croilar.pipelines.spotify.source"
    source_factory: str               # "spotify_source"
    baml_function: str                # "ExtractSpotifyTrack"
    dataset_name: str                 # "music_data"
    local_only: bool = False          # True for CV PDFs / identity docs
    embedding_required: bool = True   # True for semantic-search streams
```

The 12 default streams (4 music, 3 teaching, 3 cv, 2 research):

- `music__spotify` (Spotify Catalogue — daily 03:00)
- `music__soundcloud` (SoundCloud Catalogue — daily 03:30)
- `music__labels` (Label Catalogue — daily 04:00)
- `music__artwork` (Album Artwork — daily 04:30)
- `teaching__github` (Teaching GitHub — weekly Sunday 04:00)
- `teaching__linkedin` (LinkedIn Teaching — weekly Sunday 04:30)
- `teaching__researchgate` (ResearchGate Teaching — weekly Sunday 05:00)
- `cv__cv` (CV PDFs — weekly Sunday 06:00, `local_only=True`)
- `cv__filesystem` (CV Filesystem Index — weekly Sunday 06:30)
- `cv__search_index` (CV Search Index — weekly Sunday 07:00)
- `research__os` (Open Source Research — monthly 1st 05:00)
- `research__identity` (Identity Documents — monthly 1st 06:00, `local_only=True`)

## The `sruth/croilar/config/sources.yaml` registry file (the declarative source)

The 12 streams are declared in `sruth/croilar/config/sources.yaml`:

```yaml
# sruth/croilar/config/sources.yaml
streams:
  - id: music__spotify
    name: Spotify Catalogue
    description: Daily Spotify catalogue + audio features ingestion
    cron: "0 3 * * *"
    source_module: croilar.pipelines.spotify.source
    source_factory: spotify_source
    baml_function: ExtractSpotifyTrack
    dataset_name: music_data
    local_only: false
    embedding_required: true

  - id: cv__cv
    name: CV PDFs
    description: Weekly CV PDF ingestion from the author directory
    cron: "0 4 * * 0"
    source_module: croilar.pipelines.cv.source
    source_factory: cv_pdf_source
    baml_function: ExtractCvAchievement
    dataset_name: cv_data
    local_only: true
    embedding_required: true

  # ... 10 more streams
```

The YAML is loaded at startup via `StreamSettings.streams()`.

## The 12 stream-driven Dagster assets

The `sruth/croilar/dagster_assets/` module exposes 12 stream-driven assets:

- 4 music: `music__spotify`, `music__soundcloud`, `music__labels`, `music__artwork`
- 3 teaching: `teaching__github`, `teaching__linkedin`, `teaching__researchgate`
- 3 CV: `cv__cv`, `cv__filesystem`, `cv__search_index`
- 2 research: `research__os`, `research__identity`

The asset materialization:

```python
# sruth/croilar/dagster_assets/dlt_assets.py
@asset
def music__spotify(context: AssetExecutionContext) -> MaterializeResult:
    stream = get_settings().stream("music__spotify")
    pipeline = stream_to_pipeline(stream)  # the canonical factory
    load_info = pipeline.run(stream_to_source(stream)())
    return MaterializeResult(metadata={"load_info": str(load_info)})
```

The `stream_to_pipeline` + `stream_to_source` factories are
defined in `sruth/croilar/_shared/streams.py` and use the
`create_duckdb_destination` / `create_ducklake_destination`
factories from `sruth/croilar/pipelines/shared/destinations.py`.

## The 3 cron schedules (the orchestrator)

| Schedule | Cadence | Streams |
|:--|:--|:--|
| `daily_music_schedule` | 03:00 daily | `music__spotify`, `music__soundcloud`, `music__labels`, `music__artwork` |
| `weekly_cv_schedule` | Sunday 04:00 | `teaching__*`, `cv__*` |
| `monthly_identity_schedule` | 1st of month 05:00 | `research__identity` |

The schedules live at `sruth/croilar/dagster_assets/schedules.py`.

## The 9 BAML extraction functions (the 12 streams)

The 12 streams consume 9 BAML functions in `sruth/croilar/baml/`:

- `ExtractSpotifyTrack`, `ExtractSoundCloudTrack`, `ExtractArtworkAnalysis`
- `ExtractLinkedInProfile`, `ExtractResearchGatePublication`
- `ExtractTeachingPlacement`, `ExtractTeachingFeedback`
- `ExtractCvAchievement`, `ExtractIdentityDocument`

## The 4 R2 destinations (the storage)

- `croilar-data` — the per-tenant R2 bucket (formerly `aleyum-data`)
- `cianfhoghlaim-public` — the shared public R2 bucket (the default)
- `local://` — the no-upload sentinel for `local_only=True` streams
- `R2_LOCAL_ONLY=true` — the env var to force local-only mode globally

## Worked example: add a new stream

1. Add the stream to `sruth/croilar/config/sources.yaml`:

   ```yaml
   - id: research__github_stars
     name: GitHub Stars
     description: Daily GitHub stars + repo metadata ingestion
     cron: "0 5 * * *"
     source_module: croilar.pipelines.github.source
     source_factory: github_stars_source
     baml_function: ExtractGitHubRepo
     dataset_name: research_data
     local_only: false
     embedding_required: true
   ```

2. Add the source module at
   `sruth/croilar/pipelines/github/source.py`:

   ```python
   import dlt

   @dlt.resource(write_disposition="replace")
   def github_stars_repo():
       # the canonical source
       ...

   def github_stars_source() -> list:
       return [github_stars_repo]
   ```

3. Add the Dagster asset at
   `sruth/croilar/dagster_assets/dlt_assets.py`:

   ```python
   @asset
   def research__github_stars(context):
       stream = get_settings().stream("research__github_stars")
       pipeline = stream_to_pipeline(stream)
       load_info = pipeline.run(stream_to_source(stream)())
       return MaterializeResult(metadata={"load_info": str(load_info)})
   ```

4. Add the schedule at
   `sruth/croilar/dagster_assets/schedules.py`:

   ```python
   daily_research_schedule = ScheduleDefinition(
       name="daily_research_schedule",
       cron_schedule="0 5 * * *",
       job=define_asset_job(
           name="daily_research_job",
           selection=["research__github_stars"],
       ),
   )
   ```

5. Update the openspec change
   `croilar-aleyum-to-streams-cleanup-v1` to document the
   13th stream.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `KeyError: stream 'X' not registered` | The stream id is not in `sources.yaml` | Add the stream id to `sruth/croilar/config/sources.yaml` |
| The `ALEYUM_*` env var is silently ignored | The legacy prefix has been retired | Switch to the `STREAMS_*` env prefix |
| The R2 upload fails with `403` | The bucket name is wrong (still using `aleyum-data`) | Use `croilar-data` (or the `STREAMS_R2_BUCKET` env var) |
| The Dagster asset fails with `aleyum_local not found` | The pipeline name still references the old name | Update the DLT pipeline name to `croilar_local` |
| The CV PDF leaks to R2 | The `local_only` flag is missing | Add `local_only: true` to the stream declaration |

## Cross-references

- `sruth/croilar/_shared/streams.py` — the `Stream` model + the `list_streams` loader
- `sruth/croilar/_shared/config/settings.py` — the `StreamSettings` Pydantic BaseSettings
- `sruth/croilar/config/sources.yaml` — the 12 default streams
- `sruth/croilar/pipelines/shared/destinations.py` — the 3 DLT destination factories
- `sruth/croilar/pipelines/shared/ducklake.py` — the DuckLake catalog
- `sruth/croilar/pipelines/shared/r2_client.py` — the R2 client
- `sruth/croilar/dagster_assets/dlt_assets.py` — the 12 stream-driven assets
- `sruth/croilar/dagster_assets/schedules.py` — the 3 cron schedules
- `sruth/croilar/baml/` — the 9 BAML extraction functions
- `openspec/specs/croilar-data-engineering/spec.md` — the canonical spec
- `openspec/changes/croilar-aleyum-to-streams-cleanup-v1/` — the round 11 openspec change
