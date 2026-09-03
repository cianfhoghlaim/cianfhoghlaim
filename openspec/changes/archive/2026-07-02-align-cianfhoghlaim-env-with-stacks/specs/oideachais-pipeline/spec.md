# Oideachais Pipeline — BAML Env Vars + DLT Credentials + Marimo Wiring Delta

> This file is the change-side delta for
> `2026-07-02-align-cianfhoghlaim-env-with-stacks`. It applies on
> top of the canonical `oideachais-pipeline` spec at
> `../../../../specs/oideachais-pipeline/spec.md` and on top of the
> prior `2026-07-02-replace-private-images-and-bring-wave2` delta.

## ADDED Requirements

### Requirement: BAML clients MUST use litellm + llama-swap env vars

The system MUST use BAML env var substitution for the 7 BAML
clients in `baml/clients.baml` (LocalVisionQwen, LocalVisionGLM,
LocalVisionMoondream, OideachaisDefault, MeaisinfhoghlaimDefault,
TuathaDefault, CroilarDefault, ReasoningStrong) and the 4 clients
in `baml/clients_llama_swap.baml` (LlamaSwapClient,
LlamaSwapOCRClient, LlamaSwapExtractionClient,
LlamaSwapReasoningClient) for their `base_url` lines:

- All litellm-routed clients: `base_url env.LITELLM_BASE_URL`
  (replaces the previous hardcoded `"http://localhost:4000/v1"`)
- All llama-swap-routed clients: `base_url env.LLAMASWAP_BASE_URL`
  (replaces the previous hardcoded `"http://llama-swap:8080/v1"`)

The BAML client is regenerated via
`cd cianfhoghlaim && uv run baml-cli generate` after the
substitution; the regenerated Python module references the env
var names at runtime (no hardcoded URLs in the compiled client).

#### Scenario: BAML env var substitution
- **WHEN** `cd cianfhoghlaim && uv run baml-cli generate` runs
  against the updated `clients.baml` + `clients_llama_swap.baml`
- **THEN** the generated `baml_client/` Python module contains
  references to `os.environ["LITELLM_BASE_URL"]` and
  `os.environ["LLAMASWAP_BASE_URL"]` (no `http://localhost:4000` or
  `http://llama-swap:8080` literals)
- **AND** the BAML compiler exits 0 (no syntax errors)

#### Scenario: BAML call routes through litellm
- **WHEN** a BAML function (e.g. `ExtractMarkingScheme`) is
  invoked at runtime
- **THEN** the BAML client POSTs to
  `${LITELLM_BASE_URL}/v1/chat/completions` (e.g.
  `http://litellm:4000/v1` in-docker or `http://127.0.0.1:4000`
  on-host)
- **AND** the litellm gateway routes the call to the appropriate
  model (extracted from the client config)

### Requirement: DLT DuckLake destination uses GARAGE→AWS credential mapping

The system MUST use the `_resolve_aws_credentials()` helper in
`dlt/common/destinations_oideachais.py::_build_local_destination`
to map the lakehouse's `GARAGE_*` env vars (from
`bonneagar/stacks/lakehouse/.env.dev`) to the `AWS_*` naming
convention that `boto3` and the DuckDB S3 extension expect.

The mapping is:
- `GARAGE_ACCESS_KEY_ID` → `AWS_ACCESS_KEY_ID`
  (if `AWS_ACCESS_KEY_ID` is not already set)
- `GARAGE_SECRET_ACCESS_KEY` → `AWS_SECRET_ACCESS_KEY`
  (if `AWS_SECRET_ACCESS_KEY` is not already set)
- `AWS_REGION` (default `garage`) is used directly (no
  `GARAGE_REGION` mapping needed)

#### Scenario: DLT pipeline materialises to lakehouse
- **WHEN** a DLT pipeline (e.g. `create_pipeline('ncca_aistear',
  'aistear')`) materialises
- **THEN** `_resolve_aws_credentials()` sets
  `AWS_ACCESS_KEY_ID` from `GARAGE_ACCESS_KEY_ID` (or preserves
  the existing AWS_* if set)
- **AND** the destination writes to the lakehouse Garage S3
  bucket `s3://ducklake/oideachais/`
- **AND** the catalog metadata lands in lakehouse-postgres
  `ducklake_oideachais` database

### Requirement: 8 marimo notebooks MUST query live lakehouse data

The system MUST wire the 8 stage/cross-domain marimo notebooks
in `cianfhoghlaim/notebooks/dashboards/` to query the corresponding
lakehouse data sources (not hardcoded dataframes). The 4
lakehouse-relevant notebooks in `notebooks/dashboards/duckdb/`
already query the lakehouse (no change).

The 8 notebooks + their data sources:

| Notebook | Lakehouse data source |
|:--|:--|
| `aistear.py` | Cognee `oideachais.aistear` dataset |
| `primary.py` | Cognee `oideachais.primary` dataset |
| `junior_cycle.py` | Cognee `oideachais.junior_cycle` dataset |
| `senior_cycle.py` | Cognee `oideachais.senior_cycle` dataset |
| `tertiary.py` | Cognee `oideachais.tertiary` dataset |
| `cross_domain.py` | Cognee `oideachais.cross_stage` dataset |
| `leabharlann_full_stack_demo.py` | Local DuckDB at `/tmp/leabharlann_demo.duckdb` (existing default) |
| `email_inbox_triage.py` | lakehouse-postgres `oideachais_inbox_messages` table |

The marimo stack (in `bonneagar/stacks/marimo/`) needs to have the
`LANCEDB_URI` + `DUCKLAKE_POSTGRES_HOST` + `AWS_*` env vars set
(per `marimo/.env.dev` from Change 7) so the notebooks can reach
the lakehouse services via the `cianfhoghlaim` docker network.

#### Scenario: marimo notebook loads with live data
- **WHEN** the user opens any of the 8 stage/cross-domain notebooks
  via `http://localhost:2718/notebooks/dashboards/<name>.py`
- **THEN** the notebook runs a Cognee / DuckDB / LanceDB query
  against the corresponding lakehouse data source
- **AND** the response contains real data (not the hardcoded
  dataframe defaults)
- **AND** the marimo container can reach the lakehouse services
  via the `cianfhoghlaim` docker network (or `localhost` on host)

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  cross-reference to the docker-stack side of the alignment
- [`agent-observability`](../agent-observability/spec.md) —
  Langfuse port + Logfire self-host mode
- [`agent-memory-systems`](../agent-memory-systems/spec.md) —
  Cognee postgres+pgvector default
- [`dagster-5-layer-component-architecture`](../dagster-5-layer-component-architecture/spec.md) —
  5 KCG Components resource defaults
