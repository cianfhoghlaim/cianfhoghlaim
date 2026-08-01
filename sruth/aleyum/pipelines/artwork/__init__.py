"""Artwork Processing Pipeline.

DLT source for downloading, caching, and processing album artwork.
Integrates with vision models for style analysis and generation.

Usage:
    from pipelines.artwork import artwork_source, process_artwork

    # DLT pipeline
    pipeline = dlt.pipeline(
        pipeline_name="artwork_processing",
        destination="duckdb",
        dataset_name="artwork_data",
    )
    source = artwork_source(input_table="label_data.artwork")
    pipeline.run(source)
"""

from pipelines.artwork.source import (
    ArtworkImage,
    ArtworkMetadata,
    artwork_source,
    download_artwork,
    extract_image_metadata,
    run_artwork_pipeline,
)

__all__ = [
    "ArtworkImage",
    "ArtworkMetadata",
    "artwork_source",
    "download_artwork",
    "extract_image_metadata",
    "run_artwork_pipeline",
]
