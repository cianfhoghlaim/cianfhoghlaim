"""Sruth Pipeline Components - Component-based Dagster assets.

This module provides executable Dagster components for sruth pipelines
following the official Dagster component pattern with dg.Field.

References:
- https://docs.dagster.io/guides/build/components/asset-factories-to-components
- https://docs.dagster.io/integrations/libraries/dlt

The dg.Field Pattern:
    class MyComponent(dg.Component, dg.Resolvable, dg.Model):
        name: str = dg.Field(description="Component name")
        enabled: bool = dg.Field(default=True)

This enables:
- YAML-based configuration with schema validation
- Type-safe attribute access
- Automatic documentation generation
- Component composition and nesting
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import dagster as dg


# ============================================================================
# OIDEACHAS COMPONENTS
# ============================================================================

@dataclass
class CurriculumDLTComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for Irish curriculum DLT assets.

    Creates @dlt_assets for each curriculum cycle with MultiPartition
    support for subject and language dimensions.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.CurriculumDLTComponent
        attributes:
          cycles:
            - "junior_cycle"
            - "senior_cycle"
          group_name: "curriculum"
          enable_ducklake: true
    """

    cycles: list[str] = dg.Field(
        default=["junior_cycle", "senior_cycle", "primary", "early_childhood"],
        description="Curriculum cycles to ingest",
    )
    group_name: str = dg.Field(
        default="curriculum",
        description="Asset group name",
    )
    enable_ducklake: bool = dg.Field(
        default=True,
        description="Use DuckLake (Iceberg+S3) destination",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build curriculum DLT assets."""
        from sruth.oideachais.dagster_defs.assets.ireland import (
            CYCLE_PARTITIONS,
            create_cycle_asset,
            create_short_course_asset,
        )

        assets = []

        # Create one asset per cycle
        for cycle in self.cycles:
            if cycle in CYCLE_PARTITIONS:
                asset = create_cycle_asset(cycle)
                assets.append(asset)

        # Add short courses asset
        assets.append(create_short_course_asset())

        return dg.Definitions(assets=assets)


@dataclass
class MultiNationCurriculumComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for multi-nation curriculum ingestion.

    Creates assets for all UK nations: England, Scotland, Wales,
    Northern Ireland, and Isle of Man.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.MultiNationCurriculumComponent
        attributes:
          nations:
            - "england"
            - "scotland"
            - "wales"
            - "northern_ireland"
            - "isle_of_man"
    """

    nations: list[str] = dg.Field(
        default=["england", "scotland", "wales", "northern_ireland", "isle_of_man"],
        description="UK nations to ingest curriculum from",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build multi-nation curriculum assets."""
        from sruth.oideachais.dagster_defs.assets.multi_nation_curriculum_assets import (
            create_all_nation_assets,
        )

        assets = create_all_nation_assets(nations=self.nations)

        return dg.Definitions(assets=assets)


@dataclass
class PDFProcessingComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for PDF processing pipeline.

    Creates assets for downloading PDFs and extracting text via OCR.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.PDFProcessingComponent
        attributes:
          enable_ocr: true
          ocr_backend: "docling"
    """

    enable_ocr: bool = dg.Field(
        default=True,
        description="Enable OCR text extraction",
    )
    ocr_backend: str = dg.Field(
        default="docling",
        description="OCR backend: docling, paddleocr, dots",
    )
    pdf_bucket: str = dg.Field(
        default="curriculum-pdfs",
        description="S3 bucket for PDF storage",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build PDF processing assets."""
        from sruth.oideachais.dagster_defs.assets.pdf_assets import (
            pdf_downloads_asset,
            pdf_extracted_text_asset,
        )

        return dg.Definitions(
            assets=[
                pdf_downloads_asset,
                pdf_extracted_text_asset,
            ],
        )


@dataclass
class EmbeddingComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for curriculum text embedding generation.

    Creates assets for generating BGE-M3 embeddings from curriculum text.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.EmbeddingComponent
        attributes:
          model: "BAAI/bge-m3"
          dimension: 1024
          batch_size: 100
    """

    model: str = dg.Field(
        default="BAAI/bge-m3",
        description="Embedding model name",
    )
    dimension: int = dg.Field(
        default=1024,
        description="Embedding dimension",
    )
    batch_size: int = dg.Field(
        default=100,
        description="Batch size for embedding generation (min 100 for performance)",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build embedding assets."""
        from sruth.oideachais.dagster_defs.assets.embedding_assets import (
            curriculum_text_embeddings_asset,
            curriculum_chunk_embeddings_asset,
        )

        return dg.Definitions(
            assets=[
                curriculum_text_embeddings_asset,
                curriculum_chunk_embeddings_asset,
            ],
        )


# ============================================================================
# CRYPTEOLAS COMPONENTS
# ============================================================================

@dataclass
class GitHubIngestionComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for GitHub REST API ingestion.

    Creates assets for GitHub repositories, issues, PRs, and commits.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.GitHubIngestionComponent
        attributes:
          include_issues: true
          include_prs: true
          include_commits: true
    """

    include_issues: bool = dg.Field(
        default=True,
        description="Include GitHub issues",
    )
    include_prs: bool = dg.Field(
        default=True,
        description="Include pull requests",
    )
    include_commits: bool = dg.Field(
        default=True,
        description="Include commit history",
    )
    include_code_content: bool = dg.Field(
        default=False,
        description="Clone and index code content",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build GitHub ingestion assets."""
        from sruth.crypteolas.dagster_assets.github_assets import (
            github_repo_data,
            github_issues,
            github_pull_requests,
            github_commits,
            github_code_content,
        )

        assets = [
            github_repo_data,
        ]

        if self.include_issues:
            assets.append(github_issues)
        if self.include_prs:
            assets.append(github_pull_requests)
        if self.include_commits:
            assets.append(github_commits)
        if self.include_code_content:
            assets.append(github_code_content)

        return dg.Definitions(assets=assets)


@dataclass
class DeFiIngestionComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for DeFi protocol REST API ingestion.

    Creates assets for DeFi TVL, yields, and token prices.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.DeFiIngestionComponent
        attributes:
          include_tvl: true
          include_yields: true
          include_prices: true
    """

    include_tvl: bool = dg.Field(
        default=True,
        description="Include TVL data from DeFiLlama",
    )
    include_yields: bool = dg.Field(
        default=True,
        description="Include yield data",
    )
    include_prices: bool = dg.Field(
        default=True,
        description="Include token prices",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build DeFi ingestion assets."""
        from sruth.crypteolas.dagster_assets.defi_assets import (
            defi_protocols_asset,
            defi_tvl_asset,
            defi_yields_asset,
            token_prices_asset,
        )

        assets = []

        if self.include_tvl:
            assets.extend([defi_protocols_asset, defi_tvl_asset])
        if self.include_yields:
            assets.append(defi_yields_asset)
        if self.include_prices:
            assets.append(token_prices_asset)

        return dg.Definitions(assets=assets)


@dataclass
class CodeEmbeddingComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for code embedding generation.

    Creates assets for generating embeddings from code.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.CodeEmbeddingComponent
        attributes:
          model: "microsoft/codebert-base"
          dimension: 768
          batch_size: 100
    """

    model: str = dg.Field(
        default="microsoft/codebert-base",
        description="Embedding model for code",
    )
    dimension: int = dg.Field(
        default=768,
        description="Embedding dimension",
    )
    batch_size: int = dg.Field(
        default=100,
        description="Batch size for embedding generation",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build code embedding assets."""
        from sruth.crypteolas.dagster_assets.embedding_assets import (
            code_embeddings_asset,
        )

        return dg.Definitions(assets=[code_embeddings_asset])


# ============================================================================
# ALEYUM COMPONENTS
# ============================================================================

@dataclass
class MusicIngestionComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for music platform ingestion.

    Creates assets for Spotify, SoundCloud, and label scraping.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.MusicIngestionComponent
        attributes:
          platforms:
            - "spotify"
            - "soundcloud"
    """

    platforms: list[str] = dg.Field(
        default=["spotify", "soundcloud"],
        description="Music platforms to scrape",
    )
    include_labels: bool = dg.Field(
        default=True,
        description="Include record label scraping",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build music ingestion assets."""
        from sruth.aleyum.dagster_assets.dlt_assets import (
            spotify_ingestion_asset,
            soundcloud_ingestion_asset,
            label_ingestion_asset,
        )

        assets = []

        if "spotify" in self.platforms:
            assets.append(spotify_ingestion_asset)
        if "soundcloud" in self.platforms:
            assets.append(soundcloud_ingestion_asset)
        if self.include_labels:
            assets.append(label_ingestion_asset)

        return dg.Definitions(assets=assets)


@dataclass
class ArtworkProcessingComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for music artwork processing.

    Creates assets for downloading artwork and generating CLIP embeddings.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.ArtworkProcessingComponent
        attributes:
          clip_model: "openai/clip-vit-large-patch14"
          dimension: 768
    """

    clip_model: str = dg.Field(
        default="openai/clip-vit-large-patch14",
        description="CLIP model for artwork",
    )
    dimension: int = dg.Field(
        default=768,
        description="Embedding dimension",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build artwork processing assets."""
        from sruth.aleyum.dagster_assets.dlt_assets import (
            artwork_processing_asset,
        )

        return dg.Definitions(assets=[artwork_processing_asset])


# ============================================================================
# COCODEOLAS COMPONENTS
# ============================================================================

@dataclass
class CodeAnalysisComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for code analysis and documentation.

    Creates assets for analyzing code repositories.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.CodeAnalysisComponent
        attributes:
          include_ast: true
          include_embeddings: true
    """

    include_ast: bool = dg.Field(
        default=True,
        description="Include AST extraction",
    )
    include_embeddings: bool = dg.Field(
        default=True,
        description="Include code embeddings",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build code analysis assets."""
        from sruth.códeolas.dagster_assets.code_assets import (
            code_ast_asset,
            code_documentation_asset,
        )

        assets = []

        if self.include_ast:
            assets.append(code_ast_asset)
        if self.include_embeddings:
            assets.append(code_documentation_asset)

        return dg.Definitions(assets=assets)


# ============================================================================
# TAUTH COMPONENTS
# ============================================================================

@dataclass
class CurriculumContentComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for curriculum content ingestion.

    Creates assets for mythology and cultural content.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.CurriculumContentComponent
        attributes:
          include_mythology: true
          include_curriculum: true
    """

    include_mythology: bool = dg.Field(
        default=True,
        description="Include Irish mythology content",
    )
    include_curriculum: bool = dg.Field(
        default=True,
        description="Include curriculum content",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build curriculum content assets."""
        from sruth.tuath.dagster_assets.mythology_assets import (
            mythology_content_asset,
        )
        from sruth.tuath.dagster_assets.curriculum_assets import (
            curriculum_content_asset,
        )

        assets = []

        if self.include_mythology:
            assets.append(mythology_content_asset)
        if self.include_curriculum:
            assets.append(curriculum_content_asset)

        return dg.Definitions(assets=assets)


# ============================================================================
# PIPELINE FACTORY COMPONENTS
# ============================================================================

@dataclass
class SruthPipelineComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Factory component for complete sruth pipelines.

    Combines DLT sources, transformations, and exports into a single
    configurable component.

    This component enables gradual migration by returning existing
    definitions from each sruth pipeline.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.SruthPipelineComponent
        attributes:
          pipeline: "oideachais"
          demo_mode: false
    """

    pipeline: str = dg.Field(
        default="oideachais",
        description="Pipeline name: oideachais, crypteolas, aleyum, códeolas, tuath",
    )
    demo_mode: bool = dg.Field(
        default=False,
        description="Enable demo mode with reduced data",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build complete sruth pipeline."""
        if self.pipeline == "oideachais":
            return self._build_oideachais_pipeline()
        elif self.pipeline == "crypteolas":
            return self._build_crypteolas_pipeline()
        elif self.pipeline == "aleyum":
            return self._build_aleyum_pipeline()
        elif self.pipeline == "códeolas":
            return self._build_cocodeolas_pipeline()
        elif self.pipeline == "tuath":
            return self._build_tuath_pipeline()
        else:
            return dg.Definitions()

    def _build_oideachais_pipeline(self) -> dg.Definitions:
        """Build oideachais (education) pipeline."""
        from sruth.oideachais.dagster_defs import defs

        # Return existing definitions for gradual migration
        return defs

    def _build_crypteolas_pipeline(self) -> dg.Definitions:
        """Build crypteolas (REST API) pipeline."""
        try:
            from sruth.crypteolas.dagster_assets import defs
            return defs
        except ImportError:
            return dg.Definitions()

    def _build_aleyum_pipeline(self) -> dg.Definitions:
        """Build aleyum (web scraping) pipeline."""
        try:
            from sruth.aleyum.dagster_assets import defs
            return defs
        except ImportError:
            return dg.Definitions()

    def _build_cocodeolas_pipeline(self) -> dg.Definitions:
        """Build códeolas (code analysis) pipeline."""
        try:
            from sruth.códeolas.dagster_assets import defs
            return defs
        except ImportError:
            return dg.Definitions()

    def _build_tuath_pipeline(self) -> dg.Definitions:
        """Build tuath (content) pipeline."""
        try:
            from sruth.tuath.dagster_assets import defs
            return defs
        except ImportError:
            return dg.Definitions()


@dataclass
class IcebergExportComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for Iceberg table export.

    Creates assets for exporting data to Iceberg via Lakekeeper.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.IcebergExportComponent
        attributes:
          catalog_uri: "http://lakekeeper:8181"
          warehouse: "s3://garage/warehouse"
          namespace: "oideachais"
    """

    catalog_uri: str = dg.Field(
        default="http://lakekeeper:8181",
        description="Lakekeeper catalog URI",
    )
    warehouse: str = dg.Field(
        default="s3://garage/warehouse",
        description="Iceberg warehouse location",
    )
    namespace: str = dg.Field(
        default="sruth",
        description="Iceberg namespace",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build Iceberg export assets."""
        from sruth.shared.dagster.components import IcebergIOComponent

        iceberg = IcebergIOComponent(
            catalog_uri=self.catalog_uri,
            warehouse=self.warehouse,
            namespace=self.namespace,
        )

        return iceberg.build_defs(context)


@dataclass
class LanceDBExportComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Component for LanceDB vector export.

    Creates assets for exporting embeddings to LanceDB.

    Example YAML:
        type: sruth.shared.dagster.components.sruth.LanceDBExportComponent
        attributes:
          uri: "s3://lance"
          namespace: "oideachais"
    """

    uri: str = dg.Field(
        default="s3://lance",
        description="LanceDB storage URI",
    )
    namespace: str = dg.Field(
        default="sruth",
        description="LanceDB namespace",
    )

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build LanceDB export assets."""
        from sruth.oideachais.dagster_defs.assets.embedding_assets import (
            lance_export_asset,
        )

        return dg.Definitions(assets=[lance_export_asset])


__all__ = [
    # Oideachais
    "CurriculumDLTComponent",
    "MultiNationCurriculumComponent",
    "PDFProcessingComponent",
    "EmbeddingComponent",
    # Crypteolas
    "GitHubIngestionComponent",
    "DeFiIngestionComponent",
    "CodeEmbeddingComponent",
    # Aleyum
    "MusicIngestionComponent",
    "ArtworkProcessingComponent",
    # Códeolas
    "CodeAnalysisComponent",
    # Tuath
    "CurriculumContentComponent",
    # Factory
    "SruthPipelineComponent",
    # Export
    "IcebergExportComponent",
    "LanceDBExportComponent",
]
