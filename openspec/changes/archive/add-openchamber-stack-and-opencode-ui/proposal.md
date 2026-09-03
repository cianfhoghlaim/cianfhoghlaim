# Change: add-openchamber-stack-and-opencode-ui

## Why

OpenCode (the upstream `sst/opencode` CLI) is the canonical
local AI coding agent used across the Cianfhoghlaim monorepo.
Today the user runs it in one of two ways:

1. **Local-only** — `bunx opencode-ai` (or `npx opencode-ai`)
   from the terminal, with no web UI, no multi-device sync,
   no Cloudflare tunnel for remote access.
2. **Per-repo dev loop** — the `opencode` CLI is invoked
   from inside Cursor / VS Code / a CI runner, but each
   session is ephemeral and per-machine.

Neither gives the user a **dedicated, persistent, browser-based
OpenCode UI** that they can reach from any device on the Pangolin
mesh — a single pane of glass for the 12-agent fleet, with
session history, theme support, and provider config.

The upstream [`openchamber/openchamber`](https://github.com/openchamber/openchamber)
project packages exactly this: an OpenCode web/desktop UI built
on Bun + React, with 18+ themes, session sync, bundled
OpenCode runtime, optional Cloudflare tunnel, and provider
config for OpenAI, Anthropic, and OpenCode-compatible gateways
(minimax included).

This change adds OpenChamber as a first-class Docker Compose
stack on `arm1-oci`, reachable at
`openchamber.cianfhoghlaim.ie` via the Pangolin private
resource mesh.

## What Changes

### 1. New Docker Compose stack `infrastructure/stacks/openchamber/`

A single-service stack running the upstream OpenChamber
container (built on `oven/bun:1.3.5@sha256:<digest>` with
`opencode-ai` bundled) plus a `locket` sidecar for Infisical
secret injection. Networking: shared `cianfhoghlaim` bridge.

- `compose.yaml` — single service, named volume for
  persistent session state (`openchamber-state`).
- `sidecar.yaml` — canonical Locket shape (same as openclaw).
- `secrets.env` — 4 `infisical://dev-baile/openchamber/<key>`
  references: UI access password, OpenAI key, Anthropic key,
  minimax key.
- `pangolin.yaml` — Traefik routing for
  `openchamber.cianfhoghlaim.ie → openchamber:3000` (the
  React UI + WebSocket terminal).
- `blueprint.yaml` — Pangolin resource definitions matching
  the 6-label shape.
- `.env.example` — non-secret defaults: port, theme, log
  level, `OPENCHAMBER_UI_PASSWORD` placeholder.

### 2. Bundled-mode (no external OpenCode server)

The OpenChamber container bundles its own `opencode-ai`
runtime — there is no need to point it at a separately-running
OpenCode daemon. This change **does not** set the
`OPENCODE_HOST` env var; the UI talks to the in-container
runtime.

This decision was made in the build-phase user survey (the
user picked "bundled" over "external" to avoid running two
processes). The future-enhancement path to external-mode is
documented in `README.md`.

### 3. No Cloudflare tunnel for v1

OpenChamber supports a `cloudflared`-based tunnel for public
access without a Pangolin route. This change **leaves the
`OPENCHAMBER_TUNNEL_TOKEN` blank**; Pangolin handles the
routing via TinyAuth + Pocket ID OIDC. The `cloudflared`
binary remains in the image (pinned to upstream SHA256) so
the tunnel mode can be enabled by setting the token and
rebuilding the compose file.

### 4. Komodo stack + deploy procedure

- `infrastructure/komodo/stacks/openchamber-arm1-oci.toml` —
  `[[stack]]` block referencing the 6-file compose set, with
  tags `host:arm1-oci`, `tier:control-plane`,
  `type:agent-ui`, `domain:openchamber.cianfhoghlaim.ie`.
- `infrastructure/komodo/procedures/deploy-openchamber-arm1-oci.toml`
  — 5-stage deploy (prereqs → pangolin → openchamber stack →
  pangolin routes → health checks via
  `curl https://openchamber.cianfhoghlaim.ie/api/health`).

### 5. Stack inventory + AGENTS.md

- `infrastructure/AGENTS.md` gets **+1 row** in the Stack
  Inventory table (`openchamber/`).

### 6. OpenSpec change artifacts

- This `proposal.md` + `tasks.md` +
  `specs/infrastructure-stacks/spec.md` +
  `specs/agentic-frontend-frameworks/spec.md`.

## Impact

- **Affected specs:**
  - MODIFIED `infrastructure-stacks` — the new stack plus
    the OpenChamber UI runtime contract (bundled OpenCode,
    no Cloudflare tunnel in v1).
  - MODIFIED `agentic-frontend-frameworks` — OpenChamber as
    a sibling agent UI surface alongside TanStack Start
    (CopilotKit AG-UI), Convex dashboards, marimo notebooks,
    and Babylon.js game UI.
- **NEW files:**
  - `infrastructure/stacks/openchamber/{compose.yaml, sidecar.yaml, secrets.env, pangolin.yaml, blueprint.yaml, .env.example, README.md}`
  - `infrastructure/komodo/stacks/openchamber-arm1-oci.toml`
  - `infrastructure/komodo/procedures/deploy-openchamber-arm1-oci.toml`
  - `openspec/changes/add-openchamber-stack-and-opencode-ui/{proposal.md, tasks.md, specs/infrastructure-stacks/spec.md, specs/agentic-frontend-frameworks/spec.md}`
- **MODIFIED files:**
  - `infrastructure/AGENTS.md` — +1 row in Stack Inventory
  - `.infisical.env` — +4 vault references
- **Affected agent skills:**
  - `.agents/skills/infrastructure-stacks/SKILL.md` —
    1-line addition in the "11 inventory categories" section
    for the openchamber stack (agent UI).
  - `.agents/skills/agentic-frontend-frameworks/SKILL.md` —
    new section "Bundled-mode OpenCode UI (OpenChamber)"
    documenting the runtime model and the relationship to the
    CopilotKit AG-UI surface.
- **Affected CI:** `bun run validate-stacks` (stack-doctor
  4-gate check) — the new stack must pass all 4 gates
  before commit.
- **Affected workflows:** `komodo run procedure
  deploy-openchamber-arm1-oci` registers a new 5-stage
  deploy procedure in Komodo.

## Non-Goals

- This change does **not** enable the Cloudflare tunnel
  mode. Pangolin handles routing; the Cloudflare tunnel is
  an alternative path documented in the upstream README.
- This change does **not** wire OpenChamber to an
  external OpenCode daemon. Bundled mode only.
- This change does **not** add a new LLM provider to the
  OpenCode runtime; the UI uses the existing OpenAI /
  Anthropic / OpenCode-compatible gateway keys.
- This change does **not** expose port 3000 directly —
  Pangolin routes the public traffic; the container port
  stays on the Docker network.
- This change does **not** add a public-domain route.
  `openchamber.cianfhoghlaim.ie` is private (Pocket ID SSO
  via TinyAuth).

## Risk Assessment

- **Risk: arm1-oci resource ceiling.** Same as openclaw —
  ~256 MB idle / 1 GB under load. **Mitigation:** task 1.0
  in `tasks.md` re-runs
  `infrastructure/audit/scripts/inventory-arm1-oci.sh`
  pre-deploy; if utilization exceeds 80%, deploy is
  aborted.
- **Risk: bundled OpenCode version drifts.** The
  `opencode-ai` package bundled in the OpenChamber image
  is upstream-pinned to a semver. **Mitigation:** monthly
  renovate cycle.
- **Risk: webchat password reuse.** `OPENCHAMBER_UI_PASSWORD`
  is the only auth for the bundled UI. **Mitigation:** the
  Pocket ID OIDC SSO at Pangolin is the primary auth; the
  UI password is a 2nd factor (set in `.env.example` to a
  random 32-char string).
- **Risk: openchamber upstream is moving fast (5.8k stars
  on a young repo).** **Mitigation:** semver + SHA256 pin;
  renovate workflow covers monthly upgrades.

## Validation

1. `docker compose -f infrastructure/stacks/openchamber/compose.yaml config`
   parses successfully.
2. `docker compose -f infrastructure/stacks/openchamber/compose.yaml -f infrastructure/stacks/openchamber/sidecar.yaml config`
   parses successfully and shows `locket` as `service_healthy`
   dependency.
3. `infrastructure/stacks/openchamber/pangolin.yaml` matches the
   6-label shape.
4. `bun run validate-stacks` passes all 4 gates with the
   openchamber stack present.
5. `openspec validate add-openchamber-stack-and-opencode-ui --strict`
   passes — every `### Requirement:` has at least one
   `#### Scenario:`.
6. (post-deploy) `curl -fsS https://openchamber.cianfhoghlaim.ie/api/health`
   returns HTTP 200 within 30 s of `komodo run procedure
   deploy-openchamber-arm1-oci`.