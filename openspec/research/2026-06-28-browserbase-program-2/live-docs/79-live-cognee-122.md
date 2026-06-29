# Agent 79 — Live Cognee 1.2.2 verification

- **Agent**: 79 (live docs verifier) · **Verified**: 2026-06-29 UTC
- **Sources**: `https://docs.cognee.ai` (Mintlify), `https://docs.cognee.ai/llms.txt`, `https://pypi.org/pypi/cognee/json`, `https://github.com/topoteretes/cognee/releases/tag/v1.2.2`
- **Skill under review**: `.agents/skills/cognee/SKILL.md` (Wave 1, 693 lines, header `>=0.1.0 / Last Updated 2025-04`)

## 1. TL;DR

- **3 of the 5 task URLs return HTTP 404** — docs live at `/getting-started/`, `/cognee-mcp/`, `/python-api/`, not the Wave 1 paths.
- **cognee 1.2.2** released **2026-06-26** (Python `>=3.10,<3.15`) ships the **v1.0 API redesign**: `remember()` / `recall()` / `forget()` / `improve()` / `serve()` / `push()` replace Wave 1 `add()` + `cognify()` + `search()`.
- Skill is also stale on the **`SearchType` enum** (7 in skill, **15 live**), **MCP surface** (6 tools in skill, **14 live**), and storage paths (`lancedb_data` → `DATA_ROOT_DIRECTORY`/`SYSTEM_ROOT_DIRECTORY`).

## 2. Current version (verified live)

| Field | Value | Source |
|:--|:--|:--|
| Latest PyPI | **`cognee 1.2.2`** | `GET https://pypi.org/pypi/cognee/json` → `info.version` |
| Release date | **`2026-06-26T13:38:05Z`** | PyPI `urls[0].upload_time` |
| Python range | **`>=3.10, <3.15`** | PyPI `info.requires_python` |
| Docs platform | Mintlify on Vercel (`x-mintlify-client-version: 0.0.3140`) | HTTP headers |
| GH tag | `topoteretes/cognee@v1.2.2` — **"Truth Subspace & Retrieval Improvements"** | `/releases/tag/v1.2.2` → HTTP 200 |

Release cadence: 1.2.2 (2026-06-26) · 1.2.1 (2026-06-21) · 1.2.0 (2026-06-21) · 1.1.3 (2026-06-18) · 1.1.2 (2026-05-30).

## 3. Verbatim live code examples

Copied verbatim from `docs.cognee.ai/getting-started/{installation,quickstart}.md`, `python-api/{remember,recall,search-type}.md`, `cognee-mcp/mcp-tools.md`.
### 3.1 Base install

```bash
pip install cognee     # or:  uv pip install cognee
```

> "We use openai/gpt-5-mini for the LLM model and openai/text-embedding-3-large (3072 dimensions) for embeddings by default."
### 3.2 Ollama (local, no API key)

```bash
LLM_PROVIDER="ollama";   LLM_MODEL="llama3.1:8b"
LLM_ENDPOINT="http://localhost:11434/v1";   LLM_API_KEY="ollama"
EMBEDDING_PROVIDER="ollama";   EMBEDDING_MODEL="nomic-embed-text:latest"
EMBEDDING_ENDPOINT="http://localhost:11434/api/embed"
EMBEDDING_DIMENSIONS="768";    HUGGINGFACE_TOKENIZER="nomic-ai/nomic-embed-text-v1.5"
```
```bash
uv pip install "cognee[ollama]"
ollama pull llama3.1:8b && ollama pull nomic-embed-text:latest
```
### 3.3 Quickstart (v1.0)

```python
import cognee, asyncio

async def main():
    await cognee.forget(everything=True)
    await cognee.remember("Cognee turns documents into AI memory.")
    for r in await cognee.recall("What does Cognee do?"):
        print(r.text)
asyncio.run(main())
```

> "**`.remember`** — Stores data in memory. Under the hood it runs ingestion, chunking, entity extraction, graph building, and a follow-up enrichment pass. **`.recall`** — Retrieves from memory. It auto-routes the query to the best retrieval strategy and returns contextual results from the knowledge graph."
### 3.4 `cognee.remember()` signature

