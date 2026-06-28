"""Crypteolas Dagster component loader.

This module loads YAML component definitions and creates Dagster assets
for the REST API ingestion pipeline.

Usage:
    from tuatha.crypteolas.dagster_assets.components import load_crypteolas_components

    defs = load_crypteolas_components()
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dagster import Definitions

from sruth.tuatha.crypteolas._shims.dagster.components.sruth_components import (
    GitHubIngestionComponent,
    DeFiIngestionComponent,
    CodeEmbeddingComponent,
    SruthPipelineComponent,
)


def load_github_components(
    include_issues: bool = True,
    include_prs: bool = True,
    include_commits: bool = True,
    include_code_content: bool = False,
) -> Definitions:
    """Load GitHub ingestion components.

    Args:
        include_issues: Include GitHub issues
        include_prs: Include pull requests
        include_commits: Include commit history
        include_code_content: Clone and index code content

    Returns:
        Dagster Definitions with GitHub assets
    """
    component = GitHubIngestionComponent(
        include_issues=include_issues,
        include_prs=include_prs,
        include_commits=include_commits,
        include_code_content=include_code_content,
    )

    return component.build_defs(context=None)


def load_defi_components(
    include_tvl: bool = True,
    include_yields: bool = True,
    include_prices: bool = True,
) -> Definitions:
    """Load DeFi ingestion components.

    Args:
        include_tvl: Include TVL data from DeFiLlama
        include_yields: Include yield data
        include_prices: Include token prices

    Returns:
        Dagster Definitions with DeFi assets
    """
    component = DeFiIngestionComponent(
        include_tvl=include_tvl,
        include_yields=include_yields,
        include_prices=include_prices,
    )

    return component.build_defs(context=None)


def load_code_embedding_components(
    model: str = "microsoft/codebert-base",
    dimension: int = 768,
    batch_size: int = 100,
) -> Definitions:
    """Load code embedding components.

    Args:
        model: Embedding model for code
        dimension: Embedding dimension
        batch_size: Batch size for embedding generation

    Returns:
        Dagster Definitions with code embedding assets
    """
    component = CodeEmbeddingComponent(
        model=model,
        dimension=dimension,
        batch_size=batch_size,
    )

    return component.build_defs(context=None)


def load_crypteolas_components(
    component_dir: str | None = None,
) -> Definitions:
    """Load all Crypteolas components.

    This is the main entry point for loading Crypteolas Dagster definitions.

    Args:
        component_dir: Directory containing component YAML files (unused, for compatibility)

    Returns:
        Dagster Definitions

    Example:
        from tuatha.crypteolas.dagster_assets.components import load_crypteolas_components

        defs = load_crypteolas_components()
    """
    # Use the factory component to return all existing assets
    # This allows gradual migration to component-based config
    component = SruthPipelineComponent(pipeline="crypteolas")

    return component.build_defs(context=None)


def load_crypteolas_from_yaml(
    config_path: str | None = None,
) -> Definitions:
    """Load Crypteolas components from YAML configuration.

    Args:
        config_path: Path to YAML component config

    Returns:
        Dagster Definitions with configured assets
    """
    if config_path is None:
        config_path = str(
            Path(__file__).parent / "rest_pipeline_component.yaml"
        )

    import yaml

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Parse YAML config and build components
    components = config.get("components", [])
    all_assets = []

    for component_config in components:
        component_type = component_config.get("type")
        attributes = component_config.get("attributes", {})

        if "github" in component_type.lower():
            component = GitHubIngestionComponent(**attributes)
        elif "defi" in component_type.lower():
            component = DeFiIngestionComponent(**attributes)
        elif "embedding" in component_type.lower() and "code" in component_type.lower():
            component = CodeEmbeddingComponent(**attributes)
        else:
            continue

        defs = component.build_defs(context=None)
        all_assets.extend(defs.assets)

    return Definitions(assets=all_assets)


class CrypteolasPipelineComponent:
    """Crypteolas pipeline component for backward compatibility.

    This class provides the same interface as the placeholder implementation
    but delegates to the new component-based approach.
    """

    def __init__(
        self,
        name: str = "crypteolas_rest",
        sources: list[str] | None = None,
    ) -> None:
        """Initialize the Crypteolas pipeline component.

        Args:
            name: Pipeline name
            sources: REST API sources to ingest (default: all)
        """
        self.name = name
        self.sources = sources or [
            "github",
            "defillama",
            "coingecko",
            "binance",
        ]

    def get_partitions(self) -> dict[str, Any]:
        """Get partition definitions.

        Returns:
            Partition configuration
        """
        return {
            "source": self.sources,
            "content_type": ["repos", "issues", "prs", "commits", "protocols", "yields", "prices"],
        }

    def get_storage_config(self) -> dict[str, Any]:
        """Get storage configuration for exports.

        Returns:
            Storage configuration dict
        """
        return {
            "ducklake": {
                "catalog_uri": os.getenv(
                    "LAKEKEEPER_CATALOG_URI",
                    "http://lakekeeper:8181"
                ),
                "warehouse": os.getenv(
                    "ICEBERG_WAREHOUSE",
                    "s3://garage/warehouse"
                ),
                "namespace": "crypteolas",
            },
            "motherduck": {
                "token": os.getenv("MOTHERDUCK_TOKEN"),
                "database": os.getenv("MOTHERDUCK_DATABASE", "sruth"),
            },
            "postgres": {
                "url": os.getenv(
                    "POSTGRES_URL",
                    "postgresql://postgres:postgres@postgres:5432/crypteolas"
                ),
            },
        }

    def build_defs(self, context: Any = None) -> Definitions:
        """Build Dagster definitions from this component.

        Args:
            context: Component load context (unused)

        Returns:
            Dagster Definitions
        """
        component = SruthPipelineComponent(pipeline="crypteolas")
        return component.build_defs(context=context)


__all__ = [
    "load_crypteolas_components",
    "load_github_components",
    "load_defi_components",
    "load_code_embedding_components",
    "load_crypteolas_from_yaml",
    "CrypteolasPipelineComponent",
]
