# Cianfhoghlaim Convergence Saga v1 — The 8-Plan Refactor (2026-10-01)

> **The meta-plan that supersedes the 7-stage super-saga.** Built from
> analysis of: the 79 pending openspec changes (0 tasks done on most),
> the 103 active specs, the 387-archived changes, the 74 skills,
> the 107-stack bonneagar fleet, the 20/22 healthy containers on
> bunchloch, the recent ADK 2 Pillar 1+3 implementation
> (`agents/workflows/*.py` — 914 LOC), the new cianfhoghlaim-nua web
> consolidation, and the Tuatha British Isles MMO direction.
>
> **The constraint**: produce visible interim updates between each
> plan so the operator can demo progress. Tie off stubs + quality-of-life
> wins per plan. Use subagents for the heavy lifting.

---

## 0. How to read this plan

This is the **top-level saga doc** for 8 openspec changes (Plan 1 through
Plan 8). Each plan has its own `openspec/changes/2026-10-0X-<plan>/`
folder with a `proposal.md`, `tasks.md`, and `specs/<capability>/spec.md`.
**Plan 0** is this document (the meta-plan).

Each plan:
- Has a single domain focus (lakehouse, ADK, CocoIndex, FIBO, etc.)
- Chains to the next plan (no plan is an island)
- Ships 1 visible demo + 1 quality-of-life win + 1 stub-to-real conversion
- Uses 1+ subagents for parallel work
- Closes 1 of the 79 pending openspec changes (or absorbs multiple)

The cross-cutting concerns (C1–C6) run in parallel and accelerate all plans.

---

## 1. Plan 0 (this document) — the meta-plan

Already done in this PR: the saga doc itself.

---

## 2. Plan 1 — `2026-10-02-adk-asset-generation-pillar3-v1` (ADK 2 + asset-gen domain)

### Domain
The ADK 2 Pillar 3 deep-research pipelines (aistear + primary + JC + SC + tertiary)
currently produce a written briefing but no visual assets. The `image_generation_agent`
exists but with `GENERATE_2D_ASSET_TOOL = None` (stub). The 6
`_stub_generate_image` calls return `{"stub": True}` dicts. The
5 `image_gen` MODEL_REGISTRY entries (flux2-dev + z-image-turbo + qwen-image
+ sdxl + fibo) are wired through litellm but never called.

### What this plan ships
1. Real LiteLLM-routed image-gen calls (replace the 6 stubs)
2. `aistear_deep_research.py` Pillar-4 stage: `decompose → research → synthesize → render_assets`
3. The 24 agents wired through the image-gen tools (not just image_generation_agent)
4. The `cocoindex_flows/media/image_generation_flow.py` LanceDB schema verified + indexed

### Files touched
- `agents/adk/tools/image_generation.py` — replace `_stub_generate_image` with real `litellm.completion(model=model_for(image_gen, role), messages=[...])` calls
- `agents/adk/image_generation_agent.py` — replace `GENERATE_2D_ASSET_TOOL = None` with real `FunctionTool(generate_2d_asset)` wraps
- `agents/workflows/aistear_deep_research.py` — add `render_assets_node` stage
- `notebooks/dashboards/asset_gen_demo.py` — new marimo notebook that demonstrates the pipeline
- `.agents/skills/tuatha-asset-generation/SKILL.md` — new skill (replaces deprecated `celtic-asset-generation`)

### Visible demo
```
$ uv run python scripts/asset_bench.py "An Irish round tower at sunset"
→ 1.5s: research briefing on round tower architecture
→ 3.2s: FIBO diagram rendered (qwen-image, role=bilingual)
→ 4.1s: 6 Celtic language variants in parallel (gaeilge + cymraeg + ...)
→ 6.8s: 12 assets in LanceDB media.image_gen_chunks
→ marimo dashboard updates: 12 rows in the per-subject asset browser
```

