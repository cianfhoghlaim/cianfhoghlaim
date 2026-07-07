# Tasks — `2026-06-30-agent-platform-cluster-hermes-cocoindex`

## Phase 0 — Pre-flight verification

- [ ] **0.1** — Run the `bunchloch-utilization.sh` (a new audit
  script; see 6.1 below) and confirm bunchloch is below 80%
  utilization (CPU + memory). If utilization exceeds 80%,
  abort and surface to user.
- [ ] **0.2** — Confirm `LITELLM_MASTER_KEY` is set in `.env`
  (or in the Infisical `dev-baile/litellm/master_key` slot)
  and that the upstream `http://litellm:4000/health/liveliness`
  endpoint returns OK. Run a sample completion
  `curl -X POST http://litellm:4000/v1/chat/completions -H "Authorization: Bearer $LITELLM_MASTER_KEY" -d '{"model":"minimax-m3","messages":[{"role":"user","content":"ping"}]}'`
  and confirm a 200.
- [ ] **0.3** — Confirm the operator's Pocket ID subject is
  known (we'll need it to populate Hermes's
  `users.allowlist`). The Pocket ID admin UI exposes the
  subject as `sub` in the user detail view.
- [ ] **0.4** — Confirm the upstream Hermes v0.17.0 release
  is tagged; record the semver + SHA256 digest. The release
  page is at https://github.com/NousResearch/hermes-agent/releases/tag/v0.17.0.
- [ ] **0.5** — Confirm the user's macOS Photos library is
  exportable. The one-shot operator step is:
  `osxphotos export /Users/cian/Pictures/Photos\ Library.photoslibrary --no-progress --use-photokit-info --directory leabharlann/photos/`
  (operator runs this on the MacBook once before Phase 6).
  Document the export size for capacity planning.

## Phase 1 — Stack files (Hermes)

- [ ] **1.1** — `mkdir -p bonneagar/stacks/hermes/config`
- [ ] **1.2** — Write `bonneagar/stacks/hermes/compose.yaml`:
  - `name: hermes`
  - Single service `hermes` (image pinned to
    `ghcr.io/nousresearch/hermes-agent:0.17.0@sha256:<digest>`,
    `pull_policy: if_not_present`).
  - **`network_mode` is NOT `host`** (the upstream default is
    rewritten to the 6-file GOLD_STANDARD pattern). The
    gateway runs on the `cianchoghlaim` bridge network with
    explicit port publishes:
    - `127.0.0.1:9119:9119` (dashboard, exposed to Pangolin)
    - `127.0.0.1:8443:8443` (Telegram webhook, internal only)
    - `127.0.0.1:8090:8090` (WhatsApp Cloud webhook, internal only)
    - `127.0.0.1:8080:8080` (SMS webhook, internal only)
    - `127.0.0.1:8645:8645` (WeCom/BlueBubbles, internal only)
  - `restart: unless-stopped`
  - Healthcheck: `curl -fs http://localhost:9119/api/health || exit 1`
    (`interval: 30s, timeout: 10s, retries: 3, start_period: 30s`).
  - Environment block: `HERMES_STATE_DIR=/home/hermes/.hermes`,
    `HERMES_CONFIG=/home/hermes/.hermes/config/hermes.yaml`,
    `OPENAI_BASE_URL=http://litellm:4000/v1`,
    `OPENAI_API_KEY` (injected by Locket from
    `LITELLM_MASTER_KEY`), `OTEL_SERVICE_NAME=hermes-agent`,
    `HERMES_DASHBOARD_BIND=127.0.0.1:9119`.
  - Volumes: `hermes-state:/home/hermes/.hermes`,
    `./config:/home/hermes/.hermes/config:ro`.
  - `depends_on: locket: { condition: service_healthy }`
  - `volumes: [stack-secrets:/run/secrets/locket:ro]`,
    `env_file: [/run/secrets/locket/secrets.env]`
  - `networks: [cianchoghlaim]`
  - `deploy.resources.limits: { cpus: '2', memory: 2G }`
  - `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`.
