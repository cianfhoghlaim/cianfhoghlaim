# Refactor 38 — Cognee v0.5 → v1.2.2 API Migration (`add/cognify/search` → `remember/recall/improve/forget`)

**Agent 38 of 43** · Program 2 · 2026-06-29
**Priority:** P2 (refactor-prioritizer §5 P2-9; chain dependency `P0-5 → P1-11 → P2-9 → P2-10,P2-11`)
**Estimated effort:** ~10 hours (2h audit + 4h codemod + 1h dataset fix + 2h validate + 1h cutover)
**BrowserBase credits:** 0 (read-only synthesis; 5 RAGAS dry-runs pre-cutoever)
**Cross-references:** `agent-09-cognee.md`, `synthesis/26-refactor-prioritizer.md` (P0-5 + P1-11 + P2-9/10/11), `synthesis/28-misunderstandings-corrector.md` (C-1B.3), `cognee_config.py`, `cognee_service.py`, 6 `cognify/cognee_integration/*.py` files

---

## 1. TL;DR

Cognee 1.0 (released 2026-04-11) replaced the v0.x pipeline `add` + `cognify` + `search` with a unified `remember` / `recall` / `forget` / `improve` API; **65 v0-API call sites** exist in `cianfhoghlaim/` (excluding 13 in `docs/legacy/crypteolas/`), 6 `SearchType.INSIGHTS` references (removed in v1.x), 1 dataset-naming drift (`oideachais_cross_stage` vs `oideachais.cross_stage`), and 2 graph-backend drifts (compose.yaml `USE_UNIFIED_PROVIDER=pghybrid` is experimental; `cognee_config.py` defaults to Memgraph — neither is the v1.2.2 default of **Kuzu**). The fix is a 5-step plan with a **LibCST codemod** that auto-rewrites the 65 sites, validated against 6 datasets (`aistear`, `primary`, `junior_cycle`, `senior_cycle`, `tertiary`, `cross_stage`) on bunchloch.

---

## 2. The v0 → v1 API map

### 2.1 Function-level translation

| v0 (legacy) | v1.0 (canonical) | Notes |
|:--|:--|:--|
| `cognee.add(data, dataset_name=…)` | `cognee.remember(data, dataset_name=…)` | Stores + extracts entities (no separate cognify) |
| `cognee.cognify(dataset=…)` | (folded into `remember`) | v1.0 auto-cognifies on `remember` |
| `cognee.search(query_text=…, query_type=…, top_k=…)` | `cognee.recall(query, search_type=…, top_k=…)` | `query_text`→positional; `query_type`→`search_type` |
| `cognee.prune.prune_data()` | `cognee.forget(dataset_name=…)` | Selective per-dataset |
| `cognee.prune.prune_system(metadata=True)` | `cognee.forget(everything=True, metadata=True)` | One call covers system + data |
| `cognee.delete(dataset)` | `cognee.forget(dataset_name=dataset)` | Same intent, renamed |
| `cognee.visualize_graph(path)` | `cognee.visualize_graph(path)` | Unchanged in v1.0 |
| `cognee.config.set_<X>(p)` (13 per-key setters) | `cognee.config.set("<x>", p)` | Per-key setters → generic-key setter |

### 2.2 Session-scoped memory (new in v1.0)

```python
# v1.0 only — no v0 equivalent
await cognee.remember("User prefers worked examples", session_id="chat_42")
# Persists to session cache only; no LLM extraction

await cognee.improve(session_ids=["chat_42"])
# Bridge session → permanent graph: 4-stage pipeline
#   1. Apply feedback weights to graph nodes/edges
#   2. Persist session Q&A into permanent graph
#   3. Enrich graph with triplet embeddings (memify)
#   4. Sync enriched graph back into session caches
```

### 2.3 `SearchType` — 15 modes, drop `INSIGHTS`

Per `docs.cognee.ai/python-api/search-type`, the v1.2.2 enum has **14 valid modes** (was 15 in v0.x; `INSIGHTS` removed):

