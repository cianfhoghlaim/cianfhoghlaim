# Infrastructure Stacks — Code-side Env Defaults Delta

> This file is the change-side delta for
> `2026-07-02-align-cianfhoghlaim-env-with-stacks`. It applies on top
> of the canonical `infrastructure-stacks` spec at
> `../../../../specs/infrastructure-stacks/spec.md` and on top of the
> prior `2026-07-02-replace-private-images-and-bring-wave2` delta
(which aligned the **docker-stack** side).

## ADDED Requirements

### Requirement: Code-side env defaults match deployed stack contracts

The system SHALL update the cianfhoghlaim Python code so its env-var
defaults match the actual host ports + docker DNS names of the
deployed stacks (per the lakehouse-lancedb-viewer port remap, the
langfuse port remap, etc.). Specifically:

- `dagster/resources.py::LiteLLMResource.base_url` default
  `LITELLM_BASE_URL` env var (default
  `http://litellm:4000/v1` in-docker or
  `http://127.0.0.1:4000/v1` on-host)
- `dagster/resources.py::FalkorDBResource.host` and `.port` default
  `FALKORDB_HOST` (default `falkordb`) + `FALKORDB_PORT` (default
  `6379` in-docker or `6380` on-host)
- `dagster/resources.py::CogneeMemoryResource.graph_url` replaced
  with `postgres_url` default (since cognee now uses
  `USE_UNIFIED_PROVIDER=pghybrid` per the cognee compose; the old
  Memgraph `bolt://...` default is incorrect)
- `dagster/resources.py::ProgressTrackerResource.redis_url` default
  `REDIS_URL` env var (default
  `redis://lakehouse-redis:6379` in-docker or
  `redis://localhost:6390` on-host)
- `dagster/resources.py` — `MemgraphResource`, `Neo4jResource`,
  `TemporalGraphResource` get deprecation comments (no stack in
  the Wave 1+2 lineup; the `agent-observability` spec removed
  Memgraph in favour of FalkorDB + lakehouse-postgres)
- `observability/langfuse_config.py::LANGFUSE_HOST` default changed
  from `http://localhost:3000` to `http://localhost:3001` (the
  langfuse stack's host port is `:3001`, not `:3000`)
- `observability/logfire_config.py` —
  `logfire_instrument_local_otlp_only()` helper added for dev
  mode (bypasses SaaS and routes to the local OTel collector
  when `LOGFIRE_TOKEN` is empty)
- `cocoindex/_lifespan.py::LANCEDB_URI` default changed from
  `rest://lance-api.cianfhoghlaim.ie` (prod) to
  `rest://lakehouse-lance-namespace:8182` (dev — the
  lakehouse-lance-namespace service is the canonical vector store)
- `baml/clients.baml` — 3 LocalVision* client `base_url` lines
  changed from `"http://localhost:4000/v1"` to
  `env.LITELLM_BASE_URL` (BAML env var substitution; the value
  comes from the runtime env)
- `baml/clients_llama_swap.baml` — 4 LlamaSwap* client `base_url`
  lines changed from `"http://llama-swap:8080/v1"` to
  `env.LLAMASWAP_BASE_URL`
- `dlt/common/destinations_oideachais.py` —
  `_resolve_aws_credentials()` helper added that maps
  `GARAGE_ACCESS_KEY_ID` → `AWS_ACCESS_KEY_ID` (and SECRET
  analog) so DLT destinations work with the lakehouse's GARAGE
  env-var naming without code changes
- `cianfhoghlaim/.env.dev.local` NEW — canonical local env file
  documenting all dev endpoints (LITELLM_BASE_URL,
  LANGFUSE_HOST, MLFLOW_TRACKING_URI, COGNEE_BASE, lakehouse
  DuckLake + Garage + Redis + LanceDB endpoints, etc.)

#### Scenario: Dagster dev boots cleanly
- **WHEN** `cd cianfhoghlaim && DAGSTER_HOME=. uv run dagster dev
  -m cianfhoghlaim.dagster.definitions` is invoked
- **THEN** the 5 KCG Components load with the correct env-var
  defaults (lancedb connects to `rest://lakehouse-lance-namespace:8182`,
  falkordb connects to `falkordb:6379`, litellm connects to
  `http://litellm:4000/v1`, cognee connects to `cognee-postgres:5432/cognee_oideachais`,
  progress tracker connects to `redis://lakehouse-redis:6379`)

#### Scenario: BAML generation succeeds
- **WHEN** `cd cianfhoghlaim && uv run baml-cli generate` is invoked
  after the env var substitution in `clients.baml` and
  `clients_llama_swap.baml`
- **THEN** the regenerated `baml_client/` Python module references
  the new `LITELLM_BASE_URL` and `LLAMASWAP_BASE_URL` env vars
  (no hardcoded localhost:4000)
- **AND** the BAML compiler accepts the substitution (no syntax
  errors)

#### Scenario: DLT DuckLake destination uses lakehouse creds
- **WHEN** a DLT pipeline materialises to the local DuckLake
  destination
- **THEN** `_resolve_aws_credentials()` sets `AWS_ACCESS_KEY_ID` from
  `GARAGE_ACCESS_KEY_ID` (or preserves the existing AWS_* if set)
- **AND** `AWS_SECRET_ACCESS_KEY` is set from
  `GARAGE_SECRET_ACCESS_KEY`
- **AND** the destination writes to the lakehouse Garage S3 bucket
  `s3://ducklake/{namespace}/`

#### Scenario: 8 marimo notebooks query live lakehouse data
- **WHEN** the user opens any of the 8 stage/cross-domain notebooks
  (`aistear`, `primary`, `junior_cycle`, `senior_cycle`, `tertiary`,
  `cross_domain`, `leabharlann_full_stack_demo`, `email_inbox_triage`)
- **THEN** the notebook queries the corresponding lakehouse data
  source (Cognee dataset, lakehouse-postgres table, or local DuckDB)
- **AND** the marimo container can reach the lakehouse services via
  the `cianfhoghlaim` docker network

## MODIFIED Requirements

### Requirement: Langfuse /api/public/health endpoint returns valid response

The system SHALL fix the existing bug where `GET /api/public/health`
on the langfuse stack returns an empty response (status 0, no
headers). The fix is in the langfuse Next.js configuration, not in
the cianfhoghlaim code — this is a separate ops change tracked
under `2026-07-XX-fix-langfuse-health`.

(Logged as a known issue, NOT fixed in this change.)

#### Scenario: Langfuse health endpoint returns 200
- **WHEN** an operator runs `curl -fsS http://localhost:3002/api/public/health`
  after the next langfuse release is deployed
- **THEN** the response SHALL be HTTP 200 with a valid JSON body
  (e.g. `{"status":"ok","version":"3.x.x"}`)
- **AND** the langfuse-web container SHALL report `healthy` in
  `docker ps` (not `unhealthy`)

## Cross-references

- [`agent-observability`](../agent-observability/spec.md) —
  LANGFUSE_HOST default + logfire self-host mode
- [`agent-memory-systems`](../agent-memory-systems/spec.md) —
  CogneeMemoryResource postgres_url default
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  BAML env var substitution + DLT GARAGE→AWS helper
- [`dagster-5-layer-component-architecture`](../dagster-5-layer-component-architecture/spec.md) —
  5 KCG Components resource defaults
- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  cross-reference to the docker-stack side of the alignment
