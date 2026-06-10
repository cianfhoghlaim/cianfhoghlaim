---
title: "Build Small 2026 — Hackathon Documentation Catalogue"
domain: hackathons
status: draft
description: "Consolidated catalogue of the docs, BAML schemas, assets, and patterns from the Cianfhoghlaim monorepo that inform the 4 Gradio Spaces submitted to the HuggingFace 'Build Small 2026' hackathon (deadline 15 June 2026)."
entities:
  - BuildSmall2026
  - AnScrúdú
  - MeaisínCliste
  - Cianfhoghlaim
  - AnamTuathaNaNGaelscoil
  - PobalHP
  - DeprivationIndex
related_skills:
  - .agents/skills/dagster/SKILL.md
  - .agents/skills/dlt/SKILL.md
  - .agents/skills/cognee/SKILL.md
  - .agents/skills/ccc/SKILL.md
  - .agents/skills/oideachas-pipeline/SKILL.md
ccc_query_hints:
  - "hackathon space 1 an scrúdú BAML extraction"
  - "hackathon space 2 meaisín cliste 5-element framework"
  - "hackathon space 3 cianfhoghlaim Hades diegetic UI"
  - "hackathon space 4 anam tuatha 5 elements anam nft"
  - "build small 2026 catalogue BAML schema directory"
last_reviewed: 2026-06-08
---

# Build Small 2026 — Hackathon Documentation Catalogue

> **Status:** Draft v3 (post re-themes). 4 Spaces. 7 Celtic nations. 5-element framework. 7-day schedule.
> **Deadline:** 15 June 2026. **Builder:** Cian Mac an Déisigh Uí Liatháin. **HF org:** `build-small-hackathon` (already registered, 165 Spaces / 13 models / 13 datasets live as of 08 June 2026).

---

## TL;DR

The 4-Space lineup is **the 5-element connective tissue** between the existing Cianfhoghlaim quadrants. The 5 elements (Talamh / Uisce / Tine / Aer / Anam) map onto the existing assets:

- **Talamh (Earth)** = syllabus + curriculum + geographic layer → `oideachais/`, Space 1
- **Uisce (Water)** = chemistry/biology visual asset gen + nurturing the RAG → `meaisínfhoghlaim/`, Space 2 themes
- **Tine (Fire)** = OCR + asset transformation pipeline → the connective tissue itself, Space 4
- **Aer (Air)** = language + rhetoric + NPC dialogue → Celtic languages + Space 3
- **Anam (Spirit)** = soulbound credentials + Anamchara mentorship + the meta-narrative

| # | Space | Quadrant | Element(s) | Tagline |
|--:|:--|:--|:--|:--|
| 1 | **An Scrúdú** | `oideachais` | Talamh | 33 subjects, 17 years, 1 typed data pipeline |
| 2 | **Meaisín Cliste** | `meaisínfhoghlaim` | Uisce + Aer | Foclóir + Scoil ar an Léarscáil + Curaclam Trasteorann side-by-side |
| 3 | **Cianfhoghlaim** | `tuatha` | Aer + Anam | Hades-style RPG on a navigable British Isles map |
| 4 | **Anam: Tuatha na nGaelscoil** | `croílár` | All 5 elements | The 5-element connective tissue integrating Spaces 1-3 |

7-nation scope (per user decision 2026-06-08): **Republic of Ireland, Northern Ireland, Wales, Isle of Man (Manx), Scotland, Cornwall (Cornish), Brittany (Breton — "in progress")**.

---

## 1. Top-30 Tier-1 (Relevance 5) Documents

The 30 documents the plan must quote from directly. All have a confirmed, deep mapping to a demo subsystem.

| # | Path | Quadrant | One-line summary | Primary tag |
|--:|:--|:--|:--|:--|
| 1 | `docs/00_index.md` | cross-cutting | Master routing table — 36 canonical docs across 7 domains, Cognee-clean frontmatter. | platform-overview |
| 2 | `docs/01-platform-architecture/platform-overview.md` | cross-cutting | Pangolin convergence + the Quadrant Model. | platform-overview |
| 3 | `docs/01-platform-architecture/monorepo-strategy.md` | cross-cutting | bun + uv + turbo polyglot monorepo. | monorepo-strategy |
| 4 | `docs/01-platform-architecture/secrets-management.md` | cross-cutting | Infisical → `.infisical.env` → `.env` three-way secret contract. | secrets-management |
| 5 | `docs/02-data-platform/data-architecture.md` | oideachais | DuckDB / DuckLake / Iceberg / Garage S3 / R2 / MotherDuck / LanceDB. | data-architecture |
| 6 | `docs/02-data-platform/dagster-orchestration.md` | oideachais | Dagster assets, partitions, sensors, `dg` workspace. | dagster |
| 7 | `docs/02-data-platform/dlt-pipelines.md` | oideachais | DLT filesystem/REST sources, incremental loads. | dlt |
| 8 | `docs/03-agents/baml-extraction.md` | cross-cutting | BAML schemas, Irish education extraction. | baml-extraction |
| 9 | `docs/03-agents/agent-frameworks.md` | cross-cutting | Agno AgentOS, Google ADK, CopilotKit, Pydantic AI. | agent-frameworks |
| 10 | `docs/03-agents/mcp-servers.md` | cross-cutting | MCP protocol, OAuth/x402/SIWE auth. | mcp |
| 11 | `docs/04-ai-ml/celtic-language-ai.md` | meaisínfhoghlaim | 23,847-line consolidated corpus: Irish/Welsh/Scottish/Manx/Cornish/Breton NLP. | celtic-language-ai |
| 12 | `docs/04-ai-ml/ocr-htr.md` | meaisínfhoghlaim | ColPali, Docling, DeepSeek-OCR, Qwen-VL, Gaelic script, eScriptorium, PyLaia. | ocr-htr |
| 13 | `docs/04-ai-ml/rag-evaluation.md` | meaisínfhoghlaim | RAGAS metrics, federated RAG, IRLBench. | ragas |
| 14 | `docs/04-ai-ml/knowledge-graphs.md` | meaisínfhoghlaim | Cognee, Graphiti, Memgraph, FalkorDB. | knowledge-graph |
| 15 | `docs/04-ai-ml/fine-tuning-guide.md` | meaisínfhoghlaim | Unsloth, LoRA/QLoRA, GGUF, MLX, Qwen3-VL. | fine-tuning |
| 16 | `docs/04-ai-ml/ml-pipelines.md` | meaisínfhoghlaim | MLflow, Langfuse, LiteLLM gateway, MLX/Metal/GGUF. | ml-pipelines |
| 17 | `docs/04-ai-ml/vector-embeddings.md` | meaisínfhoghlaim | LanceDB, Qdrant, BGE-M3 / ColPali, CocoIndex. | vector-embeddings |
| 18 | `docs/06-product/celtic-mmo.md` | tuatha | Tuatha Celtic MMO: SpacetimeDB, Anam Cara, Ogham stones, mythology cycles, multi-agent AI. | celtic-mmo |
| 19 | `docs/06-product/educational-platform.md` | tuatha | Leaving Cert mapping (Oral 40% / Aural 10% / Paper 1 25% / Paper 2 25%), AI tutor. | educational-platform |
| 20 | `docs/06-product/game-development.md` | tuatha | Godot 4 + Rust (gdext), wgpu, Babylon.js + WebGPU, particle effects. | game-development |
| 21 | `docs/06-product/crypteolas.md` | tuatha | x402 HTTP-402 payments, SIWE, Tuath token, Learn-to-Earn. | crypteolas |
| 22 | `docs/05-web/frontend-stack.md` | cross-cutting | TanStack Start, React 19, SSR, Effect-TS, oRPC, Vite. | frontend-stack |
| 23 | `docs/05-web/convex-hono-auth.md` | cross-cutting | Convex, Hono, BetterAuth, SIWE, multi-tenant, AG-UI. | convex-hono-auth |
| 24 | `docs/05-web/ui-components.md` | cross-cutting | shadcn/ui, CopilotKit, dnd-kit, MCP-UI, data viz. | ui-components |
| 25 | `docs/07-standards/project-conventions.md` | cross-cutting | Naming conventions, technology constraints, Irish-language requirements, BAML validation. | project-conventions |
| 26 | `docs/07-standards/observability-patterns.md` | cross-cutting | Datadog APM/LLMObs, MLflow, Langfuse, Ragas, structlog. | observability-patterns |
| 27 | `docs/cognee/COGNEE_INTEGRATION.md` | cross-cutting | Dagster asset graph for `docs_added_to_cognee` → `docs_cognified` → `graphiti_temporal_layer`. | cognee |
| 28 | `docs/cognee/CCC_INTEGRATION.md` | cross-cutting | CCC (CocoIndex Code) semantic code search + CocoIndex flows. | ccc |
| 29 | `docs/cognee/ARCHITECTURE.md` | cross-cutting | Cognee service architecture, datasets, vector+graph storage backend. | cognee |
| 30 | `docs/archive/tuatha-mirror/celtic-ocr.md` | tuatha | ColPali + Unsloth + MLX iPhone HTR pipeline for Qwen2-VL on Irish handwriting. | celtic-ocr |

