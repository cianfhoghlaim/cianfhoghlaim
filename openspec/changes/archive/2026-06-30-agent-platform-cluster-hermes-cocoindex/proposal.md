# Change: 2026-06-30-agent-platform-cluster-hermes-cocoindex

## Why

The Cianfhoghlaim platform has reached an inflection point. Three
forces are converging on the `agent-platform` group of
`bonneagar/stacks/`, and the existing ad-hoc extensions can no
longer carry the weight.

### 1. The new minimax M3 plan is online — the LLM gateway contract must change

The user has a new, more powerful `minimax-coding-plan` allocation
that enables parallel subagent execution. Today the 3 agent
surfaces (OpenClaw, OpenChamber, and the soon-to-arrive Hermes)
each hard-code their LLM path differently:

- **OpenClaw** — `opencode-go` primary with `minimax-coding-plan` fallback
  (per `bonneagar/stacks/openclaw/config/openclaw.json`).
- **OpenChamber** — bundled `opencode-ai` runtime with 3 hard-coded
  provider keys (OpenAI, Anthropic, minimax).
- **Hermes** (not yet deployed) — would default to its own gateway.

This is 3 different secret contracts, 3 different fallback chains,
3 different rate-limit envelopes, and **3 different ways to exhaust
the new M3 quota**. The M3 plan needs a **single chokepoint**:
the existing `litellm` stack, which already speaks OpenAI-compatible
and can route to M3 + 70+ other models with vendor-derisking.

### 2. The CocoIndex code index is a powerful index, but only the index — not a pipeline

The v1 CocoIndex code App
(`cianfhoghlaim/cocoindex/codebase_indexing.py`) currently indexes
**8,845 source files / 257,957 chunks** in `BAAI/bge-m3` 1024-dim
embeddings, backed by LanceDB. But the index is **only** the
output — there is no:

- **Discovered agent surface** — a way for an agent to ask
  "which of the 7 OpenCode agents handles X?" without grepping
  `opencode.json`. The `opencode.json` `agent.*.prompt` fields
  are 2 KB+ of unstructured prose.
- **AGENTS.md discovery surface** — a way for an agent to ask
  "what's in the root AGENTS.md?" without reading the whole
  20 KB file. The root + 5 per-area AGENTS.md files (oideachais,
  meaisinfhoghlaim, tuatha, croilar, bonneagar) are the
  canonical dispatch contracts but live outside the index.
- **Incremental pipeline** — the index is rebuilt by hand
  (`bun run ccc:index`); there is no Dagster sensor, no
  Komodo cron, and no CI gate that fails on staleness.
- **Re-index trigger on agent-registry changes** — when
  `opencode.json` changes, the index doesn't know to refresh
  the agent surface.

### 3. The agent-platform group needs a third vertex — Hermes