- [ ] **1.3** — Write `bonneagar/stacks/hermes/sidecar.yaml`
  (canonical Locket shape — copy from openclaw/openchamber,
  adjust `container_name: hermes-locket`).
- [ ] **1.4** — Write `bonneagar/stacks/hermes/secrets.env`
  (10 `infisical://dev-baile/hermes/<key>` references):
  - `OPENAI_API_KEY` (LITELLM_MASTER_KEY — note the rename
    from `OPENAI_API_KEY` to `LITELLM_MASTER_KEY` happens at
    the Infisical layer, not the env layer)
  - `OPENAI_BASE_URL=http://litellm:4000/v1`
  - `HERMES_API_SERVER_KEY` (admin token, 32-char random hex)
  - `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`,
    `LANGFUSE_BASE_URL=https://langfuse.cianfhoghlaim.ie`
  - `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`
    (channel credentials)
  - `HERMES_OPERATOR_POCKET_ID_SUBJECT` (the operator's
    Pocket ID subject, for the day-one allowlist)
  - `OTEL_EXPORTER_OTLP_ENDPOINT` (Langfuse OTLP/HTTP)
  - Header comments documenting the `dev-baile` folder
    structure.
- [ ] **1.5** — Write `bonneagar/stacks/hermes/pangolin.yaml`:
  - `http.routers.hermes-dashboard` —
    `Host(\`hermes.cianfhoghlaim.ie\`)`, `service: hermes`,
    `entryPoints: [https]`, `tls.certResolver: letsencrypt`,
    `middlewares: [tinyauth, secure-headers]`.
  - `http.services.hermes.loadBalancer.servers[0].url: "http://hermes:9119"`.
  - No other routes (the webhook ports stay on `127.0.0.1`).
- [ ] **1.6** — Write `bonneagar/stacks/hermes/blueprint.yaml`
  (6-label shape, single entry for the dashboard route;
  mirror `openclaw/blueprint.yaml` template).
- [ ] **1.7** — Write `bonneagar/stacks/hermes/.env.example`:
  - Non-secret defaults: `HERMES_PORT=9119`, `HERMES_LOG_LEVEL=info`,
    `HERMES_DASHBOARD_BIND=127.0.0.1`, `HERMES_USERS_ALLOWLIST_OPERATOR=`,
    `PANGOLIN_DOMAIN=hermes.cianfhoghlaim.ie`.

## Phase 2 — Runtime config + Hermes allowlist

- [ ] **2.1** — Write `bonneagar/stacks/hermes/config/hermes.yaml`
  per the proposal schema:
  - `provider: { name: litellm, base_url: http://litellm:4000/v1, model: minimax-m3, api_key_env: OPENAI_API_KEY }`
  - `fallback_chain: []` (LiteLLM handles fallback internally)
  - `users.allowlist:` — populated from day one with the
    operator's Pocket ID subject (read from
    `HERMES_OPERATOR_POCKET_ID_SUBJECT` env var at container
    start; the deploy procedure has a 1-shot pre-check that
    fails CI if the env var is empty)
  - `channels: { telegram: { enabled: true, token_env: TELEGRAM_BOT_TOKEN, allow_from: [] }, discord: { enabled: true, token_env: DISCORD_BOT_TOKEN, allow_from: [] }, webchat: { enabled: true, bind: 0.0.0.0:9119, allow_from: [] } }`
  - `mcp_servers:` — the canonical 10 KCG MCP servers +
    `hermes-mcp` (Hermes-as-MCP-server, issue #342 preview;
    bound to `0.0.0.0:9120`)
  - `langfuse: { enabled: true, public_key_env: LANGFUSE_PUBLIC_KEY, secret_key_env: LANGFUSE_SECRET_KEY, base_url_env: LANGFUSE_BASE_URL, env: bunchloch, release: hermes-0.17.0, sample_rate: 1.0 }`
  - `otel: { service_name: hermes-agent, endpoint_env: OTEL_EXPORTER_OTLP_ENDPOINT, protocol: http/protobuf }`
