# Game Development Reference Library

Central reference library for the Tuath Celtic MMO and Cianfhoghlaim game development technologies. This collection contains source code, examples, and documentation for multiplayer infrastructure, graphics programming, cross-platform development, and payment systems.

## Strategic Documents

High-level strategy documents for platform and technology decisions:

| Document | Description |
|----------|-------------|
| [Irish Handwriting App Development](./Irish%20Handwriting%20App%20Development.md) | Technical strategy for handwriting recognition app targeting Irish Gaelic learners |
| [iOS App Development Ecosystem Strategy](./iOS%20App%20Development%20Ecosystem%20Strategy.md) | Comprehensive strategy for Swift, SwiftUI, and Apple platform development |
| [Kotlin Multiplatform vs React Native](./Kotlin%20Multiplatform%20vs.%20React%20Native_%20A%20cross-platform%20comparison%20_%20Kotlin%20Multiplatform.md) | Cross-platform framework comparison for mobile development decisions |

---

## Core Technologies

### Real-Time Multiplayer

The backbone of the Celtic MMO's multiplayer architecture.

| Directory | Description | Language |
|-----------|-------------|----------|
| [SpacetimeDB](./SpacetimeDB/) | Relational database with embedded server logic. Write modules in Rust that run directly in the database. Used as the entire backend for BitCraft Online MMORPG. | Rust |
| [spacetimedb-typescript-sdk](./spacetimedb-typescript-sdk/) | TypeScript client SDK for SpacetimeDB connections. Provides type-safe subscriptions and reducer calls. | TypeScript |
| [spacetimedb-cookbook](./spacetimedb-cookbook/) | Collection of examples and patterns for SpacetimeDB development. Includes chat apps, game state sync, and authentication. | Rust/TS |
| [hophacks-spacetimedb-workshop](./hophacks-spacetimedb-workshop/) | Workshop materials for learning SpacetimeDB from scratch. | Rust/TS |

**Key Concepts:**
- **Modules**: Application logic that runs inside the database as stored procedures
- **Reducers**: Type-safe functions called by clients that modify database state
- **Subscriptions**: Real-time queries that push updates to connected clients
- **Identity**: Built-in authentication with WebSocket connection tokens

### Game Engines

Native game engine integrations for high-performance gameplay.

| Directory | Description | Language |
|-----------|-------------|----------|
| [gdext](./gdext/) | **godot-rust** bindings for Godot 4. Write game logic in Rust with full type safety and memory safety. | Rust |
| [react-native-godot](./react-native-godot/) | Embed Godot game views inside React Native applications. Bridge between mobile UI and game engine. | TypeScript/C++ |

**gdext Features:**
- Full GDExtension API coverage
- Procedural macros for class definitions (`#[derive(GodotClass)]`)
- Type-safe signal connections
- Hot-reload support for rapid iteration

### Graphics Programming

Low-level graphics APIs and rendering technologies.

| Directory | Description | Language |
|-----------|-------------|----------|
| [wgpu](./wgpu/) | Cross-platform WebGPU implementation in Rust. Runs natively on Vulkan, Metal, D3D12, OpenGL and WebGPU/WebGL2 on WASM. | Rust |

**Platform Support:**
| API | Windows | Linux/Android | macOS/iOS | Web |
|-----|---------|---------------|-----------|-----|
| Vulkan | Y | Y | MoltenVK | - |
| Metal | - | - | Y | - |
| DX12 | Y | - | - | - |
| OpenGL | GL 3.3+ | GLES 3.0+ | ANGLE | WebGL2 |
| WebGPU | - | - | - | Y |

---

## Cross-Platform Development

### AI & Language Models

| Directory | Description | Language |
|-----------|-------------|----------|
| [AnyLanguageModel](./AnyLanguageModel/) | Swift package providing unified API for multiple LLM providers. Drop-in replacement for Apple's Foundation Models with support for Anthropic, OpenAI, Gemini, Ollama, MLX, llama.cpp. | Swift |

**Supported Providers:**
- Apple Foundation Models (on-device)
- Core ML models
- MLX (Apple Silicon optimized)
- llama.cpp (GGUF models)
- Ollama, Anthropic, Google Gemini, OpenAI

### UI & Components

| Directory | Description | Language |
|-----------|-------------|----------|
| [react-native-reusables](./react-native-reusables/) | Production-ready React Native UI components. shadcn/ui-style patterns for mobile. | TypeScript |
| [agui_kotlin](./agui_kotlin/) | AG-UI Kotlin Multiplatform SDK. Connect applications to AI agents implementing the Agent User Interaction Protocol. | Kotlin |

---

## Payment & Monetization

### x402 Payment Protocol

[x402](./x402/) provides HTTP-based micropayments using the `402 Payment Required` status code. Enable pay-per-request APIs without traditional payment infrastructure.

| Component | Description | Language |
|-----------|-------------|----------|
| [x402/typescript](./x402/typescript/) | TypeScript implementation with Express, Hono, Next.js middleware | TypeScript |
| [x402/go](./x402/go/) | Go implementation for facilitators and servers | Go |
| [x402/python](./x402/python/) | Python implementation for FastAPI, Flask servers | Python |
| [x402/x402-rs](./x402/x402-rs/) | Rust implementation with Axum middleware | Rust |
| [x402/a2a-x402](./x402/a2a-x402/) | Agent-to-Agent payments using x402 | Python |

