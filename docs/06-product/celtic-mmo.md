---
domain: product
title: Celtic MMO Design
description: Consolidated Celtic MMO architecture, SpacetimeDB multi-player backend, Anam/Anam Cara system, mythology framework, world map design, and game architecture.
supersedes:
  - docs/tuatha/celtic_mmo.md
  - docs/tuatha/repo-SpacetimeDB.md
  - docs/tuatha/repo-spacetimedb-cookbook.md
  - docs/tuatha/repo-spacetimedb-typescript-sdk.md
  - docs/tuatha/repo-hophacks-spacetimedb-workshop.md
  - docs/tuatha/SpacetimeDB.md
  - docs/tuatha/SPACETIMEDB_GUIDE.md
  - docs/tuatha/Rust Client.md
  - docs/tuatha/game-design-README.md
  - docs/tuatha/game_CONTRIBUTING.md
  - docs/tuatha/mythology-framework.md
  - docs/tuatha/world-map.md
  - docs/tuatha/Celtic MMO Web3 Concept Integration.md
  - docs/tuatha/SpacetimeDB Ogham Stone Game Integration.md
  - docs/tuatha/Ogham Crypto MMO Research.md
  - docs/tuatha/Spacetimedb Blockchain Integration Strategy.md
  - docs/tuatha/MMO Geospatial Data & Visual RAG.md
  - docs/tuatha/British Isles Mythology MMO Research.md
  - docs/tuatha/British Isles Education Map.md
  - docs/tuatha/Celtic Etymology for Game Names.md
  - docs/tuatha/The Expulsion of the Déisi - Wikipedia.md
  - docs/tuatha/Interactive Map & AI Agents.md
  - docs/tuatha/Celtic Language Data Aggregation & Analysis.md
  - docs/tuatha/repo-ireland.md
cognee_entities:
  - entity: TúathaCelticMMO
    type: MMORPG
    relationships:
      - powers: SpacetimeDB
      - renders_with: Godot
      - renders_with: BabylonJS
      - integrates: OghamStoneSystem
      - integrates: CelticMythology
  - entity: SpacetimeDB
    type: GameDatabase
    relationships:
      - stores: GameState
      - syncs: PlayerPositions
      - processes: Reducers
ccc_query_hints:
  - "SpacetimeDB reducer subscription"
  - "Celtic MMO zone design"
  - "Ogham stone game integration"
  - "mythology NPC framework"
  - "British Isles world map"
updated: 2026-06-06
---

# Celtic MMO Design

The Túatha Celtic MMO is a real-time multiplayer educational game traversing the mythology, language, and geography of the Celtic nations. This document consolidates all game architecture, SpacetimeDB backend design, mythology framework, and world map planning.

## 1. Core Concept

Túatha (Irish: "tribes" or "peoples") is a **Learn-to-Earn educational MMO** where players explore a fantasy version of the British Isles, learning Celtic languages, mythology, and culture through quests, challenges, and social interaction.

### Core Game Loop
1. **Explore**: Navigate a real-world geographic map overlaid with Celtic mythology zones
2. **Learn**: Complete language, history, and culture challenges at Knowledge Nodes
3. **Earn**: Gain "Soul XP" and Tuath utility tokens for demonstrated competence
4. **Progress**: Unlock new zones, abilities, and NPC relationships
5. **Connect**: Form Anam Cara (soul friend) bonds for cooperative learning

## 2. SpacetimeDB: Real-Time Game Backend

SpacetimeDB (24.7k GitHub stars) is a relational database with embedded application logic. Game modules written in Rust run directly inside the database, serving as the entire multiplayer backend — the same architecture used by BitCraft Online MMORPG.

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Modules** | Application logic running inside the database as stored procedures (Rust WASM) |
| **Tables** | Define game state schema with automatic indexing |
| **Reducers** | Type-safe functions called by clients that modify database state |
| **Subscriptions** | Real-time SQL queries that push updates to connected clients via WebSocket |
| **Identity** | Built-in authentication with WebSocket connection tokens |

### Game State Schema

