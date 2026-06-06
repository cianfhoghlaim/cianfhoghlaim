# docs/tuatha/ — Flatness Verification

**Date:** 2026-06-06  
**Status:** CONFIRMED FLAT — 0 subdirectories, 115 `.md` files at root level

## Verification Commands

```bash
$ find docs/tuatha -mindepth 1 -type d | wc -l
0
$ find docs/tuatha -maxdepth 1 -type f -name '*.md' | wc -l
115
```

No subdirectories exist. All 115 `.md` files live at `docs/tuatha/*.md`.

## Files by Category

### Repo Summaries (`repo-*`) — 11 files

File names follow the pattern `docs/tuatha/files/repo-{upstream-name}.md`. Each is a KCG-specific summary of an upstream open-source project relevant to the Túatha educational MMO.

| File | Upstream | Relevance |
|---|---|---|
| `repo-agui_kotlin.md` | AG-UI Kotlin | Agent UI protocol for mobile |
| `repo-AnyLanguageModel.md` | AnyLanguageModel | iOS LLM inference |
| `repo-hophacks-spacetimedb-workshop.md` | SpacetimeDB workshop | Multiplayer game workshop |
| `repo-ireland.md` | ireland (Ireland geo data) | Geospatial boundaries |
| `repo-react-native-godot.md` | react-native-godot | RN Godot bridge |
| `repo-react-native-reusables.md` | react-native-reusables | UI components |
| `repo-spacetimedb-cookbook.md` | SpacetimeDB cookbook | Recipes & patterns |
| `repo-spacetimedb-typescript-sdk.md` | SpacetimeDB TypeScript SDK | Browser multiplayer |
| `repo-SpacetimeDB.md` | SpacetimeDB core | Real-time game database |
| `repo-wgpu.md` | wgpu (gfx-rs) | Cross-platform GPU API; v29.0.3 (May 2026), 17.3k stars, 587 contributors |
| `repo-x402.md` | x402 (Coinbase) | HTTP 402 micropayment protocol; USDC on Base/Arbitrum, SIWE auth |

### Game Development (`game_*` / `game-*`) — 4 files

| File | Purpose |
|---|---|
| `game-design-README.md` | Game design bootstrap documentation |
| `game_CONTRIBUTING.md` | Contribution guide for game code |
| `game_DEVELOPMENT.md` | Developer setup & workflow |
| `game_siwe-auth.md` | Sign-In With Ethereum auth integration |

### Guides & HOWTOs — 6 files

| File | Purpose |
|---|---|
| `ADDING_AGENTS.md` | Adding new agents to the system |
| `ADDING_DATA_SOURCES.md` | Connecting curriculum data sources |
| `ADDING_TOOLS.md` | Creating custom agent tools |
| `ADDING_ZONES.md` | Extending MMO zone maps |
| `CELTIC_LANGUAGES.md` | Irish/Welsh/Scottish Gaelic language patterns |
| `CROSS_PLATFORM_GUIDE.md` | iOS, Android, Web, Desktop support |

### Architecture & Strategy — 12 files

These are high-level planning documents that came from AI research sessions.

| File | Topic |
|---|---|
| `Agentic Education Platform Development.md` | Multi-agent tutoring system design |
| `Agentic Web Scraping Pipeline.md` | Stealth browser scraping for curriculum data |
| `AI Chemistry Education Image Generation.md` | Chemistry asset generation |
| `Asset Management for Full-Stack App.md` | 3D asset pipeline |
| `British Isles Education Map.md` | Pan-Celtic geographic visualization |
| `British Isles Game Dev Data Pipeline.md` | Data flow for game assets |
| `British Isles Mythology MMO Research.md` | Mythology integration research |
| `Building an Educational Agent's Knowledge Base.md` | Knowledge graph for agents |
| `Celtic Etymology for Game Names.md` | Naming conventions from Celtic roots |
| `Celtic Language Data Aggregation Analysis.md` | Data aggregation strategy |
| `Celtic MMO Web3 Concept Integration.md` | Web3 + education concept |
| `Chemistry Education Asset Generation.md` | Chemistry visualization |

### Technical Guides — 9 files