### Subagent used
`asset-gen-orchestrator` (C4 subagent) — runs the DLT → BAML → CocoIndex → image-gen chain end-to-end.

### Spec materialised
`openspec/specs/adk-asset-gen-pillar3/spec.md` — 4 Requirements:
- R1: Real image-gen calls (no stubs)
- R2: Pillar 3 → asset-gen wiring (per pipeline)
- R3: 24 agents can request assets
- R4: Per-language asset generation (6 Celtic)

---

## 3. Plan 2 — `2026-10-03-cocoindex-retro-gameplay-v1` (CocoIndex + retro domain)

### Domain
`baml_src/media/gameplay_descriptor.baml` defines typed schemas for
Hades/WoW/Golden Sun/Pokémon gameplay descriptors but no CocoIndex
flow consumes them. The `retro-game-design-catalogue` spec describes
a `retro_design_pattern_embedding` App that doesn't exist. SAM3 sprite
segmentation isn't wired.

### What this plan ships
1. `cocoindex_flows/media/retro_design_embedding.py` — the missing App
2. `baml_src/media/extract_design_pattern.baml` — the new BAML function
3. SAM3 sprite segmentation glue (against `sam3-server` stack)
4. `libretro-retroarch` integration for screenshot capture
5. `ludusavi` save-state restoration
6. Pattern catalog dashboard

### Files touched
- `cocoindex_flows/media/retro_design_embedding.py` (new)
- `baml_src/media/extract_design_pattern.baml` (new)
- `agents/adk/tools/retro_gameplay_descriptor.py` (new)
- `bonneagar/stacks/retro-screenshots/` (new stack)
- `notebooks/dashboards/retro_patterns.py` (new marimo)

### Visible demo
```
$ uv run python scripts/retro_capture.py "number_munchers.nes"
→ Title screen captured (PNG, sha256 = ...)
→ SAM3 segmented into 8 sprites (player + 6 munchers + 1 grid)
→ ExtractGameplayDescriptor → typed pattern (rogue_like + match_three)
→ CocoIndex stores pattern + 8 sprite vectors in lance://media.retro_design
→ marimo dashboard shows: 1 game × 1 pattern × 8 sprites, all clickable
```

### Subagent used
`cocoindex-media-builder` (C4) — wires CocoIndex + BAML + LanceDB for media flows.

### Spec materialised
`openspec/specs/cocoindex-retro-gameplay/spec.md`

---

## 4. Plan 3 — `2026-10-04-fibo-asset-pipeline-v1` (FIBO + syllabus domain)

### Domain
The `celtic-asset-generation` spec describes FIBO 2D diagram generation
from NCCA syllabus PDFs but the actual code only exists as 5 .pyc
files in `tuatha/asset_generation/fibo/__pycache__/` (the source `.py`
files are missing). The `ExtractSyllabusDiagram` BAML function is
referenced in the spec but doesn't exist. The dagster assets under
`orchestration/defs/4_asset_generation/` don't include FIBO.

### What this plan ships
1. The 5 missing `tuatha/asset_generation/fibo/{__init__,assets,education_fibo,resources,schemas}.py` source files (rewritten from .pyc + spec)
2. `baml_src/media/extract_syllabus_diagram.baml` — the new BAML function
3. `orchestration/defs/4_asset_generation/fibo_dagster_assets.py` — the dagster assets
4. `tuatha/asset_generation/fibo/main.py` — the CLI entrypoint
5. FIBO → marimo notebook for diagram demo

### Files touched
- `tuatha/asset_generation/fibo/__init__.py` (new)
- `tuatha/asset_generation/fibo/assets.py` (new)
- `tuatha/asset_generation/fibo/education_fibo.py` (new)
- `tuatha/asset_generation/fibo/resources.py` (new)
- `tuatha/asset_generation/fibo/schemas.py` (new)
- `baml_src/media/extract_syllabus_diagram.baml` (new)
- `orchestration/defs/4_asset_generation/fibo_dagster_assets.py` (new)
- `notebooks/dashboards/fibo_diagram_demo.py` (new)

