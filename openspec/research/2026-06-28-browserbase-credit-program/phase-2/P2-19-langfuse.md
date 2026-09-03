# P2-19 — langfuse (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

Langfuse is the **LLM observability platform** that traces every LiteLLM call, BAML extraction, and opencode subagent dispatch. It runs as a self-hosted stack on arm1-oci at `langfuse.cianfhoghlaim.ie:3000` with Postgres + ClickHouse + S3 (for trace storage).

The canonical Cianfhoghlaim pattern: every LLM call auto-traces via LiteLLM's Langfuse integration; BAML calls use the `@observe` decorator; opencode subagents tag their dispatches via the `metadata.user_id` + `metadata.session_id` pattern.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/langfuse/compose.yaml` | Langfuse web + worker + Postgres + ClickHouse |
| `stacks/langfuse/blueprint.yaml` | Pangolin private-resource (`langfuse.cianfhoghlaim.ie:3000`) |
| `stacks/langfuse/sidecar.yaml` | Locket sidecar |
| `oideachais/baml_src/clients.baml` | BAML clients with `@observe` decorator |
| `cognify/rules/langfuse_dashboards.py` | Pre-built dashboards (per-agent spend, per-task latency) |
| `stacks/litellm/config/config.yaml` (langfuse block) | LiteLLM's Langfuse integration config |

**LiteLLM Langfuse integration** (from `stacks/litellm/config/config.yaml` line ~795):

```yaml
langfuse:
  langfuse_enabled: true
  langfuse_host: os.environ/LANGFUSE_HOST
  langfuse_public_key: os.environ/LANGFUSE_PUBLIC_KEY
  langfuse_secret_key: os.environ/LANGFUSE_SECRET_KEY
```

**BAML @observe decorator** (`oideachais/baml_src/clients.baml`):

```baml
client<llm> MiniMax {
  provider "openai"
  api_key env.MINIMAX_API_KEY
  base_url env.LITELLM_BASE_URL
  options {
    headers {
      "X-Langfuse-User-Id" env.LANGFUSE_USER_ID  // auto-tags every trace
      "X-Langfuse-Session-Id" env.LANGFUSE_SESSION_ID
    }
  }
}

function ExtractCurriculum(doc: string) -> Curriculum {
  client MiniMax
  prompt #"
    Extract the curriculum from {{ doc }}.
    {{ ctx.output_format }}
  "
}
```

**Custom span** (in BAML):

```baml
function TraceExtractCurriculum(doc: string) -> Curriculum {
  client MiniMax
  // The @observe decorator auto-creates a span in Langfuse
  span "extract-curriculum" {
    metadata {
      "phase": "5-stage-pdf"
      "subject": subject
      "doc_size": doc.size()
    }
    return ExtractCurriculum(doc)
  }
}
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `LANGFUSE_HOST` | `https://langfuse.cianfhoghlaim.ie` | Locket |
| `LANGFUSE_PUBLIC_KEY` | `infisical://dev-baile/langfuse/public_key` | Locket |
| `LANGFUSE_SECRET_KEY` | `infisical://dev-baile/langfuse/secret_key` | Locket |
| `LANGFUSE_USER_ID` | `os.environ/USER` (set by mise) | per-host |
| `LANGFUSE_SESSION_ID` | `os.environ/SESSION_ID` (per opencode session) | per-session |
| `LANGFUSE_DATABASE_URL` | `postgres://langfuse-postgres:5432/langfuse` | compose env |
| `LANGFUSE_S3_BUCKET` | `langfuse-traces` (on Garage) | compose env |

## CCC anchors

`stacks/langfuse/` · `oideachais/baml_src/clients.baml` · `cognify/rules/langfuse_dashboards.py` · `stacks/litellm/config/config.yaml` (langfuse block)

Search terms: `"@observe"`, `"langfuse_enabled: true"`, `"X-Langfuse-User-Id"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-10 | Initial Langfuse deploy (LiteLLM integration) |
| 2025-12 | Added ClickHouse for trace storage (10x faster queries) |
| 2026-01 | Migrated from Langfuse Cloud to self-hosted |
| 2026-03 | Added BAML `@observe` decorator pattern |
| 2026-04 | Built 6 pre-built dashboards (per-agent spend, per-task latency, etc.) |
| 2026-05 | Added `metadata.fallback_triggered` to track when `minimax` fallback fires |

## Anti-patterns

1. Don't log full LLM responses — they're expensive in ClickHouse storage
2. Don't put PII in trace metadata — Langfuse is per-org
3. Don't disable `langfuse_enabled` — you lose visibility into the fallback chain
4. Don't use `LANGFUSE_DEBUG=true` in production — it leaks secrets to stdout
5. Don't skip the `session_id` tag — without it, traces can't be grouped by session
6. Don't put traces in the same Postgres as the Langfuse web UI — separate read/write paths
7. Don't use the Langfuse Cloud API — it's expensive at scale

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Hosting | Self-hosted (arm1-oci) | Cost + privacy |
| Storage | ClickHouse (traces) + Postgres (metadata) | Optimized for time-series |
| Trace sampling | 100% (for now) | Low volume (~10K calls/day) |
| SDK integration | LiteLLM auto-instrument | Zero code changes |
| BAML integration | `@observe` decorator + `@trace` | Fine-grained spans |
| Auth | OIDC via Pocket ID | Single SSO source |
| Dashboard count | 6 pre-built + ad-hoc queries | Covers 80% of operator needs |
| Retention | 30 days (ClickHouse), 1 year (Postgres) | Balance cost vs debugging |

## Files to read next

`stacks/langfuse/compose.yaml` · `oideachais/baml_src/clients.baml` · `cognify/rules/langfuse_dashboards.py` · `.agents/skills/langfuse/SKILL.md` · `.agents/skills/agent-observability/SKILL.md`
