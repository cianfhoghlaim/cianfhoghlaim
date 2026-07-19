---
name: agent-observability
description: Unified agent observability stack — Langfuse cost + prompt management (`@observe`), Logfire Python tracing, MLflow experiment tracking + model registry, Ragas evaluation as a Dagster asset_check, structlog. Use when wiring traces, costs, RAG quality, and experiments across the KCG agent layer.
---

# Agent Observability

## When to use this skill

Use when you need to:

- "Trace every LLM call with input + output + token count"
- "Track experiment runs (RAGAS scores, hyperparams) in MLflow"
- "Monitor cost per agent invocation (USD) in Langfuse"
- "Add a RAGAS quality gate to a Dagster asset (asset_check)"
- "Wire Logfire Python tracing for full-stack observability"
- "Set up structured JSON logging in production"

## Overview

The KCG agent observability stack is **5 layers**, all wired
together. Each layer covers a different concern:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Traces (Langfuse + Logfire)                        │
│  → FastAPI middleware, @observe / logfire.span decorators   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Experiments (MLflow)                              │
│  → Run tracking, model registry, artifact logging            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Cost + prompt management (Langfuse)               │
│  → Per-invocation cost, prompt versioning, eval              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: RAG quality (Ragas)                                │
│  → faithfulness, answer-relevancy, ctx precision/recall     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Structured logging (structlog)                    │
│  → JSON for prod, console for dev                            │
└─────────────────────────────────────────────────────────────┘
```

## 1. Langfuse + Logfire tracing

```python
import logfire
from langfuse.decorators import observe, langfuse_context


@observe(name="curriculum_search", as_type="workflow")
def curriculum_search(query: str) -> list[dict]:
    """Top-level workflow — emitted as a Langfuse workflow span."""
    results = vector_search(query)
    ranked = rerank_with_bge_m3(results)
    return format_response(ranked)


@observe(name="bge_m3_embedder", as_type="agent")
def bge_m3_embed(text: str) -> list[float]:
    return embed_bge_m3(text)


@observe(as_type="generation")  # auto-captures cost + token counts
def llm_call(prompt: str) -> str:
    return openai_client.chat(prompt)


@observe(name="vector_search", as_type="span")
def vector_search(query: str) -> list[dict]:
    return lance_search(query, top_k=10)
```

**FastAPI integration** (Logfire auto-instruments FastAPI via
`logfire.instrument_fastapi(app)`):

```python
import logfire
from fastapi import FastAPI

logfire.configure(token=os.environ["LOGFIRE_TOKEN"])
app = FastAPI()
logfire.instrument_fastapi(app)
```

`@observe(as_type="generation")` and Logfire's `logfire.instrument_*`
automatically capture:
- model name + provider
- input + output
- token counts (prompt + completion)
- cost (USD, via Langfuse)
- latency

## 2. MLflow experiment tracking + model registry

```python
import mlflow

mlflow.set_tracking_uri("https://mlflow.cianfhoghlaim.ie")
mlflow.set_experiment("kcg-rag-pipeline")


@mlflow.trace
def run_rag_experiment(query: str) -> dict:
    """Each invocation is a trace; param + metric logs go to MLflow."""
    mlflow.log_param("embedding_model", "BAAI/bge-m3")
    mlflow.log_param("reranker", "bge-reranker-v2-m3")
    mlflow.log_metric("faithfulness", 0.94)
    mlflow.log_metric("answer_relevancy", 0.89)
    return {"results": [...]}
```

**Model registry**:

```python
mlflow.register_model(
    "runs:/abc123/model",
    "kcg-bge-m3-v3",
)
```

## 3. Langfuse cost + prompt management

```python
from langfuse.decorators import observe, langfuse_context


@observe(as_type="generation")
def llm_call(prompt: str) -> str:
    response = openai_client.chat(prompt)
    # Langfuse automatically tracks cost + token usage
    langfuse_context.update_current_observation(
        model="gpt-4o-mini",
        usage_details={"input": 150, "output": 75},
    )
    return response