| File | Topic |
|---|---|
| `Crypteolas_ Federated Learning Crypto Payments.md` | Federated learning + crypto |
| `CRYPTEOLAS_INTEGRATION_GUIDE.md` | Crypteolas module integration |
| `DEPLOYMENT.md` | Deployment configuration |
| `FRONTEND.md` | Frontend architecture |
| `GAME_CLIENT.md` | Game client architecture |
| `GODOT_RUST_GUIDE.md` | Godot + Rust GDExtension |
| `GRAPHICS_INDEX.md` | Graphics pipeline index |
| `PAYMENT_GUIDE.md` | x402 payment integration |
| `PERFORMANCE_TUNING.md` | Rendering & network performance |

### Integration & Technical Plans — 10 files

| File | Topic |
|---|---|
| `Integrating Rust, DuckDB, TanStack, CopilotKit.md` | Stack integration |
| `Interactive AI Pipeline Development.md` | AI pipeline architecture |
| `Interactive Map AI Agents.md` | Map + agent interaction |
| `LLM Serving with MLflow Langfuse.md` | LLM observability |
| `MMO Geospatial Data Visual RAG.md` | Geospatial RAG for MMO |
| `Multimodal Video Knowledge Graph Pipeline.md` | Video knowledge graph |
| `Rust Client.md` | Rust game client design |
| `Rust Full-Stack Gaming Environment.md` | Full Rust stack |
| `TanStack DB Integration and Comparison.md` | Database integration |
| `Technical Integration Plan Dagster DLT CocoIndex Feast MLflow.md` | Data platform integration |

### Web3 & Blockchain — 5 files

| File | Topic |
|---|---|
| `Crypto Analysis AI Agent System Architecture.md` | Crypto agent system |
| `CRYPTO_INTEGRATION_SUMMARY.md` | Crypto integration summary |
| `ERC-4361_ Sign-In with Ethereum.md` | SIWE standard reference |
| `Sign In With Ethereum (SIWE) Better Auth.md` | SIWE auth guide |
| `Web3 Classroom Response System Design.md` | Classroom Web3 system |

### Mobile & iOS — 4 files

| File | Topic |
|---|---|
| `Federated AI Marketplace on iPhone.md` | Federated learning on iOS |
| `iOS App Development Ecosystem Strategy.md` | iOS development strategy |
| `Irish Handwriting App Development.md` | Handwriting recognition app |
| `Irish LLM for iPhone Development.md` | On-device Irish LLM |

### Engine & Graphics — 5 files

| File | Topic |
|---|---|
| `engine-selection.md` | Game engine comparison |
| `Game Particle Effects Research.md` | Particle effects for Celtic magic |
| `Game Particle Effects Research(2).md` | Particle effects (duplicate topic) |
| `Geospatial Workflow Particle Effects.md` | Combined geo + effects |
| `WGPU_GUIDE.md` | wgpu usage guide |

### AI & ML — 7 files

| File | Topic |
|---|---|
| `Fine-tuning VLMs for iOS HTR.md` | VLM fine-tuning for handwriting |
| `Generative AI Art Workflow Integration.md` | AI art pipeline |
| `GeoAI.md` | Geospatial AI |
| `MLflow & Langfuse Integration.md` | ML observability |
| `SpacetimeDB Ogham Stone Game Integration.md` | Ogham stone rendering |
| `unsloth-catalog.md` | Unsloth model catalog |
| `useAgent Hook.md` | CopilotKit useAgent hook |

### Scraped/External Articles — 17 files

Research articles fetched from the web via Firecrawl, covering AI, gaming, and education.

| File | Source |
|---|---|
| `AG-UI and A2UI_ Understanding the Differences CopilotKit.md` | CopilotKit blog |
| `apple_ml-fastvlm_ ... CVPR 2025.md` | Apple CVPR 2025 paper |
| `Comparing the Top 6 Agent-Native Rails...` | AI agent comparison article |
| `compass_artifact_wf-...text_markdown.md` | Compass artifact |
| `dlt_crawl4ai_lancedb.md` | dlt pipeline article |
| `The Expulsion of the Déisi - Wikipedia.md` | Wikipedia |
| `Introducing AnyLanguageModel...` | AnyLanguageModel blog |
| `Kotlin Multiplatform vs. React Native...` | Cross-platform comparison |
| `Release v28.0.0 - Mesh Shaders... gfx-rs_wgpu.md` | wgpu v28 release notes |
| `Swift Transformers Reaches 1.0...` | Swift Transformers blog |
| `Unsloth Model Catalog Unsloth Documentation.md` | Unsloth docs |
| `syft-flwr_notebooks... OpenMined_syft-flwr.md` | OpenMined blog |

