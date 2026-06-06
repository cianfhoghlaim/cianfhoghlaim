# Tuatha Documentation Index

Last updated: 2026-06-06

## Size Summary

| Category | Size | Contents |
|----------|------|----------|
| **Total** | **19 MB** | All docs/tuatha/ (down from 59 MB after skeletonization) |
| Excluding `game/` | **6 MB** | Pure docs + skeletonized SDKs |

## Directory Index

### Pure Documentation (preserved as-is)

| Directory | Size | Purpose |
|-----------|------|---------|
| [game/](game/) | 13 MB | Game client, Godot project, Babylon.js scenes, Anam particle system |
| [game-design/](game-design/) | 120 KB | Game design documents, zone layouts, NPC design, quest structures |
| [docs/](docs/) | 100 KB | Implementation guides: WGPU, Godot/Rust, SpacetimeDB, Cross-Platform |
| [guides/](guides/) | 104 KB | How-to guides: adding agents, tools, Celtic languages, deployment |
| [tokenomics/](tokenomics/) | 84 KB | Crypteolas tokenomics, Web3 economics, SIWE integration |
| [ml-models/](ml-models/) | 80 KB | ML model catalog, training configurations, Irish language model specs |
| [gdext/](gdext/) | 44 KB | Godot GDExtension bindings documentation |
| [api/](api/) | 12 KB | API reference, endpoint documentation, CopilotKit schemas |
| [infrastructure/](infrastructure/) | 4 KB | Deployment infrastructure docs |

### Skeletonized SDKs (`.md` only, source removed)

Each directory contains a `KCG_SUMMARY.md` explaining purpose and relevance to the Kings' College Galway project.

| Directory | Size | Upstream |
|-----------|------|----------|
| [SpacetimeDB/](SpacetimeDB/) | 1.6 MB | [github.com/clockworklabs/SpacetimeDB](https://github.com/clockworklabs/SpacetimeDB) |
| [x402/](x402/) | 1.0 MB | [github.com/coinbase/x402](https://github.com/coinbase/x402) |
| [wgpu/](wgpu/) | 652 KB | [github.com/gfx-rs/wgpu](https://github.com/gfx-rs/wgpu) |
| [agui_kotlin/](agui_kotlin/) | 84 KB | [github.com/ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) |
| [spacetimedb-typescript-sdk/](spacetimedb-typescript-sdk/) | 52 KB | [github.com/clockworklabs/SpacetimeDB](https://github.com/clockworklabs/SpacetimeDB) |
| [AnyLanguageModel/](AnyLanguageModel/) | 44 KB | [github.com/mattt/AnyLanguageModel](https://github.com/mattt/AnyLanguageModel) |
| [react-native-godot/](react-native-godot/) | 40 KB | [github.com/migeran/react-native-godot](https://github.com/migeran/react-native-godot) |
| [spacetimedb-cookbook/](spacetimedb-cookbook/) | 32 KB | [github.com/SpacetimeDB/cookbook](https://github.com/SpacetimeDB/cookbook) |
| [hophacks-spacetimedb-workshop/](hophacks-spacetimedb-workshop/) | 20 KB | [github.com/clockworklabs/hophacks-spacetimedb-workshop](https://github.com/clockworklabs/hophacks-spacetimedb-workshop) |
| [react-native-reusables/](react-native-reusables/) | 16 KB | [github.com/mrzachnugent/react-native-reusables](https://github.com/mrzachnugent/react-native-reusables) |
| [ireland/](ireland/) | 4 KB | Map image collection (KCG_SUMMARY.md only; images removed) |

## Key Standalone Documents

### Architecture & Integration
- [AGENTS.md](AGENTS.md) — Multi-agent system architecture for Celtic language learning
- [Technical Integration Plan_ Dagster + DLT + CocoIndex + Feast + MLflow.md](Technical%20Integration%20Plan_%20Dagster%20%2B%20DLT%20%2B%20CocoIndex%20%2B%20Feast%20%2B%20MLflow%20(with%20DuckDB%20%26%20Dragonfly).md)
- [Integrating Rust, DuckDB, TanStack, CopilotKit.md](Integrating%20Rust%2C%20DuckDB%2C%20TanStack%2C%20CopilotKit.md)
- [PIPELINES.md](PIPELINES.md) — Data pipeline architecture
- [ANALYSIS.md](ANALYSIS.md) — Project analysis

### Game Design & MMO
- [GRAPHICS_INDEX.md](GRAPHICS_INDEX.md) — Graphics, shaders, and rendering index
- [Game Particle Effects Research(2).md](Game%20Particle%20Effects%20Research(2).md) — "Anam" particle system
- [MMO Geospatial Data & Visual RAG.md](MMO%20Geospatial%20Data%20%26%20Visual%20RAG.md)
- [British Isles Mythology MMO Research.md](British%20Isles%20Mythology%20MMO%20Research.md)
- [Celtic MMO Web3 Concept Integration.md](Celtic%20MMO%20Web3%20Concept%20Integration.md)

### Blockchain & Web3
- [CRYPTEOLAS_INTEGRATION_GUIDE.md](CRYPTEOLAS_INTEGRATION_GUIDE.md)
- [CRYPTO_INTEGRATION_SUMMARY.md](CRYPTO_INTEGRATION_SUMMARY.md)
- [Spacetimedb Blockchain Integration Strategy.md](Spacetimedb%20Blockchain%20Integration%20Strategy.md)
- [Learn-to-Earn Blockchain and AI.md](Learn-to-Earn%20Blockchain%20and%20AI.md)

### Platform & Clients
- [GAME_CLIENT.md](GAME_CLIENT.md) — Game client architecture
- [FRONTEND.md](FRONTEND.md) — Frontend strategy
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment guide
- [iOS App Development Ecosystem Strategy.md](iOS%20App%20Development%20Ecosystem%20Strategy.md)

## Skeletonization Notes

- **2026-06-06**: 7 cloned repos skeletonized (source deleted, KCG_SUMMARY.md written). 511 non-`.md` files removed across `agui_kotlin/`, `AnyLanguageModel/`, `spacetimedb-typescript-sdk/`, `react-native-godot/`, `react-native-reusables/`, `hophacks-spacetimedb-workshop/`, `ireland/`. Total size reduced from ~59 MB to ~19 MB.
- **2026-06-05**: `SpacetimeDB/`, `x402/`, `wgpu/`, `spacetimedb-cookbook/` previously skeletonized in Phase 2.
