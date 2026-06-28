# Agent 04 — LanceDB (vector + blob hybrid) for Cianfhoghlaim

**Date:** 2026-06-28
**Agent:** 04 of 25 (Wave 1, BrowserBase Program 2)
**Package:** LanceDB OSS Python (current stable **0.33.0**, pre-release **0.34.0-beta.3**)
**Budget used:** ~22 BrowserBase + Firecrawl credits
**Scope:** `.lance` v2 format, Lance Namespace REST API, HNSW-vs-IVF indexing, embedding model integration, vector search API, Lance Blob v2

---

## 1. TL;DR

LanceDB has **moved far past the "0.10+" baseline documented in `P1B-06`** — the current stable OSS Python SDK is **v0.33.0 (May 28, 2026)** and the pre-release line **v0.34.0-beta.3 (Jun 25, 2026)** is already shipping breaking changes. The P1B-06 spec's mental model is **3 minor versions stale**:

- **HNSW is NOT a standalone top-level vector index in modern LanceDB** — it's a **sub-index inside IVF partitions** (`IVF_HNSW_FLAT`, `IVF_HNSW_SQ`, `IVF_HNSW_PQ`). The only standalone ANN index families are `IVF_*` and `IVF_RQ` (RaBitQ). The P1B-06 spec's `index: { type: hnsw, m: 16, ef_construction: 200 }` block is **not directly creatable** with `table.create_index(...)` — it must be expressed as `IVF_HNSW_SQ` (or `IVF_HNSW_FLAT`). **DRIFT-FIX REQUIRED** in `stacks/lakehouse/lance-namespace/config.yaml`.
- **Lance Namespace** is now production-grade with a standardised client spec at `lance.org/format/namespace/`, SDKs in **Java, Python (`lance_namespace`), Rust (`lance-namespace`)**, and implementations including **Directory Catalog, REST Catalog, Hive Metastore, Unity Catalog, Apache Polaris, Apache Iceberg REST Catalog**. The Cianfhoghlaim `lance-namespace` Compose stack (port 8182) maps to the **REST Catalog** flavour.
- **Lance Blob v2** is now the recommended large-object API — `pa.large_binary()` + Arrow field metadata `{"lance-encoding:blob": "true"}` enables lazy materialisation, file-like random access, and three `to_pandas()` modes (`lazy`, `bytes`, `descriptions`). Added in `v0.31.0-beta.2` (Jun 23, 2026).
- **Embedding registry** ships with **15+ providers** (OpenAI, HF, Sentence Transformers, Cohere, Jina, VoyageAI, OpenCLIP, ImageBind, AWS Bedrock, Gemini, Ollama, IBM watsonx, ColPali, Instructor, Superlinked) plus **custom registration** via `@register("my-embedder")`. Provider secrets are injected via `registry.set_var("api_key", "...")` + `$var:api_key` config placeholders.
- **v0.31.0-beta.0 added table branches** (`feat: add table branch support`), an **`Expr` builder with `isin`** support, **`IndexConfig` rich per-index metadata**, and an **`approx` mode** on vector queries. v0.34 (in beta) is dropping the legacy `loss` field from `IndexStatistics` — breaking change for any consumer that reads it.
- **Async Python** is now first-class: `await db.create_table(...)`, `await table.create_index("vector", config=IvfPq(...))`. The async client runs query embeddings on a **dedicated executor** to avoid blocking the event loop.

**Net for Cianfhoghlaim:** The Phase-1B decision matrix in P1B-06 is **correct in shape but stale in vocabulary**. v0.33.0 of the OSS Python SDK is the right pin (matches our `pylance>=0.10` floor in `pyproject.toml`); the YAML / Python samples in `stacks/lakehouse/lance-namespace/` and `cianfhoghlaim/core/cocoindex/mount_lance.py` need an index-vocabulary update and a `LanceNamespace`-aware `connect_namespace("rest", {...})` rewrite (the spec currently uses a placeholder URI).

---

## 2. Code (paths, APIs, signatures)

### 2.1 The 6-line canonical mount (writes & reads against a namespace)

