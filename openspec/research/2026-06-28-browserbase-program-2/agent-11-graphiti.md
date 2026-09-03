# Agent 11 — Graphiti (`graphiti-core` ≥ 0.29.2)

**Date:** 2026-06-28
**Phase:** BrowserBase Program 2 (Wave 1, Agent 11 of 25)
**Budget:** ~200 BrowserBase credits
**Subagent:** research

## TL;DR

**Graphiti** is the bi-temporal **context graph** engine from Zep (Apache‑2.0, `getzep/graphiti`, PyPI `graphiti-core 0.29.2` released 2026‑06‑08, RC line `0.30.0rc5`). It fuses semantic embeddings + BM25 full‑text + graph traversal into a single ranked result, with **explicit bi‑temporal tracking** (valid_at + recorded_at) and **automatic fact invalidation** — i.e. when an entity fact changes, the old `EntityEdge` is closed (`invalid_at` set, `valid_at` preserved) rather than deleted, giving point‑in‑time queries for free. The Cianfhoghlaim canonical pattern uses **`graphiti-core` + `FalkorDriver` (FalkorDB 1.1.2 with the `vector.so` loadable) + Dragonfly episode cache**; current production reference code lives at `cianfhoghlaim/core/cognee/_graph/graphiti_client.py` and the 6‑file stack at `cianfhoghlaim/stacks/graphiti/`. Performance: **94.7 % LoCoMo @ 155 ms**, **90.2 % LongMemEval @ 162 ms** (per the project README).

## Code

### Canonical `add_episode` API (verbatim from `getzep/graphiti` `graphiti_core/graphiti.py`)

```python
async def add_episode(
    self,
    name: str,
    episode_body: str,
    source_description: str,
    reference_time: datetime,                                    # ← event-time / valid_at
    source: EpisodeType = EpisodeType.message,                   # text | message | json
    group_id: str | None = None,                                 # namespace / database
    uuid: str | None = None,
    update_communities: bool = False,
    entity_types: dict[str, type[BaseModel]] | None = None,     # prescribed ontology
    excluded_entity_types: list[str] | None = None,
    previous_episode_uuids: list[str] | None = None,
    edge_types: dict[str, type[BaseModel]] | None = None,
    edge_type_map: dict[tuple[str, str], list[str]] | None = None,
    custom_extraction_instructions: str | None = None,
    saga: str | SagaNode | None = None,                          # ← v0.29+ incremental summarisation
    saga_previous_episode_uuid: str | None = None,
) -> AddEpisodeResults:                                          # episode, episodic_edges, nodes, edges, communities, community_edges
```

### Cianfhoghlaim canonical init (FalkorDB production stack + Lite fallback)

```python
# cianfhoghlaim/core/cognee/_graph/graphiti_client.py:58
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
import redislite  # for the episode-cache fallback

# production: FalkorDB compose stack at falkordb://falkordb:6379
falkor = FalkorDriver(host="falkordb", port=6379, database="default_db")

# episode cache: Dragonfly at redis://dragonfly:6379/0  (or redislite fallback locally)
cache = redislite.Redis(serverconfig={"port": "6390"})

graphiti = Graphiti(
    graph_driver=falkor,
    cache_client=cache,
    llm_client=OpenAIClient(),            # default; LiteLLM-routed in KCG
    embedder=OpenAIEmbedder(),
    cross_encoder=OpenAIRerankerClient(),
)
await graphiti.build_indices_and_constraints(delete_existing=False)
```

### Five edge types & four node types

