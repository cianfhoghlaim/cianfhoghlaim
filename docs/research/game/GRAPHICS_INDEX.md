# Graphics, Game Development & Rendering Documentation Index

This index catalogs all graphics, game development, rendering, and visual effects documentation in the Cianfhoghlaim repository.

---

## Core Documentation

### Implementation Guides (taighde/game/docs/)

| File | Lines | Topics |
|------|-------|--------|
| [WGPU_GUIDE.md](docs/WGPU_GUIDE.md) | 700+ | WebGPU rendering, terrain/water shaders, particle systems, render pipelines |
| [GODOT_RUST_GUIDE.md](docs/GODOT_RUST_GUIDE.md) | 760+ | gdext integration, GodotClass macros, signals, zones, SpacetimeDB network |
| [SPACETIMEDB_GUIDE.md](docs/SPACETIMEDB_GUIDE.md) | 710+ | Multiplayer backend, reducers, subscriptions, position sync, zone management |
| [CROSS_PLATFORM_GUIDE.md](docs/CROSS_PLATFORM_GUIDE.md) | 780+ | Kotlin Multiplatform, Swift, React Native + Godot, platform bridging |

---

## Advanced Research Documents

### Particle Systems & Visual Effects

| File | Size | Description |
|------|------|-------------|
| [Game Particle Effects Research(2).md](Game%20Particle%20Effects%20Research(2).md) | 2,500+ lines | **"Anam Initiative"** - Meteorological particle simulation using real weather data. Covers Unreal Niagara, Unity VFX Graph, Godot compute shaders. Includes Catmull-Rom bicubic interpolation, vector quantization, SpacetimeDB streaming. |
| [Geospatial Workflow & Particle Effects(1).md](Geospatial%20Workflow%20%26%20Particle%20Effects(1).md) | 1,800+ lines | Cloud-native OLAP architecture with DuckDB + MotherDuck. WebGPU particle rendering, Lagrangian particle tracking, GeoArrow zero-copy transport, Lonboard + Marimo visualization. |

### Architecture & Integration

| File | Description |
|------|-------------|
| [Integrating Rust, DuckDB, TanStack, CopilotKit.md](Integrating%20Rust%2C%20DuckDB%2C%20TanStack%2C%20CopilotKit.md) | Full-stack integration strategy combining Rust backend, DuckDB analytics, TanStack frontend, and AI copilot |
| [MMO Geospatial Data & Visual RAG.md](MMO%20Geospatial%20Data%20%26%20Visual%20RAG.md) | Integration of Retrieval Augmented Generation with geospatial MMO gameplay |
| [Celtic MMO Web3 Concept Integration.md](Celtic%20MMO%20Web3%20Concept%20Integration.md) | Web3 economics and tokenomics for Celtic MMO |

### Platform Strategy

| File | Description |
|------|-------------|
| [Irish Handwriting App Development.md](Irish%20Handwriting%20App%20Development.md) | Strategy for Irish language handwriting recognition application |
| [iOS App Development Ecosystem Strategy.md](iOS%20App%20Development%20Ecosystem%20Strategy.md) | Apple platform development strategy |
| [Kotlin Multiplatform vs. React Native comparison.md](Kotlin%20Multiplatform%20vs.%20React%20Native%20comparison.md) | Cross-platform framework evaluation |
| [Web3 Classroom Response System Design.md](Web3%20Classroom%20Response%20System%20Design.md) | Interactive education with crypto payments |

---

## Codebase Locations

### Active Game Client

| Location | Technology | Purpose |
|----------|------------|---------|
| `game/godot-client/` | Godot 4.4 + Rust gdext | Desktop game client |
| `game/godot-client/rust/` | SpacetimeDB SDK | Network integration |
| `sruth/tuath/game/client/` | Babylon.js 7 + WebGPU | Web browser client |

### Graphics Crates

| Location | Technology | Purpose |
|----------|------------|---------|
| `crates/wgpu/celtic-shaders/` | WGSL | Knotwork, spiral, fire, terrain shaders |
| `crates/wgpu/particle-system/` | GPU Compute | Particle physics and rendering |

### Reference Libraries

| Location | Size | Contents |
|----------|------|----------|
| `taighde/game/gdext/` | 15MB | Godot-Rust bindings (v0.3.0) |
| `taighde/game/wgpu/` | 37MB | WebGPU implementation + Naga shader compiler |
| `taighde/game/react-native-godot/` | 87MB | React Native + Godot bridge |
| `taighde/game/SpacetimeDB/` | 51MB | Multiplayer database + SDK |

---

## Key Technical Patterns

### From "Anam Initiative" (Particle Effects Research)

```
Meteorological Data Flow:
GRIB2/NetCDF → SpacetimeDB Chunks → Vector Quantization (RGBA8) → GPU Texture
                                                                        ↓
Game Client ← Bicubic Interpolation ← 4-Tap Optimization ← Wind Field Sampling
```

**Key Optimizations:**
- Catmull-Rom bicubic interpolation for smooth flow fields
- 4-tap optimization reduces 16 texture fetches to 4
- Vector quantization: 32-bit float → 8-bit RGBA (50% bandwidth reduction)
- Morton code/Hilbert curve spatial hashing for chunk IDs

**Engine Implementations:**
| Engine | System | Key Features |
|--------|--------|--------------|
| Unreal 5 | Niagara + Grid2D | Custom HLSL modules, Large World Coordinates |
| Unity 6 | VFX Graph + Texture2DArray | Temporal interpolation, compute shaders |
| Godot 4 | RenderingDevice API | GLSL compute shaders, SSBO storage |

### From "Geospatial Workflow"

