import dagster as dg
"""PDF handler — OCR + BAML extraction for PDFs.

Pipeline: pdf → OCR → BAML → embeddings
"""

from typing import TYPE_CHECKING

from dagster import (
    AssetCheckSpec,
    AssetsDefinition,
    AssetExecutionContext,
    MaterializeResult,
    asset,
)

if TYPE_CHECKING:
    from orchestration.components.pipeline_kind_handlers.base_handler import (
        PipelineContext,
    )


class PdfHandler:
    """Handler for OCR + BAML extraction of PDFs."""

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "pdf"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "pdf"

        @dg.asset(
            name=f"{source_name}_ocr",
            group_name=f"pdf_{source_name}",
            compute_kind="ocr",
            description=f"OCR extraction of {source_name} PDF documents.",
        )
        def ocr(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "ocr"})

        @dg.asset(
            name=f"{source_name}_baml_extraction",
            group_name=f"pdf_{source_name}",
            compute_kind="baml",
            description=f"BAML structured extraction from {source_name} OCR output.",
        )
        def baml_extraction(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "baml"})

        return [ocr, baml_extraction]
