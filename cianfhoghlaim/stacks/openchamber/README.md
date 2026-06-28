# OpenChamber — OpenCode Web/Desktop UI

## Overview

OpenChamber is a browser-based OpenCode UI built on Bun + React.
It bundles the `opencode-ai` runtime inside its own container, so
there is no need to run a separate OpenCode daemon. The UI ships
with 18+ themes, persistent session state, and a provider picker
for OpenAI, Anthropic, and minimax-compatible gateways.

The upstream `openchamber/openchamber` image is built on
`oven/bun:1.3.5` and is MIT-licensed. The stack pins it to a
semver + SHA256 digest and updates monthly via the renovate
workflow.

## Why This Matters for Kings' College Galway

OpenCode is the canonical local AI coding agent used across the
Cianfhoghlaim monorepo. Until now the user ran it from the
terminal (`bunx opencode-ai`) with no web UI, no multi-device
sync, no session history, no theme support.

OpenChamber gives the user a **dedicated, persistent,
browser-based OpenCode UI** that they can reach from any device
on the Pangolin mesh — a single pane of glass for code-agent
work, with all sessions persisted across browser restarts.

## Runtime Model: Bundled Mode (v1)

The OpenChamber container bundles its own `opencode-ai` runtime
inside the image. **No `OPENCODE_HOST` env var is set** — the
UI talks to the in-container runtime.

**External OpenCode mode** (future enhancement): if you want to
point at a separately-running OpenCode daemon instead, uncomment
the `OPENCODE_HOST` line in `.env.example` and set it to the
daemon's URL. This is documented in `.env.example` but is NOT
the default. Switching modes does not require a new openspec
proposal.

## No Cloudflare Tunnel in v1

OpenChamber supports a `cloudflared`-based tunnel for public
access without a Pangolin route. This stack **leaves the
`OPENCHAMBER_TUNNEL_TOKEN` blank**; Pangolin handles the
routing via TinyAuth + Pocket ID OIDC.

**Cloudflare tunnel mode** (future enhancement): uncomment
`OPENCHAMBER_TUNNEL_TOKEN` in `.env.example` and set the token
from your Cloudflare Zero Trust dashboard. Documented in
`.env.example` but is NOT the default.

## Key Features

- **Bundled OpenCode runtime** — no separate daemon required
- **18+ themes** — including the canonical `cianchoghlaim-dark`
- **Persistent session state** — `openchamber-state` named volume
- **3 LLM providers** — OpenAI, Anthropic, minimax-compatible
- **Pocket ID OIDC SSO** — primary auth at the Pangolin layer
- **UI password** — 2nd-factor auth inside the bundled UI
- **1 GB memory / 1 CPU limit** (sized for arm1-oci)

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/openchamber
docker compose --env-file ../../.env.local up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/openchamber
docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on `arm1-oci`. Komodo syncs
from the Forgejo repository and applies `compose.yaml` +
`sidecar.yaml` + `pangolin.yaml` + `blueprint.yaml`.

```bash
km run procedure deploy-openchamber-arm1-oci
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `OPENCHAMBER_UI_PASSWORD` | yes (prod) | 2nd-factor UI password (random 32 chars) | from Locket/Infisical |
| `OPENAI_API_KEY` | no | OpenAI provider key (any missing key disables that provider) | from Locket/Infisical |
| `ANTHROPIC_API_KEY` | no | Anthropic provider key | from Locket/Infisical |
| `MINIMAX_API_KEY` | yes (prod) | minimax-compatible provider key (default in v1) | from Locket/Infisical |
| `OPENCHAMBER_PORT` | no | UI port | `3000` |
| `OPENCHAMBER_THEME` | no | Default theme | `cianchoghlaim-dark` |
| `OPENCHAMBER_LOG_LEVEL` | no | Log level (debug/info/warn/error) | `info` |
| `OPENCODE_HOST` | no | External OpenCode daemon URL (external mode only) | not set (bundled mode) |
| `OPENCHAMBER_TUNNEL_TOKEN` | no | Cloudflare tunnel token (tunnel mode only) | not set (Pangolin handles routing) |
| `PANGOLIN_DOMAIN` | no | Public hostname | `openchamber.cianfhoghlaim.ie` |

## Access

- **URL**: `https://openchamber.cianfhoghlaim.ie` (private,
  Pangolin Member role required, then OpenChamber UI password)
- **Internal port**: 3000 (bound to `127.0.0.1`; Pangolin
  handles public routing)
- **Auth**: Pocket ID OIDC (primary) + OPENCHAMBER_UI_PASSWORD
  (2nd factor)

## Health Check

```bash
docker ps --filter name=openchamber --format "table {{.Names}}\t{{.Status}}"
curl -fsS https://openchamber.cianfhoghlaim.ie/api/health
```

## Upstream

- **Repository**: https://github.com/openchamber/openchamber
- **License**: MIT
- **Image**: `ghcr.io/openchamber/openchamber:<semver>@sha256:<digest>`
- **Base image**: `oven/bun:1.3.5@sha256:<digest>`
- **Bundled runtime**: `opencode-ai` (semver pinned in the
  upstream image)
- **Default port**: 3000