```python
async def remember(
    data: Union[BinaryIO, list[BinaryIO], str, list[str],
                DataItem, list[DataItem], MemoryEntry],
    dataset_name: str = "main_dataset",
    *, session_id: Optional[str] = None,
    chunk_size: Optional[int] = None, chunker: Optional[Any] = None,
    custom_prompt: Optional[str] = None,
    run_in_background: bool = False, self_improvement: bool = True,
    session_ids: Optional[List[str]] = None, **kwargs,
) -> RememberResult
```

Notable extras: `graph_model` (custom `DataPoint` subclass), `node_set: list[str]`, `dataset_id: UUID`, `importance_weight: float`, `incremental_loading: bool`, `data_per_batch: int`, `chunks_per_batch: int`, `temporal_cognify: bool`, `llm_config`, `embedding_config`.
### 3.5 `cognee.recall()` signature

```python
async def recall(
    query_text: str, query_type: SearchType | None = None,
    *, datasets: list[str] | None = None,
    dataset_ids: list[UUID] | None = None,
    top_k: int = 15, auto_route: bool = True,
    scope: str | list[str] | None = None, **kwargs,
) -> list[RecallResponse]
```

> Live quote: "These items are **Pydantic objects, not plain dictionaries** — read fields with attribute access (`result.text`), not `result.get("text")` or `result["text"]`. Calling `.get()` on a result raises `AttributeError: 'ResponseGraphEntry' object has no attribute 'get'`."

`source` discriminator values: `"graph"` (`ResponseGraphEntry`), `"session"` (`ResponseQAEntry`), `"trace"` (`ResponseAgentTraceEntry`), `"graph_context"` (`ResponseGraphContextEntry`). Per-item fields: `text, kind, search_type, score, dataset_id, dataset_name, metadata.{data_id, chunk_id, chunk_index, document_name}, raw, structured`.
### 3.6 Search with explicit `SearchType` + permanent-vs-session split

```python
from cognee import SearchType   # top-level; cognee.api.v1.search is the legacy path
results = await cognee.search("query", query_type=SearchType.GRAPH_COMPLETION)

result = await cognee.remember("Cognee turns documents into AI memory.", dataset_name="docs")
await cognee.remember("The customer prefers weekly updates.", session_id="sales_chat_1")
```
### 3.7 Loop over the Pydantic `RecallResponse` + restrict to a dataset

```python
results = await cognee.recall("What does Cognee do?", datasets=["docs"], top_k=5)
for r in results:
    if r.source == "graph":
        print(r.text);  print(r.raw)         # attribute access only
    elif r.source == "session":
        print(r.answer)
ctx_only = await cognee.recall("...", top_k=20, only_context=True)   # skip final LLM
```
### 3.8 MCP client config (14 tools exposed)

> Live quote: "Cognee MCP currently exposes 14 tools for memory management, retrieval, and dataset operations."

Tools (all 14, from `cognee-mcp/mcp-tools.md`):

- **v1.0 memory** (recommended): `remember`, `recall`, `forget`, `improve`
- **Legacy**: `cognify`, `search`, `prune`
- **Retrieval helpers** (not in API mode): `get_document`, `get_chunk_neighbors`
- **Interaction capture**: `save_interaction`
- **Data management**: `list_data`, `delete`, `delete_dataset`, `cognify_status`

```jsonc
// Add to Cursor / Claude / Continue / Cline / Codex
{ "mcpServers": { "cognee": {
    "url": "http://localhost:8000/mcp", "transport": "http" } } }
```

MCP quirks: `datasets` / `session_ids` are **CSV strings** (not JSON arrays); `top_k ∈ [1, 100]`; `recall` only takes dataset **names** (no `dataset_ids`); `prune` not in API mode.

## 4. Live changelog since Wave 1 (last-touched 2025-04)
### 4.1 v1.2.2 — 2026-06-26 — "Truth Subspace & Retrieval Improvements"

> "This release introduces a new 'truth subspace': a compact index built from distilled, accepted session learnings that helps rerank search results and weight feedback. It also activates an opt-in learned feedback signal for retrieval, fixes LanceDB S3 issues, and adds demos and tests to showcase the new reranking workflow."

