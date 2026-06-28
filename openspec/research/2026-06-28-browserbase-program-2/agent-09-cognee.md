# Agent 09 — Cognee (knowledge-graph memory)

**Date:** 2026-06-28
**Agent:** 09 of 25
**Package:** topoteretes/cognee (v1.2.2 released 2026-06-26)
**PyPI:** https://pypi.org/project/cognee/
**Docs:** https://docs.cognee.ai
**BrowserBase credits used:** ~12 (Firecrawl equivalent; kept BrowserBase session open for one compose overlay, fell back to Firecrawl for markdown reliability)

## TL;DR

Cognee 1.x is the canonical knowledge-graph memory layer for the Cianfhoghlaim
agent fleet. The package has shipped a **major v1.0 API redesign**
(`remember` / `recall` / `forget` / `improve` / `serve` / `push` replacing the
legacy `add` / `cognify` / `search` / `memify` pipeline). All
`cognee_integration/*.py` helpers in `cianfhoghlaim/cognify/` and
`core/memory/memory/cognee_service.py` are pinned to the **legacy v0.x API**
and will need to be migrated. The default backend has also drifted
**Neo4j → Kuzu** (file-based, single-process; current compose.yaml uses the
experimental `USE_UNIFIED_PROVIDER=pghybrid` hack instead of the recommended
`GRAPH_DATABASE_PROVIDER=postgres` + Apache AGE path).

**Cross-package drift to flag for Wave 3:**
- `core/memory/memory/cognee_config.py` configures **Memgraph + LanceDB**
  (legacy crypteolas path), but `infrastructure/stacks/cognee/compose.yaml`
  uses **Postgres + pgvector unified provider** (modern lakehouse path).
  Two configs, one package — they disagree on which graph store to use.
- Dataset names drift between compose.yaml (`oideachais.aistear`,
  dot-notation) and the cognify code (`oideachais_cross_stage`,
  underscore-notation). This will cause the cross_stage cognify asset to
  silently miss its dataset when `COGNEE_DATABASES` env var is set.

## Code (canonical patterns)

### Current Cianfhoghlaim v1.2.2 pattern (recommended)

```python
# v1.0 API — recommended for new code
import cognee
from cognee import SearchType

# Permanently store + extract (runs add + cognify + improve under the hood)
await cognee.remember("Irish Leaving Cert maths syllabus §3.2 ...")

# Session-scoped fast memory (cache only; sync to graph on improve)
await cognee.remember("User prefers worked examples", session_id="chat_42")

# Auto-routing recall (picks best search strategy per query)
results = await cognee.recall("What prerequisites for differentiation?")

# Datasets scoping (works in v1.0)
results = await cognee.recall(
    "BAML extraction patterns",
    datasets=["oideachais.primary", "oideachais.cross_stage"],
)

# Explicit search type override
results = await cognee.recall(
    "edge weight schema",
    search_type=SearchType.GRAPH_COMPLETION_COT,  # multi-hop reasoning
    top_k=15,
)
```

### Current Cianfhoghlaim v0.x pattern (legacy — what the codebase uses today)

```python
# cianfhoghlaim/cognify/cognee_integration/cross_stage_cognify.py:131
dataset_name = "oideachais_cross_stage"
await cognee.add(edge_definitions, dataset_name=dataset_name)
await cognee.cognify(dataset=dataset_name)

# cianfhoghlaim/core/memory/memory/cognee_service.py:210 (Memgraph path)
await self._cognee.add(content, dataset_name=dataset)
await self._cognee.cognify()  # processes ALL datasets — no scoping!
results = await self._cognee.search(
    query_text=query,
    query_type=cognee_type,
    top_k=top_k,
)
```

### Backend configuration — two divergent styles

**Style A — Postgres unified (`infrastructure/stacks/cognee/compose.yaml:42-59`)**:
```yaml
COGNEE_STORAGE: postgresql
COGNEE_POSTGRES_HOST: cognee-postgres
GRAPH_DATABASE_PROVIDER: postgres
VECTOR_DB_PROVIDER: pgvector
USE_UNIFIED_PROVIDER: pghybrid   # ← experimental, not in current docs
```