- [ ] **2.2** — Add a `hermes/init-allowlist.sh` script at
  `bonneagar/stacks/hermes/init-allowlist.sh` that:
  - Reads `HERMES_OPERATOR_POCKET_ID_SUBJECT` from env
  - Calls `POST /api/users/allowlist` on the Hermes admin
    API with the subject
  - Logs the result to stdout (the deploy procedure
    greps for the success line)
  - The script is `chmod +x` and is run as a one-shot
    init container in the omnibus Komodo procedure.

## Phase 3 — Komodo orchestration

- [ ] **3.1** — Write `bonneagar/komodo/stacks/hermes-bunchloch.toml`:
  - `[[stack]]` block, `name = "hermes"`, `server_id = "bunchloch"`,
    `run_directory = "/etc/komodo/sruth/bonneagar/stacks/hermes"`,
    `file_paths = ["compose.yaml","sidecar.yaml","pangolin.yaml","blueprint.yaml"]`.
  - `tags = ["host:bunchloch","tier:control-plane","type:agent-runtime","domain:hermes.cianfhoghlaim.ie"]`
  - `environment` block: `LOCKET_MODE=watch`,
    `INFISICAL_CLIENT_ID`, `INFISICAL_SECRET_FILE`.
- [ ] **3.2** — Write `bonneagar/komodo/procedures/deploy-hermes-bunchloch.toml`
  (5 stages — mirror `deploy-openclaw-arm1-oci.toml` shape):
  - Stage 0: prereqs (locket volume build, Bunchloch
    utilization check, LITELLM_MASTER_KEY existence).
  - Stage 1: dependency services (`langfuse`, `litellm`,
    `cognee`, `graphiti`).
  - Stage 2: `DeployStack { stack = "hermes" }`.
  - Stage 3: pangolin routes (apply blueprint).
  - Stage 4: `init-allowlist.sh` (add the operator's
    Pocket ID subject to the Hermes `users.allowlist`).
  - Stage 5: health verification —
    `curl -fsS https://hermes.cianfhoghlaim.ie/api/health`
    AND `curl -fsS -H "Authorization: Bearer $HERMES_API_SERVER_KEY" -X POST https://hermes.cianfhoghlaim.ie/api/users/allowlist/test -d '{"subject":"$HERMES_OPERATOR_POCKET_ID_SUBJECT"}'`
    (expect `{"allowed": true}`).
- [ ] **3.3** — Write `bonneagar/komodo/procedures/deploy-agent-platform-cluster-bunchloch.toml`
  (6 stages — the omnibus procedure with
  `--skip=<foundation|observability|memory|surfaces>` flags):
  - Stage 0: prereqs.
  - Stage 1: `foundation` — deploy `lakehouse`.
  - Stage 2: `observability` — deploy `litellm` + `langfuse`
    + `mlflow` + `logfire`.
  - Stage 3: `memory` — deploy `cognee` + `graphiti` +
    `lancedb`.
  - Stage 4: `surfaces` — deploy `openclaw` + `openchamber`
    + `hermes`.
  - Stage 5: health checks (curl `/api/health` on each of
    the 8 stacks + 1 paperless-ngx + 4 OCR stacks).
  - Stage 6: validate (the 4 stack-doctor gates).
- [ ] **3.4** — Write `bonneagar/komodo/procedures/cron-ccc-reindex-bunchloch.toml`:
  - Daily 03:00 UTC on `bunchloch`.
  - Runs `bun run ccc:index && mise run py:typecheck && mise run turbo typecheck`.
  - Posts the result to the `#kcg-indexing` Slack channel
    via the Langfuse webhook.
- [ ] **3.5** — Write `bonneagar/komodo/procedures/deploy-apple-photos-ingest-bunchloch.toml`
  (4 stages — the Apple Photos bring-up):
  - Stage 0: prereqs (the 8-stack cluster is up; the
    `leabharlann/photos/` directory exists from the
    one-shot `osxphotos export`).
  - Stage 1: `dlt run apple_photos_source()` (populates
    the `apple_photos` DuckLake table from the export).
  - Stage 2: `mise run cocoindex:update apple_photos_metadata,
    apple_photos_chunks, apple_photos_geospatial` (populates
    the 3 new v1 Apps in LanceDB).
  - Stage 3: route 1 sample document scan + 1 sample
    vehicle photo to the 2 destinations (paperless-ngx
    + vehicle_observations) as a smoke test.
  - Stage 4: register the 5 new Dagster assets in the
    `apple_photos` group; schedule
    `apple_photos_vehicle_cross_frame` to run weekly at
    04:00 UTC on `bunchloch`.

