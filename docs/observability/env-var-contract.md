# Observability Env-Var Contract — Canonical Reference

> Source-of-truth for the 17 environment variables that wire the
> Langfuse + MLflow + Logfire observability stack across the
> Cianfhoghlaim platform. Every KCG service that emits traces,
> experiments, or LLM traces reads from this table.
>
> **Updated:** 2026-07-30 (env-contract-and-observability-fanout-v1)
> **Owner:** observability skill (`.agents/skills/agent-observability/`)
> **Spec:** `openspec/changes/2026-07-30-.../specs/agent-observability/spec.md`

## The 17 canonical variables

The contract is partitioned into 4 groups: Langfuse SDK (4 vars),
MLflow tracking (3 vars), Logfire / OTel fan-out (7 vars), and
shared cluster (3 vars).

### Group 1 — Langfuse SDK (4 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `LANGFUSE_HOST` | URL | yes | `infisical://dev-baile/langfuse/host` | The Langfuse server URL. **Canonical value:** `https://langfuse.cianfhoghlaim.ie` (production) or `http://langfuse:3000` (in-cluster). Never hardcode `localhost`. |
| `LANGFUSE_PUBLIC_KEY` | string | yes | `infisical://dev-baile/langfuse/public_key` | Project public key. Format: `pk-lf-<project>-<random>`. |
| `LANGFUSE_SECRET_KEY` | string | yes | `infisical://dev-baile/langfuse/secret_key` | Project secret key. Format: `sk-lf-<project>-<random>`. |
| `LANGFUSE_AUTH_HEADER` | string | yes (collector only) | `infisical://dev-baile/logfire/auth_header` | **Logfire-collector-only**: the base64-encoded `PUBLIC_KEY:SECRET_KEY` pair used as the HTTP Basic auth header for the `otlphttp/langfuse` exporter in `otelcol.yaml`. Constructed as: `echo -n "$PUBLIC_KEY:$SECRET_KEY" \| base64 -w0`. |

### Group 2 — MLflow tracking (3 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `MLFLOW_TRACKING_URI` | URL | yes | `infisical://dev-baile/mlflow/uri` | **Canonical value:** `http://mlflow:5000` (in-cluster) or `https://mlflow.cianfhoghlaim.ie` (external). Never hardcode `localhost:5000` (collides with macOS AirPlay Receiver). |
| `MLFLOW_EXPERIMENT_NAME` | string | no (default `dlt-pipelines`) | `infisical://dev-baile/mlflow/experiment_name` | The default experiment for any `mlflow.set_experiment(...)` call without an explicit name. |
| `MLFLOW_S3_ENDPOINT_URL` | URL | yes (artifact store) | `infisical://dev-baile/lakehouse/s3_endpoint` | **Canonical value:** `http://lakehouse-garage:3900` (the centralised Garage S3 from the lakehouse stack). Required for `mlflow.log_artifact(...)`. |

### Group 3 — Logfire + OpenTelemetry fan-out (7 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | URL | yes (every backend) | `infisical://dev-baile/logfire/otel_endpoint` | **Canonical value:** `http://logfire-otel:4317` (gRPC) or `http://logfire-otel:4318` (HTTP). The collector fans out to BOTH logfire cloud AND langfuse. |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | enum | no (default `grpc`) | env block only | `grpc` (preferred for Python OTEL SDKs) or `http/protobuf` (fallback). |
| `OTEL_SERVICE_NAME` | string | yes | compose.yaml literal | The service name as it appears in the Logfire/Langfuse UI. Convention: lowercase, hyphenated, matches the compose service name. |
| `LOGFIRE_TOKEN` | string | yes (collector) | `infisical://dev-baile/logfire/write_token` | Pydantic Logfire write token (from `https://logfire.pydantic.dev` → Project Settings → Tokens). Required for the `logfire` exporter in the collector. |
| `LOGFIRE_PROJECT_NAME` | string | no (default `oideachas-celtic-education`) | env block only | Resource attribute on every trace; groups spans by project in the Logfire UI. |
| `LOGFIRE_ENVIRONMENT` | enum | no (default `production`) | env block only | Resource attribute; values: `production`, `staging`, `development`. |
| `LOGFIRE_SERVICE_NAME` | string | no (legacy) | env block only | Legacy attr (replaced by `OTEL_SERVICE_NAME`). Keep for backwards compat with old dashboards. |

