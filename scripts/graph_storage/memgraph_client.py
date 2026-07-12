"""Back-compat shim for the post-T4 split of `memgraph_client.py`.

Per the `2026-07-09-agent-fleet-and-observability-facade-v1` change,
the 1124-LOC `cianfhoghlaim/storage/memgraph_client.py` monolith was
split into 3 files:

- `_memgraph_protocol.py` — `MemgraphClient` Protocol + 4 dataclasses
  (`CurriculumNode`, `Subject`, `Strand`, `StrandUnit`,
  `LearningOutcome`) + `MemgraphConfig` + `get_config()`
- `_memgraph_client.py` — the concrete `MemgraphClient` class
- `_memgraph_queries.py` — `CurriculumGraph`, `CurriculumDataLoader`,
  `load_curriculum_to_graph`, `get_curriculum_graph`

This file now exists only as a thin re-export shim so the 4
existing consumers (`temporal_client.py`, `cache.py`,
`research.py`, the storage package `__init__.py`) keep working
without an import edit.

New code should import from one of the 3 split files directly.
"""
from __future__ import annotations

from ._memgraph_client import MemgraphClient
from ._memgraph_protocol import (
    CurriculumNode,
    LearningOutcome,
    MemgraphConfig,
    Strand,
    StrandUnit,
    Subject,
    get_config,
)
from ._memgraph_queries import (
    CurriculumDataLoader,
    CurriculumGraph,
    get_curriculum_graph,
    load_curriculum_to_graph,
)


__all__ = [
    "CurriculumDataLoader",
    "CurriculumGraph",
    "CurriculumNode",
    "LearningOutcome",
    "MemgraphClient",
    "MemgraphConfig",
    "Strand",
    "StrandUnit",
    "Subject",
    "get_config",
    "get_curriculum_graph",
    "load_curriculum_to_graph",
]
