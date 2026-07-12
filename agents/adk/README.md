# `sruth/oideachais/agents/adk/` — Google ADK Agent Surface

**Last updated:** 2026-06-16

Google Agent Development Kit (ADK) agents. 17 Python modules implementing research + analysis + AG-UI agent teams.

## Agents

### Curriculum agents

- `root_agent.py` — Root orchestrator (delegates to sub-agents).
- `curriculum_agent.py` — NCCA + curriculumonline.ie queries.
- `corpus_agent.py` — Celtic corpus queries.
- `agui_curriculum_agent.py` — AG-UI streaming agent (CopilotKit frontend).
- `mcp_curriculum_agent.py` — MCP-backed curriculum agent.
- `enhanced_orchestrator.py` — Multi-agent orchestration with planning.
- `curriculum_comparison_agent.py` — Cross-nation comparison (England vs Scotland vs Wales vs NI).
- `education_research_agent.py` — Education research queries.
- `statistics_agent.py` — Statistics queries.
- `voice_agent.py` — Voice-enabled agent (Whisper STT + TTS).
- `translation_agent.py` — Celtic language translation agent.
- `geospatial_agent.py` — Geospatial queries.
- `research_agent.py` — Research queries (general).
- `bunchloch_research_agent.py` — Bunchloch research-archive queries (CT511, GA101, Mata, Oideachas).
- `op_sync.py` — OP (operational) state sync.

### Tools

`sruth/oideachais/agents/tools/`:
- `corpus_search.py`, `corpus_tools.py` — Celtic corpus search.
- `curriculum_search.py`, `curriculum_tools.py` — Curriculum search.
- `geospatial_tools.py`, `spatial_query.py` — Geospatial queries.
- `statistics_query.py` — Statistics queries.
- `terminology.py` — Terminology queries.
- `translation_tools.py` — Translation tools.

### Callbacks

`sruth/oideachais/agents/adk/callbacks/`:
- `citation_callbacks.py` — Citation tracking callbacks for academic integrity.

## Integrations

- **Google ADK** — `google.adk.agents.LlmAgent`, `SequentialAgent` (from the Google ADK Python SDK).
- **AG-UI** — CopilotKit front-end streaming via `sruth/oideachais/web/apps/api/src/copilotkit/`.
- **Pydantic** — `BaseModel`, `Field` for response schemas.
- **LiteLLM** — routes LLM calls through `sruth/oideachais/services/litellm/` (the canonical gateway).

## Cross-references

- `sruth/oideachais/agents/agno/` — the Agno team-based agent surface (parallel to ADK).
- `sruth/oideachais/agents/letta_client.py` — Letta (AgentOS) integration.
- `sruth/oideachais/agent_os/` — AgentOS service (FastAPI).
- `sruth/oideachais/dagster_defs/assets/agent_*` — Dagster assets that wrap agent execution.
- `docs/00-core/PROJECT_SPEC.md` — agent + Dagster + DAG architecture.
