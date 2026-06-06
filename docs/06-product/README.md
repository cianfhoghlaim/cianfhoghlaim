---
domain: product
title: Product Documentation
description: Consolidated knowledge base for the Túatha educational MMO, Crypteolas crypto payment platform, game development, and Celtic educational ecosystem.
supersedes:
  - docs/tuatha/README.md
  - docs/tuatha/INDEX.md
  - docs/tuatha/ANALYSIS.md
  - docs/tuatha/FRONTEND.md
  - docs/tuatha/DEPLOYMENT.md
  - docs/tuatha/PIPELINES.md
  - docs/tuatha/AGENTS.md
  - docs/tuatha/API.md
  - docs/tuatha/api-README.md
  - docs/tuatha/GAME_CLIENT.md
  - docs/tuatha/CROSS_PLATFORM_GUIDE.md
  - docs/tuatha/ADDING_AGENTS.md
  - docs/tuatha/ADDING_ZONES.md
  - docs/tuatha/ADDING_DATA_SOURCES.md
  - docs/tuatha/ADDING_TOOLS.md
  - docs/tuatha/CELTIC_LANGUAGES.md
  - docs/tuatha/Building an Educational Agent's Knowledge Base.md
  - docs/tuatha/Interactive AI Pipeline Development.md
  - docs/tuatha/Agentic Web Scraping Pipeline.md
  - docs/tuatha/Agentic Education Platform Development.md
  - docs/tuatha/Multimodal Video Knowledge Graph Pipeline.md
  - docs/tuatha/British Isles Game Dev Data Pipeline.md
  - docs/tuatha/Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow (with DuckDB & Dragonfly).md
  - docs/tuatha/LLM Serving with MLflow & Langfuse.md
  - docs/tuatha/Kotlin Multiplatform vs. React Native_ A cross-platform comparison _ Kotlin Multiplatform.md
  - docs/tuatha/iOS App Development Ecosystem Strategy.md
  - docs/tuatha/Frontend Idea Catalog Development.md
  - docs/tuatha/Asset Management for Full-Stack App.md
  - docs/tuatha/TanStack DB Integration and Comparison.md
  - docs/tuatha/MCP-UI.md
  - docs/tuatha/useAgent Hook.md
  - docs/tuatha/GeoAI.md
  - docs/tuatha/compass_artifact_wf-918fd144-3e32-416f-b59b-15a043b18fc1_text_markdown.md
  - docs/tuatha/Swift Transformers Reaches 1.0 – and Looks to the Future.md
  - docs/tuatha/Introducing AnyLanguageModel_ One API for Local and Remote LLMs on Apple Platforms.md
  - docs/tuatha/Integrating Rust, DuckDB, TanStack, CopilotKit.md
  - docs/tuatha/Generative AI Art Workflow Integration.md
cognee_entities:
  - entity: TuathaMMO
    type: GameProduct
    relationships:
      - uses: SpacetimeDB
      - uses: GodotEngine
      - uses: BabylonJS
      - uses: CelticLanguageModels
      - implements: LearnToEarn
  - entity: CrypteolasPlatform
    type: PaymentPlatform
    relationships:
      - uses: x402Protocol
      - uses: Ethereum
      - implements: Micropayments
ccc_query_hints:
  - "Celtic MMO architecture"
  - "Túatha game design"
  - "crypto payment integration"
  - "educational game platform"
  - "learn-to-earn model"
updated: 2026-06-06
---

# Product Documentation

The product ecosystem spans two major products: **Túatha** (a Celtic educational MMO) and **Crypteolas** (a crypto payment and tokenomics platform). Together they form a decentralized, gamified educational experience anchored in Celtic mythology and powered by autonomous agentic workflows.

## Products

| Product | Description | Status |
|---------|-------------|--------|
| **Túatha** | Educational MMO traversing Celtic mythology, language, and geography | Active development |
| **Crypteolas** | x402 micropayment protocol integration, SIWE auth, Learn-to-Earn tokenomics | Active development |
| **Celtic OCR** | Gaelic manuscript digitization pipeline (document intelligence) | Research |
| **Federated Marketplace** | Decentralized AI model training with federated learning | Research |