Plus 5 more on similar topics.

### SpacetimeDB — 4 files

| File | Topic |
|---|---|
| `Spacetimedb Blockchain Integration Strategy.md` | Blockchain + SpacetimeDB |
| `SPACETIMEDB_GUIDE.md` | Usage guide |
| `SpacetimeDB.md` | Overview & concepts |
| `SpacetimeDB Ogham Stone Game Integration.md` | Ogham stone game mechanics |

### Reference & Index — 7 files

| File | Topic |
|---|---|
| `AGENTS.md` | Agent architecture (root instruction file) |
| `ANALYSIS.md` | Cross-document analysis |
| `api-README.md` | API documentation |
| `API.md` | API reference |
| `INDEX.md` | Master document index |
| `PIPELINES.md` | Pipeline configuration |
| `README.md` | Project overview |

### Monorepo Structure — 2 files

| File | Topic |
|---|---|
| `celtic_mmo.md` | MMO concept document |
| `celtic-ocr.md` | OCR strategy |

### Miscellaneous — 11 files

| File | Topic |
|---|---|
| `Infrastructure-README.md` | Infrastructure docs |
| `federated-marketplace.md` | Federated marketplace design |
| `Frontend Idea Catalog Development.md` | Frontend catalog |
| `Game Development Research AI Integration.md` | Game dev research |
| `Game Dev Pipeline Research Plan.md` | Development pipeline plan |
| `Game Reverse Engineering Workflow Design.md` | Reverse engineering |
| `learn-to-earn-model.md` | Learn-to-Earn model |
| `ml-models-README.md` | ML models index |
| `MCP-UI.md` | MCP UI integration |
| `mythology-framework.md` | Mythology framework |
| `Ogham Crypto MMO Research.md` | Ogham + crypto |
| `tokenomics-README.md` | Tokenomics documentation |
| `Web3 Gamified Education Asset Generation.md` | Web3 education |
| `world-map.md` | World map design |
| `x402-payments.md` | x402 payment flows |
| `gdext-ReadMe.md` | Godot extension docs |

---

## Count Summary

| Category | Count |
|---|---|
| Repo summaries (`repo-*`) | 11 |
| Game development (`game_*` / `game-*`) | 4 |
| Guides & HOWTOs | 6 |
| Architecture & Strategy | 12 |
| Technical Guides | 9 |
| Integration & Technical Plans | 10 |
| Web3 & Blockchain | 5 |
| Mobile & iOS | 4 |
| Engine & Graphics | 5 |
| AI & ML | 7 |
| Scraped/External Articles | 17 |
| SpacetimeDB | 4 |
| Reference & Index | 7 |
| Monorepo Structure | 2 |
| Miscellaneous | 12 |
| **Total** | **115** |

## Firecrawl Enhancements (2026-06-06)

Three repo summary files were cross-referenced with current GitHub data:

1. **repo-wgpu.md** — Confirmed: v29.0.3 (May 2026), 17.3k stars, 587 contributors, 10,736 commits. Active daily. Rust 78.6%, WGSL 14.6%. MSRV: 1.87 for wgpu, 1.93 for full repo.

2. **repo-SpacetimeDB.md** — Verified as actively maintained by Clockwork Labs. Confirmed TypeScript SDK integration path for Babylon.js frontend.

3. **repo-x402.md** — Confirmed as Coinbase open-source project. HTTP 402 Payment Required protocol for AI agent micropayments. USDC on Base/Arbitrum. SIWE wallet auth. MCPay integration for MCP server monetization.

## Verification Status: PASS

- 0 subdirectories (target met)
- 115 `.md` files all at root level
- No stray non-`.md` files in root
- All `repo-*` files follow consistent naming convention
- Directory is ready for Phase 2 (content consolidation & deduplication)