**Style B — Memgraph + LanceDB (`core/memory/memory/cognee_config.py:66-94`)**:
```python
graph=GraphConfig(provider=GraphProvider.MEMGRAPH, url="bolt://localhost:7687", ...)
vector=VectorConfig(provider=VectorProvider.LANCEDB, url="./lancedb_data", ...)
```

**v1.2.2 recommended pattern (`docs.cognee.ai/setup-configuration/graph-stores`)**:
```bash
GRAPH_DATABASE_PROVIDER="kuzu"          # default for local; single-process
# OR
GRAPH_DATABASE_PROVIDER="neo4j"          # production; requires APOC plugin
GRAPH_DATABASE_URL="bolt://localhost:7687"
# Plus APOC installed in Neo4j for type labels (apoc.create.addLabels)
```

### LLM routing via LiteLLM proxy (matches `compose.yaml:30-41`)

```bash
# cognee → LiteLLM → DeepSeek pattern
LLM_PROVIDER="openai"                    # openai-compatible adapter
LLM_MODEL="deepseek/deepseek-chat"       # routed via litellm proxy
LLM_BASE_URL="http://litellm:4000/v1"
LLM_API_KEY="no-key-needed"              # sentinel; litellm uses its own key

EMBEDDING_PROVIDER="openai"
EMBEDDING_MODEL="openai/text-embedding-3-small"  # must be tiktoken-recognizable
EMBEDDING_BASE_URL="http://litellm:4000/v1"
```

### MCP server (14 tools — v1.0 memory + legacy + retrieval + data management)

```jsonc
// opencode.json MCP server config
{
  "cognee-mcp": {
    "url": "http://localhost:8100",          // cognee REST API base
    "tools": [                               // 14 total
      // v1.0 (recommended)
      "remember", "recall", "forget", "improve",
      // legacy (still supported)
      "cognify", "search", "prune",
      // retrieval helpers
      "get_document", "get_chunk_neighbors",
      // interaction capture
      "save_interaction",
      // data management
      "list_data", "delete", "delete_dataset", "cognify_status"
    ]
  }
}
```

Standalone vs API mode (from `docs.cognee.ai/cognee-mcp/mcp-overview`):
- **Standalone** — MCP server manages its own DB; each instance isolated
- **API mode** — MCP server connects to centralised Cognee backend at
  `COGNEE_BASE_URL`; team-shared knowledge graph

### Custom graph model (current Cianfhoghlaim pattern)

```python
# cianfhoghlaim/core/memory/memory/cognee_config.py:194-225
entity_types: list[str] = field(default_factory=lambda: [
    "word", "phrase", "cognate", "etymology",
    "dialect_variant", "manuscript", "transcription",
    "pronunciation", "grammar_rule", "place_name", "person_name",
])
relationship_types: list[str] = field(default_factory=lambda: [
    "is_cognate_of", "derives_from", "translates_to",
    "has_variant", "appears_in", "spoken_in",
    "follows_rule", "related_to", "same_meaning_as", "opposite_of",
])
```

This is the Cognee-style entity/relationship schema (string labels), not
Pydantic `Node`/`Edge` subclasses. Used to constrain the LLM extraction
prompt.

### 15 SearchType modes (`docs.cognee.ai/python-api/search-type`)

| SearchType | LLM calls | Use case |
|:--|--:|:--|
| `CHUNKS` / `SUMMARIES` / `CHUNKS_LEXICAL` / `CYPHER` | 0 | Retrieval only (fastest) |
| `RAG_COMPLETION` | 1 | Simple chunk-based RAG |
| `GRAPH_COMPLETION` (default) | 1 | Best accuracy/speed balance |
| `TRIPLET_COMPLETION` | 1 | Triplet-embeddings (needs `TRIPLET_EMBEDDING=true`) |
| `NATURAL_LANGUAGE` | 1-3 | NL → Cypher translation |
| `TEMPORAL` | 2 | Time-aware queries |
| `GRAPH_SUMMARY_COMPLETION` | 2 | Tight context for noisy graphs |
| `GRAPH_COMPLETION_DECOMPOSITION` | 2-7 | Multi-entity queries |
| `GRAPH_COMPLETION_CONTEXT_EXTENSION` | up to 4 rounds | Exploratory queries |
| `GRAPH_COMPLETION_COT` | up to `max_iter` rounds | Multi-hop reasoning |
| `FEELING_LUCKY` | 1 + chosen | Auto-pick |
| `CODING_RULES` | varies | Codebase-specific |

