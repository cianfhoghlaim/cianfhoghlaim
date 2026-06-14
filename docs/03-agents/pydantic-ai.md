---
title: 'Pydantic AI — Agent Framework with Structured Validation: Reference & Skill Card'
domain: 'agents'
status: 'stable'
description: 'Pydantic AI is an agent framework built by the creators of Pydantic that combines structured data validation with LLM-powered agent logic. Reference + skill card (KCG context, integration with our stack) + AG-UI protocol, Pydantic AI Gateway, Logfire MCP support, and DBOS integration.'
read_when:
  - looking for documentation on this topic
updated: 2026-06-13
supersedes:
  - docs/agents/PYDIANTIC_AI_REFERENCE.md
  - docs/agents/pydantic-ai.md
truth: sole
ccc_query_hints:
  - pydantic ai agent framework
  - pydantic ai gateway
  - pydantic ai ag-ui
  - pydantic logfire mcp
  - pydantic ai dbos durable execution
---

# Pydantic AI — Agent Framework with Structured Validation: Reference & Skill Card

> **Merged from 2 canonical sources**:
> - `PYDIANTIC_AI_REFERENCE.md` (93 lines, 5 sections) — reference
> - `pydantic-ai.md` (53 lines, 6 sections) — skill card with KCG context

---

## Skill Card

### Overview

Pydantic AI is an agent framework built by the creators of Pydantic that combines structured data validation with LLM-powered agent logic. It lets you define agents whose inputs and outputs are validated Pydantic models — ensuring type safety throughout the agent lifecycle. Supports function calling, tool integration, and streaming responses.

### Why This Matters for Kings' College Galway

The curriculum extraction pipeline's core requirement is structured, validated output. When an agent extracts a learning outcome from a syllabus, the output must conform to the `LearningOutcome` Pydantic model — with validated fields for subject, cycle, difficulty, language, and prerequisite IDs. Pydantic AI ensures this validation is built into the agent definition itself, not bolted on as post-processing. Combined with BAML's compile-time type checking, this provides end-to-end type safety from LLM output through to the database.

### Key Features

- **Pydantic validation** — Agent inputs/outputs are type-checked Pydantic models
- **Function calling** — Agents define typed tool functions
- **Streaming** — Stream partial responses with incremental validation
- **Multi-model** — Support for OpenAI, Anthropic, Gemini, and local models
- **Dependency injection** — Injectable services and configuration

### Installation

```bash
uv add pydantic-ai
```

### Integration with Our Stack

Pydantic AI agents are used alongside BAML for structured extraction. The Pydantic models defined for curriculum data (in `oideachais/models/`) are shared between BAML schemas, Pydantic AI agents, and the Dagster asset graph. Logfire provides tracing for Pydantic model validation within agent runs.

### Upstream

- **Repository**: <https://github.com/pydantic/pydantic-ai>
- **Documentation**: <https://ai.pydantic.dev>
- **Latest**: Active development (2025) — streaming improvements, tool definition v2, Logfire integration

### Screenshot

Pydantic AI is a programmatic framework. Validation results appear in Python tracebacks with precise field-level error messages. The Logfire dashboard shows structured traces of agent runs with Pydantic model validation events highlighted. The `.agents/skills/pydantic/` skill documents Pydantic v2 patterns.

---

## Pydantic AI Reference

Pydantic AI is a GenAI agent framework built the "Pydantic way" — emphasizing type safety, validation, and developer experience.

### AG-UI Protocol Integration

The Agent-User Interaction (AG-UI) Protocol is an open standard by the CopilotKit team standardizing frontend-agent communication with streaming, frontend tools, shared state, and custom events.

```bash
pip install 'pydantic-ai-slim[ag-ui]'
# or
uv add 'pydantic-ai-slim[ag-ui]'
```

Dependencies: `ag-ui-protocol` (AG-UI types and encoder), `starlette` (ASGI handler for FastAPI).

The AG-UI integration was originally built by Rocket Science in collaboration with Pydantic AI and CopilotKit.

### Pydantic AI Gateway

A unified interface for accessing multiple AI providers with a single key.

**Key Features:**
- **API Key Management:** Single Gateway key for all providers
- **Cost Limits:** Spending limits at project, user, API key levels
- **BYOK and Managed:** Bring your own keys or pay through the platform
- **Multi-Provider:** OpenAI, Anthropic, Google Vertex, Groq, AWS Bedrock
- **Backend Observability:** Log every request via Pydantic Logfire or OpenTelemetry
- **Zero Translation:** Requests flow through in each provider's native format — immediate access to new model features
- **Open Source:** Self-hosting available under AGPL-3.0
- **Enterprise:** SSO with OIDC, granular permissions, Cloudflare deployment

```python
# Using Pydantic AI Gateway
agent = Agent(
    model="gateway/openai:gpt-4o",
)
```

### Pydantic Logfire — MCP Support

Logfire supports instrumenting the MCP Python SDK on both client and server sides:

```python
import logfire
logfire.instrument_mcp()

# Server with FastMCP
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("my-server")

# Client with Pydantic AI
from pydantic_ai import Agent
agent = Agent("openai:gpt-4o", mcp_servers=[mcp])
```

### DBOS Integration

Pydantic AI integrates with DBOS for durable execution of agent workflows. Example at `pydantic_ai/dbos/README.md`:

```bash
# Minimal durable execution with DBOS + Pydantic AI
pip install dbos pydantic-ai
```

---

## Resources

- Docs: https://ai.pydantic.dev
- Gateway: https://gateway.pydantic.dev
- Logfire: https://logfire.pydantic.dev
- GitHub: https://github.com/pydantic/pydantic-ai
