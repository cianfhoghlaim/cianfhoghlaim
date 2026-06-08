# Cianfhoghlaim Build-Small Hackathon 2026 — Implementation Plan

> **v3 — Re-themes** (post extensive ccc + cognee audit + 6 Wikipedia scrapes). Supersedes v1 (5 Projects) and v2 (4+1 with Anam Bonneagar). The 4+1 plan became a 4-Space plan with the 5-element connective tissue as the unifying theme. OpenSpec change `croilar-hf-build-small-2026-demo` validated `--strict`.

---

## TL;DR (v3)

Ship **4 Gradio Spaces** under the user's existing `build-small-hackathon` HF org, all in **7 days** (deadline 15 June 2026). Every Space reuses existing monorepo assets (BAML, OCR, RAG, Celtic curriculum, Anam SBT contracts, DAG assets, dlt sources) — **no new infra**. The unifying theme is the **5-element connective tissue** (Talamh / Uisce / Tine / Aer / Anam) derived from the Four Treasures of the Tuatha Dé Danann, with Anam as the soul-layer.

The 4 Spaces cover **7 Celtic nations** (RoI, NI, Wales, Isle of Man, Scotland, Cornwall, Breton — Breton "in progress" per user decision 2026-06-08) in **EN + Gaeilge** with the other 5 Celtic languages as i18n placeholders.

| # | Space | Quadrant | 5-element tie | Tagline |
|--:|:--|:--|:--|:--|
| 1 | **An Scrúdú** | `oideachais` (Talamh) | Earth | 33 subjects, 17 years, 1 typed data pipeline |
| 2 | **Meaisín Cliste** | `meaisínfhoghlaim` (Uisce + Aer) | Water + Air | Foclóir + Scoil ar an Léarscáil + Curaclam Trasteorann, side-by-side |
| 3 | **Cianfhoghlaim** | `tuatha` (Aer + Anam) | Air + Spirit | Hades-style RPG on a navigable British Isles map called **Tuatha** |
| 4 | **Anam: Tuatha na nGaelscoil** | `croílár` (5 elements) | All 5 | The 5-element connective tissue integrating Spaces 1–3 |

**Headline number:** "10 OCR models, 6 Celtic languages, 5 elements, 1 typed pipeline."

---

## 5-Element Connective Tissue (the unifying theme)

Per `docs/bunchloch/tuatha/learn-to-earn-model.md:224-233`, the Four Treasures of the Tuatha Dé Danann + Anam map to school subjects:

| Element | Symbol | Subject mapping | Bridge to Space |
|:--|:--|:--|:--|
| **Talamh (Earth)** | Lia Fáil (Stone of Destiny) | Geography, Agricultural Science, History | Space 1 (curriculum + geographic layer) |
| **Uisce (Water)** | Cauldron of the Dagda | Biology, Chemistry, Home Economics | Space 2 (Curaclam Trasteorann cross-jurisdiction) |
| **Tine (Fire)** | Spear of Lugh | Physics, Maths, Applied Maths | the connective tissue (OCR + asset transformation) |
| **Aer (Air)** | Sword of Nuada | English, Irish, Filosofía | Space 2 (Foclóir) + Space 3 (NPC dialogue) |
| **Anam (Spirit)** | Anam (Soul) | meta-layer | Space 3 (soulbound SBT) + Space 4 (credential) |

The 4 Spaces map onto the elements. Space 4 ties them all together.

**Design tokens (unified palette):**
- `--celtic-emerald` `#28955e` — Talamh
- `--celtic-azure` `#1e80c6` — Uisce
- `--celtic-amber` `#d68c1c` — Tine
- `--celtic-indigo` `#5a4fcf` — Aer
- `--celtic-gold` `#cc9966` — Anam
- `--hades-base` `#1d1d2f` — Background

Per `docs/05-web/ui-components.md:381-384` and `docs/ui-inspiration/UI_INSPIRATION_GUIDE.md:159-188`.

---

## What changed in v3 (and why v1/v2 are superseded)

