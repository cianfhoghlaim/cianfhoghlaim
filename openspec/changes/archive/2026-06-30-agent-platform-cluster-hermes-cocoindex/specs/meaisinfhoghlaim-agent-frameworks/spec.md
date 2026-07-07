# `meaisinfhoghlaim-agent-frameworks` capability spec — hermes delta

The meaisínfhoghlaim agent-frameworks capability spec governs the
12-agent fleet (root + 11 specialists), the OpenCode agent
registry in `opencode.json`, and the agent-platform group of
`bonneagar/stacks/` (the 7 stacks: Agno AgentOS, Google ADK,
OpenClaw, OpenChamber, Cognee, Graphiti, Letta).

This delta adds Hermes Agent
([NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent),
v0.17.0, MIT) as a 3rd vertex in the agent-platform group,
deployed on `bunchloch` (MacBook M4 Max, 32 GB headroom) and
exposed at `hermes.cianfhoghlaim.ie` as a private Pangolin
resource. The canonical LLM gateway is the existing `litellm`
stack (the new M3 chokepoint), not the upstream Hermes gateway.

## ADDED Requirements

### Requirement: Hermes is a 3rd vertex in the agent-platform group

The system SHALL deploy Hermes Agent v0.17.0 as a third vertex
in the `agent-platform` group at
`bonneagar/stacks/hermes/`, alongside the existing OpenClaw
(channel-fanout gateway) and OpenChamber (browser IDE)
vertices. Hermes SHALL route LLM calls through the canonical
`litellm` stack at `http://litellm:4000/v1` (the M3 chokepoint),
not through the upstream Hermes gateway or any direct-to-M3
path. Hermes SHALL be deployed on `bunchloch` (not `arm1-oci`)
because arm1-oci is at 70% utilization and the resource math
for Hermes (2 GB memory, 2 CPU) does not fit. Hermes SHALL be
exposed at `hermes.cianfhoghlaim.ie` as a private Pangolin
resource (Pocket ID SSO via TinyAuth, then the
`users.allowlist` allowlist in `config/hermes.yaml`, then
per-channel `allow_from` lists).

#### Scenario: Hermes is reachable at the private domain

- **GIVEN** the `deploy-agent-platform-cluster-bunchloch`
  Komodo procedure has run successfully
- **WHEN** a Pocket ID-authenticated operator navigates to
  `https://hermes.cianfhoghlaim.ie`
- **THEN** Pangolin TinyAuth SHALL pass the request to the
  Hermes dashboard at `http://hermes:9119`
