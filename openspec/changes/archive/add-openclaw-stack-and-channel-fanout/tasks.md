# Tasks — `add-openclaw-stack-and-channel-fanout`

## Phase 0 — Pre-flight verification

- [ ] **0.1** — Run `infrastructure/audit/scripts/inventory-arm1-oci.sh` and confirm OCI free-tier utilization is below 80% (CPU + memory). If utilization exceeds 80%, abort and surface to user; the change must move to `bunchloch` instead.
- [ ] **0.2** — Confirm `OPENCODE_GO_API_KEY` is set in `.env` (or in the Infisical `dev-baile/opencode-go/api_key` slot) and that the upstream gateway at `https://opencode.ai/zen/go/v1/v1/models` returns at least one model for the configured key. Document the model name to use as the primary in `openclaw.json`.
- [ ] **0.3** — Confirm the `openclaw/openclaw` upstream release tagged for use; record the semver + SHA256 digest.

## Phase 1 — Stack files (6-file GOLD_STANDARD)

- [ ] **1.1** — `mkdir -p infrastructure/stacks/openclaw/{config,skills-curated}`
- [ ] **1.2** — Write `infrastructure/stacks/openclaw/compose.yaml`:
  - `name: openclaw`
  - Single service `openclaw` (image pinned to `ghcr.io/openclaw/openclaw:<semver>@sha256:<digest>`, `pull_policy: if_not_present`).
  - Ports: `18789` (WebSocket RPC, exposed to Pangolin), `127.0.0.1:18790:18790` (bridge, internal only), `127.0.0.1:3978:3978` (MS Teams bridge, internal only).
  - `restart: unless-stopped`
  - Healthcheck: `curl -fs http://localhost:18789/api/health || exit 1` (`interval: 30s, timeout: 10s, retries: 3, start_period: 30s`).
  - Environment block: `OPENCLAW_STATE_DIR=/home/node/.openclaw` (workaround for upstream issue #77436 — host-path leak), `OPENCLAW_CONFIG=/home/node/.openclaw/openclaw.json`, `OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1`, `OTEL_SERVICE_NAME=openclaw-gateway`.
  - Volumes: `openclaw-state:/home/node/.openclaw`, `./config:/home/node/.openclaw/config:ro`, `./skills-curated:/home/node/.openclaw/workspace/skills:ro`.
  - `depends_on: locket: { condition: service_healthy }`
  - `volumes: [stack-secrets:/run/secrets/locket:ro]`, `env_file: [/run/secrets/locket/secrets.env]`
  - `networks: [cianfhoghlaim]`
  - `deploy.resources.limits: { cpus: '2', memory: 2G }`
  - `user: "1000:1000"` (matches the upstream image's non-root user; required so `OPENCLAW_STATE_DIR` is writable).
  - `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`.
- [ ] **1.3** — Write `infrastructure/stacks/openclaw/sidecar.yaml` (canonical Locket shape — copy from `infrastructure/stacks/agent-os/sidecar.yaml` template; adjust `container_name: openclaw-locket`, `image: ghcr.io/bpbradley/locket:infisical`).
- [ ] **1.4** — Write `infrastructure/stacks/openclaw/secrets.env` (9 `infisical://dev-baile/openclaw/<key>` references):
  - `OPENCLAW_GATEWAY_TOKEN` (gateway admin API token)
  - `OPENCODE_GO_API_KEY` (single-key primary)
  - `MINIMAX_API_KEY` (fallback)
  - `TELEGRAM_BOT_TOKEN`, `SLACK_BOT_TOKEN`, `DISCORD_BOT_TOKEN`, `WHATSAPP_ACCESS_TOKEN` (channel credentials)
  - `OTEL_EXPORTER_OTLP_ENDPOINT` (Langfuse OTLP/HTTP endpoint)
  - Header comments documenting the `dev-baile` folder structure.
- [ ] **1.5** — Write `infrastructure/stacks/openclaw/pangolin.yaml`:
  - `http.routers.openclaw-gateway` — `Host(\`openclaw.cianfhoghlaim.ie\`)`, `service: openclaw`, `entryPoints: [https]`, `tls.certResolver: letsencrypt`, `middlewares: [tinyauth, secure-headers]`.
  - `http.services.openclaw.loadBalancer.servers[0].url: "http://openclaw:18789"`.
- [ ] **1.6** — Write `infrastructure/stacks/openclaw/blueprint.yaml` (6-label shape, single entry for the WebChat route; mirror `infrastructure/stacks/marimo/blueprint.yaml` template).
- [ ] **1.7** — Write `infrastructure/stacks/openclaw/.env.example`:
  - Non-secret defaults: `OPENCLAW_PORT=18789`, `OPENCLAW_LOG_LEVEL=info`, `OPENCLAW_DM_POLICY=pairing`, `OPENCLAW_ALLOW_FROM=` (empty by default), `PANGOLIN_DOMAIN=openclaw.cianfhoghlaim.ie`.

## Phase 2 — Runtime config + curated skills

- [ ] **2.1** — Write `infrastructure/stacks/openclaw/config/openclaw.json` per the proposal schema (provider `opencode-go`, model `minimax-m3`, fallback `minimax-coding-plan/minimax-m3`, `dm_policy: pairing`, 6 channels enabled, OTLP block).
- [ ] **2.2** — Create `infrastructure/stacks/openclaw/skills-curated/` with 10 symlinks (relative paths) to `.agents/skills/{dagster,dlt,oideachais-baml-schemas,ccc,browser-tools,litellm,langfuse,cognee,cocoindex,agent-fleet-orchestration}/`. Verify each symlink resolves with `ls -la`.

## Phase 3 — Komodo orchestration

- [ ] **3.1** — Write `infrastructure/komodo/stacks/openclaw-arm1-oci.toml`:
  - `[[stack]]` block, `name = "openclaw"`, `server_id = "arm1-oci"`, `run_directory = "/etc/komodo/sruth/infrastructure/stacks/openclaw"`, `file_paths = ["compose.yaml","sidecar.yaml","pangolin.yaml","blueprint.yaml"]`.
  - `tags = ["host:arm1-oci","tier:control-plane","type:agent-runtime","domain:openclaw.cianfhoghlaim.ie"]`
  - `environment` block: `LOCKET_MODE=watch`, `INFISICAL_CLIENT_ID`, `INFISICAL_SECRET_FILE`.
- [ ] **3.2** — Write `infrastructure/komodo/procedures/deploy-openclaw-arm1-oci.toml` (5 stages — mirror `deploy-cognee-bunchloch.toml` shape):
  - Stage 0: prereqs (locket volume build).
  - Stage 1: dependency services (`langfuse`, `forgejo-runner`).
  - Stage 2: `DeployStack { stack = "openclaw" }`.
  - Stage 3: pangolin routes (apply blueprint).
  - Stage 4: health verification — `curl -fsS https://openclaw.cianfhoghlaim.ie/api/health` and `curl -fsS http://openclaw:18789/api/pairing/pending` (expect `{"count": 0}` or low number).

## Phase 4 — Docs + skill updates

- [ ] **4.1** — Write `infrastructure/stacks/openclaw/README.md` (Overview, Why This Matters, Key Features, Deployment, Environment Variables table, Access, Health Check, Upstream — mirror `marimo/README.md` structure).
- [ ] **4.2** — Append a row to `infrastructure/AGENTS.md` Stack Inventory table:
  - `| \`openclaw/\` | Channel-fanout gateway for the meaisínfhoghlaim 12-agent fleet (WebChat + 4 messaging channels in v1) | 18789 |`
- [ ] **4.3** — Update `.agents/skills/infrastructure-stacks/SKILL.md` with a 1-line addition in the "11 inventory categories" section noting the openclaw stack under "agent-runtime gateway".
- [ ] **4.4** — Add a new section "Channel-fanout entry-point" to `.agents/skills/agent-fleet-orchestration/SKILL.md` documenting the openclaw → 12-agent-fleet routing.
- [ ] **4.5** — Note in `tasks.md`: the `.agents/skills/meaisinfhoghlaim-agent-frameworks/SKILL.md` referenced in tasks 4.5 is the canonical openspec capability at `openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`. There is **no** corresponding `.agents/skills/meaisinfhoghlaim-agent-frameworks/SKILL.md` on disk; the canonical skill for the 12-agent fleet is `.agents/skills/agent-fleet-orchestration/SKILL.md`, which 4.4 updates directly.

## Phase 5 — Secret vault sync

- [ ] **5.1** — Append 9 URIs to `.infisical.env` (one per `secrets.env` entry).
- [ ] **5.2** — Run `bun run scripts/init-vault.ts` (a.k.a. `mise run secrets:init`) to sync the URIs to the `dev-baile/openclaw/` Infisical folder.

## Phase 6 — Validation gates

- [ ] **6.1** — `bun run validate-stacks` — must pass all 4 stack-doctor gates with the openclaw stack present.
- [ ] **6.2** — `openspec validate add-openclaw-stack-and-channel-fanout --strict` — must exit 0.
- [ ] **6.3** — `mise run lint:skills` — total must remain 108/108 (the 2 SKILL.md updates add zero new skills).
- [ ] **6.4** — Spot-check: `docker compose -f infrastructure/stacks/openclaw/compose.yaml config` parses; `docker compose -f infrastructure/stacks/openclaw/compose.yaml -f infrastructure/stacks/openclaw/sidecar.yaml config` shows `locket` as a healthy dependency.
- [ ] **6.5** — Spot-check: `cat infrastructure/stacks/openclaw/pangolin.yaml | yq -P` (if `yq` installed) — confirm the 6-label shape.

## Phase 7 — Handoff to deploy mode

- [ ] **7.1** — Hand off to deploy mode (the user runs `km run procedure deploy-openclaw-arm1-oci` on arm1-oci). Verify Stages 0–4 succeed. Capture the final URL + admin token in `infrastructure/stacks/openclaw/README.md` "First Deploy" section.
- [ ] **7.2** — Pair in the first WebChat sender (the user) via `curl -X POST -d '{"code":"<6-char>"}' https://openclaw.cianfhoghlaim.ie/api/pairing/approve` — confirm the pairing persists in the gateway's `allow_from` list.
- [ ] **7.3** — Post-deploy, archive the change: `openspec archive add-openclaw-stack-and-channel-fanout --yes`.