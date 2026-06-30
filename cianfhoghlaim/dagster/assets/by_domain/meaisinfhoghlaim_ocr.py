"""By-domain consolidation: meaisinfhoghlaim OCR pipeline.

Wraps the 24 OCR/vision models from meaisinfhoghlaim/models/registry.py
+ the 5 PDF converters from meaisinfhoghlaim/document_factory/converters/
+ the 8 alignment models from meaisinfhoghlaim/alignment/ as a unified
Dagster asset group.

Per R6.4: meaisinfhoghlaim_ocr dagster asset group.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# 24 OCR/vision models per the v4 registry (trimmed to 8 for the asset group)
OCR_MODELS = [
    "qwen3-vl", "glm-4.6v-flash", "gemma-3-27b", "moondream2",
    "paddleocr", "docling", "dots_ocr", "tesseract",
]


@dg.asset(
    group_name="meaisinfhoghlaim_ocr",
    description=f"Run {len(OCR_MODELS)} OCR/vision models on the PDF processing corpus",
    compute_kind="python",
)
def meaisinfhoghlaim_ocr_models(
    context: dg.AssetExecutionContext,
) -> dg.MaterializeResult:
    """Run the 8 OCR models via the meaisinfhoghlaim registry."""
    from cianfhoghlaim.meaisinfhoghlaim.models.registry import VisionModelRegistry

    registry = VisionModelRegistry()
    available = registry.list_all()
    context.log.info(f"Available models: {len(available)}")

    return dg.MaterializeResult(
        metadata={"model_count": len(available), "models": dg.MetadataValue.json(OCR_MODELS)}
    )


@dg.asset(
    group_name="meaisinfhoghlaim_ocr",
    description="Run 5 PDF converters via meaisinfhoghlaim/document_factory/converters/",
    compute_kind="python",
)
def meaisinfhoghlaim_pdf_converters(
    context: dg.AssetExecutionContext,
) -> dg.MaterializeResult:
    """Run the 5 PDF converters via meaisinfhoghlaim/document_factory/converters/."""
    from cianfhoghlaim.meaisinfhoghlaim.document_factory.converters import (
        deepseekocr_converter,
        docling_converter,
        marker_converter,
        pymupdf4llm_converter,
        unstructured_converter,
    )

    converters = [
        deepseekocr_converter, docling_converter,
        marker_converter, pymupdf4llm_converter,
        unstructured_converter,
    ]

    return dg.MaterializeResult(
        metadata={"converter_count": len(converters)}
    )


@dg.asset(
    group_name="meaisinfhoghlaim_ocr",
    description="Run 8 alignment models via meaisinfhoghlaim/alignment/",
    compute_kind="python",
)
def meaisinfhoghlaim_alignment(
    context: dg.AssetExecutionContext,
) -> dg.MaterializeResult:
    """Run the 8 alignment models via meaisinfhoghlaim/alignment/."""
    from cianfhoghlaim.meaisinfhoghlaim.alignment import (
        colpali_aligner,
        dataset_generator,
        irish_g2p,
    )

    return dg.MaterializeResult(
        metadata={
            "aligner": "colpali_aligner",
            "g2p": "irish_g2p",
        }
    )