# retro-educational-game-asset-pipeline-v1 — Retro Educational Game Asset Generation Pipeline (2D + 3D in parallel)

## Why

The Cianfhoghlaim Educational MMO today ingests NCCA leaving-cert syllabus +
past-paper PDFs through the canonical 6-stage `pdf_processing_*` pipeline
(DLT → BAML → CocoIndex v1 → marimo) and ships those into the TanStack
Start 2D client at `cianfhoghlaim/web/apps/cianfhoghlaim-mmo/`. The
`celtic-asset-generation` spec already has 4 pipelines
(`official_documents/`, `subject_assets/`, `language_assets/`, `exporters/`),
but **none of them produce the visual game assets** that the 8 NCCA subject
realms (maths / chem / geography / history / english / gaeilge / computer
science / applied maths) need at the level of fidelity the team wants.

The team wants to **learn from the design patterns of retro educational
games** (Number Munchers, Oregon Trail, Where in the World is Carmen
Sandiego?) and apply them — not the literal pixel art — through a
subject-conditioned generative pipeline. The pipeline must:

1. Play those retro games via deterministic headless agents (libretro
   cores) so we can screenshot every design-relevant scene.
2. Segment sprites + UI overlays with **SAM3** so we can decompose the
   screenshot into reusable archetypes.
3. Extract typed design patterns (UI layout, sprite archetype, pedagogy
   pattern) via **BAML + CocoIndex v1 + the existing Qwen3-VL / Bolmo /
   Molmo2 VLM backbone**.
4. Generate new educational game assets — **2D** (Flux / Z-Image-Turbo /
   Qwen-Image / FIBO via InvokeAI) for the MMO v1 TanStack Start 2D
   client, and **3D** (Microsoft **TRELLIS.2-4B** + Facebook
   **SAM-3D-Objects**) staged to Garage S3 `s3://cianfhoghlaim-asset-v2/3d/`
   ready for the deferred MMO v2 Babylon.js client.

This change delivers those 4 capabilities as a parallel extension to the
existing `celtic-asset-generation` spec, and introduces one new spec
(`retro-game-design-catalogue`) for the catalogue + delivery surface.

## What Changes

A single openspec change with 5 deliverables:

### D1. New capability spec `retro-game-design-catalogue`

`openspec/specs/retro-game-design-catalogue/spec.md` (NEW spec) + the
delta at `openspec/changes/retro-educational-game-asset-pipeline-v1/specs/retro-game-design-catalogue/spec.md`.

The new spec covers 6 Requirements:

