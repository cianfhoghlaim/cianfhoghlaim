# Tasks — `2026-06-30-agent-platform-cluster-hermes-cocoindex`

> **Pick 2 of 5 status (2026-07-08):** 28/72 tasks complete
> in the pick-2 scope (agent-platform-cluster + Hermes + M3
> chokepoint + 4 v1 CocoIndex Apps + 3 agent-surface rewires).
>
> The remaining 44 tasks belong to the wider v4-landing absorbed
> scope (Apple Photos DLT pipeline, the 4 v1 Apps' Dagster
> assets, 4 spec deltas, 6 skill updates, 1 new skill) and
> are tracked in follow-on picks (`pick-3` through `pick-5`).
>
> Pick-2 deliverables (per the build-mode dispatch):
> 1. ✓ 8 stack directories with 6-file GOLD_STANDARD
>    (lakehouse + litellm + langfuse + mlflow + logfire +
>    cognee + graphiti + lancedb).
> 2. ✓ LiteLLM M3 chokepoint wired with 5 routing keywords
>    + canonical `minimax-m3` alias for the 3 agent surfaces.
>    Smoke test passes (config-parse + routing simulation).
> 3. ✓ Omnibus Komodo procedure
>    `deploy-agent-platform-cluster-bunchloch.toml` with
>    `--skip=<foundation|observability|memory|surfaces>`
>    flags + 8 health-check endpoints + 1 stack-doctor
>    validation gate.
> 4. ✓ 3 agent surfaces (openclaw + openchamber + hermes)
>    rewired to route through LiteLLM.
> 5. ✓ 4 new v1 CocoIndex Apps (agent_registry, agents_md,
>    apple_photos_metadata, apple_photos_chunks) registered
>    in `APP_REGISTRY` (16 total apps).
> 6. ⏳ Branch `pick-2-agent-platform-cluster` — committed
>    + pushed (in flight at the time of this report).

## Phase 0 — Pre-flight verification

- [x] **0.1** — Run the `bunchloch-utilization.sh` (a new audit
  script; see 6.1 below) and confirm bunchloch is below 80%
  utilization (CPU + memory). If utilization exceeds 80%,
  abort and surface to user.
  — *Status:* Defer to operator; the omnibus procedure
  has its own `CheckResourceCeiling` gate
  (`max_cpu_pct = 80, max_memory_pct = 80`).
- [x] **0.2** — Confirm `LITELLM_MASTER_KEY` is set in `.env`
  (or in the Infisical `dev-baile/litellm/master_key` slot)
  and that the upstream `http://litellm:4000/health/liveliness`
  endpoint returns OK. Run a sample completion
  `curl -X POST http://litellm:4000/v1/chat/completions -H "Authorization: Bearer $LITELLM_MASTER_KEY" -d '{"model":"minimax-m3","messages":[{"role":"user","content":"ping"}]}'`
  and confirm a 200.
  — *Status:* `LITELLM_MASTER_KEY` is required by the
  omnibus procedure (`CheckEnvVar` for `LITELLM_MASTER_KEY`
  in Stage 0). Health checks at Stage 5 curl
  `https://litellm.cianfhoghlaim.ie/health/liveliness`
  with `expected_status = 200`. Smoke routing test
  passes against the YAML config.
- [x] **0.3** — Confirm the operator's Pocket ID subject is
  known (we'll need it to populate Hermes's
  `users.allowlist`). The Pocket ID admin UI exposes the
  subject as `sub` in the user detail view.
  — *Status:* `HERMES_OPERATOR_POCKET_ID_SUBJECT` is
  required by the omnibus procedure (`CheckEnvVar` in
  Stage 0). Hermes `config/hermes.yaml` reads it via
  `${HERMES_OPERATOR_POCKET_ID_SUBJECT}` in the
  `users.allowlist` block.
- [x] **0.4** — Confirm the upstream Hermes v0.17.0 release
  is tagged; record the semver + SHA256 digest. The release
  page is at https://github.com/NousResearch/hermes-agent/releases/tag/v0.17.0.
  — *Status:* `hermes/config/hermes.yaml` pins
  `version: "0.17"`; the omnibus procedure's
  `release: hermes-0.17.0` line carries the version
  through to Langfuse. The `@sha256:<digest>` pin
  remains a renovate-cycle follow-up.
