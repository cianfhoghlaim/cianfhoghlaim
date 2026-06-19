# Performance Tuning Guide

Optimization strategies for the Tuath Celtic Educational MMO.

## Overview

Performance-critical areas:
1. **Embedding Generation** - Batching is mandatory (100x speedup)
2. **Vector Search** - HNSW index management
3. **Graph Queries** - Cypher optimization
4. **Game Client** - 60 FPS target with WebGPU

---

## Embedding Performance

### Critical: Always Batch

```python
# BAD - Unbatched (100s for 1000 texts)
for text in texts:
    embedding = model.encode(text)

# GOOD - Batched (1s for 1000 texts)
embeddings = model.encode(texts, batch_size=100)
```

Performance comparison:
| Approach | 1000 texts | Speedup |
|----------|------------|---------|
| Unbatched | ~100s | 1x |
| Batch 10 | ~10s | 10x |
| Batch 100 | ~1s | 100x |
| Batch 500 | ~0.8s | 125x |

### Optimal Batch Sizes

| Model | GPU VRAM | Recommended Batch |
|-------|----------|-------------------|
| BGE-M3 | 24GB | 500 |
| BGE-M3 | 16GB | 200 |
| BGE-M3 | 8GB | 100 |
| BGE-large | 24GB | 300 |
| BGE-large | 16GB | 150 |
| BGE-large | 8GB | 64 |

```python
from sentence_transformers import SentenceTransformer
import torch


def get_optimal_batch_size(model_name: str) -> int:
    """Calculate optimal batch size based on available VRAM."""

    if not torch.cuda.is_available():
        return 32  # CPU fallback

    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9

    # Model-specific sizing
    if "bge-m3" in model_name.lower():
        if vram_gb >= 24:
            return 500
        elif vram_gb >= 16:
            return 200
        elif vram_gb >= 8:
            return 100
        else:
            return 50

    # Default for other models
    return int(vram_gb * 10)


def batch_embed(
    texts: list[str],
    model: SentenceTransformer,
    batch_size: int | None = None,
) -> list[list[float]]:
    """
    Generate embeddings with optimal batching.

    Args:
        texts: List of texts to embed
        model: SentenceTransformer model
        batch_size: Override batch size (auto-calculated if None)

    Returns:
        List of embedding vectors
    """

    if batch_size is None:
        batch_size = get_optimal_batch_size(model.model_name)

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 100,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embeddings.tolist()
```

### GPU Memory Management

```python
import torch
import gc


def clear_gpu_memory():
    """Clear GPU memory between large operations."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()


def embed_with_memory_management(
    texts: list[str],
    model: SentenceTransformer,
    batch_size: int = 100,
) -> list[list[float]]:
    """Embed large datasets with memory management."""

    all_embeddings = []

    # Process in mega-batches to manage memory
    mega_batch_size = batch_size * 10

    for i in range(0, len(texts), mega_batch_size):
        mega_batch = texts[i:i + mega_batch_size]

        embeddings = model.encode(
            mega_batch,
            batch_size=batch_size,
            normalize_embeddings=True,
        )

        all_embeddings.extend(embeddings.tolist())

        # Clear memory after each mega-batch
        clear_gpu_memory()

    return all_embeddings
```

---

## Vector Index Management

### HNSW Index Strategy

**Critical: Drop indexes before bulk inserts!**

```python
import lancedb


class VectorIndexManager:
    """Manage HNSW indexes for optimal performance."""

    def __init__(self, db_path: str):
        self.db = lancedb.connect(db_path)

    def bulk_insert(
        self,
        table_name: str,
        data: list[dict],
        threshold: int = 50,
    ):
        """
        Insert data with automatic index management.

        For >50 rows, drop index before insert, recreate after.
        This provides ~20x speedup for bulk operations.
        """

        table = self.db.open_table(table_name)

        if len(data) > threshold:
            # Drop existing index
            try:
                table.drop_index("vector_idx")
                print(f"Dropped index for bulk insert of {len(data)} rows")
            except Exception:
                pass  # Index may not exist

            # Insert data
            table.add(data)

            # Recreate index
            table.create_index(
                "embedding",
                index_type="IVF_HNSW_SQ",
                name="vector_idx",
                num_partitions=256,
                num_sub_vectors=96,
            )
            print("Recreated HNSW index")

        else:
            # Small insert, keep index
            table.add(data)

    def optimize_index(self, table_name: str):
        """Optimize index after many small updates."""

        table = self.db.open_table(table_name)

        # Get current stats
        stats = table.stats()
        fragmentation = stats.get("fragmentation", 0)

        if fragmentation > 0.3:  # 30% fragmented
            # Rebuild index
            table.drop_index("vector_idx")
            table.create_index(
                "embedding",
                index_type="IVF_HNSW_SQ",
                name="vector_idx",
                num_partitions=256,
                num_sub_vectors=96,
            )
            print(f"Rebuilt fragmented index (was {fragmentation:.0%} fragmented)")
```

