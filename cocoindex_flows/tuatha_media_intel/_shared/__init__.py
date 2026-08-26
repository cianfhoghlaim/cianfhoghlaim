"""The shared CocoIndex lifespan + LanceDB connection for the tuatha-media-intel ingestors.

Conformance per the cianfhoghlaim-cocoindex-v1 skill (R1-R4):
- R1: imports `shared_lifespan`
- R2: imports the canonical ContextKeys from `_lifespan`
- R3: module-scope `coco.App` in every child module
- R4: at least one `@coco.fn(` decorator in every child module
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

import cocoindex as coco
from cocoindex.connectors import lancedb
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder
from lancedb import Connection as LanceConnection
from numpy.typing import NDArray

# Canonical KCG embedder: BAAI/bge-m3 (1024-d, multilingual, 100+ languages).
# Same constant used by the BIEP v3 7 Apps (per the centralized-registry skill).
EMBED_MODEL = "BAAI/bge-m3"

# The 4 Lance ContextKeys for the 4 ANAM tables.
LANCE_DB = coco.ContextKey[LanceConnection](
    "tuatha_media_intel.lance_db", detect_change=True
)
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](
    "tuatha_media_intel.embedder", detect_change=True
)
S3_LANCE_URI = coco.ContextKey[str](
    "tuatha_media_intel.s3_lance_uri", detect_change=True
)


@coco.lifespan
async def shared_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    """Open the shared Lance connection + load the embedder exactly once.

    The S3 URI is read from the TUATHA_LANCE_URI env var (Infisical
    hydrates via Locket sidecar at runtime). Falls back to a local
    ./data/tuatha_lance directory for first-run development.
    """
    import os

    s3_uri = os.environ.get(
        "TUATHA_LANCE_URI", "./data/tuatha_lance"
    )
    lance = await LanceConnection.connect_async(s3_uri)
    builder.provide(S3_LANCE_URI, s3_uri)
    builder.provide(LANCE_DB, lance)
    builder.provide(
        EMBEDDER,
        SentenceTransformerEmbedder(
            model_name=EMBED_MODEL,
            # M-series native; falls back to cpu transparently.
            device=os.environ.get("TUATHA_EMBED_DEVICE", "mps"),
        ),
    )
    yield
