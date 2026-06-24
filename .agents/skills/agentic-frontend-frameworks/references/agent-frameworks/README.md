---
title: "Agent Documentation — Canonical Index"
domain: agents
status: stable
description: "Consolidated canonical index of all agent-related documentation: frameworks, browser automation, BAML extraction, and MCP servers."
supersedes:
  - docs/agents/INDEX.md
entities:
  - AgentFramework
  - BrowserAutomation
  - BAMLSchema
  - MCPServer
related_skills:
  - .agents/skills/agno/SKILL.md
  - .agents/skills/google-adk/SKILL.md
  - .agents/skills/copilotkit/SKILL.md
  - .agents/skills/browser/SKILL.md
  - .agents/skills/firecrawl/SKILL.md
  - .agents/skills/mcp-builder/SKILL.md
  - .agents/skills/dagster/SKILL.md
  - .agents/skills/dignified-python/SKILL.md
ccc_query_hints:
  - "agent framework documentation"
  - "agent orchestration patterns"
  - "browser automation Stagehand"
  - "BAML schema Irish education"
  - "MCP server setup"
last_reviewed: 2026-06-06
truth: partial

---

# Agent Documentation — Canonical Index

This directory contains the consolidated canonical documentation for all agent-related patterns, frameworks, protocols, and tooling used across the Cianfhoghlaim monorepo. 36 source files from `docs/agents/` have been merged into 4 canonical files + this index.

## Canonical Files

| File | Description |
|---|---|
| [agent-frameworks.md](./agent-frameworks.md) | Agno, Google ADK, CopilotKit, Convex, Pydantic AI, durable execution (Restate/DBOS), A2UI, and the Irish Education Platform blueprint |
| [browser-automation.md](./browser-automation.md) | Browserbase, Stagehand V3, Smolagents+Firecrawl deep research, CDP screenshot capture, multi-agent scraping pipelines |
| [baml-extraction.md](./baml-extraction.md) | BAML fundamentals, Irish education schemas (Primary/Junior/Senior Cycle), DuckDB/Dragonfly integration, dynamic TypeBuilder, self-healing pipelines |
| [mcp-servers.md](./mcp-servers.md) | MCP protocol specification, Python/TypeScript SDKs, Claude Code integration, x402 payments, Better Auth, MCP-UI/Gradio/Evidence, security best practices |

## Entity Map

```
AgentFramework ──┬── Agno (AgentOS, A2A, Teams)
                 ├── Google ADK (Sequential, Loop, Parallel, Coordinator)
                 ├── CopilotKit (useCopilotAction, useCoAgent, AG-UI)
                 ├── Convex (Agent component, MCP server)
                 ├── Pydantic AI (AG-UI, Gateway, Logfire)
                 └── DurableExecution (Restate, DBOS)

BrowserAutomation ──┬── Browserbase (CDP, stealth, proxies)
                    ├── Stagehand V3 (act, extract, observe, agent)
                    └── Firecrawl (agent API, MCP tools)

BAMLSchema ──┬── IrishEducation (Primary, Junior Cycle, Senior Cycle)
             ├── DynamicTypeBuilder (runtime schema generation)
             └── SelfHealingPipeline (Cognee → BAML generation)

MCPServer ──┬── Protocol (JSON-RPC 2.0, transports, auth)
            ├── Integrations (Claude, Agno, Dagger, x402)
            └── UI (MCP-UI, Gradio, Evidence, MCP Apps)
```

## Related Skills

| Skill | Covers |
|---|---|
| `.agents/skills/agno/SKILL.md` | Agno agent development |
| `.agents/skills/google-adk/SKILL.md` | Google ADK development |
| `.agents/skills/copilotkit/SKILL.md` | CopilotKit UI integration |
| `.agents/skills/browser/SKILL.md` | Browserbase interactive browsing |
| `.agents/skills/firecrawl/SKILL.md` | Firecrawl scraping and crawling |
| `.agents/skills/mcp-builder/SKILL.md` | MCP server creation |
| `.agents/skills/dagster/SKILL.md` | Dagster orchestration |
| `.agents/skills/dignified-python/SKILL.md` | Python engineering standards |

## Migration Notes

All original files have been moved to `docs/archive/2026-06-06-agents/`. The `supersedes` field in each canonical file's frontmatter maps back to the original source files.
