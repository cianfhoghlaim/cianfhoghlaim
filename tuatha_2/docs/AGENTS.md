# Tuath Agent Architecture

Multi-agent system for Celtic language learning and mythology exploration.

## Architecture Overview

```
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Root Agent    │
                    │  (Orchestrator) │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│  Celtic Tutor   │ │   Mythology     │ │  Quest Guide    │
│     Agent       │ │   Narrator      │ │     Agent       │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │          ┌────────▼────────┐          │
         │          │    Research     │          │
         │          │   Assistant     │          │
         │          └────────┬────────┘          │
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │     Tools       │
                    │ (curriculum,    │
                    │  mythology,     │
                    │  translation)   │
                    └─────────────────┘
```

## Agent Framework

Built on **Google ADK (Agent Developer Kit)** with:
- LlmAgent for agent definitions
- Sub-agent routing for specialization
- Tool integration via function decorators
- AG-UI protocol for streaming responses

## Root Agent

**Location:** `sruth/tuath/agents/adk/root_agent.py`

The orchestrator that routes queries to specialist agents.

### Query Classification

```python
def classify_query(query: str) -> str:
    """Routes to: tutor, mythology, quest, or research."""
```

| Keywords | Agent |
|----------|-------|
| translate, grammar, vocabulary, pronunciation | celtic_tutor |
| story, legend, myth, who is, tell me about | mythology_narrator |
| quest, mission, objective, complete, hint | quest_guide |
| research, history, compare | research_assistant |

### Model Configuration

```python
# From agents/config.py
orchestrator_model = "claude-sonnet-4-20250514"  # Fast routing
specialist_model = "claude-opus-4-20250514"       # Deep expertise
```

## Specialist Agents

### 1. Celtic Tutor Agent

**File:** `agents/adk/celtic_tutor.py`

Handles language learning queries:
- Grammar explanations
- Vocabulary practice
- Translation help
- Pronunciation guidance

**Supported Languages:**
- Irish (Gaeilge) - ga
- Scottish Gaelic (Gàidhlig) - gd
- Welsh (Cymraeg) - cy

**Example Interaction:**
```
User: How do I conjugate "to be" in Irish past tense?
Agent: The verb "bí" (to be) has an irregular past tense...
       - Bhí mé (I was)
       - Bhí tú (you were)
       - Bhí sé/sí (he/she was)
```

### 2. Mythology Narrator Agent

**File:** `agents/adk/mythology_narrator.py`

Expert on Celtic mythology:
- Irish mythology (Tuatha Dé Danann, Fianna cycle)
- Welsh mythology (Mabinogion)
- Scottish legends
- Character backgrounds for NPCs

**Traditions Covered:**
- Tuatha Dé Danann
- Ulster Cycle (Cú Chulainn)
- Fianna Cycle (Fionn Mac Cumhaill)
- Mabinogion (Welsh)
- Scottish hero tales

**Example Interaction:**
```
User: Tell me about Cú Chulainn
Agent: Cú Chulainn (pronounced koo-HUL-in), the Hound of Ulster...
       He was the greatest warrior of the Ulster Cycle...
```

### 3. Quest Guide Agent

**File:** `agents/adk/quest_guide.py`

In-game quest assistance:
- Quest objectives and hints
- Learning outcome tracking
- Progress guidance
- Location navigation

**Quest Types:**
- Language quests (vocabulary, grammar)
- Mythology quests (story exploration)
- Culture quests (traditions, festivals)
- Exploration quests (geographic)

**Example Interaction:**
```
User: I'm stuck on the Fionn quest, where do I go next?
Agent: For "The Salmon of Knowledge" quest, you need to...
       Head to the River Boyne (An Bhóinn) and speak with Finnegas...
```

### 4. Research Assistant Agent

**File:** `agents/adk/research_assistant.py`

Deep research and curriculum connections:
- Historical context
- Curriculum mapping
- Comparative analysis
- Academic citations

**Research Capabilities:**
- Cross-reference curriculum standards
- Historical timeline placement
- Etymology and linguistic evolution
- Cultural practice research

## Tools

### curriculum_search

**File:** `agents/tools/curriculum_search.py`

Searches curriculum content from NCCA, SQA, WJEC.

```python
@tool
def curriculum_search(
    query: str,
    languages: list[str] = ["irish"],
    levels: list[str] = None,
    limit: int = 5
) -> list[CurriculumResult]:
    """Search Celtic curriculum content."""
```

### mythology_query

**File:** `agents/tools/mythology_query.py`

Queries the mythology knowledge graph.

