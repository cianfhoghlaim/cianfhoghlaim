import dagster as dg
"""Crypto handler — chain indexer for crypteolas sources.

Pipeline: crypteolas → chain indexer → defi analytics
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


class CryptoHandler:
    """Handler for chain indexer (crypteolas_chain / crypteolas_defi)."""

    def __init__(self, ctx: "PipelineContext") -> None:
        self.ctx = ctx

    @staticmethod
    def kind() -> str:
        return "crypto"

    def process_pipeline(self) -> list[AssetsDefinition]:
        source_name = self.ctx.source_name or "crypto"

        @dg.asset(
            name=f"{source_name}_chain_index",
            group_name=f"crypto_{source_name}",
            compute_kind="chain",
            description=f"Chain indexer for {source_name} (block fetcher, transaction decoder).",
        )
        def chain_index(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "chain_index"})

        @dg.asset(
            name=f"{source_name}_defi_analytics",
            group_name=f"crypto_{source_name}",
            compute_kind="defi",
            description=f"DeFi analytics (liquidity, swaps, yield) for {source_name}.",
        )
        def defi_analytics(context) -> dg.MaterializeResult:
            return dg.MaterializeResult(metadata={"source": source_name, "kind": "defi_analytics"})

        return [chain_index, defi_analytics]
