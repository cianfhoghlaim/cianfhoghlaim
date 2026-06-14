# Tuath Documentation Index

All `docs/tuatha/*.md` (consolidated into 8 topical subdirectories).

Last consolidated: 2026-06-13

---

## Quick links

- [README.md](README.md) — project overview, mission, and architecture
- [ANALYSIS.md](ANALYSIS.md) — cross-project analysis (Cianfhoghlaim stack: bonneagar / meaisínfhoghlaim / sruth / taighde)
- [00-nav/Tuath API Reference.md](00-nav/Tuath%20API%20Reference.md) — canonical API doc
- [00-nav/GRAPHICS_INDEX.md](00-nav/GRAPHICS_INDEX.md) — graphics & rendering doc catalog
- [00-nav/PIPELINES.md](00-nav/PIPELINES.md) — data pipeline architecture
- [08-mirrors/](08-mirrors/) — 11 skeletonized upstream mirrors (SpacetimeDB, wgpu, gdext, x402, etc.)

---

## 01 — Game Design (`01-game-design/`)

Celtic MMO concept, mythology, zones, asset generation, frontend.

| File | Topic |
|---|---|
| [celtic_mmo.md](01-game-design/) *(removed; redundant)* | *(was a 197-line summary; subsumed by Ogham + Celtic Naming docs)* |
| [mythology-framework.md](01-game-design/mythology-framework.md) | Pent-elemental cosmology (Spirit/Water/Fire/Earth/Air); Anam Cara |
| [Celtic Naming for the MMO.md](01-game-design/Celtic%20Naming%20for%20the%20MMO.md) | Philological survey (*anam*, *kern*, *tír*, *aran*, *gaelg*, *cymr*, *yern*) + Web3 conflict analysis |
| [CELTIC_LANGUAGES.md](01-game-design/CELTIC_LANGUAGES.md) | Tuath's language support matrix (Gaeilge/Cymraeg/Gàidhlig/Gaelg) |
| [engine-selection.md](01-game-design/engine-selection.md) | "Anam" MMO ecosystem — agents, payments, runtimes |
| [world-map.md](01-game-design/world-map.md) | "Celtic OS" Product OS spatial interface blueprint |
| [MMO Geospatial Data & Visual RAG.md](01-game-design/MMO%20Geospatial%20Data%20%26%20Visual%20RAG.md) | WebGPU MMO + RAG for NPCs |
| [GAME_CLIENT.md](01-game-design/GAME_CLIENT.md) | Babylon.js implementation (TuathGame, SceneManager, AG-UI streaming) |
| [Asset Management for Full-Stack App.md](01-game-design/Asset%20Management%20for%20Full-Stack%20App.md) | Pixel art / RPG metaphor for Leaving Cert subjects |
| [Educational Game Dev Pipeline.md](01-game-design/Educational%20Game%20Dev%20Pipeline.md) | DIAGE — scientifically accurate physics/chem sims |
| [educational-game-development.md](01-game-design/educational-game-development.md) | Same topic, expanded engine comparison |

## 02 — Agents (`02-agents/`)

Tuath's multi-agent system, how to extend it.

| File | Topic |
|---|---|
| [Tuath Agent System.md](02-agents/Tuath%20Agent%20System.md) | Architecture (Celtic Tutor, Mythology Narrator, Quest Guide, Research Assistant) + how-to for adding agents and tools (merged from AGENTS.md + ADDING_AGENTS.md + ADDING_TOOLS.md) |
| [Agentic Education Platform Development.md](02-agents/Agentic%20Education%20Platform%20Development.md) | Framework context — CopilotKit v1.5 + AgUI protocol, MCP servers |

## 03 — Data Pipelines (`03-data-pipelines/`)

DLT, CocoIndex, Dagster, MLflow, knowledge graph, federated learning, geopolitics.