> **Drift alert:** `cognee_service.py:376` references `SearchType.INSIGHTS`
> which is **not in the current docs enum**. Likely deprecated — needs
> migration to `SearchType.SUMMARIES` or `SearchType.RAG_COMPLETION`.

## Env

| Env var | Value | Source | Notes |
|:--|:--|:--|:--|
| `COGNEE_API_URL` | `http://cognee:8100` | Locket (compose.yaml:23) | REST API base |
| `LLM_API_KEY` | `no-key-needed` | Locket | Sentinel for litellm forwarding |
| `LLM_PROVIDER` | `openai` | Locket | OpenAI-compat adapter → litellm |
| `LLM_BASE_URL` | `http://litellm:4000/v1` | Locket | Routes via LiteLLM proxy |
| `LLM_MODEL` | `${COGNEE_LLM_MODEL:-minimax}` | Locket | Phase 0.4 spec default; compose.yaml:33 |
| `EMBEDDING_MODEL` | `${COGNEE_EMBEDDING_MODEL:-openai/text-embedding-3-small}` | Locket | Must be tiktoken-recognizable |
| `COGNEE_DATABASES` | `oideachais.aistear,oideachais.primary,...` | hardcoded (compose.yaml:42) | Comma-separated, **dot-notation** |
| `COGNEE_STORAGE` | `postgresql` | hardcoded | Newer env var name |
| `USE_UNIFIED_PROVIDER` | `pghybrid` | hardcoded | **Experimental**; not in v1.x docs |
| `GRAPH_DATABASE_PROVIDER` | `postgres` | hardcoded | Non-standard; v1.x defaults to `kuzu`/`neo4j` |
| `VECTOR_DB_PROVIDER` | `pgvector` | hardcoded | Required when unified |
| `DB_PROVIDER` / `DB_HOST` / ... | `postgres` / `cognee-postgres` / ... | hardcoded (compose.yaml:53-58) | Relational engine config |
| `LANCEDB_URI` | `rest://lakehouse-lance-namespace:8182` | hardcoded (compose.yaml:60) | **Dead config** — VECTOR_DB_PROVIDER=pgvector wins; this is ignored |
| `COGNEE_POSTGRES_PASSWORD` | `${COGNEE_POSTGRES_PASSWORD:-devpassword}` | Infisical (Locket) | Prod key from `infisical://dev-baile/cognee/postgres_password` |
| `LOG_LEVEL` | `INFO` | hardcoded | DEBUG for troubleshooting |
| `REQUIRE_AUTHENTICATION` | `false` | hardcoded | Set true behind Pocket ID SSO |
| `ENABLE_BACKEND_ACCESS_CONTROL` | `false` | hardcoded | Multi-tenant mode toggle |
| `ENVIRONMENT` | `production` | hardcoded | |

**v1.2.2 default backends (no extras, plain `pip install cognee`)**:
| Role | Provider | Location |
|:--|:--|:--|
| Relational | SQLite (`DB_PROVIDER=sqlite`) | `<SYSTEM_ROOT_DIRECTORY>/databases/cognee_db` |
| Vector | LanceDB (`VECTOR_DB_PROVIDER=lancedb`) | `<SYSTEM_ROOT_DIRECTORY>/databases/cognee.lancedb` |
| Graph | Ladybug/Kuzu (`GRAPH_DATABASE_PROVIDER=ladybug`) | `<SYSTEM_ROOT_DIRECTORY>/databases/cognee_graph_ladybug` |