| v1 (5 Projects) | v2 (4+1 with Anam Bonneagar) | v3 (4 Spaces + 5 elements) |
|:--|:--|:--|
| Anam Celtic Learning Companion | An Scrúdú (oideachais) | An Scrúdú (oideachais) — kept |
| BackyardAI Formative Exit-Card Loop | Meaisín Cliste (3 themes) | Meaisín Cliste (3 themes) — kept |
| Físeán Feasa Voice Tutor | Brú na Bóinne (tuatha) | **Renamed: Cianfhoghlaim** (tuatha, 10 features, 6 Wikipedia NPCs) |
| Snáithe Prerequisite Graph Explorer | Anam Bonneagar (infrastructure) | **REMOVED entirely** — infrastructure archived; Anam Bonneagar becomes a per-Space footer |
| Anam Cara Soulbound Credential | Anam: Tuatha na nGaelscoil (croílár) | **Re-themes: Anam: Tuatha na nGaelscoil (croílár)** with 5-element framework (Talamh/Uisce/Tine/Aer/Anam) + 7 features (Tine / Uisce / Talamh / Aer / Anam / Mac Léinn / Fiosraigh) |

**Why the re-themes:**
1. The ccc + cognee audit revealed that the previous "OCR race" framing for Space 2 buried the meaisínfhoghlaim quadrant's actual identity (the multilingual AI brain for the cross-country Celtic pipeline).
2. The Wikipedia mythology scrape (Tuatha Dé Danann, Ulster, Fenian, Mabinogion + 6 specific articles for the 6 NPCs) revealed that the tuatha quadrant is fundamentally about Celtic mythology + soulbound credentials + the pent-elemental magic system.
3. The user wanted the integrated game to be the *actual* product (educational resource game on a navigable British Isles map), not a thin integration layer.
4. The 5-element framework (Talamh/Uisce/Tine/Aer/Anam) is the natural connective tissue between all 4 quadrants.

**What was REMOVED (v2 → v3):**
- Space 4 "Anam Bonneagar" (infrastructure) — REMOVED. The Pangolin topology + 6-file GOLD STANDARD linter + 3-way secret contract are **archived** for a later hackathon. The "Anam Bonneagar" footer (Pobal HP + 32B model alias + linter score) is the architectural homage.
- "Tri-Naomh" persona switcher (An Scrúdaí / An Teangeolaí / An Gaiscíoch) in Space 4 — REPLACED by the 5-element framework.
- "Brittany, Cornwall, Galicia" out-of-scope — REVERSED. Per user decision 2026-06-08, all 7 nations in scope (Breton "in progress").

**What was KEPT (v2 → v3):**
- The 4-Space architecture
- The 7-day schedule (with Space 3 moved to Day 2 for risk reduction)
- The 5 file artefacts to write on plan-mode exit
- The LiteLLM model fallback chains (Qwen2.5-7B → Llama-3.1-8B → Gemma-2-9b-it)
- The hybrid model layer (HF Inference for chat, BAML-compatible cloud model for extraction)
- The Anam SBT mounter on local Anvil (not real chain)
- The 6 Wikipedia NPC roster

---

## Re-themed Space 1 — "An Scrúdú" (oideachais, Talamh)

**Headline:** 33 subjects, 17 years, 1 typed data pipeline.

**8 features (5 new added in the audit):**
1. NCCA syllabus heatmap — 33 subjects × 17 years, weightPct × question frequency
2. Marking-scheme diff viewer — BAML `leaving_cert_marking_scheme_extraction.baml` year-on-year
3. Past-paper topic graph — force-directed prerequisite chain
4. PCLM-PDF marking-scheme pack — `document_factory/curriculum_document.py` A4 export
5. **NEW: Dúchas Manuscript Explorer** — Dúchas API data model from `docs/04-ai-ml/celtic-language-ai.md:223-400`
6. **NEW: Policy Circular Timeline** — `CircularMetadata` BAML schema from `docs/03-agents/baml-extraction.md:508-524`
7. **NEW: DPRE Live "New Papers Detected" Feed** — `DynamicPartitionsDefinition` sensor at `docs/02-data-platform/dagster-orchestration.md:198-218`
8. **NEW: Cross-Strand Prerequisite Heatmap + Pobal HP Context Overlay** — RDF/OWL `maths:validForLevel` + CSO Small Areas DLT source

