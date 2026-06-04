"""CocoIndex Flows for the Croílár Portfolio.

Image embedding, CV text embedding, and analysis pipelines using CocoIndex.

Flows:
    - artwork_embedding_flow: Embed artwork images using CLIP to LanceDB
    - artwork_embedding_duckdb_flow: Embed artwork from DuckDB source
    - cv_embedding_flow: Embed CV text using sentence-transformers to LanceDB

Usage:
    from cocoindex_flows import artwork_embedding_flow

    # Setup and run
    artwork_embedding_flow.setup()
    with cocoindex.FlowLiveUpdater(artwork_embedding_flow) as updater:
        updater.wait()
"""

from cocoindex_flows.artwork_embedding import (
    artwork_embedding_flow,
    artwork_embedding_duckdb_flow,
    embed_image_clip,
    search_similar_artwork,
)
from cocoindex_flows.cv_embedding import cv_embedding_flow

__all__ = [
    "artwork_embedding_flow",
    "artwork_embedding_duckdb_flow",
    "cv_embedding_flow",
    "embed_image_clip",
    "search_similar_artwork",
]