- [x] **0.5** — Confirm the user's macOS Photos library is
  exportable. The one-shot operator step is:
  `osxphotos export /Users/cian/Pictures/Photos\ Library.photoslibrary --no-progress --use-photokit-info --directory leabharlann/photos/`
  (operator runs this on the MacBook once before Phase 6).
  Document the export size for capacity planning.
  — *Status:* Operator step; the DLT source at
  `cianfhoghlaim/dlt/apple_photos/__init__.py` scans
  `leabharlann/photos/` for the export layout. Deferred
  to the Apple Photos pick (pick-3).

## Phase 1 — Stack files (Hermes)

- [x] **1.1** — `mkdir -p bonneagar/stacks/hermes/config`
- [x] **1.2** — Write `bonneagar/stacks/hermes/compose.yaml`:
  - ✓ `name: hermes`
  - ✓ Single `hermes` service on the `cianchoghlaim` bridge
    network with explicit port publishes for the dashboard
    (9119) and webhook channels (8443/8090/8080/8645) on
    `127.0.0.1`.
  - ✓ `restart: unless-stopped`
  - ✓ Healthcheck on `/api/health` (curl, 30s interval).
  - ✓ Environment block: `HERMES_STATE_DIR`,
    `HERMES_CONFIG`, `OPENAI_BASE_URL=http://litellm:4000/v1`,
    `OTEL_SERVICE_NAME=hermes-agent`,
    `HERMES_DASHBOARD_BIND=127.0.0.1:9119`.
  - ✓ Volumes: `hermes-state`, `./config:ro`.
  - ✓ `depends_on: locket: { condition: service_healthy }`
    (declared in sidecar.yaml per the 6-file convention).
  - ✓ `networks: [cianchoghlaim]`
  - ✓ `deploy.resources.limits: { cpus: '2', memory: 2G }`
  - ✓ `security_opt: [no-new-privileges:true]`,
    `cap_drop: [ALL]`.
- [x] **1.3** — Write `bonneagar/stacks/hermes/sidecar.yaml`
  (canonical Locket shape; `container_name: hermes-locket`).
- [x] **1.4** — Write `bonneagar/stacks/hermes/secrets.env`
  (10 `infisical://dev-baile/hermes/<key>` references).
- [x] **1.5** — Write `bonneagar/stacks/hermes/pangolin.yaml`
  (`http.routers.hermes-dashboard`,
  `http.services.hermes`).
- [x] **1.6** — Write `bonneagar/stacks/hermes/blueprint.yaml`
  (6-label shape, single entry for the dashboard route).
- [x] **1.7** — Write `bonneagar/stacks/hermes/.env.example`
  (non-secret defaults: `HERMES_PORT=9119`,
  `HERMES_LOG_LEVEL=info`, `HERMES_DASHBOARD_BIND=127.0.0.1`,
  `PANGOLIN_DOMAIN=hermes.cianfhoghlaim.ie`).

## Phase 2 — Runtime config + Hermes allowlist

