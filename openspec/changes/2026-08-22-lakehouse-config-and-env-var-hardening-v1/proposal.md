# 2026-08-22-lakehouse-config-and-env-var-hardening-v1

## Why

PR #1 of the **4-PR lakehouse hardening series** (after `2026-08-15-lakehouse-unified-data-plane-v1` consolidated the 5 graph DB backends). This change addresses **critical config + env var hygiene** issues identified in the post-consolidation reanalysis:

1. **`postgres:16-alpine` lacks the 5 Lakekeeper-required extensions** (`uuid-ossp`, `pgcrypto`, `pg_trgm`, `btree_gin`, `btree_gist`) — Lakekeeper migrations will fail on first boot.
2. **Olake `SOURCE_DB_NAME=staging_pg` references a non-existent DB** — Olake CDC jobs will fail.
3. **`sidecar.yaml:101` has hardcoded absolute path** `/Users/cianmacandeisigh/...` for `infisical_secret` — breaks CI + production portability.
4. **6+ duplicate env var names** between root `.infisical.env` and lakehouse `secrets.env` (`LANCEDB_API_KEY` in 2 paths, `DUCKLAKE_BUCKET`/`R2_DUCKLAKE_BUCKET`, dead `COGNEE_API_URL=http://localhost:8001`, etc.) — drift risk.
5. **`.env.dev` (tracked) contains plaintext secrets** — `POSTGRES_PASSWORD`, `GARAGE_ACCESS_KEY_ID`, `CLICKHOUSE_PASSWORD`, etc.
6. **Memgraph healthcheck only tests TCP port** (not Bolt protocol) — false-positive "healthy".
7. **Lance-namespace + memgraph + memgraph-lab have no resource limits** — risk of memory exhaustion on bunchloch.
8. **Cognee doesn't `depends_on: lance-namespace: service_healthy`** — race condition on first boot.

This is a **pure config hygiene** change. No behavior change for users; no new services added.

## User preferences (locked-in)

| Decision | Choice |
|:--|:--|
| Postgres image | `pgvector/pgvector:pg17` (pgvector + postgresql-contrib in one image) |
| Olake source DB | Add `olake_source` to `init-db.sql` + auto-create |
| `.env.dev` policy | Keep as empty-value template + add CI secret-scan + move plaintext to `.env.local` (gitignored) |
| Ship strategy | This is **PR #1** of 4 — ship separately, no batching |
| Deprecated stacks | **Keep as read-only shadow stacks** (do NOT delete) |
| Observability stack | **Langfuse + MLflow + Logfire** (NOT Prometheus/Grafana) — wired in PR #4 |

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-08-15-lakehouse-unified-data-plane-v1` (extends the same compose.yaml + init-db.sql + sidecar.yaml files)
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes (10 files total)

### Modified (7 files)
| File | Change |
|:--|:--|
| `bonneagar/stacks/lakehouse/compose.yaml` | Switch `postgres:16-alpine` → `pgvector/pgvector:pg17`; add `depends_on: lance-namespace` to cognee; add `deploy.resources.limits` to lance-namespace + memgraph + memgraph-lab; replace Memgraph TCP probe with HTTP `/status` |
| `bonneagar/stacks/lakehouse/sidecar.yaml` | Replace hardcoded absolute `infisical_secret` path with `${INFISICAL_SECRET_FILE:-./infisical_secret}` |
| `bonneagar/stacks/lakehouse/init-db.sql` | Add `CREATE EXTENSION IF NOT EXISTS` for the 6 required extensions; add `CREATE DATABASE olake_source` |
| `bonneagar/stacks/lakehouse/.env.dev` | Rewrite as empty-value template (same keys + comments, blank values) |
| `.infisical.env` (root) | Remove 8 dead keys that now live in lakehouse `secrets.env` |
| `.github/workflows/lakehouse-secret-scan.yml` | NEW gitleaks workflow that fails PRs containing plaintext secrets in `bonneagar/stacks/lakehouse/` |

### New (4 files)
| File | Purpose |
|:--|:--|
| `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/proposal.md` | This file |
| `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/tasks.md` | The task list |
| `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/specs/infrastructure-stacks/spec.md` | The spec delta |
| `bonneagar/stacks/lakehouse/.env.local` | NEW gitignored plaintext secret file (replaces the plaintext in `.env.dev`) |
| `.github/workflows/lakehouse-secret-scan.yml` | NEW CI gate |

**Total: 11 files** (7 modified + 4 new — counting `.env.local` as one of the 4 new).

## Why this matters for the data plane

- **Without the Postgres extension fix**: Lakekeeper bootstrap fails silently in dev (the migration tries to CREATE EXTENSION which needs contrib). PR #2 (Lakekeeper production config) would be blocked.
- **Without the Olake source DB fix**: Olake CDC jobs that operators run after bring-up will fail with `database "staging_pg" does not exist`.
- **Without the infisical_secret path fix**: CI builds + production Komodo deploys would fail because the absolute path `/Users/cianmacandeisigh/...` only exists on the developer's laptop.
- **Without the .env.dev → .env.local move**: Plaintext secrets would remain in the git history forever. CI secret-scan prevents future drift.
- **Without the env var de-duplication**: Two different vault paths for `LANCEDB_API_KEY` (`lancedb-cloud` vs `lancedb`) create an undocumented contract — operators don't know which to read.

## Out of scope (deferred to PRs #2-4)

- **PR #2** (production hardening): Lakekeeper read replica, metrics, pagination, OpenID, OpenFGA env vars; Cognee Dataset Database Handlers modernization; FalkorDB canonical `REDIS_ARGS`/`FALKORDB_ARGS`; Lance namespace sidecar rewrite using official `lance-namespace` + `lance-namespace-impls` libs; CI workflow that publishes sidecar to `ghcr.io/cianfhoghlaim/lance-namespace-sidecar:v0.3.0`; OTel collector (for Langfuse + Logfire fan-out); Cognee PostgreSQL user isolation.
- **PR #3** (refactor + cleanup): `lakehouse/db_manifest.yaml` (single source of truth for 14 DBs); Pydantic `LakehouseSettings` class; split `.infisical.env` into 8 sub-files; `lakehouse-stack-doctor.sh`; garage-init bash → Python.
- **PR #4** (observability): Langfuse + MLflow + Logfire services (optional profile `observability`); wire all 16 lakehouse services to OTel collector → Langfuse + Logfire cloud (NOT Prometheus/Grafana); `lakehouse:all:up` orchestrator.

## Cross-references

- Spec delta: `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/specs/infrastructure-stacks/spec.md`
- Tasks: `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/tasks.md`
- Canonical skill: `.agents/skills/infrastructure-stacks/SKILL.md`
- Related change: `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/` (the prerequisite consolidation)
- Related archive: `openspec/changes/archive/2026-07-29-2026-08-15-knowledge-sync-loop-v1/`