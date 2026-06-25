---
name: embedding-pipeline
description: Embedding pipeline patterns — enforced batching (MIN_EMBEDDING_BATCH_SIZE=100), accumulator (stream-bounded batching), multi-model selection (BGE-M3 for multilingual, GaBERT for Irish), semantic chunking, code-aware chunking with tree-sitter, HNSW lifecycle. Use when designing the Python pipeline that produces vectors for a vector DB (LanceDB, Convex, etc.).
---

# Embedding Pipeline

## When to use this skill

Use when you need to:

- "Design the embedding pipeline for a new corpus"
- "Enforce the 100-batch minimum for inference"
- "Add a new embedding model to the multi-model router"
- "Chunk code with tree-sitter for the códeolas workspace"
- "Drop + recreate the HNSW index after a bulk insert"
- "Bounded-batching for streaming sources (Firecrawl, Kafka)"

## Overview

The embedding pipeline is the Python layer that produces
vectors for a vector DB. The canonical KCG model is
`BAAI/bge-m3` (1024-d, multilingual, MIT-licensed) — but the
embedding pipeline skill covers the **infrastructure** around
the model, not the model itself (see
`.agents/skills/lancedb/SKILL.md` §13 for the BGE-M3
convention).

The 6 patterns:

1. **BatchedEmbeddingService** — enforces the 100-batch
   minimum (a 100× performance rule)
2. **EmbeddingAccumulator** — stream-bounded batching
3. **MultiModelEmbedder** — content-aware model selection
4. **Semantic chunking** (per content type)
5. **Code-aware chunking** with tree-sitter
6. **HNSW lifecycle** — `managed_bulk_insert` context manager

## 1. BatchedEmbeddingService (the 100-batch minimum)

```python
from typing import Sequence
import os
import httpx


class BatchedEmbeddingService:
    """Enforce the MIN_EMBEDDING_BATCH_SIZE = 100 performance rule."""

    MIN_BATCH_SIZE = 100  # KCG production: 100× speedup over per-text

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name
        self.endpoint = os.environ["EMBEDDING_ENDPOINT"]

    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if len(texts) < self.MIN_BATCH_SIZE:
            raise ValueError(
                f"Too few texts ({len(texts)}); minimum is "
                f"{self.MIN_BATCH_SIZE}. Batch up to MIN_BATCH_SIZE first."
            )
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                self.endpoint,
                json={"model": self.model_name, "texts": list(texts)},
            )
            response.raise_for_status()
            return response.json()["embeddings"]
```

**Why 100?** The KCG production benchmark shows a 100×
speedup (per-call setup cost is amortised across the batch).
For < 100 texts, batch up with `EmbeddingAccumulator` (Pattern 2).

## 2. EmbeddingAccumulator (stream-bounded batching)

```python
import asyncio
import time


class EmbeddingAccumulator:
    """Stream-bounded batching with explicit timeout fallback."""

    def __init__(
        self,
        service: BatchedEmbeddingService,
        max_batch_size: int = 1000,
        max_wait_sec: float = 5.0,
    ):
        self.service = service
        self.max_batch_size = max_batch_size
        self.max_wait_sec = max_wait_sec
        self._queue: list[str] = []
        self._lock = asyncio.Lock()

    async def add(self, text: str) -> None:
        async with self._lock:
            self._queue.append(text)
            if len(self._queue) >= self.max_batch_size:
                await self._flush()

    async def _flush(self) -> None:
        if not self._queue:
            return
        batch, self._queue = self._queue, []
        await self.service.embed(batch)

    async def flush_with_timeout(self, timeout_sec: float = 30.0) -> None:
        """Flush with timeout — if 100-batch not reached in 30s, flush anyway."""
        deadline = time.monotonic() + timeout_sec
        while self._queue and time.monotonic() < deadline:
            await asyncio.sleep(0.1)
        await self._flush()
```

Use for streaming sources (Firecrawl subscription, Kafka topic,
SSE feed) where you can't control the input rate.

## 3. MultiModelEmbedder (content-aware model selection)

```python
from enum import Enum


class EmbeddingModel(str, Enum):
    BGE_M3 = "BAAI/bge-m3"               # 1024-d, multilingual
    GABERT = "DCU-NLP/bert-base-irish-cased-v1"  # 768-d, Irish only
    E5_LARGE = "intfloat/multilingual-e5-large"  # 1024-d, multilingual


class MultiModelEmbedder:
    """Route content to the right embedding model based on language + content type."""

    ROUTING = {
        "ga": EmbeddingModel.GABERT,    # Irish → GaBERT (linguistic accuracy)
        "default": EmbeddingModel.BGE_M3,  # anything else → BGE-M3
    }

    def __init__(self, models: dict[EmbeddingModel, BatchedEmbeddingService]):
        self.models = models

    async def embed(
        self, texts: list[str], language: str = "default",
    ) -> list[list[float]]:
        model = self.ROUTING.get(language, EmbeddingModel.BGE_M3)
        return await self.models[model].embed(texts)
```