**Breaking:** none (opt-in; `feedback_influence` default = 0.0).
**New:** `truth_subspace/` package (`align.py`, `build.py`, `centroids.py`, `models.py`, `constants.py`); centroid-slot truth weighting (MVP); truth-subspace reranking + learned-feedback activation; `build_truth_subspace` flag on `improve()`; demos `examples/demos/truth_centroid_slots_demo.py` and `examples/python/truth_subspace_reranking_demo.py`.
**Improvements:** `DEFAULT_FEEDBACK_INFLUENCE` env var, sha256 truth signatures, tighter centroid session filtering, `current_dataset_id` context var, clarified Claude Code plugin README.
**Fixes:** LanceDB S3, doc/API hygiene. Compat: Python `>=3.10,<3.15` · pydantic `>=2.10.5` · litellm `>=1.83.7` · fastapi `>=0.116.2,<1.0.0` · sqlalchemy `>=2.0.39,<3.0.0` · lancedb `>=0.24.3,<1.0.0` · ladybug `>=0.16.0,<0.18`.
### 4.2 v1.2.0 / v1.2.1 (2026-06-17 → 2026-06-21) — v1.0 API redesign

Docs now label `add` / `cognify` / `search` / `memify` / `prune` as **Legacy Operations**: *"These are the default v1.0 entry points for storing, querying, enriching, and deleting memory."* (`python-api.md`)
### 4.3 v1.1.x — packaging + DB extras

`installation.md` extras table now lists **27 extras** (`postgres`, `postgres-binary`, `neo4j`, `neptune`, `chromadb`, `graphiti`, `docs`, `docling`, `scraping`, `codegraph`, `langchain`, `llama-index`, `dlt`, `distributed`, `redis`, `aws`, `baml`, `tracing`, `posthog`, `deepeval`, `evals`, `notebook`, `dev`, `debug`, plus 8 provider extras `anthropic`/`groq`/`mistral`/`huggingface`/`ollama`/`llama-cpp`/`azure`/`fastembed`). Wave 1 skill only mentions 6 stores + 5 graph DBs.

## 5. Drift items vs Wave 1

| # | Item | Wave 1 | Live 1.2.2 |
|:-:|:--|:--|:--|
| D1 | **Docs URL paths** | `/get-started/installation`, `/sdk-api-reference`, `/integrations/mcp-server` | All three **HTTP 404**. Live: `/getting-started/installation`, `/python-api`, `/cognee-mcp/mcp-tools` |
| D2 | **SDK header** | `>=0.1.0` | **`1.2.2`** (2026-06-26) — bump header to `>=1.0.0,<2` |
| D3 | **Primary API** | `add()` + `cognify()` + `search()` | `remember()` + `recall()` + `improve()` + `forget()` + `serve()` + `push()` |
| D4 | **Clean-slate** | `cognee.prune.prune_data()` / `prune_system()` | `cognee.forget(everything=True)` / `forget(dataset=...)` |
| D5 | **`SearchType` enum** | 10 named incl. `CODE`, `INSIGHTS` | **15 values**, default `GRAPH_COMPLETION`. Removed `CODE` (→`CODING_RULES`), `INSIGHTS`. New: `TRIPLET_COMPLETION`, `GRAPH_COMPLETION_DECOMPOSITION`, `GRAPH_SUMMARY_COMPLETION`, `NATURAL_LANGUAGE`, `GRAPH_COMPLETION_CONTEXT_EXTENSION`, `CHUNKS_LEXICAL` |
| D6 | **Result shape** | `dict`-style `r["text"]` / `r.get("text_result")` | **Pydantic** objects, attribute access; `r.text`, `r.raw`, `r.metadata.{data_id, chunk_id, chunk_index, document_name}` |
| D7 | **MCP surface** | 6 tools | **14 tools** (see §3.10) |
| D8 | **MCP packaging** | `from cognee import MCP; MCP().start()` | `cognee-mcp` is a **separate PyPI package**; modes **Standalone** (own DB) or **API** (shared REST) |
| D9 | **Install extras** | not catalogued | 27 extras catalogued |
| D10 | **Storage paths** | `VECTOR_DATABASE_URL="./lancedb_data"` | `.env`-driven: `DATA_ROOT_DIRECTORY="~/.cognee_data"` + `SYSTEM_ROOT_DIRECTORY="~/.cognee_system"`; `load_dotenv()` at import |
| D11 | **Python range** | not stated | **`>=3.10,<3.15`** |
| D12 | **Default LLM** | `gpt-4o-mini` / `text-embedding-3-large` | `openai/gpt-5-mini` / `openai/text-embedding-3-large` (3072-d) |
| D13 | **Config API** | `await cognee.config.set_llm_provider(...)` | Per-call `LLMConfig` / `EmbeddingConfig` dataclasses (`cognee.infrastructure.llm.config`, `cognee.infrastructure.databases.vector.embeddings.config`); env-driven default, no `await` |
| D14 | **Multi-user / sharing** | not covered | per-user dataset scoping (`datasets=[name]` owner-scoped; `dataset_ids=[UUID]` for shared); MCP `recall` name-only |
| D15 | **Truth subspace (1.2.2)** | not covered | `truth_subspace/` package; `build_truth_subspace=True` on `improve()`; `DEFAULT_FEEDBACK_INFLUENCE` (default `0.0` = off) |
| D16 | **KCG image tag** | `cognee/cognee:latest` (v1.1.2) | bump to **`cognee/cognee:1.2.2`** |

