# OpenClaw — Channel-Fanout Gateway

## Overview

OpenClaw is a long-running gateway process that exposes the
**meaisínfhoghlaim 12-agent fleet** (Celtic Tutor, Mythology
Narrator, Quest Guide, Research Assistant, and 8 others) through
8 messaging channels:

| Channel | v1 status | Notes |
|:--|:--|:--|
| **WebChat** | enabled | Browser chat at `openclaw.cianfhoghlaim.ie` (Pangolin-routed) |
| **Telegram** | enabled | BotFather token from Infisical |
| **Slack** | enabled | Bot OAuth token from Infisical |
| **Discord** | enabled | Bot token from Infisical |
| **WhatsApp** | enabled | Business API access token from Infisical |
| **MS Teams** | enabled | Azure Bot Framework outbound webhook; bridge port 3978 bound to `127.0.0.1` only |
| Signal | scaffolded (`enabled: false`) | Requires `signal-cli` — not provisioned in v1 |
| iMessage | scaffolded (`enabled: false`) | Requires BlueBubbles on macOS — not provisioned in v1 |
| Matrix | scaffolded (`enabled: false`) | Requires a Matrix homeserver — not provisioned in v1 |

The upstream `openclaw/openclaw` image is built on Node 24 + Bun
1.3.13 and is MIT-licensed. The stack pins it to a semver +
SHA256 digest and updates monthly via the renovate workflow.

## Why This Matters for Kings' College Galway

Until now the platform only reached the user through the
TanStack Start web apps (`oideachais.cianfhoghlaim.ie`,
`croilar.cianfhoghlaim.ie`, `tuatha.cianfhoghlaim.ie`). The
openclaw gateway flips the model: **the platform reaches the
user** through whatever chat surface they already use.

For the Leaving Cert Irish oral-exam practice flow, a student
can now practice in WhatsApp instead of opening a web app. For
the crypteolas DeFi analytics, a researcher gets Slack pings
instead of needing to remember a URL. For the daily Celtic
language micro-lesson, a Telegram bot checks in with the
learner each morning.

## 3-Layer Auth

The gateway is intentionally opinionated about who can reach the
agent fleet:

1. **Pangolin TinyAuth** (Pocket ID OIDC) at the Traefik layer —
   required to even reach `openclaw.cianfhoghlaim.ie`.
2. **`dmPolicy: "pairing"`** at the gateway layer — first
   contact from any new sender returns a 6-character pairing
   code; an operator approves it via `POST /api/pairing/approve`.
3. **`allow_from` allowlist** per channel — once a sender is
   paired they can be added to the allowlist to bypass pairing
   for future sessions.

The default is the most restrictive combination: TinyAuth
required, pairing required, `allow_from` empty. Operators
loosen individual layers as trust grows.

## Key Features

- **6 v1 channels** (Telegram, Slack, Discord, WhatsApp,
  WebChat, Teams) + 3 scaffolded (Signal, iMessage, Matrix)
- **Curated skills subset** of 10 (out of 129) mounted
  read-only into the workspace
- **OpenCode Go gateway** as the primary LLM path with
  `minimax-coding-plan` as fallback
- **Langfuse OTLP/HTTP** export — every chat session lands
  in Langfuse as a trace
- **2 GB memory / 2 CPU limit** (sized for arm1-oci)
- **`dmPolicy: pairing`** is the upstream-recommended default
  for personal instances

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/openclaw
docker compose --env-file ../../.env.local up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/openclaw
docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on `arm1-oci`. Komodo syncs
from the Forgejo repository and applies `compose.yaml` +
`sidecar.yaml` + `pangolin.yaml` + `blueprint.yaml`.

```bash
km run procedure deploy-openclaw-arm1-oci
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `OPENCLAW_GATEWAY_TOKEN` | yes (prod) | Admin API token for the gateway | from Locket/Infisical |
| `OPENCODE_GO_API_KEY` | yes (prod) | OpenCode Go gateway API key (single primary) | from Locket/Infisical |
| `MINIMAX_API_KEY` | yes (prod) | minimax-coding-plan fallback key | from Locket/Infisical |
| `TELEGRAM_BOT_TOKEN` | no | Telegram BotFather token | from Locket/Infisical |
| `SLACK_BOT_TOKEN` | no | Slack bot OAuth token | from Locket/Infisical |
| `DISCORD_BOT_TOKEN` | no | Discord bot token | from Locket/Infisical |
| `WHATSAPP_ACCESS_TOKEN` | no | WhatsApp Business API token | from Locket/Infisical |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | yes (prod) | Langfuse OTLP/HTTP endpoint | `https://langfuse.cianfhoghlaim.ie/api/public/otel` |
| `OPENCLAW_PORT` | no | Gateway WebSocket RPC port | `18789` |
| `OPENCLAW_BRIDGE_PORT` | no | Gateway bridge port | `18790` |
| `OPENCLAW_LOG_LEVEL` | no | Log level (debug/info/warn/error) | `info` |
| `OPENCLAW_DM_POLICY` | no | Pairing model (`pairing`/`open`/`allowlist`) | `pairing` |
| `OPENCLAW_ALLOW_FROM` | no | Comma-separated allowlist (empty = all must pair) | empty |
| `PANGOLIN_DOMAIN` | no | Public hostname | `openclaw.cianfhoghlaim.ie` |

## Access

- **WebChat URL**: `https://openclaw.cianfhoghlaim.ie`
  (private, Pangolin Member role required, then openclaw pairing)
- **Telegram / Slack / Discord / WhatsApp**: bot starts up at
  container start; pairings accumulate in `/api/pairing/pending`
- **MS Teams**: bridge port 3978 is bound to `127.0.0.1` only;
  configure the Azure Bot Framework endpoint to call the
  container's `3978` port over the Docker network

## Health Check

```bash
docker ps --filter name=openclaw --format "table {{.Names}}\t{{.Status}}"
curl -fsS https://openclaw.cianfhoghlaim.ie/api/health
curl -fsS http://openclaw:18789/api/pairing/pending
```

## Pairing a New Sender (Operator Workflow)

```bash
# 1. User sends "hello" to the Telegram bot
# 2. Gateway returns a 6-character code, e.g. "K7M2PX"
# 3. Operator approves:
curl -X POST \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN" \
  -d '{"channel":"telegram","sender_id":"123456789","code":"K7M2PX"}' \
  https://openclaw.cianfhoghlaim.ie/api/pairing/approve
# 4. The sender is now in allow_from for the telegram channel
# 5. Subsequent messages route to the default_agent (Celtic Tutor)
```

## Upstream

- **Repository**: https://github.com/openclaw/openclaw
- **License**: MIT
- **Image**: `ghcr.io/openclaw/openclaw:<semver>@sha256:<digest>`
- **Runtime**: Node 24 + Bun 1.3.13
- **Default ports**: 18789 (WebSocket RPC), 18790 (bridge),
  3978 (MS Teams bridge)