# Perplexica — AI-Powered Search Engine

## Overview

Perplexica is an open-source, AI-powered search engine that combines web search with LLM reasoning to provide cited, contextual answers. It searches the web using SearXNG as its backend, then uses an LLM to synthesise results into a coherent answer with citations. Think of it as a self-hosted Perplexity AI — same concept, but running entirely on your infrastructure with your choice of LLM.

## Why This Matters for Kings' College Galway

Curriculum research often involves answering complex questions that span multiple sources: "What are the key differences between the Irish Leaving Cert and UK A-Level mathematics curricula?" or "How has the teaching of statistics evolved in Irish secondary education since 2000?" Perplexica searches multiple sources, synthesises a coherent answer with citations, and connects to the local LLM gateway — meaning it can use the same DeepSeek V4 Pro or Gemini 2.5 Pro models that power the extraction pipeline. For a research-heavy education project, having a self-hosted research assistant that cites its sources is transformative for both speed and academic rigour.

## Key Features

- **AI-synthesised answers** — LLM generates coherent responses from search results
- **Source citations** — Every claim is linked to its source
- **SearXNG backend** — Uses the self-hosted metasearch engine for web search
- **Multiple focus modes** — Academic, web, news, YouTube, Reddit, and custom modes
- **Local LLM integration** — Connects to the LiteLLM gateway via OpenAI-compatible API

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tools/Perplexica
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Requires a running SearXNG instance and access to the LiteLLM gateway for LLM queries.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `SEARXNG_URL` | Yes | SearXNG API URL | `http://searxng:8080` |
| `OLLAMA_API_URL` | Yes | LLM API URL (LiteLLM gateway) | `http://litellm:4000/v1` |
| `PERPLEXICA_PORT` | No | Web UI port | `3000` |
| `OPENAI_API_KEY` | No | API key for LLM gateway | — |

## Access

- **Web UI**: `https://perplexica.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/ItzCrazyKns/Perplexica>
- **Latest**: Active development (2025) — focus modes, image search, improved citations, Ollama/OpenAI compatibility

## Screenshot

Perplexica's web UI resembles Perplexity AI: a search bar at the top with focus mode selector (Academic, Web, etc.), results displayed as a synthesised answer paragraph with numbered citations below, source links in the sidebar, and follow-up question suggestions. The answer includes inline citations that expand to show the source URL and excerpt on hover.