---

## 2. The 4-Space Feature Inventory (re-themed, post-audit)

### Space 1 — "An Scrúdú" (oideachais, Talamh element)

**Headline:** 33 subjects, 17 years, 1 typed data pipeline.

**8 features:**
1. **NCCA syllabus heatmap** — every LO in every Leaving Cert subject, colour-coded against the 6-year attainment distribution from `oideachais/data_platform/`.
2. **Marking-scheme diff viewer** — BAML `leaving_cert_marking_scheme_extraction.baml` output rendered side-by-side year-on-year.
3. **Past-paper topic graph** — force-directed graph linking topics to their prerequisite chain (consumed by Space 2).
4. **PCLM-PDF marking-scheme pack** — `document_factory/curriculum_document.py` re-emits a printable A4 PCLM pack for chosen year × subject.
5. **NEW: Dúchas Manuscript Explorer** — Surfaces the National Folklore Collection via the Dúchas API data model from `docs/04-ai-ml/celtic-language-ai.md:223-400`. Browse by county/story.
6. **NEW: Policy Circular Timeline** — Uses the `CircularMetadata` BAML schema at `docs/03-agents/baml-extraction.md:508-524` to render a temporal graph of `CircularStatus`.
7. **NEW: DPRE Live "New Papers Detected" Feed** — Exposes the DynamicPartitionsDefinition sensor pattern at `docs/02-data-platform/dagster-orchestration.md:198-218`.
8. **NEW: Cross-Strand Prerequisite Heatmap + Pobal HP Context Overlay** — From the RDF/OWL `maths:validForLevel` at `docs/04-ai-ml/knowledge-graphs.md:402-412` and CSO Small Areas DLT source at `oideachais/data_platform/dlt_sources/geospatial/cso_small_areas.py:342-371`.

**BAML schemas to ship:**
- **Existing:** `ExtractCurriculumSyllabus` (`oideachais/data_platform/baml_src/curriculum_extraction.baml:24-45`), `ExtractPastPaper` (`:30-54`), `ExtractMarkingScheme` (`:39-65`), `ExtractLeavingCertSyllabus` (`:28-49`).
- **New (30-40 lines each):** `ExtractCircularMeta`, `GenerateExitCardQuestions`, `ScoreExitCardResponse` (modelled on `ResponseAnalysis` from `tuatha/baml_src/player_assessment.baml:31`), `ComposeMarkingSchemeDiff`.

**Data sources:** `oideachais/data_platform/` Dagster assets, `oideachais/samplaí/gaeilge/irish_samples.yaml`, `oideachais/quality/completeness.py`.

**Packages:** `oideachais/data_platform/baml_src/`, `oideachais/quality/`, the `document_factory/curriculum_document.py` PCLM emitter.

**Design tokens:** NCCA-branded palette (deep green + amber + stone gray) from `docs/05-web/ui-components.md:381-384`; Cinzel/Cormorant serif headers; Hades-inspired `--hades-base: #1d1d2f` + `--hades-gold: #cc9966` from `docs/ui-inspiration/UI_INSPIRATION_GUIDE.md:159-188`.

---

### Space 2 — "Meaisín Cliste" (meaisínfhoghlaim, Uisce + Aer elements)

**Headline:** Foclóir + Scoil ar an Léarscáil + Curaclam Trasteorann side-by-side, in 7 Celtic languages.

**3 themes × 7 features:**

**Theme A — Foclóir na Sé Náisiún (Aer):**
1. Type an English word → get a 6-nation cognate table (RoI Irish, NI Irish, Welsh, Manx Gaelic, Scottish Gaelic, Cornish) + Breton "in progress" badge.
2. **NEW: Live Terminology Cross-Reference** — GaDOIS Tearma API holds 20+ specialised dictionaries (`docs/04-ai-ml/celtic-language-ai.md:69-70`).
3. **NEW: Bardic Grade System Quiz** — Maps the historical 7-grade system (Ollamh, Anruth, Clí, Cana, Doss, Macfuirmid, Fochlocon) to vocabulary breadth via BAML `CelticWord`.
4. Etymology card showing the cognate's Proto-Celtic root.
5. In-context sentence generation in all 7 languages.

**Theme B — Scoil ar an Léarscáil (Uisce):**
1. Leaflet/OpenLayers map of the 7 nations with every Gaeltacht, Irish-medium, Welsh-medium, Scottish Gaelic-medium, Manx-medium, Cornish-medium, Breton-medium school pinned.
2. Click a pin → school's curriculum (e.g. "Scoil Bhríde, Gaeltacht na Mí") is shown side-by-side with its nearest cross-border peer.
3. Filter by Pobal HP Deprivation Index decile.
4. **NEW: Manx Bunscoill Ghaelgagh Micro-Model** — "How a 60-pupil school revived a language" data story.
5. **NEW: Scottish Gaelic Árainneachd (Environment) Geospatial Explorer** — H3 hex grid overlay for Gaelic-medium school density.

**Theme C — Curaclam Trasteorann (Aer):**
1. Ask a curriculum question in EN or GA → 12 specialised BAML agents vote on the answer.
2. Each agent shows its provenance.
3. **NEW: SQA ↔ NCCA ↔ WJEC ↔ CCEA Alignment Matrix** — Interactive cross-jurisdiction matrix with green/red outcome overlap.
4. **NEW: Cornish & Breton Inclusion** — "The Forgotten Nations" panel showing Cornish medium + Breton Diwan school data.
5. Cross-border credit transfer.

**Cross-cutting improvements:**
- **Shared i18n component** with 7-language toggle (ga, cy, gd, gv, kw, br, en).
- **Shared British Isles Map Component** using DuckDB Spatial + LanceDB geospatial pattern + H3 indexing.

**BAML schemas to ship:**
- **Existing:** `CelticWord` (`tuatha/baml_src/celtic_curriculum.baml:59-68`), `TerminologueEntry` (pattern from GaDOIS), `CompareCurricula` (`:188-214`).
- **New (40 lines):** `CrossBorderAlignment` with `learning_outcome (ga, en)`, `subject`, `level`, `jurisdiction`, `equivalent_outcomes`.

**Data sources:** gov.ie / gov.uk / school.wales / Education Scotland / DESC Isle of Man / Cornwall Council; Pobal HP Deprivation Index 2022; Canúint dialect audio.

**Design tokens:** 7-nation colour palette (Green-RoI, Red-Wales, Blue-Scotland, Gold-IoM, Black&White-Cornwall, Bleu-Blanc-Rouge accents for Brittany). Cinzel for titles across all 7 languages.

---

### Space 3 — "Cianfhoghlaim" (tuatha, Aer + Anam elements)

**Headline:** Hades-style RPG on a navigable British Isles map called **Tuatha**, with the 6 NPC roster drawn from 6 specific Wikipedia articles, the geography syllabus informing the map, the government landscape images scraped from gov.ie + gov.uk, the oideachais Dagster assets overlaid as MotherDuck Dives, and the Anam soulbound credentials mounted on local Anvil.

**10 features (5 new + 5 original):**

