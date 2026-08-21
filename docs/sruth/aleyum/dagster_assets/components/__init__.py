"""Aleyum Dagster component loader.

This module loads YAML component definitions and creates Dagster assets
for the music platform web scraping pipeline.

Usage:
    from sruth.aleyum.dagster_assets.components import load_aleyum_components

    defs = load_aleyum_components()
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dagster import Definitions

from sruth.shared.dagster.components.sruth_components import (
    MusicIngestionComponent,
    ArtworkProcessingComponent,
    SruthPipelineComponent,
)


def load_music_ingestion_components(
    platforms: list[str] | None = None,
    include_labels: bool = True,
) -> Definitions:
    """Load music ingestion components.

    Args:
        platforms: Music platforms to scrape (spotify, soundcloud, bandcamp)
        include_labels: Include record label scraping

    Returns:
        Dagster Definitions with music ingestion assets
    """
    component = MusicIngestionComponent(
        platforms=platforms or ["spotify", "soundcloud"],
        include_labels=include_labels,
    )

    return component.build_defs(context=None)


def load_artwork_components(
    clip_model: str = "openai/clip-vit-large-patch14",
    dimension: int = 768,
) -> Definitions:
    """Load artwork processing components.

    Args:
        clip_model: CLIP model for artwork
        dimension: Embedding dimension

    Returns:
        Dagster Definitions with artwork processing assets
    """
    component = ArtworkProcessingComponent(
        clip_model=clip_model,
        dimension=dimension,
    )

    return component.build_defs(context=None)


def load_aleyum_components(
    component_dir: str | None = None,
) -> Definitions:
    """Load all Aleyum components.

    This is the main entry point for loading Aleyum Dagster definitions.

    Args:
        component_dir: Directory containing component YAML files (unused, for compatibility)

    Returns:
        Dagster Definitions

    Example:
        from sruth.aleyum.dagster_assets.components import load_aleyum_components

        defs = load_aleyum_components()
    """
    # Use the factory component to return all existing assets
    # This allows gradual migration to component-based config
    component = SruthPipelineComponent(pipeline="aleyum")

    return component.build_defs(context=None)


def load_aleyum_from_yaml(
    config_path: str | None = None,
) -> Definitions:
    """Load Aleyum components from YAML configuration.

    Args:
        config_path: Path to YAML component config

    Returns:
        Dagster Definitions with configured assets
    """
    if config_path is None:
        config_path = str(Path(__file__).parent / "scraping_pipeline_component.yaml")

    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Parse YAML config and build components
    components = config.get("components", [])
    all_assets = []

    for component_config in components:
        component_type = component_config.get("type")
        attributes = component_config.get("attributes", {})

        if "music" in component_type.lower() or "scraping" in component_type.lower():
            component = MusicIngestionComponent(**attributes)
        elif "artwork" in component_type.lower():
            component = ArtworkProcessingComponent(**attributes)
        else:
            continue

        defs = component.build_defs(context=None)
        all_assets.extend(defs.assets)

    return Definitions(assets=all_assets)


class ScrapingPipelineComponent:
    """Aleyum web scraping pipeline component for backward compatibility.

    This class provides the same interface as the placeholder implementation
    but delegates to the new component-based approach.
    """

    def __init__(
        self,
        name: str = "aleyum_scraping",
        platforms: list[str] | None = None,
    ) -> None:
        """Initialize the scraping pipeline component.

        Args:
            name: Pipeline name
            platforms: Music platforms to scrape
        """
        self.name = name
        self.platforms = platforms or [
            "spotify",
            "soundcloud",
            "bandcamp",
            "musicbrainz",
            "labels",
        ]

    def get_partitions(self) -> dict[str, Any]:
        """Get partition definitions.

        Returns:
            Partition configuration
        """
        return {
            "platform": self.platforms,
            "content_type": ["tracks", "albums", "artists", "playlists", "labels"],
        }

    def get_browser_config(self) -> dict[str, Any]:
        """Get browser backend configuration.

        Returns:
            Browser configuration dict
        """
        return {
            "backend": os.getenv("BROWSER_BACKEND", "stagehand"),
            "headless": os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
            "timeout": int(os.getenv("BROWSER_TIMEOUT", "30")),
            "viewport": {
                "width": int(os.getenv("BROWSER_WIDTH", "1920")),
                "height": int(os.getenv("BROWSER_HEIGHT", "1080")),
            },
        }

    def get_storage_config(self) -> dict[str, Any]:
        """Get storage configuration for exports.

        Returns:
            Storage configuration dict
        """
        return {
            "ducklake": {
                "catalog_uri": os.getenv("LAKEKEEPER_CATALOG_URI", "http://lakekeeper:8181"),
                "warehouse": os.getenv("ICEBERG_WAREHOUSE", "s3://garage/warehouse"),
                "namespace": "aleyum",
            },
            "motherduck": {
                "token": os.getenv("MOTHERDUCK_TOKEN"),
                "database": os.getenv("MOTHERDUCK_DATABASE", "sruth"),
            },
            "postgres": {
                "url": os.getenv(
                    "POSTGRES_URL", "postgresql://postgres:postgres@postgres:5432/aleyum"
                ),
            },
        }

    def get_artwork_storage_config(self) -> dict[str, Any]:
        """Get artwork storage configuration.

        Returns:
            Artwork storage configuration (S3/R2)
        """
        return {
            "type": "s3",
            "bucket": os.getenv("ARTWORK_BUCKET", "music-artwork"),
            "prefix": "aleyum/{platform}/{year}/{month}/",
            "endpoint_url": os.getenv("GARAGE_ENDPOINT_URL", "http://garage:3900"),
            "aws_access_key_id": os.getenv("GARAGE_ACCESS_KEY", "garage_key"),
            "aws_secret_access_key": os.getenv("GARAGE_SECRET_KEY", "garage_secret"),
            # CRITICAL: Path-style URLs for Garage/MinIO
            "client_kwargs": {"addressing_style": "path"},
        }

    def build_defs(self, context: Any = None) -> Definitions:
        """Build Dagster definitions from this component.

        Args:
            context: Component load context (unused)

        Returns:
            Dagster Definitions
        """
        component = SruthPipelineComponent(pipeline="aleyum")
        return component.build_defs(context=context)


__all__ = [
    "load_aleyum_components",
    "load_music_ingestion_components",
    "load_artwork_components",
    "load_aleyum_from_yaml",
    "ScrapingPipelineComponent",
]