| # | SearchType | LLM calls | Use case |
|:-:|:--|:-:|:--|
| 1 | `CHUNKS` | 0 | Pure chunk retrieval (fastest) |
| 2 | `SUMMARIES` | 0 | Pre-generated summary retrieval |
| 3 | `CHUNKS_LEXICAL` | 0 | Lexical (BM25) over chunks |
| 4 | `CYPHER` | 0 | Direct Cypher query |
| 5 | `RAG_COMPLETION` | 1 | Standard RAG |
| 6 | `GRAPH_COMPLETION` (default) | 1 | Best accuracy/speed balance |
| 7 | `TRIPLET_COMPLETION` | 1 | Triplet-embeddings (needs `TRIPLET_EMBEDDING=true`) |
| 8 | `NATURAL_LANGUAGE` | 1-3 | NL → Cypher translation |
| 9 | `TEMPORAL` | 2 | Time-aware queries |
| 10 | `GRAPH_SUMMARY_COMPLETION` | 2 | Tight context for noisy graphs |
| 11 | `GRAPH_COMPLETION_DECOMPOSITION` | 2-7 | Multi-entity queries |
| 12 | `GRAPH_COMPLETION_CONTEXT_EXTENSION` | up to 4 rounds | Exploratory queries |
| 13 | `GRAPH_COMPLETION_COT` | up to `max_iter` rounds | Multi-hop reasoning |
| 14 | `FEELING_LUCKY` | 1 + chosen | Auto-pick best strategy |
| ~~15~~ | ~~`INSIGHTS`~~ | ~~1~~ | ~~Pre-LLM summary retrieval~~ — **REMOVED**; replace with `SUMMARIES` or `RAG_COMPLETION` |

**KCG impact**: 2 files reference `SearchType.INSIGHTS` — `core/memory/memory/cognee_service.py:376` (must migrate) and `docs/legacy/crypteolas/.../cognee_pipeline.py:251,256` (legacy, out of scope).

---

## 3. The 3 breaking changes

### 3.1 `SearchType.INSIGHTS` removed (would `AttributeError` at import)

`cognee_service.py:375-380` maps a string `"insights"` → `SearchType.INSIGHTS`. In v1.2.2 the enum value does not exist; the dict access on first call would `AttributeError`. **Replace with `SearchType.SUMMARIES`** (closest semantic match — pre-generated summary retrieval, 0 LLM calls, same cost tier as old `INSIGHTS`).

### 3.2 Dataset naming drift: `oideachais_cross_stage` vs `oideachais.cross_stage`

| Source | Pattern | Example |
|:--|:--|:--|
| `stacks/cognee/compose.yaml:42` | **dot** (Cognee v1.0 canonical) | `oideachais.aistear,oideachais.primary,...,oideachais.cross_stage` |
| `cross_stage_cognify.py:131` | **underscore** (Cognee v0.x) | `oideachais_cross_stage` |
| `cognee_service.py:194,225,275,322` | underscore (default) | `irish_vocabulary`, `manuscripts`, `cognates`, `ocr_corrections` |
| `cognee_config.py:308-323` | underscore (default) | `celtic_education`, `irish_vocabulary`, `manuscripts`, `cognates` |

**Silent-failure scenario:** The `cross_stage_cognify` Dagster asset writes to `oideachais_cross_stage` (underscore). The `COGNEE_DATABASES` env var on compose.yaml only knows about `oideachais.cross_stage` (dot). The cross-stage cognify pass silently writes to an *unmanaged* dataset that is never re-queried by the 6-dataset recall paths. **Dot notation is the Cognee v1.0 standard** (`docs.cognee.ai/python-api/remember#datasets`); the 1 drift site must convert.

### 3.3 Graph DB drift: `USE_UNIFIED_PROVIDER=pghybrid` + Memgraph config vs v1.2.2 default Kuzu

| Path | Source | Provider | Status |
|:--|:--|:--|:--|
| **Compose** | `stacks/cognee/compose.yaml:52,59` | `USE_UNIFIED_PROVIDER=pghybrid` + `GRAPH_DATABASE_PROVIDER=postgres` | **Experimental**; not in v1.2.2 docs |
| **Code** | `cognee_config.py:66,336,367,403` | `GraphProvider.MEMGRAPH` (legacy crypteolas) | **Disagrees with compose.yaml**; v0.5-era |
| **v1.2.2 default** | `docs.cognee.ai/setup-configuration/overview` | **Kuzu** (file-based, single-process) | v1.2.0+ ships Kuzu as default |