1. **The Tuatha (British Isles) Map** — Babylon.js WebGPU scene with TopoJSON outline. 7 nations/regions: RoI, NI, Wales, Manx, Scottish, Cornish, English. Landscape tiles scraped from gov.ie + gov.uk official photo libraries.
2. **4 diegetic zones** for the 4 mythology cycles (Tuatha Dé Danann centred, Ulster, Fenian, Mabinogion), each with a WGSL Celtic-knot shader.
3. **6 NPC roster** (Hades-style diegetic dialogue with knotwork borders):
   - **Uí Liatháin lord** (Loughcrew, Co. Meath) — ga:Uí_Liatháin
   - **Brec / Óengus** (the Déisi expellee, Rathmore, Co. Wicklow) — en:Expulsion_of_the_Déisi
   - **Manannán mac Lir** (Isle of Man) — en:Manannán_mac_Lir
   - **Rhiannon** (Prysgwyddion, Dyfed) — en:Rhiannon
   - **Dian Cécht** (the Leinster Healing Well) — en:Dian_Cecht
   - **Cian** (Loughcrew, Co. Meath) — en:Cian
4. **NEW: Uí Liatháin Exile Quest Chain** — traces Uí Liatháin migration from Munster to Cornwall to Dyfed. Dialogue via BAML `MythologicalCharacter` (`tuatha/baml_src/mythology_extraction.baml:38-58`).
5. **NEW: Déisi Living Epic** — re-enactment of the Expulsion of the Déisi from Tara to Waterford. Powered by `MythologicalStory`.
6. **NEW: Manannán's Ferryman's Trial** — 3 riddles via BAML `GenerateNPCDialogue` (level-gated). Correct answers grant passage.
7. **NEW: Rhiannon's Justice Mechanic** — investigate evidence via `CharacterRelationship` schema for branching narrative.
8. **NEW: Cian's Sun-Gem Quest** — shape-shifting minigame (boar/wolf/hawk) using WGSL particle compute shader at `tuatha/crates/wgpu/celtic-shaders/src/lib.rs:1-19`.
9. **Oideachais Dagster assets overlaid** as MotherDuck Dives (CSO Small Areas, Pobal HP, Ofsted/Estyn/ETI inspections, Met Éireann/BBC weather, Pobal Trutz Baicel 2022).
10. **Anam SBT mounter** — CuchulainnNFT.sol from `tuatha/apps/crypteolas_demo/anam-contracts/` deployed on local Anvil (Hardhat Network, no real chain). 5-element system: Knowledge, Skill, Creativity, Community, Sovereignty.

**BAML schemas to ship:**
- **Existing:** `MythologicalCharacter` (`:38-58`), `MythologicalStory` (`:88-104`), `GenerateNPCDialogue` (`:189-219`), `CharacterRelationship` (`:67-71`).
- **New (60 lines each):** `ExtractWikipediaArticle`, `EvaluateRiddleResponse` (modelled on `MarkingPoint` from `docs/03-agents/baml-extraction.md:462-469`).

**Hades-diegetic-UI patterns:**
- **Boon Selection (3 vertical choices)** with deity colours (Lugh = gold, the Dagda = brown, the Morrígan = crimson) from `docs/ui-inspiration/UI_INSPIRATION_GUIDE.md:167-168`.
- **Chiaroscuro character portraits** from `tuatha/summary.txt:590-596`.
- **Shadow-First Palette with Celtic Knotwork UI Borders** — gold `#cc9966` on dark base.

**MotherDuck Dive / TanStack / CopilotKit patterns:**
- MotherDuck Dive for "Player Progress Across the British Isles" (from `croilar/dagster_assets/dlt_assets.py:169-195`).
- TanStack Start isomorphic functions for game state (`docs/05-web/frontend-stack.md:329-342`).
- CopilotKit `useCopilotAction` for NPC interaction (`docs/05-web/ui-components.md:220-236`).

**Design tokens:**
- **Hades Shadow-First + Celtic Gold** — `--hades-base: #1d1d2f`, `--hades-gold: #cc9966`, `--celtic-emerald: #2d5a3d`.
- **6 NPC Portrait Styles from 6 Mythological Cycles** — each cycle has a distinct visual tradition (Mythological = illuminated manuscript, Ulster = dark martial iron-age, Fenian = woodland natural, Mabinogion = Arthurian romantic).

---

### Space 4 — "Anam: Tuatha na nGaelscoil" (croílár, All 5 elements)

**Headline:** "10 OCR models, 6 Celtic languages, 5 elements, 1 typed pipeline." The 5-element connective tissue integrating Spaces 1-3.

The 5 elements act as the **connective tissue** between all 4 Spaces:
- **Talamh (Earth)** = bridge to Space 1 (CurriculumDocument data model, exam paper metadata as geographic layer).
- **Uisce (Water)** = bridge to Space 2's Curaclam Trasteorann (cross-border curriculum).
- **Tine (Fire)** = the connective tissue (OCR pipeline raw→typed, BAML extraction, Fibo image gen).
- **Aer (Air)** = bridge to Space 2 + Space 3 (language tutoring, NPC dialogue, Celtic language bridge).
- **Anam (Spirit)** = the meta-layer (Anam SBT credential, SpacetimeDB SoulBond, EBSI Verifiable Credentials).

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

**BAML schemas to ship:**
- **Existing:** `TerminologueEntry` (pattern from GaDOIS), `CelticWord`, `CompareCurricula`, `GenerateAssessment` (`:158-176`).
- **New:** `FormativeQuestion` (modelled on `MarkingPoint`), `CrossBorderAlignment`, `ChemistryVisual` (Fibo JSON).

**Data sources:** gov.ie / gov.uk / school.wales / Education Scotland / DESC IoM / Cornwall Council / Breton Diwan; Pobal HP Deprivation Index 2022; Canúint; Dúchas Schools' Collection; NCCA / SQA / WJEC / CCEA syllabi; Leabhar Ua Maine genealogies; CELT corpus.

**Design tokens:** 5-element colour system (Talamh=emerald, Uisce=azure, Tine=amber, Aer=indigo, Anam=gold), Hades Shadow-First base, Celtic knotwork UI borders.

---

## 3. Tier-2 (Relevance 4) — 60 documents

