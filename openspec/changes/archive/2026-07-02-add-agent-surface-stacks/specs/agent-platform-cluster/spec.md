# Agent Platform Cluster Capability

> **New capability spec** created by the
> `2026-07-02-add-agent-surface-stacks` change. This spec
> was first sketched in the
> `2026-06-30-agent-platform-cluster-hermes-cocoindex`
> proposal (which described the LiteLLM chokepoint +
> Hermes as the 3rd vertex + CocoIndex agent discovery
> v1 Apps) but was never formalised as a top-level spec
> until this change. The author-of-truth for the
> original design intent is the 2026-06-30 change
> proposal.

## Purpose

The `agent-platform-cluster` capability describes the 3
agent runtime surfaces deployed on `bunchloch` (the
workload host) and the 3 supporting runtime services
(`litellm` + `langfuse` + `mlflow` + `cognee` + `graphiti`
+ `logfire` + `lancedb` + `lakehouse` + `dagster`). All
agent runtime surfaces route their LLM traffic through
the canonical `litellm` gateway at
`http://litellm:4000/v1` (the M3 chokepoint). All
runtime traces flow to `langfuse` at
`http://localhost:3001/api/public`.

The 3 agent surfaces are:

- **hermes** (NousResearch/hermes-agent v0.17.0) — the
  autonomous long-running agent runtime
- **openclaw** (ghcr.io/openclaw/openclaw) — the
  channel-fanout gateway (Telegram + Slack + Discord +
  WhatsApp + WebChat + MS Teams; Signal/iMessage/Matrix
  scaffolded but disabled)
- **openchamber** (ghcr.io/openchamber/openchamber) —
  the OpenCode web/desktop UI with bundled
  `opencode-ai` runtime

## ADDED Requirements

### Requirement: 3-vertex agent surface bundle

The system SHALL deploy the 3 agent runtime surfaces
(`hermes` + `openclaw` + `openchamber`) on `bunchloch`
(the workload host) as Wave 4 of the cold-boot sequence,
after the data + observability + dashboard layers are
healthy.

Each surface SHALL be brought up via
`./scripts/stack.sh <name> up -d` (the dev-mode direct
CLI). All 3 stacks SHALL be GOLD_STANDARD-compliant (all
6 files present: `compose.yaml` + `secrets.env` +
`sidecar.yaml` + `blueprint.yaml` + `README.md` +
`.env.example`).

#### Scenario: 3-vertex bundle ready
- **WHEN** an agent runs `./scripts/stack.sh hermes up -d`
  + `./scripts/stack.sh openclaw up -d` +
  `./scripts/stack.sh openchamber up -d` after the
  prior 3 changes' stacks are healthy
- **THEN** all 3 containers SHALL start with their
  pinned images (per
  `infrastructure-stacks` §"Image Pinning Policy
  applied to agent surfaces")
- **AND** the 3 dashboards SHALL be reachable:
  - hermes dashboard at `http://localhost:9119/`
  - openclaw WebSocket RPC at `ws://localhost:18789/`
  - openchamber UI at `http://localhost:3000/`
- **AND** all 3 healthcheck endpoints SHALL respond
  with HTTP 200

### Requirement: LiteLLM chokepoint contract

The system SHALL route every LLM call from the 3 agent
surfaces through the canonical `litellm` gateway at
`http://litellm:4000/v1`. None of the 3 surfaces SHALL
bring their own LLM provider keys; the LLM
authentication SHALL be the litellm master key injected
by Locket from `secrets.env`.

The 3 surfaces SHALL declare their `OPENAI_BASE_URL` env
var as `http://litellm:4000/v1` (or the Infisical-
resolved equivalent, per the per-stack `secrets.env`).

#### Scenario: openclaw routes LLM through litellm
- **WHEN** an inbound message arrives on any of
  openclaw's 6 enabled channels (Telegram + Slack +
  Discord + WhatsApp + WebChat + MS Teams)
- **THEN** openclaw SHALL issue an OpenAI-compatible
  chat completion request to
  `http://litellm:4000/v1/chat/completions` (NOT
  directly to `api.openai.com` or any other provider)
- **AND** the litellm access log SHALL record a
  `model=<minimax-m3>` (or equivalent) entry for the
  request

#### Scenario: hermes routes LLM through litellm
- **WHEN** a hermes session is initiated via the
  dashboard API or any of hermes's enabled channels
  (Telegram + Discord per `hermes/secrets.env` lines
  31-32)
