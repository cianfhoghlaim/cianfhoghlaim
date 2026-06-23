# Blinko — Self-Hosted Note-Taking and Knowledge Base

## Overview

Blinko is an open-source, self-hosted note-taking application with AI-powered features. It provides a clean web UI for writing, organising, and searching notes, with PostgreSQL-backed storage and NextAuth authentication. Designed as a lightweight alternative to Notion or Obsidian for self-hosted environments.

## Why This Matters for Kings' College Galway

Research notes, curriculum analysis observations, pipeline debugging logs, and meeting notes accumulate across the project. Blinko provides a shared knowledge base where team members can write, link, and search notes — creating a personal wiki for project knowledge. The PostgreSQL backend means notes are queryable and backupable alongside all other project databases, and NextAuth integration enables Pocket ID SSO for seamless access using existing passkey credentials.

## Key Features

- **Markdown notes** — Write in markdown with live preview
- **PostgreSQL-backed** — Reliable, backupable storage with full-text search
- **NextAuth** — Integrates with Pocket ID OIDC for SSO
- **AI-assisted** — Optional LLM integration for summarisation and search
- **Lightweight** — Next.js frontend with minimal resource footprint

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/blinko
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Locket resolves `NEXTAUTH_SECRET` and `DATABASE_URL` password from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `NODE_ENV` | No | Node environment | `production` |
| `NEXTAUTH_URL` | Yes | Public NextAuth URL | `https://blinko.cianfhoghlaim.ie` |
| `NEXTAUTH_SECRET` | Yes | NextAuth encryption secret | — |
| `DATABASE_URL` | Yes | PostgreSQL connection string | — |

## Access

- **Web UI**: `https://blinko.cianfhoghlaim.ie` (private, Member role)
- **Auth**: NextAuth with Pocket ID OIDC provider

## Upstream

- **Repository**: <https://github.com/blinko-space/blinko>
- **Latest**: Active development — AI note features, NextAuth improvements, PostgreSQL full-text search

## Screenshot

Blinko's web UI provides a sidebar with note folders and tags, a main editing panel with markdown input and live preview, and a search bar for full-text search across all notes. The interface is clean and minimal, similar to Bear or Simplenote.
