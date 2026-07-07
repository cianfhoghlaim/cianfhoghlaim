# Agent Observability — Wave 2 Lakehouse Integration Delta

> This file is the change-side delta for
> `2026-07-02-replace-private-images-and-bring-wave2`. It applies on
> top of the canonical `agent-observability` spec at
> `../../../../specs/agent-observability/spec.md` and on top of the
> prior `2026-07-02-bunchloch-stack-bootstrap` delta.

## ADDED Requirements

### Requirement: Langfuse host port alignment

The system SHALL expose langfuse on host port `:3001` (per the
langfuse compose.yaml `127.0.0.1:3001:3000` mapping) and the
application code SHALL default `LANGFUSE_HOST` to
`http://localhost:3001` (not `:3000`).

#### Scenario: Langfuse reachable from cianfhoghlaim
- **WHEN** an agent or Dagster asset makes a Langfuse trace
- **THEN** the trace SHALL be POSTed to `http://localhost:3001/api/public/ingestion`
- **AND** `curl http://localhost:3001/api/public/health` SHALL return 200

#### Scenario: Langfuse env var
- **WHEN** the cianfhoghlaim code initializes Langfuse
- **THEN** `os.getenv("LANGFUSE_HOST", "http://localhost:3001")`
  SHALL be the default (the code-side default is updated in
  Change 8 to align with this port mapping)

### Requirement: Logfire OTel-collector-only mode (no SaaS required)

The system SHALL support a self-hosted Logfire mode where the
`logfire` OTel collector (on port 4317/4318) receives all spans
WITHOUT requiring a SaaS `LOGFIRE_TOKEN`. This is the dev mode
behaviour per `agent-observability` §"Logfire Stack Self-Hosted
Compose".

The code path in `observability/logfire_config.py` SHALL:
- When `LOGFIRE_TOKEN` is set, send to Logfire SaaS as today
- When `LOGFIRE_TOKEN` is empty (dev mode), bypass `send_to_logfire`
  and instead rely on `OTEL_EXPORTER_OTLP_ENDPOINT` env var to
  point at the local `logfire` OTel collector

#### Scenario: Dev mode with no Logfire SaaS
- **WHEN** `LOGFIRE_TOKEN` is empty
- **THEN** the logfire Python client SHALL initialize WITHOUT
  requiring a SaaS endpoint
- **AND** all spans SHALL be sent to the `OTEL_EXPORTER_OTLP_ENDPOINT`
  (default: `http://logfire:4317` inside docker network,
  `http://127.0.0.1:4317` on host)
- **AND** the OTel collector SHALL buffer and forward to Logfire
  SaaS IF `LOGFIRE_TOKEN` is also set on the collector (currently
  not wired — the dev collector is a pure black-hole buffer)

#### Scenario: Production mode with Logfire SaaS
- **WHEN** `LOGFIRE_TOKEN` is non-empty
- **THEN** the logfire Python client SHALL send to Logfire SaaS as
  the primary destination (in addition to the local OTel collector
  if both are configured)
- **AND** the OTLP collector SHALL forward to Logfire SaaS as
  configured by its own env vars (currently deferred — production
  uses SaaS directly per the comment in
  `agent-observability/spec.md`)

### Requirement: MLflow tracking URI alignment

The system SHALL use `http://localhost:5000` as the default
`MLFLOW_TRACKING_URI` (per the mlflow compose.yaml `0.0.0.0:5000:5000`
mapping). The `MLFLOW_BACKEND_STORE_URI` SHALL point at the
lakehouse-postgres `mlflow` database (db=`mlflow`).

#### Scenario: MLflow writes trace to lakehouse
- **WHEN** a Dagster asset (or any tracked Python code) calls
  `mlflow.log_param` or `mlflow.log_metric`
- **THEN** the log record SHALL be stored in
  `postgresql://lakekeeper:devpassword@lakehouse-postgres:5432/mlflow`
  (the centralised dev DB)
- **AND** `MLFLOW_S3_ENDPOINT_URL` SHALL point at
  `http://lakehouse-garage:3900` for artifact storage

#### Scenario: MLflow artifacts in Garage
- **WHEN** a tracked experiment logs an artifact (model, plot, dataset)
- **THEN** the artifact SHALL be uploaded to
  `s3://mlflow-artifacts/` in the lakehouse Garage
- **AND** the artifact SHALL be retrievable via the MLflow UI at
  `http://localhost:5000`