1. **ROM/library ingest** — read the existing `romm` library (and
   `Drop-OSS/drop` for any retro entries outside Romm's native schema)
   and yield a typed `retro_library` DLT resource.
2. **Headless screenshot capture** — drive the games via deterministic
   macro scripts through the new `libretro-retroarch` stack; save via
   `ludusavi`-managed save states; yield `retro_screenshots`.
3. **SAM3 + SAM-3D-Objects segmentation** — the new
   `sam3-server` / `sam3d-objects-server` stacks expose OpenAI-compatible
   segmentation endpoints; `meaisinfhoghlaim/segmentation/` wraps them.
4. **VLM design-pattern extraction** — the canonical
   Bolmo / Molmo2 / Qwen3-VL backbone + BAML
   `ExtractGameDesignPattern` + CocoIndex v1 flow
   `retro_design_pattern_embedding.py` (reusing `_lifespan.py`).
5. **Subject-conditioned asset generation** — 2D (Flux / Z-Image /
   Qwen-Image / FIBO via InvokeAI) + 3D (TRELLIS.2 + SAM-3D-Objects),
   conditioned on the (syllabus LO × design pattern) tuple, with
   output to `stedding/asset_generation/2d/` and Garage S3
   `s3://cianfhoghlaim-asset-v2/3d/`.
6. **Catalogue + delivery** — marimo dashboard, Storybook static
   export variant, pxlkit sprite atlases, retroassembly catalogue
   metadata; Hermes nightly cron `retro_digest` for new entries.

### D2. MODIFIED `celtic-asset-generation` spec (5th pipeline)

The canonical `openspec/specs/celtic-asset-generation/spec.md` already
mandates 4 successive INDEPENDENT pipelines. This change adds a **5th
pipeline** `retro_design_patterns/` via a `## ADDED Requirements`
delta at
`openspec/changes/retro-educational-game-asset-pipeline-v1/specs/celtic-asset-generation/spec.md`.

The 5th pipeline reuses 3 of the existing 4 (subject_assets generates
the assets once the pattern is known; language_assets handles the 6
Celtic languages; exporters deliver to 2D + 3D runtimes) and adds 1
new pipeline that produces the **design-pattern catalogue**.

### D3. New infrastructure stacks (10 new + 2 fixed)

Add the following stacks, all per the 6-file GOLD_STANDARD pattern
(`compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` +
`blueprint.yaml` + `.env.example`):

| Stack | Upstream | Port | Domain |
|:--|:--|--:|:--|
| `sam3-server` | `facebook/sam3` (HuggingFace) via Modal local-exec | 9230 | `sam3.cianfhoghlaim.ie` |
| `sam3d-objects-server` | `facebook/sam-3d-objects` | 9231 | `sam3d.cianfhoghlaim.ie` |
| `trellis-server` | `microsoft/TRELLIS.2-4B` | 9232 | `trellis.cianfhoghlaim.ie` |
| `fibo-server` | BFL FIBO (structured image gen) | 9233 | `fibo.cianfhoghlaim.ie` |
| `comfyui` | `ghcr.io/comfyanonymous/comfyui` (optional; InvokeAI may suffice) | 9234 | `comfyui.cianfhoghlaim.ie` |
| `libretro-retroarch` | `libretro/retroarch` headless cores | 9240 | `libretro.cianfhoghlaim.ie` |
| `retroassembly` | `arianrhodsandlot/retroassembly` | 9241 | `retroassembly.cianfhoghlaim.ie` |
| `pxlkit` | `joangeldelarosa/pxlkit` (static export served by nginx) | 9242 | `pxlkit.cianfhoghlaim.ie` |
| `drop` (REPLACED) | `Drop-OSS/drop` (replaces the wrong `getcatch/drop`) | 3000 | unchanged |
| `storybook` (REBUILT) | `storybookjs/storybook` (replaces nginx placeholder) | 6006 | unchanged |

Each stack gets a Komodo procedure at
`bonneagar/komodo/procedures/<stack>.toml`, a Pangolin private resource
(6-label shape), and Infisical secrets via
`bun run scripts/init-vault.ts`.

### D4. New Python code under `cianfhoghlaim/`

| File | Purpose |
|:--|:--|
| `meaisinfhoghlaim/segmentation/{__init__,sam3,sam3d_objects,openai_api}.py` | SAM3 + SAM-3D-Objects wrappers |
| `meaisinfhoghlaim/playback/{__init__,libretro,save_state}.py` | libretro headless + ludusavi save-state bridge |
| `dlt/retro/{__init__,library,screenshots,design_patterns,asset_generation}.py` | 4 new DLT sources |
| `baml/retro/{design_extraction,asset_prompt_generation}.baml` | 2 new BAML files |
| `cocoindex/{retro_design_pattern_embedding,asset_generation_embedding}.py` | 2 new v1 CocoIndex Apps |
| `dagster/assets/{retro_design_patterns,retro_asset_generation}.py` | 2 new asset groups |
| `dagster/sensors/retro_library_watcher.py` | Sensor watching `romm` + `Drop-OSS/drop` for new entries |
| `notebooks/retro_game_design_catalogue.py` | marimo dashboard |

### D5. Documentation + Hermes cron

| File | Purpose |
|:--|:--|
| `docs/ui-inspiration/GAME_DESIGN_CATALOGUE.md` | Catalogue summary, indexing the design patterns |
| `hermes/cron/retro_digest.yaml` | Nightly cron: scan ROMM new entries → capture screenshots → extract patterns → update catalogue |

## Impact

### Affected specs
- `celtic-asset-generation` — MODIFIED, adds a 5th pipeline
  `retro_design_patterns/` via `## ADDED Requirements`
- `retro-game-design-catalogue` — NEW canonical spec (6 Requirements)
  with the delta at
  `openspec/changes/retro-educational-game-asset-pipeline-v1/specs/retro-game-design-catalogue/spec.md`

### Existing assets/services reused

- 8-subject DLT sources at
  `cianfhoghlaim/dlt/british_isles/ie/education/subjects/<subject>/`
- 8-subject CocoIndex v1 embedding flows at
  `cianfhoghlaim/cocoindex/<subject>_embedding.py` + `_lifespan.py`
- 8-subject leaving-cert corpus at
  `cianfhoghlaim/leaving_certificate/<subject>/{en,ga}/`
- ROMM v3.x at `romm.cianfhoghlaim.ie` (`bonneagar/stacks/romm/`)
- Ludusavi game-save manager at `ludusavi.cianfhoghlaim.ie`
  (`bonneagar/stacks/ludusavi/`)
- Moonlight + Sunshine for game streaming (debug/play surfaces)
- InvokeAI for image generation (`invokeai.cianfhoghlaim.ie`)
- 6 OCR backends + 10 OCR models in `meaisinfhoghlaim/`
- Canonical VLM backbone: Bolmo / Molmo2 / Qwen3-VL (per
  `celtic-asset-generation` + `meaisinfhoghlaim-ocr-htr`)
- 8 ADK subject specialist agents
- BAML contracts at `cianfhoghlaim/baml/{leaving_cert,quest_packs}/`
- DLT destinations + MotherDuck + DuckLake pipeline
- Convex + FalkorDB + LanceDB storage layer

### Files added

**OpenSpec artifacts:**
- `openspec/specs/retro-game-design-catalogue/spec.md` (NEW)
- `openspec/changes/retro-educational-game-asset-pipeline-v1/proposal.md`
- `openspec/changes/retro-educational-game-asset-pipeline-v1/tasks.md`
- `openspec/changes/retro-educational-game-asset-pipeline-v1/specs/celtic-asset-generation/spec.md`
- `openspec/changes/retro-educational-game-asset-pipeline-v1/specs/retro-game-design-catalogue/spec.md`

**Stacks (10 new × 6 files + 2 fixed):**
- `bonneagar/stacks/{sam3-server,sam3d-objects-server,trellis-server,fibo-server,comfyui,libretro-retroarch,retroassembly,pxlkit}/` (each: `compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`)
- `bonneagar/komodo/procedures/{sam3-server,sam3d-objects-server,trellis-server,fibo-server,comfyui,libretro-retroarch,retroassembly,pxlkit}.toml`

**Python code:**
- All 8 entries in `cianfhoghlaim/{meaisinfhoghlaim,dlt,baml,cocoindex,dagster}/` listed in D4 above

**Docs + Hermes:**
- `docs/ui-inspiration/GAME_DESIGN_CATALOGUE.md`
- `hermes/cron/retro_digest.yaml`

### Files modified

- `bonneagar/stacks/drop/compose.yaml` (replace `getcatch/drop` → `Drop-OSS/drop`)
- `bonneagar/stacks/storybook/compose.yaml` (replace nginx → real `storybookjs/storybook` build)
- `openspec/specs/celtic-asset-generation/spec.md` (add the 5th pipeline section, mirroring the delta)
- `.agents/skills/agent-fleet-orchestration/SKILL.md`
  (add `retro_design_agent` keyword routing slot)
- `.agents/skills/agentic-frontend-frameworks/SKILL.md`
  (add asset CDN delivery section pointing at Garage S3 + pxlkit)
- `.agents/skills/agent-observability/SKILL.md`
  (add Langfuse traces for SAM3 + VLM + Flux/Z-Image calls)
- `.agents/skills/ncca-formative-assessment/SKILL.md`
  (add generated-asset context to each formative quest)

### Non-Goals

- **No copyright infringement** — only design patterns + homage-style
  generated art; no literal asset reuse from retro games. Outputs are
  conditioned on syllabus LOs, not pixel-derivative of source games.
- **No Babylon.js 3D client** in v1 of the MMO (the existing
  `cianfhoghlaim-educational-mmo` MMO v1 spec defers it to v2). The
  3D pipeline is **built in parallel** and staged to Garage S3
  `s3://cianfhoghlaim-asset-v2/3d/`, ready for v2.
- **No NEAT/RL training in v1** of this change (deferred; the
  screenshot capture is fully deterministic via macro scripts).
- **No new web scraping** — reuses existing Firecrawl + Crawl4AI skills
  for any ROM metadata enrichment.
- **No breaking changes** to the existing 8-subject syllabus pipeline;
  the new 5th pipeline is a strict additive change.

## Risks

1. **GPU contention on bunchloch M4 Max** — 4 new GPU-using
   services (SAM3, SAM-3D-Objects, TRELLIS.2, FIBO) on top of the
   existing llama-swap + mlx-omni. Mitigation: scheduler-tuned memory
   limits (2 GB each) + call-throttling in BAML clients + Hermes
   nightly cron instead of poll-on-demand.
2. **Headless libretro on macOS arm64** — not all cores ship native
   arm64 binaries; some need x86_64 emulation under Rosetta. Mitigation:
   prioritise the 6 platforms with the densest educational-classics
   coverage (NES, SNES, GB, GBA, Genesis, PS1) and use the well-tested
   cores (mesen, snes9x, gambatte, mgba, genesis_plus_gx, pcsx_rearmed).
3. **SAM3 + SAM-3D-Objects licence** — both Apache 2.0 per their
   upstream READMEs (verify in Phase 1 task 1.1). The pipelines only
   use them for *decomposition* of source screenshots; no derivative
   assets are produced.
4. **Long-running BAML calls** — design-pattern extraction of a
   single screenshot is 1-3 LLM turns. A full ROMM library sweep
   = 100s of screenshots = ~30 minutes of wall time per platform.
   Mitigation: Hermes cron batches nightly; `retro_digest` is
   idempotent; DLT primary keys dedupe on screenshot SHA-256.
5. **Garage S3 egress cost** — the `v2/3d/` stash will grow to
   GB-scale quickly. Mitigation: lifecycle policy on the bucket
   (90-day standard → 1-year glacier-equivalent); served behind
   Cloudflare CDN (R2 mirror only if egress becomes a problem).
6. **Bilingual EN + GA coverage** — design-pattern prompts are
   generated in EN only; the BAML extraction always populates
   `name_en` + `name_ga` for the Celtic-language subjects. Coverage
   gap: none expected (the VLM backbone handles both EN + GA
   prompts via the canonical `ExtractEnStrong` + `ExtractGaStrong`).

## Out-of-scope / deferred to v2 (potential follow-up changes)

- **NEAT behavioural analysis** — train a NEAT agent on a subset
  of retro games to extract trajectory data, feeding it back into
  the design-pattern catalogue (the "pedagogy_pattern" extraction).
- **Babylon.js 3D client** — the deferred v2 of the MMO will
  consume `s3://cianfhoghlaim-asset-v2/3d/` directly.
- **Other retro game categories** — sports, platformers, RPGs (not
  yet classified for educational relevance).
- **HuggingFace Spaces public showcase** — the design-pattern
  catalogue marimo notebook could be packaged as a public
  HuggingFace Space (`gradio-ensemble-pattern` reuses do this).

## Open Questions (resolve before deploy, not blocking plan approval)

1. Which 3 retro games specifically as the v1 starting library?
   (Number Munchers + Oregon Trail + Carmen Sandiego — recommended
   per `bonneagar/stacks/romm/README.md`).
2. NEAT/RL training compute — Modal or bunchloch?
   (Recommended: Modal; M4 already saturated.)
3. Asset CDN for `v2/3d/` — Garage S3 vs Cloudflare R2?
   (Recommended: Garage S3 to avoid new infra.)
4. 3D file format — GLB only, or GLB + USDZ?
   (Recommended: both; marginal cost.)
