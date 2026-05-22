# Tuath API Reference

Complete API documentation for the Celtic Educational MMO backend.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.tuath.cianfhoghlaim.dev`

## Authentication

### SIWE (Sign-In With Ethereum)

All authenticated endpoints require a JWT token obtained via SIWE.

#### 1. Get Nonce

```http
GET /auth/nonce
```

Response:
```json
{
  "nonce": "abc123xyz..."
}
```

#### 2. Sign In

```http
POST /auth/siwe
Content-Type: application/json

{
  "message": "tuath.cianfhoghlaim.dev wants you to sign in...",
  "signature": "0x..."
}
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "address": "0x1234...",
  "expires_at": "2025-01-27T12:00:00Z"
}
```

#### 3. Use Token

Include in all subsequent requests:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

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

## Game State Endpoints

### Get Player State

```http
GET /game/state
Authorization: Bearer {token}
```

Response:
```json
{
  "player_id": "0x1234...",
  "character": {
    "name": "Fionn",
    "class": "fianna",
    "level": 12,
    "xp": 4500
  },
  "location": {
    "region": "connemara",
    "zone": "teach_an_draoi"
  },
  "quests": {
    "active": ["quest_001", "quest_002"],
    "completed": 45
  },
  "skills": {
    "irish_reading": 3,
    "irish_speaking": 2,
    "mythology_knowledge": 4
  }
}
```

### Update Progress

```http
POST /game/progress
Authorization: Bearer {token}
Content-Type: application/json

{
  "action": "complete_lesson",
  "lesson_id": "ncca-irish-vocab-001",
  "score": 85,
  "time_spent_seconds": 300
}
```

Response:
```json
{
  "xp_earned": 50,
  "skills_updated": {
    "irish_reading": {"old": 3, "new": 3, "progress": 0.15}
  },
  "achievements_unlocked": [],
  "quests_progressed": ["quest_001"]
}
```

---

## Hybrid Search Endpoints

### Vector + Graph Search

```http
POST /search/hybrid
Content-Type: application/json

{
  "query": "Cú Chulainn's training with Scáthach",
  "search_type": "hybrid",
  "vector_weight": 0.6,
  "graph_weight": 0.4,
  "include_graph_context": true,
  "limit": 10
}
```

Response:
```json
{
  "results": [
    {
      "id": "myth-cu-chulainn-training",
      "content": "Cú Chulainn traveled to Alba...",
      "score": 0.89,
      "source": "mythology",
      "graph_context": {
        "related_characters": ["scathach", "aife"],
        "locations": ["dun_scaithach"],
        "timeline": "ulster_cycle"
      }
    }
  ],
  "graph_insights": [
    {
      "type": "relationship",
      "from": "cu_chulainn",
      "to": "scathach",
      "relationship": "trained_by"
    }
  ]
}
```

---

## Agent Endpoints (AG-UI/CopilotKit)

### Chat with Agent

```http
POST /copilotkit/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Conas a deir mé 'hello' as Gaeilge?"}
  ],
  "stream": true
}
```

Response (SSE stream):
```
data: {"type": "text", "content": "Dia duit! That's how you say 'hello' in Irish..."}
data: {"type": "tool_call", "name": "curriculum_search", "args": {"query": "greetings"}}
data: {"type": "tool_result", "content": "Found 5 greeting expressions..."}
data: {"type": "text", "content": "Here are the common greetings:\n1. Dia duit..."}
data: {"type": "done"}
```

### Get Agent Info

```http
GET /copilotkit/info
```

Response:
```json
{
  "agent": "tuath_agent",
  "sub_agents": [
    "celtic_tutor_agent",
    "mythology_narrator_agent",
    "quest_guide_agent",
    "research_assistant_agent"
  ],
  "tools": [
    "curriculum_search",
    "mythology_query",
    "translation",
    "player_progress",
    "spatial_query"
  ]
}
```

---

## Payments Endpoints (x402)

### Get Pricing

```http
GET /payments/pricing
```

Response:
```json
{
  "services": {
    "chat_message": {
      "price_usd": 0.01,
      "free_daily_limit": 5
    },
    "knowledge_search": {
      "price_usd": 0.02,
      "free_daily_limit": 3
    },
    "premium_quest": {
      "price_usd": 0.05,
      "free_daily_limit": 0
    }
  },
  "accepted_currencies": ["USDC", "ETH"],
  "chains": ["base", "polygon"]
}
```

### Payment Required Response

When free limit exceeded:
```http
HTTP/1.1 402 Payment Required
X-Payment-Required: true
X-Payment-Amount: 0.01
X-Payment-Address: 0x...
X-Payment-Chain: base

{
  "error": "payment_required",
  "service": "chat_message",
  "amount_usd": 0.01,
  "payment_options": [
    {"chain": "base", "currency": "USDC", "address": "0x..."}
  ]
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {}
}
```

Common error codes:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `unauthorized` | 401 | Missing or invalid token |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `payment_required` | 402 | Free limit exceeded |
| `rate_limited` | 429 | Too many requests |
| `validation_error` | 422 | Invalid request body |

---

## Rate Limits

| Endpoint | Authenticated | Anonymous |
|----------|---------------|-----------|
| `/auth/*` | - | 10/min |
| `/curriculum/*` | 100/min | 20/min |
| `/mythology/*` | 100/min | 20/min |
| `/search/*` | 60/min | 10/min |
| `/copilotkit/*` | 30/min | 5/min |
| `/game/*` | 120/min | - |

---

## OpenAPI Schema

Full OpenAPI 3.1 schema available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- JSON: `/openapi.json`

---

## Related Documentation

- [API Reference (Detailed)](./api/README.md) - Comprehensive endpoint documentation
- [Architecture](./ARCHITECTURE.md) - System design overview
- [Frontend Integration](./FRONTEND.md) - TanStack Start hooks for API access
- [Agent Endpoints](./AGENTS.md) - Multi-agent system details
- [Deployment](./DEPLOYMENT.md) - Production deployment guide
