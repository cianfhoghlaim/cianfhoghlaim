---
title: 'Package-Updates'
status: research
supersedes: []
superseded_by: []
last_touched: 2026-06-13
---

# Package Updates Plan

## Overview

This document summarizes the package analysis findings from the three sruth directories (bonneagar, meaisínfhoghlaim, oideachais) and the documentation updates created in the openspec directory.

## Analysis Summary

### Directories Analyzed

1. **sruth/bonneagar** - Browser automation, infrastructure, and observability
2. **sruth/meaisínfhoghlaim** - Agents, evaluation, and alignment
3. **sruth/oideachais** - Education pipeline and curriculum processing

### Key Package Findings

| Category | Packages | Versions | Skills |
|----------|----------|----------|---------|
| Agent Frameworks | google-adk, agno | >=0.1.0, >=2.0.0 | [`.skills/google-adk/SKILL.md`](.skills/google-adk/SKILL.md), [`.skills/agno/SKILL.md`](.skills/agno/SKILL.md) |
| Data Pipelines | dagster, dlt, sqlmesh | >=1.9.0, >=1.4.0, >=0.228.1 | [`.skills/dagster/SKILL.md`](.skills/dagster/SKILL.md), [`.skills/dlt/SKILL.md`](.skills/dlt/SKILL.md), [`.skills/sqlmesh/SKILL.md`](.skills/sqlmesh/SKILL.md) |
| Vector/ML | lancedb, sentence-transformers, unsloth | >=0.15.0, >=3.0.0, >=2024.12 | [`.skills/lancedb/SKILL.md`](.skills/lancedb/SKILL.md) |
| Memory Systems | graphiti-core, cognee | >=0.5.0, >=0.1.0 | [`.skills/graphiti-core/SKILL.md`](.skills/graphiti-core/SKILL.md), [`.skills/cognee/SKILL.md`](.skills/cognee/SKILL.md) |
| Observability | langfuse, ragas | >=2.0.0, >=0.1.10 | [`.skills/langfuse/SKILL.md`](.skills/langfuse/SKILL.md), [`.skills/ragas/SKILL.md`](.skills/ragas/SKILL.md) |
| Frontend | tanstack-start, vinxi, copilotkit | ^1.94.0, ^0.5.1, >=0.1.0 | [`.skills/tanstack-start/SKILL.md`](.skills/tanstack-start/SKILL.md), [`.skills/vinxi/SKILL.md`](.skills/vinxi/SKILL.md), [`.skills/copilotkit/SKILL.md`](.skills/copilotkit/SKILL.md) |
| Browser Automation | @browserbasehq/stagehand | - | - |
| Infrastructure | @pulumi/hcloud, @pulumi/oci | - | - |

## Documentation Created

### New Spec Files

1. **[`openspec/specs/agent-frameworks/spec.md`](openspec/specs/agent-frameworks/spec.md)**
   - Multi-agent coordination patterns
   - Tool integration for agents
   - Memory systems for agents
   - Structured outputs with Pydantic models
   - Google ADK and Agno framework details
   - Built-in tools and storage backends

2. **[`openspec/specs/data-pipeline/spec.md`](openspec/specs/data-pipeline/spec.md)**
   - Asset-based pipeline design
   - Incremental loading with cursor-based extraction
   - Schema inference and evolution
   - Partitioning strategies
   - Dagster, DLT, and SQLMesh framework details
   - Write dispositions and destination configurations

3. **[`openspec/specs/observability/spec.md`](openspec/specs/observability/spec.md)**
   - LLM tracing with decorators and manual creation
   - Prompt management with versioning
   - A/B testing for prompt optimization
   - Evaluation metrics (faithfulness, relevance, context precision)
   - Langfuse and RAGAS framework details
   - Cost and latency tracking

4. **[`openspec/specs/frontend-frameworks/spec.md`](openspec/specs/frontend-frameworks/spec.md)**
   - File-based routing patterns
   - Server functions with type safety
   - SSR/Streaming capabilities
   - AI agent UI integration with CopilotKit
   - TanStack Start, Vinxi, and CopilotKit framework details
   - Deployment platform support