## Phase 4 — CocoIndex v1 Apps

- [ ] **4.1** — Write `cianfhoghlaim/cocoindex/agent_registry.py`:
  - `AgentRegistryIndex` v1 App, target `agent_registry`
    LanceDB table, BGE-m3 1024-dim.
  - Source: `localfs.read_file("opencode.json")` (single
    file at repo root).
  - Custom flow function that parses `opencode.json` and
    yields one record per `agent.*` block + one record per
    `mcp.*` block.
  - Fields: `kind` ("agent" or "mcp"), `name`, `description`,
    `model`, `mode`, `prompt` (for agents), `command` (for
    mcp), `tags` (comma-joined from opencode.json
    `agent.*.tags`).
  - `IdGenerator()` for stable IDs across re-runs.
  - Query helper: `async def search_agents(query: str,
    kind: str = "agent", mode: str | None = None,
    limit: int = 10)`.
- [ ] **4.2** — Write `cianfhoghlaim/cocoindex/agents_md.py`:
  - `AgentsMdIndex` v1 App, target `agents_md` LanceDB
    table, BGE-m3 1024-dim.
  - Source: `localfs.walk_dir(include_patterns=["**/AGENTS.md"],
    depth=3)` (only the per-area AGENTS.md files, not the
    100+ nested `agents.md` instances in `node_modules`).
  - Chunk size: 2048 tokens, overlap 256 tokens.
  - Fields: `area` ("oideachais" | "meaisinfhoghlaim" |
    "tuatha" | "croilar" | "bonneagar" | "root"),
    `file_path`, `chunk_index`, `text`, `routing_tables`
    (the 4 markdown table blocks extracted as
    serialized JSON).
  - Query helper: `async def search_agents_md(query: str,
    area: str | None = None, limit: int = 10)`.
- [ ] **4.3** — Write `cianfhoghlaim/cocoindex/apple_photos_metadata.py`:
  - `ApplePhotosMetadataIndex` v1 App, target
    `apple_photos_metadata` LanceDB table, BGE-m3 1024-dim.
  - Source: the `apple_photos` DuckLake table (one row
    per photo, 12 columns).
  - Fields: `photo_id`, `capture_date`, `latitude`,
    `longitude`, `camera_model`, `is_screenshot`,
    `is_document_scan`, `has_vehicle_hint`, `caption`
    (filled by the `apple_photos_captioning` asset,
    initially NULL), `file_path`.
  - Query helper: `async def search_apple_photos(query:
    str, bbox: tuple[float, float, float, float] | None = None,
    date_range: tuple[str, str] | None = None, limit: int = 10)`.
- [ ] **4.4** — Write `cianfhoghlaim/cocoindex/apple_photos_chunks.py`:
  - `ApplePhotosChunksIndex` v1 App, target
    `apple_photos_chunks` LanceDB table, BGE-m3 1024-dim.
  - Source: the OCR'd text from document scans + license
    plate reads (one row per OCR chunk).
  - Fields: `photo_id` (FK to `apple_photos_metadata`),
    `chunk_index`, `text`, `ocr_engine` ("paddleocr" |
    "dots-ocr" | "docling-serve"), `confidence` (0-1).
- [ ] **4.5** — Write `cianfhoghlaim/cocoindex/apple_photos_geospatial.py`:
  - `ApplePhotosGeospatialIndex` v1 App, target
    `apple_photos_geospatial` (GeoParquet, not LanceDB).
  - Source: the `apple_photos` DuckLake table.
  - Output: `leabharlann/photos/_derived/all_photos.geo.parquet`
    with a `geometry` column (POINT Z, EPSG:4326).
  - Companion: a second GeoParquet
    `leabharlann/photos/_derived/vehicles.geo.parquet`
    that joins the `vehicle_observations` table.
  - Both files are emitted only when
    `LEABHARLANN_PHOTOS_INCLUDE_GPS=true` is set
    (defaults to false for privacy).