**Use Cases:**
- **AI Inference APIs**: Pay per token/request
- **Content Access**: Micropayments for articles, media
- **Agent Payments**: AI agents paying for services autonomously
- **Game Items**: In-game purchases without app store fees

**Example Server (Hono):**
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

## Quick Start Guides

### Setting Up SpacetimeDB

```bash
# Install CLI
curl -sSf https://spacetimedb.com/install | sh

# Create a new module
spacetime init my-game --lang rust

# Publish to cloud
spacetime publish my-game
```

### Setting Up Godot + Rust

```bash
# Create Rust library
cargo new --lib my-godot-extension

# Add gdext dependency
cargo add godot

# Build extension
cargo build
```

### Setting Up wgpu

```bash
# Add to Cargo.toml
cargo add wgpu

# Run examples
cargo run --bin wgpu-examples cube
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

## Directory Sizes

| Directory | Size | Primary Language |
|-----------|------|------------------|
| react-native-godot | 87MB | TypeScript/C++ |
| x402 | 66MB | TypeScript/Go/Python/Rust |
| SpacetimeDB | 51MB | Rust |
| wgpu | 37MB | Rust |
| react-native-reusables | 33MB | TypeScript |
| gdext | 15MB | Rust |
| spacetimedb-cookbook | 9.6MB | Rust/TypeScript |
| agui_kotlin | 2.2MB | Kotlin |
| spacetimedb-typescript-sdk | 944KB | TypeScript |
| AnyLanguageModel | 748KB | Swift |
| hophacks-spacetimedb-workshop | 328KB | Rust/TypeScript |

---

## Graphics & Rendering Index

Comprehensive documentation for graphics, shaders, particles, and visual effects.

**[GRAPHICS_INDEX.md](./GRAPHICS_INDEX.md)** - Complete catalog of all graphics documentation

### Implementation Guides

| Guide | Focus |
|-------|-------|
| [WGPU_GUIDE.md](./docs/WGPU_GUIDE.md) | WebGPU rendering, terrain/water shaders, particle systems |
| [GODOT_RUST_GUIDE.md](./docs/GODOT_RUST_GUIDE.md) | GDExtension development, signals, zones, SpacetimeDB |
| [SPACETIMEDB_GUIDE.md](./docs/SPACETIMEDB_GUIDE.md) | Multiplayer backend, reducers, subscriptions |
| [CROSS_PLATFORM_GUIDE.md](./docs/CROSS_PLATFORM_GUIDE.md) | Kotlin, Swift, React Native + Godot |

### Advanced Research

| Document | Description |
|----------|-------------|
| [Game Particle Effects Research](./Game%20Particle%20Effects%20Research(2).md) | "Anam Initiative" - Meteorological particle simulation with Unreal Niagara, Unity VFX Graph, Godot compute shaders |
| [Geospatial Workflow & Particle Effects](./Geospatial%20Workflow%20%26%20Particle%20Effects(1).md) | Cloud-native OLAP with DuckDB, WebGPU particle rendering |

### Celtic Shaders (crates/wgpu/celtic-shaders/)

| Shader | Description |
|--------|-------------|
| Knotwork | SDF-based interlacing Celtic patterns |
| Spiral/Triskele | Multi-arm Archimedean spirals with glow |
| Fire/Magic | Billboard particle quads with life fade |
| Particle Compute | GPU physics: gravity, wind, turbulence |
| Terrain | Fog, normal mapping, diffuse lighting |

---

## Asset Generation

AI-assisted game asset generation system in `sruth/tuath/asset_generation/`:

### Supported Models

| Model | Purpose |
|-------|---------|
| FLUX.1-dev/schnell | High quality texture generation |
| SDXL Turbo | Fast texture fallback |
| Qwen2-VL-7B | Vision-language for style analysis |

### Celtic Art Styles

| Style | Use Cases |
|-------|-----------|
| La Tène | Weapons, armor, artifacts |
| Ogham | Quest items, runic effects |
| Knotwork | UI borders, textures |
| Zoomorphic | Creatures, clan heraldry |
| Spiral | Magical effects, portals |
| Illuminated | UI elements, documents |

### Multi-Engine Export

| Engine | Formats |
|--------|---------|
| Godot 4 | .tres, .tscn, .material |
| Unity | .prefab, .asset, .mat |
| Unreal | .uasset, .umap |
| Babylon.js | ES modules, .babylon |

---

## Related Documentation

- [Tuath System Architecture](../sruth/tuath/docs/ARCHITECTURE.md)
- [Babylon.js Game Client](../sruth/tuath/docs/GAME_CLIENT.md)
- [SpacetimeDB Module Development](./docs/SPACETIMEDB_GUIDE.md)
- [Godot + Rust Integration](./docs/GODOT_RUST_GUIDE.md)
- [wgpu Graphics Programming](./docs/WGPU_GUIDE.md)
- **[Graphics Index](./GRAPHICS_INDEX.md)** - Complete graphics documentation catalog

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

This is a reference library - the actual source code lives in the upstream repositories. For implementation guidance, see the individual project documentation and the Tuath development guides.
