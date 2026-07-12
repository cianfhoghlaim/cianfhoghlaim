# SearXNG — Privacy-Respecting Metasearch Engine

## Overview

SearXNG is an open-source, self-hosted metasearch engine that aggregates results from multiple search engines without tracking users. It queries Google, Bing, DuckDuckGo, Wikipedia, and dozens of other engines in parallel, strips tracking parameters, and returns clean, privacy-respecting results. Built as a modern fork of SearX with a focus on maintainability and UX.

## Why This Matters for Kings' College Galway

Curriculum research requires broad web search across educational databases, government publications, and academic repositories — without the filter bubble and tracking of commercial search engines. SearXNG provides unbiased search results for curriculum content research, and its self-hosted nature means no search history ever leaves the infrastructure. The Redis cache ensures fast repeat queries, and the configurable engine list means we can add education-specific search engines (ERIC, JSTOR metadata, NCCA publications) as custom search backends.

## Key Features

- **80+ search engines** — Aggregates results from major and niche engines
- **No tracking** — No cookies, no user profiles, no search history logging
- **Redis cache** — Fast repeat queries with configurable TTL
- **Configurable engines** — Enable/disable specific search backends per instance
- **API-first** — JSON API for programmatic search integration

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/searxng
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Requires co-located Redis for caching.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `SEARXNG_SETTINGS_PATH` | No | Settings YAML path | `/etc/searxng/settings.yml` |
| `SEARXNG_UWSGI_SETTINGS_PATH` | No | uWSGI config path | `/etc/searxng/uwsgi.ini` |
| `SEARXNG_REDIS_URL` | No | Redis connection URL | `redis://redis:6379/0` |

## Access

- **Web UI**: `https://search.cianfhoghlaim.ie` (private, Member role)
- **API**: `http://localhost:8888/search?q=<query>&format=json`
- **Health**: `http://localhost:8888/healthz`
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/searxng/searxng>
- **Documentation**: <https://docs.searxng.org>
- **Latest**: Active development (2025) — new search engines, improved Redis caching, modernised UI, JSON API v2

## Screenshot

SearXNG's web UI resembles a clean Google-style search page with a search bar, category tabs (General, Images, News, Videos, Science, Files, Social Media), and results listed with title, URL, and snippet. The preferences panel lets users configure enabled engines, language, and theme.