**KCG routing rule**:
- Irish (`ga`) → GaBERT (768-d, native-speaker-trained for
  phonological features: séimhiú, urú, dialectal variation)
- Everything else → BGE-M3 (1024-d, multilingual, 100+ languages)

## 4. Semantic chunking (per content type)

```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter,
)


SPLITTERS = {
    "markdown": MarkdownTextSplitter(chunk_size=2000, chunk_overlap=200),
    "python": PythonCodeTextSplitter(chunk_size=2000, chunk_overlap=200),
    "rust": RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150),
    "default": RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200),
}


def chunk(content: str, content_type: str) -> list[str]:
    return SPLITTERS[content_type].split_text(content)
```

**KCG chunk sizes** (from `EMBEDDINGS.md`):
- Markdown: 2000 chars, 200 overlap
- Code: 2000 chars, 200 overlap
- Default: 2000 chars, 200 overlap

## 5. Code-aware chunking with tree-sitter (for `códeolas`)

For the `códeolas` workspace (the code-intelligence layer of
Cianfhoghlaim), use tree-sitter to chunk at AST boundaries
(function, class, method — not arbitrary characters):

```python
import tree_sitter_python
from tree_sitter import Language, Parser


PY_LANGUAGE = Language(tree_sitter_python.language())


def chunk_python_code(source: str) -> list[dict]:
    """Chunk Python at function / class / method boundaries."""
    parser = Parser(PY_LANGUAGE)
    tree = parser.parse(bytes(source, "utf8"))

    chunks = []
    for node in tree.root_node.children:
        if node.type in ("function_definition", "class_definition"):
            chunks.append({
                "text": source[node.start_byte:node.end_byte],
                "type": node.type,
                "name": source[node.child_by_field_name("name").start_byte:node.child_by_field_name("name").end_byte],
            })
    return chunks
```

Tree-sitter supports 40+ languages (Python, JS, TS, Rust, Go,
C++, etc.). The KCG canonical set: Python, JS/TS, Rust, Go,
Cython, HCL.

## 6. HNSW lifecycle (managed_bulk_insert)

```python
from contextlib import contextmanager


@contextmanager
def managed_bulk_insert(table, drop_threshold: int = 50_000):
    """Drop the HNSW index before a bulk insert; rebuild after.

    The lancedb skill's recommendation: drop HNSW above 50k rows.
    This context manager enforces that rule.
    """
    has_index = table.has_index("vector_idx")
    if has_index and table.count_rows() > drop_threshold:
        table.drop_index("vector_idx")
    try:
        yield table
    finally:
        if has_index and table.count_rows() > drop_threshold:
            table.create_index(
                metric="cosine",
                index_type="HNSW",
                m=20,
                ef_construction=150,
            )
```

```python
with managed_bulk_insert(table) as t:
    t.add(rows)  # no HNSW rebuild during insert
```

## 7. Index configuration by vector count

| Vector count | Index type | Parameters | Rebuild time |
|--:|:--|:--|--:|
| < 100K | None (brute force) | — | 0 |
| 100K - 1M | HNSW | `m=20, ef_construction=150` | < 1 min |
| 1M - 10M | HNSW | `m=32, ef_construction=200` | 1-10 min |
| 10M - 100M | IVF_PQ | `num_partitions=256, num_sub_vectors=16` | 10-60 min |
| > 100M | Distributed (Lance-Ray) | `lr.create_scalar_index` | hours |

See `.agents/skills/lancedb/SKILL.md` §"Index Selection Guide"
for the full table.

## KCG integration

- The `BatchedEmbeddingService` is wired into the
  `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py` CocoIndex
  v1 App (batches the 33+ Ireland curriculum embeddings)
- The `MultiModelEmbedder` routes Irish to GaBERT, everything
  else to BGE-M3 (the KCG canonical)
- The `managed_bulk_insert` context manager is wrapped by the
  `oideachais-cocoindex-bulk-index` Dagster asset
- The `EmbeddingAccumulator` is used in the streaming Firecrawl
  pipeline (`sruth/oideachais/dlt_sources/official_media/firecrawl_streaming.py`)

## Related skills

- `.agents/skills/lancedb/SKILL.md` — vector DB (BGE-M3,
  hybrid search, HNSW, multimodal)
- `.agents/skills/cocoindex/SKILL.md` — embedding + indexing
  in CocoIndex v1 Apps
- `.agents/skills/celtic-language-ai/SKILL.md` — model catalog
  by language (GaBERT, BGE-M3, Helsinki OPUS-MT, NLLB-200)
- `.agents/skills/dlt/SKILL.md` — DLT pipelines for corpus
  ingestion
- `.agents/skills/dagster/SKILL.md` — Dagster assets for the
  embedding pipeline
- `.agents/skills/modal/SKILL.md` — Modal H100 for burst
  embedding workloads

## Resources

- BGE-M3: <https://huggingface.co/BAAI/bge-m3>
- GaBERT: <https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1>
- tree-sitter: <https://tree-sitter.github.io/tree-sitter/>
- LangChain text splitters: <https://python.langchain.com/docs/modules/data_connection/document_transformers/>
