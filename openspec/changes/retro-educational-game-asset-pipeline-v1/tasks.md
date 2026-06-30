# Tasks: retro-educational-game-asset-pipeline-v1

> Six phases. Each phase ends with a validation gate (the box at the
> bottom). Mark a task done with `[x]` only after the listed
> verification has passed.

## Phase 0: Stack updates (mechanical, ~half a day)

The two existing stacks point at the wrong upstream images; the eight
new stacks are all 6-file GOLD_STANDARD follows of
`bonneagar/stacks/invokeai/compose.yaml` plus their own upstream
revision pins.

### Fixed stacks
- [ ] Replace `getcatch/drop` with **`Drop-OSS/drop`** in `bonneagar/stacks/drop/compose.yaml`
- [ ] Replace `nginx:alpine` static export with real **`storybookjs/storybook`** build pipeline in `bonneagar/stacks/storybook/compose.yaml` (serve via Nginx from a rebuilt `storybook-static/`)
- [ ] Regenerate `pangolin.yaml` for both stacks to align with the new upstreams
- [ ] Run `bun run validate-stacks` and confirm 2/2 changed pass

### New GPU stacks (bunchloch M4 Max, sized 2 GB each)
- [ ] Create `bonneagar/stacks/sam3-server/` (6 files) — `facebook/sam3` on `http://sam3:9230/v1/segment`
- [ ] Create `bonneagar/stacks/sam3d-objects-server/` (6 files) — `facebook/sam-3d-objects` on `:9231`
- [ ] Create `bonneagar/stacks/trellis-server/` (6 files) — `microsoft/TRELLIS.2-4B` on `:9232`
- [ ] Create `bonneagar/stacks/fibo-server/` (6 files) — BFL FIBO on `:9233`
- [ ] Create `bonneagar/stacks/comfyui/` (6 files, optional) — `ghcr.io/comfyanonymous/comfyui` on `:9234`

### New headless / CPU stacks
- [ ] Create `bonneagar/stacks/libretro-retroarch/` (6 files) — headless `libretro/retroarch` cores on `:9240`
- [ ] Create `bonneagar/stacks/retroassembly/` (6 files) — `arianrhodsandlot/retroassembly` on `:9241`
- [ ] Create `bonneagar/stacks/pxlkit/` (6 files) — `joangeldelarosa/pxlkit` static export on `:9242`

### Komodo + Pangolin + Infisical glue
- [ ] Add `bonneagar/komodo/procedures/{sam3-server,sam3d-objects-server,trellis-server,fibo-server,comfyui,libretro-retroarch,retroassembly,pxlkit}.toml`
- [ ] Add 6-label Pangolin private resources for each (route + auth + `pangolin.private-resources.<name>.{url,health,admin,ws,storage,cdn}`)
- [ ] Append the 8 new stacks + 2 fixes to `.infisical.env`; run `bun run scripts/init-vault.ts` to materialise the secrets in `dev-baile`
- [ ] `bun run validate-stacks` must remain 88/88 pass after additions

**Phase 0 gate:** `bun run validate-stacks` green; `bun run iac:bootstrap` no errors.

---

## Phase 1: SAM3 + SAM-3D-Objects segmentation in meaisinfhoghlaim (~1 day)

### License + model card + version audit
- [ ] Verify Apache 2.0 (or compatible) licence for `facebook/sam3`
- [ ] Verify Apache 2.0 for `facebook/sam-3d-objects`
- [ ] Pin revisions in `bonneagar/stacks/sam3-server/compose.yaml` (commit SHA not `latest`)
- [ ] Same for `sam3d-objects-server`

### Python wrapper
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/segmentation/__init__.py`
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/segmentation/openai_api.py`
  with the OpenAI-compatible request/response shapes
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/segmentation/sam3.py`
  with `class SAM3Client` and `segment(image, prompts) -> masks`
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/segmentation/sam3d_objects.py`
  with `class SAM3DObjectsClient` and
  `synthesize_3d(mask, image, format) -> glb_path | usdz_path`
- [ ] Add unit tests: mock the HTTP client, assert the request shape

### BAML wrappers
- [ ] Extend `cianfhoghlaim/baml/retro/design_extraction.baml`
  with `function SegmentGameScreenshot(image: Image, prompt: str, ...) -> SegmentationMask`
- [ ] Same file: `function SpriteTo3D(sprite_mask, sprite_image, format) -> str`
- [ ] Run `baml-cli generate` to regenerate the BAML client

