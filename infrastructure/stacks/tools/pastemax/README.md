# Pastemax — Self-Hosted Code Pastebin

## Overview

Pastemax is an open-source, self-hosted pastebin for code snippets and text. It provides syntax highlighting, expiration controls, and a clean sharing interface — a private alternative to services like Pastebin.com or GitHub Gists for teams that need internal code sharing.

## Why This Matters for Kings' College Galway

Debugging across 5 programming languages and 89 stacks often requires sharing code snippets, error logs, and configuration excerpts between team members. Pastemax provides a private pastebin where code can be shared internally without exposing it to public pastebin services. Syntax highlighting for Python, TypeScript, BAML, SQL, and YAML ensures code is readable. Expiration controls prevent stale snippets from accumulating.

## Key Features

- **Syntax highlighting** — Supports Python, TypeScript, SQL, YAML, JSON, BAML, and more
- **Expiration controls** — Set paste expiry (hours, days, weeks, or never)
- **Private sharing** — Share URLs internally via Pangolin
- **Lightweight** — Minimal container, no database required

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tools/pastemax
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci.

## Environment Variables

None required. Pastemax runs as a self-contained service with local file storage.

## Access

- **Web UI**: `https://paste.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/pastemax/pastemax>
- **Latest**: Active development — syntax highlighting library update, expiration improvements, API support

## Screenshot

Pastemax's web UI is minimal: a text area for entering code with a language selector dropdown, expiration settings, and a "Create Paste" button. The paste view shows the code with syntax highlighting, line numbers, and sharing options. The interface is deliberately simple — focused on the code, not the chrome.
