# Change: croilar-personas-to-streams

## Why

The Croílár personal-portfolio monorepo currently models its data architecture around three hard-coded **personas** — `aleyum` (music), `cianfhoghlaim` (teaching/research), and `carlcashman` (third-party).

The persona identity leaks into every layer:

- `pipelines/linkedin/source.py` hard-codes `flow_id="carlcashman"` as the default
- `baml/linkedin_profile_extraction.baml` declares `flowId: aleyum | cianfhoghlaim | carlcashman`
- `_shared/config/settings.py` defines `AleyumSettings` — a settings class named after one persona
- `dagster_assets/dlt_assets.py` hard-codes `username="aleyummusic"`, `artist_slug="aleyum"`
- `agent_os/main.py` calls `init_config(service_name="aleyum", service_port=7774)`
- Every R2 bucket, DuckDB path, and Docker volume is named `aleyum-*`
- i18n `packages/i18n/src/index.ts` imports `aleyum` / `cianfhoghlaim` JSON files
- BetterAuth has 4 orgs (aleyum, cianfhoghlaim, croilar-admin, croilar-collab)
- One marimo notebook per persona under `notebooks/aleyum/`, `notebooks/cianfhoghlaim/`

This blocks three concrete changes the author needs to land:

1. **Consolidating all author profile sources onto a single identity** — *Cian Mac an Déisigh Uí Liatháin*. The author has a unified personal/professional identity (one GitHub `cianfhoghlaim`, one LinkedIn, one ResearchGate) but the current `flow_id` taxonomy makes it impossible to model "one human with many streams" without pretending each stream is a different person.
2. **Adding a new DLT filesystem source** that ingests the entire `/Users/.../author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/` folder. This folder doesn't belong to a single persona — it spans CV docs, teaching records, vetting certificates, Zotero library, political memberships. The persona model forces an arbitrary assignment.
3. **Adding a ResearchGate source** that needs to attach to the same `cianfhoghlaim` identity as GitHub/LinkedIn, not to a fictional `aleyum` or `carlcashman`.

The persona model was right for v1 (three independent portfolios), but it conflates *who owns the data* with *what kind of data it is*. The replacement is a **Stream** model:

- `id` (e.g. `music`, `teaching`, `cv`, `research`) — domain-driven, what kind of work
- `owner` (e.g. `aleyum`, `cianfhoghlaim`) — historical alias, who publishes it
- `owner_display_name` — canonical human-readable name (e.g. "Cian Mac an Déisigh Uí Liatháin")

This is a **hybrid** model: domain ids drive the data architecture; owner aliases survive for UI/branding continuity.

Out of scope (intentionally dropped): any Kneecap lyrics pipeline. The `leabharlann/README.md` "Moral Usage Licensing" explicitly forbids use of the croilar monorepo for Kneecap-related work; the user has agreed to drop the kneecap scope rather than override the policy. If a kneecap pipeline is ever needed, it goes in a separate repo outside `leabharlann` policy scope.

## What Changes

### Capabilities

- **REMOVE** `croilar-persona-registry` (the old persona Zod-validated registry; replaced by Stream registry)
- **ADD** `croilar-stream-registry` (new capability: `Stream`, `StreamSource`, `StreamSourceType` model + per-stream source list)
- **MODIFY** `croilar-data-engineering` (DLT assets factory becomes stream-driven; new sources: `researchgate`, `fs_author`)
- **MODIFY** `croilar-portfolio` (notebook + analytics routes re-keyed by stream id; auth orgs preserved as tenant aliases)

### Code

#### `sruth/croilar/_shared/streams.py` (NEW)
- `StreamSourceType` enum: `GITHUB | LINKEDIN | RESEARCHGATE | SPOTIFY | SOUNDCLOUD | LABELS | CV | ARTWORK | FILESYSTEM | ZOTERO_SQL`
- `StreamSource` frozen dataclass: `(type, config, local_only=False)`
- `Stream` frozen dataclass: `(id, owner, owner_display_name, r2_prefix, duckdb_dataset, sources)`
- `load_streams_from_yaml(path) -> list[Stream]` factory
- `get_stream(stream_id) -> Stream` lookup (cached)
- `list_streams() -> list[Stream]`

#### `sruth/croilar/_shared/config/settings.py` (MODIFIED)
- Rename `AleyumSettings` → `StreamSettings`
- Env prefix `ALEYUM_` → `STREAMS_`
- `streams: dict[str, Stream]` field loaded from `sruth/croilar/config/sources.yaml` (new format)

#### `sruth/croilar/config/sources.yaml` (REPLACED)
- Old top-level keys (`spotify`, `soundcloud`, `github`, …) replaced with a `streams:` map
- See `specs/croilar-data-engineering/spec.md` for the new shape

