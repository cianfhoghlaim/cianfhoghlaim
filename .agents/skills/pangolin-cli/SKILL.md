---
name: pangolin-cli
description: Install + operate the Pangolin CLI for machine-client tunneling, the OpenCode/codex/claude-code wire-up, and the systemd/launchd service-install pattern. Use when the user asks to "tunnel to cianfhoghlaim.ie", "set up the Pangolin CLI", "run pangolin up", "configure opencode for the Pangolin gateway", or any task involving the Fosrl Pangolin CLI binary. Complements the macOS `Pangolin.app` WireGuard client (which is GUI-only); the CLI is what machines + daemons + bun scripts use.
---

# Pangolin CLI

**Version**: v0.17.0 (2026-09-25) | **Upstream**: https://github.com/fosrl/cli
**Companion apps**: Pangolin.app (macOS GUI VPN client), Pangolin Dashboard (web UI at `https://pangolin.cianfhoghlaim.ie`)

The Pangolin CLI is the canonical machine-client way to connect a host or container
to a Pangolin network. It implements the same WireGuard-based tunnel as Pangolin.app
but runs in a terminal, ships as a static binary, and supports service-install for
launchd/systemd.

## 1. Install

```bash
# Auto-detect architecture + install to /usr/local/bin (requires sudo)
curl -fsSL https://static.pangolin.net/get-cli.sh | bash

# Or download a specific version manually
# See https://github.com/fosrl/cli/releases
```

## 2. Authenticate

```bash
# Interactive (browser-based) — opens Pangolin Cloud / your self-hosted UI
pangolin login

# Non-interactive (for machines + CI) — use the client ID + secret from the UI
# Settings → Machine Clients → Create
pangolin up \
  --id <client_id> \
  --secret <client_secret> \
  --endpoint https://pangolin.cianfhoghlaim.ie \
  --attach
```

## 3. The 3 canonical commands

| Command | What it does | When to use |
|:--|:--|:--|
| `pangolin login` | Browser-based user auth (stores JWT in `~/.config/pangolin/`) | Operator on their own machine |
| `pangolin up` | Starts the WireGuard tunnel + registers with the control plane | Every session |
| `pangolin configure <client>` | Writes provider entries for a coding agent | First-time agent setup |
| `pangolin service install` | Installs as launchd (macOS) or systemd (Linux) service | Production / always-on host |
| `pangolin service status` | Checks the service health | Post-deploy verify |

### `pangolin configure opencode`

Writes the right entries into `opencode.json` + `~/.local/share/opencode/auth.json`
so opencode points at a Pangolin AI Gateway resource. Example:

```bash
pangolin configure opencode --resource ai.cianfhoghlaim.ie
```

The `--resource` flag accepts either a `niceId` or a full FQDN. With no flag, the
CLI prompts for org + resource + provider IDs (defaults to `anthropic,openai`).

The CLI writes these entries into the **user-global** `opencode.json`
(`~/.config/opencode/opencode.json`), not the repo-local one. To make the repo's
checked-in `opencode.json` match, mirror the entries by hand or commit a diff after
running the CLI.

## 4. Machine-client + service-install pattern

The bunchloch MacBook needs a long-running machine client so the bunchloch services
(litellm, marimo, cianfhoghlaim-cognee, unsloth-serve, etc.) are always reachable
from `*.cianfhoghlaim.ie`.

```bash
# 1. Mint a machine client at the Pangolin UI
#    https://pangolin.cianfhoghlaim.ie → Sites → bunchloch → Clients → Create
#    Copy the ID + secret.

# 2. Install as a launchd service (macOS)
sudo pangolin service install client \
  --id <machine_client_id> \
  --secret <machine_client_secret> \
  --endpoint https://pangolin.cianfhoghlaim.ie

# 3. Verify
sudo pangolin service status client
sudo pangolin service logs client
```

## 5. Docker / Kubernetes deployment

Per https://docs.pangolin.net/manage/clients/install-client, the CLI also runs
inside Docker as a sidecar (with `network_mode: host` + `cap_add: NET_ADMIN` +
`devices: /dev/net/tun:/dev/net/tun`). For Kubernetes, see the same page for
the sidecar pattern.

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|:--|:--|:--|
| `failed to create tun interface` | Missing NET_ADMIN cap | Run as root OR use the sidecar pattern |
| `endpoint unreachable` | Self-signed cert OR expired Pangolin EE licence | Re-check `PANGOLIN_LICENCE` + the Traefik ACME cert on arm1-oci |
| `tunnel up but DNS does not resolve *.cianfhoghlaim.ie` | Split-horizon DNS not pushed to the Pangolin client | Verify in the Pangolin UI: Sites → bunchloch → DNS Records |
| `401 Unauthorized from API` | Stale `PANGOLIN_API_KEY` | Mint a new one at UI → Settings → API Keys |

## 7. When to use this skill

Activate when the user asks about:
- "set up Pangolin CLI"
- "tunnel to *.cianfhoghlaim.ie"
- "wire opencode / claude-code / codex to the AI Gateway"
- "set up the launchd / systemd service for the machine client"
- "connect bunchloch services to the Pangolin control plane"
- "deploy Pangolin CLI as a Docker sidecar / Kubernetes sidecar"

## Reference

- Upstream docs: https://docs.pangolin.net/manage/clients/install-client
- GitHub releases: https://github.com/fosrl/cli/releases
- Companion skill: `pangolin-ai-gateway` (for the AI Gateway config that this CLI
  writes provider entries for).
