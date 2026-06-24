# Dlt_utils

Utilities for dlt data loading

## Canonical Embedding Batcher

The canonical `EmbeddingBatcher` lives in `oideachais.dlt_utils.batching`
and is re-exported via `oideachais.dlt_utils.__init__.EmbeddingBatcher`.

The legacy `oideachais/embeddings/` package has been **removed**
(see `openspec/changes/consolidate-embedding-batcher/`). Do not
re-introduce it. Import the canonical batcher from `dlt_utils` instead:

```python
from oideachais.dlt_utils import (
    EmbeddingBatcher,
    batch_embeddings,
    batch_items,
    should_drop_hnsw,
    calculate_optimal_batch_size,
    MINIMUM_BATCH_SIZE,
    HNSW_DROP_THRESHOLD,
)
```

The `oideachais/modal_finetune/embed_batch.py` Modal GPU worker is
**not** a duplicate — it is a serverless GPU `@app.cls` worker that
runs on Modal infrastructure, not a local Python utility. The class
name `EmbeddingService` is shared but the layer is different.


## Cross-References

This module integrates with other components of the Oideachais platform:
- See the main [Agent Architecture](../../AGENTS.md) for global orchestration rules.
- View the [Skills Library](../../.skills/) for agent capability instructions.
- Relevant modules: [visualization](../visualization/README.md), [clients](../clients/README.md), [ui](../ui/README.md)
