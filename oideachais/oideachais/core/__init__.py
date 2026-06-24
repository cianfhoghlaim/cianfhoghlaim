"""oideachais.core — DEPRECATED backward-compat re-export shim.

The constants and functions previously defined here have been moved to
their canonical locations:

- `HNSW_DROP_THRESHOLD` → `oideachais.dlt_utils.batching.HNSW_DROP_THRESHOLD`
- `MIN_EMBEDDING_BATCH_SIZE` → `oideachais.dlt_utils.batching.MIN_EMBEDDING_BATCH_SIZE`
- `get_executor()` → `oideachais.dlt_utils.safety.get_executor()`

This shim re-exports them so any in-flight
`from oideachais.core import X` imports continue to work for one
release. New code MUST import directly from `oideachais.dlt_utils`.

Reference: openspec/changes/fix-broken-imports-and-baml
"""

from oideachais.dlt_utils.batching import HNSW_DROP_THRESHOLD, MIN_EMBEDDING_BATCH_SIZE
from oideachais.dlt_utils.safety import get_executor

__all__ = ["HNSW_DROP_THRESHOLD", "MIN_EMBEDDING_BATCH_SIZE", "get_executor"]
