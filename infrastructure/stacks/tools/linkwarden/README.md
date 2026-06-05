# Linkwarden — Collaborative Bookmark Manager

## Overview

Linkwarden is an open-source, self-hosted collaborative bookmark manager. It provides a web UI for saving, organising, archiving, and sharing web bookmarks across a team. Features include automatic page archiving (saving a snapshot of the page content), full-text search via Meilisearch, and team-based sharing with access controls.

## Why This Matters for Kings' College Galway

Curriculum research generates a vast collection of web resources that need to be organised and preserved — syllabus pages that change annually, exam paper archives, academic papers behind paywalls, Irish-language teaching resources on government websites, and Celtic studies reference materials. Linkwarden archives snapshots of every saved page, ensuring resources remain accessible even if the original website changes or goes offline. The Meilisearch-powered full-text search means finding "that 2018 chief examiner report on Higher Level Applied Maths" is instant across thousands of saved bookmarks.

## Key Features

- **Page archiving** — Save full-page snapshots (HTML, screenshots, PDF) for offline access
- **Meilisearch** — Instant full-text search across all bookmarks and archived content
- **Team sharing** — Share collections with team members and guests
- **Tagging and folders** — Organise bookmarks with hierarchical tags
- **Browser extension** — One-click save from Chrome/Firefox

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tools/linkwarden
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Requires PostgreSQL and Meilisearch (co-located). Locket resolves `POSTGRES_PASSWORD` from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password | — |
| `NEXTAUTH_SECRET` | Yes | NextAuth encryption secret | — |
| `DATABASE_URL` | No | PostgreSQL connection string | `postgresql://postgres:<pw>@postgres:5432/postgres` |

## Access

- **Web UI**: `https://linkwarden.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Email/password + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/linkwarden/linkwarden>
- **Documentation**: <https://docs.linkwarden.app>
- **Latest**: v2.x (2025) — Meilisearch v1.12 integration, improved page archiving, team sharing, browser extension update

## Screenshot

Linkwarden's web UI shows a grid of saved bookmarks with thumbnail previews, tags, and archive status indicators. The search bar provides instant full-text results. Collections can be shared with team members. Individual bookmark view shows the archived page snapshot, extracted text, tags, and sharing options.