- **THEN** hermes SHALL issue an OpenAI-compatible
  chat completion request to
  `http://litellm:4000/v1/chat/completions` (the
  `OPENAI_BASE_URL: http://litellm:4000/v1` is
  hardcoded in `hermes/compose.yaml` line 68; the
  equivalent value is also Infisical-resolved in
  `hermes/secrets.env` line 23)
- **AND** the hermes session SHALL appear in langfuse
  as a new trace with `service.name=hermes-agent`

#### Scenario: openchamber routes LLM through litellm
- **WHEN** the operator submits a prompt via the
  openchamber UI at `http://localhost:3000/`
- **THEN** the bundled opencode-ai runtime SHALL
  issue an OpenAI-compatible chat completion
  request to `http://litellm:4000/v1/chat/completions`
  (per `openchamber/secrets.env` line 18)
- **AND** the request SHALL appear in langfuse as a
  new trace with `service.name=openchamber`

### Requirement: 3-layer auth model

The system SHALL enforce the canonical 3-layer auth model
on the 3 agent surfaces:

1. **Layer 1 (Pangolin TinyAuth + Pocket ID OIDC)** at
   the Traefik layer (declarative via
   `pangolin.yaml`; activated only when Pangolin is
   running on `arm1-oci`)
2. **Layer 2 (per-stack `users.allowlist`)** at the
   application layer:
   - `hermes`: `config/hermes.yaml` `users.allowlist`
     populated from `HERMES_OPERATOR_POCKET_ID_SUBJECT`
     at deploy time (per `init-allowlist.sh`)
   - `openclaw`: `config/openclaw.json` `allowFrom`
     per-channel allowlist
   - `openchamber`: `OPENCHAMBER_UI_PASSWORD` from
     `secrets.env` (2nd-factor inside the bundled
     OpenCode UI)
3. **Layer 3 (per-channel sender allowlist)** at the
   routing layer (e.g. hermes
   `channels.<name>.allow_from`, openclaw
   `channels.<name>.allowFrom`)

#### Scenario: hermes 3-layer auth populated
- **WHEN** an agent brings up the hermes stack
- **THEN** the `init-allowlist.sh` script SHALL run
  during container startup
- **AND** the script SHALL read
  `HERMES_OPERATOR_POCKET_ID_SUBJECT` from
  `secrets.env` and write the subject to
  `hermes-state/users.json`
- **AND** the hermes service SHALL refuse any
  session-init request from a Pocket ID subject not
  in `users.json` (verified by sending a request
  with a synthetic subject and confirming the 403
  response)

#### Scenario: openclaw 3-layer auth
- **WHEN** an agent brings up the openclaw stack
- **THEN** the openclaw `config/openclaw.json`
  `allowFrom` array SHALL be populated per channel
  (each channel's `allowFrom` is a per-channel
  allowlist of Pocket ID subjects)
- **AND** the openclaw service SHALL refuse any
  inbound message from a sender not in the
  channel's `allowFrom` (verified by sending a
  test message from a non-allowlisted sender and
  confirming the 403 response)

#### Scenario: openchamber 3-layer auth
- **WHEN** an agent brings up the openchamber stack
- **THEN** the bundled openchamber UI SHALL require
  the `OPENCHAMBER_UI_PASSWORD` (resolved at runtime
  from `secrets.env`) for any login attempt
- **AND** the opencode-ai runtime SHALL refuse any
  chat completion request without a valid session
  cookie (verified by sending an unauthenticated
  POST and confirming the 401 response)

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the umbrella spec; 3-tier host convergence model;
  Image Pinning Policy; Locket Sidecar Contract
- [`agent-observability`](../agent-observability/spec.md) —
  the LLM Observability Tri-Split (langfuse + mlflow +
  logfire) that the 3 agent surfaces feed into
- [`agent-memory-systems`](../agent-memory-systems/spec.md) —
  the cognee + graphiti + falkordb + lancedb memory
  backends that the 3 agent surfaces can read from
- [`agentic-frontend-frameworks`](../agentic-frontend-frameworks/spec.md) —
  the web/UI framework that openchamber fits into
- [`openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/`](../../changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/proposal.md) —
  the original proposal that motivated this spec
  (LiteLLM chokepoint + Hermes as 3rd vertex + CocoIndex
  agent discovery v1 Apps)