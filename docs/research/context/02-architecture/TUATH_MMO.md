# Tuath System Architecture

Comprehensive architecture documentation for the Celtic Educational MMO backend, agents, and game client.

## System Overview

Tuath is a gamified Celtic language learning platform that combines an MMO-style game world with AI-powered educational content. The system integrates:

- **FastAPI Backend** (Python) - REST API with authentication and content serving
- **Axum API** (Rust) - Payment-protected premium endpoints
- **Google ADK Agents** - Multi-agent orchestration for educational support
- **TanStack Start Frontend** - Modern React SSR application
- **Babylon.js Game Client** - 3D browser-based game engine
- **SpacetimeDB Module** - Real-time multiplayer synchronization

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                    │
├────────────────────┬──────────────────────┬─────────────────────────────┤
│   Web Browser      │   Mobile (Future)    │   Desktop (Godot)           │
│   ┌────────────┐   │                      │   ┌────────────┐            │
│   │ TanStack   │   │                      │   │ gdext      │            │
│   │ Start UI   │   │                      │   │ (Rust)     │            │
│   └─────┬──────┘   │                      │   └─────┬──────┘            │
│         │          │                      │         │                   │
│   ┌─────▼──────┐   │                      │         │                   │
│   │ Babylon.js │   │                      │         │                   │
│   │ Game       │◄──┼──────────────────────┼─────────┘                   │
│   └─────┬──────┘   │                      │                             │
└─────────┼──────────┴──────────────────────┴─────────────────────────────┘
          │
          │ WebSocket (SpacetimeDB) + HTTPS (REST APIs)
          │