**Why we keep `pghybrid` for now**: v1.2.2 Kuzu is file-based with single-process locking — unsafe for the multi-Dagster-asset concurrent cognify workload. The `pghybrid` flag (despite being experimental) lets the same Postgres container serve both relational + pgvector roles, matching our 1-node bunchloch topology. **Recommendation**: keep `pghybrid` but document the upstream v1.2.2 path (Neo4j + APOC) as the prod multi-host migration target — out of scope for this PR (deferred to Refactor 39 / P2-10).

---

## 4. Step 1 — Audit consumers (2 hours)

### 4.1 Run the canonical CCC + grep searches

```bash
bun run ccc:search "cognee.add|cognee.cognify|cognee.search"
bun run ccc:search "SearchType.INSIGHTS"
rg -n 'cognee\.(add|cognify|search|visualize_graph|prune|delete)\b' cianfhoghlaim --type py | wc -l   # 65
rg -n 'SearchType\.INSIGHTS' cianfhoghlaim --type py | wc -l                                            # 6
rg -n 'cognee\.config\.set_(graph|vector|llm|embedding)_' cianfhoghlaim --type py | wc -l                # 5
```

### 4.2 Inventory of 39 actionable v0-API sites (11 files; 65 in repo incl. 19 cognee source tree + 13 legacy)

| File | Sites | Migration action |
|:--|:-:|:--|
| `cognify/cognee_integration/{author_archive,culture,leabharlann,official_media,site_analysis}_cognify.py` | 2 each = 10 | `add`→`remember`; drop `cognify()` |
| `cognify/cognee_integration/cross_stage_cognify.py:131-133` | 3 | `add`→`remember`; dataset `oideachais_cross_stage`→`oideachais.cross_stage`; drop `cognify()` |
| `core/memory/memory/cognee_service.py:210,215,266,267,313,314,345,346,385,552,630,632,639` | 13 | `add`→`remember`; `cognify`→drop; `search`→`recall`; `INSIGHTS`→`SUMMARIES`; `prune.prune_data`→`forget()`; `prune.prune_system`→`forget(everything=True,metadata=True)`; `delete(d)`→`forget(dataset_name=d)`; `visualize_graph` unchanged |
| `core/memory/memory/cognee_config.py:459,460,462,464,467,468,471,472,479,480` | 5 | 5 per-key setters → `cognee.config.set("…", …)` |
| `core/cognee/_graph/research.py:285,286,308,367,617,694` | 6 | `add/cognify/search` rewrite; `add_to_memory`→`remember` (manual) |
| `assets/_oideachais_dagster_defs/assets/leabharlann_full_stack_demo.py:189` | 1 | `add`→`remember` |
| `scripts/_oideachais/cognee_ingest.py:48` | 1 | `add`→`remember` |
| **Total in scope** | **39** | (40 with the 1 yaml pin in §7.5) |

**Out of scope**: 19 hits in `stedding/dev/stacks/machine_learning/cognee/cognee/` (the cognee source tree itself) + 13 hits in `docs/legacy/crypteolas/`.

---

## 5. Step 2 — LibCST codemod (4 hours)

### 5.1 The codemod (`tools/codemods/cognee_v0_to_v1.py`)

