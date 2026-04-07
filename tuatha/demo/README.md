# Tuath Demo

Standalone demonstration of the Celtic Educational MMO platform.

## Quick Start

```bash
cd sruth/tuath
python demo/run_demo.py
```

## What This Demo Demonstrates

### 1. SIWE Authentication
- Sign In With Ethereum
- Wallet connection
- Session management

### 2. Hybrid Search
- Vector search (LanceDB)
- Graph search (Neo4j)
- Combined semantic + structural queries

### 3. Celtic Content
- Irish mythology (Ulster Cycle, Fenian Cycle)
- Welsh mythology (Mabinogi)
- Curriculum integration
- Multilingual support (Irish, Welsh, Scottish Gaelic)

### 4. Knowledge Graph
- Character relationships
- Mythological cycles
- Geospatial regions (Ireland, Wales, Scotland)
- Quest progression

### 5. CopilotKit Agent
- Interactive storytelling
- Quest generation
- Language learning assistance

### 6. Game Mechanics
- Celtic nations & regions
- Character classes (warrior, bard, druid)
- Quest system
- x402 micropayments

## Requirements

This demo requires the FastAPI server running:

```bash
cd sruth/tuath
uv run uvicorn tuath.api.main:app --port 8000 --reload
```

Then run the demo:

```bash
python demo/run_demo.py
```

## Demo Structure

```
demo/
├── __init__.py
├── run_demo.py       # Main demo script
└── README.md         # This file
```

## Running the Demo

The demo expects the API server at `http://localhost:8000`.

```bash
# Terminal 1: Start API server
cd sruth/tuath
uv run uvicorn tuath.api.main:app --port 8000 --reload

# Terminal 2: Run demo
python demo/run_demo.py
```

The demo will showcase:
- Health checks and API overview
- Hybrid search (curriculum + mythology)
- Curriculum search by nation/subject
- Mythology search by cycle
- Search suggestions
- Agent interaction
- Game mechanics (nations, regions, cycles)
- Payment configuration

## Full Platform Setup

To run the complete platform:

```bash
# Install dependencies
cd sruth/tuath
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run API server
uv run uvicorn tuath.api.main:app --port 8000 --reload

# Start Dagster (another terminal)
dagster dev -m tuath.dagster_assets

# Run tests
uv run pytest tests/ -v
```

## API Endpoints

When the server is running:

**Search**
- `POST /search/` - Hybrid search
- `GET /search/curriculum` - Curriculum search
- `GET /search/mythology` - Mythology search
- `GET /search/suggest` - Search suggestions

**Agent**
- `GET /copilotkit/agents` - List agents
- `POST /copilotkit/chat` - Chat with agent (SSE)

**Game**
- `GET /game/nations` - List Celtic nations
- `GET /game/regions` - List regions by nation
- `POST /game/quest/start` - Start quest

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              TUATH - Celtic Educational MMO                   │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Curriculum  │      │ Mythology   │      │ Hybrid      │
│ Data        │      │ Data        │      │ Search      │
│             │      │             │      │             │
│ • Irish     │      │ • Ulster    │      │ • Vector    │
│ • Welsh     │      │ • Fenian    │      │ • Graph     │
│ • Scottish  │      │ • Mabinogi  │      │ • Keyword   │
└─────────────┘      └─────────────┘      └─────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Knowledge   │      │ CopilotKit  │      │ Game        │
│ Graph       │      │ Agent       │      │ Mechanics   │
│             │      │             │      │             │
│ • Neo4j     │      │ • Quest     │      │ • Nations   │
│ • Relations │      │ • Story     │      │ • Classes   │
└─────────────┘      └─────────────┘      └─────────────┘
```

## Game World

### Celtic Nations

| Nation | Native Name | Regions |
|--------|-------------|---------|
| Ireland | Éire | Connacht, Munster, Ulster, Leinster |
| Wales | Cymru | Gwynedd, Powys, Dyfed |
| Scotland | Alba | Highlands, Lowlands, Islands |

### Mythology Cycles

**Irish:**
- Mythological Cycle (Tuatha Dé Danann)
- Ulster Cycle (Red Branch Knights)
- Fenian Cycle (Fionn mac Cumhaill)
- Cycles of the Kings (Historical)

**Welsh:**
- Four Branches of the Mabinogi
- Arthurian Tales
- Independent Tales

### Character Classes

- **Warrior** (Gaisced, Teulu)
- **Bard** (File, Bardd)
- **Druid** (Druí, Derwydd)

## Search Capabilities

### Hybrid Search

Combines vector similarity with graph traversal:

```python
response = await client.post("/search/", json={
    "query": "Celtic warriors and heroes",
    "mode": "hybrid",
    "limit": 5,
    "vector_weight": 0.6,
    "graph_weight": 0.4,
    "include_relationships": True
})
```

### Curriculum Search

Filter by nation, level, subject:

```python
response = await client.get("/search/curriculum", params={
    "query": "greetings and introductions",
    "nation": "ireland",
    "level": "junior_cycle",
    "subject": "language",
    "limit": 5
})
```

### Mythology Search

Filter by tradition, cycle, content type:

```python
response = await client.get("/search/mythology", params={
    "query": "hero warrior",
    "tradition": "irish_mythology",
    "cycle": "ulster_cycle",
    "content_type": "character",
    "limit": 5
})
```

## Payment Configuration

x402 micropayment pricing:

| Service | Price | Free Daily |
|---------|-------|------------|
| Chat message | $0.01 | 5 |
| Knowledge search | $0.02 | 3 |
| Premium quest | $0.05 | 0 |
| Analytics | $0.05 | 0 |

## Dagster Assets

| Asset | Description | Schedule |
|-------|-------------|----------|
| `curriculum_documents` | NCCA, SEC documents | daily |
| `mythology_stories` | Dúchas, Celtic texts | daily |
| `embeddings` | BGE-M3 vectors | on change |
| `knowledge_graph` | Neo4j relationships | on change |
| `game_assets` | Unreal/Unity exports | weekly |

## CopilotKit Agent

### Available Agents

- **Root Agent** - Query routing
- **Curriculum Agent** - Learning content
- **Mythology Agent** - Stories and characters
- **Quest Agent** - Game guidance
- **Language Agent** - Translation help

### Example Interaction

```
User: Tell me about Cú Chulainn

Agent: [Streams A2UI events via SSE]
1. lifecycle.start
2. state.snapshot {vocabulary: [], currentQuest: null}
3. tool.call.start {name: 'search_mythology'}
4. render.component {type: 'CharacterCard', props: {...}}
5. message.delta "Cú Chulainn is the great hero of..."
```

## Asset Generation

Game assets exported to multiple engines:

- **Unreal Engine** - `.uasset` files
- **Unity** - `.prefab` files
- **Godot** - `.tscn` files
- **Babylon.js** - JSON models

## Observability

Integrated monitoring:
- **Datadog APM** - API performance
- **Datadog LLMObs** - Agent token usage
- **MLflow** - Experiment tracking
- **Langfuse** - Cost tracking

## Related Projects

- **oideachas** - Education curriculum (shared data)
- **crypteolas** - Knowledge graph patterns
- **códeolas** - Code analysis tools

## Support

For issues or questions:
- Main README: [sruth/tuath/README.md](../README.md)
- Dúchas: https://www.duchas.ie
- Celtic Languages: [.claude/skills/celtic-language-ai](../../../.claude/skills/celtic-language-ai)

## License

MIT