**v1.2.2 LLM defaults**:
| Variable | Default |
|:--|:--|
| `LLM_PROVIDER` | `openai` |
| `LLM_MODEL` | `openai/gpt-5-mini` |
| `LLM_TEMPERATURE` | `0.0` |
| `EMBEDDING_PROVIDER` | `openai` |
| `EMBEDDING_MODEL` | `openai/text-embedding-3-large` (3072 dims) |

> **Drift alert:** Compose defaults `LLM_MODEL=minimax` (Phase 0.4 switch) and
> `EMBEDDING_MODEL=openai/text-embedding-3-small` (1024 dims) — **neither is
> the v1.2.2 default**. If you bump `cognee/cognee:latest` past 1.2.2, you
> may get `gpt-5-mini` unless the env vars are explicitly set.

## CCC anchors

**Spec doc:** `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-09-cognee-letta.md`

**Core files (canonical paths in v4-consolidated `cianfhoghlaim/`)**:

| Path | Purpose | Drift |
|:--|:--|:--|
| `infrastructure/stacks/cognee/compose.yaml` | REST API + pgvector stack (host:8100) | Uses `USE_UNIFIED_PROVIDER=pghybrid` (experimental) |
| `infrastructure/stacks/cognee/sidecar.yaml` | Locket secret-injection sidecar | OK |
| `infrastructure/stacks/cognee/secrets.env` | Infisical URI references | OK |
| `infrastructure/stacks/cognee/.env.example` | Local dev secrets template | OK |
| `infrastructure/stacks/cognee/pangolin.yaml` | Pangolin route definitions | OK |
| `infrastructure/stacks/cognee/blueprint.yaml` | Stack blueprint + 8 cross-stage edge types | OK |
| `infrastructure/stacks/cognee/compose.dev.yaml` | Dev override (no-op sidecar) | OK |
| `infrastructure/stacks/cognee/README.md` | Stack bring-up doc (180+ lines) | OK |
| `cianfhoghlaim/stacks/cognee/compose.yaml` | Symlink/duplicate of infra version | Same content (sync drift risk) |
| `cianfhoghlaim/stacks/openclaw/skills-curated/cognee/SKILL.md` | Cognee skill (auto-loaded) | **Stale**: mentions Neo4j/FalkorDB/Memgraph as deployed, which they are NOT (only Postgres unified is deployed) |
| `cianfhoghlaim/cognify/cognee_integration/cross_stage_cognify.py:131-133` | Dagster asset for cross-stage edges | Uses legacy `cognee.add()` + `cognee.cognify(dataset=...)`; dataset name `oideachais_cross_stage` (underscore) ≠ compose.yaml `oideachais.cross_stage` (dot) |
| `cianfhoghlaim/cognify/cognee_integration/leabharlann_cognify.py:48-111` | leabharlann (books/zotero/takeout) cognify helper | Legacy API; `USE_LOCAL_SCRAPES=true` default → **always stub mode** in CI |
| `cianfhoghlaim/cognify/cognee_integration/official_media_cognify.py:36-70` | Instagram → gov resolver cognify | Legacy API; same stub-mode gating |
| `cianfhoghlaim/cognify/cognee_integration/author_archive_cognify.py`, `site_analysis_cognify.py`, `culture_cognify.py` | 3 more cognify helpers | Same legacy pattern (not opened, inferred from filenames) |
| `cianfhoghlaim/core/memory/memory/cognee_config.py:1-607` | Memgraph+LanceDB config (Celtic linguistics) | **Disagrees with compose.yaml**: uses Memgraph instead of Postgres |
| `cianfhoghlaim/core/memory/memory/cognee_service.py:100-640` | `CelticMemoryService` wrapper | Uses `cognee.config.set_graph_database_provider()` (old setter API); calls `cognee.cognify()` without scoping; references `SearchType.INSIGHTS` (deprecated) |
| `cianfhoghlaim/core/cognee/_graph/research.py:232-252` | `ResearchMemory` class | Snippet suggests deeper research-time Cognee usage |
| `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:63-77` | Spec requirement: "Cognee canonical knowledge graph layer, 6 typed datasets" | States `USE_UNIFIED_PROVIDER=pghybrid` (Neo4j fallback "for prod" — which is contradicted by actual deployment) |
| `openspec/specs/agent-memory-systems/spec.md` | Agent memory router spec | Should cross-reference Cognee dataset topology |
| `openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/` | v4 consolidation change | Moved 5 quadrants into single `cianfhoghlaim/`; spec mentions old paths like `oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py` which don't exist post-v4 |
| `docs/legacy/crypteolas/apps/crypteolas_demo/pipelines/knowledge/cognee_pipeline.py` | Old crypto dual-graph helper | Uses Memgraph+FalkorDB (legacy crypteolas) — superseded by `cognee_service.py` |

