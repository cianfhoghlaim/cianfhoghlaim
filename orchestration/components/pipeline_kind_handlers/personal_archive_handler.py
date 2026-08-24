import dagster as dg
"""Personal archive handler — notes + assignments + transcripts.

Pipeline: personal_archive → content extraction → embeddings
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


class PersonalArchiveHandler:
    """Handler for personal notes + assignments + transcripts."""

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "personal_archive"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "personal_archive"

        @dg.asset(
            name=f"{source_name}_content_extraction",
            group_name=f"personal_archive_{source_name}",
            compute_kind="python",
            description=f"Content extraction from {source_name} (PDFs, notes, transcripts).",
        )
        def content_extraction(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "extraction"})

        @dg.asset(
            name=f"{source_name}_figures",
            group_name=f"personal_archive_{source_name}",
            compute_kind="python",
            description=f"Figure extraction (diagrams, charts) from {source_name}.",
        )
        def figures(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "figures"})

        return [content_extraction, figures]