**BAML schemas:**
- **Existing (reused):** `ExtractCurriculumSyllabus`, `ExtractPastPaper`, `ExtractMarkingScheme`, `ExtractLeavingCertSyllabus`
- **New (40-60 lines each):** `ExtractCircularMeta`, `GenerateExitCardQuestions`, `ScoreExitCardResponse`, `ComposeMarkingSchemeDiff`, `ExtractPrimaryFramework`

---

## Re-themed Space 2 — "Meaisín Cliste" (meaisínfhoghlaim, Uisce + Aer)

**Headline:** 3 themes side-by-side, 7 Celtic nations, 1 multilingual AI brain.

**3 themes × 7 features (4 new added in the audit):**

**Theme A — Foclóir na Sé Náisiún (Aer):**
1. Type English word → 7-nation cognate table (`oideachais/samplaí/cognates.yaml`)
2. Pronunciation playback (Chatterbox for 5 langs + mms-tts-ga for Irish)
3. **NEW: Live Terminology Cross-Reference** — GaDOIS Tearma API from `docs/04-ai-ml/celtic-language-ai.md:69-70`
4. **NEW: Bardic Grade Quiz** — Ollamh, Anruth, Clí, Cana, Doss, Macfuirmid, Fochlocon via BAML `CelticWord`
5. Etymology card (Proto-Celtic root)
6. In-context sentence generation in all 7 languages

**Theme B — Scoil ar an Léarscáil (Uisce):**
1. Leaflet map of 7 nations + every Celtic-medium school pinned
2. Click pin → school curriculum side-by-side with nearest cross-border peer
3. Pobal HP Deprivation Index filter
4. **NEW: Manx Bunscoill Ghaelgagh Micro-Model** — "How a 60-pupil school revived a language" data story from `docs/04-ai-ml/fine-tuning-guide.md:1189-1199`
5. **NEW: Scottish Gaelic Árainneachd (Environment) Geospatial Explorer** — H3 hex grid from `docs/06-product/celtic-mmo.md:365`

**Theme C — Curaclam Trasteorann (Aer):**
1. Ask curriculum question in EN/GA → 12 BAML agents vote via BAML `CompareCurricula` from `tuatha/baml_src/celtic_curriculum.baml:188-214`
2. Each agent shows its provenance jurisdiction
3. **NEW: SQA ↔ NCCA ↔ WJEC ↔ CCEA Alignment Matrix** — from `docs/06-product/educational-platform.md:67-74` + `docs/04-ai-ml/knowledge-graphs.md:389-413`
4. **NEW: Cornish & Breton Inclusion** — "The Forgotten Nations" panel from `docs/04-ai-ml/celtic-language-ai.md:59-60`
5. Cross-border credit transfer

**Headline metric:** RAGAS 22.7pp (65.2% → 87.9% per `meaisínfhoghlaim/evaluation/ragas_pipeline.py:737-738`).

**BAML schemas:**
- **Existing (reused):** `CelticWord`, `TerminologueEntry`, `CompareCurricula`
- **New (40-50 lines each):** `CrossBorderAlignment`, `BardicGrade`, `SchoolGeography`, `TerminologueEntry`

---

## Re-themed Space 3 — "Cianfhoghlaim" (tuatha, Aer + Anam)

**Headline:** Hades-style RPG on a navigable British Isles map called **Tuatha**.

**10 features (5 new added in the audit):**

1. **The Tuatha (British Isles) Map** — Babylon.js WebGPU scene with TopoJSON outline of 7 nations. Landscape tiles scraped from gov.ie + gov.uk official photo libraries. 4 diegetic mythology zones (Tuatha Dé Danann centred, Ulster, Fenian, Mabinogion).
2. **6 NPC roster** (Hades-style diegetic dialogue with knotwork borders) drawn from 6 specific Wikipedia articles:
   - **Uí Liatháin lord** (Loughcrew, Co. Meath) — `ga:Uí_Liatháin`
   - **Brec / Óengus** (the Déisi expellee, Rathmore, Co. Wicklow) — `en:The_Expulsion_of_the_Déisi`
   - **Manannán mac Lir** (Isle of Man) — `en:Manannán_mac_Lir`
   - **Rhiannon** (Prysgwyddion, Dyfed) — `en:Rhiannon`
   - **Dian Cécht** (the Leinster Healing Well) — `en:Dian_Cecht`
   - **Cian** (Loughcrew, Co. Meath) — `en:Cian`