**CCC search terms that return high-signal hits**:
- `"cognee.cognify"` → finds all cognify helpers + research.py
- `"SearchType.GRAPH_COMPLETION"` → finds v1.0-style search references
- `"cognee.search"` → finds query paths
- `"graph_models"` → finds Pydantic-style ontology files (none in v4-consolidated path)
- `"COGNEE_DATABASES"` → finds compose.yaml + blueprint.yaml

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2024-03 | Cognee 0.1.0 first PyPI release | https://pypi.org/project/cognee/#history |
| 2024-04 → 2025-12 | Rapid 0.1.x → 0.5.x releases (weekly cadence) | https://pypi.org/project/cognee/#history |
| 2025-08 | Initial Cognee deploy (Neo4j backend) | spec/P1B-09-cognee-letta.md:90 |
| 2025-12 | Added Postgres backend (replacement for relational layer) | spec:91 |
| 2026-01 | Wired BAML extraction → Cognee cognify | spec:92 |
| 2026-03 | Added 6 typed datasets (per educational stage) | spec:93 |
| 2026-04 | Replaced Neo4j with Postgres unified provider | spec:94 |
| 2026-04-11 | Cognee 1.0.0 released — new `remember`/`recall`/`forget`/`improve` API | https://pypi.org/project/cognee/ |
| 2026-05-16 | Cognee 1.1.0 — multi-user mode + Neo4j Aura auto-provisioning | docs.cognee.ai/setup-configuration/graph-stores |
| 2026-06-12 | Cognee stack brought up on bunchloch (1.1.2-local) | stacks/cognee/README.md:154-165 |
| 2026-06-20 | Cognee 1.2.0 — Kuzu becomes default graph store | docs.cognee.ai/setup-configuration/overview |
| 2026-06-26 | Cognee 1.2.2 — current PyPI latest (2 days before this audit) | https://pypi.org/project/cognee/ |
| 2026-06-28 | v4 consolidation moved quadrants into `cianfhoghlaim/` | openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4 |
| 2026-06 | Phase 0.4 default LLM switched to `minimax` | spec:95 |

**Drift summary**:
1. **API drift (major)** — Code uses v0.x API (`cognee.add/cognify/search`); v1.0 API is `remember/recall/forget/improve/serve/push`. Both work but the legacy path is deprecated.
2. **Default backend drift (major)** — Code uses `USE_UNIFIED_PROVIDER=pghybrid` (experimental); v1.x defaults to Kuzu + LanceDB + SQLite.
3. **Dataset naming drift** — compose.yaml: `oideachais.aistear` (dot) vs cross_stage_cognify.py: `oideachais_cross_stage` (underscore). Cross-stage asset will silently fail to find its dataset.
4. **Embedding model drift** — spec uses `text-embedding-3-small` (1536 dims) but `EMBEDDING_MODEL` env var in compose.yaml overrides to `openai/text-embedding-3-small`. v1.2.2 default is `text-embedding-3-large` (3072 dims).
5. **Spec path drift** — P1B-09 spec references `oideachais/agents/meaisinfhoghlaim/memory/cognee_client.py` and `cognify/cognee_integration/graph_models/` which **don't exist** in v4-consolidated `cianfhoghlaim/`. Actual paths: `core/memory/memory/cognee_service.py` and `cognify/cognee_integration/{cross,leabharlann,official_media,...}_cognify.py`.
6. **Skill doc drift** — `stacks/openclaw/skills-curated/cognee/SKILL.md` claims Neo4j/FalkorDB/Memgraph are "all three deployed in this infrastructure" — **only Postgres unified is actually deployed**.
7. **Config drift** — `cognee_config.py` uses Memgraph (legacy crypteolas); `compose.yaml` uses Postgres unified (modern lakehouse). Two configs, one package.

