# Change: 2026-07-02-replace-private-images-and-bring-wave2

## Why

The 4 openspec changes shipped on 2026-07-02 (bunchloch-stack-bootstrap,
add-lancedb-and-logfire-stacks, add-marimo-stack, add-agent-surface-stacks)
brought 24 of 25 target stacks to "deployable" but **Wave 1 only** —
dragonfly + lancedb + falkordb + lakehouse (10 services).

To bring up Wave 2 (litellm + mlflow + cognee + langfuse + graphiti
+ dagster + unstract + logfire + 4 OCR) we have 2 hard blockers:

1. **3 private image references** that fail `docker compose pull`:
   - `ghcr.io/cianfhoghlaim/mlflow:v2.19.0` (401 on GHCR; no public alt
     with that exact tag, but `ghcr.io/mlflow/mlflow:v2.22.4` is
     publicly available — used by our existing `Dockerfile.mlflow` base)
   - `ghcr.io/cianfhoghlaim/dagster:latest` (401 on GHCR; no public
     webserver image exists at all — verified 404 on Docker Hub,
     401/403 on `ghcr.io/dagster` even with auth header)
   - `ghcr.io/nousresearch/hermes-agent:0.17.0` (401 on GHCR; public
     alternative is `nousresearch/hermes-agent:v2026.7.1` on
     Docker Hub — verified 200)

2. **No Dagster Dockerfile** in the codebase. The custom
   `ghcr.io/cianfhoghlaim/dagster:latest` referenced by the compose
   has no source Dockerfile in the stack dir. We need to build the
   Dagster image locally from a new `Dockerfile.dagster` modeled on
   `dagster-io/dagster/examples/deploy_docker`, with the cianfhoghlaim-
   specific Python deps (dagster-dlt, dagster-duckdb, dagster-postgres,
   baml, cocoindex, lancedb, duckdb, pyarrow, psycopg2-binary, boto3).

Per the user's directive: "we shouldnt be using our own ghcr for any
we should be using the typical public images" — and to enable Wave 2
deploys on bunchloch (dev mode, no Locket/Infisical).

## What changes

This omnibus bundles 3 classes of changes:

### 1 — Image replacements (5 files)

| File | Old | New |
|:--|:--|:--|
| `mlflow/compose.yaml` | `ghcr.io/cianfhoghlaim/mlflow:v2.19.0` | `ghcr.io/mlflow/mlflow:v2.22.4` |
| `mlflow/Dockerfile.mlflow` | `FROM ghcr.io/mlflow/mlflow:v2.19.0` | `FROM ghcr.io/mlflow/mlflow:v2.22.4` |
| `dagster/compose.yaml` (2x) | `ghcr.io/cianfhoghlaim/dagster:latest` | `dagster-local:latest` |
| `hermes/compose.yaml` | `ghcr.io/nousresearch/hermes-agent:0.17.0` | `nousresearch/hermes-agent:v2026.7.1` |

### 2 — Dagster Dockerfile + 6 dev-overlay files (7 files)

- New `dagster/Dockerfile.dagster` (modeled on
  `dagster-io/dagster/examples/deploy_docker`)
- New `dagster/.env.dev` + `dagster/compose.dev.yaml`
- New `mlflow/.env.dev` + `mlflow/compose.dev.yaml`
- New `cognee/.env.dev` + `cognee/compose.dev.yaml`
- New `langfuse/.env.dev` + `langfuse/compose.dev.yaml`
- New `marimo/.env.dev` + `marimo/compose.dev.yaml`
  (so the marimo container can connect to `lakehouse-postgres` for
  the ducklake_explorer notebook)

### 3 — Openspec change files (6 files)

- `proposal.md` (this file)
- `tasks.md`
- `specs/infrastructure-stacks/spec.md` (4 ADDED Requirements:
  public image policy, dagster local build, mlflow public pin,
  hermes/openclaw/openchamber hygiene)
- `specs/agent-observability/spec.md` (Langfuse port + Logfire
  OTel-collector-only path)