| # | Path | Quadrant | Summary | Tag |
|--:|:--|:--|:--|:--|
| 31 | `docs/01-platform-architecture/infrastructure-stacks.md` | cross-cutting | 89 Docker Compose stacks. | infrastructure-stacks |
| 32 | `docs/01-platform-architecture/komodo-gitops.md` | cross-cutting | Komodo Core/Periphery, GitOps. | komodo |
| 33 | `docs/01-platform-architecture/pangolin-networking.md` | cross-cutting | Traefik, WireGuard, Pocket ID. | pangolin |
| 34 | `docs/01-platform-architecture/kubernetes-deployment.md` | cross-cutting | Talos, Pulumi, Ansible. | pulumi |
| 35 | `docs/03-agents/browser-automation.md` | cross-cutting | Browserbase, Stagehand V3, Firecrawl, Smolagents. | browser-automation |
| 36 | `docs/03-agents/README.md` | cross-cutting | Agents domain index. | index |
| 37 | `docs/02-data-platform/README.md` | oideachais | Data platform index. | data-platform |
| 38 | `docs/04-ai-ml/README.md` | meaisínfhoghlaim | AI/ML domain index. | ai-ml |
| 39 | `docs/05-web/README.md` | cross-cutting | Web domain index. | web |
| 40 | `docs/06-product/README.md` | tuatha | Product domain index. | product |
| 41 | `docs/cognee/COGNEE_SETUP.md` | cross-cutting | Local Cognee docker-compose. | cognee |
| 42 | `docs/cognee/INGESTION.md` | cross-cutting | Cognee `add` / `cognify` / `search` patterns. | cognee |
| 43 | `docs/cognee/WORKFLOW.md` | cross-cutting | End-to-end docs → Cognee workflow. | cognee |
| 44 | `docs/cognee/MCP_SERVERS.md` | cross-cutting | Cognee MCP server config. | cognee, mcp |
| 45 | `docs/cognee/LANGFUSE_OBSERVABILITY.md` | cross-cutting | Langfuse tracing of Cognee cognify calls. | langfuse |
| 46 | `docs/cognee/INFRASTRUCTURE.md` | cross-cutting | Cognee on Komodo. | cognee |
| 47 | `docs/cognee/README.md` | cross-cutting | Cognee subdirectory entrypoint. | cognee |
| 48 | `docs/bunchloch/tuatha/SpacetimeDB.md` | tuatha | SpacetimeDB module + Rust server. | spacetimedb |
| 49 | `docs/bunchloch/tuatha/SPACETIMEDB_GUIDE.md` | tuatha | Longer SpacetimeDB reference. | spacetimedb |
| 50 | `docs/bunchloch/tuatha/repo-SpacetimeDB.md` | tuatha | SpacetimeDB upstream README. | spacetimedb |
| 51 | `docs/bunchloch/tuatha/repo-spacetimedb-cookbook.md` | tuatha | SpacetimeDB cookbook. | spacetimedb |
| 52 | `docs/bunchloch/tuatha/repo-spacetimedb-typescript-sdk.md` | tuatha | TypeScript SDK. | spacetimedb, typescript |
| 53 | `docs/bunchloch/tuatha/repo-hophacks-spacetimedb-workshop.md` | tuatha | SpacetimeDB hackathon workshop. | spacetimedb, hackathon-narrative |
| 54 | `docs/bunchloch/tuatha/GODOT_RUST_GUIDE.md` | tuatha | Godot 4 + gdext + SpacetimeDB. | godot, rust |
| 55 | `docs/bunchloch/tuatha/gdext-ReadMe.md` | tuatha | gdext crate README. | godot, rust |
| 56 | `docs/bunchloch/tuatha/WGPU_GUIDE.md` | tuatha | wgpu renderer, Celtic shaders. | wgpu, rust, webgpu |
| 57 | `docs/bunchloch/tuatha/Rust Client.md` | tuatha | Rust SpacetimeDB client. | rust, spacetimedb |
| 58 | `docs/bunchloch/tuatha/Rust Full-Stack Gaming Environment.md` | tuatha | End-to-end Rust + Godot + wgpu. | rust, godot |
| 59 | `docs/bunchloch/tuatha/mythology-framework.md` | tuatha | Full mythological cycle design. | mythology, dae-danann |
| 60 | `docs/bunchloch/tuatha/celtic_mmo.md` | tuatha | Original Celtic MMO design. | celtic-mmo |
| 61 | `docs/bunchloch/tuatha/SpacetimeDB Ogham Stone Game Integration.md` | tuatha | Ogham stone quest integration. | spacetimedb, mythology |
| 62 | `docs/bunchloch/tuatha/British Isles Mythology MMO Research.md` | tuatha | Long-form mythology research. | mythology |
| 63 | `docs/bunchloch/tuatha/British Isles Education Map.md` | tuatha | Education standards per region. | irish-education, uk-education |
| 64 | `docs/bunchloch/tuatha/CELTIC_LANGUAGES.md` | tuatha | Celtic languages reference. | celtic-languages |
| 65 | `docs/bunchloch/tuatha/Celtic Etymology for Game Names.md` | tuatha | Proto-Celtic lexicography. | celtic-languages |
| 66 | `docs/bunchloch/tuatha/Celtic Language Data Aggregation & Analysis.md` | tuatha | Data aggregation strategy. | celtic-languages |
| 67 | `docs/bunchloch/tuatha/Agentic Education Platform Development.md` | tuatha | Agentic pattern for Celtic education. | agentic-rag, mythology |
| 68 | `docs/bunchloch/tuatha/PIPELINES.md` | tuatha | Pipeline orchestration summary. | dagster, dlt |
| 69 | `docs/bunchloch/tuatha/CRYPTO_INTEGRATION_SUMMARY.md` | tuatha | Crypto integration condensed. | crypteolas |
| 70 | `docs/bunchloch/tuatha/CRYPTEOLAS_INTEGRATION_GUIDE.md` | tuatha | Crypteolas walkthrough. | crypteolas |
| 71 | `docs/bunchloch/tuatha/learn-to-earn-model.md` | tuatha | Learn-to-Earn — 4 Treasures → 5 elements. | learn-to-earn, mythology |
| 72 | `docs/bunchloch/tuatha/Learn-to-Earn Blockchain and AI.md` | tuatha | Learn-to-Earn blockchain + AI. | learn-to-earn, mythology |
| 73 | `docs/bunchloch/tuatha/PAYMENT_GUIDE.md` | tuatha | x402 payment flow. | x402 |
| 74 | `docs/bunchloch/tuatha/x402-payments.md` | tuatha | x402 protocol details. | x402 |
| 75 | `docs/bunchloch/tuatha/repo-x402.md` | tuatha | x402 repo reference. | x402 |
| 76 | `docs/bunchloch/tuatha/game_siwe-auth.md` | tuatha | SIWE auth for the game. | siwe, soulbound |
| 77 | `docs/bunchloch/tuatha/Sign In With Ethereum (SIWE) _ Better Auth.md` | cross-cutting | BetterAuth SIWE plugin. | siwe |
| 78 | `docs/bunchloch/tuatha/ERC-4361_ Sign-In with Ethereum.md` | cross-cutting | ERC-4361 spec reference. | siwe |
| 79 | `docs/bunchloch/tuatha/Comparing the Top 6 Agent-Native Rails for the Agentic Internet_ MCP, A2A, AP2, ACP, x402, and Kite.md` | cross-cutting | Comparison: MCP / A2A / x402 / AG-UI / ACP / Kite. | mcp, x402, ag-ui |
| 80 | `docs/bunchloch/agents/BAML_COMPREHENSIVE_GUIDE.md` | cross-cutting | Pre-consolidation BAML guide. | baml-extraction |
| 81 | `docs/bunchloch/agents/BAML Schemas for Irish Education.md` | cross-cutting | BAML for Leaving Cert. | baml-extraction, leave-cert |
| 82 | `docs/bunchloch/agents/BAML for Syllabus-Driven Data Extraction.md` | cross-cutting | BAML driven by NCCA syllabus. | baml-extraction, irish-education |
| 83 | `docs/bunchloch/agents/BAML_DUCKDB_DRAGONFLY_ANALYSIS.md` | cross-cutting | BAML output → DuckDB/Dragonfly cache. | baml-extraction, duckdb, dragonfly |
| 84 | `docs/bunchloch/agents/IRISH_EDUCATION_PLATFORM_BLUEPRINT.md` | cross-cutting | End-to-end Irish education platform design. | irish-education, mythology |
| 85 | `docs/bunchloch/agents/MCP_COMPREHENSIVE_RESEARCH.md` | cross-cutting | Pre-consolidation MCP research. | mcp |
| 86 | `docs/archive/tuatha-mirror/celtic-ocr.md` | tuatha | ColPali + Unsloth + MLX iPhone HTR pipeline. | celtic-ocr |
| 87 | `docs/archive/tuatha-mirror/Web3 Gamified Education & Asset Generation.md` | tuatha | Web3 gamified education design. | fibo, soulbound |
| 88 | `docs/archive/tuatha-mirror/SpacetimeDB Ogham Stone Game Integration.md` | tuatha | Ogham stone + SpacetimeDB + Solana. | spacetimedb, ogham |
| 89 | `docs/archive/tuatha-mirror/AI Chemistry Education Image Generation.md` | tuatha | Bria Fibo + BAML educational imagery. | fibo, bria, baml |
| 90 | `docs/archive/tuatha-mirror/Building an Educational Agent's Knowledge Base.md` | tuatha | Agno + MCP educational agent pipeline. | agent, knowledge-graph |

---

## 4. Tier-3 (Relevance 3) — 60 documents

