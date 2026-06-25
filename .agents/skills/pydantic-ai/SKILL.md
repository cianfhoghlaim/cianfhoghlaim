---
name: pydantic-ai
description: Pydantic's agent framework — typed agents with Pydantic-validated I/O, the AG-UI protocol integration, the Pydantic AI Gateway (BYOK/managed/cost-limits), Logfire MCP instrumentation, and DBOS durable execution. Use when building agents whose I/O must be Pydantic-validated, wiring AG-UI to CopilotKit, or adding durable execution to a multi-step agent workflow.
---

# Pydantic AI

## When to use this skill

Use when you need to:

- "Build an agent that returns a typed Pydantic model (not a string)"
- "Wire an agent to a CopilotKit UI via the AG-UI protocol"
- "Route LLM calls through a gateway with cost limits and OTel"
- "Instrument an MCP server + client with Pydantic Logfire"
- "Add durable execution (survive process restart) to an agent"

## Overview

Pydantic AI is the agent framework from the Pydantic team. Unlike
LangChain / LlamaIndex, it is **not** a framework — it is a thin
Pythonic layer on top of any LLM SDK, with Pydantic as the only
data-validation primitive. The "AI" stands for "Agent Interface".

The shared model substrate: any Pydantic model can be reused
across the BAML → Pydantic AI → Dagster asset graph → TanStack
Start zod-schema stack. This is the single-source-of-truth
contract.

## Core — typed Agent

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

class CurriculumArea(BaseModel):
    name: str
    strands: list[str]
    learning_outcomes: list[str]

agent = Agent(
    model=OpenAIModel("gpt-4o-mini"),
    output_type=CurriculumArea,
    system_prompt=(
        "You are a curriculum extraction agent. "
        "Extract the curriculum area, its strands, and "
        "the learning outcomes from the NCCA PDF text provided."
    ),
)

result = agent.run_sync("Children should be able to count to 10...")
# result.output is a CurriculumArea, not a string
```

**Conventions:**

- Always declare `output_type=SomePydanticModel` (no free-text
  outputs)
- The model is `pydantic_ai.models.<provider>.<Provider>Model`
  (`OpenAIModel`, `AnthropicModel`, `GeminiModel`, `BedrockModel`,
  `OpenAICompatibleModel` for vLLM/llama.cpp/Ollama)
- `agent.run_sync()` blocks; `agent.run()` is async
- `result.output` is the parsed Pydantic model (not a string)

## AG-UI protocol integration

Pydantic AI ships a built-in AG-UI adapter. AG-UI is the
CopilotKit-authored SSE protocol that bridges any UI
(CopilotKit / custom React) to any agent backend (Pydantic AI,
Agno, Google ADK, BAML).

```bash
uv add 'pydantic-ai-slim[ag-ui]'
# pulls in: ag-ui-protocol, starlette
```

```python
from pydantic_ai import Agent
from pydantic_ai.ui.ag_ui import AGUIAdapter

agent = Agent(...)
app = AGUIAdapter(agent).as_starlette_app()
```

The frontend consumes the SSE stream via the CopilotKit
`Transport` (or any custom SSE client). The protocol is documented
at <https://ag-ui.com/>.

## Pydantic AI Gateway

The Pydantic AI Gateway is a hosted model router that sits
between the agent and the LLM provider. It supports:

- **BYOK or managed** keys (the gateway can hold your OpenAI /
  Anthropic / Google keys, or you bring your own)
- **Cost limits** at the project, user, or key level
  (catches a runaway agent before it costs $10k)
- **Multi-provider** routing (one agent can use GPT-4o for
  reasoning + Gemini for vision + Cohere for embeddings)
- **OTel / Logfire** backend (every call is traced end-to-end)

```python
from pydantic_ai.models.openai import OpenAIModel

# Use the gateway instead of calling OpenAI directly
model = OpenAIModel(
    "gpt-4o",
    base_url="https://gateway.pydantic.dev/v1",
    api_key="<gateway-api-key>",
)
```

**Deployment options:**

- **Cloudflare Enterprise** (with OIDC SSO) — the recommended
  option for KCG production
- **Self-hosted** (AGPL-3.0) — the OSS option; deploy to a
  Pangolin-exposed stack

## Logfire MCP instrumentation

Logfire is the Pydantic-native observability tool. It
auto-instruments the Pydantic AI runtime AND can instrument any
MCP server / client:

```python
import logfire
from mcp.server.fastmcp import FastMCP

logfire.configure(token="<logfire-token>")
logfire.instrument_mcp()  # instruments both client and server