## 6. Skill file update — exact diffs for `.agents/skills/cognee/SKILL.md`
### 6.1 Front-matter (line 8) + Resources (lines 627–631)

```diff
-**Version:** >=0.1.0 | **Last Updated:** 2025-04
+**Version:** >=1.0.0,<2 (v1.0 surface) — verified against **cognee 1.2.2** (PyPI 2026-06-26) | **Last Updated:** 2026-06-29
+**Live docs root:** https://docs.cognee.ai (Mintlify) | **Verified URLs:** `/getting-started/{installation,quickstart}`, `/python-api`, `/python-api/{remember,recall,search-type}`, `/cognee-mcp/{mcp-overview,mcp-tools}` | **llms.txt:** https://docs.cognee.ai/llms.txt
+**Python:** >=3.10,<3.15 | **Default LLM:** openai/gpt-5-mini | **Default embeddings:** openai/text-embedding-3-large (3072-d)
```
```diff
 ## Resources
-- **Documentation**: https://docs.cognee.ai
-- **GitHub**: https://github.com/topoteretes/cognee
-- **Website**: https://www.cognee.ai
+- **Documentation**: https://docs.cognee.ai
+- **GitHub**: https://github.com/topoteretes/cognee
+- **Website**: https://www.cognee.ai
+- **PyPI**: https://pypi.org/project/cognee/  (latest **1.2.2**, 2026-06-26)
+- **llms.txt (LLM sitemap)**: https://docs.cognee.ai/llms.txt
+- **Verified URLs (Wave 2)**: `/getting-started/installation` · `/getting-started/quickstart` · `/python-api/{remember,recall,search-type}` · `/cognee-mcp/{mcp-overview,mcp-tools}` · GitHub `/releases/tag/v1.2.2`
```
### 6.2 Replace `### 1. ECL Pipeline` (lines 36–50)

```diff
-### 1. ECL Pipeline (Extract-Cognify-Load)
+### 1. v1.0 Pipeline (Remember → Recall)
 ```python
 import cognee
-await cognee.add(content, dataset_name="my_dataset")            # Extract
-await cognee.cognify()                                         # Cognify
-from cognee.api.v1.search import SearchType                     # + Load/Search
-results = await cognee.search("Your question", query_type=SearchType.GRAPH_COMPLETION)
+# Store: ingestion + chunking + extraction + graph + enrichment in one call
+result = await cognee.remember("Your data", dataset_name="my_dataset")
+# Retrieve: auto-routes between session memory and the graph (Pydantic objects, not dicts)
+for r in await cognee.recall("Your question", top_k=10):
+    print(r.text)                                                # r.source ∈ {"graph","session","trace","graph_context"}
 ```
+The older ECL surface (`add` + `cognify` + `search` + `memify` + `prune`) is still
+available under **Legacy Operations** — see https://docs.cognee.ai/python-api.
```
### 6.3 Replace `### 2. Configuration` (lines 52–76)

```diff
-### 2. Configuration
+### 2. Configuration (.env + LLMConfig; no more `await cognee.config`)
 ```python