5. **[`openspec/specs/memory-systems/spec.md`](openspec/specs/memory-systems/spec.md)**
   - Temporal knowledge graphs with Graphiti Core
   - Episodic memory for agents
   - Knowledge graph traversal and search
   - Hybrid search combining vector and graph
   - Cognee and LanceDB framework details
   - Dual-engine architecture for production systems

### Updated Documentation

1. **[`AGENTS.md`](AGENTS.md)** - Updated with latest package information and best practices
2. **[`README.md`](README.md)** - Updated with package analysis findings
3. **Directory READMEs** - Updated for sruth/bonneagar, sruth/meaisínfhoghlaim, sruth/oideachais

## Key Features by Package

### Agent Frameworks

**Google ADK (>=0.1.0)**
- Multi-agent coordination (sequential, parallel, hierarchical)
- Tool integration (WebSearchTool, CalculatorTool, custom tools)
- Memory systems (vector_store, key_value, hybrid)
- Google AI integration with Gemini models

**Agno (>=2.0.0)**
- Agent orchestration for single agents and multi-agent teams
- Tool calling with built-in tools (DuckDuckGo, Calculator, YFinance, PythonTools)
- Memory systems with PostgreSQL, SQLite, Redis, and DynamoDB backends
- Knowledge bases with RAG-style integration
- Knowledge graph support for complex relationships

### Data Pipelines

**Dagster (>=1.9.0)**
- Asset-first design with automatic dependency tracking
- Observability with rich metadata, lineage, and data quality tracking
- Type safety with ConfigurableResource and Pydantic validation
- Partitioning for efficient incremental processing at scale
- First-class testing with mocked resources and unit tests

**DLT (>=1.4.0)**
- Declarative loading with decorators for resources and sources
- Automatic schema detection and evolution
- Cursor-based incremental extraction
- Multiple destinations (DuckDB, BigQuery, Snowflake, Postgres, S3)
- Automatic flattening of nested JSON structures
- Streaming support for real-time data

**SQLMesh (>=0.228.1)**
- DuckDB integration for local development
- Virtual data environments for isolated testing
- CI/CD for SQL transformations
- Model versioning and deployment

### Memory Systems

**Graphiti Core (>=0.5.0)**
- Temporal tracking of relationships and entities over time
- Episodic memory for storing agent experiences
- Bi-temporal model (valid time + transaction time)
- Entity and relationship extraction from text
- Point-in-time queries for historical analysis

**Cognee (>=0.1.0)**
- Knowledge graphs from documents and text
- Semantic search with vector + graph hybrid approach
- Persistent memory for AI agents
- Multi-backend support (vector and graph databases)
- Graph traversal for context-aware retrieval
- Temporal tracking of knowledge changes

**LanceDB (>=0.15.0)**
- Embedded vector database without separate server
- Multimodal storage (vectors, text, images, audio)
- HNSW indexing for high-performance search
- MVCC safety for concurrent operations
- Hybrid search combining vector and full-text search

### Observability

**Langfuse (>=2.0.0)**
- Tracing with decorators for automatic capture
- Prompt management with versioning and variable substitution
- A/B testing for prompt and model comparison
- Analytics with deep insights into LLM performance
- Session tracking for multi-turn conversations
- Evaluation scoring with manual and automated scores

**RAGAS (>=0.1.10)**
- Trace-based metrics for RAG evaluation
- Multiple metrics: faithfulness, answer relevance, context precision, context recall
- LLM-based evaluation using configurable models
- Custom metrics for domain-specific evaluation
- Batch evaluation with configurable workers

### Frontend Frameworks

**TanStack Start (^1.94.0)**
- File-based routing with automatic route tree generation
- Server functions with type-safe RPC-style calls
- SSR/Streaming with progressive UI rendering
- End-to-end TypeScript integration
- React Server Components for optimal performance
- Edge runtime support (Vercel, Cloudflare)