### Search Optimization

```python
from lancedb import LanceDBConnection


async def optimized_search(
    db: LanceDBConnection,
    table_name: str,
    query_vector: list[float],
    limit: int = 10,
    filters: dict | None = None,
) -> list[dict]:
    """
    Optimized vector search with pre-filtering.

    Pre-filtering is faster than post-filtering for selective queries.
    """

    table = db.open_table(table_name)

    # Build query
    query = table.search(query_vector)

    # Apply pre-filters (faster for selective conditions)
    if filters:
        filter_expr = build_filter_expression(filters)
        query = query.where(filter_expr, prefilter=True)

    # Limit results
    query = query.limit(limit)

    # Execute
    results = query.to_list()

    return results


def build_filter_expression(filters: dict) -> str:
    """Build SQL filter expression."""

    conditions = []

    for key, value in filters.items():
        if value is None:
            continue

        if isinstance(value, str):
            conditions.append(f"{key} = '{value}'")
        elif isinstance(value, list):
            values_str = ", ".join(f"'{v}'" for v in value)
            conditions.append(f"{key} IN ({values_str})")
        else:
            conditions.append(f"{key} = {value}")

    return " AND ".join(conditions)
```

---

## Database Performance

### DuckDB Single-Threading

**Critical: DuckDB is NOT thread-safe for concurrent access!**

```python
import threading
from queue import Queue
from typing import Any


class SerialDatabaseExecutor:
    """
    Execute all database operations serially to prevent corruption.

    DuckDB concurrent access = segfault/corruption!
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._queue: Queue = Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        """Worker thread for serial execution."""
        import duckdb

        conn = duckdb.connect(self.db_path)

        while True:
            task = self._queue.get()
            if task is None:
                break

            query, params, result_queue = task

            try:
                result = conn.execute(query, params).fetchall()
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", e))

    def execute(self, query: str, params: tuple = ()) -> list[Any]:
        """Execute query serially."""
        result_queue: Queue = Queue()
        self._queue.put((query, params, result_queue))

        status, result = result_queue.get()

        if status == "error":
            raise result

        return result
```

### LanceDB Multi-Process Safety

```python
import lancedb
from contextlib import contextmanager
import time
import random


class LanceDBClient:
    """
    LanceDB client with MVCC and retry logic.

    LanceDB is multi-process safe via MVCC, but benefits from retry logic.
    """

    def __init__(self, db_path: str):
        self.db = lancedb.connect(db_path)

    @contextmanager
    def table(self, name: str):
        """Get table with automatic retry on conflict."""
        yield self.db.open_table(name)

    def write_with_retry(
        self,
        table_name: str,
        data: list[dict],
        max_retries: int = 3,
    ):
        """
        Write with exponential backoff retry.

        Handles MVCC conflicts between processes.
        """

        for attempt in range(max_retries):
            try:
                table = self.db.open_table(table_name)
                table.add(data)
                return

            except Exception as e:
                if "conflict" in str(e).lower() and attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                else:
                    raise
```

### FalkorDB Graph Optimization

```python
# Cypher query optimization tips

# BAD - Full scan
query = "MATCH (n) WHERE n.name CONTAINS 'Cu' RETURN n"

# GOOD - Index lookup
query = """
MATCH (n:Character)
WHERE n.name STARTS WITH 'Cú'
RETURN n
"""

# BAD - Multiple separate queries
for character in characters:
    client.execute("MATCH (c:Character {name: $name}) RETURN c", {"name": character})

# GOOD - Single parameterized query
query = """
UNWIND $names AS name
MATCH (c:Character {name: name})
RETURN c
"""
client.execute(query, {"names": characters})


# Create indexes for common queries
INDEX_QUERIES = [
    "CREATE INDEX ON :Character(name)",
    "CREATE INDEX ON :Story(title)",
    "CREATE INDEX ON :Document(id)",
    "CREATE INDEX ON :Entity(type, name)",
]
```

---

## API Performance

