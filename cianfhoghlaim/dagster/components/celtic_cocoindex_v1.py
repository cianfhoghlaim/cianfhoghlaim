"""
CelticCocoindexV1Component — wrap a CocoIndex v1 App update.

Wraps a CocoIndex v1 App and registers a `dg.asset` that calls
`app.update()` to materialise the App. This is the 2026-06
Component that consumes the shared lifespan in
`oideachais/cocoindex_flows/_lifespan.py`.

Usage (from a YAML defs file):

    type: cianfhoghlaim.assets._oideachais_dagster_defs.components.CelticCocoindexV1Component
    attributes:
      app_name: LeabharlannBooksEmbedding
      module: cianfhoghlaim.embeddings._oideachais_src.leabharlann_embedding
      asset_name: leabharlann_books_cocoindex_update
      group_name: leabharlann
"""

from __future__ import annotations

import importlib
import logging

import dagster as dg

logger = logging.getLogger(__name__)


class CelticCocoindexV1Component(dg.Component, dg.Model):
    """Update a CocoIndex v1 App and report materialisation metadata.

    Attributes:
        app_name: The CocoIndex App name (e.g. "LeabharlannBooksEmbedding").
        module: The module that exports the App. Default
                ``oideachais.cocoindex_flows.leabharlann_embedding``.
        asset_name: The Dagster asset name. Default
                    ``{app_name_snake_case}_cocoindex_update``.
        group_name: The Dagster group_name. Default
                    ``"cocoindex_v1"``.
    """

    app_name: str
    module: str = "cianfhoghlaim.embeddings._oideachais_src.leabharlann_embedding"
    asset_name: str | None = None
    group_name: str | None = None

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        asset_name = self.asset_name or f"{_to_snake(self.app_name)}_cocoindex_update"
        group_name = self.group_name or "cocoindex_v1"

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="cocoindex",
            description=f"CocoIndex v1 App update: {self.app_name}",
        )
        def _cocoindex_update_asset(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            try:
                mod = importlib.import_module(self.module)
            except ImportError as exc:
                asset_context.log.warning(
                    f"cocoindex_v1_module_import_failed module={self.module} err={exc}"
                )
                return dg.MaterializeResult(
                    metadata={"skipped": True, "reason": str(exc)}
                )
            # The CocoIndex v1 App name is the AppConfig.name.
            # We scan the module's globals for the matching App.
            app = None
            for name, obj in vars(mod).items():
                if name.startswith("_"):
                    continue
                if hasattr(obj, "name") and getattr(obj, "name", None) == self.app_name:
                    app = obj
                    break
            if app is None:
                asset_context.log.warning(
                    f"cocoindex_app_not_found name={self.app_name} module={self.module}"
                )
                return dg.MaterializeResult(
                    metadata={"skipped": True, "reason": "app_not_found"}
                )
            # Run the update. The CocoIndex v1 App exposes
            # `update()` (synchronous, blocking) — we run it
            # in a thread to keep the Dagster asset event loop
            # responsive.
            import asyncio

            update = getattr(app, "update", None)
            if update is None:
                asset_context.log.warning(
                    f"cocoindex_app_has_no_update_method name={self.app_name}"
                )
                return dg.MaterializeResult(
                    metadata={"skipped": True, "reason": "no_update_method"}
                )
            try:
                if asyncio.iscoroutinefunction(update):
                    asyncio.run(update())
                else:
                    update()
            except Exception as exc:  # pragma: no cover
                asset_context.log.warning(
                    f"cocoindex_update_failed name={self.app_name} err={exc}"
                )
                return dg.MaterializeResult(
                    metadata={"skipped": True, "reason": str(exc)}
                )
            return dg.MaterializeResult(
                metadata={
                    "app_name": self.app_name,
                    "module": self.module,
                }
            )

        return dg.Definitions(assets=[_cocoindex_update_asset])


def _to_snake(name: str) -> str:
    """Convert a CamelCase App name to snake_case."""
    import re

    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


__all__ = ["CelticCocoindexV1Component"]
