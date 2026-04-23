# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Agent Capabilities

### Agent Frameworks

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`agno`](.skills/agno/SKILL.md) | Multi-agent orchestration with tool calling | Knowledge graphs (v2.0+), memory systems, knowledge bases |
| [`google-adk`](.skills/google-adk/SKILL.md) | Google's Agent Development Kit | Multi-agent coordination, Google AI integration, scalable architecture |

### Knowledge & Memory Systems

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`graphiti-core`](.skills/graphiti-core/SKILL.md) | Temporal knowledge graph memory | Bi-temporal model, episodic memory, temporal tracking |
| [`graphiti`](.skills/graphiti/SKILL.md) | Knowledge graph for agents | HNSW indexing (v0.5+), MVCC safety, hybrid search |
| [`cognee`](.skills/cognee/SKILL.md) | Graph-based knowledge management | Graph traversal (v0.1+), temporal tracking, multi-modal support |
| [`lancedb`](.skills/lancedb/SKILL.md) | Vector database for RAG | HNSW indexing (v0.15+), MVCC safety, hybrid search |

### Data Pipelines & Orchestration

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`dagster`](.skills/dagster/SKILL.md) | Data orchestration platform | Asset-based pipelines (v1.9+), observability, partitioning |
| [`dlt`](.skills/dlt/SKILL.md) | Data load tool for pipelines | Pythonic pipelines (v1.4+), streaming support, schema inference |
| [`sqlmesh`](.skills/sqlmesh/SKILL.md) | Data transformation framework | DuckDB integration, virtual data warehouse, CI/CD |

### Observability & Evaluation

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`langfuse`](.skills/langfuse/SKILL.md) | LLM observability platform | Prompt management, A/B testing, trace-based analytics |
| [`ragas`](.skills/ragas/SKILL.md) | RAG evaluation framework | Trace-based metrics, faithfulness, answer relevance |

### UI & Agent Interaction

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`copilotkit`](.skills/copilotkit/SKILL.md) | AI agent UI framework | React components, multi-agent support, state management |
| [`vinxi`](.skills/vinxi/SKILL.md) | Full-stack framework (Poimandres) | Vite-based, server components, edge runtime |

### Model Training & Fine-tuning

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`unsloth`](.skills/unsloth/SKILL.md) | LLM fine-tuning | Multilingual support (v2024.12+), flash attention, 2x faster |
| [`tanstack-start`](.skills/tanstack-start/SKILL.md) | React framework | React Server Components (v1.94+), edge runtime, streaming suspense |

## Tool Integration Patterns

### Multi-Agent Coordination

Use [`google-adk`](.skills/google-adk/SKILL.md) or [`agno`](.skills/agno/SKILL.md) for:

- **Sequential workflows**: Research → Analyze → Write
- **Parallel execution**: Multiple agents working simultaneously
- **Hierarchical patterns**: Orchestrator managing specialist agents

```python
# Example: Multi-agent research team
orchestrator = AgentOrchestrator(
    agents=[researcher, analyst, writer],
    workflow="sequential"
)
```

### Knowledge Graph Memory

Use [`graphiti-core`](.skills/graphiti-core/SKILL.md) for temporal tracking:

```python
# Track curriculum changes over time
episode = await client.add_episode(
    name="Curriculum Update",
    episode_body="Added data science to Junior Cycle Mathematics",
    reference_time=datetime(2025, 4, 23),
    episode_type=EpisodeType.knowledge_update
)
```

### Data Pipeline Patterns

Use [`dagster`](.skills/dagster/SKILL.md) assets with [`dlt`](.skills/dlt/SKILL.md) sources:

```python
@asset
def curriculum_data():
    """Asset defined in Dagster"""
    return pipeline.run(my_api_source())  # dlt pipeline
```

### RAG Evaluation

Use [`ragas`](.skills/ragas/SKILL.md) with [`langfuse`](.skills/langfuse/SKILL.md) tracing:

```python
result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy]
)
langfuse.score(name="rag_evaluation", value=result)
```

## Best Practices

### Agent Development

1. **Use knowledge graphs** for complex relationships ([`agno`](.skills/agno/SKILL.md) v2.0+, [`cognee`](.skills/cognee/SKILL.md) v0.1+)
2. **Implement temporal tracking** for evolving data ([`graphiti-core`](.skills/graphiti-core/SKILL.md))
3. **Leverage MVCC safety** for concurrent operations ([`lancedb`](.skills/lancedb/SKILL.md) v0.15+, [`graphiti`](.skills/graphiti/SKILL.md) v0.5+)
4. **Use hybrid search** for better relevance ([`lancedb`](.skills/lancedb/SKILL.md), [`graphiti`](.skills/graphiti/SKILL.md))

### Data Engineering

1. **Define assets first** in Dagster for better observability
2. **Use streaming support** in dlt (v1.4+) for real-time data
3. **Integrate DuckDB** with sqlmesh for local development
4. **Implement incremental loading** with cursor-based extraction

### Observability

1. **Trace all LLM calls** with Langfuse decorators
2. **A/B test prompts** using Langfuse prompt management
3. **Evaluate RAG systems** with RAGAS trace-based metrics
4. **Monitor costs and latency** across all agent interactions

### UI/UX

1. **Use CopilotKit components** for consistent AI interfaces
2. **Implement streaming suspense** with TanStack Start (v1.94+)
3. **Leverage React Server Components** for better performance
4. **Support multi-agent interfaces** for complex workflows

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

## Skill Activation

When working on tasks, activate the appropriate skill based on the domain:

- **Agent development**: `agno`, `google-adk`
- **Knowledge management**: `graphiti-core`, `graphiti`, `cognee`, `lancedb`
- **Data pipelines**: `dagster`, `dlt`, `sqlmesh`
- **Observability**: `langfuse`, `ragas`
- **UI development**: `copilotkit`, `vinxi`, `tanstack-start`
- **Model training**: `unsloth`

See [`.skills/`](.skills/) directory for detailed skill documentation.

