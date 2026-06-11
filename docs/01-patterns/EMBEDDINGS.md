---
title: 'Pattern: Embeddings (Batching, Models, Indexes)'
domain: 'patterns'
status: 'stable'
description: '| Constraint | Description | Violation Consequence | |------------|-------------|----------------------| | **BATCH MINIMUM 100** | Never embed fewer than 100 texts per API call | 100x performance degradation | | **HNSW DROP >50 rows** | Drop index before bulk insert, recreate aft'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/EMBEDDINGS.md
ccc_query_hints:
  - pattern: embeddings (batching, models, i
---

# Pattern: Embeddings (Batching, Models, Indexes)

## Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **BATCH MINIMUM 100** | Never embed fewer than 100 texts per API call | 100x performance degradation |
| **HNSW DROP >50 rows** | Drop index before bulk insert, recreate after | 20x slower inserts |
| **Normalize embeddings** | Always normalize for cosine similarity | Incorrect similarity scores |
| **Match training context** | Chunk size should match model's training context | Poor retrieval quality |
| **Language-specific models** | Use specialized models for Celtic languages | 20% accuracy drop |

---

## Performance Impact

| Scenario | Time | Notes |
|----------|------|-------|
| Unbatched 1000 texts | ~100s | One API call per text |
| Batched 1000 texts | ~1s | Single batched call |
| **Improvement** | **100x** | MANDATORY for production |

---

## Batching Patterns

### Pattern 1: Batched Embedding Service (MANDATORY)

**When to use**: ALL embedding operations.

**Implementation**:
```python
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# MANDATORY: Minimum batch size for embeddings
MIN_EMBEDDING_BATCH_SIZE = 100

class BatchedEmbeddingService:
    """Embedding service with enforced batching."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str = "auto",
    ):
        self.model = SentenceTransformer(model_name)
        if device == "auto":
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(device)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = MIN_EMBEDDING_BATCH_SIZE,
    ) -> np.ndarray:
        """
        Embed texts with enforced minimum batch size.

        Args:
            texts: List of texts to embed
            batch_size: Batch size (enforced minimum 100)

        Returns:
            Normalized embeddings as numpy array
        """
        # Enforce minimum batch size
        if batch_size < MIN_EMBEDDING_BATCH_SIZE:
            logger.warning(
                f"Batch size {batch_size} below minimum {MIN_EMBEDDING_BATCH_SIZE}. "
                "Using minimum for performance."
            )
            batch_size = MIN_EMBEDDING_BATCH_SIZE

        # Log performance warning for small inputs
        if len(texts) < MIN_EMBEDDING_BATCH_SIZE:
            logger.warning(
                f"Only {len(texts)} texts provided. "
                f"Consider accumulating to {MIN_EMBEDDING_BATCH_SIZE}+ for optimal performance."
            )

        # Embed with normalization
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,  # CRITICAL: For cosine similarity
            show_progress_bar=len(texts) > 1000,
        )

        return embeddings

    def embed_single(self, text: str) -> np.ndarray:
        """
        Embed single text (use sparingly - prefer embed_batch).

        WARNING: This is 100x slower than batched embedding.
        Only use for real-time, single-query scenarios.
        """
        logger.debug("Single text embedding - consider batching for performance")
        return self.model.encode(
            text,
            normalize_embeddings=True,
        )

# Usage
service = BatchedEmbeddingService()
embeddings = service.embed_batch(texts, batch_size=100)
```

### Pattern 2: Accumulator for Stream Processing

**When to use**: Processing data streams where items arrive one at a time.

**Implementation**:
```python
import asyncio
from dataclasses import dataclass, field
from typing import Callable

MIN_EMBEDDING_BATCH_SIZE = 100
MAX_WAIT_SECONDS = 5.0

@dataclass
class EmbeddingAccumulator:
    """Accumulate items until batch threshold or timeout."""

    embedding_service: BatchedEmbeddingService
    on_complete: Callable[[list[dict]], None]
    batch_size: int = MIN_EMBEDDING_BATCH_SIZE
    max_wait: float = MAX_WAIT_SECONDS
    _buffer: list[dict] = field(default_factory=list)
    _timer: asyncio.Task | None = None

    async def add(self, item: dict):
        """Add item to buffer, process when threshold reached."""
        self._buffer.append(item)

        if len(self._buffer) >= self.batch_size:
            await self._process_batch()
        elif self._timer is None:
            # Start timeout timer
            self._timer = asyncio.create_task(self._timeout())

    async def _timeout(self):
        """Process batch after timeout even if not full."""
        await asyncio.sleep(self.max_wait)
        if self._buffer:
            await self._process_batch()

    async def _process_batch(self):
        """Process accumulated items."""
        if self._timer:
            self._timer.cancel()
            self._timer = None

        if not self._buffer:
            return

        batch = self._buffer
        self._buffer = []

        # Extract texts and embed
        texts = [item["text"] for item in batch]
        embeddings = self.embedding_service.embed_batch(texts)

        # Attach embeddings to items
        for item, embedding in zip(batch, embeddings):
            item["embedding"] = embedding.tolist()

        # Callback with completed items
        self.on_complete(batch)

    async def flush(self):
        """Force process remaining items."""
        await self._process_batch()
```

---

## Model Selection

### Pattern 3: Language-Specific Model Selection

**When to use**: Multi-language content, especially Celtic languages.

**Model Recommendations**:

| Use Case | Model | Dimensions | Notes |
|----------|-------|------------|-------|
| **General multilingual** | `BAAI/bge-m3` | 1024 | Best overall quality |
| **Fast multilingual** | `paraphrase-MiniLM-L6-v2` | 384 | 3x faster, good quality |
| **Code (Python, JS, etc.)** | `microsoft/graphcodebert-base` | 768 | Trained on code |
| **Code (Rust, TS, etc.)** | `microsoft/unixcoder-base` | 768 | Extended language support |
| **Irish text** | `DCU-NLP/bert-base-irish-cased-v1` | 768 | GaBERT - Irish-specific |
| **Visual documents** | `vidore/colpali-v1.2` | 128 | PDF/image understanding |

**Implementation**:
```python
from enum import Enum

class EmbeddingModel(Enum):
    # Multilingual
    BGE_M3 = "BAAI/bge-m3"
    MINILM = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    E5_LARGE = "intfloat/multilingual-e5-large"

    # Code
    GRAPHCODEBERT = "microsoft/graphcodebert-base"
    UNIXCODER = "microsoft/unixcoder-base"
    CODEBERT = "microsoft/codebert-base"

    # Irish/Celtic
    GABERT = "DCU-NLP/bert-base-irish-cased-v1"

    # Visual
    COLPALI = "vidore/colpali-v1.2"

def select_model(content_type: str, language: str = "en") -> EmbeddingModel:
    """Select appropriate embedding model based on content."""

    # Irish language content
    if language in ("ga", "gd", "cy", "gv"):  # Celtic languages
        return EmbeddingModel.E5_LARGE  # Best multilingual coverage

    # Code content
    if content_type == "code":
        return EmbeddingModel.GRAPHCODEBERT

    # Visual documents
    if content_type in ("pdf", "image"):
        return EmbeddingModel.COLPALI

    # Default: best quality multilingual
    return EmbeddingModel.BGE_M3
```

### Pattern 4: Multi-Model Embedding

**When to use**: Different content types in same pipeline.

**Implementation**:
```python
class MultiModelEmbedder:
    """Embed different content types with appropriate models."""

    def __init__(self):
        self.models = {}

    def _get_model(self, model_enum: EmbeddingModel) -> SentenceTransformer:
        """Lazy load models on demand."""
        if model_enum not in self.models:
            self.models[model_enum] = SentenceTransformer(model_enum.value)
        return self.models[model_enum]

    def embed(
        self,
        items: list[dict],
        content_key: str = "text",
        type_key: str = "type",
        language_key: str = "language",
    ) -> list[dict]:
        """Embed items using content-appropriate models."""

        # Group by model
        model_groups: dict[EmbeddingModel, list[tuple[int, dict]]] = {}
        for i, item in enumerate(items):
            model = select_model(
                item.get(type_key, "text"),
                item.get(language_key, "en"),
            )
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append((i, item))

        # Embed each group
        results = [None] * len(items)
        for model_enum, group in model_groups.items():
            model = self._get_model(model_enum)
            texts = [item[content_key] for _, item in group]

            embeddings = model.encode(
                texts,
                batch_size=MIN_EMBEDDING_BATCH_SIZE,
                normalize_embeddings=True,
            )

            for (idx, item), embedding in zip(group, embeddings):
                item["embedding"] = embedding.tolist()
                item["model"] = model_enum.value
                results[idx] = item

        return results
```

---

## Chunking Patterns

### Pattern 5: Semantic Chunking

**When to use**: Documents where context matters.

**Implementation**:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_semantic_chunker(
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    content_type: str = "markdown",
) -> RecursiveCharacterTextSplitter:
    """Create chunker with semantic boundaries."""

    # Language-specific separators
    separators_by_type = {
        "markdown": [
            "\n## ",      # H2 headers
            "\n### ",     # H3 headers
            "\n\n",       # Paragraphs
            "\n",         # Lines
            ". ",         # Sentences
            " ",          # Words
        ],
        "code": [
            "\nclass ",   # Classes
            "\ndef ",     # Functions
            "\n\n",       # Blocks
            "\n",         # Lines
            " ",          # Tokens
        ],
        "html": [
            "</div>",
            "</p>",
            "<br>",
            "\n\n",
            "\n",
            " ",
        ],
    }

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators_by_type.get(content_type, ["\n\n", "\n", " "]),
        length_function=len,
    )

