# Agno — KCG Summary

## What It Is
Agno (formerly PhiData) is an open-source Python framework for building multi-agent AI systems with tool calling, knowledge bases, and persistent memory. It enables agent teams, sequential/parallel workflows, and hierarchical orchestration.

## Why This Matters for Kings' College Galway
The project uses Agno for coordinating specialized educational agents: curriculum agent (Irish education policy), mathematics agent (prerequisite validation), Irish-language agent (bilingual content quality), and study asset agent (educational image generation). Agno's knowledge base integration gives each agent access to the relevant documentation corpus via vector search.

## Key Patterns
- Agent teams with tool-calling and inter-agent routing
- Knowledge bases backed by LanceDB/Qdrant for domain-specific retrieval
- Persistent agent memory across multi-step extraction workflows
- Multi-model support via the LiteLLM gateway

## Source Files
Full framework docs and source removed (2026-06-05). Available at <https://github.com/agno-agi/agno>. Agent skill definition at `.agents/skills/agno/SKILL.md`.
