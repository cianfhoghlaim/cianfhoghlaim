# Infrastructure Stacks — Wave 4 Agent Surfaces Delta

> This file is the change-side delta for
> `2026-07-02-add-agent-surface-stacks`. It applies on top
> of the canonical `infrastructure-stacks` spec at
> `../../../../specs/infrastructure-stacks/spec.md` and on
> top of the prior `2026-07-02-bunchloch-stack-bootstrap`
> + `2026-07-02-add-lancedb-and-logfire-stacks` +
> `2026-07-02-add-marimo-stack` deltas.

## ADDED Requirements

### Requirement: Wave 4 agent surfaces bring-up

The system SHALL provide a procedure to bring up the 3
agent UI surface stacks (`hermes` + `openclaw` +
`openchamber`) in Wave 4, after all data + observability
+ dashboard stacks are healthy (per the prior 3 changes).

All 3 stacks SHALL be brought up via
`./scripts/stack.sh <name> up -d` (the dev-mode direct
CLI). No Locket, Infisical, or live secret round-trip
SHALL be required (each stack's `secrets.env` provides
sensible dev-mode defaults; Locket integration is a
separate follow-up change).

#### Scenario: openclaw Wave 4
- **WHEN** an agent runs `./scripts/stack.sh openclaw up -d`
  after Wave 2's `litellm` is healthy
- **THEN** the openclaw container SHALL start using the
  pinned image `ghcr.io/openclaw/openclaw:2026.2.6`
  (the latest published GHCR tag; the previous
  `1.0.0` reference did not exist)
- **AND** the WebSocket RPC SHALL listen on
  `127.0.0.1:18789` (verified by `curl :18789/api/health`)
- **AND** the gateway SHALL be ready to accept inbound
  channel traffic (Telegram + Slack + Discord + WhatsApp
  + WebChat + MS Teams) with the LLM chokepoint at
  `http://litellm:4000/v1` (configured in
  `secrets.env` line 34)

#### Scenario: openchamber Wave 4
- **WHEN** an agent runs `./scripts/stack.sh openchamber
  up -d` after Wave 2's `litellm` is healthy AND after
  the operator has authenticated to GHCR with
  openchamber credentials (the upstream image is
  private at GHCR)
- **THEN** the openchamber container SHALL start using
  the pinned image `ghcr.io/openchamber/openchamber:1.0.0`
- **AND** the UI SHALL be reachable at
  `127.0.0.1:3000/` (verified by `curl :3000/api/health`)
- **AND** the bundled opencode-ai runtime SHALL be
  wired to the litellm chokepoint via
  `OPENAI_BASE_URL=http://litellm:4000/v1` (configured
  in `secrets.env` line 18, Infisical-resolved at
  runtime; in dev mode the value MUST be hardcoded in
  the env)

#### Scenario: hermes Wave 4
- **WHEN** an agent runs `./scripts/stack.sh hermes up -d`
  after Wave 2's `litellm` is healthy AND after the
  operator has authenticated to GHCR with NousResearch
  credentials (the upstream image is private at GHCR)
- **THEN** the hermes container SHALL start using the
  pinned image `ghcr.io/nousresearch/hermes-agent:0.17.0`
  (per the `agent-platform-cluster` spec)
- **AND** the dashboard SHALL listen on
  `127.0.0.1:9119` (verified by `curl :9119/api/health`)
- **AND** the LLM provider SHALL be the litellm
  chokepoint (per the `agent-platform-cluster` spec)
  configured via `OPENAI_BASE_URL: http://litellm:4000/v1`
  in `compose.yaml` line 68
- **AND** the `init-allowlist.sh` script SHALL run
  during container startup and populate
  `hermes-state/users.json` with the operator's
  Pocket ID subject (from
  `HERMES_OPERATOR_POCKET_ID_SUBJECT`)

### Requirement: Image Pinning Policy applied to agent surfaces

The system SHALL pin the 3 agent surface images to their
resolved semver tags (no `:latest` AND no placeholder
`@sha256:0000...` digests). The `bun run validate-stacks`
Image Pinning Policy gate SHALL report zero `:latest`
WARNINGs and zero placeholder-digest WARNINGs for the 3
stacks.

The 3 pinned images are:

| Stack | Image | Resolved semver | Source verified |
|:--|:--|:--|:--|
| `hermes` | `ghcr.io/nousresearch/hermes-agent:0.17.0` | NousResearch release `0.17.0` per `agent-platform-cluster` spec; upstream image is **private** at GHCR (401 on HEAD) — requires operator credentials |
| `openclaw` | `ghcr.io/openclaw/openclaw:2026.2.6` | GHCR date-tagged `2026.2.6` (the previous `1.0.0` reference did not exist); upstream is publicly available (200 on HEAD) |
| `openchamber` | `ghcr.io/openchamber/openchamber:1.0.0` | Semver `1.0.0` per compose header; upstream image is **private** at GHCR (401 on HEAD) — requires operator credentials |

#### Scenario: All 3 stacks pinned + placeholder digests removed
- **WHEN** `bun run validate-stacks` runs against the 3
  agent surface stacks
- **THEN** the validator SHALL report zero `:latest`
  WARNINGs for hermes + openclaw + openchamber
- **AND** the validator SHALL report zero
  `@sha256:0000...` placeholder-digest WARNINGs for
  the 3 stacks
- **AND** the `image:` line in each compose.yaml SHALL
  end with a semver tag (no `:latest` AND no
  `@sha256:0000...` suffix)

#### Scenario: Full SHA256 digest pinning deferred to renovate cycle
- **WHEN** Renovate is configured to run on
  `bonneagar/stacks/`
- **THEN** the renovate cycle SHALL re-introduce the
  `@sha256:<digest>` suffix to each image line
  (replacing the bare semver tag) for true content-
  addressable immutability
- **AND** the digest SHALL be refreshed on every
  upstream image update