# Croílár HF Build Small 2026 Demo — 4 Gradio Spaces + 5-Element Connective Tissue

## Why

The HuggingFace "Build Small 2026" hackathon runs **5–15 June 2026**. The user is **already registered** in the `build-small-hackathon` HF org (165 Spaces, 13 models, 13 datasets live as of 08 June 2026). This change activates a 4-Space submission that demonstrates the **Cianfhoghlaim monorepo's Celtic-language AI capabilities** in a unified thematic frame.

The submission's central design choice is the **5-element connective tissue** (Talamh / Uisce / Tine / Aer / Anam) — derived from the Four Treasures of the Tuatha Dé Danann, extended with the Anam soul-layer. Each of the 4 Spaces maps cleanly to one or more elements; Space 4 ties them all together. This is the **meta-narrative** the 4 Spaces share, the demo video will narrate, and the OpenSpec capability is named after.

The 4 Spaces cover **7 Celtic nations** (RoI, NI, Wales, Manx, Scottish, Cornish, Breton — Breton "in progress" per user decision 2026-06-08), in **EN + Gaeilge** (with the 5 other Celtic languages as i18n placeholders ready for the next iteration).

## What

This change ships **4 Gradio Spaces on HuggingFace**, each a north-star demo of one quadrant of the Cianfhoghlaim monorepo:

| # | Space | HF Space name | Quadrant | 5-element tie | Tagline |
|--:|:--|:--|:--|:--|:--|
| 1 | **An Scrúdú** | `build-small-hackathon/an-scrudai` | `oideachais` (Talamh) | Earth | 33 subjects, 17 years, 1 typed data pipeline |
| 2 | **Meaisín Cliste** | `build-small-hackathon/meaisin-cliste` | `meaisínfhoghlaim` (Uisce + Aer) | Water + Air | Foclóir + Scoil ar an Léarscáil + Curaclam Trasteorann, side-by-side |
| 3 | **Cianfhoghlaim** | `build-small-hackathon/cianfhoghlaim` | `tuatha` (Aer + Anam) | Air + Spirit | Hades-style RPG on a navigable British Isles map called **Tuatha** |
| 4 | **Anam: Tuatha na nGaelscoil** | `build-small-hackathon/anam-tuatha-na-ngaelscoil` | `croílár` (5 elements) | All 5 | The 5-element connective tissue integrating Spaces 1–3 |

Each Space is a **Gradio app** (HF Spaces native), backed by a **hybrid model layer** (HF Inference for chat, BAML-compatible cloud model for extraction — per the locked decision 2026-06-08). All models ≤ 32B to satisfy the hackathon constraint.

The 5-element framework is the **connective tissue**:
- **Talamh (Earth)** = bridge to Space 1 (curriculum + geographic layer)
- **Uisce (Water)** = bridge to Space 2 themes (cross-border curriculum, nurturing the RAG)
- **Tine (Fire)** = the connective tissue itself (OCR + asset transformation pipeline)
- **Aer (Air)** = bridge to Space 2 + Space 3 (language + NPC dialogue)
- **Anam (Spirit)** = the meta-layer (Anam SBT credential, Anamchara peer-mentorship, EBSI Verifiable Credentials)

## Impact

### Affected specs
- NEW `croilar-gradio-hf-demo` — the 4-Space submission capability

### Existing assets to extend (no redevelopments, only reuses)
- `oideachais/data_platform/baml_src/` (BAML extraction schemas)
- `oideachais/data_platform/dlt_sources/` (DLT sources for all 7 nations)
- `oideachais/data_platform/dagster_defs/assets/ireland/exam_materials_assets.py` (Dagster assets)
- `oideachais/document_factory/curriculum_document.py` (PCLM emitter)
- `oideachais/samplaí/` (6 Celtic language sample corpora + cognates)
- `meaisínfhoghlaim/agents/` (12 specialised agents)
- `meaisínfhoghlaim/ocr/` (10 OCR models, gaelic_metrics, irish_processing)
- `meaisínfhoghlaim/evaluation/ragas_pipeline.py` (RAGAS, 22.7pp headline)
- `meaisínfhoghlaim/language/` (6 Celtic language DLT sources)
- `tuatha/baml_src/` (player_assessment, mythology_extraction, game_content, celtic_curriculum)
- `tuatha/asset_generation/` (CelticPromptGenerator)
- `tuatha/fibo_generation/` (FIBO JSON configs)
- `tuatha/crates/wgpu/celtic-shaders/src/lib.rs` (WGSL Celtic-knot shader)
- `tuatha/apps/crypteolas_demo/anam-contracts/src/CuchulainnNFT.sol` (soulbound contract)
- `croilar/apps/web/`, `croilar/packages/`, `croilar/hono-api/` (BAML + i18n patterns)

### New code to write
- 4 Gradio `app.py` files (one per Space)
- 1 `spaces/_common/` shared bundle (Celtic theme tokens, Anam Bonneagar footer, soulbound SVG, social card, demo recorder)
- 1 `tuatha/baml_src/clients_hackathon.baml` (fork of `tuatha_clients.baml`, re-pointed to HF Inference)
- ~10 new BAML schemas (40–60 lines each) per the catalogue's "to add" lists
- 1 Anvil-sidecar Dockerfile for Space 4 (CuchulainnNFT.sol)