| Class              | Type   | Lifetime semantics                                           |
|:--|:--|:--|
| `EntityEdge`       | RELATES_TO | `valid_at` (event time) + `invalid_at` (None ⇒ still true) + `created_at` (record time) |
| `EpisodicEdge`     | MENTIONS  | Provenance: Entity ↔ Episodic; survives as long as episode exists |
| `CommunityEdge`    | IN_COMMUNITY | Leiden / label-propagation communities, rebuilt by `update_communities=True` |
| `HasEpisodeEdge`   | HAS_EPISODE | Saga → Episode (forward chain) |
| `NextEpisodeEdge`  | NEXT_EPISODE | Saga → next Episode (chronological chain) |
| `EntityNode`       | — | mutable `summary` field, regenerated on every episode |
| `EpisodicNode`     | — | ground-truth source stream; `content` is the raw `episode_body` |
| `CommunityNode`    | — | `summary` + `name`; set rebuilt on community update |
| `SagaNode`         | — | v0.29+; `last_summarized_at` (wall-clock watermark) + `last_summarized_episode_valid_at` (temporal watermark) |

### Fact extraction flow (per `_extract_and_resolve_edges`)

1. `extract_edges(clients, episode, extracted_nodes, previous_episodes, …)` — single LLM call against the prompt library that produces `EntityEdge` candidates
2. `resolve_edge_pointers(extracted_edges, uuid_map)` — in-memory rewrite of dangling node UUIDs
3. `resolve_extracted_edges(…)` returns `(resolved, invalidated, new)` — **invalidated** edges get `invalid_at = reference_time` (event-time)
4. Embeddings batched in `create_entity_edge_embeddings` (semantic similarity later used by `EDGE_HYBRID_SEARCH_*`)

### Episode types

| `EpisodeType` | `episode_body` shape | Use |
|:--|:--|:--|
| `text`  | arbitrary prose | OCR dumps, articles, docs |
| `message` | `"speaker: text\n…"` multi-turn | chat logs, support transcripts |
| `json` | `json.dumps(dict)` | structured product / catalog updates |

### 15 search recipes (`graphiti_core/search/search_config_recipes.py`)

```
COMBINED_HYBRID_SEARCH_RRF | _MMR | _CROSS_ENCODER
EDGE_HYBRID_SEARCH_RRF | _MMR | _NODE_DISTANCE | _EPISODE_MENTIONS | _CROSS_ENCODER
NODE_HYBRID_SEARCH_RRF | _MMR | _NODE_DISTANCE | _EPISODE_MENTIONS | _CROSS_ENCODER
COMMUNITY_HYBRID_SEARCH_RRF | _MMR | _CROSS_ENCODER
```

Rerankers: `OpenAIRerankerClient` (default, logprobs), `GeminiRerankerClient` (gemini-2.5-flash-lite), `BGERerankerClient` (`BAAI/bge-reranker-v2-m3` via `sentence-transformers`).

### KCG in-tree files

| Path | Status |
|:--|:--|
| `cianfhoghlaim/core/cognee/_graph/graphiti_client.py` | **current** — wraps `graphiti_core.Graphiti` with FalkorDB + Lite fallback (per `refactor-dlt-dagster-2026-stack-align` change) |
| `cianfhoghlaim/stacks/graphiti/` | 6‑file GOLD_STANDARD stack (`compose.yaml`, `blueprint.yaml`, `pangolin.yaml`, `sidecar.yaml`, `secrets.env`, `README.md`) |
| `cianfhoghlaim/stacks/falkordb/` | FalkorDB 1.1.2 + `vector.so` loadable + `falkordb-data` named volume |
| `cianfhoghlaim/tests/_tuatha/test_graphiti_integration.py` | Integration test for the wrapper |
| `cianfhoghlaim/docs/legacy/crypteolas/graphiti/__init__.py` | Legacy placeholder (kept for backward navigation post‑v4 consolidation) |
| `cianfhoghlaim/docs/legacy/crypteolas/knowledge_graph/graphiti_client.py` | Legacy alternate wrapper |
| `cianfhoghlaim/docs/legacy/crypteolas/api/services/knowledge_graph_service.py:53‑80` | Legacy `add_episode(content, source, source_type, metadata)` shim — **drift**: signature does not match upstream `graphiti_core 0.29` |
| `cianfhoghlaim/docs/legacy/crypteolas/pipelines/defs/knowledge/graphiti_temporal.py` | Legacy Dagster asset wrapper |