# Usage
chunker = create_semantic_chunker(chunk_size=800, content_type="markdown")
chunks = chunker.split_text(document_text)
```

### Pattern 6: Code-Aware Chunking with Tree-sitter

**When to use**: Source code where AST structure matters.

**Implementation**:
```python
from tree_sitter_languages import get_parser
from dataclasses import dataclass
from enum import Enum

class ChunkType(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    STATEMENT = "statement"
    COMMENT = "comment"

@dataclass
class CodeChunk:
    text: str
    chunk_type: ChunkType
    name: str | None
    start_line: int
    end_line: int
    language: str
    parent_name: str | None = None

def chunk_code(
    code: str,
    language: str,
    max_chunk_size: int = 1200,
    min_chunk_size: int = 100,
) -> list[CodeChunk]:
    """Chunk code using AST structure."""

    parser = get_parser(language)
    tree = parser.parse(code.encode())

    chunks = []

    def extract_chunks(node, parent_name=None):
        # Identify chunk type
        if node.type in ("function_definition", "method_definition"):
            chunk_type = ChunkType.FUNCTION
        elif node.type == "class_definition":
            chunk_type = ChunkType.CLASS
        elif node.type == "comment":
            chunk_type = ChunkType.COMMENT
        else:
            chunk_type = ChunkType.STATEMENT

        # Extract text
        text = code[node.start_byte:node.end_byte]

        # Skip tiny chunks
        if len(text) < min_chunk_size:
            return

        # Split large chunks
        if len(text) > max_chunk_size:
            for child in node.children:
                extract_chunks(child, parent_name)
            return

        # Get name if available
        name = None
        for child in node.children:
            if child.type == "identifier":
                name = code[child.start_byte:child.end_byte]
                break

        chunks.append(CodeChunk(
            text=text,
            chunk_type=chunk_type,
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            language=language,
            parent_name=parent_name,
        ))

    extract_chunks(tree.root_node)
    return chunks
```

---

## Index Management

### Pattern 7: HNSW Index Lifecycle

**When to use**: Any LanceDB table with vector search.

**Implementation**:
```python
import lancedb
from contextlib import contextmanager

HNSW_DROP_THRESHOLD = 50

@contextmanager
def managed_bulk_insert(
    table: lancedb.table.Table,
    data: list[dict],
    vector_column: str = "embedding",
):
    """Context manager for bulk inserts with automatic index management."""

    need_rebuild = len(data) > HNSW_DROP_THRESHOLD
    index_name = f"{vector_column}_idx"

    try:
        # Drop index before large insert
        if need_rebuild:
            try:
                table.drop_index(index_name)
            except Exception:
                pass  # Index might not exist

        yield table

    finally:
        # Recreate index after insert
        if need_rebuild:
            table.create_index(
                index_name,
                index_type="IVF_HNSW",
                metric="cosine",
                num_partitions=256,
                num_sub_vectors=32,
            )

# Usage
with managed_bulk_insert(table, data) as t:
    t.add(data)
```

### Pattern 8: Index Configuration by Use Case

**When to use**: Optimizing search performance.

**Configuration Guide**:

| Use Case | Index Type | Partitions | Sub-vectors | Notes |
|----------|------------|------------|-------------|-------|
| **<10K vectors** | None | - | - | Brute force is faster |
| **10K-100K vectors** | IVF_HNSW | 64 | 16 | Balanced |
| **100K-1M vectors** | IVF_HNSW | 256 | 32 | Default recommendation |
| **>1M vectors** | IVF_PQ | 512 | 64 | Product quantization |
| **Low memory** | IVF_SQ | 256 | - | Scalar quantization |

**Implementation**:
```python
def create_optimal_index(
    table: lancedb.table.Table,
    vector_count: int,
    vector_column: str = "embedding",
):
    """Create index optimized for dataset size."""

    if vector_count < 10_000:
        # Brute force is faster for small datasets
        return

    if vector_count < 100_000:
        table.create_index(
            f"{vector_column}_idx",
            index_type="IVF_HNSW",
            metric="cosine",
            num_partitions=64,
            num_sub_vectors=16,
        )
    elif vector_count < 1_000_000:
        table.create_index(
            f"{vector_column}_idx",
            index_type="IVF_HNSW",
            metric="cosine",
            num_partitions=256,
            num_sub_vectors=32,
        )
    else:
        # Use product quantization for very large datasets
        table.create_index(
            f"{vector_column}_idx",
            index_type="IVF_PQ",
            metric="cosine",
            num_partitions=512,
            num_sub_vectors=64,
        )
```

---

## Integration with CocoIndex

### Pattern 9: CocoIndex Embedding Flow

**When to use**: Standard document embedding pipeline.

**Implementation**:
```python
import cocoindex
from cocoindex.sources import LocalFile
from cocoindex.functions import SplitRecursively, SentenceTransformerEmbed
from cocoindex.storages import LanceDB

@cocoindex.flow_def(name="DocumentEmbedding")
def document_embedding_flow(flow_builder, data_scope):
    # Source
    data_scope["documents"] = flow_builder.add_source(
        LocalFile(path="./documents", glob_pattern="**/*.md")
    )

    with data_scope["documents"].row() as doc:
        # Chunk with semantic boundaries
        doc["chunks"] = doc["content"].transform(
            SplitRecursively(
                chunk_size=800,
                chunk_overlap=150,
                language="markdown",
            )
        )

        # Embed with batching (handled internally by CocoIndex)
        with doc["chunks"].row() as chunk:
            chunk["embedding"] = chunk["text"].transform(
                SentenceTransformerEmbed(
                    model="BAAI/bge-m3",
                    normalize=True,
                    # CocoIndex handles batching automatically
                )
            )

    # Export with vector index
    embeddings = data_scope["documents"]["chunks"].collector()
    embeddings.export(
        "document_embeddings",
        LanceDB(uri="./lancedb"),
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE,
            )
        ],
    )
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Embedding one text at a time | Accumulate to 100+ before embedding |
| Missing normalization | Always set `normalize_embeddings=True` |
| Wrong model for content type | Use code models for code, multilingual for Irish |
| Chunks too large | Keep chunks 500-1000 tokens |
| Chunks too small | Minimum 100 tokens for context |
| Skipping index rebuild | Always recreate after bulk insert |
| Same model for all languages | Use language-specific models |
| No overlap in chunks | Add 10-20% overlap for context |

---

## Performance Benchmarks

| Operation | Without Pattern | With Pattern | Notes |
|-----------|-----------------|--------------|-------|
| 1000 text embeddings | 100s | 1s | Batching |
| 10000 row insert | 45s | 2.2s | HNSW management |
| Irish text retrieval | 60% P@10 | 78% P@10 | GaBERT model |
| Code search | 55% MRR | 72% MRR | CodeBERT model |

---

## References

- Source: `taighde/cocoindex/`, `sruth/oideachais/cocoindex_flows/`
- Skills: `.claude/skills/cocoindex/`, `.claude/skills/lancedb/`
- Models: HuggingFace Hub, sentence-transformers
