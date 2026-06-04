"""Shim for `sruth.shared.dagster.components.sruth_components` — see tuatha/crypteolas/STATUS.md.

Provides stub component classes for the Crypteolas Dagster pipeline. The
real implementations would read YAML and instantiate the underlying DLT /
CocoIndex / knowledge-graph resources. The stubs return empty Dagster
`Definitions` so the import succeeds and the YAML can be parsed for
documentation / dry-runs.
"""

from __future__ import annotations

from typing import Any

from dagster import Definitions


class _BaseStubComponent:
    """Common base for the crypteolas component stubs."""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def build_defs(self, context: Any = None) -> Definitions:
        return Definitions()


class GitHubIngestionComponent(_BaseStubComponent):
    """Stub for the GitHub ingestion component."""


class DeFiIngestionComponent(_BaseStubComponent):
    """Stub for the DeFi (DeFiLlama / CoinGecko / Binance) component."""


class CodeEmbeddingComponent(_BaseStubComponent):
    """Stub for the code-embedding (CodeBERT) component."""


class SruthPipelineComponent(_BaseStubComponent):
    """Stub for the umbrella Sruth pipeline component."""


__all__ = [
    "GitHubIngestionComponent",
    "DeFiIngestionComponent",
    "CodeEmbeddingComponent",
    "SruthPipelineComponent",
]