```

**Prompt versioning**:

```python
from langfuse import Langfuse

langfuse = Langfuse()
prompt = langfuse.get_prompt("system_prompt", label="production")
response = openai_client.chat(prompt.compile(variables={"query": query}))
```

## 4. Ragas evaluation (Dagster asset_check)

```python
from dagster import asset_check, AssetCheckResult, AssetCheckSeverity
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy


@asset_check(asset=rag_asset, blocking=True)
def rag_quality_check(context, rag_asset):
    """Run Ragas on the latest 100 samples; gate on faithfulness."""
    samples = load_eval_samples(limit=100)
    scores = evaluate(samples, metrics=[faithfulness, answer_relevancy])
    f = scores["faithfulness"]
    r = scores["answer_relevancy"]
    return AssetCheckResult(
        passed=f >= 0.8 and r >= 0.7,
        severity=AssetCheckSeverity.ERROR if (f < 0.8 or r < 0.7) else AssetCheckSeverity.WARN,
        metadata={
            "faithfulness": f,
            "answer_relevancy": r,
            "n_samples": len(samples),
        },
    )
```

**KCG thresholds**: faithfulness ≥ 0.8, answer-relevancy ≥ 0.7.

## 5. Structured logging with structlog

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),  # JSON for prod
    ],
)

log = structlog.get_logger()
log.info("rag_query", query=query, n_results=10, latency_ms=42)
```

Output:

```json
{"event": "rag_query", "level": "info", "timestamp": "2026-04-15T12:34:56Z", "query": "...", "n_results": 10, "latency_ms": 42}
```

## Observability checklist

For every new agent in the KCG stack, ensure:

- [ ] Every LLM call is wrapped in `logfire.instrument_*` (Logfire)
  or `@observe` (Langfuse)
- [ ] Every agent is wrapped in `@agent` for cost tracking
- [ ] Every workflow is wrapped in `@workflow` for end-to-end
  tracing
- [ ] Every task is wrapped in `@task` for step-level timing
- [ ] RAGAS quality gate (asset_check) for any RAG asset
- [ ] MLflow experiment for any model retraining
- [ ] structlog JSON logging in production

## KCG integration

- `observability/` — the integration module
  (Logfire + MLflow + Langfuse + Ragas)
- `agents/meaisinfhoghlaim/evaluation/` — the Ragas evaluation harness
- `agents/meaisinfhoghlaim/evaluation/canonical_eval_set.json` —
  100 samples × 4 metrics
- Dagster assets: `orchestration/defs/quality_assets.py`
  (the Ragas asset_check group)

## Related skills

- `.agents/skills/langfuse/SKILL.md` — LLM tracing +
  cost + prompt management
- `.agents/skills/mlflow/SKILL.md` — experiment tracking +
  model registry
- `.agents/skills/ragas/SKILL.md` — RAG evaluation
- `.agents/skills/dagster/SKILL.md` — Dagster asset_check
  integration
- `.agents/skills/pydantic-ai/SKILL.md` — Pydantic AI + Logfire
  agent framework

## Dagster Cognee integration

Cognee sits inside the data platform as **8 Dagster
software-defined assets** that drive the canonical-docs →
knowledge-graph pipeline:

```
docs_collected ─────┐
   (DLT filesystem) │    codebase_indexed ─────┐
                    ▼            (CCC job)      ▼
              docs_added_to_cognee      ccc_index_updated
                    │                          (sidecar)
                    ▼
              docs_cognified  ◀──── cognify via HTTP API
                    │             (DeepSeek V4 Pro entity
                    ▼              extraction + relationship
              graphiti_temporal_layer   inference)
                    │             (Neo4j + LanceDB)
                    ▼
              consolidation_plan_generated
                  (GraphRAG query → merge clusters)
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
  docs_merged              langfuse_traced
  (subagent exec)          (all LLM ops)
```