## Env

| Env var | Value | Source | Notes |
|:--|:--|:--|:--|
| `OPENAI_API_KEY` | `infisical://dev-baile/openai/api_key` | Locket | Default LLM + embedder (KCG keeps this for prod) |
| `FALKORDB_HOST` | `falkordb` | compose env | `compose.yaml` `falkordb` service |
| `FALKORDB_PORT` | `6379` | compose env | Redis-protocol + Bolt multiplexed |
| `FALKORDB_URI` | `falkordb://falkordb:6379` | KCG convention | Read by `GraphitiClient.connect()` default |
| `FALKORDB_LITE_PATH` | `/tmp/falkordb_lite` | KCG convention | Embedded fallback when compose unreachable |
| `DRAGONFLY_URL` | `redis://dragonfly:6379/0` | compose env | Episode cache (separate Redis instance) |
| `NEO4J_URI` (fallback) | `bolt://neo4j:7687` | Locket | OSS dev fallback only |
| `SEMAPHORE_LIMIT` | `10` (default) | Graphiti default | Lower if LLM 429s; raise if provider allows higher throughput |
| `GRAPHITI_TELEMETRY_ENABLED` | unset (default ON) | PostHog | Opt-out via `export GRAPHITI_TELEMETRY_ENABLED=false` |
| `USE_PARALLEL_RUNTIME` | `true` | Neo4j Enterprise | Only used if switching to Neo4j |

## CCC anchors

* `cianfhoghlaim/core/cognee/_graph/graphiti_client.py` — current canonical wrapper
* `cianfhoghlaim/stacks/graphiti/compose.yaml` — 6‑file GOLD_STANDARD
* `cianfhoghlaim/stacks/falkordb/compose.yaml` — backend with `vector.so`
* `openspec/specs/agent-memory-systems/spec.md` — 5‑backend memory layer (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph)
* `openspec/specs/oideachais-storage/spec.md` — `### Requirement: Graphiti uses FalkorDB for persistence + Dragonfly for episode cache`
* `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-07-falkordb-graphiti-dragonfly-risingwave.md` — sibling research artifact
* `openspec/changes/refactor-dlt-dagster-2026-stack-align/` — Phase 6 deletes `sruth/oideachais/graph/temporal.py` (hand-rolled) and wires the real `graphiti_core`
* `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:36-47` — Graphiti add_episode spec

