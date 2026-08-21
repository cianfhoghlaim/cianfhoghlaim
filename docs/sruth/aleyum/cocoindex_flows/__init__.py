"""CocoIndex Flows for Artwork Processing.

Image embedding and analysis pipelines using CocoIndex.

Flows:
    - artwork_embedding_flow: Embed artwork images using CLIP to LanceDB
    - artwork_analysis_flow: Analyze artwork with vision models
    - style_graph_flow: Build style/similarity knowledge graph

Usage:
    from cocoindex_flows import artwork_embedding_flow

    # Setup and run
    artwork_embedding_flow.setup()
    with cocoindex.FlowLiveUpdater(artwork_embedding_flow) as updater:
        updater.wait()
"""

from cocoindex_flows.artwork_embedding import (
    artwork_embedding_flow,
    embed_image_clip,
    search_similar_artwork,
)

__all__ = [
    "artwork_embedding_flow",
    "embed_image_clip",
    "search_similar_artwork",
]
