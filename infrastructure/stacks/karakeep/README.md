# Karakeep — Self-Hosted Bookmark and Read-Later Service

## Overview

Karakeep is an open-source, self-hosted bookmark and read-later service (formerly Hoarder). It provides a web UI for saving, tagging, searching, and organising web bookmarks, with full-text search powered by Meilisearch and AI-powered automatic tagging. Supports browser extensions and mobile apps for one-click saving.

## Why This Matters for Kings' College Galway

Curriculum research involves collecting hundreds of web resources: NCCA syllabus pages, SEC exam archives, academic papers on education methodology, Irish-language teaching resources, and Celtic studies references. Karakeep provides a shared bookmark library where the team can save, tag (e.g., `#leaving-cert`, `#mathematics`, `#irish-medium`), and search research materials. The Meilisearch full-text index means finding "that paper about Irish-medium mathematics instruction" takes seconds rather than scrolling through browser bookmarks. The AI auto-tagging ensures consistent taxonomy even when different team members save resources.

## Key Features

- **Full-text search** — Meilisearch-powered instant search across all bookmarks
- **AI auto-tagging** — Automatic tag suggestions using LLM integration
- **Browser extension** — One-click save from Chrome/Firefox
- **Archive snapshots** — Save page content for offline reading
- **List sharing** — Share curated reading lists with the team

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/karakeep
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Requires PostgreSQL and Meilisearch (both co-located in the compose stack). Locket resolves `KARAKEEP_DB_PASSWORD` and `KARAKEEP_MEILISEARCH_KEY` from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `KARAKEEP_DB_PASSWORD` | Yes | PostgreSQL password | — |
| `KARAKEEP_MEILISEARCH_KEY` | Yes | Meilisearch master key | — |
| `DATABASE_URL` | No | PostgreSQL connection string | `postgresql://karakeep:<pw>@karakeep-pg/karakeep` |
| `MEILISEARCH_URL` | No | Meilisearch URL | `http://karakeep-meilisearch:7700` |

## Access

- **Web UI**: `https://karakeep.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Email/password + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/greentechinnovate/karakeep>
- **Latest**: Active development — rebranded from Hoarder, AI tagging improvements, Meilisearch integration, mobile app

## Screenshot

Karakeep's web UI shows a Pinterest-style grid of saved bookmarks with thumbnail previews, tags, and reading status. The search bar provides instant full-text results. The sidebar shows tag categories, reading lists, and archive status. Individual bookmark view shows saved page content, extracted text, and AI-suggested tags.
