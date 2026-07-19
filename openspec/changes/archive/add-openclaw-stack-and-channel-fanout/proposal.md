# Change: add-openclaw-stack-and-channel-fanout

## Why

The Cianfhoghlaim platform reaches the user through one of three
surfaces today:

1. **TanStack Start web apps** at `oideachais.cianfhoghlaim.ie`,
   `croilar.cianfhoghlaim.ie`, `tuatha.cianfhoghlaim.ie` — full
   web apps that need a browser and an authenticated Pocket ID
   session.
2. **AgentOS** long-running agent runtimes (`agent-os` stack,
   ports 7771–7774) — operator dashboards, not user-facing.
3. **Pangolin private mesh** — operator-only infra surface.

None of these reach a user on **a phone, a chat window, or a
messaging app**. The user has to come to the platform; the
platform never reaches the user.

This change adds an **outbound channel-fanout gateway** that
**the platform reaches the user with**, using the upstream
[`openclaw/openclaw`](https://github.com/openclaw/openclaw)
gateway:

- A single long-running gateway process on `arm1-oci` exposes
  the **Celtic-Tutor agent** (and the other 11 agents in the
  meaisínfhoghlaim fleet) through 8 channels: WhatsApp,
  Telegram, Slack, Discord, Signal, iMessage, Matrix, and
  Microsoft Teams.
- Plus a built-in **WebChat** surface at
  `openclaw.cianfhoghlaim.ie` — a low-friction chat UI that
  any visitor can pair into, no Pocket ID account required.
- Plus an **MS Teams bridge** on gateway port 3978 (kept
  internal, not exposed via Pangolin).

The gateway uses **`dmPolicy: "pairing"`** by default — first
contact from any new sender returns a 6-character pairing code;
the operator approves it via the gateway's admin API; subsequent
messages from that sender go straight to the agent fleet. This
is the upstream-recommended default for personal-instance
deployments and is **the auth model this change adopts**.

## What Changes

### 1. New Docker Compose stack `infrastructure/stacks/openclaw/`

The stack runs a single `openclaw` container (the upstream
image, pinned to a semver) plus a `locket` sidecar for
Infisical secret injection. Networking: shared
`cianfhoghlaim` bridge so the gateway can reach internal
services (e.g. the LiteLLM gateway at `:4000`, once the
`litellm-minimax-vendor-derisking` change lands).

- `compose.yaml` — single service, named volumes for state +
  skills-curated mount.
- `sidecar.yaml` — canonical Locket shape: `user: 65532:65532`,
  `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`,
  `read_only: true`, tmpfs `stack-secrets` with `mode=0700`,
  `LOCKET_MODE=watch`.
- `secrets.env` — 9 `infisical://dev-baile/openclaw/<key>`
  references: gateway auth token, OpenCode-Go API key, minimax
  API key, 4 channel tokens (Telegram bot token, Slack bot
  token, Discord bot token, WhatsApp access token), and the
  OTLP/HTTP endpoint for Langfuse traces.
- `pangolin.yaml` — Traefik routing for
  `openclaw.cianfhoghlaim.ie → openclaw:18789` (gateway
  WebSocket RPC). The 18790 bridge port and 3978 Teams port
  are bound to `127.0.0.1` only, not exposed via Pangolin.
- `blueprint.yaml` — Pangolin resource definitions matching
  the 6-label shape (name, mode, full-domain, destination-port,
  protocol, roles).
- `.env.example` — non-secret defaults: port, log level,
  `OPENCLAW_DM_POLICY=pairing`.

### 2. Curated skills subset

The upstream openclaw `workspace/skills/` directory is
mounted read-only from
`infrastructure/stacks/openclaw/skills-curated/`, which is a
sibling symlink directory pointing at 10 hand-picked skills
out of the 108 in `.agents/skills/`:

| Skill | Why |
|:--|:--|
| `dagster` | Gateway surfaces Dagster asset status to chat |
| `dlt` | Ingestion from chat-triggered DLT pipelines |
| `oideachais-baml-schemas` | BAML extraction invoked from chat |
| `ccc` | Code search from chat (the gateway's primary dev tool) |
| `browser-tools` | Browser automation from chat (Stagehand / Firecrawl) |
| `litellm` | LLM gateway debug from chat |
| `langfuse` | Trace lookup from chat |
| `cognee` | Memory recall from chat |
| `cocoindex` | Embedding new chat content into LanceDB (the cognify step) |
| `agent-fleet-orchestration` | The 12-agent fleet reference |

The remaining 98 skills are **not** exposed; they are
agent-runtime internals (CI, secrets-management, infra-stacks,
etc.) that have no business being callable from a chat surface.

### 3. `openclaw.json` config

`infrastructure/stacks/openclaw/config/openclaw.json` ships
the gateway with:

```json
{
  "provider": "opencode-go",
  "model": "minimax-m3",
  "fallback_chain": ["minimax-coding-plan/minimax-m3"],
  "dm_policy": "pairing",
  "channels": {
    "telegram":  {"enabled": true, "token_env": "TELEGRAM_BOT_TOKEN"},
    "slack":     {"enabled": true, "token_env": "SLACK_BOT_TOKEN"},
    "discord":   {"enabled": true, "token_env": "DISCORD_BOT_TOKEN"},
    "whatsapp":  {"enabled": true, "token_env": "WHATSAPP_ACCESS_TOKEN"},
    "webchat":   {"enabled": true, "bind": "0.0.0.0:18789"},
    "teams":     {"enabled": true, "bind": "127.0.0.1:3978"}
  },
  "allow_from": [],
  "otel": {
    "endpoint_env": "OTEL_EXPORTER_OTLP_ENDPOINT",
    "service_name": "openclaw-gateway"
  }
}
```

- **Provider** is `opencode-go` (the OpenCode Go gateway,
  `https://opencode.ai/zen/go/v1`) with the single
  `OPENCODE_GO_API_KEY` env var. The
  `litellm-minimax-vendor-derisking` change adds 3-key
  rotation *inside LiteLLM*; this change uses the simpler
  single-key path because (a) the gateway does not have to
  pay the LiteLLM proxy round-trip latency and (b) the user
  picked "OpenCode Go single-key (simpler)" in the build
  decision.
- **Fallback chain** is `minimax-coding-plan/minimax-m3` —
  the upstream minimax subscription path, used only if the
  primary provider errors out.
- **`dm_policy: "pairing"`** — the default pairing model.
  The `allow_from` list is empty in v1; the operator
  populates it as senders pair in.
- **6 channels enabled** (Telegram, Slack, Discord,
  WhatsApp, WebChat, Teams). Signal, iMessage, and Matrix
  are scaffolded in the config but `enabled: false` in v1
  (each requires additional infrastructure — Signal needs
  `signal-cli`, iMessage needs BlueBubbles on macOS, Matrix
  needs a homeserver).

### 4. Komodo stack + deploy procedure

- `infrastructure/komodo/stacks/openclaw-arm1-oci.toml` —
  `[[stack]]` block referencing the 6-file compose set, with
  tags `host:arm1-oci`, `tier:control-plane`,
  `type:agent-runtime`, `domain:openclaw.cianfhoghlaim.ie`.
- `infrastructure/komodo/procedures/deploy-openclaw-arm1-oci.toml`
  — 5-stage deploy (prereqs → langfuse + locket volume →
  openclaw stack → pangolin routes → health checks via
  `curl https://openclaw.cianfhoghlaim.ie/api/health`).

### 5. Stack inventory + AGENTS.md

- `infrastructure/AGENTS.md` gets **+1 row** in the Stack
  Inventory table (`openclaw/`).

### 6. OpenSpec change artifacts

- This `proposal.md` + `tasks.md` +
  `specs/infrastructure-stacks/spec.md` +
  `specs/meaisinfhoghlaim-agent-frameworks/spec.md`.

## Impact

- **Affected specs:**
  - MODIFIED `infrastructure-stacks` — the new stack plus
    the channel-fanout gateway contract (port, auth model,
    skills-curated mount, `dm_policy` default).
  - MODIFIED `meaisinfhoghlaim-agent-frameworks` — the
    openclaw gateway as the **channel-fanout entry-point**
    to the 12-agent fleet (Celtic Tutor reachable from
    WhatsApp, Telegram, Slack, Discord, Signal, iMessage,
    Matrix, Teams, WebChat).
- **NEW files:**
  - `infrastructure/stacks/openclaw/{compose.yaml, sidecar.yaml, secrets.env, pangolin.yaml, blueprint.yaml, .env.example, README.md}`
  - `infrastructure/stacks/openclaw/config/openclaw.json`
  - `infrastructure/stacks/openclaw/skills-curated/{10 symlinks}`
  - `infrastructure/komodo/stacks/openclaw-arm1-oci.toml`
  - `infrastructure/komodo/procedures/deploy-openclaw-arm1-oci.toml`
  - `openspec/changes/add-openclaw-stack-and-channel-fanout/{proposal.md, tasks.md, specs/infrastructure-stacks/spec.md, specs/meaisinfhoghlaim-agent-frameworks/spec.md}`
- **MODIFIED files:**
  - `infrastructure/AGENTS.md` — +1 row in Stack Inventory
  - `.infisical.env` — +9 vault references
- **Affected agent skills:**
  - `.agents/skills/infrastructure-stacks/SKILL.md` —
    1-line addition in the "11 inventory categories" section
    for the openclaw stack (channel-fanout gateway).
  - `.agents/skills/agent-fleet-orchestration/SKILL.md` —
    new section "The OpenClaw channel-fanout gateway (the
    inbound surface)" documenting the openclaw → 12-agent-fleet
    routing, channel defaults, 3-layer auth, LLM provider chain,
    and Langfuse trace contract. (Note: there is **no**
    `.agents/skills/meaisinfhoghlaim-agent-frameworks/SKILL.md`
    on disk — `agent-fleet-orchestration` is the canonical
    skill for the 12-agent meaisínfhoghlaim fleet. The openspec
    capability `meaisinfhoghlaim-agent-frameworks` is unchanged.)
- **Affected CI:** `bun run validate-stacks` (stack-doctor
  4-gate check) — the new stack must pass all 4 gates
  before commit.
- **Affected workflows:** `komodo run procedure
  deploy-openclaw-arm1-oci` registers a new 5-stage deploy
  procedure in Komodo.

## Non-Goals

- This change does **not** provision Signal / iMessage /
  Matrix. Those 3 channels are `enabled: false` in v1
  pending additional infrastructure (`signal-cli`,
  BlueBubbles, homeserver).
- This change does **not** add a new LLM provider. The
  gateway uses the existing `OPENCODE_GO_API_KEY` and the
  existing `minimax-coding-plan` subscription.
- This change does **not** use LiteLLM as the primary path
  (user picked "OpenCode Go single-key"); LiteLLM remains
  the routing option for the `litellm-minimax-vendor-derisking`
  change.
- This change does **not** expose gateway ports 18790
  (bridge) or 3978 (Teams) via Pangolin. Those stay on
  `127.0.0.1`; Teams uses the dedicated Azure Bot Framework
  outbound webhook model.
- This change does **not** add a public-domain route.
  `openclaw.cianfhoghlaim.ie` is private (Pocket ID SSO via
  TinyAuth).
- This change does **not** introduce a new shared tmps
  volume; the openclaw Locket uses the canonical
  `stack-secrets` pattern.
- This change does **not** wire the gateway into the
  `oideachais-agent-services` change's ADK / Agno services.
  The gateway reaches the 12-agent fleet through the existing
  Letta / LiteLLM / BAML layers, not through the ADK compose
  service.
- This change does **not** rewrite the openclaw upstream
  Dockerfile; the stack uses the upstream-built
  `ghcr.io/openclaw/openclaw:<semver>` image with a pinned
  SHA256 digest.

## Risk Assessment

- **Risk: arm1-oci resource ceiling.** A long-running
  Node 24 + Bun daemon consumes ~256 MB idle, up to ~1 GB
  under load. arm1-oci (Oracle Cloud ARM free tier) is
  already at 70% utilization per the 2026-06 audit. **Mitigation:**
  task 1.0 in `tasks.md` re-runs
  `infrastructure/audit/scripts/inventory-arm1-oci.sh`
  pre-deploy; if utilization exceeds 80%, deploy is
  aborted and the user is alerted to migrate to `bunchloch`
  instead.
- **Risk: openclaw upstream is moving fast.** The semver
  pin reduces accidental breakage but also blocks security
  patches. **Mitigation:** documented renovate workflow
  (the `croilar-renovate-pr.toml` procedure) covers
  `ghcr.io/openclaw/openclaw` monthly.
- **Risk: dmPolicy="pairing" is operator-burden.** If
  the operator forgets to approve a pairing request, the
  sender is locked out. **Mitigation:** the openclaw admin
  UI exposes the pending-pairing queue; the deploy
  procedure's last stage surfaces a
  `curl /api/pairing/pending` count in the deploy log.
- **Risk: the curated skills subset is curated.** A
  user-requested skill (e.g. `motherduck`) might not be
  reachable from chat. **Mitigation:** the
  `skills-curated/` dir is a sibling symlink directory,
  not a copy — adding a skill is one symlink + a service
  restart.
- **Risk: WebChat at 18789 has no built-in auth.** Anyone
  reaching the Pangolin private resource can pair into the
  gateway. **Mitigation:** 3-layer auth (Pangolin TinyAuth
  → Pocket ID OIDC → openclaw pairing) is enforced in
  `pangolin.yaml`.

## Validation

1. `docker compose -f infrastructure/stacks/openclaw/compose.yaml config`
   parses successfully.
2. `docker compose -f infrastructure/stacks/openclaw/compose.yaml -f infrastructure/stacks/openclaw/sidecar.yaml config`
   parses successfully and shows `locket` as `service_healthy`
   dependency.
3. `infrastructure/stacks/openclaw/pangolin.yaml` matches the
   6-label shape (`name`, `mode`, `full-domain`,
   `destination-port`, `protocol`, `roles`).
4. `bun run validate-stacks` (a.k.a. `stack-doctor`) passes
   all 4 gates with the openclaw stack present.
5. `openspec validate add-openclaw-stack-and-channel-fanout --strict`
   passes — every `### Requirement:` has at least one
   `#### Scenario:`.
6. `mise run lint:skills` — the 2 skill SKILL.md updates
   pass the 4 metadata rules; total still 108/108.
7. (post-deploy) `curl -fsS https://openclaw.cianfhoghlaim.ie/api/health`
   returns HTTP 200 within 30 s of `komodo run procedure
   deploy-openclaw-arm1-oci`.