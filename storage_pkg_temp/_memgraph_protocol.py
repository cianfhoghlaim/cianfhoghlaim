"""Memgraph Protocol + dataclasses (split from `memgraph_client.py` per T4).

Per the `2026-07-09-agent-fleet-and-observability-facade-v1` change,
the 1124-LOC `cianfhoghlaim/storage/memgraph_client.py` monolith is
split into 3 files (kept under `_memgraph_*` prefix so consumers
that imported the old public surface keep working):

- `_memgraph_protocol.py` — `MemgraphClient` Protocol + the 4
  dataclasses (`CurriculumNode`, `Subject`, `Strand`,
  `StrandUnit`, `LearningOutcome`).
- `_memgraph_client.py` — the concrete `MemgraphClient`
  implementation (the neo4j Bolt driver wrapper).
- `_memgraph_queries.py` — the `CurriculumGraph`,
  `CurriculumDataLoader`, `load_curriculum_to_graph`,
  `get_curriculum_graph` helpers.

The original `memgraph_client.py` is preserved as a thin back-compat
shim that re-exports the names from the three new modules. This
keeps every existing consumer (`temporal_client.py`,
`cache.py:CurriculumGraph`, `research.py`, etc.) working
without an import edit.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class MemgraphConfig:
    """Memgraph connection configuration.

    The pre-v4 monolithic `memgraph_client.py` imported this from a
    non-existent `storage/config.py` module — that broke the entire
    storage package import. We declare it locally here so the
    Protocol + concrete client can be loaded without that dead
    import.
    """

    uri: str = "bolt://localhost:7687"
    username: str | None = None
    password: str | None = None
    database: str = "memgraph"
    mermaid_creds: str | None = None


@dataclass
class FalkorDBConfig:
    """FalkorDB connection configuration.

    Declared locally (same reason as `MemgraphConfig`) so the
    `falkordb_client.py` can be loaded without the dead
    `storage/config.py` import path.
    """

    uri: str = "falkor://localhost:6379"
    host: str = "localhost"
    port: int = 6379
    username: str | None = None
    password: str | None = None
    db: int = 0


def get_config() -> "MemgraphConfigBundle":
    """Return a bundle of (memgraph, falkordb, lancedb) configs.

    Mirrors the legacy `get_config()` shape so consumers that read
    `cfg.memgraph.uri` (etc.) keep working. The default values
    match the dev-Docker Compose port set.
    """

    @dataclass
    class MemgraphConfigBundle:  # local class; avoids polluting top namespace
        memgraph: MemgraphConfig = field(default_factory=MemgraphConfig)
        falkordb: FalkorDBConfig = field(default_factory=FalkorDBConfig)
        falkordb_uri: str = "falkor://localhost:6379"
        lancedb_path: str = "/tmp/lancedb"

    return MemgraphConfigBundle()


# ---------------------------------------------------------------------------
# Curriculum graph dataclasses
# ---------------------------------------------------------------------------


@dataclass
class CurriculumNode:
    """Base class for curriculum graph nodes."""

    id: str
    name_en: str
    name_ga: str | None = None
    properties: dict[str, Any] | None = None


@dataclass
class Subject(CurriculumNode):
    """Subject node (e.g., Irish, Mathematics)."""

    code: str = ""
    education_level: str = ""
    syllabus_url: str | None = None


@dataclass
class Strand(CurriculumNode):
    """Strand within a subject."""

    subject_code: str = ""
    sequence: int = 0
    description: str | None = None


@dataclass
class StrandUnit(CurriculumNode):
    """Unit within a strand."""

    strand_id: str = ""
    sequence: int = 0
    description: str | None = None


@dataclass
class LearningOutcome(CurriculumNode):
    """Specific learning outcome."""

    code: str = ""
    strand_unit_id: str = ""
    description_en: str = ""
    description_ga: str | None = None
    difficulty_level: str = ""
    curriculum_year: int = 2024
    key_skills: list[str] | None = None


# ---------------------------------------------------------------------------
# Protocol (the narrow type signature that every backend implements)
# ---------------------------------------------------------------------------


@runtime_checkable
class MemgraphClient(Protocol):
    """The narrow Protocol that concrete Memgraph backends implement.

    Consumers should type-annotate against this Protocol, NOT
    against the concrete class in `_memgraph_client.py`. The
    memory-backend facade in `memf.py` also depends on it.
    """

    config: "MemgraphConfig"

    def query(
        self, cypher: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return the raw result rows."""
        ...

    def execute(
        self, cypher: str, parameters: dict[str, Any] | None = None
    ) -> Any:
        """Execute a write Cypher query (no return)."""
        ...

    def close(self) -> None:
        """Close the underlying driver connection."""
        ...


__all__ = [
    "CurriculumNode",
    "FalkorDBConfig",
    "LearningOutcome",
    "MemgraphClient",
    "MemgraphConfig",
    "Strand",
    "StrandUnit",
    "Subject",
    "get_config",
]