```python
"""
LibCST codemod: rewrite Cognee v0.5 API calls to v1.0.

Handles:
  cognee.add(data, dataset_name=...)              -> cognee.remember(data, dataset_name=...)
  cognee.add(data, dataset_name="x") + .cognify() -> cognee.remember(data, dataset_name="x")
        (drop the .cognify() call)
  cognee.cognify()                                -> (DELETE — auto-folded into remember)
  cognee.cognify(dataset=...)                     -> (DELETE)
  cognee.search(query_text=Q, query_type=T, top_k=K)
      -> cognee.recall(Q, search_type=T, top_k=K)
  cognee.search(query, limit=K)                   -> cognee.recall(query, top_k=K)
  cognee.delete(dataset)                          -> cognee.forget(dataset_name=dataset)
  cognee.prune.prune_data()                       -> cognee.forget()
  cognee.prune.prune_system(metadata=True)        -> cognee.forget(everything=True, metadata=True)
  cognee.config.set_graph_database_provider(X)    -> cognee.config.set("graph_database_provider", X)
  ... 16 more per-key setters
  SearchType.INSIGHTS                             -> SearchType.SUMMARIES
"""
import libcst as cst
import libcst.matchers as m
from typing import Sequence


SETTER_RENAMES = {  # method_name -> config_key (16 entries; LLM/embedding/relational/graph/vector)
    "set_graph_database_provider": "graph_database_provider",
    "set_graph_database_url": "graph_database_url",
    "set_graph_database_username": "graph_database_username",
    "set_graph_database_password": "graph_database_password",
    "set_vector_database_provider": "vector_db_provider",
    "set_vector_database_url": "vector_db_url",
    "set_llm_provider": "llm_provider",
    "set_llm_model": "llm_model",
    "set_llm_api_key": "llm_api_key",
    "set_llm_endpoint": "llm_endpoint",
    "set_embedding_provider": "embedding_provider",
    "set_embedding_model": "embedding_model",
    "set_embedding_endpoint": "embedding_endpoint",
    "set_embedding_api_key": "embedding_api_key",
    "set_relational_database_provider": "db_provider",
    "set_relational_database_url": "db_url",
}


class CogneeV0ToV1(cst.CSTTransformer):
    """Rewrite Cognee v0.5 API surface to v1.0.

    Transformations:
      cognee.add(data, dataset_name=...)          -> cognee.remember(...)
      cognee.cognify()                            -> DELETE (folded into remember)
      cognee.search(query_text=Q, query_type=T)   -> cognee.recall(Q, search_type=T)
      cognee.prune.prune_data()                   -> cognee.forget()
      cognee.prune.prune_system(metadata=True)    -> cognee.forget(everything=True, metadata=True)
      cognee.config.set_<X>(v)                    -> cognee.config.set("<x>", v)
      SearchType.INSIGHTS                         -> SearchType.SUMMARIES
    """
    def __init__(self) -> None:
        super().__init__()
        self.rewrites: list[tuple[str, int, str]] = []
        self.removed: list[tuple[str, int]] = []

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call):
        f = updated_node.func
        if m.matches(f, m.Attribute(value=m.Name("cognee"), attr=m.Name("add"))):
            self.rewrites.append(("cognee.add", _line(original_node), "cognee.remember"))
            return updated_node.with_changes(
                func=cst.Attribute(value=cst.Name("cognee"), attr=cst.Name("remember")))
        if m.matches(f, m.Attribute(value=m.Name("cognee"), attr=m.Name("cognify"))):
            self.removed.append(("cognee.cognify()", _line(original_node)))
            return cst.RemoveFromParent()
        if m.matches(f, m.Attribute(value=m.Name("cognee"), attr=m.Name("search"))):
            return self._rewrite_search(updated_node)
        if m.matches(f, m.Attribute(value=m.Name("cognee"), attr=m.Name("delete"))):
            d = updated_node.args[0]
            return updated_node.with_changes(
                func=cst.Attribute(value=cst.Name("cognee"), attr=cst.Name("forget")),
                args=[cst.Arg(value=d.value, keyword=cst.Name("dataset_name"))])
        if m.matches(f, m.Attribute(value=m.Attribute(value=m.Name("cognee"),
                attr=m.Name("prune")), attr=m.Name("prune_data"))):
            return updated_node.with_changes(
                func=cst.Attribute(value=cst.Name("cognee"), attr=cst.Name("forget")), args=[])
        if m.matches(f, m.Attribute(value=m.Attribute(value=m.Name("cognee"),
                attr=m.Name("prune")), attr=m.Name("prune_system"))):
            return updated_node.with_changes(
                func=cst.Attribute(value=cst.Name("cognee"), attr=cst.Name("forget")),
                args=[cst.Arg(value=cst.Name("True"), keyword=cst.Name("everything")),
                      cst.Arg(value=cst.Name("True"), keyword=cst.Name("metadata"))])
        if m.matches(f, m.Attribute(value=m.Attribute(value=m.Name("cognee"),
                attr=m.Name("config")),
                attr=m.MatchIfTrue(lambda a: a.value in SETTER_RENAMES))):
            key = SETTER_RENAMES[f.attr.value]  # type: ignore[union-attr]
            return updated_node.with_changes(
                func=cst.Attribute(value=cst.Attribute(value=cst.Name("cognee"),
                    attr=cst.Name("config")), attr=cst.Name("set")),
                args=[cst.Arg(value=cst.SimpleString(f'"{key}"'))] + list(updated_node.args))
        return updated_node

    def leave_Attribute(self, original_node: cst.Attribute, updated_node: cst.Attribute):
        if (isinstance(updated_node.value, cst.Name)
                and updated_node.value.value == "SearchType"
                and updated_node.attr.value == "INSIGHTS"):
            self.rewrites.append(
                ("SearchType.INSIGHTS", _line(original_node), "SearchType.SUMMARIES"))
            return updated_node.with_changes(attr=cst.Name("SUMMARIES"))
        return updated_node

    def _rewrite_search(self, node: cst.Call) -> cst.Call:
        positional, kwargs = [], []
        for arg in node.args:
            kw = arg.keyword.value if arg.keyword else None
            if kw == "query_text":
                positional.append(cst.Arg(value=arg.value))
            elif kw == "query_type":
                kwargs.append(cst.Arg(value=arg.value, keyword=cst.Name("search_type")))
            elif kw == "limit":
                kwargs.append(cst.Arg(value=arg.value, keyword=cst.Name("top_k")))
            else:
                kwargs.append(arg)
        self.rewrites.append(("cognee.search", _line(node), "cognee.recall"))
        return node.with_changes(
            func=cst.Attribute(value=cst.Name("cognee"), attr=cst.Name("recall")),
            args=positional + kwargs)


def _line(node) -> int:
    return node.location.start.line  # type: ignore[no-any-return]


# ---- Runner ----
if __name__ == "__main__":
    import sys
    from pathlib import Path

    codemod = CogneeV0ToV1()
    for path in sys.argv[1:]:
        src = Path(path).read_text()
        new_tree = cst.parse_module(src).visit(codemod)
        Path(path).write_text(new_tree.code)
        print(f"{path}: {len(codemod.rewrites)} rewrites, {len(codemod.removed)} deletes")
```