-import cognee
-import os
-os.environ["LLM_API_KEY"] = "your-openai-key"
-await cognee.config.set_llm_provider("openai")
-await cognee.config.set_graph_database_provider("neo4j")
-await cognee.config.set_vector_database_provider("lancedb")
-await cognee.config.set_vector_database_url("./lancedb_data")
-await cognee.config.set_embedding_provider("openai")
-await cognee.config.set_embedding_model("text-embedding-3-large")
+# Cognee calls `load_dotenv()` at import. Drop this in `.env` next to your code:
+#   LLM_API_KEY="sk-..."  LLM_PROVIDER="openai"  LLM_MODEL="openai/gpt-5-mini"
+#   EMBEDDING_PROVIDER="openai"  EMBEDDING_MODEL="openai/text-embedding-3-large"  # 3072-d
+#   DATA_ROOT_DIRECTORY="~/.cognee_data"             # replaces ./lancedb_data
+#   SYSTEM_ROOT_DIRECTORY="~/.cognee_system"
+#   DEFAULT_FEEDBACK_INFLUENCE="0.0"                  # opt-in (1.2.2 truth-subspace)
+import cognee
+# Per-call override:
+from cognee.infrastructure.llm.config import LLMConfig
+from cognee.infrastructure.databases.vector.embeddings.config import EmbeddingConfig
+await cognee.remember("...", dataset_name="docs",
+    llm_config=LLMConfig(provider="anthropic", model="claude-3-5-sonnet", api_key="..."),
+    embedding_config=EmbeddingConfig(provider="openai", model="text-embedding-3-large"))
 ```
```
### 6.4 Replace `### 4. Search Types` (lines 100–147)

```diff
-### 4. Search Types
+### 4. Search Types (15 values; `GRAPH_COMPLETION` is default)
 ```python
-from cognee.api.v1.search import SearchType
-(… CHUNKS / INSIGHTS / GRAPH_COMPLETION / SUMMARIES / CODE / CYPHER / FEELING_LUCKY …)
+from cognee import SearchType                                          # top-level; cognee.api.v1.search is legacy
+# 0-LLM-call: CHUNKS, CHUNKS_LEXICAL, SUMMARIES, CYPHER
+# Default (1 LLM): GRAPH_COMPLETION
+# High-depth (multi-LLM): GRAPH_COMPLETION_DECOMPOSITION, _COT, _CONTEXT_EXTENSION
+ans      = await cognee.recall("...", query_type=SearchType.GRAPH_COMPLETION)
+ctx_only = await cognee.recall("...", only_context=True, top_k=20)   # skip final LLM
+results  = await cognee.recall("...", auto_route=True, top_k=10)     # let Cognee pick
+for r in ans:                                                          # Pydantic, NOT dicts
+    if r.source == "graph":
+        print(r.text)                                                 # .get(...) raises AttributeError
+# 15 values verbatim: SUMMARIES, CHUNKS, CHUNKS_LEXICAL, RAG_COMPLETION, TRIPLET_COMPLETION,
+# GRAPH_COMPLETION (default), GRAPH_COMPLETION_DECOMPOSITION, GRAPH_SUMMARY_COMPLETION,
+# CYPHER, NATURAL_LANGUAGE, GRAPH_COMPLETION_COT, GRAPH_COMPLETION_CONTEXT_EXTENSION,
+# FEELING_LUCKY, TEMPORAL, CODING_RULES
 ```
```
> "The biggest cost driver is how many LLM calls a search type makes." (`/python-api/search-type`)
### 6.5 Replace `### 5. Dataset Management` (lines 149–172)

```diff
-### 5. Dataset Management
+### 5. Dataset Management
 ```python
-await cognee.add(data1, dataset_name='dataset_a')              # Scoped queries
-await cognee.add(data2, dataset_name='dataset_b')
-await cognee.cognify()
-results = await cognee.search(query_text="query", node_name="dataset_a", top_k=5)
-await cognee.prune.prune_data()                                # Clear all data
-await cognee.prune.prune_system(metadata=True)                 # Full system reset
-await cognee.delete(data_id)                                   # Delete specific data
+await cognee.remember(data1, dataset_name='dataset_a')          # Per-dataset scoped storage
+await cognee.remember(data2, dataset_name='dataset_b')
+results = await cognee.recall(query_text="query", datasets=["dataset_a"], top_k=5)
+await cognee.forget(everything=True)                            # v1.0 clean-slate (replace prune)
+await cognee.forget(dataset="dataset_a")                        # delete one dataset
+await cognee.prune.prune_data(); await cognee.prune.prune_system(metadata=True)   # legacy; deprecated
+# Per-item delete via `cognee.datasets` (the `cognee.delete(data_id)` helper is deprecated)
 ```
```
### 6.6 Replace the MCP subsection (lines 339–355)