### Hosting
- HuggingFace Spaces (4 separate spaces, all in `build-small-hackathon/` org)
- Anvil sidecar container bundled in Space 4 (local Foundry/Hardhat)
- No LiteLLM gateway, no Pocket ID, no Pangolin, no Locket — the infrastructure quadrant is **archived for this hackathon** (per decision 2026-06-08). The "Anam Bonneagar" footer is the architectural homage.

### Cost
- ~$3.55 across the 8-day hackathon (per the `build-small-2026-model-fallback.md` estimate)
- Well within the user's HF free tier + OpenCode Go flat-rate budget

## Non-Goals
- No live SpacetimeDB real-time multiplayer (Space 3 runs locally)
- No real chain / no x402 micropayments (Anam SBT mounted on local Anvil, no gas)
- No Pocket ID / Pangolin / WireGuard / Locket / Traefik (infrastructure archived)
- No real-world gig / freelance / consulting angle (purely educational platform)
- No Breton, Cornish, or Welsh-medium primary content in the v1 demo (languages scaffolded but data limited)
- No x402 / Agentic Commerce integration (the Solidity contracts exist but are demo-only)

## 7-Day Schedule

| Day | Build | Cross-cutting |
|--:|:--|:--|
| **1 (Mon)** | Spin up `spaces/_common/` (Celtic theme, Anam Bonneagar footer, soulbound SVG, social card); OpenSpec change dir; BAML re-pointing to HF Inference | 5 file artefacts written (catalogue, indexes, model fallback, OpenSpec change, plan patch) |
| **2 (Tue)** | **Space 3** core: Babylon.js WebGPU canvas + 6 NPCs + 4 diegetic zones; demo video 1 (Cian → Manannán → Rhiannon flow) | MotherDuck Dive snapshots pre-computed; gov landscape scraping begins |
| **3 (Wed)** | **Space 1** core: BAML `ComposeMarkingSchemeDiff` + Gradio Blocks heatmap + PCLM-PDF emitter; demo video 2 | CuchulainnNFT.sol deployed to local Anvil; fada-accuracy preserved end-to-end |
| **4 (Thu)** | **Space 2** (3 themes in parallel): Foclóir + Scoil ar an Léarscáil + Curaclam Trasteorann; demo video 3 | 12-agent Q&A scaffolded; cross-border matrix built; Anam Bonneagar footer added |
| **5 (Fri)** | **Space 4** — 5 elements, 7 features: Tine → Uisce → Talamh → Aer → Anam → Mac Léinn → Fiosraigh; demo video 4 | All 5 Spaces polished; 5-element connective-tissue story is the demo narration |
| **6 (Sat)** | All Spaces polish: bilingual EN/GA verified, accessibility audit, mobile-responsive check, demo videos 1–4, social cards | OpenSpec `tasks.md` and `proposal.md` written |
| **7 (Sun)** | Final polish + HF Space submissions + OpenSpec `spec:validate croilar-hf-build-small-2026-demo --strict` + `spec:archive` after approval | Blog posts published; Twitter/Mastodon thread with 4 social cards |

## Risks
1. HF Inference quota exceeded during 4-Space demo — the 3-tier fallback chain (Qwen2.5-7B → Llama-3.1-8B → Gemma-2-9B) mitigates
2. Babylon.js WebGPU + HF Spaces cold-start may take >60s — agressive caching of the 6 NPC dialogue trees as JSON pre-loads
3. Anvil-sidecar in Space 4 may not start on HF Spaces (CPU-only, no GPU) — fall back to deterministic SVG-only mounter, no live chain
4. 7-day schedule is tight — Space 3 (most distinctive) is Day 2 to bank a working demo early; Space 4 (largest scope) is Day 5
5. Fada preservation end-to-end is hard — verify the OCR → BAML → Gradio chain preserves `á é í ó ú`, `⁊`, `ḃċḋḟġṁṗṡṫ` on every step

## Cross-References
- `doc/hackathons/build-small-2026-docs-catalogue.md` — consolidated catalogue (Tier-1 / Tier-2 / Tier-3 / demo-stack mapping / refactor hooks / 22 known-drift items)
- `doc/hackathons/croilar-demo-quadrant-indexes.md` — per-quadrant asset indexes
- `doc/hackathons/build-small-2026-model-fallback.md` — model fallback chains
- `doc/hackathons/build-small-2026-plan.md` — re-themes section appended
- `openspec/specs/curriculum-ingestion/spec.md` — existing BAML extraction capability (extended by this change)
- `openspec/specs/assessment-extraction/spec.md` — existing assessment capability (extended by this change)
- `openspec/specs/oideachais-pipeline/spec.md` — existing oideachais pipeline capability (extended by this change)
- `openspec/specs/knowledge-graph/spec.md` — existing KG capability (extended by this change)
- `openspec/specs/semantic-search/spec.md` — existing vector search capability (extended by this change)
- `openspec/specs/bilingual-content/spec.md` — existing EN+GA content capability (extended by this change)
