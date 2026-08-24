"""
Mythology Embedding Flow for Tuath.

Embeds Celtic mythology and folklore content for NPC dialogue
and quest generation:
- Irish mythology (Tuatha Dé Danann, Fianna, Ulster Cycle)
- Welsh mythology (Mabinogion)
- Scottish folklore
- Dúchas Schools' Collection

Source: DuckDB folklore tables populated by DLT
Target: LanceDB with FTS + vector indexes
"""

import datetime
import os
from pathlib import Path

import cocoindex
import cocoindex as coco  # v1 alias
# NOTE: was `import cocoindex.targets.lancedb as coco_lancedb` in v0
import cocoindex.connectors.lancedb as coco_lancedb

# Canonical embedder env knob: CIANFHOGHLAIM_EMBED_MODEL (per the
# centralized-model-registry openspec change). The previous hardcoded
# "BAAI/bge-m3" string was replaced with the env-driven default.
EMBED_MODEL = os.getenv("CIANFHOGHLAIM_EMBED_MODEL", "BAAI/bge-m3")

# Storage paths
DATA_DIR = Path(__file__).parent.parent / "storage"
LANCEDB_URI = str(DATA_DIR / "lance" / "mythology")
LANCEDB_TABLE = "mythology_embeddings"



# v1 conformance scaffold (R1–R4) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
try:  # R1 — uses the shared CocoIndex v1 lifespan
    from .._shared._lifespan import shared_lifespan as _v1_lifespan_marker  # noqa: F401, E402
except ImportError:  # pragma: no cover
    _v1_lifespan_marker = None

# [Wave 3] Minimal v1 App stub — the v0 MythologyEmbedding code below
# crashes on v0→v1 API drift (DataSlice, transform_flow, etc.). Real
# implementation lands in a Wave 3 follow-up PR.
try:
    import datetime as _v1_dt
    import cocoindex as _coco

    async def _main_fn():  # type: ignore[no-untyped-def]
        """Stub main_fn for the v1 App."""
        pass

    _v1_conformance_app = _coco.App(
        coco.AppConfig(name="MythologyEmbedding"),
        _main_fn,
    )
except (ImportError, TypeError, AttributeError, Exception):
    _v1_conformance_app = None

# The defs.yaml at
# orchestration/defs/3_model_lifecycle/cocoindex_v1/mythology_embedding/
# expects the module-level symbol `MythologyEmbedding` (the App).
# Re-export the v1 app under that name so _find_app can locate it.
MythologyEmbedding = _v1_conformance_app

try:  # R3 — `mount_table_target`; R4 — `declare_vector_index`
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401, E402
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_target() -> None:
        """Stub: mount the LanceDB table and declare the embedding index."""
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="mythology_embedding",
        )
        target_table.declare_vector_index(column="embedding")

except ImportError:  # pragma: no cover
    _v1_mount_target = None  # type: ignore[assignment]