### 5.2 Run the codemod

```bash
# Add libcst to dev deps (already a transitive of ruff/uv)
uv pip install libcst

# Run on all 11 in-scope files
uv run python tools/codemods/cognee_v0_to_v1.py \
  cianfhoghlaim/cognify/cognee_integration/{author_archive,cross_stage,culture,leabharlann,official_media,site_analysis}_cognify.py \
  cianfhoghlaim/core/memory/memory/{cognee_service,cognee_config}.py \
  cianfhoghlaim/core/cognee/_graph/research.py \
  cianfhoghlaim/assets/_oideachais_dagster_defs/assets/leabharlann_full_stack_demo.py \
  cianfhoghlaim/scripts/_oideachais/cognee_ingest.py
```

### 5.3 Sample diff (from `cross_stage_cognify.py:131-133`)

```diff
-    dataset_name = "oideachais_cross_stage"
-    await cognee.add(edge_definitions, dataset_name=dataset_name)
-    await cognee.cognify(dataset=dataset_name)
+    dataset_name = "oideachais.cross_stage"
+    await cognee.remember(edge_definitions, dataset_name=dataset_name)
```

### 5.4 Sample diff (from `cognee_service.py:374-389`)

```diff
     search_type_map = {
         "chunks": SearchType.CHUNKS,
-        "insights": SearchType.INSIGHTS,
+        "insights": SearchType.SUMMARIES,
         "graph_completion": SearchType.GRAPH_COMPLETION,
         "summaries": SearchType.SUMMARIES,
         "feeling_lucky": SearchType.FEELING_LUCKY,
     }
     cognee_type = search_type_map.get(search_type, SearchType.GRAPH_COMPLETION)
-    results = await self._cognee.search(query_text=query, query_type=cognee_type, top_k=top_k)
+    results = await self._cognee.recall(query, search_type=cognee_type, top_k=top_k)
```

### 5.5 Codemod limitations (require manual follow-up)

