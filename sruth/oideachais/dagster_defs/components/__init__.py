"""Oideachais Dagster component loader.

This module loads YAML component definitions and creates Dagster assets
for the Irish curriculum PDF processing pipeline.

Usage:
    from sruth.oideachais.dagster_defs.components import load_oideachais_components

    defs = load_oideachais_components()
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dagster import Definitions

from sruth.shared.dagster.components.sruth_components import (
    CurriculumDLTComponent,
    MultiNationCurriculumComponent,
    PDFProcessingComponent,
    EmbeddingComponent,
    SruthPipelineComponent,
)


def load_curriculum_components(
    cycles: list[str] | None = None,
) -> Definitions:
    """Load curriculum DLT components.

    Args:
        cycles: Curriculum cycles to ingest (default: all)

    Returns:
        Dagster Definitions with curriculum assets
    """
    component = CurriculumDLTComponent(
        cycles=cycles or ["junior_cycle", "senior_cycle", "primary", "early_childhood"],
    )

    return component.build_defs(context=None)


def load_multi_nation_components(
    nations: list[str] | None = None,
) -> Definitions:
    """Load multi-nation curriculum components.

    Args:
        nations: Nations to ingest (default: all UK nations)

    Returns:
        Dagster Definitions with multi-nation assets
    """
    component = MultiNationCurriculumComponent(
        nations=nations or ["england", "scotland", "wales", "northern_ireland", "isle_of_man"],
    )

    return component.build_defs(context=None)


def load_pdf_components(
    enable_ocr: bool = True,
    ocr_backend: str = "docling",
) -> Definitions:
    """Load PDF processing components.

    Args:
        enable_ocr: Enable OCR text extraction
        ocr_backend: OCR backend (docling, paddleocr, dots)

    Returns:
        Dagster Definitions with PDF processing assets
    """
    component = PDFProcessingComponent(
        enable_ocr=enable_ocr,
        ocr_backend=ocr_backend,
    )

    return component.build_defs(context=None)


def load_embedding_components(
    model: str = "BAAI/bge-m3",
    dimension: int = 1024,
    batch_size: int = 100,
) -> Definitions:
    """Load embedding components.

    Args:
        model: Embedding model name
        dimension: Embedding dimension
        batch_size: Batch size for embedding generation

    Returns:
        Dagster Definitions with embedding assets
    """
    component = EmbeddingComponent(
        model=model,
        dimension=dimension,
        batch_size=batch_size,
    )

    return component.build_defs(context=None)


def load_oideachais_components(
    component_dir: str | None = None,
) -> Definitions:
    """Load all Oideachais components.

    This is the main entry point for loading Oideachais Dagster definitions.

    Args:
        component_dir: Directory containing component YAML files (unused, for compatibility)

    Returns:
        Dagster Definitions

    Example:
        from sruth.oideachais.dagster_defs.components import load_oideachais_components

        defs = load_oideachais_components()
    """
    # Use the factory component to return all existing assets
    # This allows gradual migration to component-based config
    component = SruthPipelineComponent(pipeline="oideachais")

    return component.build_defs(context=None)


def load_oideachais_from_yaml(
    config_path: str | None = None,
) -> Definitions:
    """Load Oideachais components from YAML configuration.

    Args:
        config_path: Path to YAML component config

    Returns:
        Dagster Definitions with configured assets
    """
    if config_path is None:
        config_path = str(
            Path(__file__).parent / "pdf_pipeline_component.yaml"
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

        if "curriculum" in component_type.lower():
            component = CurriculumDLTComponent(**attributes)
        elif "multi_nation" in component_type.lower():
            component = MultiNationCurriculumComponent(**attributes)
        elif "pdf" in component_type.lower():
            component = PDFProcessingComponent(**attributes)
        elif "embedding" in component_type.lower():
            component = EmbeddingComponent(**attributes)
        else:
            continue

        defs = component.build_defs(context=None)
        all_assets.extend(defs.assets)

    return Definitions(assets=all_assets)


class OideachaisPipelineComponent:
    """Oideachais pipeline component for backward compatibility.

    This class provides the same interface as the placeholder implementation
    but delegates to the new component-based approach.
    """

    def __init__(
        self,
        name: str = "oideachais_pdf",
        cycles: list[str] | None = None,
        subjects: list[str] | None = None,
        languages: list[str] | None = None,
    ) -> None:
        """Initialize the Oideachais pipeline component.

        Args:
            name: Pipeline name
            cycles: Curriculum cycles (default: all)
            subjects: Subjects to process (default: all)
            languages: Languages (default: en, ga)
        """
        self.name = name
        self.cycles = cycles or ["junior_cycle", "senior_cycle", "primary"]
        self.subjects = subjects or [
            "mathematics", "english", "irish", "science",
            "history", "geography",
        ]
        self.languages = languages or ["en", "ga"]

    def get_partitions(self) -> dict[str, Any]:
        """Get partition definitions for multi-dimensional partitioning.

        Returns:
            Partition configuration
        """
        return {
            "cycle": self.cycles,
            "subject": self.subjects,
            "language": self.languages,
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
                "namespace": "oideachais",
            },
            "motherduck": {
                "token": os.getenv("MOTHERDUCK_TOKEN"),
                "database": os.getenv("MOTHERDUCK_DATABASE", "sruth"),
            },
            "lancedb": {
                "uri": os.getenv("LANCEDB_URI", "s3://lance"),
                "namespace": "oideachais",
            },
        }

    def build_defs(self, context: Any = None) -> Definitions:
        """Build Dagster definitions from this component.

        Args:
            context: Component load context (unused)

        Returns:
            Dagster Definitions
        """
        component = SruthPipelineComponent(pipeline="oideachais")
        return component.build_defs(context=context)


__all__ = [
    "load_oideachais_components",
    "load_curriculum_components",
    "load_multi_nation_components",
    "load_pdf_components",
    "load_embedding_components",
    "load_oideachais_from_yaml",
    "OideachaisPipelineComponent",
]