### Visible demo
```
$ uv run python scripts/fibo_demo.py "chemistry_2019_p3.pdf"
→ ExtractSyllabusDiagram → 1 figure (Overview of Leaving Cert Chemistry)
→ FiboResource → render iteration 1 → ValidationResource → score 0.72
→ render iteration 2 → score 0.91 → accept
→ asset_id = fibo_chemistry_2019_p3_overview.png → 1024×1024 PNG
→ marimo notebook: 1 figure, 3 iterations, final score 0.91
```

### Subagent used
`baml-typer` (C4) — fills in the FIBO-related BAML contracts + .py source.

### Spec materialised
`openspec/specs/fibo-asset-pipeline/spec.md`

---

## 5. Plan 4 — `2026-10-05-lakehouse-ml-assetgen-wiring-v1` (Lakehouse ↔ ML ↔ web)

### Domain
The lakehouse has 17 services in compose but only 5 running on bunchloch.
The image-gen assets land in LanceDB but aren't registered in the Iceberg
catalog. The OTel collector (16/17 lakehouse services) isn't tracing the
image-gen pipeline. The marimo dashboards can't query asset metadata via SQL.

### What this plan ships
1. `orchestration/assets/ducklake_maintenance.py` — sync LanceDB → DuckLake → Iceberg
2. OTel spans for the full DLT → BAML → CocoIndex → image-gen → LanceDB → DuckLake chain
3. Per-asset Lakehouse table: `ducklake_cianfhoghlaim.media.image_gen_chunks`
4. `notebooks/dashboards/asset_lakehouse_browser.py` — marimo browser for the asset table
5. Lakehouse bring-up: 12 missing services (Garage + ClickHouse + Cognee + Graphiti + FalkorDB + Memgraph + Memgraph Lab + Olake + OTel collector + Nimtable UI + lance-namespace sidecar + lakekeeper-migrate)
6. OpenTelemetry semantic conventions applied to the image-gen pipeline

### Files touched
- `orchestration/assets/ducklake_maintenance.py` (new)
- `orchestration/assets/otel_image_gen_traces.py` (new)
- `notebooks/dashboards/asset_lakehouse_browser.py` (new)
- `bonneagar/stacks/lakehouse/compose.yaml` — verify all 17 services enabled
- `agents/adk/tools/image_generation.py` — add OTel spans

### Visible demo
```
$ mise run lakehouse:up
→ 17/17 containers healthy
$ uv run python -c "import duckdb; con=duckdb.connect('md:cianfhoghlaim'); print(con.execute('SELECT COUNT(*) FROM ducklake_cianfhoghlaim.media.image_gen_chunks').fetchone())"
→ (12,)  # 12 assets from Plan 1
```

### Subagent used
`lakehouse-bridge-builder` (C4) — wires LanceDB → DuckLake → Iceberg.

### Spec materialised
`openspec/specs/lakehouse-assetgen-wiring/spec.md`

---

## 6. Plan 5 — `2026-10-06-adk-cognee-visual-assets-v1` (Cognee + visual-assets domain)

### Domain
The ADK 2 Pillar 3 deep-research pipelines write findings to in-memory
context but never persist to Cognee. The 5 educational agents can't
answer "show me the assets related to Julius Caesar" because there's no
Cognee graph linking entities to assets.

### What this plan ships
1. Extend each Pillar 3 workflow to: write briefing to Cognee as `LearningEpisode`
2. `baml_src/media/extract_entities.baml` — NER function
3. `agents/meaisinfhoghlaim/media_intel/cognee_linker.py` — links entities to assets via `CITED_IN` edges
4. `notebooks/dashboards/cognee_asset_graph.py` — marimo visual graph
5. The 8 subject agents (maths + chemistry + biology + physics + english +
   irish + geography + history) wired to the entity-asset graph
6. Cross-jurisdictional support (EN + GA + CY + GD)

