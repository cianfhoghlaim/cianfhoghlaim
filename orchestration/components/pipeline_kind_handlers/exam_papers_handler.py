import dagster as dg
"""Exam papers handler — UoG exam papers + Leaving Cert + GCSE.

Pipeline: exam_papers → VLM extraction → BAML structured fields → embeddings

Generates 2 assets per exam-papers source:
1. exam_papers_extracted — VLM extraction of the PDF exam paper
2. exam_papers_structured — BAML-extracted structured fields
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


class ExamPapersHandler:
    """Handler for UoG exam papers + Leaving Cert + GCSE (VLM extraction)."""

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "exam_papers"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "exam_papers"

        @dg.asset(
            name=f"{source_name}_vlm_extraction",
            group_name=f"exam_papers_{source_name}",
            compute_kind="vlm",
            description=f"VLM extraction of the {source_name} PDF exam paper.",
        )
        def vlm_extraction(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "vlm"})

        @dg.asset(
            name=f"{source_name}_baml_structured",
            group_name=f"exam_papers_{source_name}",
            compute_kind="baml",
            description=f"BAML extraction of structured fields from {source_name} exam paper.",
        )
        def baml_structured(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "baml"})

        return [vlm_extraction, baml_structured]