- [ ] **4.6** — Update `cianfhoghlaim/cocoindex/__init__.py` to
  register the 4 new Apps in the `APP_REGISTRY` tuple (13
  → 17 entries).

## Phase 5 — DLT sources

- [ ] **5.1** — Write `cianfhoghlaim/dlt/apple_photos/__init__.py`:
  - `@dlt.source name="apple_photos"` (single resource,
    `apple_photos`).
  - Scans `leabharlann/photos/` for the export layout
    (`originals/<year>/<month>/<day>/<photo>.jpg`).
  - For each photo:
    - Reads the EXIF via `piexif` (GPS, timestamp, camera model)
    - Computes `file_hash` via SHA-256
    - Calls the `docling-serve` stack to determine
      `is_document_scan` (one quick call per photo,
      cached in the DLT pipeline state)
    - Writes a row to the `apple_photos` table
  - `write_disposition="merge"` with `primary_key="photo_id"`
    for incremental updates.
- [ ] **5.2** — Update `cianfhoghlaim/dlt/__init__.py` to
  re-export `apple_photos_source`.

## Phase 6 — Dagster assets + sensors

- [ ] **6.1** — Write `cianfhoghlaim/dagster/assets/agent_registry_assets.py`:
  - 1 asset: `agent_registry_index` (compute kind: `embedding`).
  - Invokes `mise run cocoindex:update agent_registry`
  - `group_name="agent_registry"`.
- [ ] **6.2** — Write `cianfhoghlaim/dagster/assets/embedding_model_health.py`:
  - 1 asset: `embedding_model_health` (compute kind: `monitor`).
  - Polls `http://litellm:4000/health/liveliness` every
    5 min; computes rolling avg latency over the last
    100 completions.
  - Emits a Dagster `AssetCheck` that fails when
    avg latency > 500 ms.
  - `group_name="observability"`.
- [ ] **6.3** — Write `cianfhoghlaim/dagster/assets/apple_photos_assets.py`:
  - 5 assets:
    1. `apple_photos_raw` (compute kind: `dlt`) — invokes
       `dlt run apple_photos_source()`.
    2. `apple_photos_captioning` (compute kind: `vision`)
       — for each new row in `apple_photos`, calls
       `minimax-m3-vision` via LiteLLM to generate a
       1-2 sentence caption.
    3. `apple_photos_cocoindex_metadata_update` (compute
       kind: `embedding`) — invokes
       `mise run cocoindex:update apple_photos_metadata`.
    4. `apple_photos_cocoindex_chunks_update` (compute
       kind: `embedding`) — invokes
       `mise run cocoindex:update apple_photos_chunks`.
    5. `apple_photos_cocoindex_geospatial_update`
       (compute kind: `embedding`) — emits the 2
       GeoParquet files.
  - 1 partition: `apple_photos_batches`
    (DynamicPartitions over the photo_id prefix).
  - 1 schedule: `apple_photos_weekly_recompute`
    (Mondays 04:00 UTC).
- [ ] **6.4** — Write
  `cianfhoghlaim/dagster/assets/apple_photos_routing_assets.py`:
  - 2 assets:
    1. `apple_photos_document_scan_route` (compute kind:
       `ocr`) — for each row in `apple_photos` where
       `is_document_scan = true`, calls
       `docling-serve` to classify, then POSTs to
       `paperless-ngx` with the EXIF as tags.
    2. `apple_photos_vehicle_route` (compute kind:
       `vision`) — for each row in
       `apple_photos` where `has_vehicle_hint = true`,
       calls `paddleocr` for the plate + `dots-ocr` for
       make/model, then writes to the
       `vehicle_observations` DuckLake table.
  - 1 cross-frame asset:
     `apple_photos_vehicle_cross_frame` (compute kind:
     `analytics`, schedule: weekly Sundays 04:00 UTC)
     — joins successive photos of the same `plate_text`
     within 60s; computes `velocity_estimate_mps` from
     GPS delta / time delta; skips pairs where GPS
     delta < 50m or time delta > 120s.
  - `group_name="apple_photos_routing"`.
