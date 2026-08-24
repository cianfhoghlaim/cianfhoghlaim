import dagster as dg
"""Media handler — codec probe + thumbnail + embeddings.

Pipeline: media → codec probe → thumbnail → embeddings
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


class MediaHandler:
    """Handler for media (audio + video + image) assets."""

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "media"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "media"

        @dg.asset(
            name=f"{source_name}_codec_probe",
            group_name=f"media_{source_name}",
            compute_kind="codec",
            description=f"Codec probe for {source_name} media (audio/video/image).",
        )
        def codec_probe(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "codec_probe"})

        @dg.asset(
            name=f"{source_name}_thumbnail",
            group_name=f"media_{source_name}",
            compute_kind="image",
            description=f"Thumbnail generation for {source_name} media.",
        )
        def thumbnail(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "thumbnail"})

        @dg.asset(
            name=f"{source_name}_embeddings",
            group_name=f"media_{source_name}",
            compute_kind="embedding",
            description=f"Embedding generation for {source_name} media (CLIP / audio / video).",
        )
        def embeddings(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "embeddings"})

        return [codec_probe, thumbnail, embeddings]