## Anti-patterns

1. **Don't use legacy `cognee.add/cognify/search` in new code** — migrate to `remember/recall/forget/improve` for v1.0 API surface.
2. **Don't pass `dataset=None` to `cognee.cognify()`** — processes ALL datasets; expensive and unintended. Always pass `datasets=[...]`.
3. **Don't store Cognee data in SQLite for multi-writer** — use Postgres (`cognee[postgres]`).
4. **Don't use Neo4j without APOC** — without it, all nodes show generic `__Node__` label only (no type-specific labels visible in Neo4j Browser). Install via Neo4j Desktop plugins area.
5. **Don't use Kuzu for multi-agent scenarios** — file-based locking is not safe for concurrent processes. Use Neo4j instead.
6. **Don't pass `LLM_API_KEY=<litellm master key>` to cognee** — DeepSeek (and other backends) will reject it. Use sentinel `LLM_API_KEY=no-key-needed`.
7. **Don't use `LLM_MODEL=embedding` or `embedding-curriculum` aliases** — Cognee validates against tiktoken at startup; aliases fail. Use full litellm model path like `openai/text-embedding-3-small`.
8. **Don't use `LLM_INSTRUCTOR_MODE=json_schema_mode` with Ollama or custom endpoints** — won't work; use `json_mode` or `tool_call` instead.
9. **Don't `cognee.add()` rows in production when `USE_LOCAL_SCRAPES=true`** — all cognify helpers stub-out in CI/local dev. Default for all 6 cognify_*.py helpers.
10. **Don't use `cognee.config.set_graph_database_provider()`** — old setter API. Use `cognee.config.set("graph_database_provider", "...")` (the new generic-key setter).
11. **Don't use `SearchType.INSIGHTS`** — removed from current enum. Use `SearchType.SUMMARIES` (pre-generated summaries) or `SearchType.RAG_COMPLETION` (retrieval + LLM).
12. **Don't reference datasets by different names in compose.yaml vs code** — `oideachais.aistear` (dot) and `oideachais_aistear` (underscore) are different dataset strings; cross_stage asset will miss its target silently.
13. **Don't skip `incremental_loading=True`** on `cognify()` — defaults to True and avoids reprocessing unchanged chunks.
14. **Don't put Neo4j connection pool args in `POOL_ARGS`** without validating JSON — invalid JSON raises config error at startup.
15. **Don't use `ENABLE_BACKEND_ACCESS_CONTROL=true` with `GRAPH_DATABASE_PROVIDER=kuzu`** — only works for supported providers.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Default LLM | `openai/gpt-5-mini` (v1.2.2 default) | Lower cost than gpt-4o; good for knowledge-graph extraction. **NOT** `minimax` (Phase 0.4 spec) — minimax is KCG's litellm alias, not a direct cognee model |
| Fallback LLM chain | DeepSeek → OpenAI via LiteLLM proxy | DeepSeek 14× cheaper; spec routes via `deepseek/deepseek-chat` |
| Default embedding | `openai/text-embedding-3-small` (1536 dims) | Multilingual support + cost; spec matches. **NOT** v1.2.2 default of `text-embedding-3-large` (3072 dims) |
| Default graph backend | **Kuzu** (v1.2.2 default) for dev; **Neo4j + APOC** for prod multi-agent | Kuzu = file-based, no concurrent agents. Neo4j + APOC = proper type labels |
| Current KCG graph backend | **Postgres unified (`USE_UNIFIED_PROVIDER=pghybrid`)** | Simpler ops, no separate Neo4j container. **Risk:** experimental flag not in v1.x docs; may break on Cognee upgrade |
| Default vector backend | **pgvector** (when unified) | Same Postgres host. Alternative: LanceDB if splitting graph from vector |
| Default relational backend | **Postgres** (`pgvector/pgvector:pg17`) | Multi-writer; spec confirmed |
| Datasets | 6 (aistear, primary, junior_cycle, senior_cycle, tertiary, cross_stage) + 3 leabharlann | Per-stage scope; spec confirmed |
| Dataset naming | `oideachais.aistear` (dot notation) in compose.yaml — **must match in code** | DRIFT: code uses `oideachais_cross_stage` (underscore) |
| LLM routing | LiteLLM proxy at `http://litellm:4000/v1` | One key, fallback chains, easy model swap |
| Embedding routing | LiteLLM proxy same endpoint | Reuse proxy; tiktoken-recognizable model names only |
| MCP server mode | **API mode** (centralised) for team; **standalone** for dev isolation | Spec confirms; cognee-mcp image supports both via `TRANSPORT_MODE` env |
| MCP tools to expose | 4 v1.0 tools (`remember/recall/forget/improve`) + retrieval helpers (`get_document`, `get_chunk_neighbors`) | v1.0 API recommended |
| API version to target | v1.0+ (`remember/recall/forget/improve/serve/push`) | Legacy `add/cognify/search` works but is being deprecated |
| API entry point for new code | `await cognee.remember(data, dataset_name="oideachais.primary")` | Single call = add + cognify + improve |
| Cross-stage cognify asset | `cross_stage_cognify.py` (Dagster asset) — already wired | 8 edge types enumerated in `EDGE_DEFINITIONS` |
| Memory backend for agents | **Cognee** for document cognition + **Letta** for agent session memory | Spec confirms split: Cognee = what the codebase knows; Letta = what each agent remembers |
| Auth in dev | `REQUIRE_AUTHENTICATION=false` + `ENABLE_BACKEND_ACCESS_CONTROL=false` | Local-only |
| Auth in prod | `REQUIRE_AUTHENTICATION=true` + Pocket ID SSO + Pangolin route | Standard pattern |