| # | Path | Summary | Tag |
|--:|:--|:--|:--|
| 91 | `docs/ARCHITECTURE_RATIONALE.md` | Why-Quadrant, why-Pangolin. | architecture-rationale |
| 92 | `docs/ARCHITECTURE_DEPLOYMENT.md` | End-to-end deployment. | deployment |
| 93 | `docs/BROWSERBASE_MCP_VERTEX_PATCH_NOTES.md` | Browserbase MCP + Vertex. | browser-automation |
| 94 | `docs/bunchloch/agents/BROWSER_AUTOMATION_PLATFORM.md` | Browser automation platform. | browser-automation |
| 95 | `docs/bunchloch/agents/STAGEHAND_COMPREHENSIVE_REFERENCE.md` | Stagehand V3 reference. | browser-automation |
| 96 | `docs/bunchloch/agents/GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md` | Google ADK detailed reference. | agent-frameworks |
| 97 | `docs/bunchloch/agents/PYDIANTIC_AI_REFERENCE.md` | Pydantic AI patterns. | agent-frameworks |
| 98 | `docs/bunchloch/agents/MCP_RESEARCH.md` | Pre-consolidation MCP. | mcp |
| 99 | `docs/bunchloch/agents/MCP _ Better Auth.md` | BetterAuth + MCP. | mcp |
| 100 | `docs/bunchloch/agents/MCP Server with x402.md` | MCP server paid via x402. | mcp, x402 |
| 101 | `docs/bunchloch/agents/MCP Server.md` | MCP server reference. | mcp |
| 102 | `docs/bunchloch/agents/MCP Toolbox.md` | MCP toolbox. | mcp |
| 103 | `docs/bunchloch/agents/mcp-research-report.md` | MCP research. | mcp |
| 104 | `docs/bunchloch/agents/mcp-ui-gradio-evidence-integration-analysis.md` | MCP-UI + Gradio analysis. | gradio, mcp-ui |
| 105 | `docs/bunchloch/agents/MCP-UI.md` | MCP-UI protocol. | mcp-ui |
| 106 | `docs/bunchloch/agents/DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md` | Restate durable execution. | agent-frameworks |
| 107 | `docs/bunchloch/agents/CONVEX_AGENT_PLATFORM.md` | Convex-as-agent-platform. | convex |
| 108 | `docs/bunchloch/agents/INDEX.md` | Agents docs index. | index |
| 109 | `docs/bunchloch/agents/baml-patterns-and-best-practices.md` | BAML best practices. | baml-extraction |
| 110 | `docs/bunchloch/data_engineering/ARCHITECTURE.md` | Data platform architecture. | data-architecture |
| 111 | `docs/bunchloch/data_engineering/INDEX.md` | Data engineering index. | index |
| 112 | `docs/bunchloch/data_engineering/dagster-comprehensive.md` | Dagster patterns. | dagster |
| 113 | `docs/bunchloch/data_engineering/dlt-comprehensive.md` | DLT patterns. | dlt |
| 114 | `docs/bunchloch/data_engineering/DLT_COMPLETE_GUIDE.md` | DLT complete guide. | dlt |
| 115 | `docs/bunchloch/data_engineering/cocoindex-comprehensive.md` | CocoIndex flows. | cocoindex |
| 116 | `docs/bunchloch/data_engineering/data-pipeline-architecture.md` | DLT + Dagster + CocoIndex + Feast + MLflow. | dagster, dlt, mlflow |
| 117 | `docs/bunchloch/data_engineering/data-architecture.md` | Older data architecture. | data-architecture |
| 118 | `docs/bunchloch/data_engineering/data-sources.md` | Data source inventory. | data-sources |
| 119 | `docs/bunchloch/data_engineering/data-versioning.md` | Data versioning with LakeFS / Iceberg. | data-versioning |
| 120 | `docs/bunchloch/data_engineering/duckdb-reference.md` | DuckDB reference. | duckdb |
| 121 | `docs/bunchloch/data_engineering/lancedb-reference.md` | LanceDB reference. | lancedb |
| 122 | `docs/bunchloch/data_engineering/marimo-reference.md` | Marimo reference. | marimo |
| 123 | `docs/bunchloch/data_engineering/Generative AI Art Workflow Integration.md` | FLUX.1 / SDXL art workflow. | fibo, bria, image-gen |
| 124 | `docs/bunchloch/data_engineering/Dagster Orchestration for Cocoindex, Graphiti.md` | Dagster ↔ CocoIndex ↔ Graphiti. | dagster, knowledge-graph |
| 125 | `docs/bunchloch/data_engineering/Ontology and Temporal Graphs Research.md` | Graphiti temporal-graph. | knowledge-graph |
| 126 | `docs/bunchloch/data_engineering/Knowledge-Systems.md` | Cognee + Graphiti + Memgraph + FalkorDB. | knowledge-graph |
| 127 | `docs/bunchloch/data_engineering/Geography of Truth - GeoAI.md` | GeoAI for the British Isles. | geoai, mmo |
| 128 | `docs/bunchloch/bonneagar/BAML, Graphiti, Tanstack AI Pipeline.md` | BAML → Graphiti → TanStack AI. | baml-extraction, knowledge-graph |
| 129 | `docs/bunchloch/bonneagar/Dagster Orchestration for Cocoindex, Graphiti.md` | Dagster for CocoIndex + Graphiti. | dagster, knowledge-graph |
| 130 | `docs/bunchloch/bonneagar/agentic-scraping-architecture.md` | Agentic scraping. | browser-automation |
| 131 | `docs/bunchloch/bonneagar/graphiti-crypto-adaptation.md` | Graphiti extended with crypto. | knowledge-graph, crypteolas |
| 132 | `docs/bunchloch/bonneagar/infrastructure-knowledge-graph.md` | KG infra deployment. | knowledge-graph |
| 133 | `docs/bunchloch/bonneagar/knowledge-graph-infrastructure.md` | KG infra patterns. | knowledge-graph |
| 134 | `docs/bunchloch/bonneagar/knowledge-graph-schema.md` | KG schema design. | knowledge-graph |
| 135 | `docs/bunchloch/bonneagar/hosting-litellm-pangolin-public-vs-private-access-models.md` | LiteLLM hosting. | litellm, pangolin |
| 136 | `docs/bunchloch/bonneagar/hosting-lancedb-docker-compose.md` | LanceDB docker-compose. | lancedb |
| 137 | `docs/bunchloch/bonneagar/comparing-approaches-pangolin-registration-komodo-deployment.md` | Pangolin vs Komodo. | pangolin, komodo |
| 138 | `docs/bunchloch/bonneagar/apple-silicon-deployment.md` | Apple Silicon ML. | apple-silicon |
| 139 | `docs/bunchloch/bonneagar/cloudflare.md` | Cloudflare stack. | cloudflare |
| 140 | `docs/bunchloch/bonneagar/Pangolin_Complete_Guide.md` | Pangolin complete reference. | pangolin |
| 141 | `docs/bunchloch/bonneagar/Komodo_Complete_Guide.md` | Komodo complete reference. | komodo |
| 142 | `docs/hackathons/Google Cloud Rapid Agent Hackathon_ Building Agents for Real-World Challenges - Devpost.pdf` | Prior agent-hackathon. | hackathon-narrative |
| 143 | `docs/hmgcc/Eligibility of technology readiness levels (TRL).md` | TRL definitions. | trl |
| 144 | `docs/openspec/README.md` | OpenSpec tooling. | openspec |
| 145 | `docs/openspec/openspec-comprehensive-research.md` | OpenSpec schema. | openspec |
| 146 | `docs/openspec/opencode-comprehensive-research.md` | OpenCode agent loop. | opencode |
| 147 | `docs/openspec/opencode-design-patterns-ontology.md` | Design patterns. | opencode |
| 148 | `docs/bunchloch/web/TanStack Start.md` | TanStack Start reference. | frontend-stack |
| 149 | `docs/bunchloch/web/repo-tanstack.md` | TanStack upstream README. | frontend-stack |
| 150 | `docs/bunchloch/web/Overview _ TanStack AI Docs.md` | TanStack AI overview. | agent-frameworks |
| 151 | `croilar/README.md` | Croílár portfolio README. | croilar |

**One off-list footgun:** `docs/bunchloch/meaisínfhoghlaim/` and `docs/bunchloch/teanga/` are **empty directories**; the canonical meaisínfhoghlaim content has been merged into `docs/04-ai-ml/*.md`. Don't grep those paths for source material.

---

## 5. Demo Stack Mapping (the table that ties it all together)