- [ ] **6.5** — Write `cianfhoghlaim/dagster/sensors/ccc_freshness_sensor.py`:
  - `@sensor` named `ccc_freshness_sensor` (job:
    `codebase_index`).
  - Polls `.cocoindex_code/cocoindex.db` mtime every
    30 min.
  - When the mtime is > 24h old on `main` (or > 7d on
    a release branch), fires a `RunRequest` to re-run
    `codebase_index` + `agent_registry_index` +
    `agents_md_index`.
  - Logs the freshness check to stdout; the
    `embedding_model_health` asset surfaces the
    staleness to Langfuse.
- [ ] **6.6** — Update `cianfhoghlaim/dagster/definitions.py`
  to include the 5 new asset files + 1 new sensor.

## Phase 7 — Spec deltas (5 files)

- [ ] **7.1** — Write
  `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/meaisinfhoghlaim-agent-frameworks/spec.md`
  (ADDED Requirement: `Hermes is a 3rd vertex in the agent-platform group, deployed on bunchloch as a private Pangolin resource at hermes.cianfhoghlaim.ie, using LiteLLM as its canonical LLM gateway and Langfuse as its observability destination`; ADDED Requirement: `Hermes uses 3-layer auth (TinyAuth → Pocket ID SSO → users.allowlist)`; 2 Scenarios each).
- [ ] **7.2** — Write
  `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/agentic-frontend-frameworks/spec.md`
  (ADDED Requirement: `OpenClaw + OpenChamber route LLM calls through LiteLLM`; ADDED Requirement: `opencode-go fallback is removed from openclaw.json`; 2 Scenarios each).
- [ ] **7.3** — Write
  `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/indexing-and-cognition/spec.md`
  (ADDED Requirement: `agent_registry v1 App is the canonical agent discovery surface`; ADDED Requirement: `agents_md v1 App is the canonical AGENTS.md discovery surface`; ADDED Requirement: `ccc_freshness_sensor runs every 30 min and triggers re-index when stale`; ADDED Requirement: `CCC freshness is a hard CI fail on PRs that touch opencode.json or AGENTS.md files`; 2 Scenarios each).
- [ ] **7.4** — Write
  `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/oideachais-cocoindex-v1-migration/spec.md`
  (MODIFIED the "V1 CocoIndex Apps" Requirement to go from 13 → 17 Apps; add `agent_registry`, `agents_md`, `apple_photos_metadata`, `apple_photos_chunks` to the list).
- [ ] **7.5** — Write
  `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/infrastructure-stacks/spec.md`
  (ADDED Requirement: `hermes Stack Directory`; ADDED Requirement: `hermes 3-Layer Auth Contract`; ADDED Requirement: `agent-platform-cluster deploy procedure brings up the 8 stacks in dependency order`; ADDED Requirement: `apple-photos-ingest deploy procedure runs the 4-stage Apple Photos bring-up`; 1 Scenario each).
- [ ] **7.6** — Write
  `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/oideachais-leabharlann/spec.md`
  (ADDED Requirement: `apple_photos dlt source scans the leabharlann/photos/ export`; ADDED Requirement: `apple_photos_metadata + apple_photos_chunks v1 Apps are the canonical Apple Photos discovery surfaces`; ADDED Requirement: `apple_photos_document_scan_route asset routes document scans to paperless-ngx`; ADDED Requirement: `apple_photos_vehicle_route + apple_photos_vehicle_cross_frame assets route vehicle photos to the vehicle_observations table`; 2 Scenarios each).

## Phase 8 — Modified files (12)