### Health check + Langfuse wiring
- [ ] `curl https://sam3.cianfhoghlaim.ie/v1/health` returns 200
- [ ] Same for `sam3d.cianfhoghlaim.ie`
- [ ] Verify the requests land in Langfuse v3 as a trace (per
  `.agents/skills/agent-observability/SKILL.md`)

**Phase 1 gate:** Both SAM services are reachable from `bunchloch`;
`baml-cli generate` compiles clean; ≥1 unit test passes.

---

## Phase 2: Retro game-playing agents (~1 sprint)

### libretro headless setup
- [ ] Pin the 6 libretro cores in `libretro-retroarch/compose.yaml`:
  `mesen` (NES), `snes9x` (SNES), `gambatte` (GB), `mgba` (GBA),
  `genesis_plus_gx` (Genesis), `pcsx_rearmed` (PS1)
- [ ] Wire the `ludusavi` volume mount so save states can be loaded
  via `ludusavi restore`
- [ ] Verify the 3 starting games (Number Munchers, Oregon Trail,
  Carmen Sandiego) are present in the ROMM library + Drop-OSS/drop

### Python playback wrapper
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/playback/__init__.py`
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/playback/save_state.py`
  with `class LudusaviBridge` and `load_state(rom_sha, slot) -> state_path`
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/playback/libretro.py`
  with `class LibretroClient` and
  `play_macro(rom, macro_buttons) -> List[PNG]` capturing one
  frame per major scene transition
- [ ] Add 3 macro scripts to `meaisinfoghlaim/playback/macros/`:
  - `number_munchers_title_to_level1.py`
  - `oregon_trail_title_to_choose_path.py`
  - `carmen_sandiego_title_to_evidence_board.py`

### DLT source
- [ ] Create `cianfhoghlaim/dlt/retro/__init__.py`
- [ ] Create `cianfhoghlaim/dlt/retro/library.py` — yields `retro_library`
  resource from `romm` + `Drop-OSS/drop`
- [ ] Create `cianfhoghlaim/dlt/retro/screenshots.py` — yields
  `retro_screenshots` resource, one row per `scene_id × frame_id`
- [ ] Add unit tests: mock libretro + ludusavi; assert ≥1 screenshot
  yields per game

### Dagster sensor
- [ ] Create `cianfhoghlaim/dagster/sensors/retro_library_watcher.py`
  with a `@sensor` that polls ROMM (`/api/roms`) + Drop-OSS
  (`/api/games`) every 30 min; on new entry materialises
  `retro_screenshots` for that game

**Phase 2 gate:** `retro_screenshots` produces ≥10 screenshots for
each of the 3 starting games; sensor fires on a synthetic new ROMM
event.

---

## Phase 3: Design-pattern extraction (~1 sprint)

### BAML contracts
- [ ] Create `cianfhoghlaim/baml/retro/design_extraction.baml`
- [ ] Define the 4 classes per the proposal (UIPattern,
  SpriteArchetype, PedagogyPattern, GameDesignPattern)
- [ ] Define `class BilingualPatternText { text_en: str | null; text_ga: str | null }`
- [ ] Define `@function ExtractGameDesignPattern(image: Image, game_ctx: GameContext) -> GameDesignPattern`
- [ ] Use the `ExtractEnStrong` client by default + `ExtractGaStrong`
  fallback when `game_ctx.language == "ga"`
- [ ] Run `baml-cli generate`

### CocoIndex v1 flow
- [ ] Create `cianfhoghlaim/cocoindex/retro_design_pattern_embedding.py`
- [ ] Reuse `from ._lifespan import LANCE_DB, EMBEDDER` (per
  REFACTORING.md item 12 enforcement)
- [ ] `@coco.App(refresh_interval=300)` walks
  `stedding/ingest_queue/retro/<platform>/<game>/<scene_id>.png`
- [ ] Yields `{id, game, platform, scene_id, text, embedding, subjects: list[str]}`
- [ ] Run the canonical 4-rule conformance linter via
  `cocoindex_v1_conformance_app`

### DLT source
- [ ] Create `cianfhoghlaim/dlt/retro/design_patterns.py` — yields
  `retro_design_patterns` resource, one row per
  `(game, level_index, scene_id)` with BAML-extracted
  `GameDesignPattern`

### Dagster asset group
- [ ] Create `cianfhoghlaim/dagster/assets/retro_design_patterns.py`
- [ ] 6 assets mirroring the per-subject template:
  `retro_screenshots_raw`, `retro_design_patterns_typed`,
  `retro_design_patterns_validation`, `retro_design_patterns_embedding`,
  `retro_design_patterns_validation_check`,
  `retro_design_patterns_dashboard_link`

**Phase 3 gate:** All 3 starting games produce ≥1 `GameDesignPattern`
per scene; the CocoIndex v1 table `oideachais.retro.design_patterns`
has ≥1 BGE-large-en-v1.5 vector per pattern; `mise run lint:skills`
remains green.

---

## Phase 4: Subject-conditioned asset generation (~2 sprints)

### 2D pipeline (MMO v1)
- [ ] Add 8 BAML function signatures to
  `cianfhoghlaim/baml/retro/asset_prompt_generation.baml`
  (`GenerateChemistryAsset`, `GenerateGeographyAsset`,
  `GenerateMathematicsAsset`, `GenerateHistoryAsset`, … + 4 more)
- [ ] Each function takes `(syllabus_lo: LearningOutcome,
  design_pattern: GameDesignPattern, sprite_mask: SegmentationMask)`
  and returns an
  `AssetPrompt { negative_prompt: str, positive_prompt: str, model: "flux" | "z-image-turbo" | "qwen-image" | "fibo", seed: int }`
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/playback/asset_caller.py`
  with `class AssetGenerationClient` that POSTs to the 4 image-gen
  services (Flux/Z-Image via InvokeAI; Qwen-Image via mlx-omni;
  FIBO via fibo-server)
