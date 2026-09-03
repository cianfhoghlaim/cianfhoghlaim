# `sruth/oideachais/agents/agno/` — Agno Team-Based Agent Surface

**Last updated:** 2026-06-16

Agno (formerly PhiData) team-based agents. Parallel to the Google ADK agent surface in `sruth/oideachais/agents/adk/`.

## Agents

### Top-level teams

- `education_team.py` — 6-agent education team (the canonical entry point).

### Sub-teams

`sruth/oideachais/agents/agno/stage_teams/`:

- **Aistear team** — Aistear (early childhood) specialist agents.
- **Primary team** — Primary curriculum agents.
- **Junior Cycle team** — Junior Cycle curriculum agents.
- **Senior Cycle team** — Senior Cycle curriculum agents.
- **Tertiary team** — CAO + QQI-FET + Apprenticeship agents.
- **Shared sub-agents** (`_shared/`) — common agents reused across teams (CurriculumScout, TranslationAgent, CogneeGraphQuery, SourceCiter).

## Integrations

- **Agno** — `agno.Team` instances with stage-specific sub-agents.
- **BAML** — typed extraction via `sruth/oideachais/agents/baml_integration.py` (the canonical adapter).
- **Pydantic gateway** — `sruth/oideachais/agents/pydantic_gateway.py` (LLM routing).
- **LiteLLM** — same gateway as ADK.

## Cross-references

- `sruth/oideachais/agents/adk/` — the Google ADK agent surface.
- `docs/00-core/PROJECT_SPEC.md` — agent architecture.
