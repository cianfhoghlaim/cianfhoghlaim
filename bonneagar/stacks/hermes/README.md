# Hermes — Autonomous Agent Runtime

> **STATUS 2026-08-23: NOT SERVING.** The container starts its supervisor tree
> and then exits with `Failed to initialize agent: No LLM provider configured`.
> It is deliberately **not** declared as a Pangolin private resource — pointing
> a resource at a dead destination produces exactly the silent failure that
> `pangolin-doctor` exists to catch. See [§ Current state](#current-state-2026-08-23).

## Current state (2026-08-23)

Four real defects were found and fixed; one remains.

**Fixed**

1. **Secrets were never injected.** The stack was being started from
   `compose.yaml` alone. `sidecar.yaml` is what mounts the Locket volume at
   `/run/secrets/locket`, so hermes came up with no configuration at all —
   which is why nothing listened and the logs were completely empty.
2. **`sidecar.yaml` could not be parsed.** It declared `environment:` twice in
   the `locket` service. Duplicate mapping keys are a YAML error, so
   `docker compose -f compose.yaml -f sidecar.yaml` failed outright — the
   overlay could never have been used. (17 files in this repo had this; all
   fixed.)
3. **Port collision.** The SMS webhook mapped host `8080`, which llama-swap
   already owns, so the container failed to start with "port is already
   allocated". Host side moved to `8647`.
4. **Placeholder credentials.** Infisical held the literal
   `sk-placeholder-replace-me` at `/hermes/openai_api_key`, and
   `/hermes/openai_base_url` pointed at `http://litellm:4000` (a network hermes
   is not on). Both replaced with the real LiteLLM master key and the
   `host.docker.internal` route.

With those fixed, hermes now *starts* its s6 services (`main-hermes`,
`dashboard`, `gateway-default`) — previously they never ran.

**Outstanding**

`config/config.yaml` was rewritten to the current schema and verified to load
correctly *standalone*:

```
model: 'custom:litellm:default'
custom view: [{'name': 'litellm', 'base_url': 'http://host.docker.internal:4000/v1',
               'key_env': 'OPENAI_API_KEY', 'model': 'default'}]
```

but the s6-supervised process inside the container still reports
`No LLM provider configured`. HERMES_HOME, the config path, the API key and the
base URL were all confirmed correct in the container. The remaining difference
is the environment of the s6 service itself.

**Next step:** run `hermes setup` interactively inside the container and diff
the config it writes against `config/config.yaml`. That is the fastest way to
settle the last gap; the schema is large (`_config_version: 32`) and guessing
at it is not economical.

### Notes on the config schema

Three things the old `config/hermes.yaml` got wrong, worth knowing before
editing:

- `_config_version` must be present and current, or the file parses as v0 and
  is rejected wholesale.
- `model` is a **string** (`"provider:model"`), not a mapping.
- `openai:` means OpenAI *the vendor*. An OpenAI-**compatible** endpoint such
  as LiteLLM is a `custom:` provider declared under `custom_providers:`. Using
  a bare `openai:` falls through to the OpenRouter default URL with no key,
  which surfaces as the misleading "No LLM provider configured".
- There is no `HERMES_CONFIG` env var. Hermes reads `$HERMES_HOME/config.yaml`.

## Overview

Hermes is a long-running autonomous agent runtime that
complements OpenClaw (channel-fanout gateway) and OpenChamber
(browser IDE) as the 3rd vertex in the `agent-platform` group.
It runs the upstream
[`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent)
v0.17.0 (MIT, Python 81.9%, 206k stars on GitHub).

Hermes adds three capabilities that OpenClaw and OpenChamber
don't have:

- **Built-in learning loop** — Hermes gets more capable the
  longer it runs, with persistent memory + skills.
- **MCP-native** — built-in MCP **client** (consumes the 10
  canonical Cianfhoghlaim MCP servers + the new `hermes-mcp` server
  that exposes Hermes-as-MCP-server, upstream issue #342).
- **Autonomous cron / scheduling** — runs scheduled jobs
  without operator intervention.

The upstream `docker-compose.yml` uses `network_mode: host`.
This rewrite fits the 6-file GOLD_STANDARD pattern with
explicit published ports on the `cianfhoghlaim` bridge
network. The upstream 206k-star count is a popularity signal
(treat with appropriate skepticism per the
`hermes-agent-research-2026-06-30` audit), but the MIT
license + 13,746 commits in the main branch are stronger
evidence of activity.

## Why This Matters for Kings' College Galway

The agent-platform group now has 3 complementary surfaces:

| Surface | Stack | Strength |
|:--|:--|:--|
| Channel fanout (Telegram, Slack, Discord, WhatsApp, WebChat, Teams) | OpenClaw | reach (8 channels, WebChat pair-in) |
| Browser IDE (devs) | OpenChamber | OpenCode UI (Bun + React, 18+ themes) |
| Autonomous long-running runtime | **Hermes** | learning loop + MCP-native + cron |

The 3 vertices share the same `litellm` LLM chokepoint (M3
plan) and the same Langfuse observability destination. An
operator can pick the right surface for the right task without
managing 3 different LLM provider chains.

## 3-Layer Auth

1. **Pangolin TinyAuth** (Pocket ID OIDC) at the Traefik
   layer — required to even reach `hermes.cianfhoghlaim.ie`.
2. **`users.allowlist`** in `config/hermes.yaml` —
   populated from day one with the operator's Pocket ID
   subject (sourced from `HERMES_OPERATOR_POCKET_ID_SUBJECT`
   env var). The `init-allowlist.sh` one-shot init container
   adds the subject via the admin API at deploy time.
3. **`channels.<name>.allow_from`** per channel — populated
   as senders pair in (the same model OpenClaw uses).

The default is the most restrictive combination: TinyAuth
required, allowlist required, `allow_from` empty. Operators
loosen individual layers as trust grows.

## Key Features

- **3 v1 channels** (Telegram, Discord, WebChat) — no overlap
  with OpenClaw's 6 channels
- **MCP-native** — consumes the 10 Cianfhoghlaim MCP servers + the
  new `hermes-mcp` server
- **LiteLLM chokepoint** — the M3 plan is reached
  exclusively through `http://litellm:4000/v1`
- **Langfuse OTLP/HTTP export** — every chat session + every
  tool call lands in Langfuse as a trace
- **2 GB memory / 2 CPU limit** (sized for `bunchloch`)
- **Day-one allowlist population** — `init-allowlist.sh` is
  a 1-shot init container that adds the operator's
  Pocket ID subject at deploy time

## Deployment

### Docker Compose (Local Development)
```bash
cd bonneagar/stacks/hermes
docker compose --env-file ../../.env.local up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd bonneagar/stacks/hermes
docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on `bunchloch` (MacBook M4
Max, 32 GB headroom). Komodo syncs from the Forgejo
repository and applies `compose.yaml` + `sidecar.yaml` +
`pangolin.yaml` + `blueprint.yaml`.

```bash
km run procedure deploy-agent-platform-cluster-bunchloch
```

The omnibus procedure brings up the 8-stack cluster in
dependency order (lakehouse → litellm + langfuse + mlflow +
logfire → cognee + graphiti + lancedb → openclaw + openchamber
+ hermes), then runs the health checks.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `HERMES_API_SERVER_KEY` | yes (prod) | Admin API token | from Locket/Infisical |
| `OPENAI_API_KEY` | yes (prod) | `LITELLM_MASTER_KEY` (re-keyed at Infisical) | from Locket/Infisical |
| `OPENAI_BASE_URL` | yes (prod) | LiteLLM gateway URL | `http://litellm:4000/v1` |
| `LANGFUSE_PUBLIC_KEY` | yes (prod) | Langfuse public key | from Locket/Infisical |
| `LANGFUSE_SECRET_KEY` | yes (prod) | Langfuse secret key | from Locket/Infisical |
| `LANGFUSE_BASE_URL` | yes (prod) | Langfuse base URL | `https://langfuse.cianfhoghlaim.ie` |
| `TELEGRAM_BOT_TOKEN` | no | Telegram bot token (separate from OpenClaw's) | from Locket/Infisical |
| `DISCORD_BOT_TOKEN` | no | Discord bot token (separate from OpenClaw's) | from Locket/Infisical |
| `HERMES_OPERATOR_POCKET_ID_SUBJECT` | yes (prod) | Operator's Pocket ID subject for day-one allowlist | from Locket/Infisical |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | yes (prod) | Langfuse OTLP/HTTP endpoint | from Locket/Infisical |
| `HERMES_PORT` | no | Dashboard port | `9119` |
| `HERMES_MCP_PORT` | no | Hermes-as-MCP-server port | `9120` |
| `HERMES_LOG_LEVEL` | no | Log level | `info` |
| `PANGOLIN_DOMAIN` | no | Public hostname | `hermes.cianfhoghlaim.ie` |

## Access

- **Dashboard URL**: `https://hermes.cianfhoghlaim.ie`
  (private, Pangolin Member role required, then
  `users.allowlist` check, then dashboard access).
- **Hermes-as-MCP-server** (preview): `http://hermes:9120/mcp`
  (internal, requires `Authorization: Bearer $HERMES_API_SERVER_KEY`).
- **Webhook ports** (Telegram 8443, WhatsApp 8090, SMS 8080,
  WeCom 8645): bound to `127.0.0.1` only; upstream services
  dial in.

## Health Check

```bash
docker ps --filter name=hermes --format "table {{.Names}}\t{{.Status}}"
curl -fsS https://hermes.cianfhoghlaim.ie/api/health
curl -fsS -H "Authorization: Bearer $HERMES_API_SERVER_KEY" \
  -X POST https://hermes.cianfhoghlaim.ie/api/users/allowlist/test \
  -d "{\"subject\":\"$HERMES_OPERATOR_POCKET_ID_SUBJECT\"}"
# Expected: {"allowed": true}
```

## Network Model: Non-Host Rewrite

The upstream `NousResearch/hermes-agent` `docker-compose.yml`
uses `network_mode: host`. The Cianfhoghlaim GOLD_STANDARD
pattern requires the shared `cianfhoghlaim` bridge network
with explicit published ports. The rewrite:

- **Dashboard:** `127.0.0.1:9119:9119` (exposed to Pangolin
  via the `hermes-dashboard` Traefik route).
- **Hermes-as-MCP-server:** `127.0.0.1:9120:9120` (internal
  only; no Pangolin route).
- **Webhook ports:** `127.0.0.1:8443/8090/8080/8645` (internal
  only; upstream services dial in).

If you see webhook timeouts, check that Pocket ID returned a
fresh OIDC session (the upstream hermes-cli requires OIDC
session refresh every 30 min for webhook auth).

## LLM Provider: LiteLLM-Only

The M3 plan is reached **exclusively** through
`http://litellm:4000/v1`. The upstream Hermes gateway is NOT
used. The previous `opencode-go` + `minimax-coding-plan`
fallback chain (used by OpenClaw) is removed entirely per
the omnibus change. LiteLLM handles fallback internally to
its 70+ model routing.

## Upstream

- **Repository**: https://github.com/NousResearch/hermes-agent
- **License**: MIT
- **Image**: `ghcr.io/nousresearch/hermes-agent:0.17.0@sha256:<digest>`
- **Runtime**: Python 3.11 (uv-managed) + Node 24
- **Default ports**: 9119 (dashboard), 9120 (MCP server),
  8443 (Telegram webhook), 8090 (WhatsApp Cloud), 8080 (SMS),
  8645 (WeCom / BlueBubbles)
- **Migration path** (NOT used in v1):
  [hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw](https://hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw)
  — for a future change that retires OpenClaw.