OpenClaw (channel-fanout gateway) and OpenChamber (browser IDE)
are deployed. The user is now adding
[`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent)
as a third vertex: an autonomous long-running agent runtime with
a built-in learning loop, 20+ messaging-platform gateway, MCP-native,
designed as the spiritual successor to OpenClaw but **kept in
parallel** (the user explicitly chose "three separate vertices"
over the upstream's `hermes claw migrate` path).

The Hermes stack needs to:
- Land in the `agent-platform` group on `bunchloch` (MacBook M4
  Max, 32 GB headroom) — not `arm1-oci` (already 70% utilized).
- Route LLM through `litellm` (the M3 chokepoint), not its own
  gateway.
- Expose at `hermes.cianfhoghlaim.ie` via Pangolin TinyAuth.
- Use the same 3-layer auth model as OpenClaw: TinyAuth →
  Pocket ID SSO → `users.allowlist` in `config/hermes.yaml`.
- **NOT** use `network_mode: host` (the upstream default) — must
  fit the 6-file GOLD_STANDARD.

### 4. The personal archive is missing a major corpus — Apple Photos

The existing leabharlann pipeline ingests 4 corpora:
- `ollscoil_na_gaillimhe/` (University of Galway artefacts)
- `gemini_deep_research/` (Gemini deep research PDFs)
- `zotero/` (117 academic papers in real Zotero storage format)
- `gaeilge/` + `aigne/` (books corpus)
- `stedding/Takeout/` (Google Takeout)

There is **no Apple Photos ingest**. The user's iOS/macOS Photos
library contains ~50,000+ photos with two distinct surfaces
that the platform should serve:

- **Document screenshots & scans** — should be OCR'd via the
  existing `docling-serve` / `paddleocr` / `dots-ocr` /
  `olmocr` stacks and routed to `paperless-ngx` for permanent
  archive. (This is the standard "turn a photo of a receipt
  into a searchable document" flow.)
- **License plate / vehicle photos** — the user has an extensive
  collection of vehicles in Galway, Belfast, and London that
  document traffic-law violations. These need:
  - **EXIF extraction** — GPS lat/lon, capture timestamp,
    camera model, focal length
  - **Vehicle classification** — make/model via on-device
    vision-language model (precedent: the user's prior
    HMG government comms project that did offline vehicle
    velocity/acceleration inference from successive photos)
  - **License plate OCR** — `paddleocr` is the natural fit
  - **Cross-frame analysis** — successive photos of the same
    vehicle can derive velocity/acceleration if the timestamps
    and GPS deltas are tight enough
  - **Geospatial indexing** — fold into the existing
    `geospatial_indexing` v1 App for "find me all photos
    taken within 200m of X at time T"

## What Changes

This omnibus change adds the 3rd agent vertex (Hermes), the
3rd indexing dimension (agent discovery + AGENTS.md surface),
the LiteLLM chokepoint, and the 5th leabharlann corpus
(Apple Photos) in a single coherent change because all 4
share the same new M3 + LiteLLM + Bunchloch host contract.

### 1. New Docker Compose stack `bonneagar/stacks/hermes/`

Hermes Agent v0.17.0 as a 3rd vertex in the `agent-platform`
group, deployed on `bunchloch` (not `arm1-oci`).

- **6-file GOLD_STANDARD** at `bonneagar/stacks/hermes/`:
  `compose.yaml` + `sidecar.yaml` + `secrets.env` +
  `pangolin.yaml` + `blueprint.yaml` + `.env.example` + `README.md`.
- **Runtime config** at
  `bonneagar/stacks/hermes/config/hermes.yaml`:
  - `provider: litellm` (chokepoint, not opencode-go)
  - `model: minimax-m3` (the new M3 plan)
  - `users.allowlist:` populated from day one with the
    operator's Pocket ID subject (user answered Q2: "from day one")
  - `channels:` — Telegram + Discord + WebChat enabled in v1
    (OpenClaw keeps WhatsApp/Slack/Teams; **no channel overlap**)
  - `mcp_servers:` — the canonical 10 KCG MCP servers +
    `hermes-mcp` (Hermes-as-MCP-server, issue #342 preview)
  - `langfuse:` — full observability wiring
- **Network model rewrite** — the upstream
  `network_mode: host` is rewritten to explicit published ports
  on the `cianfhoghlaim` bridge network. Dashboard binds
  `127.0.0.1:9119`; webhook ports (Telegram 8443, etc.) stay
  on `127.0.0.1` only.
- **3-layer auth:**
  1. Pangolin TinyAuth (Pocket ID OIDC) at Traefik
  2. `users.allowlist` in `config/hermes.yaml` — empty by
     default; populated at deploy time with the operator's
     Pocket ID subject
  3. `channels.<name>.allow_from` per channel

### 2. Two new CocoIndex v1 Apps for agent discovery

**`agent_registry`** v1 App at
`cianfhoghlaim/cocoindex/agent_registry.py`:
- Indexes the 7 `opencode.json` `agent.*` blocks (description +
  model + mode + prompt) + the 10 `mcp.*` server blocks into
  a new `agent_registry` LanceDB table.
- Embeds with BGE-m3 1024-dim (consistent with the other
  13 v1 Apps).
- Query helper: `await search_agents(query, mode="subagent",
  limit=10)` — returns ranked agent matches.
- Companion Dagster asset: `agent_registry_index` in
  `cianfhoghlaim/dagster/assets/agent_registry_assets.py`.

**`agents_md`** v1 App at
`cianfhoghlaim/cocoindex/agents_md.py`:
- Indexes the root `AGENTS.md` + the 5 per-area AGENTS.md
  files (oideachais, meaisinfhoghlaim, tuatha, croilar,
  bonneagar) into a new `agents_md` LanceDB table with
  2048-token chunks + 256-token overlap.
- Embeds with BGE-m3 1024-dim.
- Query helper: `await search_agents_md(query, area="infrastructure",
  limit=10)`.
- Companion Dagster asset: `agents_md_index`.

This brings the v1 App count from 13 → **15** (the canonical
`APP_REGISTRY` at `cianfhoghlaim/cocoindex/__init__.py`).

### 3. Incremental CocoIndex re-indexing pipeline

3 new components:

- **Dagster sensor** at
  `cianfhoghlaim/dagster/sensors/ccc_freshness_sensor.py` —
  polls `.cocoindex_code/cocoindex.db` mtime every 30 min and
  fires re-runs of `codebase_index`, `agent_registry_index`,
  and `agents_md_index` when stale (> 24h on main, > 7d on
  release branches).
- **Komodo cron procedure** at
  `bonneagar/komodo/procedures/cron-ccc-reindex.toml` — runs
  `bun run ccc:index && mise run py:typecheck && mise run turbo typecheck`
  daily at 03:00 UTC on `bunchloch` as a backstop.
- **CI gate tightening** in
  `.forgejo/workflows/ccc-freshness.yml` (NEW) — the existing
  `bun run validate-ccc-freshness` becomes a **hard fail**
  (not just a warning) on PRs that touch `opencode.json` or
  any `AGENTS.md` file.

Plus a new Dagster asset `embedding_model_health` at
`cianfhoghlaim/dagster/assets/embedding_model_health.py`
that polls the LiteLLM `/health` endpoint and emits a Dagster
asset check that fails when the M3 embedder's avg latency
> 500 ms. (Note: CocoIndex code embeddings stay on BGE-m3 —
M3 is the LLM, not the embedder. The asset check is just a
LiteLLM-up guardrail.)

### 4. OpenClaw + OpenChamber LLM rewiring to LiteLLM

**`openclaw/config/openclaw.json`:**
- Drop the `opencode-go` provider and the `opencode-go` fallback
  chain entry entirely (per user answer to Q5: "remove").
- `provider: { name: litellm, base_url: http://litellm:4000/v1,
  model: minimax-m3, api_key_env: OPENAI_API_KEY }`.
- `fallback_chain: []` (LiteLLM handles fallback internally to
  its 70+ model routing).

**`openclaw/secrets.env`:**
- Drop `OPENCODE_GO_API_KEY` and `MINIMAX_API_KEY` entries.
- Add `OPENAI_API_KEY={{ infisical:///litellm/master_key }}` and
  `OPENAI_BASE_URL=http://litellm:4000/v1`.

**`openclaw/compose.yaml`:**
- Drop the `OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1`
  env entry (now set in `secrets.env` via Locket).

**`openchamber/secrets.env`:**
- Same treatment — drop bare provider keys, add
  `OPENAI_BASE_URL=http://litellm:4000/v1`.

**`openchamber/config`:** (bundled runtime provider picker)
- Add a 4th provider entry "litellm" with base URL
  `http://litellm:4000/v1` and `models: [minimax-m3]`.

### 5. Adjacent stack pull-in — the agent-platform cluster

The 8 stacks that get wired into the deploy graph alongside
Hermes + OpenClaw + OpenChamber. All 8 already exist in
`bonneagar/stacks/`; the work is a single omnibus Komodo
procedure that orders the 8-stack bring-up.

| Stack | Port | Role in the cluster |
|:--|--:|:--|
| `litellm` | 4000 | Canonical LLM gateway for M3 + 70+ models |
| `langfuse` | 3000 | LLM observability + traces for the 3 new stacks |
| `mlflow` | 8080 | Experiment tracking + fine-tune lineage |
| `logfire` | (OTLP only) | Python-level structured tracing |
| `cognee` | 8000 | Knowledge graph memory (7 typed clusters) |
| `graphiti` | 8080 | Bi-temporal knowledge graph |
| `lancedb` | (local) | Vector storage for the 15 v1 CocoIndex Apps |
| `lakehouse` | 3900-3904 | Garage S3 + Postgres + Lakekeeper (data plane) |

**Komodo deploy ordering** (the new procedure
`deploy-agent-platform-cluster-bunchloch.toml` with
`--skip=<foundation|observability|memory|surfaces>` flags):

1. **Stage 0 — pre-reqs:** Pangolin mesh healthy, Pocket ID
   SSO reachable, Infisical `dev-baile` reachable, Bunchloch
   resource ceiling check (< 80% utilized).
2. **Stage 1 — `foundation`:** Deploy `lakehouse` (Garage S3
   must exist before litellm can store its logs).
3. **Stage 2 — `observability`:** Deploy `litellm` + `langfuse`
   + `mlflow` + `logfire` (OpenClaw/OpenChamber/Hermes cannot
   start without litellm; langfuse/mlflow/logfire are
   observability consumers of those 3 surfaces).
4. **Stage 3 — `memory`:** Deploy `cognee` + `graphiti` +
   `lancedb` (the v1 CocoIndex Apps write to lancedb; cognee
   is the doc knowledge graph; graphiti is the temporal
   knowledge graph).
5. **Stage 4 — `surfaces`:** Deploy `openclaw` + `openchamber`
   + `hermes` (the 3 agent surfaces).
6. **Stage 5 — health checks:** `curl /api/health` on each,
   `litellm/health`, `langfuse/api/public/health`,
   `cognee/health`. The 8 stack-doctor gates
   (`bun run validate-stacks`) must all pass.

### 6. Apple Photos ingestion — the 5th leabharlann corpus

This is the new Workstream F that the user added in the
"now proceed with your plan" message. It introduces a 5th
leabharlann corpus with two distinct destination flows.

#### 6.1 New DLT source

**`apple_photos`** at
`cianfhoghlaim/dlt/apple_photos/__init__.py`:
- `@dlt.source name="apple_photos"`, single resource.
- Scans `leabharlann/photos/` (the user's exported
  `Photos Library.photoslibrary` directory, after running
  `osxphotos export` once on the MacBook).
- 7 columns: `photo_id` (Apple's UUID), `capture_date`,
  `latitude`, `longitude`, `camera_model`, `width`, `height`,
  `file_path`, `file_hash` (SHA-256), `is_screenshot`,
  `is_document_scan`, `has_vehicle_hint` (YOLO-v8 quick
  pass via `docling-serve` for `is_document_scan`).
- Auto-detects the `.photoslibrary` directory structure
  (`originals/`, `resources/`, `Masters/`, `thumbnails/`).

#### 6.2 Two new CocoIndex v1 Apps

**`apple_photos_metadata`** v1 App at
`cianfhoghlaim/cocoindex/apple_photos_metadata.py`:
- Indexes the 12-column metadata rows (without the image
  bytes) for fast "find photos taken at GPS X between
  time T1 and T2" queries.
- Embeds the `caption` column (filled in by the
  `apple_photos_captioning` Dagster asset, see below) with
  BGE-m3 1024-dim.
- Companion Dagster asset.

**`apple_photos_chunks`** v1 App at
`cianfhoghlaim/cocoindex/apple_photos_chunks.py`:
- Indexes the OCR'd text from document scans + license
  plate reads for semantic search.
- Embeds with BGE-m3 1024-dim.
- Companion Dagster asset.

This brings the v1 App count from 15 → **17** (per the
`oideachais-cocoindex-v1-migration` spec's APP_REGISTRY).

#### 6.3 The 2 destination flows

**Destination A: document scans → paperless-ngx**

- Dagster asset `apple_photos_document_scan_route` polls
  the `apple_photos_metadata` table for rows where
  `is_document_scan = true`.
- For each match, calls the `docling-serve` stack
  (`http://docling-serve:5001/v1/convert/file`) to OCR +
  classify the document (invoice / receipt / letter / form).
- Posts the result to the `paperless-ngx` stack
  (`http://paperless-ngx:8000/api/documents/post_document/`)
  with the original photo as the source PDF, the OCR'd
  text as the body, and the EXIF GPS + timestamp as
  metadata tags.
- Marks the row as `routed_to_paperless_at` to avoid
  re-routing on subsequent re-runs.

**Destination B: vehicle photos → vehicle catalog**

- Dagster asset `apple_photos_vehicle_route` polls the
  `apple_photos_metadata` table for rows where
  `has_vehicle_hint = true`.
- For each match, calls:
  - `paddleocr` (port 5000) for license plate OCR
  - `dots-ocr` (port 5000) for vehicle make/model
    classification (VLM fallback for ambiguous cases)
  - The on-device `minimax-m3-vision` model via LiteLLM
    for captioning
- Writes a row to the new `vehicle_observations` table in
  DuckLake:
  - `photo_id` (FK to apple_photos)
  - `plate_text` (the OCR'd plate)
  - `vehicle_make`, `vehicle_model`, `vehicle_colour`
  - `latitude`, `longitude`, `capture_date`
  - `velocity_estimate_mps` (NULL for single photos;
    populated by the cross-frame analysis asset below)
- Companion Dagster asset: `apple_photos_vehicle_cross_frame`
  joins successive photos of the same `plate_text` within
  60 seconds and computes velocity from GPS delta /
  time delta. (Precedent: the user's prior HMG government
  comms project that did offline vehicle velocity /
  acceleration inference from successive photos.)

#### 6.4 The 2 GeoParquet outputs

- `geospatial_indexing` v1 App gains a new "vehicle
  observations" branch that emits a GeoParquet file
  at `leabharlann/photos/_derived/vehicles.geo.parquet`
  with the `vehicle_observations` rows + a `geometry`
  column (POINT Z) for QGIS / marimo visualisation.
- `apple_photos_geospatial` v1 App at
  `cianfhoghlaim/cocoindex/apple_photos_geospatial.py`
  emits a second GeoParquet at
  `leabharlann/photos/_derived/all_photos.geo.parquet`
  with all photos + their EXIF GPS for the "show me
  every photo I took in Galway in 2024" query.

#### 6.5 Spec delta to `oideachais-leabharlann`

A 5th `### Requirement:` block is added to the
`oideachais-leabharlann` spec:

- `apple_photos` dlt source
- `apple_photos_metadata` + `apple_photos_chunks` v1 Apps
- `apple_photos_document_scan_route` asset routes to
  paperless-ngx
- `apple_photos_vehicle_route` + cross-frame asset
  routes to the `vehicle_observations` table
- 2 GeoParquet outputs

## Impact

### Affected specs (5 deltas, 0 new specs)

- **MODIFIED `meaisinfhoghlaim-agent-frameworks`** — Hermes
  is a 3rd vertex in the agent-platform group, with
  3-layer auth, LiteLLM chokepoint, and the `hermes-mcp`
  preview. The 12-agent fleet expands to 13 (12 + 1 root
  Hermes orchestrator).
- **MODIFIED `agentic-frontend-frameworks`** — OpenClaw +
  OpenChamber both route LLM through LiteLLM (no more
  opencode-go). The provider chain is simplified.
- **MODIFIED `indexing-and-cognition`** — 2 new v1 Apps
  (`agent_registry`, `agents_md`) + 1 new Dagster sensor
  (`ccc_freshness_sensor`) + 1 new CI gate + 1 new
  `embedding_model_health` asset check.
- **MODIFIED `oideachais-cocoindex-v1-migration`** — APP_REGISTRY
  goes from 13 → 17 v1 Apps (the 2 new agent-discovery
  apps + the 2 new Apple Photos apps).
- **MODIFIED `infrastructure-stacks`** — the Hermes stack
  + the agent-platform-cluster deploy procedure + the
  Apple Photos ingest procedure.
- **MODIFIED `oideachais-leabharlann`** — the 5th corpus
  (Apple Photos) with 2 destination flows.

### NEW files (~25)

**Hermes stack (`bonneagar/stacks/hermes/`):**
- `compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`,
  `blueprint.yaml`, `.env.example`, `README.md`
- `config/hermes.yaml`

**CocoIndex v1 Apps (`cianfhoghlaim/cocoindex/`):**
- `agent_registry.py`
- `agents_md.py`
- `apple_photos_metadata.py`
- `apple_photos_chunks.py`
- `apple_photos_geospatial.py` (GeoParquet output)

**DLT sources (`cianfhoghlaim/dlt/apple_photos/`):**
- `__init__.py` (the `apple_photos_source` factory)

**Dagster assets (`cianfhoghlaim/dagster/assets/`):**
- `agent_registry_assets.py`
- `apple_photos_assets.py` (the 5 assets: raw, scan_route,
  vehicle_route, cross_frame, geospatial)
- `embedding_model_health.py`

**Dagster sensors (`cianfhoghlaim/dagster/sensors/`):**
- `ccc_freshness_sensor.py`

**Komodo procedures (`bonneagar/komodo/procedures/`):**
- `deploy-hermes-bunchloch.toml`
- `deploy-agent-platform-cluster-bunchloch.toml`
- `deploy-apple-photos-ingest-bunchloch.toml`
- `cron-ccc-reindex-bunchloch.toml`

**Komodo stack (`bonneagar/komodo/stacks/`):**
- `hermes-bunchloch.toml`

**CI workflow:**
- `.forgejo/workflows/ccc-freshness.yml`

### MODIFIED files (~12)

- `bonneagar/stacks/openclaw/config/openclaw.json` — drop
  opencode-go provider + fallback
- `bonneagar/stacks/openclaw/secrets.env` — drop 2 keys,
  add `OPENAI_BASE_URL` + `OPENAI_API_KEY`
- `bonneagar/stacks/openclaw/compose.yaml` — drop
  `OPENCODE_GO_BASE_URL` env
- `bonneagar/stacks/openchamber/secrets.env` — same
  LiteLLM treatment
- `bonneagar/AGENTS.md` — +1 row in Stack Inventory
- `openspec/project.md` — 2 new capabilities in the list
- `opencode.json` — add `hermes` MCP server; add
  `agent_registry` + `agents_md` MCP servers; expand
  the 5 subagent `skill_filter` lists with
  `apple-photos` skill
- `.infisical.env` — +12 vault references
- `.cocoindex_code/settings.yml` — explicit
  `AGENTS.md` + `opencode.json` include patterns
- 6 affected skill SKILL.md files (see below)

### Affected skills (6 updated, 0 new)

- `.agents/skills/agent-fleet-orchestration/SKILL.md` —
  add a "Hermes autonomous runtime" subsection; add the
  `agent_registry` / `agents_md` query helpers in the
  existing AGENTS.md-indexing section
- `.agents/skills/oideachais-cocoindex-v1/SKILL.md` —
  document the 4 new v1 Apps (13 → 17 total); document
  the Apple Photos GeoParquet pattern
- `.agents/skills/indexing-and-cognition/SKILL.md` (and
  `INDEXING_AND_COGNITION.md` if it exists) — add a
  section on "agent discovery via CocoIndex"
- `.agents/skills/agent-observability/SKILL.md` — add
  the 3 new stacks (Hermes, OpenClaw-on-LiteLLM,
  OpenChamber-on-LiteLLM) to the trace-destination matrix
- `.agents/skills/infrastructure-stacks/SKILL.md` — add
  the `agent-platform-cluster` deploy procedure to the
  5-stage pattern
- `.agents/skills/secrets-management/SKILL.md` — add the
  Hermes secret contract + the Apple Photos Vault
  contract

### NEW skills (1)

- `.agents/skills/apple-photos-ingestion/SKILL.md` —
  the 4-component pipeline (DLT source → CocoIndex Apps
  → Dagster assets → 2 destinations); the 2 GeoParquet
  outputs; the HMG-precedent cross-frame velocity
  inference.

### Affected CI

- `bun run validate-stacks` — 89th stack (hermes) must
  pass; the Apple Photos procedure must pass.
- `mise run lint:v1-conformance` — must report
  `17/17 apps passed` (was 13/13).
- `mise run lint:skills` — must report `124/124` (was
  123, +1 for the new apple-photos-ingestion skill).
- `openspec validate 2026-06-30-agent-platform-cluster-hermes-cocoindex --strict` —
  must pass.

## Non-Goals

- This change does **not** migrate OpenClaw → Hermes. The
  upstream `hermes claw migrate` command is left for a
  follow-up change. v1 ships Hermes as a *3rd vertex*.
- This change does **not** deploy Hermes on `arm1-oci`.
  Hermes goes to `bunchloch` (MacBook M4 Max, 32 GB
  headroom) per the user's explicit Q1 answer.
- This change does **not** provision Signal / iMessage /
  Matrix channels for Hermes. Those stay disabled per the
  same constraint OpenClaw ships with.
- This change does **not** rewrite any existing v1 CocoIndex
  App. The 13 existing Apps are untouched; this change adds
  4 new Apps and 1 new sensor.
- This change does **not** add a new LLM provider to the
  OpenCode runtime. LiteLLM is the chokepoint.
- This change does **not** add a public-domain route.
  `hermes.cianfhoghlaim.ie` is private (Pocket ID SSO via
  TinyAuth).
- This change does **not** run the actual Apple Photos
  export from the MacBook Photos library. That export step
  (`osxphotos export /Users/.../Pictures/Photos\ Library.photoslibrary
  --no-progress --use-photokit-info --directory
  leabharlann/photos/`) is a one-shot operator action that
  produces the `leabharlann/photos/` directory the DLT
  source scans.
- This change does **not** run the actual cross-frame
  velocity analysis at deploy time. The cross-frame
  `apple_photos_vehicle_cross_frame` Dagster asset is
  scheduled to run weekly at 04:00 UTC on `bunchloch` and
  only over photos with `capture_date > NOW() - 90 days`
  (sliding window).
- This change does **not** add new model backends to the
  on-device vehicle inference. The 3 backends
  (`paddleocr` for plates, `dots-ocr` for VLM
  classification, `minimax-m3-vision` for captioning) all
  already exist as separate stacks.
- This change does **not** add Apple iCloud API access.
  All ingestion is from a local export, not the cloud.

## Risk Assessment

- **Risk: bunchloch resource ceiling.** 1 new agent surface
  (Hermes, 2 GB / 2 CPU) + 1 new Dagster sensor + 1 new
  embedding_model_health asset + 1 new Apple Photos
  pipeline (5 assets) ≈ 4 GB memory + 3 CPU. bunchloch
  is at ~50% utilization; the math fits. **Mitigation:**
  pre-flight `bunchloch-utilization.sh` check in the
  omnibus procedure; abort + alert if > 80%.
- **Risk: LiteLLM as a single point of failure.** 3 new
  surfaces (Hermes + the rewritten openclaw/openchamber)
  all depend on `litellm:4000`. **Mitigation:** the
  litellm stack has its own observability + circuit
  breaker; the `embedding_model_health` asset check
  catches sustained outages within 5 minutes; the Komodo
  procedure has a `--skip=litellm` flag for fallback to
  the prior `opencode-go` path (we keep that key in
  Infisical as a 1-command rollback).
- **Risk: Hermes `users.allowlist` initial state.** The
  user answered "from day one" — populated with the
  operator's Pocket ID subject at deploy time. **Mitigation:**
  the deploy procedure's last stage prints a
  `curl /api/whoami` test; if the response doesn't include
  the operator's subject, the deploy fails CI.
- **Risk: Apple Photos library size.** A typical
  MacBook Photos library is 30-100 GB; the DLT source
  needs to be incremental. **Mitigation:** the source
  uses `file_hash` (SHA-256) as the merge key and the
  `apple_photos_metadata` v1 App respects
  `detect_change=True` on the file path. Re-runs only
  process new/modified files.
- **Risk: Apple Photos privacy.** The library contains
  personal photos. **Mitigation:** the
  `apple_photos_geospatial` v1 App's GeoParquet output
  is gated behind a `--include-gps` flag that defaults
  to `false`; the paperless-ngx destination
  automatically tags documents with `personal:
  do-not-share`; the `vehicle_observations` table is
  scoped to the user's Pocket ID subject only.
- **Risk: `network_mode: host` rewrite breaks the
  gateway.** **Mitigation:** the Hermes compose file
  keeps the gateway inside the `cianfhoghlaim` bridge
  network; the webhook ports (Telegram 8443, etc.)
  bind to `127.0.0.1` only; the dashboard binds
  `127.0.0.1:9119`. Documented in the Hermes README
  with a "If you see webhook timeouts, check that
  Pocket ID returned a fresh OIDC session" note.
- **Risk: cross-frame vehicle inference accuracy.**
  Single-photo velocity estimates from
  successive photos are inherently noisy (the user
  flagged this from prior HMG experience). **Mitigation:**
  the `apple_photos_vehicle_cross_frame` asset writes
  the velocity estimate as `NULL` for any photo pair
  where the GPS delta < 50m OR the time delta > 120s
  (configurable thresholds); the marimo notebook for
  vehicle observations surfaces a "Low confidence"
  badge for these cases.
- **Risk: AGENTS.md churn causes infinite re-indexing
  loops.** **Mitigation:** the `ccc_freshness_sensor`
  only fires when the indexed asset group's mtime >
  24h, not on every commit. The Komodo cron is the
  backstop (daily 03:00 UTC).

## Validation

1. `docker compose -f bonneagar/stacks/hermes/compose.yaml -f bonneagar/stacks/hermes/sidecar.yaml config`
   parses successfully.
2. `bun run validate-stacks` passes all 4 stack-doctor
   gates with the hermes stack + Apple Photos procedure
   present.
3. `openspec validate 2026-06-30-agent-platform-cluster-hermes-cocoindex --strict` —
   every `### Requirement:` has at least one
   `#### Scenario:`.
4. `mise run lint:v1-conformance` reports
   `17/17 apps passed` (was 13/13).
5. `mise run lint:skills` reports `124/124` (was 123).
6. `bun run ccc:index` rebuilds the v1 index in
   < 15 min (was 10 min; the 4 new apps add ~5 min).
7. Post-deploy: `curl -fsS https://hermes.cianfhoghlaim.ie/api/health`
   returns 200 within 30s of `komodo run procedure
   deploy-agent-platform-cluster-bunchloch`.
8. Post-deploy: `osxphotos export` → `leabharlann/photos/`
   → `dlt run apple_photos` yields > 0 rows; the
   `apple_photos_metadata` v1 App's `search_apple_photos("Galway", limit=5)`
   returns the most recent 5 photos taken in Galway
   with their EXIF GPS.
9. Post-deploy: 1 sample document scan photo + 1
   sample vehicle photo each route to the correct
   destination (paperless-ngx + vehicle_observations
   table) within 10 min of `dlt run apple_photos`.

## References

- **Hermes upstream:** [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) — MIT, v0.17.0 (2026-06-19), Python 81.9%, 206k stars
- **Hermes docs:** https://hermes-agent.nousresearch.com/docs/
- **Hermes migration path (NOT used in v1):**
  [hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw](https://hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw)
- **Apple Photos export:** `osxphotos` Python library (MIT)
  by Rhet Turnbull — https://github.com/RhetTbull/osxphotos
- **EXIF extraction:** `exiftool` (Artistic License 2.0) +
  `piexif` (MIT) Python wrapper
- **Vehicle classification:** on-device `minimax-m3-vision`
  (already deployed via `llama-swap`); the HMG-precedent
  velocity/acceleration inference lives in the user's
  prior `gov-comms-vehicle-pipeline` repo (out of scope
  to re-host here; the pattern is mirrored)
- **Existing leabharlann pattern:** `openspec/changes/archive/2026-06-16-leabharlann-cocoindex-v1/proposal.md`
- **Existing openclaw pattern:** `openspec/changes/add-openclaw-stack-and-channel-fanout/proposal.md`
- **Existing openchamber pattern:** `openspec/changes/add-openchamber-stack-and-opencode-ui/proposal.md`
