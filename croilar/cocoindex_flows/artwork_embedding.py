"""Artwork Image Embedding Flow.

CocoIndex flow for embedding album artwork using CLIP model
and storing in LanceDB for similarity search.

This flow:
1. Reads artwork records from DuckDB (output of DLT pipeline)
2. Downloads images from R2 cache
3. Embeds using CLIP (openai/clip-vit-large-patch14)
4. Optionally generates captions using vision LLM
5. Exports to LanceDB for vector similarity search

Usage:
    import cocoindex
    from cocoindex_flows import artwork_embedding_flow

    cocoindex.init()
    artwork_embedding_flow.setup()

    # Run once
    cocoindex.run_flows()

    # Or live updates
    with cocoindex.FlowLiveUpdater(artwork_embedding_flow) as updater:
        updater.wait()

Query:
    from cocoindex_flows import search_similar_artwork

    results = await search_similar_artwork("abstract colorful geometric")
"""

import datetime
import functools
import io
import math
import os
from typing import Any, Literal

import cocoindex
import cocoindex.targets.lancedb as coco_lancedb
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


# Configuration
DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "./aleyum.duckdb")
LANCEDB_URI = os.environ.get("LANCEDB_URI", "./lancedb_data")
LANCEDB_TABLE = "artwork_embeddings"
CLIP_MODEL_NAME = os.environ.get("CLIP_MODEL", "openai/clip-vit-large-patch14")
VISION_MODEL = os.environ.get("VISION_MODEL", "qwen3-vl")  # From litellm_config.yaml