- [ ] Create `cianfhoghlaim/dlt/retro/asset_generation.py` — yields
  `asset_generation_2d` resource with rows keyed by
  `(subject, syllabus_lo, design_pattern_id)`
- [ ] Create `cianfhoghlaim/dagster/assets/retro_asset_generation.py`
  — 6 assets mirroring the per-subject template
- [ ] Output: `stedding/asset_generation/2d/<subject>/<asset_id>.png`

### 3D pipeline (MMO v2 staging)
- [ ] Add `function SynthesizeAsset3D(...)` to
  `cianfhoghlaim/baml/retro/asset_prompt_generation.baml`
- [ ] Create `cianfhoghlaim/meaisinfhoghlaim/playback/asset_caller_3d.py`
  with `class AssetGenerationClient3D` that POSTs to
  `trellis-server` + `sam3d-objects-server`
- [ ] Create `cianfhoghlaim/dlt/retro/asset_generation_3d.py` —
  yields `asset_generation_3d` resource
- [ ] Output: `s3://cianfhoghlaim-asset-v2/3d/<subject>/<asset_id>.{glb,usdz}`
- [ ] Add a 90-day-lifecycle policy on the bucket (per the Risks section)

### pxlkit + retroassembly integration
- [ ] Add `pixelpack(2d_dir) -> atlas.png` CLI call to
  `meaisinfhoghlaim/playback/asset_caller.py` (calls the `pxlkit`
  stack over HTTP)
- [ ] Add `retroassembly_import(metadata_jsonl) -> status: int` to
  the same module (calls the `retroassembly` stack)

### Atlas delivery
- [ ] Create `stedding/asset_generation/2d/<subject>/atlas.png` per
  subject after every asset-generation materialisation
- [ ] Update `cianfhoghlaim/web/apps/cianfhoghlaim-mmo/src/lib/assets.ts`
  to point at the new atlas URLs
- [ ] Restart the MMO client stack to pick up the new assets

### CocoIndex v1 flow for 2D + 3D
- [ ] Create `cianfhoghlaim/cocoindex/asset_generation_embedding.py`
- [ ] Indexes the `AssetPrompt` text + the asset file SHA-256 +
  subject tags
- [ ] Same pattern as `retro_design_pattern_embedding.py`

**Phase 4 gate:** Subject-conditioned generation produces ≥1 asset
per NCCA subject; the 2D output lands in the MMO client; the 3D
output lives in `s3://cianfhoghlaim-asset-v2/3d/`.

---

## Phase 5: Catalogue + delivery (~1 sprint)

### Marimo dashboard
- [ ] Create `cianfhoghlaim/notebooks/retro_game_design_catalogue.py`
- [ ] Imports the marimo pattern from
  `oideachais-marimo-dashboards/SKILL.md`
- [ ] Renders the design-pattern table + per-pattern sprite thumbnails
  + click-through to the asset generation
- [ ] Add a bilingual EN + GA toggle

### Storybook variant
- [ ] Add a new workspace `packages/game-assets-storybook/` to the
  monorepo
- [ ] Workspace lists the design-pattern categories as sidebar nav
- [ ] Each category renders the pattern + at least 1 generated asset
- [ ] CI rebuilds the static export + the `storybook` stack serves it

### pxlkit + retroassembly backends
- [ ] Wire `meaisinfhoghlaim/playback/asset_caller.py` to upload
  atlases + metadata to `retroassembly` after every materialisation
