# Dagster 5-Layer Component Architecture — Resource Defaults Delta

> This file is the change-side delta for
> `2026-07-02-align-cianfhoghlaim-env-with-stacks`. It applies on
> top of the canonical `dagster-5-layer-component-architecture` spec
> at `../../../../specs/dagster-5-layer-component-architecture/spec.md`.

## ADDED Requirements

### Requirement: 5 KCG Components resource defaults MUST align with deployed stack

The system MUST align 5 KCG Components resource defaults with
deployed stack contracts. The 5 KCG Components
(CelticIngestionComponent, CelticMaterialsComponent,
CelticModelLifecycleComponent, CelticAssetGenerationComponent,
CelticAgentOpsComponent) loaded by `dagster/devs/defs/` MUST use
resource defaults that match the deployed stack contracts (per the
prior `2026-07-02-replace-private-images-and-bring-wave2` change):

- `LiteLLMResource` — `base_url` default via `LITELLM_BASE_URL` env
  var (in-docker `http://litellm:4000/v1`; on-host
  `http://127.0.0.1:4000/v1`); `master_key` via `LITELLM_MASTER_KEY`
  (default `sk-1234`)
- `FalkorDBResource` — `host` + `port` via `FALKORDB_HOST` +
  `FALKORDB_PORT` env vars (in-docker `falkordb:6379`; on-host
  `127.0.0.1:6380`)
- `CogneeMemoryResource` — `postgres_url` default via
  `COGNEE_PG_HOST` + `COGNEE_PG_PASSWORD` env vars (the deployed
  cognee stack uses `USE_UNIFIED_PROVIDER=pghybrid`)
- `LanceDBResource` — `LANCEDB_URI` env var (default
  `rest://lakehouse-lance-namespace:8182`)
- `ProgressTrackerResource` — `REDIS_URL` env var (default
  `redis://lakehouse-redis:6379`)

#### Scenario: 5 KCG Components load with correct env defaults
- **WHEN** `cd cianfhoghlaim && DAGSTER_HOME=. uv run dagster dev
  -m cianfhoghlaim.dagster.definitions` is invoked (with the
  canonical env vars set in `dagster/.env.dev`)
- **THEN** the 5 KCG Components load successfully with no
  connection errors to litellm, falkordb, cognee-postgres, lakehouse-
  lance-namespace, or lakehouse-redis
- **AND** the assets materialise data into the correct destinations
  (Lakekeeper, LanceDB, lakehouse-postgres, Garage)

#### Scenario: Dagster dev runs on host
- **WHEN** the same command runs on the host (no docker) with the
  `.env.dev.local` file sourced
- **THEN** the same code works (the env var defaults switch
  automatically from `falkordb` → `127.0.0.1` etc.)

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md)
- [`agent-observability`](../agent-observability/spec.md)
- [`agent-memory-systems`](../agent-memory-systems/spec.md)
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md)