- [ ] **8.1** — Edit `bonneagar/stacks/openclaw/config/openclaw.json`:
  - Drop the `provider.opencode-go` block.
  - Drop the `fallback_chain` array (or set to `[]`).
  - Add `provider: { name: litellm, base_url: http://litellm:4000/v1, model: minimax-m3, api_key_env: OPENAI_API_KEY }`.
- [ ] **8.2** — Edit `bonneagar/stacks/openclaw/secrets.env`:
  - Drop `OPENCODE_GO_API_KEY` and `MINIMAX_API_KEY` entries.
  - Add `OPENAI_API_KEY={{ infisical:///litellm/master_key }}`.
  - Add `OPENAI_BASE_URL=http://litellm:4000/v1`.
- [ ] **8.3** — Edit `bonneagar/stacks/openclaw/compose.yaml`:
  - Drop the `OPENCODE_GO_BASE_URL: https://opencode.ai/zen/go/v1`
    line from the `environment:` block.
- [ ] **8.4** — Edit `bonneagar/stacks/openchamber/secrets.env`:
  - Same treatment — add `OPENAI_BASE_URL=http://litellm:4000/v1`,
    keep `OPENAI_API_KEY` (renamed to point at
    `LITELLM_MASTER_KEY`).
- [ ] **8.5** — Edit `bonneagar/AGENTS.md`:
  - +1 row in the Stack Inventory table for `hermes/`.
- [ ] **8.6** — Edit `openspec/project.md`:
  - Add `agent-platform-cluster` and `apple-photos-ingestion`
    to the capability list.
- [ ] **8.7** — Edit `opencode.json`:
  - Add a `mcp.hermes` block pointing at
    `http://hermes:9120` (Hermes-as-MCP-server preview).
  - Add a `mcp.cocoindex-agent-registry` block pointing
    at the new `agent_registry` CocoIndex query helper
    (the helper exposes an MCP-server shim at
    `http://bunchloch:8765/mcp`).
  - Add a `mcp.cocoindex-agents-md` block similarly.
  - Expand each of the 5 sruth-subagent `skill_filter`
    lists to include `apple-photos` (the new skill).
- [ ] **8.8** — Edit `.infisical.env`:
  - +12 vault references:
    - 7 under `hermes/` (api_server_key, langfuse_public_key,
      langfuse_secret_key, langfuse_base_url,
      telegram_bot_token, discord_bot_token,
      operator_pocket_id_subject)
    - 2 under `openclaw/` (rename `OPENCODE_GO_API_KEY` →
      `OPENAI_API_KEY`; add `OPENAI_BASE_URL`)
    - 2 under `openchamber/` (same)
    - 1 under `apple_photos/` (paperless_consumer_token)
- [ ] **8.9** — Edit `.cocoindex_code/settings.yml`:
  - Add explicit include patterns for `AGENTS.md` (root +
    per-area) and `opencode.json` (so the 2 new v1 Apps
    pick them up first).
  - Add explicit include patterns for `leabharlann/photos/`
    (so the 3 new Apple Photos v1 Apps scan the export).
- [ ] **8.10** — Edit `.forgejo/workflows/ccc-freshness.yml`
  (NEW file):
  - GitHub/Forgejo Actions workflow that runs
    `bun run validate-ccc-freshness` on every PR.
  - Hard-fails the PR if the freshness check exits 1
    AND the PR touches `opencode.json` or any
    `**/AGENTS.md` file.
- [ ] **8.11** — Edit `bonneagar/komodo/stacks/` (or create
  the `[[stack]]` block in 3.1).
- [ ] **8.12** — Edit `mise.toml`:
  - Add a `[tasks."cocoindex:update-apple-photos"]` alias
    that runs `uv run cocoindex update
    cianfhoghlaim.cocoindex.apple_photos_metadata:ApplePhotosMetadataIndex`.

## Phase 9 — Skills (1 new + 6 updates)

- [ ] **9.1** — Write `.agents/skills/apple-photos-ingestion/SKILL.md`
  (NEW):
  - 4-component pipeline (DLT source → CocoIndex Apps
    → Dagster assets → 2 destinations).
  - 2 GeoParquet outputs.
  - The HMG-precedent cross-frame velocity inference.
  - The privacy gate (`LEABHARLANN_PHOTOS_INCLUDE_GPS`).
  - The `osxphotos` one-shot export step.