| Subsystem | Doc 1 | Doc 2 | Doc 3 | Doc 4 | Doc 5 |
|:--|:--|:--|:--|:--|:--|
| **Gradio HF Space** | `docs/00_index.md` | `docs/cognee/COGNEE_SETUP.md` | `docs/bunchloch/tuatha/Interactive AI Pipeline Development.md` | `docs/archive/2026-06-06-data-engineering/tool-ecosystem.md` | `docs/07-standards/project-conventions.md` |
| **BAML extraction** | `docs/03-agents/baml-extraction.md` | `docs/bunchloch/agents/BAML_COMPREHENSIVE_GUIDE.md` | `docs/bunchloch/agents/BAML Schemas for Irish Education.md` | `docs/bunchloch/agents/BAML_DUCKDB_DRAGONFLY_ANALYSIS.md` | `docs/bunchloch/agents/baml-patterns-and-best-practices.md` |
| **Docling / Unstract VLM** | `docs/04-ai-ml/ocr-htr.md` | `docs/04-ai-ml/vector-embeddings.md` | `docs/bunchloch/old/document-intelligence-vlm.md` | `docs/archive/2026-06-06-bonneagar/vlm-ocr-comparison.md` | `docs/archive/2026-06-06-meaisinfhoghlaim/document-processing-reference.md` |
| **Bria FIBO image gen** | `docs/bunchloch/data_engineering/FIBO Hackathon.md` | `docs/bunchloch/tuatha/Interactive AI Pipeline Development.md` | `docs/bunchloch/tuatha/Web3 Gamified Education & Asset Generation.md` | `docs/bunchloch/tuatha/AI Chemistry Education Image Generation.md` | `docs/archive/2026-06-06-meaisinfhoghlaim/AI Syllabus to JSON Schema.md` |
| **LiteLLM gateway / self-hosted models** | `docs/04-ai-ml/ml-pipelines.md` | `docs/04-ai-ml/fine-tuning-guide.md` | `docs/bunchloch/bonneagar/hosting-litellm-pangolin-public-vs-private-access-models.md` | `docs/archive/2026-06-06-bonneagar/overview.md` | `docs/01-platform-architecture/secrets-management.md` |
| **Cognee / Graphiti knowledge graph** | `docs/cognee/COGNEE_INTEGRATION.md` | `docs/cognee/CCC_INTEGRATION.md` | `docs/cognee/ARCHITECTURE.md` | `docs/cognee/INGESTION.md` | `docs/04-ai-ml/knowledge-graphs.md` |
| **SpacetimeDB game server** | `docs/bunchloch/tuatha/SpacetimeDB.md` | `docs/bunchloch/tuatha/SPACETIMEDB_GUIDE.md` | `docs/bunchloch/tuatha/repo-spacetimedb-cookbook.md` | `docs/06-product/celtic-mmo.md` | `docs/bunchloch/tuatha/SpacetimeDB Ogham Stone Game Integration.md` |
| **Babylon.js / wgpu / WebGPU client** | `docs/06-product/game-development.md` | `docs/bunchloch/tuatha/WGPU_GUIDE.md` | `docs/bunchloch/tuatha/GAME_CLIENT.md` | `docs/bunchloch/tuatha/CROSS_PLATFORM_GUIDE.md` | `docs/bunchloch/tuatha/PERFORMANCE_TUNING.md` |
| **Formative assessment logic** | `docs/06-product/educational-platform.md` | `docs/bunchloch/agents/IRISH_EDUCATION_PLATFORM_BLUEPRINT.md` | `docs/bunchloch/tuatha/Agentic Education Platform Development.md` | `docs/bunchloch/tuatha/Web3 Classroom Response System Design.md` | `docs/bunchloch/old/educational-game-development.md` |
| **Mythology (Tuatha Dé Danann, Anam, soulbound)** | `docs/06-product/celtic-mmo.md` | `docs/bunchloch/tuatha/mythology-framework.md` | `docs/bunchloch/tuatha/British Isles Mythology MMO Research.md` | `docs/bunchloch/tuatha/celtic_mmo.md` | `docs/bunchloch/tuatha/Ogham Crypto MMO Research.md` |
| **Celtic language AI** | `docs/04-ai-ml/celtic-language-ai.md` | `docs/bunchloch/tuatha/CELTIC_LANGUAGES.md` | `docs/bunchloch/tuatha/Celtic Etymology for Game Names.md` | `docs/bunchloch/tuatha/Celtic Language Data Aggregation & Analysis.md` | `docs/archive/2026-06-06-context/02-architecture/BILINGUAL_EDTECH.md` |
| **OCR / HTR pipeline** | `docs/archive/tuatha-mirror/celtic-ocr.md` | `docs/archive/tuatha-mirror/Irish Handwriting App Development.md` | `docs/archive/tuatha-mirror/Irish LLM for iPhone Development.md` | `docs/archive/tuatha-mirror/Fine-tuning VLMs for iOS HTR.md` | `docs/04-ai-ml/ocr-htr.md` |
| **5-element framework (Talamh/Uisce/Tine/Aer/Anam)** | `docs/bunchloch/tuatha/learn-to-earn-model.md` | `docs/bunchloch/tuatha/Learn-to-Earn Blockchain and AI.md` | `docs/bunchloch/tuatha/celtic_mmo.md` | `docs/bunchloch/tuatha/Celtic MMO Web3 Concept Integration.md` | `docs/archive/tuatha-mirror/Web3 Classroom Response System Design.md` |
| **Anam / Soulbound / NFT** | `docs/bunchloch/tuatha/Celtic MMO Web3 Concept Integration.md` | `docs/bunchloch/tuatha/learn-to-earn-model.md` | `docs/bunchloch/tuatha/celtic_mmo.md` | `docs/bunchloch/tuatha/Spacetimedb Blockchain Integration Strategy.md` | `docs/bunchloch/tuatha/Ogham Crypto MMO Research.md` |
| **Interactive education map** | `docs/bunchloch/tuatha/British Isles Education Map.md` | `docs/bunchloch/tuatha/Interactive Map & AI Agents.md` | `docs/bunchloch/tuatha/world-map.md` | `docs/bunchloch/tuatha/GRAPHICS_INDEX.md` | `docs/bunchloch/tuatha/ADDING_ZONES.md` |

---

## 6. Cross-Cutting Tag Index (Top 50)

| Tag | Count | Tag | Count | Tag | Count |
|:--|--:|:--|--:|:--|--:|
| `baml-extraction` | 22 | `spacetimedb` | 12 | `dagster` | 9 |
| `celtic-mmo` | 18 | `bge-m3` | 11 | `knowledge-graph` | 9 |
| `irish` | 16 | `celtic-language` | 11 | `x402` | 8 |
| `irish-education` | 14 | `mythology` | 11 | `gradio` | 7 |
| `huggingface-space` | 13 | `cognee` | 10 | `irish-ga` | 7 |
| `gaelic-metrics` | 12 | `fibo` | 10 | `webgpu` | 7 |
| `lancedb` | 12 | `gaeilge` | 10 | `agent-frameworks` | 6 |
| `litellm` | 12 | `leave-cert` | 10 | `celtic-mmo.md` | 6 |
| `oceldeachais-` | 12 | `tuatha` | 10 | `celtic-mmo` | 6 |
| `oceltic-` | 12 | `wgpu` | 10 | `cymraeg` | 6 |
| `bria` | 11 | `cymraeg` | 10 | `gaeilge` | 6 |
| `daer` | 11 | `daer` | 10 | `gaeilge` | 6 |
| `daer` | 11 | `gradio` | 10 | `goidelic-brythonic` | 6 |
| `gaeilge` | 11 | `huggingface` | 10 | `goidelic-gaeilge` | 6 |
| `gaeilge` | 11 | `huggingface-space` | 10 | `hackathon-narrative` | 6 |
| `huggingface-space` | 11 | `irish-education` | 10 | `ian-mac-an-deisigh-ui-liathain` | 6 |
| `irish-education` | 11 | `junior-cycle` | 10 | `mabinogion` | 6 |
| `an-scrudai` | 6 | `mabinogion` | 10 | `mythology` | 6 |
| `mabinogion` | 6 | `celtic-` | 10 | `pobal-hp` | 6 |
| `british-isles` | 6 | `pobal-hp` | 10 | `ragan-22.7` | 6 |

(Trimmed from the consolidated catalog; the noisy bulk tags from the automated extraction are excluded.)

---

## 7. The 6 Scraped Wikipedia Articles (the Cianfhoghlaim NPC lore source)

Cached to `doc/hackathons/wikipedia-sources/` (per the original plan):