┌─────────▼───────────────────────────────────────────────────────────────┐
│                          API LAYER                                       │
├─────────────────────────────┬───────────────────────────────────────────┤
│   FastAPI (Python)          │   Axum (Rust)                             │
│   Port: 8000                │   Port: 8080                              │
│   ┌───────────────────────┐ │   ┌───────────────────────────┐           │
│   │ /auth     - SIWE      │ │   │ /premium/*                │           │
│   │ /copilotkit - Agent   │ │   │ x402 Payment Protection   │           │
│   │ /curriculum - Content │ │   │                           │           │
│   │ /mythology  - Lore    │ │   │ - Premium Quests          │           │
│   │ /geospatial - Maps    │ │   │ - Extended AI Chat        │           │
│   │ /game      - State    │ │   │ - Analytics Access        │           │
│   │ /search    - Hybrid   │ │   └───────────────────────────┘           │
│   │ /payments  - x402     │ │                                           │
│   └───────────────────────┘ │                                           │
└─────────────────────────────┴───────────────────────────────────────────┘
          │
          │
┌─────────▼───────────────────────────────────────────────────────────────┐
│                          AGENT LAYER                                     │
│                     Google ADK Multi-Agent System                        │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      Root Agent (Orchestrator)                      │ │
│  │              Gemini 2.0 Flash - Query Routing                       │ │
│  └──────────┬────────────┬────────────┬────────────┬──────────────────┘ │
│             │            │            │            │                     │
│  ┌──────────▼──────────┐ │ ┌──────────▼──────────┐ │                     │
│  │   Celtic Tutor      │ │ │ Mythology Narrator  │ │                     │
│  │   ---------------   │ │ │ ----------------    │ │                     │
│  │   Language learning │ │ │ Celtic lore/stories │ │                     │
│  │   Grammar help      │ │ │ NPC backgrounds     │ │                     │
│  │   Translation       │ │ │ Cultural context    │ │                     │
│  └─────────────────────┘ │ └─────────────────────┘ │                     │
│             │            │            │            │                     │
│  ┌──────────▼──────────┐ │ ┌──────────▼──────────┐ │                     │
│  │   Quest Guide       │ │ │ Research Assistant  │ │                     │
│  │   ---------------   │ │ │ -----------------   │ │                     │
│  │   Quest objectives  │ │ │ Deep research       │ │                     │
│  │   Progress tracking │ │ │ Curriculum links    │ │                     │
│  │   Navigation hints  │ │ │ Historical context  │ │                     │
│  └─────────────────────┘   └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │
┌─────────▼───────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
├────────────────────┬────────────────────┬───────────────────────────────┤
│   LanceDB          │   FalkorDB         │   SpacetimeDB                 │
│   (Vector Store)   │   (Graph Database) │   (Multiplayer State)         │
│   ┌──────────────┐ │   ┌──────────────┐ │   ┌───────────────┐           │
│   │ BGE-M3       │ │   │ Graphiti     │ │   │ Player State  │           │
│   │ Embeddings   │ │   │ Knowledge    │ │   │ Zone Presence │           │
│   │              │ │   │ Graph        │ │   │ Chat/Events   │           │
│   │ - Curriculum │ │   │              │ │   │ Reducers      │           │
│   │ - Mythology  │ │   │ - Entities   │ │   │ Subscriptions │           │
│   │ - Stories    │ │   │ - Relations  │ │   └───────────────┘           │
│   └──────────────┘ │   │ - Temporal   │ │                               │
│                    │   └──────────────┘ │                               │
└────────────────────┴────────────────────┴───────────────────────────────┘
          │
          │
┌─────────▼───────────────────────────────────────────────────────────────┐
│                          PIPELINE LAYER                                  │
│                     Dagster Orchestration                                │
├─────────────────────────────────────────────────────────────────────────┤
│   DLT Sources          CocoIndex Flows        Dagster Assets            │
│   ┌──────────────┐     ┌──────────────┐      ┌──────────────┐           │
│   │ NCCA         │ ──► │ Curriculum   │ ───► │ curriculum_  │           │
│   │ WJEC         │     │ Embeddings   │      │ embeddings   │           │
│   │ SQA          │     └──────────────┘      └──────────────┘           │
│   └──────────────┘     ┌──────────────┐      ┌──────────────┐           │
│   ┌──────────────┐     │ Mythology    │ ───► │ mythology_   │           │
│   │ Celtic       │ ──► │ Embeddings   │      │ content      │           │
│   │ Mythology    │     └──────────────┘      └──────────────┘           │
│   │ Sources      │     ┌──────────────┐      ┌──────────────┐           │
│   └──────────────┘     │ Multilingual │ ───► │ graphiti_    │           │
│   ┌──────────────┐     │ Transforms   │      │ knowledge    │           │
│   │ Geospatial   │     └──────────────┘      └──────────────┘           │
│   │ Data (OSM)   │                                                      │
│   └──────────────┘                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Request Flow: User Query

```
User Query (e.g., "How do I say hello in Irish?")
        │
        ▼
┌───────────────────────────────────────┐
│  TanStack Start Frontend              │
│  - TuathCopilot component             │
│  - CopilotKit hooks                   │
└───────────────┬───────────────────────┘
                │ POST /copilotkit/stream
                ▼
┌───────────────────────────────────────┐
│  FastAPI /copilotkit Endpoint         │
│  - AG-UI protocol handler             │
│  - Streaming SSE response             │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Root Agent (Orchestrator)            │
│  - Analyzes query intent              │
│  - Routes to Celtic Tutor agent       │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│  Celtic Tutor Agent                   │
│  - Uses translation tool              │
│  - Queries curriculum search          │
└───────────────┬───────────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌───────────────┐ ┌───────────────┐
│ LanceDB       │ │ FalkorDB      │
│ Vector Search │ │ Graph Query   │
└───────┬───────┘ └───────┬───────┘
        └───────┬─────────┘
                │ Hybrid Results
                ▼
┌───────────────────────────────────────┐
│  Response Synthesis                   │
│  - Combine search results             │
│  - Format with Celtic/English         │
│  - Stream back to user                │
└───────────────────────────────────────┘
```

### Data Pipeline Flow

```
External Sources
       │
       ▼
┌─────────────────────────────────┐
│  DLT Ingestion                  │
│  - celtic_mythology source      │
│  - curriculum sources (NCCA)    │
│  - geospatial data (OSM)        │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  CocoIndex Transform            │
│  - Text chunking                │
│  - BGE-M3 embedding             │
│  - Multilingual processing      │
└───────────────┬─────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌───────────────┐ ┌───────────────┐
│ LanceDB       │ │ Graphiti      │
│ Vector Index  │ │ Knowledge     │
│               │ │ Graph         │
└───────────────┘ └───────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| REST API | FastAPI (Python 3.11+) | Main API with 8 route modules |
| Premium API | Axum (Rust) | Payment-protected endpoints |
| Authentication | SIWE (Sign-In With Ethereum) | Web3 wallet auth |
| Payments | x402 Protocol | HTTP micropayments |
| Agent Streaming | AG-UI / CopilotKit | Server-sent events |

### Agents

| Component | Technology | Purpose |
|-----------|------------|---------|
| Orchestration | Google ADK | Multi-agent routing |
| LLM | Gemini 2.0 Flash | Fast inference |
| Tools | Custom Python | Search, translation, progress |
| Protocol | AG-UI | Streaming agent messages |

### Databases

| Database | Technology | Purpose |
|----------|------------|---------|
| Vector Store | LanceDB | BGE-M3 embeddings, semantic search |
| Graph Database | FalkorDB | Graphiti knowledge graph |
| Multiplayer State | SpacetimeDB | Real-time game state sync |
| Analytics | DuckDB | OLAP queries (single-threaded) |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | TanStack Start | SSR React framework |
| Game Engine | Babylon.js 7 | WebGPU/WebGL2 3D rendering |
| State | Zustand | Client state management |
| Data Fetching | React Query | Server state caching |
| Styling | Tailwind CSS | Utility-first CSS |

### Data Pipelines

| Component | Technology | Purpose |
|-----------|------------|---------|
| Ingestion | dlt (data load tool) | Source extraction |
| Embedding | CocoIndex | Vector generation |
| Orchestration | Dagster | Pipeline scheduling |
| Transforms | BGE-M3, Celtic NLP | Multilingual processing |

---

## Module Structure

### Python Package (`sruth/tuath/`)

```
sruth/tuath/
├── api/                      # FastAPI application
│   ├── main.py               # App entrypoint, router config
│   ├── ag_ui_protocol.py     # AG-UI streaming handler
│   ├── routes/               # API endpoints
│   │   ├── auth.py           # SIWE authentication
│   │   ├── copilotkit.py     # Agent streaming
│   │   ├── curriculum.py     # Learning content
│   │   ├── mythology.py      # Celtic lore
│   │   ├── geospatial.py     # Map data
│   │   ├── game_state.py     # Player state
│   │   ├── payments.py       # x402 integration
│   │   └── search.py         # Hybrid search
│   └── services/             # Business logic
│       ├── curriculum_service.py
│       ├── mythology_service.py
│       ├── geospatial_service.py
│       ├── game_state_service.py
│       └── player_progress_service.py
│
├── agents/                   # AI Agent System
│   ├── config.py             # Agent configuration
│   ├── orchestrator.py       # Agent routing logic
│   ├── adk/                  # Google ADK agents
│   │   ├── root_agent.py     # Main orchestrator
│   │   ├── celtic_tutor.py   # Language learning
│   │   ├── mythology_narrator.py
│   │   ├── quest_guide.py
│   │   └── research_assistant.py
│   ├── tools/                # Agent tools
│   │   ├── mythology_query.py
│   │   ├── translation.py
│   │   ├── player_progress.py
│   │   ├── spatial_query.py
│   │   └── curriculum_search.py
│   ├── callbacks/            # Streaming callbacks
│   └── mcp_server/           # MCP tool server
│
├── knowledge_graph/          # Search Infrastructure
│   ├── hybrid_search.py      # Vector + Graph fusion
│   └── graphiti/             # FalkorDB integration
│       └── celtic_knowledge.py
│
├── dlt_sources/              # Data Ingestion
│   ├── mythology/
│   │   └── celtic_mythology.py
│   └── geospatial/
│       ├── gaeltacht_boundaries.py
│       ├── welsh_language_areas.py
│       └── gaelic_communities.py
│
├── cocoindex_flows/          # Embedding Generation
│   ├── mythology_embedding.py
│   └── transforms/
│       └── celtic_multilingual.py
│
├── dagster_assets/           # Pipeline Definitions
│   ├── definitions.py        # Asset defs
│   ├── mythology_assets.py
│   ├── embedding_assets.py
│   ├── curriculum_assets.py
│   └── schedules.py
│
├── storage/                  # Database Access
│   └── serial_executor.py    # Thread-safe DB access
│
└── tests/                    # Test Suite
    ├── conftest.py
    ├── test_api_endpoints.py
    ├── test_hybrid_search.py
    └── test_graphiti_integration.py
```

### Rust Package (`sruth/tuath/api-rs/`)

```
api-rs/
├── Cargo.toml
└── src/
    ├── main.rs               # Axum server entry
    ├── lib.rs                # Library exports
    ├── config.rs             # Environment config
    └── routes/
        ├── mod.rs            # Route modules
        ├── free.rs           # Public endpoints
        └── premium.rs        # x402-protected routes
```

### TypeScript Packages

```
ui/                           # TanStack Start Frontend
├── package.json
├── src/
│   ├── routes/               # File-based routing
│   │   ├── index.tsx         # Home page
│   │   ├── game.tsx          # Game viewport
│   │   └── ...
│   ├── components/           # React components
│   ├── hooks/                # Custom hooks
│   └── server/               # Server functions

game/client/                  # Babylon.js Game Client
├── package.json
└── src/
    ├── index.ts              # Main exports
    ├── babylon/              # Engine setup
    │   ├── engine.ts         # WebGPU/WebGL
    │   └── scene-manager.ts  # Zone lifecycle
    ├── entities/             # Game objects
    │   ├── player-controller.ts
    │   └── camera-controller.ts
    ├── scenes/               # Zone implementations
    │   ├── base-zone.ts
    │   ├── gaeltacht.ts
    │   ├── alba.ts
    │   └── cymru.ts
    └── network/              # Multiplayer
        └── spacetime-client.ts
```

---

## Database Schema

### LanceDB Vector Tables

```
curriculum_embeddings
├── id: string              # Unique identifier
├── content: string         # Source text
├── embedding: float[1024]  # BGE-M3 vector
├── subject: string         # irish, welsh, scottish_gaelic
├── level: string           # junior_cycle, leaving_cert, etc.
├── topic: string           # Grammar, vocabulary, etc.
└── metadata: json          # Source-specific data

mythology_embeddings
├── id: string
├── content: string
├── embedding: float[1024]
├── entity_type: string     # character, story, location, artifact
├── tradition: string       # irish, welsh, scottish
├── source: string          # Primary source text
└── related_entities: array # Graph entity links
```

### FalkorDB Graph Schema

```cypher
// Node types
(:Character {
  id, name, name_gaelic, tradition, role, description
})

(:Story {
  id, title, title_gaelic, tradition, period, themes
})

(:Location {
  id, name, name_gaelic, tradition, type, coordinates
})

(:Artifact {
  id, name, name_gaelic, tradition, powers, origin
})

// Relationship types
(:Character)-[:APPEARS_IN]->(:Story)
(:Character)-[:WIELDS]->(:Artifact)
(:Character)-[:RULES]->(:Location)
(:Story)-[:SET_IN]->(:Location)
(:Story)-[:MENTIONS]->(:Artifact)
```

### SpacetimeDB Tables

```rust
#[spacetimedb::table]
pub struct Player {
    #[primary_key]
    pub id: Identity,
    pub name: String,
    pub position: Vector3,
    pub zone_id: String,
    pub level: u32,
    pub xp: u64,
}

#[spacetimedb::table]
pub struct ZonePresence {
    #[primary_key]
    pub id: u64,
    pub player_id: Identity,
    pub zone_id: String,
    pub region_id: String,
    pub entered_at: Timestamp,
}
```

---

## Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │     │   FastAPI   │     │   Session   │
│   (Wallet)  │     │   Backend   │     │   Store     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  GET /auth/nonce  │                   │
       │──────────────────►│                   │
       │                   │   Generate nonce  │
       │                   │──────────────────►│
       │   { nonce }       │                   │
       │◄──────────────────│                   │
       │                   │                   │
       │  Sign message     │                   │
       │  (wallet popup)   │                   │
       │                   │                   │
       │ POST /auth/siwe   │                   │
       │ { message, sig }  │                   │
       │──────────────────►│                   │
       │                   │   Verify sig      │
       │                   │   Create JWT      │
       │                   │──────────────────►│
       │  { token, addr }  │                   │
       │◄──────────────────│                   │
       │                   │                   │
       │  All requests:    │                   │
       │  Authorization:   │                   │
       │  Bearer <token>   │                   │
       │──────────────────►│                   │
```

---

## Payment Integration

The x402 protocol enables HTTP micropayments using the `402 Payment Required` status code:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │  Rust API   │     │ Facilitator │
│             │     │  (Axum)     │     │  (Coinbase) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ GET /premium/quest│                   │
       │──────────────────►│                   │
       │                   │                   │
       │    402 Payment    │                   │
       │    Required       │                   │
       │    X-Payment-*    │                   │
       │◄──────────────────│                   │
       │                   │                   │
       │ Create payment    │                   │
       │ (wallet signs)    │                   │
       │                   │                   │
       │ GET /premium/quest│                   │
       │ X-Payment: <sig>  │                   │
       │──────────────────►│                   │
       │                   │   POST /verify    │
       │                   │──────────────────►│
       │                   │   { valid: true } │
       │                   │◄──────────────────│
       │                   │                   │
       │   200 OK + Data   │                   │
       │◄──────────────────│                   │
       │                   │   POST /settle    │
       │                   │──────────────────►│
```

### Pricing Configuration

```python
PAYMENT_CONFIG = {
    "chat_message": {
        "price_usd": 0.01,
        "free_daily_limit": 5,
    },
    "knowledge_search": {
        "price_usd": 0.02,
        "free_daily_limit": 3,
    },
    "premium_quest": {
        "price_usd": 0.05,
        "free_daily_limit": 0,
    },
}
```

---

## Multiplayer Architecture

SpacetimeDB provides real-time synchronization without a separate game server:

```
┌─────────────────────────────────────────────────────────────┐
│                     SpacetimeDB Cloud                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Tuath Module (Rust WASM)                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │   │
│  │  │   Tables    │  │  Reducers   │  │  Indexes    │   │   │
│  │  │  (State)    │  │ (Mutations) │  │ (Queries)   │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
        ▲                    ▲                    ▲
        │ WebSocket          │ WebSocket          │ WebSocket
        │                    │                    │
┌───────┴────────┐  ┌────────┴───────┐  ┌────────┴────────┐
│   Player 1     │  │   Player 2     │  │   Player 3      │
│  (Babylon.js)  │  │  (Babylon.js)  │  │  (Godot/Rust)   │
└────────────────┘  └────────────────┘  └─────────────────┘
```

### Sync Pattern

1. **Client connects** to SpacetimeDB via WebSocket
2. **Subscribes to queries** for visible zone players
3. **Position updates** sent at 20Hz via reducers
4. **State changes** automatically pushed to all subscribers
5. **Conflict resolution** handled by database

---

## Error Handling

### API Error Response Format

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Story 'tain_bo_cuailnge' not found",
    "details": {
      "resource_type": "mythology_story",
      "resource_id": "tain_bo_cuailnge"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing auth token |
| `PAYMENT_REQUIRED` | 402 | x402 payment needed |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Entity doesn't exist |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Performance Considerations

### Critical Constraints

1. **DuckDB: Single-threaded only**
   - Concurrent access causes segfaults
   - Use `SerialDatabaseExecutor` wrapper

2. **Embedding Batching: Mandatory**
   - Unbatched: ~100s for 1000 texts
   - Batched: ~1s for 1000 texts
   - Minimum batch size: 100

3. **HNSW Index Management**
   - DROP indexes before bulk inserts >50 rows
   - RECREATE after batch complete
   - Provides 20x speedup

### Caching Strategy

| Layer | Technology | TTL |
|-------|------------|-----|
| CDN | Cloudflare | 1 hour (static) |
| API Response | Redis | 5 minutes |
| Vector Search | LanceDB Cache | Session |
| Graph Query | FalkorDB Cache | 1 minute |

---

## Related Documentation

- [API Reference](./API.md) - Complete endpoint documentation
- [Agent System](./AGENTS.md) - Multi-agent architecture details
- [Game Client](./GAME_CLIENT.md) - Babylon.js implementation
- [Frontend](./FRONTEND.md) - TanStack Start application
- [Data Pipelines](./PIPELINES.md) - ETL and embedding flows
- [Deployment](./DEPLOYMENT.md) - Production setup guide
