"""Nigerian federal law DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, the per-jurisdiction `law/` sub-tree has been migrated from
`dlt_sources/commonwealth/nigeria/law/` to
`dlt_sources/law/nigeria/commonwealth/`.

This `__init__.py` re-exports the per-source modules for backwards
compatibility AND for new code that uses the domain-first path.
"""
from __future__ import annotations

# The pre-Wave-1 `from dlt_sources.commonwealth.nga.law import nass` import
# was broken — the actual `nass` module lives in this very directory.
from . import nass  # noqa: F401

__all__ = ["nass"]