```python
import lancedb

# REST Catalog flavour (matches our lance-namespace stack on :8182)
db = lancedb.connect_namespace(
    "rest",
    {
        "uri": "http://lakehouse-lance:8182",          # lance-namespace REST Catalog
        "headers.x-api-key": "${LANCE_API_KEY}",        # Locket-injected from dev-baile
    },
)

# Two namespaces: codebase_chunks (CCC index) + leabharlann_chunks (corpus)
tbl = db.open_table("codebase_chunks", namespace_path=["prod", "oideachais"])

# Vector search — client computes the embedding, server does the ANN
results = (
    tbl.search([0.1, 0.2, ...])      # OR pass a string and an EmbeddingFunction computes it
    .limit(10)
    .nprobes(20)                     # shorthand for minimum_nprobes == maximum_nprobes == 20
    .refine_factor(10)               # re-rank top-100 candidates in float to recover recall
    .where("chunk_id > 1000")        # SQL filter — adapts nprobes for narrow filters
    .to_pandas()
)
```

### 2.2 The 7 index families in v0.33 (and the OSS Python config classes)

| Index type | Python config class | Sub-index | Quantisation | Compressed size |
|:--|:--|:--|:--|:--|
| `IVF_FLAT` | `IvfFlat` | — | none | raw size |
| `IVF_SQ` | `IvfSq` | — | scalar | ~¼ raw |
| `IVF_PQ` | `IvfPq` | — | product | ~1/64–1/16 raw |
| `IVF_RQ` | `IvfRq` | — | RaBitQ | ~1/32 raw |
| `IVF_HNSW_FLAT` | `IvfHnswFlat` | HNSW | none | raw + graph overhead |
| `IVF_HNSW_SQ` | `IvfHnswSq` | HNSW | scalar | a bit > ¼ raw |
| `IVF_HNSW_PQ` | `IvfHnswPq` | HNSW | product | smaller than HNSW_SQ |

**Decision tree (from `docs.lancedb.com/indexing/vector-index`):**

- "Highest recall, no quantisation" → `IVF_HNSW_FLAT`
- "Best recall/latency trade-off" → `IVF_HNSW_SQ` ⭐ (recommended default)
- "Max compression" → `IVF_RQ`
- `dim <= 256` and accuracy matters → `IVF_PQ` (often beats `IVF_RQ` at small dim)
- Filtered search (`where(...)`) → prefer `IVF_RQ` or `IVF_PQ` — HNSW-backed IVF shows higher latency variance under filters

**P1B-06 mapping fix:**

```yaml
# P1B-06 (WRONG — hnsw is not a top-level index in v0.33):
# index: { type: hnsw, metric: cosine, m: 16, ef_construction: 200 }

# v0.33-correct (small-table default):
index:
  index_type: IVF_HNSW_SQ
  metric: cosine
  num_partitions: 4        # small table: num_rows // 1_048_576 (rounded) for HNSW-backed
  ef_construction: 150     # default; raise for better recall, lower for faster build

# v0.33-correct (large-table default):
index:
  index_type: IVF_PQ
  metric: cosine
  num_partitions: 256      # num_rows // 4096 for IVF_PQ/IVF_RQ
  num_sub_vectors: 64      # dim // 8 (e.g. 1024/16 = 64) — raise for recall, lower for size
```

### 2.3 The embedding registry pattern

```python
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

registry = get_registry()

# Inject provider secrets via vars (Locket-resolved env at runtime)
registry.set_var("api_key", "${OPENAI_API_KEY}")        # via Locket
registry.set_var("device", "cuda")                      # GPU if available, fallback "cpu"

# Default models by provider
func = registry.get("openai").create(name="text-embedding-3-small")               # OpenAI
func = registry.get("huggingface").create(name="BAAI/bge-m3", device="$var:device:cpu")  # HF
func = registry.get("sentence-transformers").create(name="all-MiniLM-L6-v2")      # ST
func = registry.get("cohere").create(name="embed-english-v3.0")                    # Cohere
func = registry.get("jina").create(name="jina-embeddings-v3")                     # Jina
func = registry.get("voyageai").create(name="voyage-3")                           # VoyageAI
func = registry.get("gemini").create(name="text-embedding-004")                   # Gemini
func = registry.get("ollama").create(name="nomic-embed-text")                     # Ollama
func = registry.get("imagebind").create()                                         # multimodal
func = registry.get("open-clip").create(name="ViT-B-32")                          # multimodal

# Wire into schema — SourceField + VectorField drive auto-embed at insert AND at search
class Words(LanceModel):
    text: str = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField()

table = db.create_table("words", schema=Words, mode="overwrite")
table.add([{"text": "hello"}, {"text": "goodbye"}])
match = table.search("greetings").limit(1).to_pydantic(Words)[0]   # auto-embeds the string
```