1. **17th setter** (`set_<anything>_timeout`) — codemod handles the 16 most common setters.
2. **`cognee.add_to_memory()`** in `core/cognee/_graph/research.py:694` is a custom method (not cognee's API); manual line edit required.
3. **`_run_cognee_cognify` helper function name** in `cross_stage_cognify.py:126` — manual rename to `_run_cognee_remember` recommended.

---

## 6. Step 3 — Dataset naming fix (1 hour)

### 6.1 Standardize on dot notation

Per `docs.cognee.ai/python-api/remember#datasets` (Cognee v1.0), dataset names use **dot notation for namespaced** (`oideachais.aistear`, etc.) and **plain** for unnamespaced (`cognates`, `manuscripts`). The 6 oideachais.* names already exist in `compose.yaml:42`; the codemod converts the one drift site (`oideachais_cross_stage`→`oideachais.cross_stage` in `cross_stage_cognify.py:131`). The 9 leabharlann / culture-heritage / official-media / site-analysis datasets are **already canonical** and need no rename.

**Total diff: 1 line in code** (`cross_stage_cognify.py:131`); `compose.yaml:42` already correct.

---

## 7. Step 4 — Validate (2 hours)

### 7.1 Pre-cutoever RAGAS dry-runs (every 5th output rule)

Per the 43-prompt BrowserBase program spec, **run RAGAS evaluation on every 5th output for drift detection**. Checkpoints at 5 files (cognify/*) and 9 files (final).

```bash
# After 5 files migrated (cognify/*.py):
uv run ragas eval --metrics faithfulness,answer_relevance,context_precision \
  --dataset cianfhoghlaim.datasets.ragas.cognee_migration \
  --output openspec/research/2026-06-28-browserbase-program-2/ragas/38-cognee-migration-step5.json

# After all 9 files migrated + tests pass (adds context_recall):
uv run ragas eval --metrics faithfulness,answer_relevance,context_precision,context_recall \
  --dataset cianfhoghlaim.datasets.ragas.cognee_migration \
  --output openspec/research/2026-06-28-browserbase-program-2/ragas/38-cognee-migration-step9.json
```

**Pass criteria**: `faithfulness ≥ 0.92` (no regression vs v0 baseline 0.94), `context_precision ≥ 0.85` (no regression vs 0.88), `answer_relevance ≥ 0.90` (no regression vs 0.91).

### 7.2 Run the 6 datasets through the new API

```bash
# 1. Bring up cognee stack on bunchloch
mise run cognee:up

# 2. Run the cross-stage cognify asset (validates the critical naming-drift fix)
mise run dagster:asset-materialize --asset cross_stage_cognify

# 3. Run all 6 oideachais cognify helpers in sequence (cognify + recall)
DSS='aistear primary junior_cycle senior_cycle tertiary cross_stage'
for ds in $DSS; do
  uv run python -c "
import asyncio
from cianfhoghlaim.cognify.cognee_integration import leabharlann_cognify
import cognee
from cognee import SearchType
async def main():
    await leabharlann_cognify.cognify_leabharlann_rows(dataset='oideachais.$ds', rows=load_test_rows('$ds'))
    results = await cognee.recall('test query for $ds', datasets=['oideachais.$ds'],
        search_type=SearchType.GRAPH_COMPLETION, top_k=5)
    print(f'$ds: {len(results)} results')
asyncio.run(main())"
done
```

### 7.3 Verify identical knowledge graph output

```bash
docker exec cianfhoghlaim-cognee-postgres \
  pg_dump --table=*edges* --table=*nodes* -U cognee cognee_oideachais \
  > /tmp/kg-pre-migration-$(date +%Y%m%d-%H%M%S).sql
# (after migration) ... /tmp/kg-post-migration-*.sql
diff <(grep -v '^--' /tmp/kg-pre-*.sql | sort) \
     <(grep -v '^--' /tmp/kg-post-*.sql | sort) | head -100
```

**Pass criteria**: graph node/edge count within ±2% of pre-migration; all 6 dataset rows retrievable via `cognee.recall(dataset_name=…)`.

### 7.4 Test the `SearchType.SUMMARIES` replacement for `INSIGHTS`

```bash
uv run python -c "
import asyncio, cognee
from cognee import SearchType
async def main():
    results = await cognee.recall('Find dialect variants of teach in Irish dialects',
        datasets=['oideachais.primary'], search_type=SearchType.SUMMARIES, top_k=10)
    print(f'OK: {len(results)} results')
asyncio.run(main())
"
```

### 7.5 Pin the cognee image to `1.2.2`

`stacks/cognee/compose.yaml:19` `cognee/cognee:latest` → `cognee/cognee:1.2.2` (locks the migration target; tracked as P3-17 in `synthesis/26-refactor-prioritizer.md`).

---

## 8. Step 5 — Cutover (1 hour)

### 8.1 Deploy to bunchloch

```bash
# 1. Merge the codemod PR (after RAGAS validation passes)
gh pr merge 38-cognee-v1-api-migration --squash --delete-branch

# 2. Pull latest on bunchloch
ssh bunchloch 'cd kings_college_galway && git pull --rebase && bun install'

# 3. Restart the cognee stack
ssh bunchloch 'cd kings_college_galway/infrastructure/stacks/cognee && \
  docker compose -f compose.yaml -f sidecar.yaml down && \
  docker compose -f compose.yaml -f sidecar.yaml up -d'

# 4. Watch for errors
ssh bunchloch 'docker logs -f cianfhoghlaim-cognee 2>&1 | \
  grep -E "(ERROR|cognee\.search|cognee\.add|cognee\.cognify|AttributeError|TypeError)" | head -100'
```

### 8.2 Run a smoke test (3 minutes)

```bash
ssh bunchloch 'cd kings_college_galway && \
  mise run dagster:asset-materialize --asset cross_stage_cognify && \
  mise run dagster:asset-materialize --asset leabharlann_full_stack_demo && \
  mise run dagster:asset-materialize --asset official_media_cognify'
```

**Pass criteria**: All 3 assets return `0` (stub mode) or `> 0` edges; no `AttributeError`/`TypeError`/`KeyError` in cognee container logs.

### 8.3 Watch for the 3 most likely regression patterns

| Failure | Fix |
|:--|:--|
| `AttributeError: type object 'SearchType' has no attribute 'INSIGHTS'` (missed codemod site) | `rg 'SearchType\.INSIGHTS' cianfhoghlaim`; fix manually |
| `KeyError: 'oideachais_cross_stage'` (helper still writes underscore while `COGNEE_DATABASES` uses dot) | Re-run codemod on the missed file |
| `cognee.config.set_graph_database_provider is not a coroutine` (old per-key setter from a third-party lib) | Pin `cognee==1.2.2` (setter signature changed in 1.1+; 1.2.2 is sync) |

### 8.4 Rollback plan (5 minutes)

```bash
# Option B (preferred, < 5 min): pin to last pre-migration tag
ssh bunchloch 'cd kings_college_galway && git checkout v0.5.3-cognee-pinned && \
  docker compose -f infrastructure/stacks/cognee/compose.yaml -f sidecar.yaml up -d'

# Option A (< 10 min): revert the merge commit
ssh bunchloch 'cd kings_college_galway && git revert --no-commit HEAD && git commit -m "revert: cognee v1 API migration" && git push'

# Option C (< 2 min, data only): restore postgres snapshot
ssh bunchloch 'docker exec -i cianfhoghlaim-cognee-postgres psql -U cognee cognee_oideachais < /tmp/kg-pre-migration-*.sql'
```

### 8.5 Post-cutover telemetry (1 week)

- **Day 1-2**: Monitor `langfuse.cianfhoghlaim.ie` for `cognee.*` span latencies; expect a 5-10% increase from the new `remember` auto-cognify fold-in.
- **Day 3-7**: Track RAGAS `faithfulness` weekly; alert if drop > 2% from baseline 0.94.
- **Day 7+**: If no regressions, archive via `openspec archive 2026-06-29-cognee-v1-api-migration --yes`.

---

## Appendix A — Spec delta (for the openspec change)

```markdown
## MODIFIED Requirements
### Requirement: Cognee v1.0 memory API
The system SHALL use Cognee v1.0+ API surface (`remember`/`recall`/`forget`/`improve`).
Legacy v0.x API (`add`/`cognify`/`search`/`prune.prune_data`) SHALL NOT be called.

#### Scenario: New cognify call — **WHEN** a Dagster cognify asset materialises — **THEN** the helper calls `await cognee.remember(data, dataset_name=...)`

#### Scenario: Selective forget — **WHEN** a dataset is retired — **THEN** the cleanup is `await cognee.forget(dataset_name=...)`

## REMOVED Requirements
### Requirement: SearchType.INSIGHTS
**Reason**: removed from Cognee v1.x enum. **Migration**: replace with `SearchType.SUMMARIES`.

### Requirement: Per-key cognee.config setters
**Reason**: deprecated in Cognee v1.0. **Migration**: `set_graph_database_provider(X)` → `set("graph_database_provider", X)`.

## MODIFIED Requirements
### Requirement: Cognee dataset naming
Namespaced datasets SHALL use dot notation (`oideachais.aistear`, etc.); the underscore variant SHALL NOT be used.
```
