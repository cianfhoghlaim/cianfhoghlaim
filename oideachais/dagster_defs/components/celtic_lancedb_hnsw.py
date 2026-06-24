"""
CelticLancedbHnswComponent — wrap a LanceDB HNSW index build.

Wraps a LanceDB table and registers a `dg.asset` that builds
an HNSW index on the `embedding` column. This is the
2026-06-Component that consumes the
`oideachais.lancedb.indexing.build_hnsw_index` helper.

Usage (from a YAML defs file):

    type: oideachais.dagster_defs.components.CelticLancedbHnswComponent
    attributes:
      table_name: leabharlann_books
      asset_name: leabharlann_books_hnsw_index
      group_name: leabharlann
      ef_construction: 100
      M: 16
"""
from __future__ import annotations

import dagster as dg


class CelticLancedbHnswComponent(dg.Component, dg.Model):
    """Build an HNSW index on a LanceDB table.

    Attributes:
        table_name: The LanceDB table name (e.g. "leabharlann_books").
        asset_name: The Dagster asset name. Default
                    ``{table_name}_hnsw_index``.
        group_name: The Dagster group_name. Default ``"lancedb_indexes"``.
        vector_column: The vector column name. Default ``"embedding"``.
        ef_construction: HNSW `ef_construction` parameter. Default 100.
        M: HNSW `M` parameter. Default 16.
    """

    table_name: str
    asset_name: str | None = None
    group_name: str | None = None
    vector_column: str = "embedding"
    ef_construction: int = 100
    M: int = 16

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        # Lazy import to avoid a hard lancedb dependency at module load.
        from oideachais.lancedb.indexing import LANCEDB_AVAILABLE, build_hnsw_index

        asset_name = self.asset_name or f"{self.table_name}_hnsw_index"
        group_name = self.group_name or "lancedb_indexes"

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="lancedb",
            description=f"Build HNSW index on {self.table_name}.{self.vector_column}",
        )
        def _hnsw_index_asset(asset_context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            if not LANCEDB_AVAILABLE:
                asset_context.log.warning("lancedb_not_available_skipping_hnsw_index")
                return dg.MaterializeResult(
                    metadata={"skipped": True, "reason": "lancedb_not_available"}
                )
            # The CocoIndex v1 app already builds the table; this
            # component just builds the HNSW index on top.
            import lancedb

            db = lancedb.connect("rest://lance-api.cianfhoghlaim.ie")
            table = db.open_table(self.table_name)
            build_hnsw_index(
                table,
                column=self.vector_column,
                ef_construction=self.ef_construction,
                M=self.M,
            )
            return dg.MaterializeResult(
                metadata={
                    "table_name": self.table_name,
                    "vector_column": self.vector_column,
                    "ef_construction": self.ef_construction,
                    "M": self.M,
                }
            )

        return dg.Definitions(assets=[_hnsw_index_asset])


__all__ = ["CelticLancedbHnswComponent"]
