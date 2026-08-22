# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Langfuse MUST be configured with the 3 critical security env vars

The Langfuse compose stack (`bonneagar/stacks/langfuse/compose.yaml`) SHALL set the following 3 critical security env vars on BOTH `langfuse-web` and `langfuse-worker` services:
- `NEXTAUTH_SECRET` (NextAuth authentication secret — `openssl rand -base64 32`)
- `SALT` (API-key hashing salt — `openssl rand -base64 32`)
- `ENCRYPTION_KEY` (256-bit hex — `openssl rand -hex 32`)

If any of these 3 env vars is unset when docker compose runs, compose MUST fail with a clear error message. This prevents the Langfuse deployment from running with weak default secrets.

Per the official Langfuse self-hosting docs (https://langfuse.com/self-hosting/configuration) — these 3 env vars are listed as `Required` for production deployments.

#### Scenario: Operator brings up Langfuse

- **GIVEN** the lakehouse stack + langfuse stack are both deployed
- **AND** the 3 critical env vars (`NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY`) are set in `.env.local`
- **WHEN** `docker compose -f compose.yaml -f sidecar.yaml up -d` runs
- **THEN** langfuse-web + langfuse-worker come up with the 3 env vars resolved from Infisical (via Locket)
- **AND** langfuse-web serves on port 3000 (reachable via pangolin.cianfhoghlaim.ie)
- **AND** langfuse-worker runs the ingestion queue without auth errors

#### Scenario: Operator forgets to set a critical env var

- **GIVEN** the lakehouse stack + langfuse stack are both deployed
- **AND** `NEXTAUTH_SECRET` is unset in `.env.local`
- **WHEN** `docker compose -f compose.yaml -f sidecar.yaml up -d` runs
- **THEN** docker compose MUST fail with the error: `ERROR: NEXTAUTH_SECRET must be set via Locket/Infisical`
- **AND** langfuse-web + langfuse-worker MUST NOT start

### Requirement: MLflow MUST be configured with the v3.5.0+ security middleware env vars

The MLflow compose stack (`bonnegar/stacks/mlflow/compose.yaml`) MUST use image `ghcr.io/mlflow/mlflow:v3.15.1` (or later) AND MUST set the following canonical v3.5.0+ security middleware env vars:
- `MLFLOW_SERVER_ALLOWED_HOSTS` (DNS-rebinding Host validation; comma-separated list)
- `MLFLOW_SERVER_CORS_ALLOWED_ORIGINS` (browser CORS allow-list; comma-separated list)

The compose MUST NOT use the CLI flag form (`--allowed-hosts ... --cors-allowed-origins ...`) — env vars are canonical and survive `docker compose restart`.

Per the official MLflow v3.5.0 release notes (https://mlflow.org/releases) — these env vars are **mandatory** when binding to `0.0.0.0` (since v3.5.0+ ships a security middleware that locks the server to localhost unless overridden).

#### Scenario: Operator deploys MLflow with security middleware enabled

- **GIVEN** the MLflow compose is configured with `MLFLOW_SERVER_ALLOWED_HOSTS="mlflow.cianfhoghlaim.ie"`
- **WHEN** the MLflow container starts on port 5000
- **THEN** the DNS-rebinding attack vector is closed (only requests with `Host: mlflow.cianfhoghlaim.ie` are accepted)
- **AND** browser requests from `https://cianfhoghlaim.cianfhoghlaim.ie` are accepted via CORS
- **AND** Dagster assets that log to MLflow via `mlflow.set_tracking_uri("http://mlflow:5000")` work without CORS preflight failures

#### Scenario: Operator tries to bind MLflow without security env vars

- **GIVEN** the MLflow compose has no `MLFLOW_SERVER_ALLOWED_HOSTS` set
- **WHEN** the MLflow container starts on port 5000
- **THEN** the v3.5.0+ security middleware locks the server to localhost only
- **AND** requests from `mlflow.cianfhoghlaim.ie` are rejected with 403 Forbidden

### Requirement: Dagster MUST use the official 1.13+ images + declarative config

The Dagster compose stack (`bonnegar/stacks/dagster/compose.yaml`) MUST use:
- `image: dagster/dagster-webserver:1.13.18` for the webserver
- `image: dagster/dagster-daemon:1.13.18` for the daemon

The Dagster deployment MUST include the 3 declarative config files (mounted into the container):
- `dagster.yaml` — instance config (storage + run coordinator + logging)
- `dagster-daemon.yaml` — daemon-specific config (scheduler + sensor concurrency)
- `workspace.yaml` — code locations declaration

The `dagster-daemon` service MUST have `deploy.replicas: 1` (the Dagster daemon is officially singleton per the docs — multiple replicas are NOT supported).

Per the official Dagster docs (https://docs.dagster.io/deployment/oss/dagster-yaml + https://docs.dagster.io/deployment/execution/dagster-daemon).

#### Scenario: Operator brings up Dagster

- **GIVEN** `bonneagar/stacks/dagster/` has `dagster.yaml` + `dagster-daemon.yaml` + `workspace.yaml`
- **WHEN** `docker compose -f compose.yaml -f sidecar.yaml up -d` runs
- **THEN** `dagster` (webserver) comes up on port 3335 with the declarative config
- **AND** `dagster-daemon` comes up as a SINGLETON (1 replica only)
- **AND** `workspace.yaml` declares the `orchestration.defs` code location
- **AND** schedules + sensors run on the daemon (not the webserver)

#### Scenario: Operator tries to scale dagster-daemon to 2 replicas

- **GIVEN** the compose has `deploy.replicas: 1` for `dagster-daemon`
- **WHEN** the operator tries to scale with `docker compose up --scale dagster-daemon=2`
- **THEN** Docker emits a warning ("scale is ignored for deploy.replicas")
- **AND** only 1 daemon replica runs (the singleton constraint)

## REMOVED Requirements

(None — no requirement removed in this change.)