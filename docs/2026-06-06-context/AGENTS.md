# Pattern: Agent Design

## Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **Root agent routing** | Use LLM router for query classification before specialist dispatch | Incorrect agent handles query, poor responses |
| **Sequential pipelines** | Multi-step tasks require SequentialAgent, not parallel execution | Race conditions, incomplete workflows |
| **Human-in-the-loop** | Destructive operations need approval gates | Unintended side effects, data loss |
| **Session persistence** | Maintain conversation state across interactions | Context loss, repeated questions |
| **Tool confirmation** | Tools with side effects should request confirmation | Accidental modifications |

---

## Code Patterns

### Pattern 1: Root Agent with Specialist Routing

**When to use**: Multi-domain applications where queries need routing to specialized agents.

**Implementation**:
```python
from google.adk.agents import LlmAgent

# Define specialist agents
curriculum_agent = LlmAgent(
    name="curriculum_agent",
    model="gemini-2.0-flash",
    instruction="Answer questions about educational curriculum content.",
    tools=[search_curriculum, get_learning_outcomes],
)

translation_agent = LlmAgent(
    name="translation_agent",
    model="gemini-2.0-flash",
    instruction="Translate content between Celtic languages and English.",
    tools=[translate_text, detect_language],
)

# Root agent routes to specialists
root_agent = LlmAgent(
    name="router",
    model="gemini-2.0-flash",
    instruction="""Route user queries to the appropriate specialist:
    - Curriculum questions → curriculum_agent
    - Translation requests → translation_agent
    - General questions → answer directly""",
    sub_agents=[curriculum_agent, translation_agent],
)
```

### Pattern 2: Sequential Pipeline for Multi-Step Tasks

**When to use**: Complex workflows requiring ordered execution (scraping, extraction, validation).

**Implementation**:
```python
from google.adk.agents import SequentialAgent, LoopAgent

# Step 1: Navigate to target
hunter_agent = LlmAgent(
    name="hunter",
    instruction="Navigate to the specified URL and prepare for interaction.",
    tools=[navigate_to_url, wait_for_element],
)

# Step 2: Perform interactions
operator_agent = LlmAgent(
    name="operator",
    instruction="Perform required interactions (click, fill, scroll).",
    tools=[click_element, fill_form, scroll_page],
)

# Step 3: Extract content
gatherer_agent = LlmAgent(
    name="gatherer",
    instruction="Extract structured content from the current page.",
    tools=[extract_content, capture_screenshot],
)

# Step 4: Validate quality (loop until satisfied)
quality_loop = LoopAgent(
    name="quality_loop",
    max_iterations=2,
    sub_agents=[
        LlmAgent(name="evaluator", instruction="Evaluate extraction quality."),
        LlmAgent(name="escalator", instruction="Escalate to fallback if quality low."),
    ],
)

# Full pipeline
browser_pipeline = SequentialAgent(
    name="browser_pipeline",
    sub_agents=[hunter_agent, operator_agent, gatherer_agent, quality_loop],
)
```

### Pattern 3: Agno Team-Based Agents

**When to use**: Complex research tasks requiring multiple perspectives.

**Implementation**:
```python
from agno import Agent, Team

# Research team with specialized roles
research_agent = Agent(
    name="researcher",
    model="gpt-4o",
    instructions="Deep research on specified topics.",
    tools=[web_search, document_search],
)

analyst_agent = Agent(
    name="analyst",
    model="gpt-4o",
    instructions="Analyze research findings and extract insights.",
    tools=[summarize, extract_entities],
)

writer_agent = Agent(
    name="writer",
    model="gpt-4o",
    instructions="Write clear, structured reports from analysis.",
    tools=[format_markdown, generate_citations],
)

# Team orchestration
research_team = Team(
    agents=[research_agent, analyst_agent, writer_agent],
    workflow="sequential",  # or "parallel", "hierarchical"
)

result = await research_team.run("Research Celtic language NLP models")
```

### Pattern 4: Stagehand Browser Automation

**When to use**: Vision-driven web interaction without CSS selectors.

