# Game Development Reference Library

Central reference library for the **Tuath Celtic Educational MMO** and Cianfhoghlaim game development technologies. This collection contains strategy docs, research essays, technical guides, and skeletonized upstream mirrors for multiplayer infrastructure, graphics programming, cross-platform development, and payment systems.

For the full file catalog, see [INDEX.md](INDEX.md). For project-level analysis of the broader Cianfhoghlaim stack, see [ANALYSIS.md](ANALYSIS.md).

---

## Mission

Tuath is a Celtic educational MMO that teaches Irish, Welsh, Scottish Gaelic, and Manx through quests grounded in authentic mythology and history. It is being built atop:

- **SpacetimeDB** as the persistent multiplayer backend (Rust)
- **Babylon.js 7 + WebGPU** as the browser client
- **TanStack Start** for the React UI shell
- **x402** for HTTP 402-based micropayments
- **Google ADK + AG-UI** for the multi-agent tutoring system
- **LiteLLM** as the model gateway
- **Celtic cultural partnerships** (Foras na Gaeilge, Teanglann.ie, Abair.ie)

---

## Strategic Documents

High-level strategy documents for platform and technology decisions. All moved to [`01-game-design/`](01-game-design/) and [`05-ios-ml/`](05-ios-ml/).

| Document | Location | Description |
|----------|----------|-------------|
| [Celtic Naming for the MMO](01-game-design/Celtic%20Naming%20for%20the%20MMO.md) | `01-game-design/` | Philological survey + Web3 conflict analysis for *Anam*, *Tír*, *Aran*, *Cymr*, *Gaelg*, *Iwerz* |
| [mythology-framework.md](01-game-design/mythology-framework.md) | `01-game-design/` | Pent-elemental cosmology + Anam Cara mechanic |
| [engine-selection.md](01-game-design/engine-selection.md) | `01-game-design/` | "Anam" MMO ecosystem — agentic AI, x402, runtimes |
| [iOS App Development Ecosystem Strategy](05-ios-ml/iOS%20App%20Development%20Ecosystem%20Strategy.md) | `05-ios-ml/` | KMP + Swift + Rust sandwich architecture |
| [Kotlin Multiplatform vs React Native](07-clippings/Kotlin%20Multiplatform%20vs.%20React%20Native_%20A%20cross-platform%20comparison%20_%20Kotlin%20Multiplatform.md) | `07-clippings/` | Cross-platform framework comparison (clipping) |

---

## Core Technologies

### Real-Time Multiplayer

The backbone of the Celtic MMO's multiplayer architecture. All skeletonized mirrors live in [`08-mirrors/`](08-mirrors/).

| Mirror | KCG Summary | Description | Language |
|--------|-------------|-------------|----------|
| [SpacetimeDB/](08-mirrors/SpacetimeDB/) | [repo-SpacetimeDB.md](08-mirrors/_summaries/repo-SpacetimeDB.md) | Relational database with embedded server logic. Write modules in Rust that run directly in the database. Used as the entire backend for BitCraft Online MMORPG. | Rust |
| [spacetimedb-typescript-sdk/](08-mirrors/spacetimedb-typescript-sdk/) | [repo-spacetimedb-typescript-sdk.md](08-mirrors/_summaries/repo-spacetimedb-typescript-sdk.md) | TypeScript client SDK for SpacetimeDB connections. | TypeScript |
| [spacetimedb-cookbook/](08-mirrors/spacetimedb-cookbook/) | [repo-spacetimedb-cookbook.md](08-mirrors/_summaries/repo-spacetimedb-cookbook.md) | Examples and patterns — chat apps, game state sync, OIDC, VoIP. | Rust/TS |
| [hophacks-spacetimedb-workshop/](08-mirrors/hophacks-spacetimedb-workshop/) | [repo-hophacks-spacetimedb-workshop.md](08-mirrors/_summaries/repo-hophacks-spacetimedb-workshop.md) | Workshop materials for learning SpacetimeDB from scratch. | Rust/TS |

**Key Concepts:** Modules (stored procedures), Reducers (typed mutators), Subscriptions (real-time queries), Identity (WebSocket auth).

### Game Engines

| Mirror | KCG Summary | Description | Language |
|--------|-------------|-------------|----------|
| [gdext/](08-mirrors/gdext/) | *(no separate summary; see file)* | godot-rust bindings for Godot 4. | Rust |
| [react-native-godot/](08-mirrors/react-native-godot/) | [repo-react-native-godot.md](08-mirrors/_summaries/repo-react-native-godot.md) | Embed Godot in React Native apps (skeleton only). | TypeScript/C++ |

### Graphics Programming

| Mirror | KCG Summary | Description | Language |
|--------|-------------|-------------|----------|
| [wgpu/](08-mirrors/wgpu/) | [repo-wgpu.md](08-mirrors/_summaries/repo-wgpu.md) | Cross-platform WebGPU implementation in Rust. Runs on Vulkan, Metal, DX12, OpenGL, WebGPU. | Rust |