The 2 core assets are `docs_added_to_cognee` (iterates
`*.md` files in a directory, POSTs each to
`/api/v1/add` with `datasetName`) and `docs_cognified`
(deps on the first, POSTs to `/api/v1/cognify` to trigger
LLM-based entity extraction, 10 min timeout). Three
**GraphRAG query patterns** ride on top: `find_related_docs`
(GRAPH_COMPLETION for related-doc lookup),
`generate_merge_plan` (asks the LLM to find merge clusters
and return file paths + suggested titles), and
`detect_cross_dir_duplicates` (INSIGHTS search across
datasets).

The Cognee v1.0.1+ API simplifies the v0.x
`add → cognify → search` flow into a 2-step
`remember → recall` pattern; `forget(dataset)` removes a
dataset, and `improve()` re-weights graph nodes from
session scores.

**Langfuse tracing** wraps every `cognify()` call so cost +
latency is visible per-dataset (see next section).

See `references/dagster/COGNEE_INTEGRATION.md` for the full
226-line reference: the 8-asset graph diagram, the
`CogneeIngestConfig` Pydantic config, the batch processing
strategy (6 batches × `docs_added_to_cognee` then one
`docs_cognified` with `__all__`), the Langfuse-traced cognify
template, and the v1.0.1 `remember/recall/forget/improve`
API surface.

## Cognee ingestion workflow

The **operator runbook** for ingesting the canonical
36-doc corpus (post-round-1) into Cognee. Three ways to
run, all converging on the same 6-domain dataset layout:

```bash
# Method 1: mise task (local, recommended)
mise run docs:cognee              # all 7 domains
mise run docs:cognee:domain standards  # single domain
mise run docs:cognee:summary      # plan only (no ingest)

# Method 2: script directly (dev/debugging)
uv run python infrastructure/scripts/cognee-ingest-docs.py --all
uv run python infrastructure/scripts/cognee-ingest-docs.py --domain ai-ml
uv run python infrastructure/scripts/cognee-ingest-docs.py --summary --all

# Method 3: GitHub Action / Forgejo workflow (CI)
# .github/workflows/cognee-ingest.yaml
# Schedule: Sunday 04:00 UTC (catches drift)
# Manual: pick a domain or run all from Actions tab
```

The **pre-flight checklist** is: (1) Cognee stack is up
(`docker ps --filter name=cianfhoghlaim-cognee`),
(2) REST API reachable (`curl -sf
http://localhost:8100/health`),
(3) `LLM_API_KEY` set (mise-hydrated from `.env` →
`DEEPSEEK_API_KEY` → `LLM_API_KEY`),
(4) the script exists at
`infrastructure/scripts/cognee-ingest-docs.py`.

The **7 per-domain datasets** are `docs-architecture`
(8 files, 78.9 KB), `docs-data-platform` (4, 57.9 KB),
`docs-agents` (5, 66.0 KB), `docs-ai-ml` (8, 6,059.1 KB —
the largest, absorbed `meaisínfhoghlaim/` + `teanga/`),
`docs-web` (4, 41.1 KB), `docs-product` (5, 52.0 KB),
`docs-standards` (2, 22.6 KB). Total: 36 files, ~6,377 KB.

**Cognify cost** is **~$0.55 per full ingest** (vs ~$6
for the pre-consolidation 2,242-doc corpus) on DeepSeek
V4 Pro. The `docs-ai-ml` domain alone is ~$0.40 (6 MB);
all others are $0.01-0.04.

The 4-stage cognify process is: (1) chunk by `##` headings,
(2) extract entities with DeepSeek V4 Pro, (3) infer
relationships from explicit "A depends on B" prose, (4)
embed with `text-embedding-3-small`, (5) store in Neo4j +
LanceDB. Typical runtime: 2-5 min/domain, 10-15 min for
`docs-ai-ml`.