**Implementation**:
```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({
  env: "LOCAL",  // or "BROWSERBASE" for cloud
  modelName: "claude-sonnet-4-20250514",
});

await stagehand.init();
await stagehand.page.goto("https://example.com");

// Act: Single atomic action
await stagehand.act("click the sign in button");

// Observe: Plan actions before executing
const actions = await stagehand.observe("find the search input");
await stagehand.act(actions[0]);

// Extract: Structured data with Zod schema
const { listings } = await stagehand.extract(
  "extract all product listings",
  z.object({
    listings: z.array(z.object({
      name: z.string(),
      price: z.number(),
      url: z.string(),
    })),
  })
);

// Agent: Multi-step autonomous execution
const result = await stagehand.agent.execute({
  instruction: "Find NVDA stock price and recent news",
  maxSteps: 20,
});
```

### Pattern 5: Human-in-the-Loop Approval

**When to use**: Operations with side effects requiring user confirmation.

**Implementation**:
```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

async def delete_file_with_approval(path: str) -> str:
    """Delete a file after user confirmation."""
    # Request approval (handled by frontend)
    approval = await request_user_approval(
        action="delete_file",
        details={"path": path},
        message=f"Are you sure you want to delete {path}?",
    )

    if approval.approved:
        os.remove(path)
        return f"Deleted {path}"
    else:
        return f"Deletion of {path} was cancelled by user"

agent = LlmAgent(
    name="file_manager",
    tools=[FunctionTool(delete_file_with_approval)],
    instruction="Manage files. Always request confirmation for deletions.",
)
```

### Pattern 6: Durable Execution with Restate/DBOS

**When to use**: Long-running workflows that must survive crashes.

**Implementation**:
```python
from dbos import DBOS

@DBOS.workflow
def deep_research_workflow(query: str) -> dict:
    """Durable research workflow with automatic checkpointing."""

    # Step 1: Search (checkpointed)
    search_results = DBOS.step(search_web)(query)

    # Step 2: Analyze (checkpointed)
    analysis = DBOS.step(analyze_results)(search_results)

    # Step 3: Generate report (checkpointed)
    report = DBOS.step(generate_report)(analysis)

    return report

# If workflow crashes, it resumes from last checkpoint
result = deep_research_workflow("Celtic language preservation")
```

---

## Integration Points

| Connects To | Purpose |
|-------------|---------|
| **CocoIndex** | Agents query vector stores for RAG |
| **BAML** | Type-safe extraction schemas for agent outputs |
| **Dagster** | Schedule agent tasks as Dagster assets |
| **FastAPI** | Expose agents via REST/WebSocket endpoints |
| **AG-UI Protocol** | Stream agent state to frontend |
| **MCP Servers** | Provide tools via Model Context Protocol |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Parallel execution of dependent steps | Use `SequentialAgent` for ordered workflows |
| Missing error handling in tools | Wrap tools with try/except, return error objects |
| No session persistence | Store conversation state in database/cache |
| Hardcoded model names | Use environment variables for model selection |
| No rate limiting | Implement backoff for external API calls |
| Missing tool descriptions | Always provide clear docstrings for tools |
| Blocking I/O in async agents | Use `asyncio` for all I/O operations |

---

## Agent Framework Comparison

| Framework | Best For | Model Support | Key Features |
|-----------|----------|---------------|--------------|
| **Google ADK** | Production deployments | Gemini, LiteLLM | Vertex AI integration, A2A protocol |
| **Agno** | Team-based research | OpenAI, Anthropic | Multi-agent teams, session memory |
| **Stagehand** | Browser automation | Claude, Gemini CUA | Vision-driven, no selectors |
| **Pydantic AI** | Type-safe agents | Any | Strong typing, validation |
| **Smolagents** | Deep research | HuggingFace | Multi-hop reasoning |

---

## References

- Source: `taighde/agents/saoi/`, `taighde/agents/agno/`, `taighde/agents/stagehand/`
- Skills: `.claude/skills/agno/`, `.claude/skills/stagehand/`
- Examples: `sruth/oideachais/agents/adk/`, `sruth/browser/agents/`