### Files touched
- `agents/workflows/{aistear,primary,jc,sc,tertiary}_deep_research.py` — add `cognee_emit_node` after `synthesize`
- `baml_src/media/extract_entities.baml` (new)
- `agents/meaisinfhoghlaim/media_intel/cognee_linker.py` (new)
- `notebooks/dashboards/cognee_asset_graph.py` (new)

### Visible demo
```
$ uv run python scripts/cognee_assets.py "Julius Caesar"
→ Cognee returns: 12 entities + 12 linked assets
→ marimo graph: entity → asset (12 nodes + 12 edges, clickable)
```

### Subagent used
`cognee-linker` (C4) — wires ADK ↔ Cognee ↔ asset-gen.

### Spec materialised
`openspec/specs/adk-cognee-visual-assets/spec.md`

---

## 7. Plan 6 — `2026-10-07-bilingual-celtic-asset-pipeline-v1` (Bilingual Celtic domain)

### Domain
The `baml_src/british_isles/_cross/vernacular_languages.baml` defines
the 6 Celtic languages but no asset generation code exists for any of
them. Irish-only assets aren't generated.

### What this plan ships
1. `baml_src/british_isles/_cross/asset_generation.baml` — the 6-language asset generation BAML
2. Per-language CocoIndex flows (6 flows × 1 per language)
3. Per-language LanceDB tables (`media.image_gen_chunks_gaeilge` + ..._cymraeg` + ..._gaidhlig` + ..._gaelg` + ..._kernewek` + ..._brezhoneg`)
4. Per-language marimo notebook (`notebooks/dashboards/asset_gen_gaeilge.py` etc.)
5. Irish-first launch (most content available)
6. Welsh + Scottish Gaelic + Manx + Cornish + Breton (staged)

### Files touched
- `baml_src/british_isles/_cross/asset_generation.baml` (new)
- `cocoindex_flows/media/asset_generation_gaeilge.py` (new, + 5 more)
- `notebooks/dashboards/asset_gen_gaeilge.py` (new, + 5 more)

### Visible demo
```
$ uv run python scripts/celtic_assets.py "An Irish round tower at sunset"
→ 6 variants rendered in parallel (gaeilge + cymraeg + gaidhlig + gaelg + kernewek + brezhoneg)
→ 6 LanceDB tables updated
→ marimo dashboard: 1 prompt × 6 languages × 3 variants = 18 cells
```

### Subagent used
`baml-typer` (C4) — multi-language BAML contract authoring.

### Spec materialised
`openspec/specs/bilingual-celtic-asset-pipeline/spec.md`

---

## 8. Plan 7 — `2026-10-08-tuatha-closed-loop-mmo-v1` (Tuatha closed-loop demo)

### Domain
The Tuatha British Isles Formative Assessment MMO spec describes
PixiJS realms + sprite banks + BAML quest packs but nothing is wired
together. The `tuatha/` dir has 0 .py files. The 14 subjects don't
have working realms.

### What this plan ships
1. `orchestration/defs/4_asset_generation/tuatha_realm_asset.py` — per-subject realm asset
2. `tuatha/agents/realm_constructor_agent.py` — the ADK agent that builds realms
3. `tuatha/agents/quest_pack_agent.py` — generates quest packs from BAML
4. PixiJS realm routes in `web/apps/cianfhoghlaim-nua/src/routes/realm/{subject}.tsx`
5. `notebooks/dashboards/tuatha_realm_demo.py` — live demo surface
6. Mathematics-first launch (1 of 14 subjects)
7. Per-subject asset-gen → realm-constructor → PixiJS-render pipeline

### Files touched
- `tuatha/agents/realm_constructor_agent.py` (new)
- `tuatha/agents/quest_pack_agent.py` (new)
- `orchestration/defs/4_asset_generation/tuatha_realm_asset.py` (new)
- `web/apps/cianfhoghlaim-nua/src/routes/realm/mathematics.tsx` (new)
- `notebooks/dashboards/tuatha_realm_demo.py` (new)

### Visible demo
```
$ uv run python scripts/tuatha_demo.py
→ "Mathematics Formative Session" button clicked
→ 5 questions rendered as PixiJS realm
→ Celtic-themed sprites (round towers + mathematical symbols)
→ student plays → score trace → Cognee asset graph updates
→ RAGAS faithfulness score: 0.91
```

### Subagent used
`tuatha-realm-constructor` (C4) — builds + tests PixiJS realms.

### Spec materialised
`openspec/specs/tuatha-closed-loop-mmo/spec.md`

---

## 9. Plan 8 — `2026-10-09-fresh-slate-spec-rules-v1` (Stage 8 fresh-slate spec refactor)

### Domain
The current openspec model (200-line proposals + flat task.md + 0/X
progress pattern) produces 79 stalled changes. The 33 completed changes
use a different model. The fresh-slate rewrite brings the spec-driven-
development rules up to date with the converged baseline.

### What this plan ships
1. New `openspec/AGENTS.md` with the saga header + milestone pattern
2. New `openspec/templates/{proposal,tasks,spec}.md` — the canonical archetypes
3. Archive all 79 pending changes + start fresh with the 8-plan model
4. New `bun run openspec:archive --cascade` command
5. New `mise run saga:status` command
6. Update `AGENTS.md` + `CHEATSHEET.md` + `README.md` to reflect the new rules
7. ONE PR that re-writes the openspec layer from scratch

### Files touched
- `openspec/AGENTS.md` (rewritten)
- `openspec/templates/` (new)
- `openspec/changes/` (archived)
- `openspec/specs/` (archived then re-materialised)

### Visible demo
```
$ bun run openspec:list
→ 0 pending changes (all 79 archived)
$ bun run openspec:archive --cascade
→ 0 stale archives
$ bun run saga:status
→ 8 plans × 100% complete (or whatever)
```

### Subagent used
`spec-archivist` (C4) — the bulk-archive + rewrite worker.

### Spec materialised
`openspec/specs/openspec-2-0/spec.md`

---

## 10. Cross-cutting concerns (run in parallel with all 8 plans)

### C1 — The stub-to-real sweep (Plan 1's first deliverable)
- 6 `_stub_generate_image` calls in `agents/adk/tools/image_generation.py` → real LiteLLM calls
- `image_generation_agent.GENERATE_2D_ASSET_TOOL = None` → real `FunctionTool`
- `voice_agent` NotImplementedError → real Pipecat + TTS
- BAML stub prompts → real BAML contracts
- All "Phase L stub" → real implementations

### C2 — The intra-stack wiring (Plan 4's first deliverable)
- Lakehouse (17 services) → ML stack (litellm + unsloth-serve + llama-swap + invokeai) → Web (cianfhoghlaim-nua)
- OTel collector traces the full chain
- Cognee dataset ingests from CocoIndex outputs
- marimo dashboards query the DuckLake tables

### C3 — The 6 intra-stack improvements (per plan)
1. **ADK 2** → Pillar 3 → image-gen (Plan 1)
2. **DLT** → path drift fix (Plan 3 side-effect)
3. **CocoIndex** → SAM3 + retro gameplay (Plan 2)
4. **Lakehouse** → LanceDB → DuckLake → Iceberg bridge (Plan 4)
5. **ML** → BAML → Cognee → LanceDB → image-gen (Plan 5)
6. **Web** → closed-loop Tuatha MMO (Plan 7)

### C4 — The 6 subagents (one per plan)
- `asset-gen-orchestrator` (Plan 1)
- `cocoindex-media-builder` (Plan 2)
- `baml-typer` (Plan 3)
- `lakehouse-bridge-builder` (Plan 4)
- `cognee-linker` (Plan 5)
- `tuatha-realm-constructor` (Plan 7)
- `spec-archivist` (Plan 8)

### C5 — Tie-offs (1 per plan)
- Plan 1: archive `celtic-asset-generation` skill → new `tuatha-asset-generation` skill
- Plan 2: archive `apple_photos` placeholder in tuatha
- Plan 3: ship `notebooks/dashboards/fibo_diagram_demo.py`
- Plan 4: archive `lakehouse-lance-namespace` legacy docs
- Plan 5: consolidate `meaisinfhoghlaim/educational/` duplicates
- Plan 6: archive `vernacular_languages.baml` placeholder
- Plan 7: archive deprecated `tuatha-mmo` + `tuatha-platform` skills
- Plan 8: archive the 79 pending changes

### C6 — Quality-of-life wins (1 per plan)
- Plan 1: `mise run asset:bench`
- Plan 2: `bun run retro:demo`
- Plan 3: `mise run fibo:render <pdf> <page>`
- Plan 4: `mise run lakehouse:status` (marimo-style)
- Plan 5: `mise run cognee:graph "Julius Caesar"`
- Plan 6: `mise run celtic:assets "prompt"`
- Plan 7: `bun run tuatha:demo`
- Plan 8: `bun run saga:status`

---

## 11. The 13-week timeline

```
Week 1  → Plan 1 (ADK + asset-gen)
Week 2  → Plan 1 finishes + Plan 2 starts (CocoIndex retro)
Week 3  → Plan 2 finishes + Plan 3 starts (FIBO)
Week 4  → Plan 3 finishes + Plan 4 starts (Lakehouse wiring)
Week 5-6 → Plan 4 (12 missing lakehouse services up + asset bridge)
Week 7-8 → Plan 5 (Cognee visual assets)
Week 9-10 → Plan 6 (Celtic bilingual)
Week 11-12 → Plan 7 (Tuatha closed-loop)
Week 13 → Plan 8 (fresh-slate spec refactor on a separate branch)
```

---

## 12. The interim updates — visible progress at every checkpoint

| After plan | Demo |
|---|---|
| 1 | Run a Pillar 3 deep-research briefing → see real generated assets in marimo |
| 2 | Sprite a retro game → see the design pattern in CocoIndex |
| 3 | Upload a syllabus PDF → see a FIBO diagram rendered |
| 4 | Run `SELECT * FROM ducklake_cianfhoghlaim.media.image_gen_chunks` |
| 5 | Run "research Julius Caesar" → see the entity-linked asset graph |
| 6 | Generate "round tower" in 6 Celtic languages, all in one go |
| 7 | Run a Mathematics formative session → see a Tuatha realm |
| 8 | The new openspec rules on top of the converged baseline |

---

## 13. Risk + mitigation

| Risk | Mitigation |
|---|---|
| InvokeAI image doesn't pull on bunchloch | Use Qwen-Image first (lightweight GGUF already deployed via llama-swap) |
| Bunchloch 16 GB RAM hits ceiling | Stage heavy work (FIBO render + SAM3 segment) to arm1-oci |
| Lakehouse 12 missing services have RAM requirements | Cascade bring-up: Garage + Lance first (smallest), then Cognee + Graphiti, then ClickHouse last |
| FIBO source code lost (.pyc only) | Rewrite from spec + functional refactor (don't try to decompile) |
| Pillar 3 → image-gen chain doubles API costs | Per-call budget caps + model fallback chain (qwen-image → flux2-dev → z-image-turbo) |
| Tuatha closed-loop too ambitious | Mathematics-only first; expand to 14 subjects after the demo works |

---

## 14. The operator quick-reference

```bash
# After Plan 1
uv run python scripts/asset_bench.py "An Irish round tower at sunset"

# After Plan 2
uv run python scripts/retro_capture.py "number_munchers.nes"

# After Plan 3
uv run python scripts/fibo_demo.py "chemistry_2019_p3.pdf"

# After Plan 4
mise run lakehouse:up
uv run python -c "import duckdb; con=duckdb.connect('md:cianfhoghlaim'); print(con.execute('SELECT COUNT(*) FROM ducklake_cianfhoghlaim.media.image_gen_chunks').fetchone())"

# After Plan 5
uv run python scripts/cognee_assets.py "Julius Caesar"

# After Plan 6
uv run python scripts/celtic_assets.py "An Irish round tower at sunset"

# After Plan 7
bun run tuatha:demo

# After Plan 8
bun run saga:status
```

---

## 15. What I'm NOT doing (out-of-scope)

- The 7-stage super-saga from the prior plan (lakehouse + pangolin + web + baml + marimo + agents + sister repos) — deferred to a separate `2026-11-01-v7-foundation-saga-v1/` after this saga
- The Stage 8 spec refactor until after Plan 7 (per the user instructions)
- The full sister-repo consolidation (the 5 sister-umbrella changes) — deferred
- The web-monorepo consolidation (148 tasks) — deferred

---

## 16. Status

**Current state**: Plan 0 (this document) + Plan 1 (ADK + asset-gen) being implemented.

**Date**: 2026-10-01
**Author**: Build subagent
**Next step**: Wire `image_generation_agent` to real LiteLLM calls (C1 stub sweep).


---

## Status (as of 2026-10-26)

7 of 8 plans merged to main. Only Stage 8 fresh-slate spec refactor remains (separate branch).

### Plan → PR mapping

| Plan | PR | Commit | Files | Status |
|:--|:--|:--|:--|:--|
| 1 (Saga meta-plan) | #196 | `8b200afad` | 20 / 2,354 lines | ✅ Merged |
| 2 (ADK + asset-gen) | #196 | `8b200afad` | (same) | ✅ Merged |
| 3 (CocoIndex + retro) | #197 | `1af8194d6` | 15 / 1,577 lines | ✅ Merged |
| 4 (FIBO 2D diagram) | #198 | `a2a54c181` | 9 / ~1,500 lines | ✅ Merged |
| 5 (Lakehouse bridge) | #199 + #204 | `1a9c2dca0` | 6 / 631 lines + 5 / 277 lines | ✅ Merged |
| 6 (Cognee + visual assets) | #200 + #204 | `1a9c2dca0` | 6 / 837 + 5 / 277 lines | ✅ Merged |
| 7 (Celtic bilingual) | #201 | `fc0808dac` | 23 / 1,270 lines | ✅ Merged |
| 8 (Tuatha closed-loop) | #202 | `59012ca52` | 8 / 849 lines | ✅ Merged |
| Phase A (typo fix + duplicate) | #203 | `5b9659fe3` | 12 / 172 lines | ✅ Merged |
| Phase C2 (Cognee retry) | #204 | `1a9c2dca0` | (rolled into Plan 5) | ✅ Merged |

### Remaining work

**Stage 8 fresh-slate spec refactor** (deferred per original user direction):
- Branch: `fresh-slate-spec-rules` (new branch off `main`)
- Work: Phase B schema-naming convergence (TODO notes already in `baml_src/AGENTS.md`, `cocoindex_flows/AGENTS.md`, `dlt_sources/AGENTS.md`)
- 2 BAML parser workarounds in the new BAML contracts (extract_syllabus_diagram.baml, extract_design_pattern.baml) — `baml-py 0.226.1` issue with multi-line function signatures
- Docker daemon recovery (OrbStack socket issue blocking Plan 5 service bring-up)

### Operational notes

- All demo scripts run with graceful stub fallbacks (Cognee + LanceDB + Litellm)
- `uv run python scripts/asset_bench.py --list-models` → 7 image_gen entries
- `uv run python scripts/celtic_assets.py --lang ga --prompt '...'` → 5.4s end-to-end
- `uv run python scripts/cognee_link.py --demo` → 3-retry exponential backoff + stub fallback
- `uv run python scripts/lakehouse/verify_bridge.py` → graceful FAIL with no traceback when offline