**Common failures**:
`ConnectionRefusedError` (Cognee not up), `LLMAPIKeyNotSetError`
(check both `opencode.json` cognee env and the container
env — Locket sidecar should hydrate from Infisical),
`graph database error` (Neo4j down), `cognify() hangs >15min`
on `docs-ai-ml` is normal; on smaller datasets, check LLM
quota. To re-cognify from scratch:
`curl -X POST http://localhost:8100/api/v1/prune` then
re-run.

See `references/ingestion/INGESTION.md` for the full 299-line
operator runbook: the pre-flight checklist, the 3 run
methods, the 7-dataset breakdown, the cost-by-domain table,
the 5-step cognify internals, the verification queries
(via MCP + REST), the troubleshooting matrix, the cost
estimate, the maintenance schedule, and the cross-references.

## Cognee→Langfuse tracing

Every Cognee `cognify()` operation involves LLM calls
(entity extraction, relationship inference, summarisation,
GraphRAG search). Without tracing, they're opaque. Langfuse
provides per-operation cost, latency, prompt versioning,
and entity-extraction quality.

The 3-span trace template for one cognify run:

```python
trace = langfuse.trace(name=f"cognee-cognify-{dataset}")
with trace.span(name="document-count"):
    doc_count = get_document_count(dataset)
with trace.span(name="entity-extraction"):
    result = httpx.post("http://localhost:8100/api/v1/cognify",
                        json={"datasets": [dataset]}, timeout=600)
    # span auto-captures tokens + cost
with trace.span(name="extraction-quality"):
    quality = evaluate_extraction_quality(dataset)
    span.score("entity_accuracy", quality["accuracy"])
```

**6 key metrics** to track per cognify run: cognify cost
per dataset (Langfuse traces), entity extraction quality
(RAGAS), cognify latency (span duration), documents
processed per run, LLM token usage, API error rate.

The **Langfuse web UI** at
`https://langfuse.cianfhoghlaim.ie` renders each cognify
run as a waterfall: `cognee-cognify-docs-agents` (2.3s,
$0.42) → `document-count` (0.1s) → `entity-extraction`
(1.8s, 1,847 tokens, $0.35) → `relationship-inference`
(0.3s, 234 edges, $0.05) → `quality-evaluation` (0.1s,
accuracy 0.94). The dashboard view aggregates per-dataset
costs, throughput, average extraction quality, and the
most expensive documents by token count.

**3 recommended alerts**:
`cognify_cost > $10/run` (model fallback or error retries),
`extraction_quality < 0.85` (prompt update or model change
needed), `cognify_latency > 300s` (overloaded LLM API or
Neo4j connection issues).

See `references/langfuse/LANGFUSE_OBSERVABILITY.md` for
the full 189-line reference: the `opencode.json` MCP
config, the 3-span trace template, the
`track_cognify_costs()` aggregation function, the CCC
indexing trace pattern, the 6 key metrics table, the web
UI trace view, the dashboard view, and the 3 alerts.

## KCG MCP inventory

9 MCP servers are wired in `opencode.json` to give every
agent a tool surface covering cognition, code search,
tracing, web scraping, browser automation, SQL analytics,
and secret management:

| Server | Port | MCP package | Agent tools |
|:--|:--|:--|:--|
| `cocoindex-code` | — | `ccc mcp` | `cocoindex-code_search(query, limit, languages, paths)` |
| `cognee` | 8100 | `cognee-mcp` | `cognee_add`, `cognee_cognify`, `cognee_search` |
| `graphiti` | 8000 | `graphiti_core.mcp` | `graphiti_search`, `graphiti_get_node`, `graphiti_get_edges` |
| `langfuse` | — | `@langfuse/mcp` | `langfuse_get_trace`, `langfuse_get_traces`, `langfuse_get_prompt` |
| `motherduck` | — | `mcp-server-motherduck` | `motherduck_execute_query`, `motherduck_list_tables`, `motherduck_list_databases` |
| `firecrawl` | — | `firecrawl-mcp` | `firecrawl_scrape`, `firecrawl_search`, `firecrawl_crawl`, `firecrawl_map` |
| `browserbase` | — | `@browserbasehq/mcp` | `browserbase_navigate`, `browserbase_act`, `browserbase_extract`, `browserbase_observe` |
| `chrome` | — | `chrome-devtools-mcp` | `chrome_navigate_page`, `chrome_take_screenshot`, `chrome_take_snapshot`, `chrome_evaluate_script` |
| `infisical` | 8081 | `@infisical/mcp` | `infisical_get_secret`, `infisical_list_secrets`, `infisical_create_secret` |

