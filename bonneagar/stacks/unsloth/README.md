# Unsloth — Pangolin Traefik Routing Stack

This is a **Pangolin-only** stack directory (no Docker compose, no deployment). Unsloth Studio runs directly on the bunchloch host (MacBook M4 Max) at `127.0.0.1:8888`; this directory only exists to wire the Pangolin Traefik routing rules.

## Per-stack files

- **`pangolin.yaml`** — Traefik HTTP routers + services that route `unsloth.cianfhoghlaim.ie` and `unsloth-api.cianfhoghlaim.ie` to the host's Unsloth Studio via the Newt WireGuard tunnel.
- **`blueprint.yaml`** — Generated from `pangolin.yaml` for use with the Pangolin Blueprint API (alternative to manual config).

## URLs

| Public (via Pangolin) | Internal (Docker → host) |
|:--|:--|
| `https://unsloth.cianfhoghlaim.ie` | `http://host.docker.internal:8888` |
| `https://unsloth-api.cianfhoghlaim.ie/v1/...` | `http://host.docker.internal:8888/v1/...` |

## How it works

1. **External user** → `https://unsloth-api.cianfhoghlaim.ie/v1/chat/completions`
2. **Pangolin (arm1-oci)** → TLS termination + Pocket ID SSO at the edge
3. **Newt WireGuard tunnel** → routes the request over the secure tunnel to bunchloch
4. **Traefik on arm1-oci** → matches the Host header (`unsloth-api.cianfhoghlaim.ie`) + PathPrefix (`/v1`)
5. **Backend** → `http://bunchloch:8888` (the Unsloth Studio on the host)
6. **Unsloth Studio** → `/v1/chat/completions` → llama-server → response

For Docker containers on bunchloch, use `http://host.docker.internal:8888` directly (no Pangolin overhead).

## Sources

- `openspec/changes/2026-08-21-unsloth-v5-architecture-refinement-v1/` — the follow-up change
- `bonneagar/stacks/unsloth-serve/README.md` — the deleted container stack README (now superseded by this directory)