# Crawl4AI

## Overview
Crawl4AI is an LLM-friendly web crawler and scraper designed for AI data pipelines. Created by unclecode, it provides a REST API at port 11235 with full browser rendering (Chromium), LLM-powered extraction strategies, and configurable provider support for OpenAI, Anthropic, DeepSeek, Mistral, and others. The stack runs as a single container with Gunicorn serving the API.

## Why This Matters for Kings' College Galway
Crawl4AI is the primary ingestion engine for Celtic education content from public websites — scraping Irish curriculum specifications from `curriculumonline.ie`, Leaving Cert exam papers from `examinations.ie`, and bilingual Irish/English educational resources. The LLM-powered extraction strategies parse unstructured HTML into structured educational content with language detection and topic classification. In production, it routes through Gluetun's VPN tunnel for geo-resilient scraping and feeds directly into the DevDocs pipeline and the Dagster-orchestrated data platform.

## Key Features
- REST API with `/health`, `/crawl`, and `/crawl_stream` endpoints on port 11235
- LLM-powered extraction strategies (OpenAI, Anthropic, DeepSeek, Groq, Together, Mistral, Gemini)
- Full Chromium browser rendering with shared `/dev/shm` for performance
- 4GB memory allocation with configurable GPU support
- Configurable via `.llm.env` for API keys

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/crawl4ai
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/crawl4ai
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `OPENAI_API_KEY` | No | OpenAI API key | — |
| `DEEPSEEK_API_KEY` | No | DeepSeek API key | — |
| `ANTHROPIC_API_KEY` | No | Anthropic Claude API key | — |
| `GROQ_API_KEY` | No | Groq API key | — |
| `TOGETHER_API_KEY` | No | Together AI API key | — |
| `MISTRAL_API_KEY` | No | Mistral API key | — |
| `GEMINI_API_TOKEN` | No | Google Gemini API token | — |
| `LLM_PROVIDER` | No | Override default extraction provider | — |
| `IMAGE` | No | Docker image override | `unclecode/crawl4ai:latest` |
| `TAG` | No | Image tag override | `latest` |
| `INSTALL_TYPE` | No | Build install type | `default` |
| `ENABLE_GPU` | No | Enable GPU support at build time | `false` |

## Access
- **URL**: `https://crawl4ai.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 11235
- **Auth**: No built-in auth — protected by Pangolin/TinyAuth upstream

## Health Check
```bash
docker ps --filter name=crawl4ai --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/unclecode/crawl4ai
- **Documentation**: https://crawl4ai.com
- **Latest release**: Pulls `unclecode/crawl4ai:latest` — a continuously updated LLM-friendly web crawler with multi-provider extraction support.