All sensitive config (API keys, project IDs) uses the
`infisical://dev-baile/...` URI pattern — never plain
secrets on disk. The mise directory hooks hydrate
`INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET`,
`INFISICAL_PROJECT_ID` from `.env`.

**Activation flow**: opencode starts → reads
`opencode.json` → for each `"enabled": true` server, resolves
Infisical URI refs → installs package if needed (bunx/uvx
auto-install) → starts subprocess → registers tools.

**Adding a new MCP server**: 5 steps — add the block to
`opencode.json` under `"mcp"`, add secrets to Infisical
vault, add the Infisical reference to `.infisical.env`,
run `bun run secrets:init` to hydrate, restart opencode.

See `references/mcp/MCP_SERVERS.md` for the full 228-line
reference: the server inventory table, the per-server
`opencode.json` config (cognee, CCC, Graphiti, Langfuse,
MotherDuck, Firecrawl, Browserbase, Chrome, Infisical), the
per-server tool listing, the MCP activation flow, and the
5-step "add a new server" procedure.

## Cognee 7-phase workflow

The end-to-end cognition pipeline that takes raw `.md` files
to a queryable, time-aware, agent-accessible knowledge
graph:

```
PHASE 1: INDEX      → CCC builds semantic code index
PHASE 2: INGEST     → Cognee ingests .md files by dataset
PHASE 3: COGNIFY    → Cognee builds knowledge graph (LLM)
PHASE 4: TEMPORAL   → Graphiti adds bi-temporal layer
PHASE 5: ANALYZE    → GraphRAG queries identify merge clusters
PHASE 6: CONSOLIDATE → Subagents merge scattered docs
PHASE 7: MONITOR    → Langfuse + Dozzle + Beszel
```

**Phase 1** runs `bun run ccc:index` (~35 MB SQLite db).
**Phase 2** ingests each `docs/<subtree>` into a Cognee
dataset via `cognee_http_ingest.py`. **Phase 3** triggers
the LLM entity extraction via `POST /api/v1/cognify` with
all 6 datasets and `runInBackground: true`; cost is ~$6 for
2,242 documents. **Phase 4** layers Graphiti on the same
Neo4j instance for bi-temporal queries like "what were the
prerequisite chains before the 2023 reform?".

**Phase 5** is the GraphRAG analysis: `GRAPH_COMPLETION`
asks for "find groups of documents that discuss the same
topics and should be merged into single comprehensive
documents" → produces a `CONSOLIDATION_PLAN.md`. `INSIGHTS`
asks for "documents in the wrong directory based on
content vs directory name". `SUMMARIES` gives a top-level
topic overview.

**Phase 6** fans out the merges to subagents: subagent 1
handles `docs/agents/` + `docs/context/`; subagent 2
handles `docs/data_engineering/` + `docs/bonneagar/`;
subagent 3 handles `docs/meaisínfhoghlaim/`; subagent 4
handles `docs/web/`. Each reads its section of the plan,
writes a single merged document with a `## Merged From`
header, and replaces the originals with `MERGED INTO` stubs.

**Phase 7** monitors via 3 surfaces: **Langfuse** at
`https://langfuse.cianfhoghlaim.ie` (token + cost + latency
per cognify), **Dozzle** at `https://dozzle.cianfhoghlaim.ie`
(container logs filtered by `cognee`),
**Beszel** at `https://beszel.cianfhoghlaim.ie` (CPU during
cognify, memory for Neo4j graph, disk for LanceDB index).
Verify with `bun run ccc:index && bun run ccc:search "..."`.

