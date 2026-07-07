# Tasks

## Phase 1 — File authoring (15 min)

- [ ] 1.1 Edit `cianfhoghlaim/dagster/resources.py`:
  - `FalkorDBResource.host=""` + `port=0` (env-driven)
  - `CogneeMemoryResource`: replace `graph_url` with `postgres_url`
  - Deprecation comments on `MemgraphResource`, `Neo4jResource`,
    `TemporalGraphResource`
  - `ProgressTrackerResource.redis_url` env-driven
- [ ] 1.2 Edit `cianfhoghlaim/observability/langfuse_config.py`:
  - `LANGFUSE_HOST` default: `:3000` → `:3001`
- [ ] 1.3 Edit `cianfhoghlaim/observability/logfire_config.py`:
  - Add `logfire_instrument_local_otlp_only()` helper for dev mode
  - When `LOGFIRE_TOKEN` is empty, send to OTel collector
- [ ] 1.4 Edit `cianfhoghlaim/cocoindex/_lifespan.py`:
  - `LANCEDB_URI` default: `rest://lance-api.cianfhoghlaim.ie`
    → `rest://lakehouse-lance-namespace:8182`
- [ ] 1.5 Edit `cianfhoghlaim/baml/clients.baml`:
  - Replace 7 hardcoded `http://localhost:4000/v1` with `env.LITELLM_BASE_URL`
- [ ] 1.6 Edit `cianfhoghlaim/baml/clients_llama_swap.baml`:
  - Replace 4 hardcoded `http://llama-swap:8080/v1` with
    `env.LLAMASWAP_BASE_URL`
- [ ] 1.7 Edit `cianfhoghlaim/dlt/common/destinations_oideachais.py`:
  - Add `_resolve_aws_credentials()` helper
  - Map `GARAGE_ACCESS_KEY_ID` → `AWS_ACCESS_KEY_ID` (and SECRET analog)
- [ ] 1.8 Write `cianfhoghlaim/.env.dev.local` (canonical local env file)
- [ ] 1.9 Wire 8 marimo notebooks (aistear/primary/junior_cycle/senior_cycle/
      tertiary/cross_domain/leabharlann_full_stack_demo/email_inbox_triage)
      to live lakehouse data
- [ ] 1.10 Write the 5 openspec spec deltas (infrastructure-stacks,
      agent-observability, agent-memory-systems, oideachais-pipeline,
      dagster-5-layer-component-architecture)
- [ ] 1.11 Write `proposal.md` (this change's proposal)
- [ ] 1.12 Write `tasks.md` (this file)

## Phase 2 — Regenerate BAML client (2 min)

- [ ] 2.1 `cd cianfhoghlaim && uv run baml-cli generate` — generates
      new Python client module from the updated BAML files
- [ ] 2.2 Verify no errors in BAML generation output
- [ ] 2.3 Spot-check the generated `baml_client/` for the new env var
      references (e.g., `from cianfhoghlaim.baml_client.baml_client.types import
      LlmHttpClientConfig` shows `LITELLM_BASE_URL`)

## Phase 3 — Validate openspec change (1 min)

- [ ] 3.1 `cd cianfhoghlaim && openspec validate
      2026-07-02-align-cianfhoghlaim-env-with-stacks --strict` —
      must say "is valid"

## Phase 4 — Run smoke tests (3 min)

- [ ] 4.1 Re-run the 12 lakehouse integration smoke tests from
      Change 7 (should all still pass; no regression)
- [ ] 4.2 Test the BAML Python client:
      `cd cianfhoghlaim && uv run python -c "from cianfhoghlaim.baml_client.baml_client import b; print(b)"` — imports clean
- [ ] 4.3 Test the DLT destination factory with the GARAGE→AWS helper:
      `uv run python -c "from dlt.common.destinations_oideachais import get_dlt_destination; print(get_dlt_destination())"` — prints a DuckLake object
- [ ] 4.4 Test the dagster resources load with env vars:
      `DAGSTER_HOME=. uv run python -c "from cianfhoghlaim.dagster.resources import falkordb_resource, cognee_memory_resource; print(falkordb_resource); print(cognee_memory_resource)"` — no exceptions
- [ ] 4.5 Test langfuse env var: `LANGFUSE_HOST=http://localhost:3001
      uv run python -c "from cianfhoghlaim.observability.langfuse_config import LANGFUSE_HOST; print(LANGFUSE_HOST)"` — prints `http://localhost:3001`
- [ ] 4.6 Test logfire dev path: `LOGFIRE_TOKEN='' uv run python -c
      "from cianfhoghlaim.observability.logfire_config import logfire_instrument_local_otlp_only; logfire_instrument_local_otlp_only()"` — no exceptions
- [ ] 4.7 Test cocoindex LANCEDB_URI: `uv run python -c "from
      cianfhoghlaim.cocoindex._lifespan import LANCEDB_URI; print(LANCEDB_URI)"` — prints `rest://lakehouse-lance-namespace:8182`

## Phase 5 — Wire 8 marimo notebooks (30 min)

- [ ] 5.1 aistear.py — query Cognee `oideachais.aistear` dataset
- [ ] 5.2 primary.py — query Cognee `oideachais.primary` dataset
- [ ] 5.3 junior_cycle.py — query Cognee `oideachais.junior_cycle` dataset
- [ ] 5.4 senior_cycle.py — query Cognee `oideachais.senior_cycle` dataset
- [ ] 5.5 tertiary.py — query Cognee `oideachais.tertiary` dataset
- [ ] 5.6 cross_domain.py — query Cognee `oideachais.cross_stage` dataset
- [ ] 5.7 leabharlann_full_stack_demo.py — keep existing local DuckDB read
- [ ] 5.8 email_inbox_triage.py — query lakehouse-postgres
      `oideachais_inbox_messages` table
- [ ] 5.9 Restart marimo stack and verify all 11 marimo notebooks
      load without error: `cd bonneagar && ./scripts/stack.sh marimo up -d`

## Phase 6 — Refresh HEALTH_REPORT + commit (10 min)

- [ ] 6.1 Update `HEALTH_REPORT.md` Session 7 entry with:
  - The code defaults + env-var alignment
  - 8 marimo notebooks now live-data-wired
  - BAML client regenerated
  - 12/12 smoke tests passing
- [ ] 6.2 Commit on cianfhoghlaim main repo:
  `git add -A && git commit -m "feat(cianfhoghlaim): Change 8 — align code env defaults with deployed stacks"`
- [ ] 6.3 Commit on bonneagar worktree (if any file changes):
  `git add -A && git commit -m "feat(bonneagar): HEALTH_REPORT Session 7 — code-side alignment"`

## Phase 7 — STOP + hand off to Wave 3

- [ ] 7.1 Report status to user (smoke test results, any deviations)
- [ ] 7.2 **STOP** before starting Wave 3 (invokeai + convex + risingwave
      + marimo) — the user must explicitly say "proceed"