## §8 Refactor opportunities

### High-impact (do these first)

**R1. Migrate legacy `add/cognify/search` to v1.0 `remember/recall/improve/forget`** — 6 files affected
- `cognify/cognee_integration/cross_stage_cognify.py:131-133` → use `remember`
- `cognify/cognee_integration/leabharlann_cognify.py:104-105` → use `remember`
- `cognify/cognee_integration/official_media_cognify.py:64-65` → use `remember`
- `cognify/cognee_integration/{author_archive,site_analysis,culture}_cognify.py` (similar pattern)
- `core/memory/memory/cognee_service.py:210-216,266-267,313-314,345-346` → use `remember`
- Removes deprecated `cognee.add/cognify/search` surface usage; reduces risk of v1.x API removal

**R2. Fix dataset-naming drift between compose.yaml and code** — 1 file change but cross-cutting impact
- `infrastructure/stacks/cognee/compose.yaml:42` uses `oideachais.aistear,oideachais.primary,...` (dot)
- `cognify/cognee_integration/cross_stage_cognify.py:131` uses `oideachais_cross_stage` (underscore)
- **Choice A**: Change compose.yaml to underscore (`oideachais_aistear,oideachais_primary,...`) — matches code
- **Choice B**: Change code to dot — matches compose.yaml (more standard Cognee convention)
- Recommend Choice B: dot notation is the standard for namespaced datasets

**R3. Replace `USE_UNIFIED_PROVIDER=pghybrid` with explicit `GRAPH_DATABASE_PROVIDER=postgres` + Apache AGE**
- Current `pghybrid` is experimental and undocumented in v1.x docs
- Recommended path: enable Apache AGE extension on Postgres, set `GRAPH_DATABASE_PROVIDER=postgres`
- Avoids the experimental flag, future-proofs for Cognee upgrades