The whole workflow automates as a single Dagster `job`:
`docs_added_to_cognee → docs_cognified →
graphiti_temporal_layer → consolidation_plan_generated →
execute_merges`. Schedule: weekly CCC re-index
(`0 2 * * 0`), monthly cognify (`0 3 1 * *`), daily spec
validate (`0 8 * * *`).

See `references/workflow/WORKFLOW.md` for the full 204-line
reference: the 7-phase overview, the per-phase commands +
outputs, the GraphRAG query templates, the subagent fan-out
pattern, the 3 monitoring surfaces, the Dagster job
definition, and the 3 cron schedules.

## Logfire/MLflow/Langfuse/Ragas patterns

The 11 canonical observability patterns from the
round-1 `docs/context/01-patterns/OBSERVABILITY.md` (442
lines), grouped by tool:

**Logfire** (3 patterns): FastAPI instrumentation
(`logfire.instrument_fastapi(app)`, `LOGFIRE_TOKEN`/
`LOGFIRE_PROJECT_NAME`/`LOGFIRE_ENVIRONMENT` env vars,
`logfire.span()` context managers), Langfuse `@observe` /
`logfire.instrument_*` decorators (auto-captures
`logfire.info(msg, **kwargs)` calls with structured fields), and
a custom `trace_pydantic_agent` decorator that tags
`agent.name`/`agent.type`/`agent.duration_ms`/`agent.status`
and uses `logfire.span()` for input/output data.

**MLflow** (2 patterns): experiment tracking
(`set_tracking_uri`, `set_experiment`, `start_run` +
`log_params`/`log_metrics`/`log_model` + `register_model`),
and model registry (`MlflowClient.transition_model_version_stage`
to promote to Staging/Production/Archived + `load_production_model`
via `models:/{name}/Production` URI).

**Langfuse** (2 patterns): cost tracking
(`@observe(as_type="generation")` auto-captures
input/output tokens, latency, cost; nested
`langfuse_context.observe(name=)` for retrieval + generation
spans), and prompt management
(`langfuse.get_prompt(name=, version=, type=)` returns
`.compile()`; chat prompts compile with `**variables`).

**Ragas** (3 patterns): evaluation
(`evaluate(dataset, metrics=[faithfulness, answer_relevancy,
context_precision, context_recall])` from a `datasets.Dataset`),
continuous evaluation as a Dagster `asset`
(`rag_quality_check` logs failures when any metric drops
below threshold; `@asset_check(asset=rag_quality_check)`
gates the asset on `faithfulness >= 0.8`), and
MLflow-tracked evaluation (log RAGAS metrics to MLflow
`run_name="rag-eval"` for longitudinal tracking).

**structlog** (1 pattern): unified JSON-or-pretty logging
(`configure_logging(service_name, env)` adds
`merge_contextvars`/`add_log_level`/`TimeStamper`/
`StackInfoRenderer`/`format_exc_info`, then either
`JSONRenderer` for prod or `dev.ConsoleRenderer` for dev).

**6 integration points** in the matrix: Logfire→FastAPI
(instrument_fastapi middleware), Langfuse→agents (`@observe`/
`logfire.instrument_*`), MLflow→ training (`log_*` + registry),
Langfuse→LLM calls (`@observe`), Ragas→RAG pipeline (eval
metrics), structlog→all services (unified JSON ingest).

**6 common mistakes** to avoid: no LLM cost tracking
(add Langfuse), missing trace context (use propagation
headers), no RAG evaluation (run Ragas regularly), logs
without structure (use structlog + JSON), no experiment
tracking (log all training runs), silent agent failures
(add error tracing to all agents).

