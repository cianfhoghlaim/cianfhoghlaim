# Tasks — `add-openchamber-stack-and-opencode-ui`

## Phase 0 — Pre-flight verification

- [ ] **0.1** — Run `infrastructure/audit/scripts/inventory-arm1-oci.sh` and confirm OCI free-tier utilization is below 80% (CPU + memory). If utilization exceeds 80%, abort and surface to user; the change must move to `bunchloch` instead.
- [ ] **0.2** — Confirm the `openchamber/openchamber` upstream release tagged for use; record the semver + SHA256 digest + base image digest (`oven/bun:1.3.5`).

## Phase 1 — Stack files (6-file GOLD_STANDARD)

- [ ] **1.1** — `mkdir -p infrastructure/stacks/openchamber`
- [ ] **1.2** — Write `infrastructure/stacks/openchamber/compose.yaml`:
  - `name: openchamber`
  - Single service `openchamber` (image pinned to `ghcr.io/openchamber/openchamber:<semver>@sha256:<digest>`, `pull_policy: if_not_present`).
  - Port: `127.0.0.1:3000:3000` (Pangolin routes 3000).
  - `restart: unless-stopped`
  - Healthcheck: `curl -fs http://localhost:3000/api/health || exit 1` (`interval: 30s, timeout: 10s, retries: 3, start_period: 20s`).
  - Environment block: `OPENCHAMBER_PORT=3000`, `OPENCHAMBER_THEME=${OPENCHAMBER_THEME:-cianchoghlaim-dark}`, `OPENCHAMBER_LOG_LEVEL=${OPENCHAMBER_LOG_LEVEL:-info}`.
  - **NO `OPENCODE_HOST` env var** — bundled mode only.
  - **NO `OPENCHAMBER_TUNNEL_TOKEN` env var** — no Cloudflare tunnel in v1.
  - Volumes: `openchamber-state:/home/bun/.openchamber`.
  - `depends_on: locket: { condition: service_healthy }`
  - `volumes: [stack-secrets:/run/secrets/locket:ro]`, `env_file: [/run/secrets/locket/secrets.env]`
  - `networks: [cianchoghlaim]`
  - `deploy.resources.limits: { cpus: '1', memory: 1G }`
  - `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`.
- [ ] **1.3** — Write `infrastructure/stacks/openchamber/sidecar.yaml` (canonical Locket shape — copy from `infrastructure/stacks/openclaw/sidecar.yaml` template; adjust `container_name: openchamber-locket`).
- [ ] **1.4** — Write `infrastructure/stacks/openchamber/secrets.env` (4 `infisical://dev-baile/openchamber/<key>` references):
  - `OPENCHAMBER_UI_PASSWORD` (UI 2nd-factor auth, 32-char random)
  - `OPENAI_API_KEY` (OpenAI provider key for OpenCode runtime)
  - `ANTHROPIC_API_KEY` (Anthropic provider key)
  - `MINIMAX_API_KEY` (minimax-compatible provider key)
  - Header comments documenting the `dev-baile` folder structure.
- [ ] **1.5** — Write `infrastructure/stacks/openchamber/pangolin.yaml`:
  - `http.routers.openchamber-ui` — `Host(\`openchamber.cianfhoghlaim.ie\`)`, `service: openchamber`, `entryPoints: [https]`, `tls.certResolver: letsencrypt`, `middlewares: [tinyauth, secure-headers]`.
  - `http.services.openchamber.loadBalancer.servers[0].url: "http://openchamber:3000"`.
- [ ] **1.6** — Write `infrastructure/stacks/openchamber/blueprint.yaml` (6-label shape, single entry for the UI route; mirror `infrastructure/stacks/openclaw/blueprint.yaml` template).
- [ ] **1.7** — Write `infrastructure/stacks/openchamber/.env.example`:
  - Non-secret defaults: `OPENCHAMBER_PORT=3000`, `OPENCHAMBER_THEME=cianchoghlaim-dark`, `OPENCHAMBER_LOG_LEVEL=info`, `PANGOLIN_DOMAIN=openchamber.cianfhoghlaim.ie`.
  - Documented placeholder for `OPENCHAMBER_UI_PASSWORD` (set via Locket).

## Phase 2 — Komodo orchestration

