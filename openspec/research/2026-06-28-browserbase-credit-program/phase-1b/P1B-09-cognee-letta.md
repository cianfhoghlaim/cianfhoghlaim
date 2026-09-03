# P1B-09 — Cognee + Letta (Phase 1B, Vector + Graph + Storage)

**Date:** 2026-06-28
**Phase:** 1B (Vector + Graph + Storage Tier)
**Budget:** ~180 credits
**Subagent:** research

## TL;DR

Cognee is the **knowledge graph memory layer** for the Cianfhoghlaim agent fleet. It indexes `.md` documentation + BAML-extracted structured data into a Postgres + Neo4j backend, with 6 typed datasets (aistear, primary, junior_cycle, senior_cycle, tertiary, cross_stage). Letta is the **agent persistent memory layer** that gives agents stateful, long-term memory across sessions.

The canonical Cianfhoghlaim pattern uses Cognee for **document cognition** (what the codebase knows) and Letta for **agent memory** (what each agent remembers).

## Code

| Path | Purpose |
|:--|:--|
| `stacks/cognee/compose.yaml` | Cognee web + cognee-postgres + Neo4j (port 8100) |
| `stacks/cognee/secrets.env` | Locket-injected (COGNEE_API_KEY, LLM_MODEL=minimax) |
| `oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py` | Cognee Python client (cognify + search) |
| `stacks/letta/compose.yaml` (planned, Tier 2) | Letta agent memory server |
| `cognify/cognee_integration/` | 7 graph model files (one per Cognee dataset type) |
| `cognify/rules/cognee_datasets.py` | Lists 6 active datasets |

**Canonical Cognee cognify** (`oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py`):

```python
import cognee
from cognee import SearchType

async def cognify_oideachais():
    """Cognify the oideachais documentation into the 6 typed datasets."""
    # 1. Add documentation files
    await cognee.add("docs/oideachais/", dataset_name="oideachais.primary")
    await cognee.add("docs/baml/", dataset_name="oideachais.cross_stage")
    await cognee.add("docs/cognify/", dataset_name="oideachais.tertiary")
    
    # 2. Cognify (graph extraction + embedding)
    await cognee.cognify()
    
    # 3. Search across datasets
    results = await cognee.search(
        "What BAML extraction patterns are used for curriculum docs?",
        query_type=SearchType.GRAPH_COMPLETION,
    )
    return results
```

**Canonical Cognee graph model** (`cognify/cognee_integration/graph_models/oideachais_primary.py`):

```python
from cognee.infrastructure.databases.graph import get_graph_engine
from cognee.modules.graph.models import Edge, Node

# Dataset-specific node types
class CurriculumNode(Node):
    label: str  # "Subject", "Topic", "LearningObjective", "Assessment"
    name: str
    properties: dict

class AssessmentEdge(Edge):
    relationship_type: str  # "TESTS", "BUILDS_ON", "PREREQUISITE_FOR"
    source_node_id: str
    target_node_id: str
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `COGNEE_API_URL` | `http://cognee:8100` | Locket |
| `COGNEE_API_KEY` | `infisical://dev-baile/cognee/api_key` | Locket |
| `LLM_MODEL` | `minimax` (Phase 0.4 default) | Locket |
| `LLM_API_KEY` | `no-key-needed` (litellm handles auth) | Locket |
| `LLM_PROVIDER` | `openai` | Locket |
| `LLM_BASE_URL` | `http://litellm:4000/v1` | Locket |
| `COGNEE_POSTGRES_PASSWORD` | `infisical://dev-baile/cognee/postgres_password` | Locket |

## CCC anchors

`stacks/cognee/compose.yaml` · `oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py` · `cognify/cognee_integration/graph_models/` · `cognify/rules/cognee_datasets.py`

Search terms: `"cognee.cognify"`, `"SearchType.GRAPH_COMPLETION"`, `"cognee.search"`, `"graph_models"`.

## Drift log

| Date | Event |
|--:|:--|
| 2025-08 | Initial Cognee deploy (Neo4j backend) |
| 2025-12 | Added Postgres backend (replacement for the relational layer) |
| 2026-01 | Wired BAML extraction → Cognee cognify |
| 2026-03 | Added 6 typed datasets (per educational stage) |
| 2026-04 | Replaced Neo4j with Postgres unified provider |
| 2026-06 | Phase 0.4: switched default LLM_MODEL to `minimax` |

## Anti-patterns

1. Don't cognify the same content into multiple datasets — dedupe first
2. Don't use LLM for embeddings directly — use the embedding model via LiteLLM
3. Don't skip `build_indices_and_constraints` — bi-temporal queries need them
4. Don't store Cognee data in SQLite — use Postgres for multi-writer
5. Don't use `query_type=SearchType.RAG_COMPLETION` for cross-archive questions — use `GRAPH_COMPLETION`

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| LLM | `minimax` (Phase 0.4 default) | 7-tier fallback |
| Embeddings | `openai/text-embedding-3-small` (via LiteLLM) | Multilingual support |
| Graph backend | Postgres unified (Neo4j fallback for prod) | Simpler ops |
| Datasets | 6 (per educational stage) + 3 (leabharlann) = 9 total | Per-stage scope |
| Memory | Letta (planned) | Cross-session agent state |

## Files to read next

`stacks/cognee/compose.yaml` · `oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py` · `cognify/cognee_integration/graph_models/` · `cognify/rules/cognee_datasets.py` · `.agents/skills/cognee/SKILL.md` · `.agents/skills/agent-memory-systems/SKILL.md`
