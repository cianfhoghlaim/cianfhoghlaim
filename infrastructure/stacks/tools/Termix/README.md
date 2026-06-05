# Termix — Self-Hosted SSH and Terminal Manager

## Overview

Termix is a self-hosted web-based SSH client and terminal manager. It provides a browser-based terminal interface for connecting to remote servers via SSH, with support for multiple sessions, credential management, and session persistence. Built with Next.js and backed by PostgreSQL.

## Why This Matters for Kings' College Galway

The Cianfhoghlaim infrastructure spans three physical servers that require regular SSH access for maintenance, debugging, and deployment verification. Termix provides a browser-based SSH client accessible through Pangolin, meaning team members can access any server without installing an SSH client or managing SSH keys locally. Session persistence means long-running operations (model conversion, pipeline runs) continue even if the browser tab is closed. This is particularly useful for monitoring the 12+ hour HuggingFace → GGUF model conversions.

## Key Features

- **Browser-based SSH** — Full terminal emulation in the browser
- **Multi-server** — Connect to arm1-oci, cax41-hetzner, and bunchloch
- **Session persistence** — Reconnect to running sessions after browser close
- **Credential management** — Store server credentials securely in PostgreSQL
- **Web-based** — No SSH client installation needed

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tools/Termix
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Locket resolves `TERMIX_DB_PASSWORD` from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `TERMIX_DB_PASSWORD` | Yes | PostgreSQL password | — |
| `DATABASE_URL` | No | PostgreSQL connection string | `postgresql://termix:<pw>@termix-pg/termix` |

## Access

- **Web UI**: `https://termix.cianfhoghlaim.ie` (private, Admin role)
- **Auth**: Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/justinlawrence/termix>
- **Latest**: Active development — session persistence improvements, multi-tab terminal, credential vault integration

## Screenshot

Termix's web UI resembles VS Code's integrated terminal: a tabbed interface with multiple SSH sessions, a sidebar listing saved server connections, and a full terminal emulator supporting colours, ANSI escape codes, and clipboard integration.