Search terms: `"Graphiti"`, `"add_episode"`, `"FalkorDriver"`, `"bi-temporal"`, `"entity_edge"`, `"search_config_recipes"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025‑07 | `graphiti-core 0.17.0` introduced the `graph_driver` kwarg — KCG patterns pre‑0.17 used the positional `Graphiti(uri, user, password)` shape |
| 2025‑11 | Initial FalkorDB deploy (per P1B‑07) |
| 2026‑01 | Dragonfly episode cache added |
| 2026‑03 | Wired 12 leabharlann episodes (one per `leabharlann/` subdir) |
| 2026‑04 | RisingWave CDC → Iceberg → FalkorDB |
| 2026‑05 | `graphiti_core 0.5` + `FalkorDB Lite` embedded mode landed — KCG `graphiti_client.py` adopted Lite as the local fallback (closes the prior OSS-only‑Neo4j gap) |
| 2026‑05 | Cross-archive edge types: cites / builds-on / contradicts (3 total) |
| 2026‑06‑28 | `graphiti-core 0.29.2` released (current stable); v0.29+ adds **Saga** incremental summarisation with bi‑temporal watermarks |
| 2026‑06‑28 | **Legacy drift**: `cianfhoghlaim/docs/legacy/crypteolas/api/services/knowledge_graph_service.py:53-80` still uses the pre-0.17 shim signature `add_episode(content, source, source_type, metadata)` — does NOT match upstream 0.29 |
| 2026‑06‑28 | **Legacy drift**: `cianfhoghlaim/docs/legacy/crypteolas/knowledge_graph/graphiti_client.py` and `…/pipelines/defs/knowledge/graphiti_temporal.py` are duplicated by the canonical `core/cognee/_graph/graphiti_client.py` |

## Anti-patterns

1. **Don't import the legacy shim.** `crypteolas/api/services/knowledge_graph_service.py:add_episode` predates the 0.17 `graph_driver` API and silently returns `{"success": False, "error": "Graphiti not available"}` on every call. Use `core/cognee/_graph/graphiti_client.py:GraphitiClient.connect().add_episode(name=…, body=…, source_description=…)`.
2. **Don't use Kuzu.** Deprecated in 0.29 (upstream Kuzu is unmaintained); `pip install graphiti-core[kuzu]` still works but emits `DeprecationWarning`. KCG policy: Neo4j for OSS dev, FalkorDB for prod.
3. **Don't bypass `build_indices_and_constraints`.** Without it, bi-temporal range queries become O(N²) over `EntityEdge.valid_at` + `invalid_at`; the unique constraints also dedupe duplicate facts on `add_episode`.
4. **Don't use `add_episode` in hot loops.** The fast path is `add_episode_bulk(RawEpisode(...), …)` — bulk skips per-fact invalidation, so use only for backfill of an empty graph.
5. **Don't set `SEMAPHORE_LIMIT` high on local LLMs.** Ollama, llama.cpp, vLLM often accept `json_schema` in the request but don't enforce it; raise `structured_output_mode="json_object"` instead and keep concurrency ≤ 5.
6. **Don't store raw episode bodies in prod.** Set `store_raw_episode_content=False` if the episode is re-derivable from upstream sources (saves ~40 % storage on large OCR corpora).
7. **Don't assume `group_id == driver database`.** v0.17+ clones the driver when `group_id != self.driver._database`; passing mismatched values creates a new database connection each call. Use one driver per tenant.
8. **Don't pick Gemini reranker on long episodes.** `gemini-2.5-flash-lite` is cost-optimised but truncates past ~8 K tokens; use `OpenAIRerankerClient` for full-corpus leabharlann episodes.
9. **Don't forget `GRAPHITI_TELEMETRY_ENABLED=false` in compose.** PostHog PostHog-cdn is reachable from the control plane but emits a one‑shot call per `Graphiti()` init.
10. **Don't co‑run FalkorDB + Neo4j in the same environment.** Graphiti's `SagaNode` schema is driver‑specific (the `_get_or_create_saga` Cypher is hand‑written and not shared with the FalkorDB equivalent via `graph_operations_interface`).

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Backend driver | **FalkorDriver** | Vector + graph in one DB; `vector.so` loadable covers all of Graphiti's similarity needs; multi-tenant RESP isolation per `database` arg |
| OSS dev fallback | **Neo4j 5.26** | Most mature driver; widely available locally; required for `USE_PARALLEL_RUNTIME` if performance matters |
| Offline dev fallback | **FalkorDB Lite** (`falkordb_lite` extra) | Zero-config embedded; no port collisions; per `refactor-dlt-dagster-2026-stack-align` Phase 6 |
| Episode cache | **Dragonfly** | 5× faster than Redis; Redis-protocol compatible; separate instance on port 6379 (KCG uses a non-default port for Dragonfly to keep it distinct) |
| Episode source format | **`EpisodeType.text`** for OCR dumps, **`EpisodeType.json`** for catalog updates | text is the natural language ingest path; json bypasses entity extraction prompts and is 10× faster per episode |
| Default LLM | **OpenAI** (`gpt-4o-mini` via LiteLLM `minimax` alias in KCG) | Most reliable `structured_output_mode="json_schema"` |
| Embedder | **OpenAI `text-embedding-3-small`** (dim 1536) | Multilingual coverage for Irish / Welsh / Scottish Gaelic |
| Reranker | **OpenAIRerankerClient** | Default; cost-effective logprobs reranker; swap to `BGERerankerClient` if avoiding OpenAI at query time |
| Search recipe | **`EDGE_HYBRID_SEARCH_NODE_DISTANCE`** for entity queries, **`COMBINED_HYBRID_SEARCH_CROSS_ENCODER`** for broad queries | Node-distance reranking adds graph locality that BM25 + cosine misses |
| Cross-archive edge taxonomy | **cites / builds-on / contradicts** | 3 typed edges per `cognify/rules/falkordb_edge_types.py` — matches academic citation graph semantics |
| Saga watermarks | `last_summarized_at` = wall-clock; `last_summarized_episode_valid_at` = temporal | Per upstream 0.29+ design: wall-clock is the *filter*, event-time is the *public watermark* |
| Bulk vs single ingest | `add_episode_bulk` for backfill, `add_episode` for live | Bulk skips invalidation; live performs it |

## §8 Refactor opportunities

1. **Delete the legacy shim at `cianfhoghlaim/docs/legacy/crypteolas/api/services/knowledge_graph_service.py:53`.** The `add_episode(content, source, source_type, metadata)` signature was correct for `graphiti-core` < 0.17 but now silently fails on every call. Either delete the file outright (it's under `docs/legacy/`) or rewrite to delegate to `core/cognee/_graph/graphiti_client.py:GraphitiClient`.
2. **De‑duplicate the three Graphiti wrappers.** `docs/legacy/crypteolas/knowledge_graph/graphiti_client.py`, `docs/legacy/crypteolas/knowledge_graph/graphiti/`, and `docs/legacy/crypteolas/pipelines/defs/knowledge/graphiti_temporal.py` are all subsumed by `core/cognee/_graph/graphiti_client.py`. Refactor: keep only one canonical import path and have legacy re‑export from it.
3. **Add type stubs for `EpisodeType` and `EntityEdge` in the KCG `.env.example`.** The 5 typed edge / 4 typed node surface area is the most likely drift point between upstream 0.29.x and 0.30 (SagaNode watermarks already added two fields in 0.29). Add a `mypy --strict-reexport` check to the CI for `core/cognee/_graph/`.
4. **Promote `SagaNode` to first-class KCG usage.** The v0.29+ saga API (`summarize_saga(saga_id)` with bi-temporal watermarks) is currently un-used in KCG. Plan: one saga per leabharlann subdir (12 sagas total), so the `add_episode` flow records into a per-subdir summarization chain.
5. **Drop the `USE_LOCAL_SCRAPES` Graphiti integration if it still references `stedding/ingest_queue`.** KCG already routes text episodes through the `core/cognee/_graph/graphiti_client.py` path; the fallback cache should only apply to DLT text ingestion, not bi-temporal episodes.
6. **Replace `graph_driver=falkor` + `cache_client=dragonfly` positional coupling** with a single `graphiti_pool` keyed on `group_id`. v0.17+ already clones the driver when `group_id != driver._database`; a tenant-aware pool removes the O(N) driver creation cost from `add_episode`.
7. **Add a `graphiti eval` Dagster asset_check** using RAGAS `faithfulness` + `context_recall` against a fixed leabharlann test set. Upstream's 94.7 % LoCoMo number is their benchmark, not ours; we need a KCG-specific floor.
8. **Wire `group_id` to the `leabharlann/` subdir path.** Right now the 12 episodes share a default group; per-subdir isolation (group_id = `leabharlann/<subdir>`) would let the saga watermarks live at subdir granularity, matching the `cognify/rules/graphiti_episodes.py` taxonomy.
9. **Migrate to `graphiti-core 0.30.0` when it ships.** RC5 is on PyPI (2025-09-30); stable will likely add the `Kuzu → Kuzu-lite` rename and possibly a driver-level streaming API. Track via `upstream-package-monitoring` change.
10. **Add a `GRAPHITI_TELEMETRY_ENABLED=false` line to `infrastructure/stacks/graphiti/secrets.env`.** Default ON in upstream; KCG policy is OFF (per `secrets-management` skill: opt-out by default for telemetry-emitting deps).