- `specs/oideachais-pipeline/spec.md` (CocoIndex Lakehouse
  LANCEDB_URI + DLT DuckLake GARAGE→AWS mapping + smoke-test
  procedure for the full pipeline)

Plus `HEALTH_REPORT.md` Session 6 entry.

### 4 — Wave 2 deploys (bundled)

After the image + Dockerfile + dev-overlay changes land, Wave 2 is
deployed in 3 sub-waves:

- **Wave 2a** (3 stacks, 5 containers): litellm + mlflow + cognee
- **Wave 2b** (4 stacks, 8 containers): langfuse+4 backing + graphiti
  + dagster + unstract
- **Wave 2c** (5 stacks, 5 containers): logfire + 4 OCR (dots-ocr
  broken — accepted per deferred-change convention)

Total Wave 2: 12 stacks, 18 containers, 23 containers running on
bunchloch after Change 7.

### 5 — 15 lakehouse integration smoke tests (after deploy)

Verifies CocoIndex + DLT + Dagster + BAML + Marimo are all wired
to lakehouse destinations end-to-end.

## Impact

- **Affected specs:** `infrastructure-stacks`, `agent-observability`,
  `oideachais-pipeline` (3 spec deltas)
- **Affected code:** 5 image edits + 1 Dockerfile.mlflow edit +
  1 new Dockerfile.dagster + 6 new .env.dev + 5 new
  compose.dev.yaml + 1 new HEALTH_REPORT entry
- **Affected hosts:** `bunchloch` only
- **Risk:** medium — building the dagster image is a 5-min build
  that may need a C compiler + 2GB of pip cache. If the build fails,
  the omnibus scope reduces to just the image replacements (12 of
  18 Wave 2 containers) and dagster is deferred to a follow-up
- **Audit gates:** `bun run validate-stacks` + `mise run lint:skills`
  + `openspec validate --strict` + 15 smoke tests

## Non-goals

- **Not bringing up Wave 3 (invokeai + convex + risingwave) or
  Wave 4 (hermes full + openclaw + openchamber).** openchamber is
  explicitly deferred to a separate change (its upstream image is
  private on BOTH Docker Hub and GHCR with no public alternative
  found). Wave 3 + the openclaw/hermes halves of Wave 4 are deferred
  to follow-up sessions.
- **Not modifying cianfhoghlaim code** (the env default fixes, BAML
  env var substitution, marimo notebook wiring). That's Change 8
  (alignment). This omnibus only handles the docker-stack side.
- **Not running the 15 lakehouse smoke tests in Change 8** — those
  tests verify BOTH the stack side (Change 7 deliverable) AND the
  app code side (Change 8 deliverable). Running them after Change
  7 is informative (catches stack-side issues early); running them
  after Change 8 is the final sign-off.

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Bring openchamber stack to spec (compose + Dockerfile + GHCR auth) | `2026-07-XX-bring-openchamber-stack-to-spec` |
| Align cianfhoghlaim env defaults + BAML env vars + marimo wiring | `2026-07-02-align-cianfhoghlaim-env-with-stacks` (this session's Change 8) |
| Wave 3 deploy (invokeai + convex + risingwave) | `2026-07-03-wave-3-ui-streams-deploy` |
| Wave 4 deploy (hermes + openclaw) | `2026-07-03-wave-4-agent-deploy` |
| dots-ocr (broken registry path) | `2026-07-XX-bring-dots-ocr-up-to-spec` |
| browser (missing 5/6 GOLD_STANDARD files) | `2026-07-XX-bring-browser-stack-to-gold-standard` |
| Full SHA256 digest pinning (renovate cycle) | `2026-07-XX-stack-doctor-image-digest-pinning` |
| Migrate lakehouse to cax41-hetzner (per convergence spec) | `2026-07-XX-migrate-lakehouse-to-hetzner` |
| Register stacks in Komodo after v5-drift lands | `2026-07-XX-komodo-register-bunchloch-stacks` |