| File | Topic |
|---|---|
| [ADDING_DATA_SOURCES.md](03-data-pipelines/ADDING_DATA_SOURCES.md) | How-to: add a DLT source to the Tuath pipeline |
| [Data Platform Technical Integration Plan.md](03-data-pipelines/Data%20Platform%20Technical%20Integration%20Plan.md) | **Canonical** data platform design (DLT + CocoIndex + Feast + MLflow + Dagster + DuckDB + Dragonfly), with Crypto Analytics as a worked example |
| [British Isles Education Map.md](03-data-pipelines/British%20Isles%20Education%20Map.md) | 2021/2022 census data + DuckDB+Convex+TanStack viz stack |
| [British Isles Game Dev Data Pipeline.md](03-data-pipelines/British%20Isles%20Game%20Dev%20Data%20Pipeline.md) | OS MasterMap + GeoHive + LiDAR + Met Office → 2.5D game terrain |
| [Celtic Language Data Aggregation & Analysis.md](03-data-pipelines/Celtic%20Language%20Data%20Aggregation%20%26%20Analysis.md) | Federated Linguistic Data Lakehouse for non-Ireland Celtic |
| [Agentic Web Scraping Pipeline.md](03-data-pipelines/Agentic%20Web%20Scraping%20Pipeline.md) | Browserbase + Z.AI GLM 4.6V + Cognee + BAML + Ag-UI |
| [Building an Educational Agent's Knowledge Base.md](03-data-pipelines/Building%20an%20Educational%20Agent%27s%20Knowledge%20Base.md) | Agno + dlt + Dagster + BAML + Cloudflare R2 + Cognee/Graphiti |
| [Multimodal Video Knowledge Graph Pipeline.md](03-data-pipelines/Multimodal%20Video%20Knowledge%20Graph%20Pipeline.md) | yt-dlp + WhisperX + Qwen3-Omni → GraphRAG |
| [Integrating Rust, DuckDB, TanStack, CopilotKit.md](03-data-pipelines/Integrating%20Rust%2C%20DuckDB%2C%20TanStack%2C%20CopilotKit.md) | SpacetimeDB + DuckDB WASM + TanStack Start + CopilotKit ("Thick Client, Smart Server") |
| [TanStack DB Integration and Comparison.md](03-data-pipelines/TanStack%20DB%20Integration%20and%20Comparison.md) | TanStack DB + DuckDB + RisingWave + Marimo + Convex comparison |
| [LLM Serving with MLflow & Langfuse.md](03-data-pipelines/LLM%20Serving%20with%20MLflow%20%26%20Langfuse.md) | Llama-swap + mlx-vlm + Z.AI gateway + observability |
| [dlt_crawl4ai_lancedb.md](03-data-pipelines/dlt_crawl4ai_lancedb.md) | Crypto sentiment pipeline — dlt + crawl4ai + LanceDB + BAML + DuckDB |
| [Crypteolas_ Federated Learning & Crypto Payments.md](03-data-pipelines/Crypteolas_%20Federated%20Learning%20%26%20Crypto%20Payments.md) | Project Crypteolas — SyftBox + Flower + x402 |
| [CRYPTEOLAS_INTEGRATION_GUIDE.md](03-data-pipelines/CRYPTEOLAS_INTEGRATION_GUIDE.md) | Crypteolas agent integration (CopilotKit + Agent OS pattern) |
| [CRYPTO_INTEGRATION_SUMMARY.md](03-data-pipelines/CRYPTO_INTEGRATION_SUMMARY.md) | x402 + MCPay + AP2 + Web3 UI components summary |

## 04 — Game Tech (`04-game-tech/`)

Game-engine research (essays) + operational reference.

| Section | File | Topic |
|---|---|---|
| (root) | [Game Dev Pipeline Research & Plan.md](04-game-tech/Game%20Dev%20Pipeline%20Research%20%26%20Plan.md) | Hades + BitCraft hybrid — LangGraph agentic research pipeline |
| (root) | [Game Particle Effects Research(2).md](04-game-tech/Game%20Particle%20Effects%20Research(2).md) | "Anam Initiative" — meteorological particle sim (Unreal/Unity/Godot) |
| (root) | [Geospatial Workflow & Particle Effects(1).md](04-game-tech/Geospatial%20Workflow%20%26%20Particle%20Effects(1).md) | DuckDB + MotherDuck + WebGPU particles, GeoArrow + Lonboard |
| (root) | [SpacetimeDB Ogham Stone Game Integration.md](04-game-tech/SpacetimeDB%20Ogham%20Stone%20Game%20Integration.md) | **Merged** — Ogham archaeology + procedural generation + sovereignty/token economy |
| (root) | [Spacetimedb Blockchain Integration Strategy.md](04-game-tech/Spacetimedb%20Blockchain%20Integration%20Strategy.md) | SpacetimeDB + Solana Token-2022 + Ethereum EIP-7702 |
| (root) | [Rust Full-Stack Gaming Environment.md](04-game-tech/Rust%20Full-Stack%20Gaming%20Environment.md) | SpacetimeDB + Godot (gdext) + Alloy/Anchor |
| (root) | [Game Reverse Engineering Workflow Design.md](04-game-tech/Game%20Reverse%20Engineering%20Workflow%20Design.md) | DIARE — Z.AI GLM-4.6V + Agno + Ghidra/Frida |
| (root) | [Interactive AI Pipeline Development.md](04-game-tech/Interactive%20AI%20Pipeline%20Development.md) | Gradio + CopilotKit + MCP → Bria Fibo image gen |
| (root) | [Generative AI Art Workflow Integration.md](04-game-tech/Generative%20AI%20Art%20Workflow%20Integration.md) | InvokeAI + MLX for pixel art (PostHog aesthetic) |
| (reference/) | [ADDING_ZONES.md](04-game-tech/reference/ADDING_ZONES.md) | How-to: extend a zone in Babylon.js |
| (reference/) | [DEPLOYMENT.md](04-game-tech/reference/DEPLOYMENT.md) | Production deployment (Python + Rust + SpacetimeDB) |
| (reference/) | [FRONTEND.md](04-game-tech/reference/FRONTEND.md) | TanStack Start + Babylon.js frontend |
| (reference/) | [PERFORMANCE_TUNING.md](04-game-tech/reference/PERFORMANCE_TUNING.md) | Embedding batching, HNSW, Cypher optimization |
| (reference/guides/) | [WGPU_GUIDE.md](04-game-tech/reference/guides/WGPU_GUIDE.md) | WebGPU rendering, terrain, particle compute |
| (reference/guides/) | [GODOT_RUST_GUIDE.md](04-game-tech/reference/guides/GODOT_RUST_GUIDE.md) | gdext integration, GodotClass macros |
| (reference/guides/) | [SPACETIMEDB_GUIDE.md](04-game-tech/reference/guides/SPACETIMEDB_GUIDE.md) | Multiplayer backend |
| (reference/guides/) | [CROSS_PLATFORM_GUIDE.md](04-game-tech/reference/guides/CROSS_PLATFORM_GUIDE.md) | Kotlin, Swift, React Native + Godot |
| (reference/guides/) | [PAYMENT_GUIDE.md](04-game-tech/reference/guides/PAYMENT_GUIDE.md) | x402 payment integration |

## 05 — iOS & ML (`05-ios-ml/`)

Celtic OCR, on-device LLMs, Apple ecosystem.

| File | Topic |
|---|---|
| [celtic-ocr.md](05-ios-ml/celtic-ocr.md) | Bilingual Irish-English HTR on iOS (ColPali, MLX, ml-fastvlm, Unsloth) |
| [Irish Handwriting App Development.md](05-ios-ml/Irish%20Handwriting%20App%20Development.md) | iPad Air M2 + Apple Pencil + Qwen2.5-VL/Gemma 3 |
| [Irish LLM for iPhone Development.md](05-ios-ml/Irish%20LLM%20for%20iPhone%20Development.md) | On-device Irish LLM via Unsloth 4-bit GGUF + AnyLanguageModel |
| [Federated AI Marketplace on iPhone.md](05-ios-ml/Federated%20AI%20Marketplace%20on%20iPhone.md) | Crypteolas iOS — Apple MLX + Flower + x402 |
| [iOS App Development Ecosystem Strategy.md](05-ios-ml/iOS%20App%20Development%20Ecosystem%20Strategy.md) | KMP + Swift + Rust sandwich architecture |
| [apple_ml-fastvlm_…CVPR 2025.md](05-ios-ml/apple_ml-fastvlm_%20This%20repository%20contains%20the%20official%20implementation%20of%20_FastVLM_%20Efficient%20Vision%20Encoding%20for%20Vision%20Language%20Models_%20-%20CVPR%202025.md) | Apple CVPR 2025 paper clip |

## 06 — Tokenomics & Web3 (`06-tokenomics/`)

x402, SIWE, learn-to-earn.

| File | Topic |
|---|---|
| [x402-payments.md](06-tokenomics/x402-payments.md) | x402 protocol reference |
| [Learn-to-Earn Blockchain and AI.md](06-tokenomics/Learn-to-Earn%20Blockchain%20and%20AI.md) | L2E model for Tuath |
| [Sign In With Ethereum (SIWE) _ Better Auth.md](06-tokenomics/Sign%20In%20With%20Ethereum%20%28SIWE%29%20_%20Better%20Auth.md) | Better Auth SIWE plugin (implementation reference) |

## 07 — Clippings (`07-clippings/`)

External articles, archived for reference. No edits, no synthesis.

| File | Source |
|---|---|
| [AG-UI and A2UI_…CopilotKit.md](07-clippings/AG-UI%20and%20A2UI_%20Understanding%20the%20Differences%20_%20CopilotKit.md) | CopilotKit blog |
| [Comparing the Top 6 Agent-Native Rails….md](07-clippings/Comparing%20the%20Top%206%20Agent-Native%20Rails%20for%20the%20Agentic%20Internet_%20MCP%2C%20A2A%2C%20AP2%2C%20ACP%2C%20x402%2C%20and%20Kite.md) | Agent comparison article |
| [Kotlin Multiplatform vs. React Native….md](07-clippings/Kotlin%20Multiplatform%20vs.%20React%20Native_%20A%20cross-platform%20comparison%20_%20Kotlin%20Multiplatform.md) | Cross-platform comparison |
| [GeoAI.md](07-clippings/GeoAI.md) | Geospatial AI |
| [useAgent Hook.md](07-clippings/useAgent%20Hook.md) | CopilotKit useAgent hook |
| [MCP-UI.md](07-clippings/MCP-UI.md) | MCP UI integration |
| [Introducing AnyLanguageModel_…Apple Platforms.md](07-clippings/Introducing%20AnyLanguageModel_%20One%20API%20for%20Local%20and%20Remote%20LLMs%20on%20Apple%20Platforms.md) | HuggingFace blog |
| [Swift Transformers Reaches 1.0….md](07-clippings/Swift%20Transformers%20Reaches%201.0%20%E2%80%93%20and%20Looks%20to%20the%20Future.md) | HuggingFace blog |
| [Unsloth Model Catalog _ Unsloth Documentation.md](07-clippings/Unsloth%20Model%20Catalog%20_%20Unsloth%20Documentation.md) | Unsloth docs |
| [Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md](07-clippings/Release%20v28.0.0%20-%20Mesh%20Shaders%2C%20Immediates%2C%20and%20More!%20%C2%B7%20gfx-rs_wgpu.md) | wgpu v28 release notes |
| [The Expulsion of the Déisi - Wikipedia.md](07-clippings/The%20Expulsion%20of%20the%20D%C3%A9isi%20-%20Wikipedia.md) | Wikipedia |

## 08 — Mirrors (`08-mirrors/`)

11 skeletonized upstream repositories. See `08-mirrors/_summaries/` for one-page KCG summaries.

| Directory | Size | Language |
|---|---|---|
| [SpacetimeDB/](08-mirrors/SpacetimeDB/) | 41M | Rust |
| [wgpu/](08-mirrors/wgpu/) | 840K | Rust |
| [gdext/](08-mirrors/gdext/) | 5.0M | Rust |
| [x402/](08-mirrors/x402/) | 26M | TS/Go/Python/Rust |
| [spacetimedb-typescript-sdk/](08-mirrors/spacetimedb-typescript-sdk/) | 944K | TypeScript |
| [spacetimedb-cookbook/](08-mirrors/spacetimedb-cookbook/) | 9.6M | Rust/TypeScript |
| [hophacks-spacetimedb-workshop/](08-mirrors/hophacks-spacetimedb-workshop/) | 328K | Rust/TypeScript |
| [react-native-reusables/](08-mirrors/react-native-reusables/) | 7.9M | TypeScript |
| [react-native-godot/](08-mirrors/react-native-godot/) | 76K | TypeScript/C++ |
| [agui_kotlin/](08-mirrors/agui_kotlin/) | 80K | Kotlin |
| [AnyLanguageModel/](08-mirrors/AnyLanguageModel/) | 48K | Swift |

## 99 — Archive

The `99-archive/` slot for misplaced files was retired in the 2026-06-13 consolidation (all content was either deleted as out-of-scope or moved to its proper topical home).

---

## Verification

| Metric | Before (2026-06-06) | After (2026-06-13) |
|---|---|---|
| Top-level subdirs | 0 (flat) | 8 (`00-nav`–`07-clippings`, plus `08-mirrors`) |
| `.md` files at root | 116 | 3 (`README.md`, `INDEX.md`, `ANALYSIS.md`) |
| Total `.md` files (excl. mirrors) | 116 | ~85 |
| Repo summaries | 11 | 11 (now in `08-mirrors/_summaries/`) |
| Skeletonized mirrors | 11 (~161 MB) | 11 (~95 MB; -41% from pruning) |
| Byte-identical dupes | 5 pairs (~75 KB) | 0 |

Last consolidated: 2026-06-13
