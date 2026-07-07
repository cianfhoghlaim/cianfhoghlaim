# Change: 2026-07-06-upgrade-4-stacks-with-infisical

## Why

After Change 1 (`2026-07-06-deploy-infisical-bunchloch-local`) brings up a local
Infisical vault, the 4 consumer stacks (lakehouse, litellm, mlflow, unstract)
need to be brought up + upgraded + re-pointed at the new vault. PaddleOCR is
deferred to a follow-up openspec change (`2026-07-XX-paddleocr-remediation`) —
Firecrawl research on 2026-07-06 confirmed the upstream `paddlecloud/paddleocr`
image is a Jupyter container on port 8888, not an OCR HTTP service.

Each stack's upgrade is grounded in Firecrawl-verified upstream research
(see tasks.md §0 for source URLs). No component upgrades are speculative —
every pin + breaking-change note is cited inline.

## What changes (per stack)

### lakehouse (data plane, 11 services)

- Lakekeeper `quay.io/lakekeeper/catalog:latest` → `v0.13.1`
- Garage `dxflrs/garage:v1.0.1` → `v2.3.0` (BREAKING config schema;
  rewrite `garage.toml` per v2 migration guide)
- ClickHouse `24.3` → `25.8.28.1-lts`
- Nimtable `nimtable/nimtable:latest` → `v0.1.0`
- Olake `ghcr.io/olake-io/olake:0.1.5` → `v0.8.0` (closes CVE-2026-33816 +
  Go CVEs GO-2026-5037/5039)
- `lance-sidecar/requirements.txt`: `pylance>=0.26.0` → `pylance>=8.0.0`;
  `lance-namespace-urllib3-client>=0.0.21` → `>=0.0.30`
- `lance-sidecar/main.py`: v0.9.0 changed context header prefix from
  `x-lance-ctx-*` → `header.<name>`; rename the sidecar's response
  header construction

### litellm (LLM gateway, 1 service)

- Image `ghcr.io/berriai/litellm:main-stable` →
  `ghcr.io/berriai/litellm-database:v1.91.0` (database variant bundles
  Prisma binaries — required for `lakehouse-postgres/litellm`)
- Memory limit `4G` → `16G` (per upstream `4Gi × num_workers` formula
  with 4 workers)
- New env: `LITELLM_MODE=PRODUCTION`, `USE_PRISMA_MIGRATE=True`,
  `MAX_REQUESTS_BEFORE_RESTART=10000`,
  `MAX_REQUESTS_BEFORE_RESTART_JITTER=1000`
- Healthcheck widened to include `/health/readiness`
- Add cosign image verification step to the deploy runbook (signatures
  introduced v1.90)
- Add post-`use_prisma_migrate` DB migration to first-boot — schema
  auto-creates but log a `[OK] prisma migrated` marker

### mlflow (ML + GenAI tracking, 1 service)

- Image `ghcr.io/mlflow/mlflow:v2.22.4` → `v3.12.0`
- Command args: add `--allowed-hosts="localhost,mlflow.cianfhoghlaim.ie"`
  + `--cors-allowed-origins="https://oideachais.cianfhoghlaim.ie"`
  (v3.5.0+ security middleware is mandatory for `0.0.0.0` binding)
- New env: `MLFLOW_S3_EXPECTED_BUCKET_OWNER=<garage-account-id>` (new
  v3 anti-bucket-takeover env var)
- Existing `psycopg2-binary + boto3` Dockerfile.mlflow bake remains correct

### unstract (15-service vendor)

- EXISTING `compose.yaml` (49 lines, 1 service + 1 pg) → ENTIRELY
  REPLACED with the upstream `docker-compose.yaml` from
  `Zipstack/unstract:v0.177.7` (released 06 Jul 2026, ~7 hours before
  this change was drafted). Pin all 8 images to `:v0.177.7`. Override
  upstream's `*-1` numeric container-name suffixes to the bare
  KCG pattern (`unstract-backend`, `unstract-celery-worker-general`,
  etc.) — per user decision 2026-07-06.
- DB image: `postgres:16` → `pgvector/pgvector:pg15`
- Drop `UNSTRACT_API_KEY` env (does not exist in OSS)
- Drop `HF_TOKEN` env (OSS does not auto-download HF models)
- Healthcheck port: 8002 → 8000 (real backend port per upstream docs)
- Rewrite `secrets.env` to canonical Locket form covering the full new
  URI surface: db, secret_key, celery_broker_url, rabbitmq_*,
  qdrant_*, minio_*, feature_flag
- Add new `pangolin.yaml` (stack only had `blueprint.yaml`)
- Add new `sidecar.yaml` with the canonical Locker sidecar
  (the upstream does not ship one)

## Impact

- **Affected specs:** `infrastructure-stacks` + `agent-observability`
  + `indexing-and-cognition` (the Lance-namespace 0.9 contract change)
- **Affected hosts:** `bunchloch` only
- **Risk:** medium-high (Garage v2 breaking config + full Unstract
  vendor; both have migration guides that MUST be followed exactly)
- **Disk:** ~5 GB pulled in fresh images + Lance-namespace Python wheel
  rebuild
- **RAM:** peak ~10 GB across the 4 stacks combined (Lakehouse
  + Litellm is the largest contributor)
- **Audit gates:** `bun run validate-stacks` + `openspec validate
  <id> --strict` + manual smoke: each consumer's locket sidecar logs
  show `secrets synced` after stack up

## Non-goals

- Not upgrading PaddleOCR (deferred; see
  `2026-07-XX-paddleocr-remediation`)
- Not migrating the Lance REST sidecar to a non-Python impl (no upstream
  Docker image exists; the custom Python sidecar is the canonical path)
- Not enabling MLflow tracing to replace Langfuse (the agent-observability
  spec keeps Langfuse for production observability; we just upgrade the
  MLflow tracking server)

## Spec delta

See `specs/infrastructure-stacks/spec.md` for the ADDED Requirements
governing each consumer stack's version pin + the MODIFIED Requirement
to `agent-observability` §"Infisical URI Format Conformance" (extending
the infisical-compose-pinned-2026-07 Scenario with a check for each of
the 4 consumer compose files). See `specs/indexing-and-cognition/spec.md`
for the Lance-namespace 0.9 contract delta.