## Core Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Multiplayer Backend** | SpacetimeDB | Real-time game state sync, embedded Rust server logic |
| **Game Engine** | Godot 4 + Rust (gdext) | Native game client with type-safe game logic |
| **Web Client** | Babylon.js | Browser-based 3D rendering |
| **Payments** | x402 Protocol, USDC on Base/Arbitrum | Micropayment gateway, HTTP 402 |
| **Identity** | BetterAuth + SIWE (ERC-4361) | Wallet-based authentication |
| **Blockchain** | EVM-compatible (Base, Arbitrum) | Smart contracts, token settlement |
| **AI/Agents** | Google ADK, Agno, Unsloth | Multi-agent tutoring, LLM fine-tuning |
| **ML Models** | FLUX.1, SDXL, Qwen2-VL, GaBERT, BGE-M3 | Asset gen, language, embeddings |
| **Data Pipeline** | Dagster, DLT, CocoIndex, LanceDB, DuckDB | Curriculum ingestion, knowledge graphs |
| **Graphics** | wgpu (Vulkan/Metal/DX12), Babylon.js, Godot | Cross-platform rendering, Celtic shaders |
| **Mobile** | React Native + Godot, Kotlin Multiplatform, Swift | iOS/Android clients |
| **Infrastructure** | Docker, Komodo, Pangolin, Infisical | Self-hosted orchestration, secrets |

## Architecture Overview

```
                    ┌──────────────────────────────────────────┐
                    │            Client Platforms               │
                    ├──────────────┬───────────────┬───────────┤
                    │  Web Browser  │  iOS/Android  │  Desktop  │
                    │  (Babylon.js) │ (RN + Godot)  │  (Godot)  │
                    └──────┬───────┴───────┬───────┴─────┬─────┘
                           │               │             │
                    ┌──────▼───────────────▼─────────────▼─────┐
                    │          SpacetimeDB Module              │
                    │    (Rust — game logic & persistence)      │
                    └──────────────────┬───────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────┐
                    │            x402 Payments                 │
                    │     (Micropayments for premium content)  │
                    └──────────────────┬───────────────────────┘
                                       │
                    ┌──────────────────▼───────────────────────┐
                    │       AI Agent Layer (Google ADK)        │
                    │  (Tutor, Narrator, Quest Guide, Research)│
                    └──────────────────────────────────────────┘
```

## Documentation Map

- **[celtic-mmo.md](./celtic-mmo.md)** — Celtic MMO design, SpacetimeDB, Anam, mythology, game architecture
- **[crypteolas.md](./crypteolas.md)** — Crypto, x402, SIWE, tokenomics, Web3, NFT, DAO
- **[game-development.md](./game-development.md)** — Godot, wgpu, Rust, Babylon.js, game pipeline, particle effects
- **[educational-platform.md](./educational-platform.md)** — Education platform, Leaving Cert, curriculum, interactive learning

## Directory Sizes (Research Libraries)

| Library | Size | Language | Purpose |
|---------|------|----------|---------|
| react-native-godot | 87MB | TypeScript/C++ | Embed Godot in React Native |
| x402 | 66MB | TS/Go/Python/Rust | HTTP micropayment protocol |
| SpacetimeDB | 51MB | Rust | Real-time game database (24.7k stars) |
| wgpu | 37MB | Rust | Cross-platform GPU API (17.3k stars) |
| react-native-reusables | 33MB | TypeScript | shadcn-style mobile components |
| gdext | 15MB | Rust | Godot 4 GDExtension bindings |
| spacetimedb-cookbook | 9.6MB | Rust/TS | Recipes and patterns |
| agui_kotlin | 2.2MB | Kotlin | AG-UI mobile SDK |
| AnyLanguageModel | 748KB | Swift | Multi-provider LLM API |

## ML Models Catalog

| Category | Models |
|----------|--------|
| **Image Generation** | FLUX.1-dev/schnell, SDXL Turbo |
| **Celtic Language** | UCCIX-Llama2, GaBERT |
| **Embeddings** | BGE-M3, ColPali |
| **Speech** | Chatterbox TTS, Wav2Vec2, Whisper |
| **OCR** | PaddleOCR, DeepSeek-OCR, Granite Docling |
| **Vision-Language** | Qwen2-VL-7B, FastVLM (Apple CVPR 2025) |

## Contributing

This is a reference library — actual source code lives in upstream repositories. See individual product documentation for implementation guides.
