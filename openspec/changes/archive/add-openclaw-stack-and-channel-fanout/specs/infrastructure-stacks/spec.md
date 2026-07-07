# `infrastructure-stacks` capability spec — openclaw delta

The infrastructure-stacks capability spec governs the 94+ Docker
Compose stacks under `infrastructure/stacks/`, the 6-file
GOLD_STANDARD pattern, the Locket sidecar contract, and the
Pangolin Traefik routing shape.

This delta adds the openclaw channel-fanout gateway as a
first-class stack with the channel-fanout gateway contract.

## ADDED Requirements

### Requirement: openclaw Stack Directory
The system SHALL provide a Docker Compose stack at `infrastructure/stacks/openclaw/` that runs the upstream `openclaw/openclaw` channel-fanout gateway plus a Locket sidecar for Infisical secret injection.

#### Scenario: 6 GOLD_STANDARD files present
- **WHEN** a developer lists `infrastructure/stacks/openclaw/`
- **THEN** the directory SHALL contain all 6 GOLD_STANDARD files: `compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `.env.example`
- **AND** a `README.md` describing the stack
- **AND** a `config/openclaw.json` runtime config

#### Scenario: compose.yaml uses pinned image
- **WHEN** a developer reads `infrastructure/stacks/openclaw/compose.yaml`
- **THEN** the `image:` line SHALL be pinned to `<major>.<minor>.<patch>@sha256:<digest>` with no `:latest` tag
- **AND** the gateway state directory SHALL be set to `/home/node/.openclaw` (workaround for upstream issue #77436 host-path leak)
- **AND** the service SHALL declare `restart: unless-stopped` and a `healthcheck` against `/api/health`

#### Scenario: sidecar.yaml uses canonical Locket shape
- **WHEN** a developer reads `infrastructure/stacks/openclaw/sidecar.yaml`
- **THEN** the locket service SHALL declare `user: "65532:65532"`, `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`, `read_only: true`
- **AND** the `stack-secrets` volume SHALL be a tmpfs with `mode=0700`
- **AND** the openclaw service SHALL `depends_on: locket: { condition: service_healthy }` and bind `stack-secrets` read-only

### Requirement: openclaw Channel-Fanout Contract
The system SHALL run openclaw with `dm_policy: "pairing"` and expose the 6 v1 channels (Telegram, Slack, Discord, WhatsApp, WebChat, MS Teams) with the WebChat port 18789 routed via Pangolin and the Teams bridge port 3978 bound to `127.0.0.1` only.

#### Scenario: dmPolicy pairing is the default
- **WHEN** a new sender sends a message to any enabled channel
- **THEN** the gateway SHALL return a 6-character pairing code and NOT route the message to the agent fleet
- **AND** an operator SHALL be able to approve the pairing via `POST /api/pairing/approve`
- **AND** subsequent messages from the approved sender SHALL route to the configured agent (Celtic Tutor by default)

#### Scenario: WebChat route is private
- **WHEN** a user navigates to `https://openclaw.cianfhoghlaim.ie`
- **THEN** Pangolin TinyAuth SHALL require Pocket ID OIDC authentication first
- **AND** only then SHALL the user be presented with the openclaw WebChat pairing UI

#### Scenario: Teams bridge stays internal
- **WHEN** the openclaw container starts
- **THEN** port 3978 SHALL bind to `127.0.0.1` only
- **AND** no Pangolin route SHALL expose it
- **AND** the Azure Bot Framework outbound webhook model SHALL be used instead

### Requirement: openclaw Curated Skills Subset
The system SHALL mount a curated subset of 10 skills (out of the 108 in `.agents/skills/`) into the openclaw workspace via the `skills-curated/` sibling symlink directory.

#### Scenario: Skills subset is exactly 10
- **WHEN** a developer lists `infrastructure/stacks/openclaw/skills-curated/`
- **THEN** the directory SHALL contain exactly 10 symlinks pointing to: `dagster`, `dlt`, `oideachais-baml-schemas`, `ccc`, `browser-tools`, `litellm`, `langfuse`, `cognee`, `cocoindex`, `agent-fleet-orchestration`
- **AND** no other skills SHALL be reachable from the openclaw workspace

#### Scenario: Skills subset is mounted read-only
- **WHEN** the openclaw container starts
- **THEN** the `skills-curated/` directory SHALL be mounted at `/home/node/.openclaw/workspace/skills` with `:ro` flag
- **AND** a malformed skill update from chat SHALL fail with a clear error rather than mutating the upstream skill

### Requirement: openclaw LLM Provider Chain
The system SHALL configure openclaw with the OpenCode Go gateway (`opencode-go`) as primary provider and `minimax-coding-plan/minimax-m3` as fallback.

#### Scenario: opencode-go is primary
- **WHEN** the openclaw container starts
- **THEN** `config/openclaw.json` SHALL declare `provider: "opencode-go"` with `model: "minimax-m3"` (or the model documented in task 0.2)
- **AND** the single `OPENCODE_GO_API_KEY` SHALL be the only key required for the primary path

#### Scenario: minimax-coding-plan is fallback
- **WHEN** the primary `opencode-go` provider returns a non-retryable error
- **THEN** the gateway SHALL retry against `minimax-coding-plan/minimax-m3`
- **AND** only if both providers fail SHALL the gateway return a user-visible error

### Requirement: openclaw Pangolin Routing
The system SHALL route `openclaw.cianfhoghlaim.ie` to the openclaw container's gateway port 18789 via the Pangolin private-resource blueprint with Pocket ID OIDC SSO via TinyAuth.

#### Scenario: Pangolin resource is registered
- **WHEN** `pangolin apply blueprint` runs against `infrastructure/stacks/openclaw/blueprint.yaml`
- **THEN** a private resource SHALL be created with `name: "OpenClaw Gateway"`, `mode: "http"`, `full-domain: "openclaw.cianfhoghlaim.ie"`, `destination-port: 18789`, `protocol: "http"`, `roles: ["Member"]`, `destination: "openclaw"`

#### Scenario: Traefik labels are correct
- **WHEN** the Traefik router reads `infrastructure/stacks/openclaw/pangolin.yaml`
- **THEN** the `openclaw-gateway` router SHALL match `Host(\`openclaw.cianfhoghlaim.ie\`)`
- **AND** it SHALL apply `middlewares: [tinyauth, secure-headers]`
- **AND** the load-balancer SHALL target `http://openclaw:18789`