### Async Best Practices

```python
import asyncio
from typing import Coroutine, Any


async def parallel_fetch(
    tasks: list[Coroutine[Any, Any, Any]],
    max_concurrent: int = 10,
) -> list[Any]:
    """
    Execute async tasks with concurrency limit.

    Prevents overwhelming external services.
    """

    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_task(task: Coroutine):
        async with semaphore:
            return await task

    return await asyncio.gather(
        *[bounded_task(task) for task in tasks],
        return_exceptions=True,
    )


# Example usage
async def search_multiple_sources(query: str) -> list[dict]:
    """Search multiple sources in parallel."""

    tasks = [
        search_curriculum(query),
        search_mythology(query),
        search_geospatial(query),
    ]

    results = await parallel_fetch(tasks, max_concurrent=3)

    # Flatten and filter errors
    all_results = []
    for result in results:
        if not isinstance(result, Exception):
            all_results.extend(result)

    return all_results
```

### Response Caching

```python
from functools import lru_cache
from cachetools import TTLCache
import hashlib
import json


# In-memory cache with TTL
_search_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute TTL


def cache_key(query: str, filters: dict) -> str:
    """Generate cache key from query parameters."""
    data = json.dumps({"query": query, "filters": filters}, sort_keys=True)
    return hashlib.md5(data.encode()).hexdigest()


async def cached_search(
    query: str,
    filters: dict | None = None,
) -> list[dict]:
    """Search with caching layer."""

    key = cache_key(query, filters or {})

    if key in _search_cache:
        return _search_cache[key]

    results = await perform_search(query, filters)

    _search_cache[key] = results

    return results
```

### Connection Pooling

```python
from contextlib import asynccontextmanager
import asyncpg


class DatabasePool:
    """Async database connection pool."""

    _pool: asyncpg.Pool | None = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """Get or create connection pool."""

        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                dsn="postgresql://user:pass@localhost/tuath",
                min_size=5,
                max_size=20,
                command_timeout=30,
            )

        return cls._pool

    @classmethod
    @asynccontextmanager
    async def connection(cls):
        """Get connection from pool."""
        pool = await cls.get_pool()

        async with pool.acquire() as conn:
            yield conn
```

---

## Game Client Performance

### Babylon.js Optimization

```typescript
// engine.ts

import {
  Engine,
  Scene,
  WebGPUEngine,
  SceneOptimizer,
  SceneOptimizerOptions,
  HardwareScalingOptimization,
} from '@babylonjs/core';


export async function createOptimizedEngine(
  canvas: HTMLCanvasElement,
): Promise<Engine> {
  // Prefer WebGPU for better performance
  const webGPUSupported = await WebGPUEngine.IsSupportedAsync;

  let engine: Engine;

  if (webGPUSupported) {
    engine = new WebGPUEngine(canvas, {
      antialias: true,
      powerPreference: 'high-performance',
    });
    await (engine as WebGPUEngine).initAsync();
  } else {
    engine = new Engine(canvas, true, {
      preserveDrawingBuffer: true,
      stencil: true,
      antialias: true,
    });
  }

  // Hardware scaling for performance
  engine.setHardwareScalingLevel(1.0);

  return engine;
}


export function optimizeScene(scene: Scene): void {
  // Scene optimizer for dynamic quality adjustment
  const options = new SceneOptimizerOptions(60, 2000);

  options.addOptimization(new HardwareScalingOptimization(0, 1.5));

  SceneOptimizer.OptimizeAsync(
    scene,
    options,
    () => console.log('Scene optimized'),
    () => console.log('Scene optimization failed'),
  );

  // Reduce draw calls
  scene.blockMaterialDirtyMechanism = true;

  // Freeze materials that won't change
  scene.materials.forEach((mat) => {
    if (!mat.name.includes('dynamic')) {
      mat.freeze();
    }
  });

  // Enable frustum culling
  scene.meshes.forEach((mesh) => {
    mesh.alwaysSelectAsActiveMesh = false;
  });
}
```

### LOD (Level of Detail)