- **AND** the `users.allowlist` check SHALL pass (the
  operator's Pocket ID subject is in the allowlist)
- **AND** the dashboard SHALL render the Hermes home page
  with the operator's subject visible in the top-right
  user menu

#### Scenario: Hermes is reachable at the public domain is denied

- **WHEN** an unauthenticated visitor navigates to
  `https://hermes.cianfhoghlaim.ie`
- **THEN** Pangolin TinyAuth SHALL redirect to the Pocket ID
  OIDC login page
- **AND** no part of the Hermes dashboard SHALL be exposed
  before Pocket ID SSO succeeds

#### Scenario: LiteLLM is the only LLM provider

- **GIVEN** `bonneagar/stacks/hermes/config/hermes.yaml`
- **WHEN** the file is read
- **THEN** the `provider.base_url` SHALL be
  `http://litellm:4000/v1`
- **AND** the `provider.name` SHALL be `litellm`
- **AND** the `fallback_chain` SHALL be empty (LiteLLM
  handles fallback internally to its 70+ model routing)
- **AND** the `OPENAI_BASE_URL` env var in
  `bonneagar/stacks/hermes/secrets.env` SHALL be
  `http://litellm:4000/v1`
- **AND** the `OPENAI_API_KEY` SHALL resolve at runtime to
  the `LITELLM_MASTER_KEY` Infisical value

### Requirement: Hermes uses 3-layer auth (TinyAuth → Pocket ID SSO → users.allowlist)

The system SHALL enforce 3-layer authentication on
`hermes.cianfhoghlaim.ie`:

1. **Pangolin TinyAuth** (Pocket ID OIDC SSO) at the Traefik
   layer — required to even reach the domain.
2. **`users.allowlist`** in `config/hermes.yaml` — a
   comma-separated list of Pocket ID subject IDs; an
   authenticated principal whose subject is not in the
   allowlist SHALL be rejected by Hermes's admin API even
   after TinyAuth passes.
3. **`channels.<name>.allow_from`** per channel — a
   comma-separated list of sender IDs (Telegram user ID,
   Discord user ID, etc.) allowed to invoke the agent on
   that channel. Empty by default.

The `users.allowlist` SHALL be populated from day one with
the operator's Pocket ID subject, sourced from the
`HERMES_OPERATOR_POCKET_ID_SUBJECT` env var (in turn sourced
from the `dev-baile/hermes/operator_pocket_id_subject`
Infisical value). The `init-allowlist.sh` one-shot init
container SHALL add the subject at deploy time.

#### Scenario: Pocket ID principal outside the allowlist is rejected

- **GIVEN** the operator's Pocket ID subject is
  `oidc-subject-abc-123`
- **AND** `users.allowlist` contains only `oidc-subject-abc-123`
- **WHEN** a different Pocket ID principal (e.g.
  `oidc-subject-def-456`) authenticates via Pocket ID and
  navigates to `https://hermes.cianfhoghlaim.ie/api/sessions`
- **THEN** Hermes SHALL return HTTP 403 with body
  `{"error": "subject not in users.allowlist"}`
- **AND** no sessions SHALL be enumerated

#### Scenario: Allowlist is populated from day one

- **GIVEN** `dev-baile/hermes/operator_pocket_id_subject` is
  set to `oidc-subject-abc-123`
- **WHEN** the `deploy-agent-platform-cluster-bunchloch`
  Komodo procedure runs to completion
- **THEN** the `init-allowlist.sh` step SHALL have run
  successfully
- **AND** `curl -X POST -H "Authorization: Bearer $HERMES_API_SERVER_KEY" https://hermes.cianfhoghlaim.ie/api/users/allowlist/test -d '{"subject":"oidc-subject-abc-123"}'`
  SHALL return `{"allowed": true}`

### Requirement: Hermes `network_mode` is NOT host

The system SHALL NOT use `network_mode: host` for the Hermes
container. The upstream Hermes `docker-compose.yml` uses
host networking; this delta rewrites the network model to
fit the 6-file GOLD_STANDARD pattern (shared `cianchoghlaim`
bridge network with explicit published ports):

- Dashboard: `127.0.0.1:9119:9119` (exposed to Pangolin)
- Telegram webhook: `127.0.0.1:8443:8443` (internal only)
- WhatsApp Cloud webhook: `127.0.0.1:8090:8090` (internal only)
- SMS webhook: `127.0.0.1:8080:8080` (internal only)
- WeCom / BlueBubbles: `127.0.0.1:8645:8645` (internal only)

The dashboard, once bound to `127.0.0.1:9119`, is reached by
Pangolin via the standard Traefik route. The webhook ports
stay on `127.0.0.1` because the upstream Telegram/WhatsApp/
etc. services dial in to the container, not the other way
around.

#### Scenario: compose.yaml uses explicit port publishes

- **GIVEN** `bonneagar/stacks/hermes/compose.yaml`
- **WHEN** the file is read
- **THEN** no `network_mode: host` line SHALL appear
- **AND** the `hermes` service SHALL declare the 5 port
  publishes above (9119 to Pangolin, 4 webhook ports to
  127.0.0.1 only)
- **AND** `networks: [cianchoghlaim]` SHALL be set

### Requirement: Hermes channels do not overlap OpenClaw

The system SHALL enable only 3 of Hermes's 6 v1 channels in
the `agent-platform` group, with no overlap to OpenClaw's
6 channels:

- Hermes enables: `telegram`, `discord`, `webchat`
- OpenClaw keeps: `telegram`, `slack`, `discord`, `whatsapp`,
  `webchat`, `ms-teams`

Hermes's `telegram` and `discord` channels are isolated from
OpenClaw's via separate bot tokens (different
`dev-baile/openclaw/telegram_bot_token` vs
`dev-baile/hermes/telegram_bot_token`). Operators explicitly
opt-in to overlap by enabling additional channels.

#### Scenario: Hermes and OpenClaw use separate Telegram bots

- **GIVEN** OpenClaw's `TELEGRAM_BOT_TOKEN` resolves to bot A
- **AND** Hermes's `TELEGRAM_BOT_TOKEN` resolves to bot B
- **WHEN** a user sends a message to bot A
- **THEN** OpenClaw SHALL handle the message (via its
  `dm_policy: pairing` model)
- **AND** Hermes SHALL NOT receive the message
- **WHEN** the same user sends a message to bot B
- **THEN** Hermes SHALL handle the message (via its
  `users.allowlist` + `channels.telegram.allow_from` model)
- **AND** OpenClaw SHALL NOT receive the message

## Cross-references

- [`.agents/skills/agent-fleet-orchestration/SKILL.md`](../../.agents/skills/agent-fleet-orchestration/SKILL.md)
- [`bonneagar/stacks/hermes/`](../../../bonneagar/stacks/hermes/)
- [`bonneagar/stacks/hermes/config/hermes.yaml`](../../../bonneagar/stacks/hermes/config/hermes.yaml)
- [`openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/proposal.md`](../proposal.md)
