# OpenChamber — OpenCode Web/Desktop UI

## Overview

OpenChamber is a browser-based OpenCode UI built on Bun + React.
It can either bundle the `opencode-ai` runtime inside its own
container (the **arm1-oci** production surface) or it can route to
an externally-running OpenCode server (the **bunchloch** development
surface). The UI ships with 18+ themes, persistent session state,
and a provider picker for OpenAI, Anthropic, and
minimax-compatible gateways.

The upstream `openchamber/openchamber` image is built on
`oven/bun:1.3.5` and is MIT-licensed. The stack pins it to a
semver + SHA256 digest and updates monthly via the renovate
workflow.

## Why This Matters for Kings' College Galway

OpenCode is the canonical local AI coding agent used across the
Cianfhoghlaim monorepo. Until now the user ran it from the
terminal (`bunx opencode-ai`) with no web UI, no multi-device
sync, no session history, no theme support.

OpenChamber gives the user a **dedicated, persistent,
browser-based OpenCode UI** that they can reach from any device
on the Pangolin mesh — a single pane of glass for code-agent
work, with all sessions persisted across browser restarts.

## Runtime Model: Dual-Mode (arm1-oci bundled, bunchloch external)

The two surfaces of this stack use different runtime modes:

### arm1-oci (production): Bundled Mode

The OpenChamber container bundles its own `opencode-ai` runtime
inside the image. **No `OPENCODE_HOST` env var is set** — the UI
talks to the in-container runtime. Pangolin handles routing
(Pocket ID OIDC + TinyAuth at the Traefik layer).

### bunchloch (development): External OpenCode Mode

The user's Bunchloch development surface (MacBook M4) already
runs an OpenCode 1.17.9 server (`opencode --version` → `1.17.9`,
host-port `4096`) owned by the host operator. The
`compose.dev.yaml` overlay configures OpenChamber to consume
that external server instead of starting a second runtime:

| Env var | Value | Why |
|:--|:--|:--|
| `OPENCODE_HOST` | `http://host.docker.internal:4096` | Points at the host OpenCode server (must include explicit port + http(s) scheme) |
| `OPENCODE_PORT` | `4096` | Explicit port override (mirrors `OPENCODE_HOST`) |
| `OPENCODE_SKIP_START` | `true` | Refuses to launch a bundled `opencode-ai` daemon in the OpenChamber container |

In external mode:

- **One OpenCode runtime per host** — the user owns the host
  OpenCode process. The OpenChamber container is a UI only.
- **Host sessions and MCP config are authoritative** — sessions
  created by the host CLI (`bunx opencode-ai`) are visible inside
  the OpenChamber UI without copying or shadowing. The enabled
  MCP list (set in `~/.config/opencode/opencode.jsonc`) is
  consumed via the external server, never rehydrated into the
  OpenChamber volume.
- **Host OpenCode binaries reach the container** — the
  `extra_hosts: host.docker.internal:host-gateway` mapping plus
  the in-Dockerfile mount of
  `/Users/cianmacandeisigh/.local/share/mise/installs/opencode/1.17.9/opencode`
  at `/usr/local/bin/opencode-ai` (read-only) lets the
  container resolve the binary path the same way the host does.

This contract is implemented and verified in
`openspec/changes/2026-07-28-openchamber-bunchloch-dev-parity-v1`
(reference: the `infrastructure-stacks` spec delta in
`specs/infrastructure-stacks/spec.md`).

## Image Pinning

| Surface | Image | Tag |
|:--|:--|:--|
| arm1-oci | `ghcr.io/cianfhoghlaim/openchamber` | `1.14.1-arm1` (built by `Dockerfile.openchamber-web`) |
| bunchloch | `openchamber:local-1.16.3` (built from `Dockerfile.openchamber-web` against the v1.16.3 tarball at `/tmp/openchamber-build/`) | `1.16.3` |

Images MUST NOT use `:latest` or any unversioned reference.
The Dockerfile installs `git` in the runtime stage so
git-aware OpenCode sessions resolve against the host checkout
mounted at the identical absolute path.

## No Cloudflare Tunnel in v1

OpenChamber supports a `cloudflared`-based tunnel for public
access without a Pangolin route. This stack **leaves the
`OPENCHAMBER_TUNNEL_TOKEN` blank** for arm1-oci; Pangolin
handles the routing via TinyAuth + Pocket ID OIDC. The
bunchloch dev surface binds loopback only (no public listener).

**Cloudflare tunnel mode** (future enhancement): uncomment
`OPENCHAMBER_TUNNEL_TOKEN` in `.env.example` and set the token
from your Cloudflare Zero Trust dashboard. Documented in
`.env.example` but is NOT the default.

## Key Features

- **Bundled OpenCode runtime** (arm1-oci) — no separate daemon
  required
- **External OpenCode mode** (bunchloch dev) — uses the host
  OpenCode server, keeps host sessions + MCP config authoritative
