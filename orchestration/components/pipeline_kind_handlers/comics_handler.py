import dagster as dg
"""Comics handler — VLM via cognee for comics.

Pipeline: comics → VLM (cognee) → asset generation
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


class ComicsHandler:
    """Handler for comics (VLM via cognee)."""

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "comics"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "comics"

        @dg.asset(
            name=f"{source_name}_vlm_panel_extraction",
            group_name=f"comics_{source_name}",
            compute_kind="vlm",
            description=f"VLM panel extraction for {source_name} comics.",
        )
        def vlm_panels(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "vlm_panels"})

        @dg.asset(
            name=f"{source_name}_cognee_knowledge",
            group_name=f"comics_{source_name}",
            compute_kind="cognee",
            description=f"Cognee knowledge graph enrichment for {source_name}.",
        )
        def cognee_kg(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "cognee_kg"})

        return [vlm_panels, cognee_kg]
