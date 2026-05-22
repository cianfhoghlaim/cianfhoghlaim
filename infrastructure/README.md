# Bonneagar - Browser Automation & Infrastructure

Bonneagar provides browser automation, agent orchestration, and infrastructure management for the Celtic Education Platform. This stream handles web scraping, MCP server implementations, and cloud infrastructure provisioning.

## Tech Stack Overview

### Core Python Packages
| Package | Version | Purpose |
|---------|---------|---------|
| **httpx** | >=0.27.0 | Async HTTP client with HTTP/2 support |
| **aiohttp** | >=3.9.0 | Async HTTP client/server framework |
| **fastapi** | >=0.109.0 | Modern async web framework for APIs |
| **uvicorn** | >=0.27.0 | ASGI server for FastAPI |
| **pydantic** | >=2.5.0 | Data validation and settings management |

### Agent Frameworks
| Package | Version | Purpose |
|---------|---------|---------|
| **google-adk** | >=1.0.0 | Google's Agent Development Kit for multi-agent coordination |
| **agno** | >=2.0.0 | Multi-agent orchestration with knowledge graphs and memory |
| **mcp** | >=1.0.0 | Model Context Protocol for agent-tool integration |
| **baml-py** | >=0.80.0 | Type-safe LLM function calling and schema generation |

### Observability & Monitoring
| Package | Version | Purpose |
|---------|---------|---------|
| **langfuse** | >=2.0.0 | LLM observability, tracing, and evaluation |
| **logfire** | Latest | Structured logging with OpenTelemetry |
| **mlflow** | >=2.18.0 | ML experiment tracking and model registry |
| **ragas** | >=0.1.10 | RAG evaluation framework with trace-based metrics |
| **datadog** | Latest | APM and infrastructure monitoring |

### Infrastructure as Code
| Package | Version | Purpose |
|---------|---------|---------|
| **@pulumi/hcloud** | Latest | Hetzner Cloud infrastructure provisioning |
| **@pulumi/oci** | Latest | Oracle Cloud Infrastructure provisioning |
| **@infisical/connect** | Latest | Infisical SDK for secrets management |

### Browser Automation
| Package | Version | Purpose |
|---------|---------|---------|
| **@browserbasehq/stagehand** | Latest | Browser automation with natural language actions |
| **patchright** | Latest | Browser automation with patch-based control |
| **playwright** | >=1.40.0 | Cross-browser automation and testing |

## Key Features & Capabilities

### Browser Automation
- **Sruth Browser**: Custom MCP server for browser-based web scraping and interaction
- **Firecrawl Integration**: Advanced web crawling with JavaScript rendering
- **Natural Language Actions**: Use plain English to control browser interactions via Stagehand
- **Multi-browser Support**: Chrome, Firefox, Safari via Playwright

### Agent Orchestration
- **Multi-Agent Coordination**: Sequential and parallel agent workflows via Google ADK and Agno
- **Knowledge Graph Memory**: Persistent memory across agent sessions using Graphiti
- **Tool Integration**: MCP protocol for seamless agent-tool communication
- **Schema Generation**: Type-safe LLM function calling via BAML

### Observability
- **Full Tracing**: End-to-end tracing of all agent interactions via Langfuse
- **Evaluation Framework**: RAG quality metrics via Ragas (faithfulness, answer relevance)
- **ML Tracking**: Experiment tracking and model registry via MLflow
- **Infrastructure Monitoring**: Datadog APM for performance insights

### Infrastructure
- **Multi-Cloud Support**: Hetzner Cloud and OCI provisioning via Pulumi
- **Secrets Management**: Infisical for secure secret injection
- **Modular Stacks**: Docker Compose stacks for each service (see `stacks/` directory)
- **Zero-Egress Design**: Federated lakehouse deployment with local processing

## Latest Package Updates (April 2026)

### Google ADK v1.0.0
- Multi-agent coordination with hierarchical patterns
- Google AI integration for enhanced reasoning
- Scalable architecture for complex workflows