**Vinxi (^0.5.1)**
- Vite-powered for fast development
- File-based routing with automatic generation
- Server functions with type safety
- SSR/Streaming support
- Modular plugin-based architecture
- Multi-platform deployment (Vercel, Netlify, Cloudflare)

**CopilotKit (>=0.1.0)**
- Pre-built React components for AI interactions
- Easy integration with various AI agents
- Built-in state management for AI conversations
- Fully customizable components and themes
- Multi-agent support
- Side panel and text area components

## Integration Patterns

### Agent + Memory + Observability

```
┌─────────────────────────────────────────────────────────┐
│                   AI Agent System                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌────────┐  │
│  │ Agent       │  │ Memory       │  │ Observ │  │
│  │ (Agno/ADK) │  │ (Cognee/    │  │ (Langfuse/│  │
│  │             │  │ Graphiti)    │  │ RAGAS)  │  │
│  │ - Tools    │  │ - Temporal   │  │ - Trace │  │
│  │ - Memory    │  │ - Episodes   │  │ - Score │  │
│  │ - Knowledge │  │ - Graph      │  │ - Eval  │  │
│  └─────────────┘  └──────────────┘  └────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Pipeline + Knowledge Graph

```
┌─────────────────────────────────────────────────────────┐
│              Data + Knowledge Pipeline              │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────┐│
│  │ Data Source  │  │ Pipeline        │  │ Knowledge││
│  │ (API/DB)    │  │ (Dagster/DLT)  │  │ Graph    ││
│  │              │  │ - Assets        │  │ (Cognee/││
│  │              │  │ - Incremental    │  │ Graphiti)││
│  │              │  │ - Validation    │  │ - Search ││
│  │              │  │ - Scheduling    │  │ - Graph  ││
│  └──────────────┘  └──────────────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
```

### Frontend + Agent UI

```
┌─────────────────────────────────────────────────────────┐
│           Full-Stack AI Application                │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────┐│
│  │ Frontend     │  │ Agent UI        │  │ Backend  ││
│  │ (TanStack/   │  │ (CopilotKit)    │  │ (Agno/  ││
│  │ Vinxi)       │  │ - Chat          │  │ ADK)    ││
│  │ - Routing    │  │ - Sidebar       │  │ - Agents ││
│  │ - SSR        │  │ - Multi-agent   │  │ - Tools  ││
│  │ - Streaming  │  │ - Context       │  │ - Memory ││
│  └──────────────┘  └──────────────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
```

## Best Practices

### Agent Development
1. **Clear Instructions**: Provide specific, actionable instructions
2. **Single Responsibility**: Each agent should have a focused purpose
3. **Tool Selection**: Only include relevant tools to reduce complexity

### Data Engineering
1. **Asset-First Design**: Define data assets, not just tasks
2. **Incremental Loading**: Always use incremental for large datasets
3. **Schema Evolution**: Let systems evolve schemas automatically

### Memory Systems
1. **Episode Granularity**: Keep episodes focused and specific
2. **Reference Time**: Always set accurate reference times for temporal queries
3. **Dual-Engine**: Consider separating static knowledge from dynamic memory

### Observability
1. **Regular Evaluation**: Evaluate regularly during development
2. **A/B Testing**: Compare different prompt and model variants
3. **Cost Tracking**: Monitor LLM costs and optimize accordingly

### Frontend Development
1. **File-Based Routing**: Leverage automatic route generation
2. **Server Functions**: Use type-safe RPC-style server calls
3. **Streaming**: Enable streaming for better user experience

## Next Steps

1. **Implementation**: Apply these patterns to the sruth directories
2. **Integration**: Connect agent, data pipeline, and memory systems
3. **Testing**: Implement evaluation with RAGAS and tracing with Langfuse
4. **Deployment**: Set up observability and monitoring for production systems

## Related Documentation

- [`.skills/`](.skills/) - Complete skill documentation for all packages
- [`AGENTS.md`](AGENTS.md) - Agent development guidelines
- [`README.md`](README.md) - Project overview and setup
- [`openspec/specs/`](openspec/specs/) - Detailed capability specifications
