## ADDED Requirements

### Requirement: Unstract OSS Self-Host at v0.177.7 (15-service fleet)

The `bonneagar/stacks/unstract/` stack MUST match the upstream
`Zipstack/unstract:v0.177.7` (released 2026-07-06) 15-service
docker-compose layout, vendored as 731 lines + 6 unstract images +
7 infrastructure images, with the KCG bare container-name
convention applied.

#### Scenario: Unstract compose is a true 15-service fleet

- **WHEN** `compose.yaml` is read
- **THEN** it SHALL declare ALL 6 upstream unstract images pinned to
  `:v0.177.7`:
  - `unstract/backend:v0.177.7`
  - `unstract/frontend:v0.177.7`
  - `unstract/platform-service:v0.177.7`
  - `unstract/x2text-service:v0.177.7`
  - `unstract/runner:v0.177.7`
  - `unstract/worker-unified:v0.177.7`
- **AND** it SHALL declare the 6 worker-unified worker services
  (api-deployment, callback, file-processing, general, notification,
  log-consumer, scheduler, executor, log-history-scheduler)
- **AND** it SHALL declare the 7 infrastructure services
  (pgvector, redis, minio, qdrant, rabbitmq, flipt, traefik) with
  pinned semver tags
- **AND** every container SHALL be named with the bare KCG pattern
  (`unstract-backend`, `unstract-worker-api-deployment`, etc.) — NOT
  the upstream's `*-1` numeric suffixes
- **AND** the `db` image SHALL be `pgvector/pgvector:pg15` (matching
  the upstream dev-essentials default)
- **AND** the `secrets.env` SHALL declare at least 20 canonical
  `infisical://dev-baile/unstract/<key>` entries (no Jinja `{{...}}`
  wrappers)
- **AND** the `sidecar.yaml` SHALL declare the canonical Locket
  sidecar (user 65532:65532, no-new-privileges, cap_drop ALL, tmpfs 700)
- **AND** the `compose.dev.yaml` SHALL override the locket service
  with a no-op alpine container that passes healthcheck

### Requirement: Unstract secrets in Infisical vault

The bunchloch-local Infisical vault MUST contain at least 20 secrets
under the path `dev-baile/dev/unstract/*`, covering postgres, minio,
qdrant, rabbitmq, django, celery, oauth, and LLM-provider keys.

#### Scenario: Universal Auth can read all 21 unstract secrets

- **WHEN** the bunchloch-locket-machine UA identity logs in to the
  local Infisical and queries `GET /api/v3/secrets/raw/<key>?workspaceId=...&environment=dev&secretPath=/unstract`
- **THEN** the response SHALL contain the secret value for at least
  20 distinct keys (postgres_user, postgres_password, postgres_db,
  postgres_schema, minio_root_user, minio_root_password,
  minio_access_key, minio_secret_key, qdrant_user, qdrant_pass,
  qdrant_db, rabbitmq_user, rabbitmq_pass, django_secret_key,
  celery_broker_url, celery_result_backend, openai_api_key, etc.)