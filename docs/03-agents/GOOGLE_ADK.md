---
title: 'Google ADK — Agent Development Kit: Comprehensive Reference & Skill Card'
domain: 'agents'
status: 'stable'
description: 'Google''s Agent Development Kit (ADK) open-source framework for building multi-agent AI systems. Comprehensive reference (project structure, workflow primitives, examples, neuro-symbolic truth anchoring, deployment) plus skill card (KCG context, integration with our stack).'
read_when:
  - building AI agents
  - looking for documentation on this topic
updated: 2026-06-13
supersedes:
  - docs/agents/GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md
  - docs/agents/google-adk.md
truth: sole
ccc_query_hints:
  - google adk agent development kit
  - google adk multi-agent orchestration
  - google adk a2a protocol
  - google adk firecrawl
---

# Google ADK — Agent Development Kit: Comprehensive Reference & Skill Card

> **Merged from 2 canonical sources**:
> - `GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md` (141 lines, 5 parts) — architectural deep-dive
> - `google-adk.md` (53 lines, 6 sections) — skill card with KCG context
>
> The original referenced 8 stub files in `google-adk/` subdirs (README.md, GEMINI.md, deployment/README.md, tests/load_test/README.md, examples/academic-research/README.md, examples/deep-search/README.md, examples/firecrawl/README.md, etc.) — those have been migrated to the canonical.

---

## Overview (skill card)

Google's Agent Development Kit (ADK) is an open-source framework for building multi-agent AI systems. It provides a workflow engine for defining agent hierarchies, inter-agent routing, and tool integration — enabling complex multi-step reasoning across multiple specialised agents.

### Why This Matters for Kings' College Galway

The curriculum extraction pipeline involves multiple AI agents working in concert: an OCR agent that reads exam papers, a BAML extraction agent that structures the content, an embedding agent that indexes it, a Graphiti agent that builds prerequisite chains, and a RAGAS agent that evaluates quality. Google ADK provides the orchestration framework for these agent workflows, handling inter-agent message passing and ensuring each agent's output is correctly routed to the next stage.

### Key Features

- **Multi-agent orchestration** — Define hierarchies of specialised agents
- **Inter-agent routing** — Native message passing between agents
- **Tool integration** — Agents can call external tools and APIs
- **Workflow engine** — Define sequential, parallel, and conditional agent chains
- **NodeRunner** — Execute agent graphs with dependency resolution

### Installation

```bash
uv add google-adk
```

### Integration with Our Stack

ADK agent definitions are used alongside the BAML extraction pipeline and the Agno framework. The LiteLLM gateway provides the LLM backend for all agents, and Langfuse traces every inter-agent message for observability.

### Upstream

- **Repository**: <https://github.com/google/adk-python>
- **Documentation**: <https://google.github.io/adk-docs/>
- **Latest**: v2.1.x (2025) — multi-agent workflow engine, NodeRunner, inter-agent routing improvements

### Screenshot

Google ADK is a programmatic framework with no standalone UI. Agent workflows are defined in Python code. The Langfuse trace view shows agent interactions as nested spans in a waterfall chart. The `.agents/skills/google-adk/` directory contains the project's ADK skill definition.

---

## Part I: Google ADK Overview

Google's Agent Development Kit (ADK) is a framework for building, deploying, and managing AI agents. It supports the Agent2Agent (A2A) protocol and integrates with Google Cloud infrastructure.

### Project Structure

```
saoi/
├── app/                 # Core application code
│   ├── agent.py         # Main agent logic
│   ├── agent_engine_app.py
│   └── app_utils/       # App utilities
├── .cloudbuild/         # CI/CD pipeline configs
├── deployment/          # Terraform infra
├── notebooks/           # Jupyter notebooks
├── tests/               # Unit, integration, load tests
├── GEMINI.md            # AI-assisted development guide
└── pyproject.toml       # Dependencies
```

### Quick Start

```bash
make install && make playground
```

**Commands:**

| Command | Description |
|---|---|
| `make install` | Install dependencies via uv |
| `make playground` | Local dev environment |
| `make deploy` | Deploy to Agent Engine |
| `make inspector` | Launch A2A Protocol Inspector |
| `make test` | Run tests |
| `make lint` | Code quality (codespell, ruff, mypy) |

---

## Part II: ADK Workflow Primitives

### Sequential Agent
Linear phases: OCR → Text Cleaning → Context Extraction. Each step must complete before next begins.

### Loop Agent
Draft-Critique-Refine cycle. The LoopAgent executes Drafter and Critic repeatedly until a Termination Strategy condition is met (e.g., quality score >95%, zero compliance violations).

### Parallel Agent
"Fan-Out/Gather" pattern — splits long documents into sections, spawns concurrent agents to process simultaneously, reassembles results in correct order.

### Coordinator Pattern (TripPlanner)
Root Agent acts as persistent Project Manager — decomposes tasks into sub-tasks, assigns to specialized agents, maintains global view of document state. Prevents the "Receptionist Problem" where root agent loses control after routing.

---

## Part III: Example Projects

### Academic Research
Multi-agent research pipeline:
- Web Search Agent: Discovers relevant papers
- New Research Agent: Deep research on findings
- Sub-agents orchestrated via ADK routing
- Evaluation via eval/ framework

### Deep Search
Full-stack search agent with React frontend. Agent orchestrates web searches, extracts structured data, and presents results in components.

### Firecrawl Integration
ADK + Firecrawl examples:
- **Quickstart Streaming:** SSE streaming from Firecrawl agent
- **Agent Team:** Multi-agent Firecrawl team with tool routing
- **Tool Usage Examples:** Firecrawl tools within ADK agents

```typescript
// ADK agent with Firecrawl tool
const agent = adk.agent({
  model: "google/gemini-2.0-flash",
  tools: [firecrawlTool],
  systemPrompt: "You have access to Firecrawl for web scraping."
});
```

### LaunchMyBakery
Complete bakery business launch agent using ADK with MCP tools. Demonstrates authentication, multi-step reasoning, and business logic.

### With-ADK: A2A Protocol
Demonstrates Google's Agent-to-Agent protocol:
- **A2A TypeScript:** TypeScript A2A server/client
- **A2A Python:** Python implementation
- **AG-UI Integration:** Agent UI protocol support

---

## Part IV: Neuro-Symbolic Truth Anchoring

The ADK Compliance Agent integrates symbolic Ontology (OWL Knowledge Graph) for deterministic verification:

- If Glossary mandates "Mionnscríbhinn" for "Affidavit" and neural model outputs "Ráiteas faoi mhionn" (valid synonym), symbolic layer detects mismatch and forces correction
- Ensures "Ground Truth" rules are mathematically enforced, not probabilistically generated

---

## Part V: Deployment

Terraform-based deployment to Google Cloud:
- Agent Engine for production serving
- Cloud Build for CI/CD
- Cloud Trace for telemetry (always enabled)
- Optional: GCS, BigQuery, Cloud Logging for prompt-response logging (metadata only in production)

```bash
make deploy              # Deploy to Agent Engine
make register-gemini-enterprise  # Register to Gemini Enterprise
```

---

## Resources

- Agent Starter Pack: https://github.com/GoogleCloudPlatform/agent-starter-pack
- A2A Protocol: https://github.com/google/A2A
- Gemini CLI: https://github.com/google-gemini/gemini-cli
- Restate Docs: https://docs.restate.dev