- [ ] Verify the retroassembly web UI shows the new atlas with
  correct tags (`subject=chemistry`, `design_pattern=...`)

### Subject×design-pattern cross-walk
- [ ] Create `cianfhoghlaim/cocoindex/subject_design_xwalk.py`
- [ ] Generates a per-subject, per-NCCA-LO × design-pattern index
  (one row per "this LO can be illustrated by this design pattern")
- [ ] Wired into both the marimo dashboard and the MMO teacher view

**Phase 5 gate:** The marimo dashboard renders ≥10 design patterns
with thumbnails + bilingual labels; Storybook static export builds
clean; `retroassembly` shows the new atlases.

---

## Phase 6: Hermes cron + Langfuse + MLflow wiring (~2 days)

### Hermes cron
- [ ] Create `hermes/cron/retro_digest.yaml`
- [ ] Schedule: `0 2 * * *` (02:00 UTC daily)
- [ ] Actions: `dagster.materialize(asset=romm_new_entries_sensor)` →
  `dagster.materialize(asset_group=retro_design_patterns)` →
  `dagster.materialize(asset_group=retro_asset_generation)` →
  `langfuse.flush()`
- [ ] Verify Hermes picks up the cron (HAPI endpoint
  `POST /api/crons`)
- [ ] Verify the first nightly run completes without error

### Langfuse traces
- [ ] Add `@observe(name="seg.game_screenshot")` to `SAM3Client.segment`
- [ ] Add `@observe(name="vlm.extract_design_pattern")` to the BAML
  client wrapper
- [ ] Add `@observe(name="gen.2d.flux", …)` +
  `@observe(name="gen.2d.z_image", …)` +
  `@observe(name="gen.2d.fibo", …)` to AssetGenerationClient
- [ ] Add `@observe(name="gen.3d.trellis", …)` +
  `@observe(name="gen.3d.sam3d", …)` to AssetGenerationClient3D
- [ ] Verify all traces land in Langfuse with the correct tag taxonomy

### MLflow experiments
- [ ] Wrap the Flux + Z-Image + Qwen-Image runs as an MLflow
  experiment `retro_asset_generation_2d` with per-asset params
  + metrics (CLIP score, SSIM to source sprite, palette match)
- [ ] Same for the 3D pipeline: experiment `retro_asset_generation_3d`
  with params (TRELLIS.2 cfg, SAM-3D bbox IoU, GLB triangle budget)

### Skill updates
- [ ] Update `.agents/skills/agent-fleet-orchestration/SKILL.md`
  to add a 9th routing slot `retro_design_agent` (default model
  `litellm/anthropic/claude-sonnet-4`)
- [ ] Update `.agents/skills/agentic-frontend-frameworks/SKILL.md`
  with an "Asset CDN delivery" section pointing at
  `s3://cianfhoghlaim-asset-v2/` + `stedding/asset_generation/2d/`
- [ ] Update `.agents/skills/agent-observability/SKILL.md` with the
  5 new trace shapes (SAM3 / VLM / 2D / 3D / cron)
- [ ] Update `.agents/skills/ncca-formative-assessment/SKILL.md`
  with the generated-asset context per quest (per the D-folder
  deliverable)

**Phase 6 gate:** First 02:00 UTC run of `retro_digest` completes;
all 5 trace shapes appear in Langfuse; both MLflow experiments have
≥1 run.

---

## Phase 7: Openspec validation + documentation

- [ ] Run `openspec validate retro-educational-game-asset-pipeline-v1 --strict`
- [ ] Run `mise run lint:skills` — must remain green (currently 123/123)
- [ ] Run `bun run validate-stacks` — must remain 88/88 (10 new + 2
  fixed)
- [ ] Run `bun run turbo typecheck`
- [ ] Run `mise run py:typecheck`
- [ ] Update `docs/ui-inspiration/GAME_DESIGN_CATALOGUE.md`
- [ ] Update `README.md` if the high-level pitch changed

---

## Phase 8: Optional v2 follow-ups (out of scope for v1)

- [ ] NEAT behavioural analysis (Modal) — deferred
- [ ] Babylon.js 3D client consuming `s3://cianfhoghlaim-asset-v2/3d/` — deferred to MMO v2
- [ ] Public HuggingFace Space showcase of the catalogue (reuses
  `.agents/skills/gradio-ensemble-pattern/SKILL.md`)
- [ ] Add more retro games beyond the 3 v1 starters (Number Munchers
  + Oregon Trail + Carmen Sandiego)