3. **NEW: Uí Liatháin Exile Quest Chain** — traces Uí Liatháin migration Munster → Cornwall → Dyfed via BAML `MythologicalCharacter` (`tuatha/baml_src/mythology_extraction.baml:38-58`)
4. **NEW: Déisi Living Epic** — re-enactment of the Expulsion of the Déisi from Tara to Waterford via `MythologicalStory`
5. **NEW: Manannán's Ferryman's Trial** — 3 riddles via BAML `GenerateNPCDialogue` (level-gated)
6. **NEW: Rhiannon's Justice Mechanic** — investigate evidence via `CharacterRelationship` for branching narrative
7. **NEW: Cian's Sun-Gem Quest** — shape-shifting minigame (boar/wolf/hawk) using WGSL particle compute shader at `tuatha/crates/wgpu/celtic-shaders/src/lib.rs:1-19`
8. **Oideachais Dagster assets overlaid** as MotherDuck Dives (CSO Small Areas, Pobal HP, Ofsted/Estyn/ETI inspections, Met Éireann/BBC weather, Pobal Trutz Baicel 2022)
9. **Anam SBT mounter** — CuchulainnNFT.sol from `tuatha/apps/crypteolas demo/anam-contracts/src/CuchulainnNFT.sol` deployed on local Anvil (Hardhat Network, no real chain, no gas). 5-element system.
10. **Croílár BAML integration** — `tuatha/baml_src/curriculum_agent.py` + `tuatha/baml_src/celtic_curriculum.baml` for cross-nation curriculum comparison

**BAML schemas:**
- **Existing (reused):** `MythologicalCharacter`, `MythologicalStory`, `GenerateNPCDialogue`, `CharacterRelationship`
- **New (60 lines each):** `ExtractWikipediaArticle`, `EvaluateRiddleResponse`

---

## Re-themed Space 4 — "Anam: Tuatha na nGaelscoil" (croílár, All 5 elements)

**Headline:** "10 OCR models, 6 Celtic languages, 5 elements, 1 typed pipeline." The 5-element connective tissue integrating Spaces 1, 2, 3.

**The 5 elements act as the connective tissue between all 4 Spaces:**
- **Talamh (Earth)** = bridge to Space 1 (CurriculumDocument data model, exam paper metadata as geographic layer)
- **Uisce (Water)** = bridge to Space 2 (Curaclam Trasteorann cross-border curriculum)
- **Tine (Fire)** = the connective tissue (OCR pipeline raw→typed, BAML extraction, Fibo image gen)
- **Aer (Air)** = bridge to Space 2 + Space 3 (language tutoring, NPC dialogue, Celtic language bridge)
- **Anam (Spirit)** = the meta-layer (Anam SBT credential, SpacetimeDB SoulBond, EBSI Verifiable Credentials)

**7 features, one per element + 2 cross-cutting:**

