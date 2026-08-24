import dagster as dg
"""Official docs handler — university module pages + student union.

Pipeline: official_docs → HTML scraping → schema inference → UI auto-gen
"""

from typing import TYPE_CHECKING

from dagster import (
    AssetsDefinition,
    AssetExecutionContext,
    MaterializeResult,
    asset,
)

if TYPE_CHECKING:
    from orchestration.components.pipeline_kind_handlers.base_handler import (
        PipelineContext,
    )


class OfficialDocsHandler:
    """Handler for university module pages + student union official sites."""

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "official_docs"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "official_docs"

        @dg.asset(
            name=f"{source_name}_scraped",
            group_name=f"official_docs_{source_name}",
            compute_kind="scrape",
            description=f"HTML scraping of {source_name} official pages.",
        )
        def scraped(context: AssetExecutionContext) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "scraped"})

        @dg.asset(
            name=f"{source_name}_schema",
            group_name=f"official_docs_{source_name}",
            compute_kind="schema",
            description=f"Schema inference from {source_name} pages (for AG-UI auto-generation).",
        )
        def schema(context: AssetExecutionContext) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "schema"})

        return [scraped, schema]