```
Data Pipeline:
Met Office/GeoHive → DuckDB Spatial → Ibis Abstraction → GeoArrow → WebGPU
                                                                       ↓
                           Marimo Notebook ← Lonboard ← Deck.gl Layers
```

**Stack Components:**
| Layer | Technology | Purpose |
|-------|------------|---------|
| Compute | DuckDB + MotherDuck | Hybrid local/cloud OLAP |
| State | PlanetScale + pg_duckdb | Transactional + analytical |
| Transport | GeoParquet + GeoArrow | Zero-copy binary transfer |
| Render | Lonboard + Deck.gl | WebGPU particle visualization |

---

## Celtic Art Styles (Asset Generation)

Supported styles in `sruth/tuath/asset_generation/`:

| Style | Description | Use Cases |
|-------|-------------|-----------|
| La Tène | Iron Age Celtic patterns | Weapons, armor, artifacts |
| Ogham | Ancient Irish inscription | Quest items, runic effects |
| Knotwork | Interlacing Celtic patterns | UI borders, textures |
| Zoomorphic | Animal-inspired designs | Creature design, clan heraldry |
| Spiral | Triskelion, Newgrange patterns | Magical effects, portals |
| Illuminated | Book of Kells style | UI elements, documents |

---

## Shader Reference

### Celtic Shaders (crates/wgpu/celtic-shaders/)

| Shader | Type | Description |
|--------|------|-------------|
| Knotwork | Fragment | SDF-based interlacing lines with animation |
| Spiral/Triskele | Fragment | Multi-arm Archimedean spirals with glow |
| Fire/Magic | Vertex+Fragment | Billboard particle quads with life fade |
| Particle Compute | Compute | GPU physics: gravity, wind, turbulence |
| Terrain | Vertex+Fragment | Fog, normal mapping, diffuse lighting |

### Default Parameters

```rust
// Knotwork
color_primary: [0.8, 0.6, 0.2, 1.0]    // Gold
color_secondary: [0.2, 0.5, 0.3, 1.0]  // Forest green

// Particles
gravity: 9.8
damping: 0.1
emit_rate: 100  // particles/sec
default_life: 2.0  // seconds
```

---

## SpacetimeDB Game Integration

### Tables (tuath-game module)

| Category | Tables | Purpose |
|----------|--------|---------|
| Player | Player, EntityPosition | Identity, spatial tracking |
| Inventory | InventoryItem, PendingMint | Items, blockchain sync |
| Clans | Clan, ClanProposal, ClanVote | Governance, treasury |
| Quests | Quest, PlayerQuest | Templates, progress |
| NPCs | Npc, NpcDialogueState, VocabularyProgress | Dialogue, language learning |
| Zones | ZonePresence | Real-time zone tracking |

### Reducers (25 total)

```rust
// Player
create_player(), link_wallet(), update_position()

// Inventory
request_item_mint(), confirm_mint(), create_item()

// Quests
start_quest(), complete_objective(), complete_quest(), abandon_quest()

// Clans
create_proposal(), cast_vote(), execute_proposal()

// Zones
enter_zone(), leave_zone(), zone_heartbeat()

// NPCs
interact_with_npc(), select_dialogue_option()
learn_vocabulary(), review_vocabulary()
```

---

## Game Zones

| Zone ID | Region | Language | Description |
|---------|--------|----------|-------------|
| Connemara | Ireland | Irish | Rocky coastline, bog lands |
| Donegal | Ireland | Irish (Ulster) | Cliffs, fishing villages |
| Kerry | Ireland | Irish (Munster) | Mountains, ring forts |
| ClearIsland | Ireland | Irish | Remote island community |
| AranIslands | Ireland | Irish | Stone walls, prehistoric forts |
| SkyeIsland | Scotland | Scottish Gaelic | Dramatic landscapes |
| Highlands | Scotland | Scottish Gaelic | Glens, lochs |
| OuterHebrides | Scotland | Scottish Gaelic | Remote islands |
| Dyfed | Wales | Welsh | Pembrokeshire coast |
| Gwynedd | Wales | Welsh | Snowdonia mountains |
| Anglesey | Wales | Welsh | Druid island |
| TirNaNog | Mythological | - | Land of eternal youth |
| TechDuinn | Mythological | - | House of the dead |
| MagMell | Mythological | - | Plain of delight |
| Annwn | Mythological | Welsh | Celtic otherworld |

---

## Related Catalogs

- **ML Models:** `meaisínfhoghlaim/catalog/models.yaml`
- **Data Sources:** `meaisínfhoghlaim/catalog/sources.yaml`
- **Skills:** `.claude/skills/` (63 skills)
- **Infrastructure:** `bonneagar/` (37+ stacks)

---

## Quick Links

### Guides
- [WGPU Guide](docs/WGPU_GUIDE.md) - WebGPU rendering
- [Godot Rust Guide](docs/GODOT_RUST_GUIDE.md) - GDExtension development
- [SpacetimeDB Guide](docs/SPACETIMEDB_GUIDE.md) - Multiplayer backend
- [Cross-Platform Guide](docs/CROSS_PLATFORM_GUIDE.md) - Multi-platform development

### Research
- [Anam Particle System](Game%20Particle%20Effects%20Research(2).md) - Weather-driven particles
- [Geospatial Workflow](Geospatial%20Workflow%20%26%20Particle%20Effects(1).md) - Cloud-native OLAP

### Code
- [Celtic Shaders](../../crates/wgpu/celtic-shaders/) - WGSL shader library
- [Godot Client](../../game/godot-client/) - Desktop game
- [Web Client](../../sruth/tuath/game/client/) - Babylon.js browser client
