# Agno — Multi-Agent Orchestration Framework

## Overview

Agno (formerly PhiData) is an open-source Python framework for building AI agent systems. It provides agent teams, tool-calling agents, knowledge bases, and agent memory — enabling complex multi-agent workflows with tool integration and persistent state. Supports multiple LLM backends through a unified interface.

## Why This Matters for Kings' College Galway

The project's agent architecture uses Agno for coordinating specialized agents: a curriculum agent that understands Irish education policy, a mathematics agent that validates prerequisite chains, an Irish-language agent that ensures bilingual content quality, and a study asset agent that generates educational images. Agno's knowledge base integration means each agent has access to the relevant documentation corpus (curriculum specs, teaching methodology, language references) via vector search, and the memory system retains context across multi-step extraction workflows.

## Key Features

- **Agent teams** — Coordinate multiple specialist agents
- **Tool calling** — Agents can invoke external APIs and functions
- **Knowledge bases** — Vector-search-powered document retrieval per agent
- **Agent memory** — Persistent state across sessions
- **Multi-model** — Support for OpenAI, Anthropic, Google, and local models

## Installation

```bash
uv add agno
```

## Integration with Our Stack

Agno agents are defined as Python classes with tool integrations. They call through the LiteLLM gateway for LLM access and use LanceDB/Qdrant for knowledge base retrieval. The `.agents/skills/agno/` skill definition documents the project's Agno patterns.

## Upstream

- **Repository**: <https://github.com/agno-agi/agno>
- **Documentation**: <https://docs.agno.com>
- **Latest**: v2.0+ (2025) — AgentOS, stateless execution, full async knowledge base, unified media

## Screenshot

Agno is a programmatic framework. Agent interactions are visible in the terminal or Langfuse trace view. The knowledge base integration provides a retrieval interface showing relevant document chunks for agent queries. Agent state is persisted in a database backend (PostgreSQL) for session continuity.
