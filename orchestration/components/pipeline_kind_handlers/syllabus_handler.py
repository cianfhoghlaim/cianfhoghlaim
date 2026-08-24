import dagster as dg
"""Syllabus handler — NCCA / SEC / CCEA / SQA / WJEC syllabuses.

Pipeline: chemistry_syllabus → experiments → artifacts

Generates 3 assets per syllabus:
1. syllabus_assets — parses the syllabus PDF/XML into structured topics
2. experiments_assets — generates experiment templates per topic
3. artifacts_assets — produces teaching artifacts (rubrics, worksheets)
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


class SyllabusHandler:
    """Handler for NCCA / SEC / CCEA / SQA / WJEC syllabuses.

    Implements the chemistry_syllabus → experiments → artifacts pipeline.
    """

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "syllabus"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "syllabus"

        @dg.asset(
            name=f"{source_name}_syllabus_topics",
            group_name=f"syllabus_{source_name}",
            compute_kind="python",
            description=f"Parse the {source_name} syllabus PDF/XML into structured topics.",
        )
        def syllabus_topics(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "syllabus"})

        @dg.asset(
            name=f"{source_name}_experiments",
            group_name=f"syllabus_{source_name}",
            compute_kind="python",
            description=f"Generate experiment templates per topic for {source_name}.",
        )
        def experiments(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "experiments"})

        @dg.asset(
            name=f"{source_name}_artifacts",
            group_name=f"syllabus_{source_name}",
            compute_kind="python",
            description=f"Produce teaching artifacts (rubrics, worksheets) for {source_name}.",
        )
        def artifacts(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "artifacts"})

        return [syllabus_topics, experiments, artifacts]