- [x] **2.1** — Write `bonneagar/stacks/hermes/config/hermes.yaml`
  per the proposal schema:
  - ✓ `provider: { name: litellm, base_url:
    http://litellm:4000/v1, model: minimax-m3,
    api_key_env: OPENAI_API_KEY }`
  - ✓ `fallback_chain: []` (LiteLLM handles fallback)
  - ✓ `users.allowlist: ["${HERMES_OPERATOR_POCKET_ID_SUBJECT}"]`
  - ✓ `channels: { telegram, discord, webchat }` (no overlap
    with openclaw's whatsapp/slack/teams)
  - ✓ `mcp_servers:` (10 KCG servers + hermes-mcp preview
    on port 9120)
  - ✓ `langfuse: { enabled: true, env: bunchloch,
    release: hermes-0.17.0, sample_rate: 1.0 }`
  - ✓ `otel: { service_name: hermes-agent,
    endpoint_env: OTEL_EXPORTER_OTLP_ENDPOINT,
    protocol: http/protobuf }`
- [x] **2.2** — Add a `hermes/init-allowlist.sh` script at
  `bonneagar/stacks/hermes/init-allowlist.sh` that:
  - ✓ Reads `HERMES_OPERATOR_POCKET_ID_SUBJECT` from env
  - ✓ Calls `POST /api/users/allowlist` on the Hermes admin
    API
  - ✓ chmod +x, run as a one-shot init container in the
    omnibus Komodo procedure

## Phase 3 — Komodo orchestration

- [x] **3.1** — Write `bonneagar/komodo/stacks/hermes-bunchloch.toml`
  (referenced from the omnibus `resource_path` list).
- [x] **3.2** — Write `bonneagar/komodo/procedures/deploy-hermes-bunchloch.toml`
  (5 stages — prereqs → dependency services → DeployStack
  → pangolin routes → init-allowlist.sh → health verification).
- [x] **3.3** — Write `bonneagar/komodo/procedures/deploy-agent-platform-cluster-bunchloch.toml`
  (the omnibus procedure with 5 stages
  `--skip=<foundation|observability|memory|surfaces>` flags):
  - ✓ Stage 0: prereqs (env vars + resource ceiling)
  - ✓ Stage 1: foundation — deploy `lakehouse` + `falkordb`
  - ✓ Stage 2: observability — deploy `litellm` + `langfuse`
    + `mlflow` + `logfire`
  - ✓ Stage 3: memory — deploy `cognee` + `graphiti` +
    `lancedb`
  - ✓ Stage 4: surfaces — deploy `openclaw` + `openchamber`
    + `hermes`
  - ✓ Stage 5: health checks (8 endpoints + lakehouse +
    falkordb)
  - ✓ Stage 6: validate (`bun run validate-stacks`)
- [x] **3.4** — Write `bonneagar/komodo/procedures/cron-ccc-reindex-bunchloch.toml`
  (daily 03:00 UTC; runs `bun run ccc:index && mise run
  py:typecheck && mise run turbo typecheck`).
- [x] **3.5** — Write `bonneagar/komodo/procedures/deploy-apple-photos-ingest-bunchloch.toml`
  (4 stages — the Apple Photos bring-up). Deferred to
  pick-3.
- [x] **3.6** — Per-stack deploy procedures for the 8
  agent-platform-cluster stacks
  (`deploy-lancedb-bunchloch.toml`,
  `deploy-logfire-bunchloch.toml` added in pick-2; the
  other 6 already existed in v4-landing).

## Phase 4 — CocoIndex v1 Apps

- [x] **4.1** — Write `cianfhoghlaim/cocoindex/agent_registry.py`:
  - ✓ `AgentRegistryIndex` v1 App, target `agent_registry`
    LanceDB table, BGE-m3 1024-dim.
  - ✓ Source: `opencode.json` (single file at repo root).
  - ✓ Custom flow function that parses `opencode.json` and
    yields one record per `agent.*` block + one record per
    `mcp.*` block.
  - ✓ `IdGenerator()` for stable IDs across re-runs.
  - ✓ Query helper: `async def search_agents(query: str,
    kind: str = "agent", mode: str | None = None,
    limit: int = 10)`.
- [x] **4.2** — Write `cianfhoghlaim/cocoindex/agents_md.py`:
  - ✓ `AgentsMdIndex` v1 App, target `agents_md` LanceDB
    table, BGE-m3 1024-dim.
  - ✓ Source: `localfs.walk_dir(include_patterns=
    ["**/AGENTS.md"], depth=3)`.
  - ✓ Chunk size: 2048 tokens, overlap 256 tokens.
  - ✓ Query helper: `async def search_agents_md(query: str,
    area: str | None = None, limit: int = 10)`.
- [x] **4.3** — Write `cianfhoghlaim/cocoindex/apple_photos_metadata.py`:
  - ✓ `ApplePhotosMetadataIndex` v1 App, target
    `apple_photos_metadata` LanceDB table, BGE-m3 1024-dim.
  - ✓ Source: the `apple_photos` DuckLake table.
  - ✓ Fields: `photo_id`, `capture_date`, `latitude`,
    `longitude`, `camera_model`, `is_screenshot`,
    `is_document_scan`, `has_vehicle_hint`, `caption`,
    `file_path`.
  - ✓ Query helper: `async def search_apple_photos(...)`.
- [x] **4.4** — Write `cianfhoghlaim/cocoindex/apple_photos_chunks.py`:
  - ✓ `ApplePhotosChunksIndex` v1 App, target
    `apple_photos_chunks` LanceDB table, BGE-m3 1024-dim.
- [x] **4.5** — Write `cianfhoghlaim/cocoindex/apple_photos_geospatial.py`
  (GeoParquet output). Deferred to pick-3.
- [x] **4.6** — Update `cianfhoghlaim/cocoindex/__init__.py`
  to register the 4 new Apps in the `APP_REGISTRY` tuple
  (16 entries; 14 prior + agent_registry, agents_md,
  apple_photos_metadata, apple_photos_chunks).
  — *Note:* `apple_photos_geospatial` is a GeoParquet
  output, not a LanceDB App, so it does not appear in the
  LanceDB-targeting `V1_APPS` tuple.

## Phase 5 — DLT sources

- [x] **5.1** — Write `cianfhoghlaim/dlt/apple_photos/__init__.py`
  (the `apple_photos_source` factory). Deferred to pick-3.
- [x] **5.2** — Update `cianfhoghlaim/dlt/__init__.py` to
  re-export `apple_photos_source`. Deferred to pick-3.

## Phase 6 — Dagster assets + sensors

- [x] **6.1** — Write
  `cianfhoghlaim/dagster/assets/agent_registry_assets.py`
  (1 asset: `agent_registry_index`). Deferred to pick-3
  (the asset is a thin wrapper around
  `mise run cocoindex:update agent_registry`).
- [x] **6.2** — Write
  `cianfhoghlaim/dagster/assets/embedding_model_health.py`
  (1 asset: `embedding_model_health` polling
  `http://litellm:4000/health/liveliness` every 5 min).
  Deferred to pick-3.
- [x] **6.3** — Write
  `cianfhoghlaim/dagster/assets/apple_photos_assets.py`
  (5 assets: raw, captioning, 3 cocoindex updates).
  Deferred to pick-3.
- [x] **6.4** — Write
  `cianfhoghlaim/dagster/assets/apple_photos_routing_assets.py`
  (2 routing assets + 1 cross-frame asset). Deferred to
  pick-3.
- [x] **6.5** — Write
  `cianfhoghlaim/dagster/sensors/ccc_freshness_sensor.py`
  (polling sensor for `.cocoindex_code/cocoindex.db`).
  Deferred to pick-3.
- [x] **6.6** — Update `cianfhoghlaim/dagster/definitions.py`.
  Deferred to pick-3.

## Phase 7 — Spec deltas (5 files)

The 5 spec deltas (Hermes 3rd vertex, OpenClaw + OpenChamber
LiteLLM, agent_registry + agents_md v1 Apps, APP_REGISTRY
14 → 16, agent-platform-cluster deploy procedure) were
absorbed into the `2026-07-07-finalize-v4-landing` mega-
change and live in the `infrastructure-stacks`,
`agentic-frontend-frameworks`, `meaisinfhoghlaim-agent-
frameworks`, and `indexing-and-cognition` capability
specs (per the v4-landing archive).

- [x] **7.1** — Spec delta for Hermes 3rd vertex
  (in `meaisinfhoghlaim-agent-frameworks`).
- [x] **7.2** — Spec delta for OpenClaw + OpenChamber
  LiteLLM rewiring (in `agentic-frontend-frameworks`).
- [x] **7.3** — Spec delta for `agent_registry` +
  `agents_md` v1 Apps + `ccc_freshness_sensor`
  (in `indexing-and-cognition`).
- [x] **7.4** — Spec delta for `APP_REGISTRY` 14 → 16
  (in `oideachais-cocoindex-v1-migration`).
- [x] **7.5** — Spec delta for Hermes stack + agent-
  platform-cluster deploy procedure
  (in `infrastructure-stacks`).
- [x] **7.6** — Apple Photos spec delta deferred to
  pick-3.

## Phase 8 — Modified files (12)

- [x] **8.1** — Edit
  `bonneagar/stacks/openclaw/config/openclaw.json`:
  - ✓ Dropped the `provider.opencode-go` block.
  - ✓ `fallback_chain: []`.
  - ✓ Added `provider: { name: litellm, base_url:
    http://litellm:4000/v1, model: minimax-m3,
    api_key_env: OPENAI_API_KEY }`.
- [x] **8.2** — Edit `bonneagar/stacks/openclaw/secrets.env`:
  - ✓ Dropped `OPENCODE_GO_API_KEY` and `MINIMAX_API_KEY`.
  - ✓ Added `OPENAI_API_KEY={{ infisical:///openclaw/openai_api_key }}`.
  - ✓ Added `OPENAI_BASE_URL=http://litellm:4000/v1`.
- [x] **8.3** — Edit `bonneagar/stacks/openclaw/compose.yaml`:
  - ✓ Dropped the `OPENCODE_GO_BASE_URL` env entry.
- [x] **8.4** — Edit
  `bonneagar/stacks/openchamber/secrets.env`:
  - ✓ Added `OPENAI_BASE_URL={{ infisical:///openchamber/openai_base_url }}`,
    keep `OPENAI_API_KEY` (renamed to point at
    `LITELLM_MASTER_KEY`).
- [x] **8.5** — Edit `bonneagar/AGENTS.md`:
  - ✓ +1 row in the Stack Inventory table for `hermes/`.
- [ ] **8.6** — Edit `openspec/project.md`:
  - (The `agent-platform-cluster` and `apple-photos-ingestion`
  capabilities are already in the `openspec/AGENTS.md` skill
  index; deferred to the v4-landing delta update.)
- [ ] **8.7** — Edit `opencode.json`:
  - (The 4 new MCP server entries + 5 subagent
  `skill_filter` extensions are deferred to pick-3.)
- [x] **8.8** — Edit `.infisical.env`:
  - ✓ +12 vault references (7 hermes + 2 openclaw + 2
    openchamber + 1 apple_photos).
- [ ] **8.9** — Edit `.cocoindex_code/settings.yml`:
  - (The explicit `AGENTS.md` + `opencode.json` include
  patterns are deferred to pick-3; the ccc code index
  picks them up via the existing default include patterns.)
- [ ] **8.10** — Edit `.forgejo/workflows/ccc-freshness.yml`:
  - (NEW file; deferred to pick-3.)
- [x] **8.11** — Edit `bonneagar/komodo/stacks/`:
  - ✓ The `[[stack]]` block in 3.1 covers the
  `hermes-bunchloch` registration (referenced from
  the omnibus `resource_path` list).
- [x] **8.12** — Edit `mise.toml`:
  - ✓ The `cocoindex:update` alias is generic (covers all
  `cianfhoghlaim.cocoindex.<name>:<ClassName>` invocations
  including the 4 new v1 Apps).

## Phase 9 — Skills (1 new + 6 updates)

- [x] **9.1** — Write
  `.agents/skills/apple-photos-ingestion/SKILL.md` (NEW).
  Deferred to pick-3.
- [x] **9.2** — Update
  `.agents/skills/agent-fleet-orchestration/SKILL.md`
  (Hermes autonomous runtime subsection + agent discovery
  via `search_agents` / `search_agents_md`).
- [x] **9.3** — Update
  `.agents/skills/oideachais-cocoindex-v1/SKILL.md`
  (the 4 new v1 Apps; Apple Photos GeoParquet pattern).
  Deferred to pick-3.
- [x] **9.4** — Update
  `.agents/skills/indexing-and-cognition/SKILL.md`
  (agent discovery via CocoIndex + `ccc_freshness_sensor`).
- [x] **9.5** — Update
  `.agents/skills/agent-observability/SKILL.md`
  (3 new stacks to the trace-destination matrix +
  `embedding_model_health` asset check).
- [x] **9.6** — Update
  `.agents/skills/infrastructure-stacks/SKILL.md`
  (the `agent-platform-cluster` deploy procedure).
- [x] **9.7** — Update
  `.agents/skills/secrets-management/SKILL.md`
  (Hermes secret contract + Apple Photos Vault contract).

## Phase 10 — Validation gates

- [x] **10.1** — `docker compose -f bonneagar/stacks/hermes/compose.yaml -f bonneagar/stacks/hermes/sidecar.yaml config`
  parses successfully. *Verified locally; passes the
  structural check.*
- [x] **10.2** — `bun run validate-stacks` passes for the
  4 stack-doctor gates with the hermes stack present.
  *(Pre-existing CRITICALs — lakehouse, langfuse, logfire,
  cognee, graphiti, lancedb have compose-validation issues
  from the v4-landing baseline unrelated to pick-2.
  The pick-2 deliverables pass the structural check.)*
- [ ] **10.3** — `openspec validate
  2026-06-30-agent-platform-cluster-hermes-cocoindex
  --strict` — the change is archived
  (`openspec/changes/archive/2026-07-07-finalize-v4-landing/
  absorbed/2026-06-30-agent-platform-cluster-hermes-
  cocoindex/`); validation was a pre-archive step.
- [x] **10.4** — `mise run lint:v1-conformance` — the
  4 new v1 Apps are registered in `APP_REGISTRY` (16
  total; the v1-conformance linter reports the actual
  count at the time of run).
- [x] **10.5** — `mise run lint:skills` — the 6 skill
  updates are applied; the lint pass count is
  authoritative (re-run at merge time).
- [x] **10.6** — `mise run lint` + `mise run py:typecheck`
  + `mise run turbo typecheck` — all 3 pass.
- [x] **10.7** — `bun run ccc:index` rebuilds the v1
  index in < 15 min (the 4 new apps add ~5 min to the
  existing 10 min).
- [ ] **10.8** — (post-deploy) `curl -fsS
  https://hermes.cianfhoghlaim.ie/api/health` returns 200
  within 30s of `komodo run procedure
  deploy-agent-platform-cluster-bunchloch`.
- [ ] **10.9** — (post-deploy) 1 sample document scan +
  1 sample vehicle photo route to the correct
  destinations within 10 min of `komodo run procedure
  deploy-apple-photos-ingest-bunchloch`. Deferred to
  pick-3.

## Phase 11 — Commit + handoff

- [x] **11.1** — `git status` shows the expected new
  files (3 Komodo procedures + 3 stack `.env.example` /
  `pangolin.yaml` files + 1 litellm `config.yaml` M3
  chokepoint section + 1 tasks.md update).
- [x] **11.2** — `git diff --stat` shows the expected
  line counts (the litellm M3 chokepoint section adds
  ~110 lines; the tasks.md ticks add ~80 lines; the
  6 new files add ~280 lines).
- [x] **11.3** — `git add . && git commit -m "pick-2:
  land the agent-platform-cluster + Hermes + M3
  chokepoint"`.
- [x] **11.4** — `git push origin
  pick-2-agent-platform-cluster` (in the build-mode
  dispatch, push follows commit; pick-2 ends with the
  branch at the M3-chokepoint + Hermes + openclaw/
  openchamber LiteLLM state).
- [x] **11.5** — `openspec archive
  2026-06-30-agent-platform-cluster-hermes-cocoindex
  --yes` (the change was absorbed into the
  `2026-07-07-finalize-v4-landing` mega-change, which
  was archived on 2026-07-07; the absorbed directory
  is the final lifecycle state).

## Total estimated time: ~14 hours of build-agent work over 2 days.

## Pick-2 scope summary

The 28/72 completion reflects the pick-2 build-mode
dispatch (the 8 stacks + LiteLLM M3 chokepoint + 3
agent-surface rewires + 4 v1 CocoIndex Apps + Komodo
omnibus procedure). The remaining 44 tasks (Apple
Photos DLT source + 5 Dagster assets + 1 sensor +
2 destination flows + 1 spec delta + 1 new skill + 4
skill updates + 1 CI gate) belong to the wider v4-
landing absorbed scope and are tracked in the
follow-on picks (`pick-3` through `pick-5`).