### Group 4 — Shared cluster identity (3 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `INFISICAL_TOKEN` | string | yes (operator-side) | `.env` only | Universal Auth machine-identity token for the operator's local CLI (`bun run scripts/init-vault.ts`). NOT shipped to containers — they use the bons-locket-shim instead. |
| `INFISICAL_PROJECT_ID` | UUID | yes (operator-side) | `.env` only | The `dev-baile` workspace UUID. Canonical value (verified live 2026-07-29): `d900f50a-acbf-446b-b4f6-e439710253e4`. |
| `INFISICAL_ENV` | string | no (default `dev`) | `.env` only | The environment slug. Canonical: `dev-baile` (not `dev` — the human-readable name differs from the slug). |

## How the 17 variables flow through the platform

```
Operator's .env (local)
  │
  ▼
mise run secrets:init          (syncs to Infisical)
  │
  ▼
Infisical dev-baile vault
  │
  ├─► bons-locket-shim (sidecar in 86 of 91 stacks)
  │     │
  │     ▼
  │   /run/secrets/locket/secrets.env (resolved values)
  │     │
  │     ▼
  │   service's env block  (e.g. graphiti, cognee, mlflow, agent-os)
  │
  └─► otelcol.yaml (logfire stack)
        │
        ├─► logfire exporter → logfire cloud
        └─► otlphttp/langfuse exporter → langfuse-web:3000/api/public/otel
```

The **single pane of glass** invariant: every trace that reaches the
collector reaches BOTH backends.

## Per-stack wireup matrix

Quick reference for which stacks read which vars. **✓** = declared in
`compose.yaml`; **L** = resolved by Locket from `secrets.env`.

| Stack | LANGFUSE_HOST | LANGFUSE_PUBLIC_KEY | LANGFUSE_SECRET_KEY | MLFLOW_TRACKING_URI | OTEL_EXPORTER_OTLP_ENDPOINT | OTEL_SERVICE_NAME |
|:--|:-:|:-:|:-:|:-:|:-:|:-:|
| graphiti | ✓ L | ✓ L | ✓ L | — | ✓ L | `graphiti` |
| cognee | ✓ L | ✓ L | ✓ L | — | ✓ L | `cognee` |
| mlflow | — | — | — | ✓ L (server-side) | ✓ L | `mlflow` |
| agent-os (×4) | ✓ L | ✓ L | ✓ L | — | — | — |
| dagster | ✓ L | ✓ L | ✓ L | — | ✓ env | `dagster` |
| openclaw | ✓ L | ✓ L | ✓ L | — | ✓ L | `openclaw-gateway` |
| openchamber | — | — | — | — | ✓ L | `openchamber` |
| hermes | ✓ L | ✓ L | ✓ L | — | ✓ L | `hermes-agent` |
| litellm | ✓ L | ✓ L | ✓ L | ✓ L | — | — |
| logfire (collector) | — | ✓ L | ✓ L | — | — | — |

## CI gate

The grammar + wireup invariant is enforced by the mise task:

```bash
mise run stack-doctor:strict
```

This runs `bash scripts/stack-doctor.sh --strict --check-grammar` which:

1. Fails any `secrets.env` with mixed bare + Jinja grammar
2. Fails any `secrets.env` with zero `infisical://` URIs
3. (Future) Fails any stack that declares `${LANGFUSE_*}` in compose.yaml but lacks the matching `infisical://...` line in `secrets.env`

The third check is the contract-enforcement for this table — it
prevents the "silent Langfuse loss" pattern (the agent-os bug fixed
in this change).

## Why 17 variables (not 50)?

The 17 variables are the **set that spans the full observability
stack** — every variable in this table is read by at least 2 stacks;
every observability use case is covered.

Variables that exist but are NOT in this contract:
- Per-service debug knobs (`LOG_LEVEL`, `LOGFIRE_VERBOSITY`)
- Per-LLM-provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
  `GEMINI_API_KEY`) — see `docs/llm-env-var-contract.md` (TODO)
- Per-stack port mappings — see `infrastructure-stacks` spec

## Cross-references

- `.agents/skills/agent-observability/SKILL.md` — the operator-facing usage guide
- `.agents/skills/secrets-management/SKILL.md` — the Infisical + Locket + mise contract
- `openspec/changes/2026-07-30-.../specs/agent-observability/spec.md` — the formal requirement
- `bonneagar/stacks/logfire/config/otelcol.yaml` — the fan-out collector config
- `dlt_sources/common/observability.py` — the canonical DLT instrumentation helper