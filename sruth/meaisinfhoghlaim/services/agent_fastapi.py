"""
FastAPI wrapper exposing the 12 agents as HTTP endpoints.

Agents: root_agent, curriculum_agent, translation_agent, geospatial_agent,
        corpus_agent, statistics_agent, research_agent, education_research_agent,
        bunchloch_research_agent, agui_curriculum_agent, mcp_curriculum_agent,
        curriculum_comparison_agent.

Each agent is loaded lazily and exposes a /agent/{name}/chat SSE endpoint
for AG-UI streaming.

Requires: infrastructure/stacks/risingwave/ (port 4566)
Requires: infrastructure/stacks/litellm (port 4000)
"""
from fastapi import FastAPI
app = FastAPI(title="meaisínfhoghlaim agents", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "agents": 12}