See `.agents/skills/{langfuse,mlflow,ragas,pydantic-ai}/SKILL.md`
for the per-tool deep dives; the 4 critical constraints are
inlined above, the 6 common mistakes are summarised at the end
of this file, and the implementation checklist is the
"Observability checklist" section above.

## 2026-06 update: Langfuse v3 + MLflow GenAI + RAGAS trace-based

The 4 observability tools that KCG agents use (Langfuse, MLflow, RAGAS, Logfire) all shipped major updates in 2026.

### Langfuse v3 (released 2026-05)

The v3 release is what KCG runs at `langfuse.cianfhoghlaim.ie`. Key features for KCG agents:

- **Prompt management v2** — version + A/B test prompts from the Langfuse UI; the agent runtime picks up new prompts at the next request without a restart
- **Cost tracking per model** — separate cost lines for `gpt-4o`, `claude-sonnet-4.5`, `gemini-2.0-flash`, `llama-swap` (the local M4 model)
- **Session grouping** — group 5 agent turns into 1 user session, so the dashboard shows the cost + latency for the whole conversation
- **Dataset + experiment tracking** — link every LLM call to a dataset version + an experiment run, so you can reproduce any past agent trace

The KCG pattern: every agent call goes through LiteLLM with `langfuse_callback` enabled, so the Langfuse trace is populated automatically.

### MLflow GenAI evaluation (the 2026-06 feature)

MLflow added a GenAI evaluation mode in 2026 that complements Langfuse:

- `mlflow.evaluate()` with the `genai` mode runs the agent against a labelled dataset
- Tracks quality metrics (faithfulness, answer relevance, context precision) per model
- Integrates with the MLflow model registry: a model can only be promoted to "Production" if it passes the eval gate

The KCG pattern: nightly batch eval of the `agents/curriculum_agent` against the `cianfhoghlaim_eval_v3` dataset, logged to MLflow. The Dagster asset `mlflow_eval_curriculum` (in `agents/meaisinfhoghlaim/dagster_defs/`) is the entry point.

### RAGAS trace-based metrics

RAGAS now ships trace-based metrics that work on the Langfuse trace (not just the dataset):

- **Faithfulness** — does the answer stay grounded in the retrieved context?
- **Answer relevance** — does the answer address the question?
- **Context precision** — is the retrieved context actually relevant?
- **Context recall** — is the retrieved context complete?

The KCG pattern: the RAGAS-as-Dagster-asset-check pattern runs these on every `cognee.remember` call. The asset check `ragas_faithfulness_check` in `orchestration/asset_checks.py` fails the asset materialisation if faithfulness drops below 0.85.

### Logfire MCP (2026-06)

Pydantic Logfire now ships an MCP server that exposes traces to the agent runtime. KCG does not yet wire it, but the skill is in `.agents/skills/pydantic-ai/SKILL.md` for future use.

### Pair this skill with

- `pydantic-ai/SKILL.md` — the agent framework that wires Logfire
- `langfuse/SKILL.md` — the Langfuse detail
- `mlflow/SKILL.md` — the MLflow detail
- `ragas/SKILL.md` — the RAGAS detail

---

## Agent-platform cluster (added 2026-06-30)

The agent-platform group now has 3 agent surfaces that all
trace to Langfuse:

| Surface | Stack | Stack port | Trace |
|:--|:--|:--|:--|
| Channel-fanout gateway | openclaw | 18789 | via OTLP/HTTP to `langfuse.cianfhoghlaim.ie` |
| Browser IDE | openchamber | 3000 | via OTLP/HTTP to `langfuse.cianfhoghlaim.ie` |
| Autonomous agent runtime | hermes | 9119 | via OTLP/HTTP to `langfuse.cianfhoghlaim.ie` |

All 3 surfaces route LLM through `litellm` (port 4000). The
`embedding_model_health` asset check polls LiteLLM's
`/health/liveliness` every 5 min and fails when the rolling avg
completion latency > 500 ms (degraded LiteLLM is the canary for
all 3 surfaces).
