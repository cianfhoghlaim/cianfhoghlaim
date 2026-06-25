# `infrastructure-stacks` capability spec — openchamber delta

The infrastructure-stacks capability spec governs the 94+ Docker
Compose stacks under `infrastructure/stacks/`, the 6-file
GOLD_STANDARD pattern, the Locket sidecar contract, and the
Pangolin Traefik routing shape.

This delta adds the openchamber OpenCode UI stack as a
first-class stack with the bundled-OpenCode runtime contract.

## ADDED Requirements

### Requirement: openchamber Stack Directory
The system SHALL provide a Docker Compose stack at `infrastructure/stacks/openchamber/` that runs the upstream `openchamber/openchamber` OpenCode web/desktop UI plus a Locket sidecar for Infisical secret injection.

#### Scenario: 6 GOLD_STANDARD files present
- **WHEN** a developer lists `infrastructure/stacks/openchamber/`
- **THEN** the directory SHALL contain all 6 GOLD_STANDARD files: `compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `.env.example`
- **AND** a `README.md` describing the stack

#### Scenario: compose.yaml uses pinned image
- **WHEN** a developer reads `infrastructure/stacks/openchamber/compose.yaml`
- **THEN** the `image:` line SHALL be pinned to `<major>.<minor>.<patch>@sha256:<digest>` with no `:latest` tag
- **AND** the service SHALL declare `restart: unless-stopped` and a `healthcheck` against `/api/health`
- **AND** port `3000` SHALL bind to `127.0.0.1` only (Pangolin handles public routing)

#### Scenario: sidecar.yaml uses canonical Locket shape
- **WHEN** a developer reads `infrastructure/stacks/openchamber/sidecar.yaml`
- **THEN** the locket service SHALL declare `user: "65532:65532"`, `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`, `read_only: true`
- **AND** the `stack-secrets` volume SHALL be a tmpfs with `mode=0700`
- **AND** the openchamber service SHALL `depends_on: locket: { condition: service_healthy }` and bind `stack-secrets` read-only

### Requirement: openchamber Bundled-Mode Runtime Contract
The system SHALL run openchamber in **bundled mode** — the `opencode-ai` runtime is shipped inside the openchamber container; no external OpenCode daemon is required.

#### Scenario: OPENCODE_HOST is not set
- **WHEN** the openchamber container starts
- **THEN** the `OPENCODE_HOST` environment variable SHALL NOT be set in `compose.yaml` or `secrets.env`
- **AND** the bundled `opencode-ai` runtime inside the image SHALL handle all LLM calls

#### Scenario: Bundled OpenCode version is pinned
- **WHEN** the openchamber image is rebuilt
- **THEN** the bundled `opencode-ai` version SHALL match the upstream openchamber release's documented version
- **AND** the version SHALL be recorded in the stack README

### Requirement: openchamber No-Cloudflare-Tunnel Contract
The system SHALL NOT enable the upstream Cloudflare tunnel mode in v1; Pangolin handles the public routing.

#### Scenario: Tunnel token is not set
- **WHEN** the openchamber container starts
- **THEN** the `OPENCHAMBER_TUNNEL_TOKEN` environment variable SHALL NOT be set in `compose.yaml` or `secrets.env`
- **AND** the `cloudflared` binary in the image SHALL remain unused

#### Scenario: Future enhancement is documented
- **WHEN** an operator wants to enable Cloudflare tunnel mode
- **THEN** `infrastructure/stacks/openchamber/README.md` SHALL document the procedure (set `OPENCHAMBER_TUNNEL_TOKEN`, expose port via Cloudflare DNS)
- **AND** the change SHALL NOT require a new openspec proposal

### Requirement: openchamber LLM Provider Keys
The system SHALL configure openchamber with 3 LLM provider keys (OpenAI, Anthropic, minimax-compatible) sourced from Infisical via the Locket sidecar.

#### Scenario: Provider keys are loaded from secrets.env
- **WHEN** the openchamber container starts
- **THEN** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `MINIMAX_API_KEY` SHALL all be populated from `secrets.env`
- **AND** any missing key SHALL disable the corresponding provider in the OpenCode runtime (graceful degradation, no crash)

#### Scenario: UI password is the 2nd-factor
- **WHEN** an authenticated Pocket ID user reaches the openchamber UI
- **THEN** the UI SHALL additionally require `OPENCHAMBER_UI_PASSWORD` from `secrets.env`
- **AND** the password SHALL be a random 32-char string stored in Infisical

### Requirement: openchamber Pangolin Routing
The system SHALL route `openchamber.cianfhoghlaim.ie` to the openchamber container's UI port 3000 via the Pangolin private-resource blueprint with Pocket ID OIDC SSO via TinyAuth.

#### Scenario: Pangolin resource is registered
- **WHEN** `pangolin apply blueprint` runs against `infrastructure/stacks/openchamber/blueprint.yaml`
- **THEN** a private resource SHALL be created with `name: "OpenChamber UI"`, `mode: "http"`, `full-domain: "openchamber.cianfhoghlaim.ie"`, `destination-port: 3000`, `protocol: "http"`, `roles: ["Member"]`, `destination: "openchamber"`

#### Scenario: Traefik labels are correct
- **WHEN** the Traefik router reads `infrastructure/stacks/openchamber/pangolin.yaml`
- **THEN** the `openchamber-ui` router SHALL match `Host(\`openchamber.cianfhoghlaim.ie\`)`
- **AND** it SHALL apply `middlewares: [tinyauth, secure-headers]`
- **AND** the load-balancer SHALL target `http://openchamber:3000`