# langfuse

## Purpose for the Cianfhoghlaim project

Langfuse v3 is the **LLM observability backbone** for the platform.
After the `centralise-data-plane` rewrite (2026-07-30) it's a pure
APPLICATION TIER over the lakehouse data plane — every BAML
extraction run (10+ functions across the per-subject pipelines),
every CocoIndex embedding generation, every study-asset image
prompt, and every LLM call from the 12-agent fleet gets a full
trace with input/output/tokens/latency/cost. When a RAGAS
evaluation flags a syllabus extraction as low-faithfulness, the
Langfuse trace shows exactly which model, which prompt, and which
document produced the result. Every trace is published to the
agentic portal's "agent activity" timeline for teacher review.

## Why it stays in komodo/pangolin/infisical GitOps

Langfuse is a **stateful application tier** with no local DB / S3 /
ClickHouse / Redis containers — every byte of state lives on the
shared lakehouse stack. The komodo `deploy-langfuse-bunchloch`
procedure ensures langfuse waits for the lakehouse stack to be
healthy first. The Infisical vault (`dev-baile/langfuse/*`) holds
the langfuse-specific secrets (SALT, ENCRYPTION_KEY,
NEXTAUTH_SECRET) while the lakehouse-* vaults hold the shared
data-plane credentials.

## Centralised Data Plane Contract

Langfuse consumes 5 resources from the lakehouse stack:

| Resource | Docker DNS | Auth |
|:--|:--|:--|
| Postgres (db=langfuse) | `lakehouse-postgres:5432` | `POSTGRES_USER` + `POSTGRES_PASSWORD` (from lakehouse/*) |
| Redis | `lakehouse-redis:6379` | `REDIS_PASSWORD` (from lakehouse-redis/*) |
| ClickHouse | `lakehouse-clickhouse:8123` | `CLICKHOUSE_USER` + `CLICKHOUSE_PASSWORD` (from lakehouse-clickhouse/*) |
| S3 (events) | `lakehouse-garage:3900` | `GARAGE_ACCESS_KEY_ID` + `GARAGE_SECRET_ACCESS_KEY` (from lakehouse-garage/*) → bucket `langfuse-events` |
| S3 (media) | `lakehouse-garage:3900` | → bucket `langfuse-media` |
| S3 (exports) | `lakehouse-garage:3900` | → bucket `langfuse-exports` |

The 3 Garage buckets are auto-created by `lakehouse/garage-init` on
first lakehouse deploy.

## Cross-references

- **Ops**: `bonneagar/stacks/langfuse/` (the 6-file GOLD_STANDARD + `compose.dev.yaml`)
- **Code**: every BAML client uses `@observe(name=...)` per `.agents/skills/agent-observability/SKILL.md`
- **Komodo procedure**: `deploy-langfuse-bunchloch.toml` (3-stage: lakehouse deploy → langfuse deploy → 5 health checks). The arm1-oci variant is at `bonneagar/komodo/procedures/langfuse.toml`.
- **Pangolin**: `https://langfuse.cianfhoghlaim.ie/api/public/health` (Member role + secure-headers)

## Tags

- `host:bunchloch` (primary) / `host:arm1-oci` (production)
- `tier:observability`
- `project:cianfhoghlaim`
- `group:observability` (depends on `foundation`)
