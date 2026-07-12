# AgentOS (Agno Multi-Agent Runtime)

## Overview
AgentOS is a production runtime for Agno-based AI agent systems, hosting four domain-specific agent services under a single Docker Compose stack. Each agent runs on its own port with isolated storage, Langfuse observability, and cross-agent communication via internal HTTP. The four agents are: Oideachais (Irish Education & Curriculum, port 7772), Crypteolas (DeFi Protocol Analysis, port 7771), Browser (Web Automation Orchestration, port 7773), and Croilar (Personal Portfolio + Data Engineering, port 7774).

## Why This Matters for Kings' College Galway
AgentOS is the AI agent orchestration layer that powers autonomous workflows across the Celtic education platform. The Oideachais AgentOS handles curriculum extraction planning — coordinating Crawl4AI scrapes, LiteLLM inference calls, and Dagster pipeline triggers. The Browser AgentOS orchestrates web automation for scraping Irish education websites through Stagehand and Browserbase. The Crypteolas AgentOS manages DeFi analytics for the Túatha crypto education module with x402 micropayment verification. All four agents share a common secret key for cross-flow authentication, use Langfuse for trace-level observability, and communicate with each other through internal service URLs — forming a self-hosted, coordinated multi-agent architecture.

## Key Features
- Four domain-specific Agno AgentOS instances: Oideachais, Crypteolas, Browser, Croilar
- Cross-agent communication via internal HTTP URLs and shared secret key
- Langfuse observability on every agent with configurable debug mode
- x402 micropayment support for Crypteolas DeFi analytics
- SQLite-backed persistent storage per agent with configurable external DB URLs
- 2 CPU / 2GB per agent (1GB for Croilar stub)

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/agent-os
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/agent-os
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `OIDEACHAIS_PORT` | No | Host port for Oideachais AgentOS | `7772` |
| `CRYPTEOLAS_PORT` | No | Host port for Crypteolas AgentOS | `7771` |
| `BROWSER_PORT` | No | Host port for Browser AgentOS | `7773` |
| `CROILAR_PORT` | No | Host port for Croilar AgentOS | `7774` |
| `OPENAI_API_KEY` | No | OpenAI API key | — |
| `ANTHROPIC_API_KEY` | No | Anthropic API key | — |
| `AGNO_DEFAULT_MODEL` | No | Default Agno model | `gpt-4o` |
| `AGNO_CLAUDE_MODEL` | No | Claude model | `claude-sonnet-4-20250514` |
| `AGENT_OS_SECRET_KEY` | Yes | Shared A2A secret | — |
| `OIDEACHAIS_DB_URL` | No | Oideachais DB URL | `sqlite:///./storage/oideachais.db` |
| `CRYPTEOLAS_DB_URL` | No | Crypteolas DB URL | `sqlite:///./storage/crypteolas.db` |
| `BROWSER_DB_URL` | No | Browser DB URL | `sqlite:///./storage/browser.db` |
| `CROILAR_DB_URL` | No | Croilar DB URL | `sqlite:///./storage/croilar.db` |
| `X402_ENABLED` | No | Enable x402 micropayments | `true` |
| `X402_PAY_TO_ADDRESS` | No | x402 payment address | — |
| `X402_NETWORK` | No | x402 network | `base` |
| `BROWSERBASE_API_KEY` | No | Browserbase API key | — |
| `BROWSERBASE_PROJECT_ID` | No | Browserbase project ID | — |
| `LANGFUSE_PUBLIC_KEY` | No | Langfuse public key | — |
| `LANGFUSE_SECRET_KEY` | No | Langfuse secret key | — |
| `LANGFUSE_HOST` | No | Langfuse host | `https://langfuse.cianfhoghlaim.ie` |
| `AGNO_DEBUG` | No | Enable Agno debug mode | `false` |

## Access
- **URLs**: `https://agents.oideachais.cianfhoghlaim.ie`, `https://agents.crypteolas.cianfhoghlaim.ie`, `https://agents.browser.cianfhoghlaim.ie`, `https://agents.croilar.cianfhoghlaim.ie`
- **Internal ports**: 7777 per agent (mapped to host ports 7771-7774)
- **Auth**: Shared secret key (`AGENT_OS_SECRET_KEY`) + Pangolin Member role

## Health Check
```bash
docker ps --filter name=agentos --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/agno-agi/agno
- **Documentation**: https://docs.agno.com
- **Latest release**: Built from source via local Dockerfiles; tracks Agno framework releases.