| # | Feature | Element | Description |
|--:|:--|:--|:--|
| F1 | **Tine** — OCR-Powered Exam Paper Transformer | Fire | Upload scanned LC/JC paper → 10-model OCR race via `meaisínfhoghlaim/ocr/model_registry.py:330-543` → ColPali pipeline → typed markdown → BAML extraction → stored in Space 1 |
| F2 | **Uisce** — Chemistry/Biology Visual Asset Factory | Water | Curriculum topic → BAML → Fibo JSON → flame-test visuals, titration endpoints, molecular geometry (with PPE safety in negative prompts) |
| F3 | **Talamh** — Interactive British Isles Education Map | Earth | DuckDB-Spatial choropleth of all 7 Celtic nations; language vitality + educational attainment per LSOA + live Met Éireann weather; PostHog-OS draggable window system; per-language AI chat agents |
| F4 | **Aer** — Celtic Languages Curriculum Bridge | Air | BAML `CompareCurricula` cross-references NCCA/SQA/WJEC/CCEA/IoM/Cornwall/Breton syllabi. RAG-powered vocabulary tutoring in all 7 Celtic languages |
| F5 | **Anam** — Soulbound Credential & NFT Minting | Spirit | Every completed topic mints an Anam SBT (ERC-5192, non-transferable). 5 Anam types mapped to 5 elements. Anamchara peer-mentorship bonds. Dynamic Cúchulainn NFT (Sétanta → warrior → hero). EBSI Verifiable Credentials for major milestones |
| F6 | **Mac Léinn** — Formative Assessment from Real Exam Papers | All elements | Agno multi-agent pipeline takes real SEC papers → BAML SAP extracts structured questions → maps to LOs → generates MCQ "quiz battles" with Bloom's Taxonomy difficulty. Correct = Critical Hit |
| F7 | **Fiosraigh** — Classroom-to-MMO Bridge | All elements | Teacher scans ArUco cards → answers stream to SpacetimeDB → Oracle mints Tuath/Sét tokens → student's Cúchulainn avatar gains XP → x402 unlocks premium content. Federated Learning for voice |

**BAML schemas:**
- **Existing (reused):** `TerminologueEntry`, `CelticWord`, `CompareCurricula`, `GenerateAssessment`
- **New:** `FormativeQuestion`, `CrossBorderAlignment`, `ChemistryVisual`

---

## Cross-cutting bundle (one-time, Day 1)

Create `spaces/_common/` with:

- `baml_client_lite/` — pruned BAML client (drop unused clients) plus a `clients_hackathon.baml` re-pointed to HF Inference (Qwen 2.5 7B Instruct → Llama 3.1 8B → Gemma 2 9B; 32B cap respected)
- `theme_celtic.py` — custom 5-element colour palette + Celtic teal + Hades Shadow-First
- `soulbound_svg.py` — deterministic Celtic-knot SVG generator (no chain; static badge for demo)
- `social_card.py` — auto-renders the social-post card with the HF logo, project name, and a "Built at NUI Galway" line
- `demo_recorder.py` — 30-second screen-recording helper using `gradio` built-ins + `moviepy`
- `anam_bonneagar_footer.py` — small per-Space footer showing Pobal HP decile + 32B model alias + linter score
- `i18n.py` — bilingual EN/GA toggle (using `croilar/packages/i18n/` pattern)

---

## Schedule (7 days, locked)

| Day | Build | Cross-cutting |
|--:|:--|:--|
| **1 (Mon)** | Spin up `spaces/_common/` bundle; OpenSpec change dir; BAML re-pointing to HF Inference | 5 file artefacts written (catalogue, indexes, model fallback, OpenSpec change, this plan patch) |
| **2 (Tue)** | **Space 3** core: Babylon.js WebGPU canvas + 6 NPCs + 4 diegetic zones; demo video 1 (Cian → Manannán → Rhiannon flow) | MotherDuck Dive snapshots pre-computed; gov landscape scraping begins |
| **3 (Wed)** | **Space 1** core: BAML `ComposeMarkingSchemeDiff` + Gradio Blocks heatmap + PCLM-PDF emitter; demo video 2 | CuchulainnNFT.sol deployed to local Anvil; fada-accuracy preserved end-to-end |
| **4 (Thu)** | **Space 2** (3 themes in parallel): Foclóir + Scoil ar an Léarscáil + Curaclam Trasteorann; demo video 3 | 12-agent Q&A scaffolded; cross-border matrix built; Anam Bonneagar footer added |
| **5 (Fri)** | **Space 4** — 5 elements, 7 features: Tine → Uisce → Talamh → Aer → Anam → Mac Léinn → Fiosraigh; demo video 4 | All 5 Spaces polished; 5-element connective-tissue story is the demo narration |
| **6 (Sat)** | All Spaces polish: bilingual EN/GA verified, accessibility audit, mobile-responsive check, demo videos 1-4, social cards | OpenSpec `tasks.md` and `proposal.md` written |
| **7 (Sun)** | Final polish + HF Space submissions + OpenSpec `spec:validate croilar-hf-build-small-2026-demo --strict` + `spec:archive` after approval | Blog posts published; Twitter/Mastodon thread with 4 social cards |

