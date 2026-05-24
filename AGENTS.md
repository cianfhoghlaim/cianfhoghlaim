# Agent Instructions

This project uses standard GitHub/Forgejo issues for task tracking. Please use `gh` or standard `git` workflows.

## Infrastructure & Secrets (Critical for Agents)

### Pangolin Convergence Architecture
- **Control Plane (`arm1-oci`)**: Handles routing (Pangolin), identity (Pocket ID), and orchestration (Komodo).
- **Workload Host (`bunchloch` - MacBook M4)**: Handles memory-intensive workloads (Vector DBs, Graph DBs, LLM Inference, local analytics).

### Secrets Management (Infisical + mise)
- Secrets are **automatically injected** via `mise` hooks when entering a directory.
- `infisical export` resolves all secrets instantly into an ignored `.env` file from a `.infisical.env` template.
- **DO NOT** attempt to manually manage, write, or look for `.env` files when configuring MCP servers or running tools. The environment is already hydrated.

## Agent Capabilities

### Agent Frameworks

| Skill | Purpose | Key Features |
|-------|---------|--------------|
| [`agno`](.skills/agno/SKILL.md) | Multi-agent orchestration with tool calling | AgentOS, stateless execution, full async knowledge base, unified media (v2.0+) |
| [`google-adk`](.skills/google-adk/SKILL.md) | Google's Agent Development Kit | Multi-Agent Workflow Engine, NodeRunner, Native Inter-Agent Routing (v2.1+) |

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
| [`dagster`](.skills/dagster/SKILL.md) | Data orchestration platform | Asset-based pipelines (v1.13+), branch deployments, AI skills integration |
| [`dlt`](.skills/dlt/SKILL.md) | Data load tool for pipelines | dlt+ Projects & Cache, Pythonic pipelines, schema inference |
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


## 🤖 Critical Agent Protocols & Habits

As an autonomous agent operating within the Cianfhoghlaim stack (via OpenCode, Roo, or Cline), you **MUST** adhere to these recursive habits to prevent regressions and maintain stability:

### 1. Zero Absolute Namespaces in Data Pipelines
Never import `oideachais.data_platform...` from within the data platform itself. Always use relative or local package imports (e.g., `from dlt_sources.ireland...`). Failing to do so causes critical `ModuleNotFoundError` crashes in the Dagster orchestrator.

### 2. Respect the Ingestion Cache
Before executing live web scrapes (e.g., Firecrawl on `examinations.ie`) that drain API credits and risk rate limits, always test `dlt` pipelines with the fallback cache enabled:
`os.environ['USE_LOCAL_SCRAPES'] = 'true'`
This automatically routes extraction to the highly curated `stedding/ingest_queue/`.

### 3. Strict Secret Hydration
**Never create manual `.env` files.** If a secret is missing:
1. Add it to the `.infisical.env` template.
2. Run `bun run init-vault.ts` in `scripts/infisical/` to synchronize it with the remote `dev-baile` Infisical vault.
3. Allow the `mise` directory hooks or `locket inject` to hydrate the runtime environment automatically.

### 4. Self-Documenting Telemetry
Upon finishing a complex task, pipeline update, or major deployment, you **MUST** execute the synchronization script:
`./scripts/sync_agent_docs.sh`
This updates the local telemetry blocks across `README.md` and ensures no rogue imports were introduced.