```python
@tool
def mythology_query(
    query: str,
    traditions: list[str] = None,
    entity_types: list[str] = None
) -> MythologyResult:
    """Query Celtic mythology knowledge base."""
```

### translation

**File:** `agents/tools/translation.py`

Translates between Celtic languages and English.

```python
@tool
def translate(
    text: str,
    source_lang: str,
    target_lang: str
) -> TranslationResult:
    """Translate between Celtic languages and English."""
```

Supports:
- Irish (ga) ↔ English (en)
- Welsh (cy) ↔ English (en)
- Scottish Gaelic (gd) ↔ English (en)
- Irish ↔ Welsh (via English pivot)

### player_progress

**File:** `agents/tools/player_progress.py`

Accesses player state for personalized responses.

```python
@tool
def get_player_progress(
    player_id: str
) -> PlayerProgress:
    """Get current player progress and stats."""
```

### spatial_query

**File:** `agents/tools/spatial_query.py`

Queries geospatial data for Celtic regions.

```python
@tool
def spatial_query(
    query: str,
    region_type: str = None,
    near_location: tuple = None
) -> list[GeoResult]:
    """Query Celtic geographic regions."""
```

## AG-UI Protocol Integration

The agents expose an AG-UI (Agent-to-UI) protocol endpoint for streaming responses.

### Endpoint

```
POST /copilotkit/chat
```

### Event Types

| Event | Description |
|-------|-------------|
| `text` | Streaming text response |
| `tool_call` | Agent invoking a tool |
| `tool_result` | Tool execution result |
| `agent_handoff` | Sub-agent delegation |
| `done` | Stream complete |

### Example Stream

```javascript
const response = await fetch('/copilotkit/chat', {
  method: 'POST',
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Teach me Irish greetings' }],
    stream: true
  })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const event = JSON.parse(new TextDecoder().decode(value));
  handleEvent(event);
}
```

## Prompt Engineering Patterns

### Celtic Language Awareness

All agents are instructed to:
1. Use Celtic language when relevant
2. Provide English explanations alongside
3. Include pronunciation guides
4. Note dialect variations (Connacht, Munster, Ulster)

### Curriculum Integration

Responses link to:
- NCCA learning outcomes (Ireland)
- SQA standards (Scotland)
- WJEC specifications (Wales)

### Immersive MMO Context

Agents maintain game world context:
- Reference in-game locations
- Mention NPC characters
- Track player quest progress
- Use appropriate Celtic greetings

## Callbacks

### Citation Callbacks

**File:** `agents/callbacks/citation_callbacks.py`

Tracks sources for all agent responses:

```python
class CitationCallback:
    """Captures curriculum and mythology citations."""

    def on_tool_call(self, tool_name: str, result: Any):
        if hasattr(result, 'source'):
            self.citations.append({
                'source': result.source,
                'id': result.id,
                'relevance': result.score
            })
```

## Testing Agents

### Unit Tests

```bash
uv run pytest tests/test_agents.py -v
```

### Interactive Testing

```python
from tuath.agents.adk.root_agent import app

# Run agent
response = app.run("Conas a deir mé 'thank you' as Gaeilge?")
print(response)
```

### Demo Mode

```bash
uv run python -m tuath.demo.run_demo
```

## Configuration

**File:** `agents/config.py`

```python
class AgentConfig:
    # Model settings
    orchestrator_model: str = "claude-sonnet-4-20250514"
    specialist_model: str = "claude-opus-4-20250514"

    # Tool settings
    curriculum_search_limit: int = 5
    mythology_search_limit: int = 10

    # Language settings
    default_language: str = "irish"
    supported_languages: list = ["irish", "welsh", "scottish_gaelic"]
```

## Adding New Agents

1. Create agent file in `agents/adk/`
2. Define LlmAgent with instruction prompt
3. Register tools from `agents/tools/`
4. Add to root_agent.sub_agents
5. Update classify_query() routing

Example:
```python
from google.adk.agents import LlmAgent
from ..config import config

new_agent = LlmAgent(
    name="new_specialist",
    model=config.specialist_model,
    description="Handles X queries",
    instruction="You are an expert in X...",
    tools=[tool1, tool2],
)
```

---

## Related Documentation

- [Adding Agents Guide](./guides/ADDING_AGENTS.md) - Step-by-step agent creation
- [Adding Tools Guide](./guides/ADDING_TOOLS.md) - Creating custom tools
- [API Reference](./api/README.md) - CopilotKit endpoints
- [Architecture](./ARCHITECTURE.md) - System overview
- [Celtic Languages](./guides/CELTIC_LANGUAGES.md) - Language-specific patterns