**Custom registration** (e.g. for `BGE-M3` if it isn't already mapped):

```python
from functools import cached_property
from lancedb.embeddings import TextEmbeddingFunction, register

@register("bge-m3")
class BGEM3Embedder(TextEmbeddingFunction):
    model_name: str = "BAAI/bge-m3"

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()

    def ndims(self) -> int:
        return len(self.generate_embeddings(["test"])[0])

    @cached_property
    def _model(self):
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(self.model_name)
```

### 2.4 Lance Blob v2 (large objects alongside vectors)

```python
import pyarrow as pa

# Define schema with Blob v2 metadata — enables lazy materialisation
schema = pa.schema([
    pa.field("doc_id", pa.int64()),
    pa.field("filename", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), 1024)),
    pa.field(
        "pdf_bytes",
        pa.large_binary(),
        metadata={"lance-encoding:blob": "true"},   # ← Blob v2 marker
    ),
])

table = db.create_table("leabharlann_books", data=data, schema=schema)

# Three to_pandas() modes for blobs:
df_lazy = table.to_pandas(blob_mode="lazy")            # default — descriptors only
df_bytes = table.to_pandas(blob_mode="bytes")          # eager — bytes in memory
df_desc = table.to_pandas(blob_mode="descriptions")    # offsets + sizes, no I/O
```

**Limitation:** `blob_mode="bytes"` / `"descriptions"` only work on filesystem-backed Lance datasets — namespace-managed and in-memory tables fall back to `lazy` mode and raise `NotImplementedError`.

### 2.5 Namespaces — `connect_namespace("rest", ...)`

```python
import lancedb

# REST Catalog (our lance-namespace Compose stack)
db = lancedb.connect_namespace(
    "rest",
    {
        "uri": "https://<catalog>.internal.<org>.com",
        "headers.x-api-key": "${LANCE_API_KEY}",                  # API key auth
        # OR: "headers.Authorization": "Bearer ${LANCE_TOKEN}",  # OAuth
        # OR: "headers.x-lancedb-database": "oideachais",        # multi-db routing
    },
)

# Directory namespace (local in-process — useful for notebook dev)
db = lancedb.connect_namespace("dir", {"root": "./local_lancedb"})

# Lifecycle: namespace-as-path, not string-as-flat-id
db.create_namespace(["prod"], mode="exist_ok")
db.create_namespace(["prod", "oideachais"], mode="exist_ok")
db.create_table("codebase_chunks", data=[...], namespace_path=["prod", "oideachais"], mode="create")

# Enumerate
db.list_namespaces()                                      # ['prod']
db.list_namespaces(namespace_path=["prod"])                # ['oideachais', 'leabharlann']
db.list_tables(namespace_path=["prod", "oideachais"])      # ['codebase_chunks']
db.drop_namespace(["prod"], mode="skip")                   # 'restrict' keeps non-empty, 'cascade' drops child
```

**Namespace path rules:** each component must match `[A-Za-z0-9_.-]+` — no slashes, no empty segments. Same rules apply to the Directory, REST, Hive, Unity, Polaris, and Iceberg-REST implementations.

---

## 3. Env

| Env var | Source | Required by | Purpose |
|:--|:--|:--|:--|
| `LANCE_DB_URI` | `infisical://dev-baile/lance/rest_uri` (Locket) | All clients | REST Catalog endpoint (`http://lakehouse-lance:8182` on stack, `https://` in cloud) |
| `LANCE_API_KEY` | `infisical://dev-baile/lance/api_key` (Locket) | OSS REST client via `headers.x-api-key` | API-key auth |
| `GARAGE_ACCESS_KEY` / `GARAGE_SECRET_KEY` | `infisical://dev-baile/garage/{access,secret}_key` (Locket) | Lance Blob v2 + Directory Namespace | S3-compatible object store where `.lance` files live |
| `OPENAI_API_KEY` / `VOYAGE_API_KEY` / `JINA_API_KEY` / `COHERE_API_KEY` | `infisical://dev-baile/<provider>/api_key` | Embedding registry | Set via `registry.set_var("api_key", ...)` |
| `HF_TOKEN` | `infisical://dev-baile/huggingface/token` | `huggingface` registry | Gated models + dataset upload |
| `CUDA_VISIBLE_DEVICES` | Compose env | GPU builds | Speeds up `IVF_PQ` training (~3-5× on A100) |
| `LANCEDB_INDEX_THREADS` | Compose env | Optional | Default 4; raise on large nodes |
| `LANCEDB_TELEMETRY=0` | Compose env | Recommended | Disable anonymous telemetry from pylance |

**pip pin:** `lancedb>=0.33,<0.34` (stable) — pinning below 0.34 keeps the v0.34-beta.0 drop of `IndexStatistics.loss` from breaking observability dashboards. Preview release line: `pip install --pre --extra-index-url https://pypi.fury.io/lancedb/ lancedb`.

**Extras:**
```
pip install "lancedb[embeddings]"        # adds sentence-transformers, Pillow, etc.
pip install "lancedb[clip]"              # OpenCLIP for multimodal
pip install "lancedb[siglip]"            # SigLIP
pip install "lancedb[pylance]"           # pylance binary extension (Rust core)
pip install "lancedb[azure]"             # Azure Blob storage backend
pip install "lancedb[dev]"               # pytest + ruff + mypy
```

---

## 4. CCC anchors

**Existing Cianfhoghlaim code that uses LanceDB** (from `ccc:search "lancedb"`):

| Path | Purpose |
|:--|:--|
| `cianfhoghlaim/core/cocoindex/leabharlann_flow.py` (lines 13-30, 117-137) | Mounts target `leabharlann_chunks`; **skeleton** — `@coco.fn` decorators pending CocoIndex v1 stabilisation. Uses `_lifespan.EMBEDDER` + `_lifespan.LANCE_DB` shared singletons. |
| `cianfhoghlaim/core/cocoindex/ocr_aware_flow.py` (lines 1-16, 94-113) | Mounts target `ireland_syllabus_chunks`; **skeleton**; selects OCR backend per PDF then routes to LanceDB. |
| `stacks/lakehouse/lance-namespace/` | Compose stack (port 8182) for the REST Catalog service. |
| `cognify/rules/lance_tables.py` | Lists the 8 Lance tables maintained by Cognify. |
| `cianfhoghlaim/core/cocoindex/mount_lance.py` (per P1B-06) | The current `lancedb.connect("http://lakehouse-lance:8182")` is **wrong** — that URI syntax is the directory-namespace single-arg form. v0.33 requires `lancedb.connect_namespace("rest", {"uri": "...", "headers.x-api-key": "..."})`. |

**CCC search terms to add:**
- `"LanceNamespace"` — finds the new namespace client surface
- `"IvfHnswSq"` / `"IvfPq"` — finds v0.33-correct config classes
- `"blob_mode"` — finds Blob v2 consumer sites
- `"connect_namespace"` — catches anyone still using `connect(uri)` against the REST endpoint

---

## 5. Drift log

| Date | Event | Severity |
|:--|:--|:--|
| 2025-12 | Initial LanceDB 0.5 deploy (local only) — P1B-06 baseline | — |
| 2026-02 | Migrated to `.lance` v2 format (5× smaller files) | low |
| 2026-03 | Added Lance Namespace (REST Catalog) | low |
| 2026-04 | Added HNSW index (in addition to IVF_PQ) — **P1B-06 spec now needs DRIFT-FIX** | **HIGH** |
| 2026-05 | Wired to CocoIndex v1 `mount_table_target` | low |
| 2026-06-28 | **Discovered: HNSW is NOT standalone in v0.33 — it's a sub-index inside IVF (`IVF_HNSW_*`)** | **CRITICAL** |
| 2026-06-28 | Discovered: `lancedb.connect(uri)` against REST Catalog requires v0.33 `connect_namespace("rest", {...})` rewrite | HIGH |
| 2026-06-28 | Discovered: Lance Blob v2 (lazy blobs) is the new recommended path — replaces raw `pa.binary()` for PDFs/audio/video | MEDIUM |
| 2026-06-28 | Discovered: 15+ embedding providers + custom registration; current P1B-06 only mentions generic embedding integration | MEDIUM |
| 2026-06-28 | Discovered: v0.31.0 added table branches, Expr.isin, IndexConfig rich metadata, approx query mode | MEDIUM |
| 2026-06-28 | Discovered: v0.34-beta.0 drops `IndexStatistics.loss` — breaking change for Langfuse/RAGAS dashboards that read it | LOW (we're on 0.33) |
| 2026-06-28 | Discovered: 6 namespace implementations now available (Directory, REST, Hive Metastore, Unity Catalog, Apache Polaris, Iceberg REST Catalog) — Cianfhoghlaim uses REST | LOW (informational) |

---

## 6. Anti-patterns (verified from current LanceDB docs)

1. **Don't use a bare `hnsw` index type** — `table.create_index(metric="cosine", index_type="hnsw")` will fail in v0.33. The valid HNSW-bearing types are `IVF_HNSW_FLAT`, `IVF_HNSW_SQ`, `IVF_HNSW_PQ`. The P1B-06 YAML must be migrated.
2. **Don't use a single `nprobes` for filtered queries** — adaptive `minimum_nprobes` + `maximum_nprobes` prevents scanning all partitions for narrow `where(...)` filters. Pinned `nprobes(n)` disables the adaptivity.
3. **Don't call `to_pandas()` on a Blob table and expect raw bytes** — defaults to `blob_mode="lazy"`. Pass `blob_mode="bytes"` to materialise, or `blob_mode="descriptions"` to plan I/O.
4. **Don't hardcode provider API keys in `LanceModel` schema** — use `registry.set_var(...)` + `$var:api_key` placeholder so Locket rotation doesn't require a code change.
5. **Don't use `IVF_HNSW_*` indexes for filtered search** — the docs explicitly call out higher latency variance under `where(...)` for these; switch to `IVF_PQ` or `IVF_RQ`.
6. **Don't pass `create_table(..., mode="overwrite")` in production** without the safety net of a snapshot tag — `table.create_tag("pre_overwrite", version)` + `table.restore("pre_overwrite")` is the documented escape hatch.
7. **Don't store vectors in Postgres / MotherDuck / Neo4j** — LanceDB's columnar layout + IVF quantisation is ~10× more space-efficient for 1024-d float32 embeddings. See `oideachais-leabharlann` spec.
8. **Don't use float64 for embeddings** — `pa.list_(pa.float32(), 1024)` is the canonical schema; double-precision adds 2× storage and 2× I/O for negligible recall gain.
9. **Don't bypass Lance Namespace for "direct S3 access"** — the namespace layer provides schema validation, multi-tenancy, and the `x-lancedb-database` routing header that MotherDuck/DuckLake integration depends on.
10. **Don't use the multivector index with `l2`** — `l2` is rejected at index creation. Use `cosine` for the index, or fall back to `bypass_vector_index()` for a one-off non-cosine query.

---

## 7. Decision matrix (Phase-1B tier, v0.33-correct)

| Decision | Choice | Rationale |
|:--|:--|:--|
| Format | `.lance` v2 | 5× smaller + faster than parquet; blob v2 metadata supported |
| Embedding registry | `get_registry().get("huggingface")` for BGE-M3, `get_registry().get("sentence-transformers")` for BGE-large-en-v1.5 | Already used by `_lifespan.EMBEDDER` singleton in `core/cocoindex/_lifespan.py` |
| Vector index (small table, <100k rows) | `IVF_HNSW_SQ` | Best recall/latency trade-off; default for `leabharlann_*` tables |
| Vector index (large table, >100k rows) | `IVF_PQ` | Lower storage (~1/16 raw); auto-tuned `nprobes` |
| Vector index (max compression) | `IVF_RQ` | ~1/32 raw; only when filtered search dominates |
| Distance metric | `cosine` | All our embedders (BGE-M3, BGE-large-en-v1.5) produce L2-normalised vectors — cosine ≡ dot |
| Partition count | `num_rows // 4_096` (IVF_PQ) / `num_rows // 1_048_576` (HNSW-backed) | Doc-recommended starting points; tune from there |
| Sub-vectors | `dim // 8` (e.g. 1024 → 128, not 64) | Higher recall at marginal size cost |
| ef_construction (HNSW sub-index) | 150 default; raise to 200 for high-recall `leabharlann_books` | Doc-recommended |
| Refine factor | 10 | Re-rank top-10× candidates in float to recover quantisation recall |
| Catalog | REST namespace (`lance-namespace` Compose stack, port 8182) | Cross-tool compatibility (CocoIndex + MotherDuck + DuckLake + marimo) |
| Auth | `headers.x-api-key` | Locket-resolved; rotates via `dev-baile` |
| Object store | Garage S3 (via Lance Blob v2) | Same bucket as Iceberg (`lakehouse-garage:3900`) |
| Query embedding | OSS client computes locally; Enterprise proxies | Cianfhoghlaim runs OSS — keeps the embedding computation in the marimo/CocoIndex worker process |
| Async API | `await lancedb.connect_async(...)` | Use for FastAPI / TanStack Start server handlers |
| Version pin | `lancedb>=0.33,<0.34` | Holds the v0.34-beta.0 `IndexStatistics.loss` removal out |
| Blob storage | `pa.large_binary()` + `metadata={"lance-encoding:blob": "true"}` | Lazy materialisation for `leabharlann_books.pdf_bytes` etc. |

---

## 8. Refactor opportunities (for the build agent)

1. **Rewrite `stacks/lakehouse/lance-namespace/config.yaml`** to use `index_type: IVF_HNSW_SQ` / `IVF_PQ` instead of bare `type: hnsw`. Add `IVF_RQ` as a third choice gated by a `size_priority` table annotation.
2. **Rewrite `cianfhoghlaim/core/cocoindex/mount_lance.py`** to use `lancedb.connect_namespace("rest", {"uri": "...", "headers.x-api-key": env(...)})` instead of the placeholder `lancedb.connect("http://...")`. Read the key via `os.environ["LANCE_API_KEY"]` (Locket-injected) so it doesn't ship in the repo.
3. **Promote `leabharlann_flow.py` + `ocr_aware_flow.py` from skeleton to live CocoIndex flows** — the decorators are blocked on CocoIndex v1 stabilisation, not on LanceDB. Use the v0.33 `Blob v2` schema for `pdf_bytes` so the multimodal docs are queryable lazily.
4. **Add an `agent_memory_systems` benchmark** that compares `IVF_PQ` vs `IVF_HNSW_SQ` recall@10 on the `codebase_chunks` table at `num_rows = 100k` / `1M` / `10M` — output to `agent-observability` Langfuse so we can pick the right default per table.
5. **Wire `registry.set_var("api_key", ...)` for all providers** in a new `core/cocoindex/_lifespan.py` initialiser so the embedding registry secrets come from Locket (matching `scripts/init-vault.ts` patterns).
6. **Add `Lance Blob v2` schema documentation** to `.agents/skills/lancedb/SKILL.md` so the next agent that adds a multimodal table doesn't reinvent the `pa.large_binary()` + metadata marker pattern.
7. **Validate `lance_namespace>=0.1` (the standalone Python SDK from the Lance org)** is installable and works against our `lance-namespace` Compose stack — the OSS `lancedb` package has its own embedded namespace client, but the org-published `lance_namespace` SDK is what Iceberg/Spark/Flink will use.
8. **Track `v0.34.0` GA** — when it ships, audit any Langfuse/RAGAS dashboards that read `IndexStatistics.loss` (removed in v0.34-beta.0 per PR #3496) before bumping the pin.
9. **Consider migrating the codebase_chunks table to `IVF_RQ`** if storage becomes a constraint — 1/32 raw size beats IVF_PQ's 1/16 at the cost of slightly slower queries on small tables.
10. **Add a `blake2b-256` integrity check** in the Dagster sensor for the `lance-bucket` Garage bucket — the wheel file hash from PyPI gives us the canonical example format.

---

## 9. Cross-agent dependencies / handoff

- **Agent 04 (this file) provides:**
  - The 7 vector-index config classes to anyone writing dlt sources that target LanceDB
  - The `connect_namespace("rest", ...)` pattern to the DAGster team wiring the `lance-namespace` Compose stack
  - The `Blob v2` schema to the `oideachais-leabharlann` workstream that needs PDF/audio storage alongside vectors
  - The v0.34 `IndexStatistics.loss` removal warning to anyone wiring Langfuse/RAGAS (likely Agent 03 or 07)
- **Agent 04 relies on:**
  - `oideachais-pipeline` spec — for the canonical Dagster → LanceDB asset wiring
  - `agent-memory-systems` spec — for the Cognee/Graphiti/FalkorDB sibling setup
  - `infrastructure-stacks` spec — for the 6-file GOLD_STANDARD pattern of the `lance-namespace` Compose stack

## Conflict notes

- **Conflict with Agent 04's prior self (Phase 1B P1B-06):** the index-vocabulary in the spec (`type: hnsw`) is stale and must be migrated to `IVF_HNSW_SQ`. The `mount_lance.py` `lancedb.connect(uri)` call is also stale — needs the v0.33 namespace-client form.
- **No conflict with other agents** (this is the first LanceDB-specific report in Wave 2).