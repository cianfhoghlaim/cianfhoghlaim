---
title: 'Google ADK — Agent Development Kit'
domain: 'agents'
status: 'stable'
description: 'Google''''s Agent Development Kit (ADK) is an open-source framework for building multi-agent AI systems. It provides a workflow engine for defining agent hierarchies, inter-agent routing, and tool integration — enabling complex multi-step reasoning across multiple specialised agents'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/google-adk.md
ccc_query_hints:
  - google adk — agent development kit
---

# Google ADK — Agent Development Kit

## Overview

Google's Agent Development Kit (ADK) is an open-source framework for building multi-agent AI systems. It provides a workflow engine for defining agent hierarchies, inter-agent routing, and tool integration — enabling complex multi-step reasoning across multiple specialised agents.

## Why This Matters for Kings' College Galway

The curriculum extraction pipeline involves multiple AI agents working in concert: an OCR agent that reads exam papers, a BAML extraction agent that structures the content, an embedding agent that indexes it, a Graphiti agent that builds prerequisite chains, and a RAGAS agent that evaluates quality. Google ADK provides the orchestration framework for these agent workflows, handling inter-agent message passing and ensuring each agent's output is correctly routed to the next stage.

## Key Features

- **Multi-agent orchestration** — Define hierarchies of specialised agents
- **Inter-agent routing** — Native message passing between agents
- **Tool integration** — Agents can call external tools and APIs
- **Workflow engine** — Define sequential, parallel, and conditional agent chains
- **NodeRunner** — Execute agent graphs with dependency resolution

## Installation

```bash
uv add google-adk
```

## Integration with Our Stack

ADK agent definitions are used alongside the BAML extraction pipeline and the Agno framework. The LiteLLM gateway provides the LLM backend for all agents, and Langfuse traces every inter-agent message for observability.

## Upstream

- **Repository**: <https://github.com/google/adk-python>
- **Documentation**: <https://google.github.io/adk-docs/>
- **Latest**: v2.1.x (2025) — multi-agent workflow engine, NodeRunner, inter-agent routing improvements

## Screenshot

Google ADK is a programmatic framework with no standalone UI. Agent workflows are defined in Python code. The Langfuse trace view shows agent interactions as nested spans in a waterfall chart. The `.agents/skills/google-adk/` directory contains the project's ADK skill definition.