```typescript
// lod-manager.ts

import { Mesh, MeshBuilder, Scene } from '@babylonjs/core';


export function addLOD(
  mesh: Mesh,
  scene: Scene,
  distances: number[] = [50, 100, 200],
): void {
  // Create simplified versions
  const lod1 = mesh.simplify([
    { distance: distances[0], quality: 0.7 },
  ]);

  const lod2 = mesh.simplify([
    { distance: distances[1], quality: 0.4 },
  ]);

  const lod3 = mesh.simplify([
    { distance: distances[2], quality: 0.1 },
  ]);

  // Add LOD levels
  mesh.addLODLevel(distances[0], lod1);
  mesh.addLODLevel(distances[1], lod2);
  mesh.addLODLevel(distances[2], lod3);
  mesh.addLODLevel(distances[2] * 2, null); // Cull beyond this
}


export function createInstancedMeshes(
  baseMesh: Mesh,
  positions: Vector3[],
): InstancedMesh[] {
  /**
   * Use instancing for repeated objects (trees, rocks, etc.)
   * Single draw call for all instances.
   */

  const instances: InstancedMesh[] = [];

  for (let i = 0; i < positions.length; i++) {
    const instance = baseMesh.createInstance(`${baseMesh.name}_${i}`);
    instance.position = positions[i];
    instances.push(instance);
  }

  return instances;
}
```

### Network Optimization

```typescript
// network/position-sync.ts

const SYNC_RATE = 20; // Hz
const POSITION_THRESHOLD = 0.1; // Only send if moved > 0.1 units
const ROTATION_THRESHOLD = 0.01; // radians


class PositionSync {
  private lastSentPosition: Vector3 = Vector3.Zero();
  private lastSentRotation: number = 0;
  private syncInterval: number | null = null;

  start(client: SpacetimeClient, getPlayerState: () => PlayerState): void {
    this.syncInterval = setInterval(() => {
      const state = getPlayerState();

      // Only send if changed significantly
      if (this.shouldSync(state)) {
        client.updatePosition(state.position, state.rotation);
        this.lastSentPosition = state.position.clone();
        this.lastSentRotation = state.rotation;
      }
    }, 1000 / SYNC_RATE);
  }

  private shouldSync(state: PlayerState): boolean {
    const positionDelta = Vector3.Distance(
      state.position,
      this.lastSentPosition,
    );

    const rotationDelta = Math.abs(state.rotation - this.lastSentRotation);

    return (
      positionDelta > POSITION_THRESHOLD ||
      rotationDelta > ROTATION_THRESHOLD
    );
  }

  stop(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }
}
```

---

## Monitoring

### Performance Metrics

```python
# api/middleware/metrics.py

import time
from fastapi import Request
from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

EMBEDDING_BATCH_SIZE = Histogram(
    "embedding_batch_size",
    "Embedding batch sizes",
    buckets=[10, 50, 100, 200, 500, 1000],
)

SEARCH_LATENCY = Histogram(
    "search_duration_seconds",
    "Search operation latency",
    ["search_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0],
)


async def metrics_middleware(request: Request, call_next):
    """Record request metrics."""

    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    return response
```

### Slow Query Detection

```python
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

SLOW_QUERY_THRESHOLD = 1.0  # seconds


def log_slow_queries(func):
    """Decorator to log slow database queries."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = await func(*args, **kwargs)

        duration = time.perf_counter() - start

        if duration > SLOW_QUERY_THRESHOLD:
            logger.warning(
                f"Slow query detected: {func.__name__} "
                f"took {duration:.2f}s",
                extra={
                    "function": func.__name__,
                    "duration": duration,
                    "args": str(args)[:200],
                },
            )

        return result

    return wrapper
```

---

## Performance Checklist

### Embedding Operations
- [ ] Batch size >= 100 for all embedding calls
- [ ] GPU memory cleared between large batches
- [ ] HNSW indexes dropped before bulk inserts >50 rows
- [ ] HNSW indexes recreated after bulk operations

### Database Operations
- [ ] DuckDB accessed single-threaded only
- [ ] LanceDB writes have retry logic
- [ ] FalkorDB queries use indexes
- [ ] Connection pooling enabled

### API Layer
- [ ] Async operations for all I/O
- [ ] Response caching for repeated queries
- [ ] Concurrency limits for external calls
- [ ] Request timeouts configured

### Game Client
- [ ] WebGPU preferred over WebGL
- [ ] LOD enabled for complex meshes
- [ ] Instancing used for repeated objects
- [ ] Position sync rate-limited to 20Hz
- [ ] Materials frozen when static

---

## Related Documentation

- [Architecture](../../ANALYSIS.md) - System overview
- [Adding Data Sources(../../03-data-pipelines/ADDING_DATA_SOURCES.md) - Pipeline configuration
- [Celtic Languages(../../01-game-design/CELTIC_LANGUAGES.md) - Embedding strategies
