"""oideachais.core — stub for legacy imports.

The constants/functions in this module are actually defined in
`data_platform.dlt_utils.batching` and `data_platform.dlt_utils.safety`.
This stub provides inline definitions so the broken
`from oideachais.core import X` imports scattered through the codebase
still resolve.

Per AGENTS.md, new code MUST use relative imports
(`from ...dlt_utils import batching`).

NOTE: This module is a migration shim. The real definitions live in
`data_platform/dlt_utils/`.
"""

# Inline values mirror `data_platform.dlt_utils.batching`.
HNSW_DROP_THRESHOLD: int = 50
MIN_EMBEDDING_BATCH_SIZE: int = 100


def get_executor(name: str = "duckdb"):
    """Stub — the real implementation lives in
    `data_platform.dlt_utils.safety.get_executor()`.
    """
    from concurrent.futures import ThreadPoolExecutor

    return ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"{name}_serial")
