# IT Tools — Developer Utility Collection

## Overview

IT Tools is a collection of handy online utilities for developers and IT professionals. It provides a single-page web app with dozens of tools: JSON formatters, base64 encoders, UUID generators, JWT decoders, hash generators, regex testers, SQL formatters, and many more. Built with Vue.js and runs as a static site.

## Why This Matters for Kings' College Galway

Working across 5 programming languages (Python, TypeScript, BAML, Rust, TOML) and 89 Docker Compose stacks means constant need for quick data transformations: decoding a JWT token from the Pocket ID OIDC flow, formatting a SQL query for DuckDB, generating a UUID for a new Dagster asset, checking a hash for a HuggingFace model download. IT Tools provides all of these in a single private web tool accessible from any browser, with no data leaving the infrastructure — the tools run entirely client-side in the browser.

## Key Features

- **JSON tools** — Format, validate, diff, convert to/from YAML/XML/CSV
- **Crypto tools** — Hash generators (MD5, SHA, Bcrypt), UUID generators, JWT decoder
- **Text tools** — Regex tester, base64 encode/decode, case converter, diff checker
- **SQL tools** — SQL formatter, query prettifier
- **Offline-first** — All tools run client-side; no data sent to any server

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/it-tools
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. No database or secrets required — the entire application is a static web page.

## Environment Variables

None required. IT Tools runs as a self-contained static site on port 80 within the container.

## Access

- **Web UI**: `https://it-tools.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/CorentinTh/it-tools>
- **Documentation**: <https://it-tools.tech>
- **Latest**: Active development (2025) — new tools added regularly, Vue 3 rewrite, PWA support, dark mode

## Screenshot

IT Tools presents a sidebar with categorised tool icons and a main panel showing the selected tool. The JSON formatter shows a split view with raw input on the left and formatted output on the right. The JWT decoder shows the decoded header, payload, and signature with syntax highlighting. Each tool is self-contained with its own input/output interface.