---

## LiteLLM model fallback chains (per `doc/hackathons/build-small-2026-model-fallback.md`)

All models ≤ 32B. Primary: HF Inference (cloud).

| Role | Primary | Fallback 1 | Fallback 2 |
|:--|:--|:--|:--|
| BAML extraction | `Qwen/Qwen2.5-7B-Instruct` | `meta-llama/Llama-3.1-8B-Instruct` | `google/gemma-2-9b-it` |
| Chat / NPC dialogue | `meta-llama/Llama-3.1-8B-Instruct` | `mistralai/Mistral-7B-Instruct-v0.3` | `Qwen/Qwen2.5-7B-Instruct` |
| OCR / VLM | `Qwen/Qwen2-VL-7B-Instruct` | `microsoft/Phi-3.5-vision-instruct` | `google/paligemma-3b-mix-448` |
| Image gen (FIBO substitute) | `stabilityai/stable-diffusion-xl-base-1.0` | `black-forest-labs/FLUX.1-schnell` | n/a |
| Embeddings | `BAAI/bge-m3` | `sentence-transformers/all-MiniLM-L6-v2` | n/a |
| Speech | `openai/whisper-large-v3` | `openai/whisper-large-v3-turbo` | n/a |
| TTS | `ResembleAI/chatterbox` | `facebook/mms-tts-ga` | n/a |

**Anam SBT mounter:** local Anvil sidecar with CuchulainnNFT.sol (5-element system, 3 stages Sétanta → Cúchulainn → Ríastrad).

**Cost estimate (8-day hackathon):** ~$3.55 (well within free tier).

---

## Risk + mitigation

- **HF Inference latency for BAML extraction** → 3-tier fallback chain (Qwen2.5-7B → Llama-3.1-8B → Gemma-2-9b-it) automatically retries.
- **BAML schemas need a cloud client for each Space** → fork `tuatha_clients.baml` → `clients_hackathon.baml` re-pointed to HF Inference; the long-term monorepo `client LiteLLM` stays untouched.
- **BAML client name collision in the merged `baml_client/`** → follow the same renaming convention as `tuatha/baml_src/clients.baml` → `tuatha_clients.baml`.
- **Spaces boot time with bundled models** → use HF Inference for chat (fast cold start); only bundle the model in Space 4 (Anvil sidecar, no chat model).
- **Fada / tironian / punctum delens preservation** → every BAML function uses `_normalize_irish_text()` from `meaisínfhoghlaim/ocr/gaelic_metrics.py:28-61`; fada-accuracy verified at every step.
- **Anvil sidecar in Space 4 may not start on HF Spaces (CPU-only, no GPU)** → fall back to deterministic SVG-only mounter (no live chain).
- **7-nation scope is wider than the data** → 6 nations (RoI, NI, Wales, Manx, Scottish, Cornish) have substantial data; Breton is "in progress" placeholder.

---

## Files written alongside this plan (5 files)

1. `doc/hackathons/build-small-2026-docs-catalogue.md` — consolidated catalogue (Tier-1 / Tier-2 / Tier-3 / demo-stack mapping / refactor hooks / 22 known-drift items)
2. `doc/hackathons/croilar-demo-quadrant-indexes.md` — per-quadrant asset indexes
3. `doc/hackathons/build-small-2026-model-fallback.md` — LiteLLM model fallback chains
4. `openspec/changes/croilar-hf-build-small-2026-demo/{proposal.md, tasks.md, specs/croilar-gradio-hf-demo/spec.md}` — OpenSpec change bundle (validated `--strict`)
5. `doc/hackathons/build-small-2026-plan.md` (this file, re-themes section appended)

**OpenSpec capability added:** `croilar-gradio-hf-demo` to `openspec/project.md`.