@functools.cache
def get_clip_model() -> tuple[CLIPModel, CLIPProcessor]:
    """Load and cache CLIP model.

    Returns:
        Tuple of (model, processor)
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained(CLIP_MODEL_NAME).to(device)
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
    return model, processor


def embed_query(text: str) -> list[float]:
    """Embed text query using CLIP text encoder.

    For searching artwork by text description.

    Args:
        text: Search query

    Returns:
        768-dimensional embedding vector
    """
    model, processor = get_clip_model()
    device = next(model.parameters()).device

    inputs = processor(text=[text], return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        features = model.get_text_features(**inputs)

    return features[0].cpu().tolist()


@cocoindex.op.function(cache=True, behavior_version=1, gpu=True)
def embed_image_clip(
    img_bytes: bytes,
) -> cocoindex.Vector[cocoindex.Float32, Literal[768]]:
    """Embed image using CLIP vision encoder.

    This is the CocoIndex transform function for embedding artwork.

    Args:
        img_bytes: Raw image bytes

    Returns:
        768-dimensional CLIP embedding vector
    """
    model, processor = get_clip_model()
    device = next(model.parameters()).device

    # Load and preprocess image
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        features = model.get_image_features(**inputs)

    return features[0].cpu().tolist()


@cocoindex.op.function(cache=True, behavior_version=1)
def extract_color_palette(img_bytes: bytes) -> list[str]:
    """Extract dominant colors from image.

    Args:
        img_bytes: Raw image bytes

    Returns:
        List of hex color codes
    """
    try:
        from sklearn.cluster import KMeans
        import numpy as np

        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        image.thumbnail((100, 100))

        pixels = np.array(image.getdata())
        kmeans = KMeans(n_clusters=5, n_init=10, random_state=42)
        kmeans.fit(pixels)

        colors = []
        for center in kmeans.cluster_centers_:
            r, g, b = map(int, center)
            colors.append(f"#{r:02x}{g:02x}{b:02x}")

        return colors

    except Exception:
        return []


@cocoindex.flow_def(name="ArtworkEmbedding")
def artwork_embedding_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """Define the artwork embedding flow.

    Reads artwork images, embeds with CLIP, exports to LanceDB.

    Args:
        flow_builder: CocoIndex flow builder
        data_scope: Data scope for flow variables
    """
    # Feature flags
    enable_captioning = os.environ.get("ENABLE_ARTWORK_CAPTIONING", "0").lower() in (
        "true",
        "1",
    )
    enable_vector_index = os.environ.get(
        "ENABLE_LANCEDB_VECTOR_INDEX", "0"
    ).lower() in ("true", "1")

    # Source: Read artwork files from R2 cache directory or URL list
    # For local development, use LocalFile source
    # For production, use DuckDB source to read URLs then fetch
    artwork_dir = os.environ.get("ARTWORK_DIR", "./artwork_cache")

    data_scope["artwork"] = flow_builder.add_source(
        cocoindex.sources.LocalFile(
            path=artwork_dir,
            included_patterns=["*.jpg", "*.jpeg", "*.png", "*.webp"],
            binary=True,
        ),
        refresh_interval=datetime.timedelta(minutes=5),
    )

    # Collector for embeddings
    artwork_embeddings = data_scope.add_collector()

    with data_scope["artwork"].row() as img:
        # Embed image with CLIP
        img["embedding"] = img["content"].transform(embed_image_clip)

        # Extract color palette
        img["colors"] = img["content"].transform(extract_color_palette)

        # Build collected fields
        collect_fields = {
            "id": cocoindex.GeneratedField.UUID,
            "filename": img["filename"],
            "embedding": img["embedding"],
            "colors": img["colors"],
        }

        # Optional: Generate caption with vision model
        if enable_captioning:
            vision_model = os.environ.get("VISION_MODEL", "qwen3-vl")
            img["caption"] = flow_builder.transform(
                cocoindex.functions.ExtractByLlm(
                    llm_spec=cocoindex.llm.LlmSpec(
                        api_type=cocoindex.LlmApiType.OLLAMA,
                        model=vision_model,
                    ),
                    instruction=(
                        "Analyze this album artwork. Describe:\n"
                        "1. Visual style (abstract, photographic, illustrated, etc.)\n"
                        "2. Color palette and mood\n"
                        "3. Main subjects or themes\n"
                        "4. Genre associations (electronic, ambient, jazz, etc.)\n"
                        "Keep it concise, 2-3 sentences."
                    ),
                    output_type=str,
                ),
                image=img["content"],
            )
            collect_fields["caption"] = img["caption"]

        artwork_embeddings.collect(**collect_fields)

    # Vector indexes for similarity search
    vector_indexes = []
    if enable_vector_index:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                "embedding",
                cocoindex.VectorSimilarityMetric.COSINE_DISTANCE,
            )
        )

    # Export to LanceDB
    artwork_embeddings.export(
        "artwork_embeddings",
        coco_lancedb.LanceDB(db_uri=LANCEDB_URI, table_name=LANCEDB_TABLE),
        primary_key_fields=["id"],
        vector_indexes=vector_indexes,
    )


@artwork_embedding_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(
        embedding=["embedding"],
        score="score",
    ),
)
async def search_similar_artwork(
    query: str,
    limit: int = 10,
) -> cocoindex.QueryOutput:
    """Search for similar artwork by text description.

    Uses CLIP text encoder to embed query and search
    the artwork vector database.

    Args:
        query: Text description (e.g., "abstract colorful geometric")
        limit: Maximum number of results

    Returns:
        QueryOutput with matching artwork
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(LANCEDB_TABLE)

    # Embed query text with CLIP
    query_embedding = embed_query(query)

    # Search in LanceDB
    search = await table.search(query_embedding, vector_column_name="embedding")
    search_results = await search.limit(limit).to_list()

    return cocoindex.QueryOutput(
        results=[
            {
                "filename": result["filename"],
                "embedding": result["embedding"],
                "colors": result.get("colors", []),
                "caption": result.get("caption"),
                # Cosine distance to similarity score
                "score": 1.0 - result["_distance"],
            }
            for result in search_results
        ],
        query_info=cocoindex.QueryInfo(
            embedding=query_embedding,
            similarity_metric=cocoindex.VectorSimilarityMetric.COSINE_DISTANCE,
        ),
    )


