# Pydantic AI Gateway

## Overview
The Pydantic AI Gateway is a managed LLM routing service from Pydantic that provides a unified API for accessing multiple LLM providers with a single API key. It offers cost tracking, usage monitoring, and BYOK (Bring Your Own Key) support — routing requests to OpenAI, Anthropic, Google, and other providers through a single proxy endpoint at `https://gateway.pydantic.dev`. This stack has no local container; it uses the SaaS service configured via environment variables.

## Why This Matters for Kings' College Galway
The Pydantic AI Gateway serves as an alternative LLM routing path alongside LiteLLM for specific Claude Code integrations and Pydantic-native AI workflows. When the `códeolas` code intelligence library or the `sruth-browser` automation client needs structured LLM outputs with Pydantic validation, the gateway provides type-safe response parsing that aligns with the platform's `dignified-python` conventions. It also serves as a cost-accountability layer — tracking which platform component spends what on which model — and integrates with the Langfuse observability stack for trace-level auditing of AI-generated study content.

## Key Features
- Unified LLM access with single API key across OpenAI, Anthropic, and more
- Built-in cost tracking and usage analytics per API key
- BYOK support for using your own provider API keys
- Type-safe structured output support (native Pydantic integration)
- Proxy endpoints for direct provider access (e.g., `/proxy/anthropic`)

## Deployment
This stack uses the managed Pydantic Gateway SaaS — no local Docker container required. Configuration is injected via Locket from Infisical `dev-baile`.

```bash
# Secrets are hydrated by mise hooks on directory entry
# No docker compose needed — environment-only configuration
```

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PYDANTIC_AI_GATEWAY_API_KEY` | Yes | Pydantic Gateway API key | — |
| `PYDANTIC_GATEWAY_URL` | No | Gateway base URL | `https://gateway.pydantic.dev` |
| `ANTHROPIC_BASE_URL` | No | Anthropic proxy endpoint | `https://gateway.pydantic.dev/proxy/anthropic` |
| `ANTHROPIC_AUTH_TOKEN` | No | Anthropic auth token (same as API key) | — |

## Access
- **URL**: `https://gateway.pydantic.dev` (managed SaaS)
- **Auth**: Pydantic AI Gateway API key

## Health Check
```bash
curl -H "Authorization: Bearer $PYDANTIC_AI_GATEWAY_API_KEY" https://gateway.pydantic.dev/health
```

## Upstream
- **Repository**: https://github.com/pydantic/pydantic-ai
- **Documentation**: https://ai.pydantic.dev/gateway/
- **Latest release**: Managed SaaS service — tracks Pydantic AI releases.