### Agno v2.0.0
- Knowledge graphs (v2.0+) for complex relationship tracking
- Memory systems with temporal tracking
- Knowledge bases for persistent storage

### Langfuse v2.0.0
- "Experiments as a First-Class Concept" for qualitative evaluation
- Hosted MCP Server for native model context protocol support
- Specialized Agent Observability UI

### Ragas v0.1.10
- Trace-based metrics for deeper insights
- Faithfulness and answer relevance evaluation
- Improved support for multi-modal RAG

## Directory Structure

```
sruth/bonneagar/
├── browser/              # Browser automation and MCP servers
│   └── sruth_browser/   # Custom browser MCP server
├── observability/        # Observability integrations
├── pulumi/             # Infrastructure as code
│   └── Provision Resources on Hetzner Cloud with Pulumi.md
├── stacks/             # Docker Compose stacks
│   ├── langfuse/
│   ├── mlflow/
│   ├── cognee/
│   └── ... (19 stacks total)
├── pangolin/           # Identity-aware proxy and routing
├── komodo/             # Stack management
├── scripts/            # Utility scripts
├── templates/          # Stack templates
├── AGENTS.md           # Agent documentation
├── PANGOLIN-SETUP.md   # Pangolin setup guide
└── README.md           # This file
```

## Quick Start

### Browser Automation

```python
from sruth.bonneagar.browser.sruth_browser import SruthBrowser

# Initialize browser
browser = SruthBrowser()

# Navigate and extract
await browser.navigate("https://curriculumonline.ie")
content = await browser.extract_content()

# Use natural language actions
await browser.perform_action("Click on Junior Cycle Mathematics")
```

### Agent Orchestration

```python
from agno import Agent, AgentOrchestrator

# Create specialized agents
researcher = Agent(name="researcher", role="Web research")
analyzer = Agent(name="analyzer", role="Content analysis")

# Orchestrate workflow
orchestrator = AgentOrchestrator(
    agents=[researcher, analyzer],
    workflow="sequential"
)

result = await orchestrator.run("Research Irish curriculum updates")
```

### Infrastructure Provisioning

```bash
# Provision Hetzner Cloud resources
cd pulumi
pulumi up

# Start a stack
cd ../stacks/langfuse
docker compose up -d
```

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agent capabilities and patterns
- [PANGOLIN-SETUP.md](PANGOLIN-SETUP.md) - Identity-aware proxy setup
- [.skills/google-adk/SKILL.md](../../.skills/google-adk/SKILL.md) - Google ADK documentation
- [.skills/agno/SKILL.md](../../.skills/agno/SKILL.md) - Agno framework documentation
- [.skills/langfuse/SKILL.md](../../.skills/langfuse/SKILL.md) - Langfuse observability
- [.skills/ragas/SKILL.md](../../.skills/ragas/SKILL.md) - RAG evaluation

## Deployment

- **Development**: Local Docker Compose stacks
- **Production**: Komodo stacks on Hetzner Cloud and OCI
- **Secrets**: Infisical via Locket
- **Routing**: Pangolin identity-aware proxy

## Architecture

Bonneagar follows a modular architecture with clear separation of concerns:

1. **Browser Layer**: Web scraping and automation via Playwright, Stagehand, and custom MCP servers
2. **Agent Layer**: Multi-agent orchestration via Google ADK and Agno
3. **Observability Layer**: Tracing, evaluation, and monitoring via Langfuse, Ragas, and MLflow
4. **Infrastructure Layer**: Cloud provisioning via Pulumi and Docker Compose stacks
5. **Security Layer**: Secrets management via Infisical and identity-aware routing via Pangolin

## Contributing

When adding new packages or updating existing ones:

1. Update the Tech Stack Overview table
2. Add relevant skills documentation to `.skills/`
3. Update AGENTS.md with new agent patterns
4. Test with `docker compose` stacks before production deployment

## 🔌 MCP Integration
This stream leverages the **Infisical MCP (`@infisical/mcp`)** for dynamic secret retrieval and orchestration across our multi-cloud deployments, ensuring agents have secure, JIT access to infrastructure credentials without hardcoded values.