- **18+ themes** — including the canonical `cianfhoghlaim-dark`
- **Persistent UI config** — `openchamber-config` named volume
  mounted at `/home/bun/.config/openchamber` (does NOT shadow
  `/home/bun/.openchamber` the application workdir)
- **3 LLM providers** — OpenAI, Anthropic, minimax-compatible
- **Pocket ID OIDC SSO** (arm1-oci primary auth) + `OPENCHAMBER_UI_PASSWORD`
  (2nd-factor inside the bundled UI)
- **Loopback-only dev surface** — `127.0.0.1:13000:3000`; no
  `0.0.0.0` binds on bunchloch

## Deployment

### Docker Compose (Local Development — bunchloch)

```bash
cd bonneagar/stacks/openchamber
docker compose \
  --env-file ../../../.env \
  -f stacks/openchamber/compose.yaml \
  -f stacks/openchamber/sidecar.yaml \
  -f stacks/openchamber/compose.dev.yaml \
  up -d
```

The dev overlay (compose.dev.yaml) enforces the external-mode
contract. Verify the contract after `up -d`:

```bash
# 1. Container /health returns 200 (canonical v1.16.3 endpoint)
curl -fsS http://127.0.0.1:13000/health | jq '{status, openchamberVersion, isOpenCodeReady, openCodePort}'

# 2. Host OpenCode 1.17.9 /global/health returns 200 (the host-owned runtime)
curl -fsS http://127.0.0.1:4096/global/health | jq '{healthy, version}'

# 3. Container can reach host OpenCode via host.docker.internal
docker exec openchamber-dev curl -fsS http://host.docker.internal:4096/global/health

# 4. git is in the runtime image
docker exec openchamber-dev git --version

# 5. container OPENCODE_HOST is set (points at the host, not bundled)
docker exec openchamber-dev printenv OPENCODE_HOST OPENCODE_PORT OPENCODE_SKIP_START

# 6. NO plaintext secret in the repository
git grep -I -E "OPENAI_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}" -- stacks/openchamber/ || echo "OK: no plaintext secret keys"
```

### Docker Compose (Production — arm1-oci with Locket Secret Injection)

```bash
cd bonneagar/stacks/openchamber
docker compose -f compose.yaml -f sidecar.yaml up -d
```

The Locket sidecar (`ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1`)
resolves all `infisical://dev-baile/openchamber/...` URIs at runtime
and writes them to `/run/secrets/locket/secrets.env`, which the
OpenChamber entrypoint then sources via a shell wrapper.

### Komodo (GitOps)

This stack is deployed via Komodo. The arm1-oci stack reads
`compose.yaml + sidecar.yaml + pangolin.yaml + blueprint.yaml`
and is built from the local Dockerfile via
`komodo/builds/openchamber-arm1-oci.toml`. The bunchloch dev
surface is brought up manually using the `compose.dev.yaml`
overlay (the Komodo bunchloch stack tracks the same 2 files
plus dev-only env via
`komodo/stacks/openchamber-bunchloch.toml`).

```bash
km run procedure deploy-openchamber-bunchloch
```

## Environment Variables

| Variable | Required | Surface | Description | Default |
|:--|:--|:--|:--|:--|
| `OPENCHAMBER_UI_PASSWORD` | yes (prod) | both | 2nd-factor UI password (random 32 chars) | from Locket/Infisical or `../../../.env` |
| `OPENAI_API_KEY` | no | both | OpenAI provider key (any missing key disables that provider) | from Locket/Infisical or `../../../.env` |
| `ANTHROPIC_API_KEY` | no | both | Anthropic provider key | from Locket/Infisical |
| `MINIMAX_API_KEY` | yes (prod) | both | minimax-compatible provider key (default in v1) | from Locket/Infisical |
| `OPENCHAMBER_PORT` | no | both | UI port (in-container) | `3000` |
| `OPENCHAMBER_THEME` | no | both | Default theme | `cianfhoghlaim-dark` |
| `OPENCHAMBER_LOG_LEVEL` | no | both | Log level (debug/info/warn/error) | `info` |
| `OPENCHAMBER_VERSION` | no | both | Image version (pinned at build time) | `1.16.3` |
| `OPENCODE_HOST` | yes (dev) / no (prod) | dev | External OpenCode daemon URL with explicit port (e.g. `http://host.docker.internal:4096`) | not set (prod bundled mode); `http://host.docker.internal:4096` (dev) |
| `OPENCODE_PORT` | yes (dev) / no (prod) | dev | External OpenCode port (mirrors `OPENCODE_HOST`) | not set (prod); `4096` (dev) |
| `OPENCODE_SKIP_START` | yes (dev) / no (prod) | dev | Refuse to launch a bundled `opencode-ai` daemon | not set (prod); `true` (dev) |
| `OPENCHAMBER_TUNNEL_TOKEN` | no | both | Cloudflare tunnel token (tunnel mode only) | not set (Pangolin handles routing) |
| `PANGOLIN_DOMAIN` | no | prod | Public hostname | `openchamber.cianfhoghlaim.ie` |
| `INFISICAL_URL` / `INFISICAL_CLIENT_ID` / `INFISICAL_PROJECT_ID` / `INFISICAL_ENV` | yes (prod) | prod | Locket sidecar credential chain | from Komodo env or Komodo-deployed `infisical_secret` file |