- [ ] **9.2** — Update `.agents/skills/agent-fleet-orchestration/SKILL.md`:
  - Add a "Hermes autonomous runtime" subsection
    (the 3rd vertex; bunchloch host; LiteLLM provider;
    3-layer auth).
  - Update the AGENTS.md-indexing section to mention
    the `search_agents` and `search_agents_md` query
    helpers.
- [ ] **9.3** — Update `.agents/skills/oideachais-cocoindex-v1/SKILL.md`:
  - Document the 4 new v1 Apps (13 → 17 total).
  - Document the Apple Photos GeoParquet pattern.
- [ ] **9.4** — Update `.agents/skills/indexing-and-cognition/SKILL.md`:
  - Add a section on "agent discovery via CocoIndex"
    (the `agent_registry` + `agents_md` pattern).
  - Document the `ccc_freshness_sensor` pattern.
- [ ] **9.5** — Update `.agents/skills/agent-observability/SKILL.md`:
  - Add the 3 new stacks (Hermes, OpenClaw-on-LiteLLM,
    OpenChamber-on-LiteLLM) to the trace-destination
    matrix.
  - Add the `embedding_model_health` asset check.
- [ ] **9.6** — Update `.agents/skills/infrastructure-stacks/SKILL.md`:
  - Add the `agent-platform-cluster` deploy procedure
    to the 5-stage pattern.
  - Add the `apple-photos-ingest` procedure.
- [ ] **9.7** — Update `.agents/skills/secrets-management/SKILL.md`:
  - Add the Hermes secret contract.
  - Add the Apple Photos Vault contract.

## Phase 10 — Validation gates

- [ ] **10.1** — `docker compose -f bonneagar/stacks/hermes/compose.yaml -f bonneagar/stacks/hermes/sidecar.yaml config`
  parses successfully.
- [ ] **10.2** — `bun run validate-stacks` passes all 4
  stack-doctor gates with the hermes stack + Apple Photos
  procedure present.
- [ ] **10.3** — `openspec validate 2026-06-30-agent-platform-cluster-hermes-cocoindex --strict`
  passes — every `### Requirement:` has at least one
  `#### Scenario:`.
- [ ] **10.4** — `mise run lint:v1-conformance` reports
  `17/17 apps passed` (was 13/13).
- [ ] **10.5** — `mise run lint:skills` reports `124/124`
  (was 123, +1 for apple-photos-ingestion).
- [ ] **10.6** — `mise run lint` + `mise run py:typecheck` +
  `mise run turbo typecheck` — all 3 pass.
- [ ] **10.7** — `bun run ccc:index` rebuilds the v1 index
  in < 15 min (the 4 new apps add ~5 min to the
  existing 10 min).
- [ ] **10.8** — (post-deploy) `curl -fsS https://hermes.cianfhoghlaim.ie/api/health`
  returns 200 within 30s of `komodo run procedure
  deploy-agent-platform-cluster-bunchloch`.
- [ ] **10.9** — (post-deploy) 1 sample document scan +
  1 sample vehicle photo route to the correct
  destinations within 10 min of
  `komodo run procedure deploy-apple-photos-ingest-bunchloch`.

## Phase 11 — Commit + handoff

- [ ] **11.1** — `git status` shows the expected 30+ new +
  modified files.
- [ ] **11.2** — `git diff --stat` shows the expected
  line counts.
- [ ] **11.3** — `git add . && git commit -m "feat(agent-platform): add Hermes + 4 v1 CocoIndex Apps + Apple Photos ingest"`.
- [ ] **11.4** — **DO NOT PUSH** without explicit user
  approval. The user will push when ready.
- [ ] **11.5** — `openspec archive 2026-06-30-agent-platform-cluster-hermes-cocoindex --yes`
  (only after the user confirms push + the production
  bring-up succeeds; archive is the final lifecycle step).

## Total estimated time: ~14 hours of build-agent work over 2 days.