```rust
use spacetimedb::{spacetimedb, ReducerContext, Identity, Timestamp};

#[spacetimedb(table)]
pub struct Player {
    #[primarykey]
    pub id: u64,
    #[unique]
    pub identity: Identity,
    pub name: String,
    pub position_x: f32,
    pub position_y: f32,
    pub position_z: f32,
    pub rotation_y: f32,
    pub zone_id: String,
    pub sub_region: String,
    pub xp: u32,
    pub level: u16,
    pub created_at: Timestamp,
    pub updated_at: Timestamp,
}

#[spacetimedb(table)]
pub struct Zone {
    #[primarykey]
    pub id: String,
    pub name: String,
    pub mythos: String,        // "Ulster", "Mabinogion", etc.
    pub language_focus: String, // "ga", "cy", "gd"
    pub required_level: u16,
    pub center_lat: f64,
    pub center_lng: f64,
    pub radius_km: f32,
}

#[spacetimedb(table)]
pub struct KnowledgeNode {
    #[primarykey]
    pub id: u64,
    pub zone_id: String,
    pub node_type: NodeType,    // LanguageQuiz, MythQuest, CultureChallenge
    pub topic: String,
    pub difficulty: u16,
    pub reward_xp: u32,
    pub reward_tuath: u64,      // Token reward
}
```

### Reducer Pattern (Server Logic)

```rust
#[spacetimedb(reducer)]
pub fn move_player(
    ctx: &ReducerContext,
    x: f32, y: f32, z: f32,
    rotation: f32,
) -> Result<(), String> {
    let player_id = ctx.sender;
    let player = ctx.db.player().identity().find(player_id)
        .ok_or("Player not found")?;

    // Validate movement (anti-cheat bounds check)
    if (x - player.position_x).abs() > 10.0 {
        return Err("Movement too far".into());
    }

    ctx.db.player().identity().update(player_id, Player {
        position_x: x,
        position_y: y,
        position_z: z,
        rotation_y: rotation,
        ..player
    });
    Ok(())
}

#[spacetimedb(reducer)]
pub fn complete_node(ctx: &ReducerContext, node_id: u64) -> Result<(), String> {
    // Verify player is near the node
    // Check prerequisites
    // Award XP and tokens
    // Unlock next nodes in zone
    Ok(())
}
```

### Subscriptions (Real-Time Sync)

```typescript
// Client subscribes to zone players
const sub = connection.subscriptionBuilder()
  .on("SELECT * FROM Player WHERE zone_id = ?", ["ulster_001"])
  .subscribe((players) => {
    // Auto-updates when any player in the zone moves
    updatePlayerPositions(players)
  })

// Subscribe to chat in zone
const chatSub = connection.subscriptionBuilder()
  .on("SELECT * FROM ChatMessage WHERE zone_id = ? ORDER BY id DESC LIMIT 50", ["ulster_001"])
  .subscribe((messages) => {
    displayMessages(messages)
  })
```

### Quick Start

```bash
# Install CLI
curl -sSf https://spacetimedb.com/install | sh

# Create module
spacetime init tuath-game --lang rust

# Publish to cloud
spacetime publish tuath-game

# TypeScript client
npm install @clockworklabs/spacetimedb-sdk
```

## 3. Anam Cara System (Soul Bonds)

The Anam Cara (soul friend) mechanic is a core social feature inspired by Celtic tradition.

### Mechanics
- **Bond Formation**: Two players complete a cooperative quest to form a bond
- **Shared XP**: Bonus XP when Anam Cara play within proximity
- **Chat Privileges**: Private whispers and group channels
- **Quest Sharing**: Bonded players can share quest progress
- **Reinforcement**: Bonds strengthen over time with activity

### Data Model
```rust
#[spacetimedb(table)]
pub struct AnamCaraBond {
    pub player_a: Identity,
    pub player_b: Identity,
    pub bond_level: u16,         // 1-10
    pub shared_xp: u64,
    pub formed_at: Timestamp,
    pub last_interaction: Timestamp,
}
```

## 4. Mythology Framework

The game world is organized around the four major Celtic mythological traditions.

### Mythological Cycles

| Cycle | Region | Key Figures | Game Zones |
|-------|--------|-------------|------------|
| **Mythological Cycle** | Ireland | Tuatha Dé Danann, Dagda, Lugh | Brú na Bóinne, Tara, Moytura |
| **Ulster Cycle** | Ulster/N Ireland | Cú Chulainn, Queen Medb, Ferdia | Emain Macha, Cooley Peninsula |
| **Fenian Cycle** | Ireland/Scotland | Fionn Mac Cumhaill, Oisín, Diarmuid | Hill of Allen, River Boyne |
| **Mabinogion** | Wales | Pryderi, Branwen, Rhiannon | Dyfed, Gwynedd, Annwn |

### NPC Framework