```diff
-### MCP Integration
-from cognee import MCP
-cognee_server = MCP(); cognee_server.start()
-# Available functions: cognify, save_interaction, search, list_data, delete, prune
+### MCP Integration (`cognee-mcp` package, **14 tools**)
+
+The MCP server is the **separate PyPI package `cognee-mcp`** (bundles Cognee library).
+Two modes: **Standalone** (server owns DB) or **API** (talks to a remote Cognee REST API).
+
+```bash
+docker run -p 8000:8000 -e LLM_API_KEY=$OPENAI_API_KEY \
+  cognee/cognee:latest cognee-mcp --transport http --host 0.0.0.0 --port 8000
+```
+```jsonc
+// Cursor / Claude / Continue / Cline / Codex
+{ "mcpServers": { "cognee": { "url": "http://localhost:8000/mcp", "transport": "http" } } }
+```
+
+**Tools (14, verbatim from `cognee-mcp/mcp-tools`):** v1.0 memory (recommended): `remember`, `recall`, `forget`, `improve`; Legacy: `cognify`, `search`, `prune`; Retrieval helpers (not in API mode): `get_document`, `get_chunk_neighbors`; Interaction capture: `save_interaction`; Data management: `list_data`, `delete`, `delete_dataset`, `cognify_status`.
+
+MCP quirks: `datasets` / `session_ids` are **CSV strings**; `top_k ∈ [1, 100]`; `recall` only takes dataset **names** (not `dataset_ids`); `prune` not in API mode.
+
+> "For new integrations, prefer the v1.0 memory tools (`remember`, `recall`, `forget`)."
```


```diff
-`cognee/cognee:latest` (v1.1.2) on port 8100
+`cognee/cognee:1.2.2` (verified live 2026-06-29) on port 8100
 services:
   cognee:
-    image: cognee/cognee:latest
+    image: cognee/cognee:1.2.2
     ports: ["8100:8000"]
     environment:
       LLM_API_KEY: ${DEEPSEEK_API_KEY}
       LLM_PROVIDER: openai
       LLM_MODEL: deepseek-chat
       LLM_ENDPOINT: https://api.deepseek.com/v1
       EMBEDDING_PROVIDER: openai
       EMBEDDING_MODEL: text-embedding-3-small
       GRAPH_DATABASE_PROVIDER: neo4j
       GRAPH_DATABASE_URL: bolt://host.docker.internal:7687
       VECTOR_DATABASE_PROVIDER: lancedb
+      DEFAULT_FEEDBACK_INFLUENCE: "0.0"     # opt-in (1.2.2 truth-subspace)
```

## 7. URL patterns + session protocol

**Live URLs (HTTP 200):** `https://docs.cognee.ai/getting-started/{introduction,installation,quickstart}.md`; `https://docs.cognee.ai/python-api.md` + `/python-api/{remember,recall,search-type,add,cognify,search,memify,forget,improve,datasets,config,delete,update,prune,serve,push,run-migrations,custom-pipeline,data-models}.md`; `https://docs.cognee.ai/cognee-mcp/{mcp-overview,mcp-tools,setup,mcp-quickstart,mcp-local-setup,integrations,mcp-cloud-connection}.md`; `https://docs.cognee.ai/llms.txt` (advertised in `<link rel="llms-txt">`); `.well-known/mcp/server-card.json` advertised in `Link:` headers; Mintlify on Vercel (`server: Vercel`, `x-mintlify-client-version: 0.0.3140`); GitHub `https://github.com/topoteretes/cognee/releases/tag/v1.2.2` → 200; PyPI `https://pypi.org/pypi/cognee/json` → v1.2.2 (2026-06-26).

**Anti-patterns:** top-level `from cognee import SearchType` (not `cognee.api.v1.search`); `RecallResponse` items are **Pydantic** (`.get()` raises `AttributeError`); drop `await cognee.config.set_*` (use `.env` + `LLMConfig`/`EmbeddingConfig` dataclasses); replace `VECTOR_DATABASE_URL="./lancedb_data"` with `DATA_ROOT_DIRECTORY="~/.cognee_data"`; live exposes **14 MCP tools** (not 6); pin KCG image to `:1.2.2` for reproducibility.

**Session:** 5× `browserbase_navigate` + 3× `browserbase_extract` on JS-heavy Mintlify pages; 5× `curl` on `.md` exports + PyPI JSON.
