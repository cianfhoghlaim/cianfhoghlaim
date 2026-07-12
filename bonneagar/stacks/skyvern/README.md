# Skyvern — AI-Powered Browser Automation

## Overview

Skyvern is an open-source AI agent that automates browser-based workflows using computer vision and LLM reasoning. Unlike traditional web scrapers that rely on fixed CSS selectors, Skyvern "sees" the page — it can navigate websites, fill forms, click buttons, and extract data by understanding the visual layout and content. Supports complex multi-step workflows like form submissions, login flows, and data extraction from JavaScript-heavy SPAs.

## Why This Matters for Kings' College Galway

The curriculum extraction pipeline's most fragile step is web scraping. Government education websites (NCCA, SEC, Department of Education) have inconsistent HTML structures, JavaScript-rendered content, and authentication gating that break traditional scrapers. Skyvern provides a computer-vision approach — it sees the page like a human, finds the "Download Exam Paper" button by visual recognition rather than CSS selector, and handles multi-step navigation (login → search → filter by year → download). This reduces the maintenance burden on the DLT sources and makes the pipeline resilient to website redesigns.

## Key Features

- **Computer vision navigation** — Finds elements by visual appearance, not CSS selectors
- **LLM reasoning** — Understands page content and decides next actions
- **Multi-step workflows** — Handles login, search, pagination, form submission
- **Self-healing** — Adapts to website changes without code updates
- **Structured extraction** — Extracts data as JSON using LLM understanding

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/skyvern
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Requires API keys for the LLM gateway (LiteLLM) for vision processing. Locket resolves credentials from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `SKYVERN_PORT` | No | API port | `8000` |
| `LLM_API_KEY` | Yes | LiteLLM gateway API key | — |
| `LLM_ENDPOINT` | Yes | LiteLLM gateway URL | `http://litellm:4000/v1` |
| `BROWSERBASE_API_KEY` | No | Browserbase API key for cloud browser | — |

## Access

- **API**: `http://localhost:8000`
- **Web UI**: `https://skyvern.cianfhoghlaim.ie` (private, Admin role)
- **Auth**: API key (machine); Pocket ID SSO (human)

## Upstream

- **Repository**: <https://github.com/Skyvern-AI/skyvern>
- **Documentation**: <https://docs.skyvern.com>
- **Latest**: Active development (2025) — vision model improvements, multi-step workflow builder, Browserbase integration, self-healing navigation

## Screenshot

Skyvern's web UI provides a workflow builder where users define multi-step browser automations. The dashboard shows past workflow runs with screenshots at each step, extracted data in JSON format, and error logs. The live view shows the browser in action as Skyvern navigates, clicks, and extracts — useful for debugging when a workflow fails on a particular website.