### Medium-impact

**R4. Update `stacks/openclaw/skills-curated/cognee/SKILL.md`** — claim that Neo4j/FalkorDB/Memgraph are "all three deployed" is false. Only Postgres unified is deployed. Either remove the false claim or add a "planned" note.

**R5. Migrate `cognee_config.py` to Postgres unified** — currently uses Memgraph; should match `compose.yaml` for consistency. Or document why two configs (Celtic linguistics path uses Memgraph for static knowledge, lakehouse path uses Postgres).

**R6. Replace deprecated `cognee.config.set_graph_database_provider()` with `cognee.config.set("graph_database_provider", ...)`**
- `core/memory/memory/cognee_config.py:459-463` uses old per-key setter
- New generic-key setter is the v1.x recommended path

**R7. Replace `SearchType.INSIGHTS` with `SearchType.SUMMARIES`** — `cognee_service.py:376` references an enum value that doesn't exist in v1.2.2. Will throw `AttributeError` on import.

**R8. Add `LANCEDB_URI` cleanup to compose.yaml** — `compose.yaml:60` sets `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` but `VECTOR_DB_PROVIDER=pgvector` overrides the vector store. The LanceDB URI is **dead config** — remove it or wire it up properly.

### Low-impact (nice-to-have)

**R9. Pin `cognee/cognee` image tag in compose.yaml** — currently `latest`. Pin to `1.2.2` (or whatever current) for reproducibility.

**R10. Add `apoc.create.addLabels` install note to Neo4j stack docs** — currently Neo4j isn't deployed but if it ever is, APOC is required for type labels.

**R11. Document the `oideachais.cross_stage` vs `oideachais_cross_stage` discrepancy** — add to spec README so future agents don't trip.

**R12. Add health check for `cognee-mcp` container** — compose.yaml only health-checks `cognee`; if MCP mode is enabled, it should also be checked.

**R13. Add `graphiti` extra consideration** — `cognee[graphiti]` is a PyPI extra that bundles Graphiti (a temporal knowledge graph backend). Could replace custom temporal cognify logic in `cross_stage_cognify.py` if temporal features become important.

## Files to read next

- `infrastructure/stacks/cognee/compose.yaml` — current REST API stack
- `infrastructure/stacks/cognee/README.md` — bring-up doc with version history
- `infrastructure/stacks/cognee/blueprint.yaml` — 8 cross-stage edge type definitions
- `cianfhoghlaim/cognify/cognee_integration/cross_stage_cognify.py` — canonical cognify pattern
- `cianfhoghlaim/core/memory/memory/cognee_service.py` — CelticMemoryService wrapper
- `cianfhoghlaim/core/memory/memory/cognee_config.py` — Memgraph+LanceDB config (drift from compose.yaml)
- `docs.cognee.ai/python-api` — v1.0 API surface (remember/recall/forget/improve)
- `docs.cognee.ai/setup-configuration/overview` — v1.2.2 default backends
- `docs.cognee.ai/setup-configuration/graph-stores` — Kuzu vs Neo4j + APOC
- `docs.cognee.ai/cognee-mcp/mcp-tools` — 14 MCP tools reference
- `docs.cognee.ai/python-api/search-type` — 15 SearchType modes
- `openspec/specs/agent-memory-systems/spec.md` — Cognee + Graphiti + LanceDB router spec
- `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:63-77` — current canonical Cognee spec

---

**Cross-agent dependencies:**
- `## Agent X relies on: Agent 09` — Any agent touching the cognify_*.py helpers, MCP config, or graph database topology.
- Wave 3 synthesis should reconcile: `## Agent 09 finding: dataset naming drift (dot vs underscore) will surface in cross_stage_cognify asset on first cognify run`.

**Conflicts to flag:**
- `## Conflict with Agent X`: If another agent claims Postgres unified is "the only" graph backend, note that `cognee_config.py` also references Memgraph (legacy crypteolas path).