- [ ] **2.1** — Write `infrastructure/komodo/stacks/openchamber-arm1-oci.toml`:
  - `[[stack]]` block, `name = "openchamber"`, `server_id = "arm1-oci"`, `run_directory = "/etc/komodo/sruth/infrastructure/stacks/openchamber"`, `file_paths = ["compose.yaml","sidecar.yaml","pangolin.yaml","blueprint.yaml"]`.
  - `tags = ["host:arm1-oci","tier:control-plane","type:agent-ui","domain:openchamber.cianfhoghlaim.ie"]`
  - `environment` block: `LOCKET_MODE=watch`, `INFISICAL_CLIENT_ID`, `INFISICAL_SECRET_FILE`, `OPENCHAMBER_PORT`, `OPENCHAMBER_THEME`, `PANGOLIN_DOMAIN`.
- [ ] **2.2** — Write `infrastructure/komodo/procedures/deploy-openchamber-arm1-oci.toml` (5 stages — mirror `deploy-openclaw-arm1-oci.toml` shape):
  - Stage 0: prereqs (locket volume build).
  - Stage 1: dependency services (`pangolin`).
  - Stage 2: `DeployStack { stack = "openchamber" }`.
  - Stage 3: pangolin routes (apply blueprint).
  - Stage 4: health verification — `curl -fsS https://openchamber.cianfhoghlaim.ie/api/health`.

## Phase 3 — Docs + skill updates

- [ ] **3.1** — Write `infrastructure/stacks/openchamber/README.md` (Overview, Why This Matters, Key Features, Deployment, Environment Variables table, Access, Health Check, Upstream — mirror `openclaw/README.md` structure; document the bundled-mode decision and the future external-mode path).
- [ ] **3.2** — Append a row to `infrastructure/AGENTS.md` Stack Inventory table:
  - `| \`openchamber/\` | OpenChamber — bundled OpenCode web/desktop UI (Bun + React, 18+ themes) | 3000 |`
- [ ] **3.3** — Update `.agents/skills/infrastructure-stacks/SKILL.md` with a 1-line addition in the "11 inventory categories" section noting the openchamber stack under "agent-ui surface".
- [ ] **3.4** — Add a new section "Bundled-mode OpenCode UI (OpenChamber)" to `.agents/skills/agentic-frontend-frameworks/SKILL.md` documenting the runtime model and the relationship to the CopilotKit AG-UI surface.

## Phase 4 — Secret vault sync

- [ ] **4.1** — Append 4 URIs to `.infisical.env` (one per `secrets.env` entry).
- [ ] **4.2** — Run `bun run scripts/init-vault.ts` (a.k.a. `mise run secrets:init`) to sync the URIs to the `dev-baile/openchamber/` Infisical folder.

## Phase 5 — Validation gates

- [ ] **5.1** — `bun run validate-stacks` — must pass all 4 stack-doctor gates with the openchamber stack present.
- [ ] **5.2** — `openspec validate add-openchamber-stack-and-opencode-ui --strict` — must exit 0.
- [ ] **5.3** — `mise run lint:skills` — total must remain 108/108 (the 2 SKILL.md updates add zero new skills).
- [ ] **5.4** — Spot-check: `docker compose -f infrastructure/stacks/openchamber/compose.yaml config` parses; `docker compose -f infrastructure/stacks/openchamber/compose.yaml -f infrastructure/stacks/openchamber/sidecar.yaml config` shows `locket` as a healthy dependency.
- [ ] **5.5** — Spot-check: confirm `OPENCODE_HOST` is NOT set anywhere in `infrastructure/stacks/openchamber/`.

## Phase 6 — Handoff to deploy mode

- [ ] **6.1** — Hand off to deploy mode (the user runs `km run procedure deploy-openchamber-arm1-oci` on arm1-oci). Verify Stages 0–4 succeed. Capture the final URL + UI password in `infrastructure/stacks/openchamber/README.md` "First Deploy" section.
- [ ] **6.2** — Open `https://openchamber.cianfhoghlaim.ie` in a browser; confirm Pocket ID OIDC flow → OpenChamber UI loads → bundled OpenCode runtime responds to a sample prompt.
- [ ] **6.3** — Post-deploy, archive the change: `openspec archive add-openchamber-stack-and-opencode-ui --yes`.