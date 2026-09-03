# litellm

## Purpose for the Cianfhoghlaim project

LiteLLM is the **M3 LLM gateway chokepoint** for the entire platform
— the central place where the agent fleet, the BAML extraction
clients, the CocoIndex embedding flows, and the 12 subject
specialist agents all reach the 70+ model routing. After the
`centralise-data-plane` rewrite (2026-07-30) its only state (the
model registry) lives on the shared lakehouse-postgres
`litellm` database. The gateway connects to OpenCode Go as the
canonical LLM backbone, routes to HuggingFace-hosted models via
the shared cache, and federates access control through a single
master key (`LITELLM_MASTER_KEY`).

## Why it stays in komodo/pangolin/infisical GitOps

LiteLLM is the single point of egress for every AI call, so it
must be:

1. **Reproducible** — registered in `bonneagar/iac/komodo/deploy-stacks.ts`
   with tags `host:bunchloch + tier:data-engineering`
2. **Secure** — bypasses any per-provider token sprawl; every
   downstream consumer uses `http://litellm:4000/v1` with a single
   master key
3. **Observability-forward** — every call is auto-traced to
   `langfuse` (per the `LANGFUSE_HOST` + `LANGFUSE_PUBLIC_KEY` env
   vars) and experiment-logged to `mlflow` (per `MLFLOW_TRACKING_URI`)

The komodo `deploy-litellm-bunchloch` procedure waits for the
lakehouse stack to be healthy first, then deploys litellm.

## Centralised Data Plane Contract

| Resource | Docker DNS | Auth |
|:--|:--|:--|
| Postgres (db=litellm) | `lakehouse-postgres:5432` | `POSTGRES_USER` + `POSTGRES_PASSWORD` (from lakehouse/*) |
| HuggingFace cache | `stedding/huggingface` (bind-mounted) | `HF_TOKEN` (from litellm/*) |

The 8 OpenCode Go parallel keys, the 5 cloud-provider keys
(Anthropic, OpenAI, Gemini, Z.AI, ZAI), and the 3 HuggingFace
token aliases are all resolved from the litellm/* Infisical
vault.

## Cross-references

- **Ops**: `bonneagar/stacks/litellm/` (the 6-file GOLD_STANDARD + `config/config.yaml` model registry + `compose.dev.yaml`)
- **Code**: the per-model routing keyword map at `.agents/skills/agent-fleet-orchestration/SKILL.md`
- **Komodo procedure**: `deploy-litellm-bunchloch.toml` (3-stage: lakehouse → litellm → 4 health checks). The arm1-oci variant is at the existing `langfuse.toml`-style.
- **Pangolin**: `https://litellm.cianfhoghlaim.ie/health/liveliness` (Member role)

## Tags

- `host:bunchloch` (primary) / `host:arm1-oci` (production)
- `tier:data-engineering` + `tier:language-model`
- `project:cianfhoghlaim`
- `group:observability` (depends on `foundation`)
