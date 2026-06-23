# LiteLLM Gateway

## Overview
LiteLLM is an open-source AI gateway that provides a single, OpenAI-compatible API for calling 100+ LLM providers including Anthropic, OpenAI, Google, DeepSeek, and HuggingFace models. Created by BerriAI and maintained by a team of contributors, it offers cost tracking, rate limiting, load balancing, guardrails and comprehensive logging. The `ghcr.io/berriai/litellm:main-stable` image runs with a Postgres 16 backend and Prometheus monitoring.

## Why This Matters for Kings' College Galway
LiteLLM is the central LLM routing layer for all AI-driven study asset generation at Kings' College Galway. It proxies every AI call — from Leaving Cert exam question extraction to bilingual Irish/English content generation — through a single API surface with unified cost tracking and Langfuse observability. The gateway connects to the OpenCode Go endpoint as the LLM backbone, routes to HuggingFace-hosted models via the shared cache, and federates access control through a single master key. Without LiteLLM, the entire Celtic education curriculum pipeline would lack a unified AI control plane.

## Key Features
- OpenAI-compatible API proxy for 100+ LLM providers (Anthropic, Gemini, DeepSeek, OpenCode Go, HuggingFace)
- Built-in cost tracking, rate limiting, and load balancing
- Postgres 16 model registry with Prometheus metrics at `/metrics`
- Cosign-signed Docker images with 4-worker parallel serving
- Langfuse + MLflow observability integration for trace-level LLM monitoring

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/litellm
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/litellm
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LITELLM_MASTER_KEY` | Yes | Gateway master API key (from Infisical) | — |
| `LITELLM_SALT_KEY` | No | Encryption salt for API key hashing | — |
| `LITELLM_DATABASE_URL` | Yes | Connection URL for LiteLLM's own Postgres | — |
| `GEMINI_API_KEY` | No | Google Gemini API key | — |
| `ANTHROPIC_API_KEY` | No | Anthropic Claude API key | — |
| `OPENAI_API_KEY` | No | OpenAI API key | — |
| `Z_AI_API_KEY` | No | Z.AI API key | — |
| `ZAI_API_KEY` | No | ZAI API key | — |
| `OPENCODE_GO_API_KEY` | No | OpenCode Go API key | — |
| `OPENCODE_GO_BASE_URL` | No | OpenCode Go base URL | `https://opencode.ai/zen/go/v1` |
| `HF_TOKEN` | No | HuggingFace token for gated models | — |
| `HUGGINGFACE_HUB_TOKEN` | No | HuggingFace Hub token (alias) | — |
| `HUGGINGFACE_TOKEN` | No | HuggingFace token (alias) | — |
| `LANGFUSE_HOST` | No | Langfuse observability host URL | — |
| `LANGFUSE_PUBLIC_KEY` | No | Langfuse public key | — |
| `LANGFUSE_SECRET_KEY` | No | Langfuse secret key | — |
| `MLFLOW_TRACKING_URI` | No | MLflow tracking URI | `http://mlflow:5000` |
| `LANCEDB_API_KEY` | No | LanceDB API key | — |
| `USE_GEMINI_3` | No | Enable Gemini 3 feature flag | `false` |
| `LITELLM_LOG` | No | Log level | `INFO` |
| `LITELLM_POSTGRES_DB` | No | Postgres database name | `litellm` |
| `LITELLM_POSTGRES_USER` | No | Postgres username | `llmproxy` |
| `LITELLM_POSTGRES_PASSWORD` | Yes | Postgres password | — |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key (from secrets.env) | — |

## Access
- **URL**: `https://litellm.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 4000 (gateway API), 9090 (Prometheus metrics)
- **Auth**: LiteLLM master key (`LITELLM_MASTER_KEY`)

## Health Check
```bash
docker ps --filter name=litellm --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/BerriAI/litellm
- **Documentation**: https://docs.litellm.ai
- **Latest release**: v1.87.1 (2026-06-04) — Backported fixes into stable branch including session-token budget-ceiling exemption and multiple staged fixes.

## Screenshot

![LiteLLM Documentation](https://storage.googleapis.com/firecrawl-scrape-media/screenshot-ec272ea2-035f-42cb-a737-0022e6c19f04.png)

LiteLLM's documentation at [docs.litellm.ai](https://docs.litellm.ai) covers the full API surface: 100+ LLM providers, load balancing, fallbacks, spend tracking, and virtual keys. The admin UI shows model health per deployment, rate limit configuration, and per-user/per-team budget management.