async def search_by_image(
    image_bytes: bytes,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search for similar artwork by image.

    Args:
        image_bytes: Query image bytes
        limit: Maximum results

    Returns:
        List of similar artwork records
    """
    db = await coco_lancedb.connect_async(LANCEDB_URI)
    table = await db.open_table(LANCEDB_TABLE)

    # Embed query image
    query_embedding = embed_image_clip(image_bytes)

    # Search
    search = await table.search(query_embedding, vector_column_name="embedding")
    search_results = await search.limit(limit).to_list()

    return [
        {
            "filename": result["filename"],
            "colors": result.get("colors", []),
            "caption": result.get("caption"),
            "score": 1.0 - result["_distance"],
        }
        for result in search_results
    ]


# DuckDB source variant for reading from DLT output
@cocoindex.flow_def(name="ArtworkEmbeddingFromDuckDB")
def artwork_embedding_duckdb_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """Artwork embedding flow that reads from DuckDB.

    Reads artwork URLs from the DLT output table and fetches
    images for embedding.

    This is the production flow that integrates with the
    DLT artwork pipeline.
    """
    import httpx

    enable_vector_index = os.environ.get(
        "ENABLE_LANCEDB_VECTOR_INDEX", "0"
    ).lower() in ("true", "1")

    # Source: DuckDB table with artwork URLs
    data_scope["artwork"] = flow_builder.add_source(
        cocoindex.sources.DuckDB(
            path=DUCKDB_PATH,
            query="""
                SELECT
                    id,
                    original_url,
                    r2_url,
                    entity_id,
                    entity_type,
                    label
                FROM artwork_data.images
                WHERE r2_url IS NOT NULL AND r2_url != ''
            """,
        ),
        refresh_interval=datetime.timedelta(minutes=10),
    )

    artwork_embeddings = data_scope.add_collector()

    with data_scope["artwork"].row() as record:
        # Fetch image from R2 URL
        record["image_bytes"] = flow_builder.transform(
            cocoindex.functions.HttpFetch(),
            url=record["r2_url"],
        )

        # Embed with CLIP
        record["embedding"] = record["image_bytes"].transform(embed_image_clip)

        # Extract colors
        record["colors"] = record["image_bytes"].transform(extract_color_palette)

        artwork_embeddings.collect(
            id=record["id"],
            filename=record["entity_id"],
            entity_type=record["entity_type"],
            label=record["label"],
            original_url=record["original_url"],
            r2_url=record["r2_url"],
            embedding=record["embedding"],
            colors=record["colors"],
        )

    vector_indexes = []
    if enable_vector_index:
        vector_indexes.append(
            cocoindex.VectorIndexDef(
                "embedding",
                cocoindex.VectorSimilarityMetric.COSINE_DISTANCE,
            )
        )

    artwork_embeddings.export(
        "artwork_embeddings",
        coco_lancedb.LanceDB(db_uri=LANCEDB_URI, table_name=LANCEDB_TABLE),
        primary_key_fields=["id"],
        vector_indexes=vector_indexes,
    )


def run_embedding_flow(use_duckdb: bool = False) -> None:
    """Run the artwork embedding flow.

    Args:
        use_duckdb: Use DuckDB source instead of local files
    """
    import cocoindex

    cocoindex.init()

    if use_duckdb:
        artwork_embedding_duckdb_flow.setup(report_to_stdout=True)
        cocoindex.run_flows([artwork_embedding_duckdb_flow])
    else:
        artwork_embedding_flow.setup(report_to_stdout=True)
        cocoindex.run_flows([artwork_embedding_flow])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run artwork embedding flow")
    parser.add_argument(
        "--duckdb",
        action="store_true",
        help="Use DuckDB source (reads from DLT output)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run in live update mode",
    )

    args = parser.parse_args()

    import cocoindex

    cocoindex.init()

    flow = artwork_embedding_duckdb_flow if args.duckdb else artwork_embedding_flow
    flow.setup(report_to_stdout=True)

    if args.live:
        with cocoindex.FlowLiveUpdater(flow) as updater:
            updater.wait()
    else:
        cocoindex.run_flows([flow])
