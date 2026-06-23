# API Reference Index

Complete API reference for the Tuath Celtic Educational MMO backend.

## Base URLs

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8000` |
| Production (Python) | `https://api.tuath.cianfhoghlaim.dev` |
| Production (Rust) | `https://api.tuath.cianfhoghlaim.dev:8080` |

## API Modules

### Core APIs (FastAPI)

| Module | Prefix | Description | Auth Required |
|--------|--------|-------------|---------------|
| [Authentication](#authentication) | `/auth` | SIWE wallet authentication | No |
| [Agent](#agent-copilotkit) | `/copilotkit` | AI agent streaming (AG-UI) | Optional |
| [Curriculum](#curriculum) | `/curriculum` | Educational content | Optional |
| [Mythology](#mythology) | `/mythology` | Celtic lore and stories | Optional |
| [Search](#hybrid-search) | `/search` | Hybrid vector + graph search | Optional |
| [Geospatial](#geospatial) | `/geospatial` | Map and location data | No |
| [Game State](#game-state) | `/game` | Player progress and state | Yes |
| [Payments](#payments) | `/payments` | x402 micropayments | Yes |

### Premium APIs (Rust/Axum)

| Module | Prefix | Description | Payment Required |
|--------|--------|-------------|------------------|
| Premium Quests | `/premium/quests` | Premium quest content | Yes |
| Extended Chat | `/premium/chat` | Extended AI conversations | Yes |
| Analytics | `/premium/analytics` | Learning analytics | Yes |

---

## Authentication

SIWE (Sign-In With Ethereum) authentication using EIP-4361 standard.

### GET /auth/nonce

Get a nonce for SIWE authentication.

**Response:**
```json
{
  "nonce": "a1b2c3d4e5f6...",
  "expires_at": "2025-01-01T12:10:00Z"
}
```

**Notes:**
- Nonces expire after 10 minutes
- Each nonce can only be used once

### POST /auth/verify

Verify SIWE message signature and create session.

**Request:**
```json
{
  "message": "tuath.cianfhoghlaim.dev wants you to sign in...",
  "signature": "0x..."
}
```

**Response:**
```json
{
  "success": true,
  "address": "0x1234...",
  "session_id": "sess_abc123...",
  "expires_at": "2025-01-02T12:00:00Z",
  "player_id": "player_xyz789...",
  "message": "Welcome to Tuath!"
}
```

### GET /auth/session

Get current session information.

**Headers:**
```
Authorization: Bearer <session_id>
```

**Response:**
```json
{
  "address": "0x1234...",
  "player_id": "player_xyz789...",
  "authenticated": true,
  "expires_at": "2025-01-02T12:00:00Z",
  "free_messages_remaining": 3,
  "free_searches_remaining": 2
}
```

### POST /auth/logout

End the current session.

**Headers:**
```
Authorization: Bearer <session_id>
```

**Response:**
```json
{
  "success": true,
  "message": "Slán! (Goodbye!)"
}
```

---

## Agent (CopilotKit)

AI agent streaming using AG-UI (Agent User Interaction) protocol.

### POST /copilotkit/stream

Stream AI agent response with AG-UI events.

**Request:**
```json
{
  "message": "How do I say hello in Irish?",
  "context": {
    "language": "ga",
    "language_level": "beginner",
    "current_quest": "first_words",
    "current_zone": "gaeltacht"
  }
}
```

**Headers:**
```
X-Session-ID: <session_id>
X-Payment-ID: <payment_id>  (optional)
```

**Response (SSE Stream):**
```
event: lifecycle.start
data: {"run_id": "run_123", "agent": "celtic_tutor"}

event: state.snapshot
data: {"language": "ga", "xp_earned": 0, "vocabulary_learned": []}

event: message.delta
data: {"content": "In Irish, "}

event: message.delta
data: {"content": "hello is \"Dia duit\""}

event: tool.call.start
data: {"tool_id": "t1", "tool_name": "translate", "parameters": {"text": "hello", "from": "en", "to": "ga"}}

event: tool.call.result
data: {"tool_id": "t1", "result": {"translation": "Dia duit", "pronunciation": "DEE-a gwit"}}

event: state.delta
data: {"xp_earned": 10, "vocabulary_learned": ["dia", "duit"]}

event: lifecycle.complete
data: {"run_id": "run_123"}
```

### AG-UI Event Types

| Event | Description |
|-------|-------------|
| `lifecycle.start` | Run started |
| `lifecycle.complete` | Run completed |
| `lifecycle.error` | Error occurred |
| `state.snapshot` | Full state snapshot |
| `state.delta` | State update |
| `message.delta` | Text content chunk |
| `message.complete` | Message finished |
| `tool.call.start` | Tool invocation started |
| `tool.call.result` | Tool returned result |
| `render.component` | Render UI component |

### Available Agents

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `celtic_tutor` | Language learning | Translation, grammar, vocabulary |
| `mythology_narrator` | Celtic stories | Character info, lore, tales |
| `quest_guide` | Quest assistance | Hints, objectives, navigation |
| `research_assistant` | Deep research | Historical context, curriculum links |

---

## Curriculum

Search and retrieve Celtic language curriculum content.

### GET /curriculum/subjects

List available subjects.

**Response:**
```json
{
  "subjects": [
    {
      "id": "irish",
      "name": "Gaeilge",
      "name_en": "Irish",
      "curriculum": "ncca",
      "levels": ["junior_cycle", "leaving_cert"]
    },
    {
      "id": "welsh",
      "name": "Cymraeg",
      "name_en": "Welsh",
      "curriculum": "wjec",
      "levels": ["gcse", "a_level"]
    }
  ]
}
```

### GET /curriculum/search

Search curriculum content using vector search.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query |
| `nation` | string | Filter: ireland, scotland, wales |
| `language` | string | Filter: ga, gd, cy, en |
| `level` | string | Filter: primary, secondary, higher |
| `limit` | int | Max results (1-50, default 10) |

**Response:**
```json
{
  "query": "conditional tense",
  "results": [
    {
      "id": "cur_001",
      "title": "An Modh Coinníollach",
      "content": "The conditional mood in Irish...",
      "nation": "ireland",
      "language": "ga",
      "level": "leaving_cert",
      "subject": "grammar",
      "learning_outcomes": ["LO.GA.5.2", "LO.GA.5.3"],
      "score": 0.92
    }
  ],
  "total": 15,
  "filters": {"nation": null, "language": null}
}
```

### GET /curriculum/{subject}/{level}

Get full curriculum for subject and level.

**Path Parameters:**
- `subject`: irish, welsh, scottish_gaelic
- `level`: junior_cycle, leaving_cert, gcse, a_level, etc.

---

## Mythology

Query Celtic mythology content from the knowledge graph.

### GET /mythology/characters

List mythological characters.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `tradition` | string | Filter: irish, welsh, scottish |
| `role` | string | Filter: god, hero, monster, druid |
| `limit` | int | Max results (1-100) |

**Response:**
```json
{
  "characters": [
    {
      "id": "char_001",
      "name": "Cú Chulainn",
      "celtic_name": "Cú Chulainn",
      "tradition": "irish",
      "role": "hero",
      "description": "The Hound of Ulster, greatest warrior of the Red Branch Knights",
      "appears_in": ["Táin Bó Cúailnge", "Aided Óenfhir Aífe"],
      "related_characters": ["Scáthach", "Emer", "Conchobar mac Nessa"]
    }
  ],
  "total": 42
}
```

### GET /mythology/stories

List mythological stories and cycles.

### GET /mythology/search

Search mythology using hybrid search.

---

## Hybrid Search

Combined vector + graph search across all content.

### POST /search

Perform hybrid search.

**Request:**
```json
{
  "query": "Tuatha Dé Danann origin",
  "mode": "hybrid",
  "content_types": ["mythology", "character"],
  "limit": 20,
  "vector_weight": 0.6,
  "graph_weight": 0.4,
  "include_relationships": true
}
```

**Response:**
```json
{
  "query": "Tuatha Dé Danann origin",
  "mode": "hybrid",
  "total": 15,
  "results": [
    {
      "id": "myth_001",
      "content_type": "mythology",
      "title": "The Arrival of the Tuatha Dé Danann",
      "content": "The Tuatha Dé Danann came from four mythical cities...",
      "score": 0.95,
      "source": "hybrid",
      "metadata": {"tradition": "irish", "cycle": "mythological"},
      "related_entities": ["Nuada", "Dagda", "Lugh"]
    }
  ]
}
```

### Search Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `vector` | Pure semantic similarity | General queries |
| `graph` | Knowledge graph traversal | Relationship queries |
| `hybrid` | Combined with rank fusion | Complex queries |

---

## Geospatial

Geographic and map data for Celtic regions.

### GET /geospatial/gaeltacht

Get Irish Gaeltacht boundaries.

**Response:**
```json
{
  "regions": [
    {
      "id": "gaeltacht_donegal",
      "name": "Gaeltacht Dhún na nGall",
      "name_en": "Donegal Gaeltacht",
      "geometry": { "type": "Polygon", "coordinates": [...] },
      "population": 23000,
      "irish_speakers_pct": 67.5
    }
  ]
}
```

### GET /geospatial/celtic-regions

Get all Celtic language regions.

---

## Game State

Player progress and game state management.

### GET /game/player

Get current player state.

**Headers:** `Authorization: Bearer <session_id>`

**Response:**
```json
{
  "player_id": "player_xyz",
  "name": "Fionn",
  "level": 5,
  "xp": 4500,
  "current_zone": "gaeltacht",
  "current_quest": "first_words",
  "vocabulary_learned": 127,
  "quests_completed": 8,
  "achievements": ["early_bird", "polyglot"]
}
```

### POST /game/progress

Update player progress.

### GET /game/quests

List available quests.

---

## Payments

x402 micropayment integration.

### GET /payments/pricing

Get pricing for all resources.

**Response:**
```json
{
  "resources": {
    "chat_message": {
      "price_usd": 0.01,
      "free_daily_limit": 5,
      "description": "AI chat message"
    },
    "knowledge_search": {
      "price_usd": 0.02,
      "free_daily_limit": 3,
      "description": "Knowledge base search"
    },
    "premium_quest": {
      "price_usd": 0.05,
      "free_daily_limit": 0,
      "description": "Premium quest access"
    }
  },
  "tokens": ["USDC", "ETH"],
  "chain": "base"
}
```

### POST /payments/request/{resource_type}

Request payment for a resource.

**Response:**
```json
{
  "payment_id": "pay_abc123",
  "resource_type": "knowledge_search",
  "price_usd": 0.02,
  "price_crypto": 0.00001,
  "token": "USDC",
  "receiver_address": "0x742d35...",
  "expires_at": "2025-01-01T12:15:00Z"
}
```

### POST /payments/verify

Verify a completed payment.

**Request:**
```json
{
  "payment_id": "pay_abc123",
  "tx_hash": "0x..."
}
```

### 402 Payment Required Response

When payment is needed:

**Response Headers:**
```
X-Payment-Required: true
X-Payment-Amount: 0.02
X-Payment-Token: USDC
X-Payment-Address: 0x742d35...
```

**Response Body:**
```json
{
  "error": "payment_required",
  "resource_type": "knowledge_search",
  "price_usd": 0.02,
  "free_remaining": 0,
  "request_url": "/payments/request/knowledge_search"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_NONCE` | 400 | Nonce expired or already used |
| `INVALID_SIGNATURE` | 400 | SIWE signature verification failed |
| `UNAUTHORIZED` | 401 | Missing or invalid session |
| `PAYMENT_REQUIRED` | 402 | x402 payment needed |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limits

| Endpoint Group | Rate Limit |
|----------------|------------|
| Authentication | 10/minute |
| Agent Streaming | 5/minute (unauthenticated), 60/minute (authenticated) |
| Search | 20/minute |
| Game State | 60/minute |
| Payments | 30/minute |

---

## Related Documentation

- [Architecture Overview](../ANALYSIS.md) - Project analysis
- [Tuath Agent System](../02-agents/Tuath%20Agent%20System.md) - Multi-agent system details
- [Game Client](../01-game-design/GAME_CLIENT.md) - Babylon.js integration
- [Frontend Reference](../04-game-tech/reference/FRONTEND.md) - UI integration patterns

---

# Appendix A: Curriculum Endpoint Reference (legacy detail)

The following section preserves the verbose, nested-resource details for the Curriculum and Mythology endpoints from the older API documentation. Use these as a reference for the full response shape, but prefer the simpler endpoint names in the main body above.

## Curriculum Endpoints

### List Subjects

```http
GET /curriculum/subjects
```

Response:
```json
{
  "subjects": [
    {
      "id": "irish",
      "name": "Gaeilge",
      "name_en": "Irish",
      "curriculum": "ncca",
      "levels": ["junior_cycle", "leaving_cert"]
    },
    {
      "id": "welsh",
      "name": "Cymraeg",
      "name_en": "Welsh",
      "curriculum": "wjec",
      "levels": ["gcse", "a_level"]
    }
  ]
}
```

### Get Curriculum Content

```http
GET /curriculum/{subject}/{level}
```

Parameters:
- `subject`: Subject ID (irish, welsh, scottish_gaelic)
- `level`: Education level (junior_cycle, leaving_cert, gcse, etc.)

Response:
```json
{
  "subject": "irish",
  "level": "leaving_cert",
  "strands": [
    {
      "id": "litriocht",
      "name": "Litríocht",
      "name_en": "Literature",
      "topics": [
        {
          "id": "filíocht",
          "name": "Filíocht",
          "name_en": "Poetry",
          "learning_outcomes": ["LO1", "LO2"]
        }
      ]
    }
  ]
}
```

### Search Curriculum

```http
POST /curriculum/search
Content-Type: application/json

{
  "query": "verb conjugation past tense",
  "languages": ["irish", "welsh"],
  "levels": ["leaving_cert", "a_level"],
  "limit": 10
}
```

Response:
```json
{
  "results": [
    {
      "id": "ncca-irish-lc-gram-001",
      "title": "An Aimsir Chaite",
      "content": "The past tense in Irish...",
      "language": "irish",
      "level": "leaving_cert",
      "relevance_score": 0.92
    }
  ],
  "total": 45,
  "query_time_ms": 125
}
```

---

## Mythology Endpoints

### List Characters

```http
GET /mythology/characters?tradition=irish&limit=20
```

Parameters:
- `tradition`: irish, welsh, scottish (optional)
- `category`: deity, hero, druid, creature (optional)
- `limit`: Max results (default 20)

Response:
```json
{
  "characters": [
    {
      "id": "lugh",
      "name": "Lugh Lámhfhada",
      "name_en": "Lugh of the Long Arm",
      "tradition": "irish",
      "category": "deity",
      "cycle": "tuatha_de_danann",
      "domains": ["light", "skill", "crafts"],
      "description": "Master of all arts, champion of the Tuatha Dé Danann..."
    }
  ]
}
```

### Get Character Details

```http
GET /mythology/characters/{id}
```

Response:
```json
{
  "id": "lugh",
  "name": "Lugh Lámhfhada",
  "tradition": "irish",
  "category": "deity",
  "cycle": "tuatha_de_danann",
  "parents": ["cian", "ethniu"],
  "children": ["cú_chulainn"],
  "stories": [
    {"id": "cath_maige_tuired", "role": "protagonist"}
  ],
  "locations": [
    {"id": "teamhair", "relationship": "rules"}
  ],
  "items": [
    {"id": "slea_bua", "relationship": "wields"}
  ],
  "welsh_equivalent": "lleu_llaw_gyffes"
}
```

### Search Mythology

```http
POST /mythology/search
Content-Type: application/json

{
  "query": "warrior who fought at the ford",
  "traditions": ["irish"],
  "include_stories": true
}
```

---

## Geospatial Endpoints

### Get Celtic Regions

```http
GET /geospatial/regions?type=gaeltacht
```

Parameters:
- `type`: gaeltacht, welsh_language_area, gaidhealtachd

Response (GeoJSON):
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-10.2, 53.1], ...]]
      },
      "properties": {
        "id": "connemara",
        "name": "Conamara",
        "name_en": "Connemara",
        "region_type": "gaeltacht",
        "language": "irish",
        "speaker_percentage": 67.5
      }
    }
  ]
}
```

### Get Region Details

```http
GET /geospatial/regions/{id}
```

### Points of Interest

```http
GET /geospatial/poi?region=connemara&category=heritage
```

---


---

# Appendix B: OpenAPI Schema (legacy reference)

The full OpenAPI 3.1 schema is auto-generated by the FastAPI backend and available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- JSON: `/openapi.json`

This schema is regenerated on every backend deploy; do not hand-edit.