1. `ga:Uí_Liatháin` — Loughcrew, Co. Meath; colony in Cornwall and Wales. Source: `https://ga.wikipedia.org/wiki/Uí_Liatháin`
2. `en:The_Expulsion_of_the_Déisi` — Tara → Leinster → Munster. Source: `https://en.wikipedia.org/wiki/The_Expulsion_of_the_Déisi`
3. `en:Manannán_mac_Lir` — Sea-god of the Otherworld; Wave-Sweeper boat; Aonbharr horse. Source: `https://en.wikipedia.org/wiki/Manannán_mac_Lir`
4. `en:Rhiannon` — Welsh sovereignty goddess; horse-riding; Birds of Rhiannon. Source: `https://en.wikipedia.org/wiki/Rhiannon`
5. `en:Dian_Cecht` — Physician of the Tuatha Dé Danann; Well of Healing. Source: `https://en.wikipedia.org/wiki/Dian_Cecht`
6. `en:Cian` — Lugh's father; "Scal Balb" (dumb champion). Source: `https://en.wikipedia.org/wiki/Cian`

---

## 8. Cross-quadrant design tokens (the unified palette)

From `docs/05-web/ui-components.md:381-384`, `docs/ui-inspiration/UI_INSPIRATION_GUIDE.md:159-188`, and the WGSL shader catalog at `docs/bunchloch/tuatha/GRAPHICS_INDEX.md:149-150`:

| Token | OKLCH | Hex | Use |
|-------|-------|-----|-----|
| `--celtic-emerald` | `oklch(0.62 0.16 145)` | `#28955e` | Talamh (Space 1) |
| `--celtic-azure` | `oklch(0.62 0.12 230)` | `#1e80c6` | Uisce (Space 2 themes) |
| `--celtic-amber` | `oklch(0.70 0.15 75)` | `#d68c1c` | Tine (Space 4 fire) |
| `--celtic-indigo` | `oklch(0.50 0.18 280)` | `#5a4fcf` | Aer (Space 2/3) |
| `--celtic-gold` | `oklch(0.75 0.13 95)` | `#cc9966` | Anam (Space 3/4) |
| `--hades-base` | `oklch(0.15 0.01 265)` | `#1d1d2f` | Background |
| `--hades-ink` | `oklch(0.10 0.01 265)` | `#1a1d2e` | Deepest background |
| `--ncca-stone` | `oklch(0.75 0.02 90)` | `#bcb8b0` | Stone gray for borders |
| `--pobal-crimson` | `oklch(0.45 0.20 25)` | `#a83a2a` | DEIS / high-deprivation accents |
| `--celtic-bronze` | `oklch(0.55 0.12 70)` | `#a67c52` | Anam wallet badge |

---

## 9. LiteLLM Model Fallback Chains

(Detailed in `doc/hackathons/build-small-2026-model-fallback.md`.)

| Role | Primary (HF Inference) | Fallback 1 | Fallback 2 |
|:--|:--|:--|:--|
| BAML extraction | `Qwen/Qwen2.5-7B-Instruct` | `meta-llama/Llama-3.1-8B-Instruct` | `google/gemma-2-9b-it` |
| Chat (tutor NPCs) | `meta-llama/Llama-3.1-8B-Instruct` | `mistralai/Mistral-7B-Instruct-v0.3` | `Qwen/Qwen2.5-7B-Instruct` |
| OCR / VLM | `Qwen/Qwen2-VL-7B-Instruct` | `microsoft/Phi-3.5-vision-instruct` | `google/paligemma-3b-mix-448` |
| Image gen (FIBO sub) | `stabilityai/stable-diffusion-xl-base-1.0` | `black-forest-labs/FLUX.1-schnell` | n/a |
| Embeddings | `BAAI/bge-m3` | `sentence-transformers/all-MiniLM-L6-v2` | n/a |
| Speech | `openai/whisper-large-v3` | `openai/whisper-large-v3-turbo` | n/a |
| TTS | `ResembleAI/chatterbox` | `facebook/mms-tts-ga` | n/a |

Space 4 ships an Anvil-sidecar container with the CuchulainnNFT.sol contract (5-element system).

---

## 10. OpenSpec Change Bundle (5 files)

Created in `openspec/changes/croilar-hf-build-small-2026-demo/`:

- `proposal.md` — 4 Spaces, deadline June 15, 7-day schedule, badges
- `tasks.md` — Day 1-7 schedule
- `specs/croilar-gradio-hf-demo/spec.md` — 4 ADDED Requirements (one per Space), each with 2 Scenarios

---

## 11. Known Drift (the 22 items the audit surfaced)

| # | Item | Where | Action |
|--:|:--|:--|:--|
| 1 | Old plan `doc/hackathons/build-small-2026-plan.md:1-115` references 5 Projects (Anam Celtic Learning Companion, BackyardAI, Físeán Feasa, Snáithe, Anam Cara). | `doc/hackathons/build-small-2026-plan.md:1-115` | Patch with the new 4-Space + 5-element re-themes section. BAML schemas and assets to be remapped, not discarded. |
| 2 | Old plan references Pipecat voice agent runtime which can't run in a Gradio Space. | `doc/hackathons/build-small-2026-plan.md:63` | Replace with Web Speech API (`docs/06-product/educational-platform.md:127`) or HF Inference for Whisper + MMS-TTS. |
| 3 | "Project 5 — Anam Cara Soulbound Credential" should be folded into Space 4. | `doc/hackathons/build-small-2026-plan.md:80-90` | Folded into Space 4 as the Anam SBT mounter on local Anvil. |
| 4 | The Tri-Naomh persona switcher (An Scrúdaí / An Teangeolaí / An Gaiscíoch) in Space 4 was replaced by the 5-element framework. | `doc/hackathons/build-small-2026-plan.md:95-110` | Replaced with Talamh/Uisce/Tine/Aer/Anam (per `learn-to-earn-model.md:224-233`). |
| 5 | `meaisínfhoghlaim/AGENTS.md` references `agents/orchestrator.py` and `agents/registry.py` which do not exist; real entry is `agents/root_agent.py`. | `meaisínfhoghlaim/AGENTS.md:30-32` | Update AGENTS.md to point at the real root agent. |
| 6 | `meaisínfhoghlaim/pyproject.toml` does not exist. | `meaisínfhoghlaim/` | Add a note to the catalogue that meaisínfhoghlaim is a logical quadrant, not a workspace member. |
| 7 | `pipelines/irish_document_scanner.py:19` references Confluent Kafka; the real path is RisingWave. | `meaisínfhoghlaim/pipelines/irish_document_scanner.py:19` | Document the migration in the catalogue. |
| 8 | `root_agent.py:16` references Datadog LLMObs; the real observability path is Langfuse. | `meaisínfhoghlaim/agents/root_agent.py:16` | Update to reference Langfuse. |
| 9 | `tuatha/summary.txt` and `tuatha/anam.md` tell different stories (summary.txt = Anam particle sim, anam.md = MMO architecture). | `tuatha/summary.txt`, `tuatha/anam.md` | Clarify in the catalogue. |
| 10 | `bunchloch/agents/BAML_DUCKDB_DRAGONFLY_ANALYSIS.md`, `BAML Schemas for Irish Education.md`, `BAML for Syllabus-Driven Data Extraction.md` are all marked MERGED → dead. | `docs/bunchloch/agents/` | Remove from catalogue (consolidated into BAML_COMPREHENSIVE_GUIDE). |
| 11 | `bunchloch/old/archive-old-project-context-raw-Finetuning Qwen3-VL for Gaelic OCR.md` is the single most complete Qwen-VL finetune doc. | `docs/bunchloch/old/` | Promote to canonical for OCR; supersedes partial coverage in `docs/04-ai-ml/ocr-htr.md`. |
| 12 | `bunchloch/old/archive-old-ml-skills-mlflow-mlflow-llm-guide.md` has richer MLflow+RAGAS code examples than the canonical. | `docs/bunchloch/old/` | Add to catalogue as recommended reading. |
| 13 | `bunchloch/old/archive-old-cianfhoghlaim-consolidated-06-document-processing-README.md` has broader document processing context. | `docs/bunchloch/old/` | Add to catalogue. |
| 14 | `bunchloch/tuatha/SpacetimeDB Ogham Stone Game Integration.md` (canonical) vs `archive/tuatha-mirror/` version: archive has 371 lines, more detail. | `docs/bunchloch/tuatha/` vs `docs/archive/tuatha-mirror/` | Add archive version as alternative. |
| 15 | `bunchloch/tuatha/CRYPTO_INTEGRATION_SUMMARY.md` (canonical) vs `archive/tuatha-mirror/`: archive is 986 lines vs canonical. | `docs/bunchloch/tuatha/` | Add archive version. |
| 16 | `bunchloch/tuatha/learn-to-earn-model.md` canonical: Four Treasures condensed. `archive/tuatha-mirror/` has the full elemental mapping. | `docs/bunchloch/tuatha/` | Use archive version for Space 4's 5-element framework. |
| 17 | `docs/archive/2026-06-06-bonneagar/infrastructure-tools.md` has Komodo v2 DB migration, recursive deployment, Ansible role internals not in canonical. | `docs/archive/2026-06-06-bonneagar/` | Add to catalogue. (Note: infrastructure is archived for this hackathon.) |
| 18 | `docs/archive/2026-06-06-context/AI_ML_PIPELINE.md:199-232` contains the original `MathQuestion` BAML schema with `text_irish`, `requires_diagram`, `topic` enum — the actual exam paper shape. | `docs/archive/2026-06-06-context/` | Add to catalogue; reuse for Space 1's `GenerateExitCardQuestions`. |
| 19 | `docs/archive/2026-06-06-meaisinfhoghlaim/AI Syllabus to JSON Schema.md` has exhaustive FIBO JSON-native visualization architecture. | `docs/archive/2026-06-06-meaisinfhoghlaim/` | Add to catalogue; reuse for Space 4's Uisce feature. |
| 20 | `docs/archive/2026-06-06-bonneagar/celtic-platform.md:1846-1879` has the 33-subject Irish Leaving Cert structure with strand breakdowns not in canonical. | `docs/archive/2026-06-06-bonneagar/` | Add to catalogue. |
| 21 | `oideachais/data_platform/dagster_defs/assets/ireland/exam_materials_assets.py` uses `ncca_multipartitions` (208 keys) and `sec_multipartitions` (780 keys), both DEPRECATED. | `oideachais/data_platform/dagster_defs/assets/ireland/exam_materials_assets.py:101-107` | Use `partitions_v2` (years as `dg.Config`). |
| 22 | `meaisínfhoghlaim/evaluation/ragas_pipeline.py:65` uses `datetime.utcnow()` which is deprecated in Python 3.12. | `meaisínfhoghlaim/evaluation/ragas_pipeline.py:65` | Cosmetic; use `datetime.now(datetime.UTC)`. |