#### `sruth/croilar/pipelines/linkedin/source.py` (MODIFIED)
- `flow_id` parameter → `stream_id`
- Drop `carlcashman` default
- Default `profile_url` = the Cian Mac an Déisigh Uí Liatháin LinkedIn URL (provided in task #5)

#### `sruth/croilar/pipelines/github/source.py` (MODIFIED)
- Default `username="cianfhoghlaim"`

#### `sruth/croilar/pipelines/researchgate/` (NEW)
- DLT REST source for ResearchGate profile + publications
- Mirrors the LinkedIn source structure: `sruth-browser` for scraping, BAML `researchgate_extraction.baml` schema for structured extraction
- New `StreamSourceType.RESEARCHGATE`

#### `sruth/croilar/pipelines/fs_author/` (NEW)
- DLT **filesystem** source
- One resource per subdirectory: `achievement`, `catharnacht`, `deacy`, `disability`, `gemini_deep_research`, `identity`, `politics`, `teaching`, `university_of_galway`, `vetting`
- **Excludes** `zotero/` (deferred to a future change; Zotero SQLite needs a separate `zotero_sql` source)
- `local_only=True` → no R2 calls, no audio cache, no artwork cache
- Writes only to `./data/local/fs_author.duckdb`
- Records: `{path, subdir, filename, ext, mtime, sha256, size, ingested_at}`

#### `sruth/croilar/baml/linkedin_profile_extraction.baml` (MODIFIED)
- `flowId` field renamed to `streamId`
- Allowed values: `music | teaching | cv | research` (no more `carlcashman`)
- New `ownerDisplayName: string` field

#### `sruth/croilar/baml/researchgate_extraction.baml` (NEW)
- Mirrors the LinkedIn schema with `streamId`, `ownerDisplayName`, and ResearchGate-specific fields (publications, citations, h-index, co-authors)

#### `sruth/croilar/dagster_assets/dlt_assets.py` (REPLACED)
- Hard-coded `aleyummusic` / `aleyum` assets removed
- New generic asset factory `make_dlt_asset(stream, source) -> AssetsDefinition`
- One `AssetKey` per `(stream.id, source.type)` pair, e.g. `("music", "spotify")`, `("teaching", "linkedin")`, `("cv", "filesystem")`
- Sync script enumerates the registry and emits a flat asset list

#### `sruth/croilar/agent_os/main.py` (MODIFIED)
- `init_config(service_name="aleyum", service_port=7774)` → `init_config(service_name=stream.id, service_port=stream.agent_port)`
- The agent OS file becomes a generic template instantiated per stream
- Per-stream ports: music=7774, teaching=7775, cv=7776, research=7777

#### `sruth/croilar/pipelines/shared/destinations.py`, `r2_client.py`, `ducklake.py` (MODIFIED)
- Generic R2 bucket `cianfhoghlaim-public` (already declared in `sruth/croilar/wrangler.toml`)
- Per-stream R2 prefix
- **Local-only streams never call `r2.upload_*`** (gated by `StreamSource.local_only`)

#### `sruth/croilar/packages/i18n/src/index.ts` (MODIFIED)
- `aleyum` / `cianfhoghlaim` persona JSON imports replaced by `streams` keyed by `id`
- Migration: `resources/aleyum/{en,ga}/persona.json` → `resources/streams/music/{en,ga}/persona.json`
- Migration: `resources/cianfhoghlaim/{en,ga}/persona.json` → `resources/streams/teaching/{en,ga}/persona.json`

#### `sruth/croilar/notebooks/aleyum/music_analytics.py` → `sruth/croilar/notebooks/streams/music/music_analytics.py` (MOVED)
#### `sruth/croilar/notebooks/cianfhoghlaim/teaching_analytics.py` → `sruth/croilar/notebooks/streams/teaching/teaching_analytics.py` (MOVED)

#### `sruth/croilar/apps/web/package.json` (MODIFIED)
- `notebook:wasm:aleyum` → `notebook:wasm:music`
- `notebook:wasm:cianfhoghlaim` → `notebook:wasm:teaching`

#### `sruth/croilar/apps/portal/src/routes/_layout/analytics/index.tsx` (MODIFIED)
- `aleyum` / `cianfhoghlaim` MotherDuck dive URLs rekeyed to `music` / `teaching`

#### `sruth/croilar/apps/portal/src/lib/tenant/tenant-context.tsx` (MODIFIED)
- Body class `tenant-aleyum` / `tenant-cianfhoghlaim` replaced with `tenant-<owner>` for the OG-image only (UI tenant aliases preserved)

#### `sruth/croilar/tests/test_database.py`, `test_smoke.py` (MODIFIED)
- `aleyum` / `cianfhoghlaim` test cases updated to use stream ids
- `test_aleyum_settings_default_loads` → `test_stream_settings_default_loads`
- New tests: `test_fs_author_local_only`, `test_researchgate_source_exports`, `test_stream_registry_resolves_all_streams`

#### `sruth/croilar/scripts/migrate-personas-to-streams.ts` (NEW)
- One-shot migration: renames dirs, rewrites TS/Python imports, emits CSV diff
- `bun run migrate:personas-to-streams`

### BetterAuth orgs (PRESERVED, not modified)
- `aleyum` / `cianfhoghlaim` orgs stay as tenant aliases (UI/branding)
- `croilar-admin` / `croilar-collab` stay as platform orgs
- They no longer drive the data layer — they are a UI concern only

### NOT changed
- `sruth/croilar/compose.yaml` and `compose.dev.yaml` service names (Docker stack named `aleyum` stays; this is the container runtime, not the data model)
- `sruth/croilar/dagster.yaml` `aleyum-postgres` (same reason)
- The kneecap-related files in `leabharlann/` and `author_.../zotero/` (out of scope)

## Impact

- **Code** — ~25 files modified, ~4 new files
- **Config** — `sruth/croilar/config/sources.yaml` rewritten
- **Data** — no data loss; new filesystem ingest is additive; existing music/teaching data flows continue unchanged
- **Tests** — `sruth/croilar/tests/test_database.py`, `test_smoke.py` updated; new tests added
- **CI** — `bun run turbo typecheck lint test` must pass; `openspec validate --strict` must pass
- **Auth** — BetterAuth orgs preserved; only the data layer is rekeyed
- **Out-of-scope, deferred to follow-up issues:**
  - Zotero SQLite ingest (`pipelines/zotero_sql/`)
  - The dropped kneecap pipeline
  - Renaming the Docker stack from `aleyum` to `croilar` (purely cosmetic; not worth the migration risk)