See the [WGPU guide](04-game-tech/reference/guides/WGPU_GUIDE.md) for the Tuath-specific rendering pipeline.

### Cross-Platform Development

| Mirror | KCG Summary | Description | Language |
|--------|-------------|-------------|----------|
| [AnyLanguageModel/](08-mirrors/AnyLanguageModel/) | [repo-AnyLanguageModel.md](08-mirrors/_summaries/repo-AnyLanguageModel.md) | Swift package for LLM provider unification. | Swift |
| [react-native-reusables/](08-mirrors/react-native-reusables/) | [repo-react-native-reusables.md](08-mirrors/_summaries/repo-react-native-reusables.md) | shadcn/ui-style components for React Native. | TypeScript |
| [agui_kotlin/](08-mirrors/agui_kotlin/) | [repo-agui_kotlin.md](08-mirrors/_summaries/repo-agui_kotlin.md) | AG-UI Kotlin Multiplatform SDK (skeleton only). | Kotlin |

### Payment & Monetization

[x402](../README.md#x402-payments) is the protocol used in Tuath for in-game microtransactions.

| Component | Description | Language |
|-----------|-------------|----------|
| [x402/typescript/](08-mirrors/x402/typescript/) | TypeScript implementation (Express, Hono, Next.js middleware) | TypeScript |
| [x402/go/](08-mirrors/x402/go/) | Go implementation (facilitators, servers) | Go |
| [x402/python/](08-mirrors/x402/python/) | Python implementation (FastAPI, Flask) | Python |
| [x402/x402-rs/](08-mirrors/x402/x402-rs/) | Rust implementation with Axum middleware | Rust |
| [x402/a2a-x402/](08-mirrors/x402/a2a-x402/) | Agent-to-Agent payments using x402 | Python |

**Use cases:** AI inference APIs, content access, agent payments, in-game items.

**Example server (Hono):**
```typescript
import { Hono } from 'hono';
import { x402Middleware } from 'x402-hono';

const app = new Hono();
app.use('/premium/*', x402Middleware({
  paymentAddress: '0x...',
  price: { amount: '0.001', currency: 'USDC' }
}));
```

---

## Architecture for Tuath Celtic MMO

This reference library supports the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Platforms                         │
├─────────────────┬──────────────────┬────────────────────────┤
│   Web Browser   │   iOS/Android    │   Desktop (Godot)      │
│   (Babylon.js)  │ (React Native +  │   (Rust via gdext)     │
│                 │     Godot)       │                        │
└────────┬────────┴────────┬─────────┴───────────┬────────────┘
          │                 │                     │
          └────────────────┬┴─────────────────────┘
                           │
          ┌────────────────▼────────────────────┐
          │         SpacetimeDB Module          │
          │   (Rust - game logic & persistence) │
          └────────────────┬────────────────────┘
                           │
          ┌────────────────▼────────────────────┐
          │          x402 Payments              │
          │   (Micropayments for premium)       │
          └─────────────────────────────────────┘
```

---

## Consolidated Layout (as of 2026-06-13)

```
docs/tuatha/
├── README.md              ← you are here
├── INDEX.md               ← file catalog
├── ANALYSIS.md            ← Cianfhoghlaim project analysis
├── 00-nav/                ← API, graphics index, pipelines
├── 01-game-design/        ← Celtic MMO concept (10 files)
├── 02-agents/             ← Tuath agent system + framework context (2 files)
├── 03-data-pipelines/     ← DLT, Dagster, CocoIndex, MLflow, federated (15 files)
├── 04-game-tech/          ← Engine research (9 files)
│   └── reference/         ← Operational docs + 5 implementation guides
├── 05-ios-ml/             ← Celtic OCR, on-device LLMs, Apple stack (6 files)
├── 06-tokenomics/         ← x402, SIWE, learn-to-earn (3 files)
├── 07-clippings/          ← External articles, archived (11 files)
├── 08-mirrors/            ← 11 skeletonized upstream repos (95 MB)
│   └── _summaries/        ← 11 KCG one-page summaries
└── (misplaced files deleted in 2026-06-13 consolidation)
```

---

## ML Models Catalog

See `meaisínfhoghlaim/catalog/models.yaml` for the complete model registry including:
- Image generation (FLUX, SDXL)
- Celtic language models (UCCIX-Llama2, GaBERT)
- Embeddings (BGE-M3, ColPali)
- Speech (Chatterbox TTS, Wav2Vec2)
- OCR (PaddleOCR, DeepSeek-OCR, Granite Docling)

---

## Contributing

This is a reference library — the actual source code lives in the upstream repositories. For implementation guidance, see the individual project documentation and the Tuath development guides in [`04-game-tech/reference/`](04-game-tech/reference/).