---

## 12. References to upstream BAML schemas to REUSE (not redefine)

1. **`tuatha/baml_src/mythology_extraction.baml`** (244 lines) — Full `MythologicalCharacter`, `MythologicalStory`, `MythologicalLocation`, `NPCDialogue`, `FolkloreElement`. The `CelticTradition` enum covers IRISH, WELSH, SCOTTISH, MANX, BRETON, CORNISH, PAN_CELTIC. The `MythologicalCycle` enum covers TUATHA_DE_DANANN, FIANNA, ULSTER, KINGS, MABINOGION, ARTHURIAN, FOLK. **All 6 Space 3 NPCs extract through this schema.**

2. **`oideachais/data_platform/baml_src/leaving_cert_syllabus_extraction.baml`** (49 lines) — `SyllabusTopic` + `LeavingCertSyllabus`. The typed foundation for Space 1.

3. **`tuatha/baml_src/player_assessment.baml`** — `GenerateAdaptiveAssessment` and `AnalyzePlayerResponse`. Reuse by Space 1 (exam assessment) and Space 3 (in-game skill checks).

---

## 13. References to upstream notebooks/datasets/assets to reference

1. **`oideachais/notebooks/mission_control.py`** — Dagster status → DLT pipeline runs → LanceDB table counts → BAML extraction success rates. Adapt into Space 1's "Pipeline Health" tab.

2. **`oideachais/data_platform/dlt_sources/geospatial/cso_small_areas.py:342-371`** — HP Deprivation Index 2022 + DEIS schools. Reference for Space 2's school heatmap overlay and Space 4's Talamh element.

3. **`tuatha/crates/stdb-modules/tuath-game/src/lib.rs:224-244`** — The `Npc` table struct. The canonical NPC data model. Space 3's 6 NPCs should conform to this schema even if running locally without SpacetimeDB.

---

## 14. The 5 Patterns Appearing in 2+ Doc Trees

1. **BAML as universal type bridge** (4/5 trees: `03-agents/baml-extraction.md`, `02-data-platform/dlt-pipelines.md:107-128`, `05-web/frontend-stack.md:386`, `06-product/educational-platform.md:59`).
2. **Dual-language (ga+en) first-class** (4/5 trees: `06-product/educational-platform.md:67-74`, `03-agents/baml-extraction.md:364-526`, `04-ai-ml/knowledge-graphs.md:416-426`, `openspec/changes/state-of-art-5-workspaces/specs/croilar-web/spec.md:62-69`).
3. **DLT + Dagster + LanceDB pipeline backbone** (`02-data-platform/dlt-pipelines.md`, `02-data-platform/dagster-orchestration.md:637-656`, `02-data-platform/data-architecture.md:470-530`).
4. **Celtic knotwork + WGSL shader design tokens** (2/5 trees: `06-product/game-development.md:263-271`, `05-web/ui-components.md:381-384`).
5. **CopilotKit + Agno + ADK multi-agent orchestration** (2/5 trees: `03-agents/agent-frameworks.md`, `05-web/ui-components.md:188-258`, `06-product/celtic-mmo.md:317-348`).

---

## 15. Schedule (7 days, locked)

| Day | Build | Cross-cutting |
|--:|:--|:--|
| **1 (Mon)** | Spin up `spaces/_common/` (Celtic theme tokens, Anam Bonneagar footer, soulbound SVG, social card); OpenSpec change dir; BAML re-pointing to HF Inference | 5 file artefacts written (catalogue, indexes, model fallback, OpenSpec change, plan patch) |
| **2 (Tue)** | **Space 3** core: Babylon.js WebGPU canvas + 6 NPCs + 4 diegetic zones; demo video 1 (Cian → Manannán → Rhiannon flow) | MotherDuck Dive snapshots pre-computed; gov landscape scraping begins |
| **3 (Wed)** | **Space 1** core: BAML `ComposeMarkingSchemeDiff` + Gradio Blocks heatmap + PCLM-PDF emitter; demo video 2 | CuchulainnNFT.sol deployed to local Anvil; fada-accuracy preserved end-to-end |
| **4 (Thu)** | **Space 2** (3 themes in parallel): Foclóir + Scoil ar an Léarscáil + Curaclam Trasteorann; demo video 3 | 12-agent Q&A scaffolded; cross-border matrix built; Anam Bonneagar footer added |
| **5 (Fri)** | **Space 4** — 5 elements, 7 features: Tine → Uisce → Talamh → Aer → Anam → Mac Léinn → Fiosraigh; demo video 4 | All 5 Spaces polished; 5-element connective-tissue story is the demo narration |
| **6 (Sat)** | All Spaces polish: bilingual EN/GA verified, accessibility audit, mobile-responsive check, demo videos 1-4, social cards | OpenSpec `tasks.md` and `proposal.md` written |
| **7 (Sun)** | Final polish + HF Space submissions + OpenSpec `spec:validate croilar-hf-build-small-2026-demo --strict` + `spec:archive` after approval | Blog posts published; Twitter/Mastodon thread with 4 social cards |

---

## 16. Notes on the CCC + Cognee Integration

- **ccc (`cocoindex-code_search`)** = the semantic code search tool. Used by every subagent to find documents and source files via natural-language queries. Already documented in `docs/cognee/CCC_INTEGRATION.md`.
- **Cognee** = the knowledge-graph memory layer (separate from ccc). It is *also* a component the demo itself will use — see `docs/cognee/COGNEE_INTEGRATION.md` for the demo's own ingestion-to-graph pipeline.
- **The dual-tool pattern**: ccc to find documents/code, Cognee to remember relationships across them. Subagents use this loop to explore the codebase + docs. The demo's own NPC dialogue can also use this loop on the curriculum + mythology corpora.

---

*End of catalogue. Approve and exit plan mode when ready; 5 file writes pending.*
