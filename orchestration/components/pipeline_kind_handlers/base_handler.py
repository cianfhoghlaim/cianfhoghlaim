"""Base class for pipeline-kind handlers.

Each handler implements `process_pipeline(dlt_source, ctx)` which returns
the list of Dagster `AssetsDefinition`s specialised for the source kind.

The handler is called by `PipelineFactoryComponent` after the factory
has introspected the dlt source via BOTH (a) decorator metadata and
(c) `pipeline.dataset()` schema introspection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

import dagster as dg


@dataclass
class PipelineContext:
    """The context passed to each pipeline-kind handler.

    Attributes:
        dlt_source: The dlt source object (already introspected)
        source_name: The dlt source's name (from @dlt.source decorator)
        primary_key: The primary key (from @dlt.resource)
        write_disposition: 'replace' | 'append' | 'merge' (from @dlt.resource)
        columns: Dict of column_name → {data_type, nullable, ...}
        row_count_estimate: Approx row count from pipeline.dataset()
        embedding_model: The embedding model name (e.g. BAAI/bge-large-en-v1.5)
        destinations: List of destination names
        pipeline_kind: The pipeline_kind string from the defs.yaml
    """
    dlt_source: Any
    source_name: str
    primary_key: Optional[str] = None
    write_disposition: str = "append"
    columns: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    row_count_estimate: Optional[int] = None
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    destinations: List[str] = field(default_factory=list)
    pipeline_kind: str = ""


class BasePipelineHandler(Protocol):
    """Protocol for pipeline-kind handlers.

    Each handler is instantiated by `PipelineFactoryComponent` and
    its `process_pipeline(ctx)` method is called to generate the
    asset graph for the source.
    """

    def __init__(self, ctx: PipelineContext) -> None:
        self.ctx = ctx

    def process_pipeline(self) -> List["dg.AssetsDefinition"]:
        """Generate the per-kind assets for this pipeline.

        Returns a list of Dagster AssetsDefinitions. The factory adds
        these to the standard 5-stage asset graph (dlt, BAML, cocoindex,
        marimo, asset_checks).
        """
        raise NotImplementedError

    @staticmethod
    def kind() -> str:
        """The pipeline_kind string this handler responds to."""
        raise NotImplementedError