mcp = FastMCP("oideachais-curriculum")
# ... MCP server code ...
```

Then every `mcp.tool()` call is traced in Logfire with the
request, response, and timing. Pair this with the Pydantic AI
agent to get a full trace from the user's UI input to the
agent's LLM call to the MCP tool invocation to the
LanceDB / DuckDB query.

## DBOS durable execution

[DBOS](https://www.dbos.dev/) is a Python-native durable
execution library. Pair it with Pydantic AI to make an agent
workflow survive a process restart (Kubernetes pod reschedule,
slack notification spam, even a `kill -9`):

```bash
pip install dbos pydantic-ai
```

```python
from dbos import DBOS, SetWorkflowID
from pydantic_ai import Agent

dbos = DBOS()
agent = Agent(...)

@dbos.workflow()
def curriculum_extraction_workflow(pdf_id: str):
    # If this function is interrupted, DBOS will re-run it
    # with the same arguments and resume from the last
    # completed step.
    pdf_text = load_pdf(pdf_id)
    result = agent.run_sync(pdf_text)
    save_to_ducklake(pdf_id, result.output)
    return result.output.model_dump()
```

DBOS records every step in Postgres; if the process dies
mid-workflow, the next instance resumes from the last successful
step. Critical for the `oideachais-curriculum-extraction` and
`oideachais-leabharlann-extraction` Dagster jobs that take
30+ minutes for large corpora.

## KCG integration

The Pydantic AI skill sits at the centre of the KCG LLM stack:

```
            ┌──────────────┐
            │  BAML class  │  ← single source of truth
            └──────┬───────┘
                   │ codegen (baml generate)
                   ▼
            ┌──────────────┐
            │  Pydantic    │  ← the runtime model
            │   model      │
            └──────┬───────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   Pydantic AI   Dagster     Convex
   agent         asset graph schema
       │           │           │
       └───────────┴───────────┘
                   │
                   ▼
            TanStack Start
            (zod mirror)
```

The KCG shared models live in `sruth/oideachais/models/` and are
imported by BAML, Pydantic AI, Dagster assets, and Convex
schemas. **Never duplicate a model** — if you change it in
BAML, `baml generate` propagates the change to all consumers.

## AG-UI protocol (round-9 deep dive)

Pydantic AI ships a first-class AG-UI integration. The
`AGUIAdapter` was originally built by Rocket Science and
contributed in collaboration with the Pydantic AI and
CopilotKit teams. Install with:

```bash
uv add 'pydantic-ai-slim[ag-ui]'
# pulls in: ag-ui-protocol, starlette, uvicorn
```

### 3 ways to expose an AG-UI agent

1. **`AGUIAdapter.run_stream()`** — most flexible. Build
   the `RunAgentInput` yourself, then stream AG-UI events.
   Use for non-Starlette frameworks (Django, Flask) or to
   pre/post-process the input/output.
2. **`AGUIAdapter.dispatch_request()`** — class method
   that takes a Starlette `Request` (e.g. from FastAPI)
   and returns a `StreamingResponse` of AG-UI events.
   Per-request `Agent.iter(...)` args (e.g. `deps`) so
   you can vary by authenticated user.
3. **`AGUIApp`** — full ASGI app, mounts under
   `app.mount("/api/agent", app)`. Per-app `Agent.iter(...)`
   args (same for every request, except for the AG-UI
   `state` injection).

```python
from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic_ai import Agent
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.ag_ui import AGUIAdapter

agent = Agent("gateway/openai:gpt-5", instructions="Be fun!")
app = FastAPI()

@app.post("/")
async def run_agent(request: Request) -> Response:
    accept = request.headers.get("accept", SSE_CONTENT_TYPE)
    try:
        run_input = AGUIAdapter.build_run_input(await request.body())
    except ValidationError as e:
        return Response(content=e.json(),
                        media_type="application/json",
                        status_code=422)
    return await AGUIAdapter.dispatch_request(agent, request, deps=...)
```

### KCG use

The KCG stack uses Pydantic AI as the **typed-agent
backend** for CopilotKit frontends. The flow:

1. **BAML** generates a typed Pydantic model (e.g.
   `LeavingCertSubject`)
2. **Pydantic AI** wraps the LLM call with
   `output_type=LeavingCertSubject`
3. **AG-UI** streams the events to the CopilotKit client
4. **Logfire** traces every step (token, tool call, state)
5. **DBOS** makes the workflow durable across restarts

The shared Pydantic model lives in `sruth/oideachais/models/`
and is imported by BAML, Pydantic AI, Dagster assets,
and Convex schemas — never duplicate.

See `references/clippings/ag-ui.md` for the full Pydantic
AI AG-UI documentation clipping.

## Resources

- Pydantic AI docs: <https://ai.pydantic.dev/>
- Pydantic AI Gateway: <https://ai.pydantic.dev/gateway/>
- AG-UI protocol: <https://ag-ui.com/>
- Logfire: <https://logfire.pydantic.dev/>
- DBOS: <https://www.dbos.dev/>
- KCG shared models: `sruth/oideachais/models/`