## Access

### arm1-oci (production)

- **URL**: `https://openchamber.cianfhoghlaim.ie` (private,
  Pangolin Member role required, then OpenChamber UI password)
- **Internal port**: 3000 (bound to `127.0.0.1`; Pangolin
  handles public routing)
- **Auth**: Pocket ID OIDC (primary) + `OPENCHAMBER_UI_PASSWORD`
  (2nd factor)

### bunchloch (development)

- **URL**: `http://127.0.0.1:13000` (loopback only — no
  Pangolin publishing, no public listener)
- **Internal port**: 3000 (inside container)
- **Loopback bind**: `127.0.0.1:13000:3000` (per task 5.3 —
  never `0.0.0.0`, never a public interface)
- **OpenCode runtime**: the host OpenCode 1.17.9 server at
  `127.0.0.1:4096` (not owned by the container)

## Health Check

### arm1-oci (production)

Pangolin's Traefik reads `/api/health` for HTTP health checking
(the bundled-opencode/1.14.x endpoint contract). Verify at:

```bash
docker ps --filter name=openchamber --format "table {{.Names}}\t{{.Status}}"
curl -fsS https://openchamber.cianfhoghlaim.ie/api/health
```

### bunchloch (development)

The canonical v1.16.x health endpoint is `/health`; the
legacy `/api/health` path returns 401 in v1.16.3 and MUST NOT
be substituted. Verify at:

```bash
docker ps --filter name=openchamber-dev --format "table {{.Names}}\t{{.Status}}"
curl -fsS http://127.0.0.1:13000/health
# External OpenCode health (host-owned runtime)
curl -fsS http://127.0.0.1:4096/global/health
# Same OpenCode health reachable from inside the container
docker exec openchamber-dev curl -fsS http://host.docker.internal:4096/global/health
```

## Rollback

The bunchloch dev contract is implemented so that the host
OpenCode sessions, host MCP configuration, and host repository
checkout are NEVER touched by the container. Rollback is
therefore a strict subset of the deploy steps:

```bash
# 1. Stop the openchamber dev container + no-op locket (no effect on host opencode)
docker compose -f stacks/openchamber/compose.yaml -f stacks/openchamber/sidecar.yaml \
               -f stacks/openchamber/compose.dev.yaml down

# 2. Remove the persistent XDG config volume (operator choice — UI preferences)
docker volume rm openchamber_openchamber-config

# 3. Everything else is intact:
#   - host opencode 1.17.9 is still running on 127.0.0.1:4096
#   - host opencode session store is unchanged
#   - host MCP config in ~/.config/opencode/opencode.jsonc is unchanged
#   - host repository /Users/cianmacandeisigh/dev/kings_college_galway is unchanged
```

The arm1-oci production rollback follows the same pattern via
`km deploy stack openchamber-bunchloch --down` (or the inverse
of the `deploy-openchamber-arm1-oci` procedure).

## Upstream

- **Repository**: https://github.com/openchamber/openchamber
- **License**: MIT
- **Image**: `ghcr.io/openchamber/openchamber:<semver>@sha256:<digest>`
  (private — the local `Dockerfile.openchamber-web` is the canonical build)
- **Base image**: `oven/bun:1.3.5@sha256:<digest>`
- **Bundled runtime**: `opencode-ai` (semver pinned in the
  upstream image; disabled in v1.16.3 bunchloch dev via
  `OPENCODE_SKIP_START=true`)
- **Default port**: 3000 (loopback: 3000 arm1-oci, 13000
  bunchloch-dev container-to-host mapping)

## Cross-references

- `openspec/changes/2026-07-28-openchamber-bunchloch-dev-parity-v1` —
  the Bunchloch dev contract implementation. Spec deltas at
  `openspec/.../specs/infrastructure-stacks/spec.md` (added) and
  `openspec/.../specs/agent-platform-cluster/spec.md` (added).
- `openspec/specs/infrastructure-stacks/spec.md` — the
  canonical 6-file GOLD_STANDARD stack contract + the agent
  cluster topology
- `openspec/specs/agent-platform-cluster/spec.md` — the
  8-stack agent cluster topology that OpenChamber is one of
  3 agent surfaces in (alongside openclaw + hermes)
- `docs/stacks/openchamber.md` — the per-stack "purpose +
  why-GitOps" doc
- `bonneagar/komodo/procedures/deploy-openchamber-bunchloch.toml` —
  the deploy procedure (adds a Stage 5
  `bunchloch-parity-verification` block per this change)
- `bonneagar/komodo/procedures/deploy-openchamber-arm1-oci.toml` —
  the production deploy procedure (arm1-oci bundled mode)
- `.agents/skills/secrets-management/SKILL.md` — the Infisical
  + Locket + mise three-way contract that this stack depends on