```python
# NPC archetypes for Celtic mythology agents
class CelticNPC:
    archetype: str       # "mentor", "challenger", "guide", "trickster"
    cycle: str           # Mythological cycle affiliation
    domain: list[str]    # Skills/areas taught (grammar, history, combat)
    dialogue_tree: dict  # Branching conversation with curriculum hooks
    quest_chain: list    # Progressive quests unlocking knowledge

# Example: Scáthach (Ulster Cycle — combat mentor)
scathach = CelticNPC(
    archetype="mentor",
    cycle="ulster",
    domain=["combat_arts", "ancient_irish", "warrior_code"],
    location="Isle of Skye",
)
```

### Ogham Stone System

Ogham stones are collectible artifacts scattered across the game world:

- **Discovery**: Found in zones through exploration
- **Deciphering**: Players learn Ogham script through mini-games
- **Rewards**: Deciphered stones grant lore, XP, and Tuath tokens
- **Collection**: Completing stone sets unlocks achievements and special zones

## 5. World Map

### Geographic Scope

The game map overlays the real British Isles with mythological regions:

| Region | Real-World Area | Mythological Overlay |
|--------|----------------|---------------------|
| **Éire** | Ireland | Tuatha Dé Danann territories |
| **Alba** | Scotland | Fenian hunting grounds, Skye |
| **Cymru** | Wales | Mabinogion kingdoms |
| **Kernow** | Cornwall | Arthurian remnants |
| **Breizh** | Brittany | Continental Celtic lore |
| **Ellan Vannin** | Isle of Man | Manx mythology |

### Zone Design Principles

1. **Proficiency-Gated**: Higher-level zones require language proficiency
2. **Weather-Linked**: Real Met Éireann/BBC weather data affects zone conditions
3. **Cultural Accuracy**: Each zone reflects authentic landscape and heritage
4. **Dynamic Events**: Timed challenges based on Celtic festival calendar (Samhain, Beltane, etc.)

### Adding New Zones

```rust
// Register zone in SpacetimeDB
fn add_zone(ctx: &ReducerContext, config: ZoneConfig) {
    ctx.db.zone().insert(Zone {
        id: config.id,
        name: config.name,
        mythos: config.mythos,
        language_focus: config.language,
        required_level: config.min_level,
        center_lat: config.lat,
        center_lng: config.lng,
        radius_km: config.radius,
    });

    // Seed knowledge nodes
    for node in config.nodes {
        ctx.db.knowledge_node().insert(node);
    }
}
```

## 6. Multi-Agent AI System

The game uses a multi-agent architecture built on Google ADK:

```
                    ┌─────────────────┐
                    │   Root Agent    │
                    │  (Orchestrator) │
                    └────────┬────────┘
         ┌───────────────────┼───────────────────┐
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│  Celtic Tutor   │ │   Mythology     │ │  Quest Guide    │
│     Agent       │ │   Narrator      │ │     Agent       │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         └───────────────────┼───────────────────┘
                    ┌────────▼────────┐
                    │   Tools         │
                    │(curriculum,     │
                    │ mythology,      │
                    │ translation)    │
                    └─────────────────┘
```

### Agent Specializations

| Agent | Role | Tools |
|-------|------|-------|
| **Celtic Tutor** | Language learning | Grammar check, vocab quiz, pronunciation feedback |
| **Mythology Narrator** | Lore and stories | Story database, character profiles, cultural context |
| **Quest Guide** | In-game assistance | Quest progress, location hints, reward tracking |
| **Research Assistant** | Deep exploration | Curriculum mapping, etymology, academic references |

### Supported Languages
- Irish (Gaeilge) — ga
- Welsh (Cymraeg) — cy
- Scottish Gaelic (Gàidhlig) — gd

## 7. Geospatial Integration

### Data Sources
- Met Éireann (Irish weather data)
- BBC Weather (UK weather data)
- OSI/OS UK (Ordnance Survey geographic data)
- ireland geospatial boundaries library

### Visual RAG
- DuckDB for cloud-native OLAP over geospatial data
- DuckDB Spatial extension for geometric operations
- H3 hexagonal grid indexing for zone partitioning
- LanceDB for vector search over terrain features

## 8. Performance & Scaling

### SpacetimeDB Scaling
- Horizontal scaling for multiplayer zones
- Module-level isolation (one module per game region)
- Automatic client code generation for TypeScript, Rust, C#

### Client Optimization
- Godot 4 for native desktop performance
- Babylon.js with WebGPU for browser
- React Native + embedded Godot view for mobile
- Level-of-detail streaming for large zones
