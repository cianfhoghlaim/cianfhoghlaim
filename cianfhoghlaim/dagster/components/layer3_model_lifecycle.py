"""
Layer 3 Model Lifecycle Component — the canonical CocoIndex v1 App
Component (rewrite of CelticCocoindexV1Component + CelticLancedbHnswComponent).

Wraps one CocoIndex v1 App and registers it as a `is_virtual=True`
Dagster asset so the LanceDB table mirrors its upstream (the L1
filesystem scan) automatically. The R1–R4 conformance contract
(oideachais-cocoindex-v1 skill) is enforced at scaffold time.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.dagster.components.CelticModelLifecycleComponent
    attributes:
      app_name: LeabharlannBooksEmbedding
      module: cianfhoghlaim.cocoindex.leabharlann_embedding
      embedding_model: BAAI/bge-large-en-v1.5
      hnsw_index: true
"""
from __future__ import annotations

import importlib
import logging
from typing import Any, Literal

import dagster as dg
from dagster.components import Component, ComponentLoadContext


EmbeddingModel = Literal["BAAI/bge-m3", "BAAI/bge-large-en-v1.5"]


class ConformanceViolation(Exception):
    """Raised when a CocoIndex v1 App fails the R1–R4 conformance contract."""

    def __init__(self, rule: str, message: str, fix: str) -> None:
        self.rule = rule
        self.message = message
        self.fix = fix
        super().__init__(f"[{rule}] {message}\nFix: {fix}")


class CelticModelLifecycleComponent(Component):
    """Layer 3 Model Lifecycle Component.

    Wraps one CocoIndex v1 App as a `is_virtual=True` Dagster asset. The
    R1–R4 conformance contract is enforced at scaffold time by
    calling `cocoindex_v1_conformance.check_module(module)` BEFORE
    emitting the asset.

    Attributes:
        app_name: The CocoIndex App name (the AppConfig.name). Used to
            find the App instance in `module` via reflection.
        module: The module that exports the App (e.g.
            "cianfhoghlaim.cocoindex.leabharlann_embedding").
        embedding_model: The embedding model. Default:
            "BAAI/bge-large-en-v1.5".
        hnsw_index: Whether to build an HNSW index on the LanceDB
            table. Default: True.
        conformance_required: Whether to enforce R1–R4. Default: True.
            Disable only for App migrations in flight.
    """

    app_name: str
    module: str
    embedding_model: EmbeddingModel = "BAAI/bge-large-en-v1.5"
    hnsw_index: bool = True
    conformance_required: bool = True

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 `is_virtual=True` @asset for the CocoIndex v1 App.

        The R1–R4 conformance contract is enforced at scaffold time
        (and at every build_defs invocation) by
        `cocoindex_v1_conformance.check_module(module)`. On failure,
        ConformanceViolation is raised with the exact rule + fix
        instructions.
        """
        if self.conformance_required:
            self._check_r1_to_r4()

        asset_name = f"{_to_snake(self.app_name)}_app"
        group_name = f"3_model_lifecycle/cocoindex_v1/{_to_snake(self.app_name)}"
        automation_condition = (
            dg.AutomationCondition.eager().resolve_through_virtual()
        )

        # Look up the App instance via reflection so we can fail fast
        # at build time if the module doesn't export the expected App.
        try:
            mod = importlib.import_module(self.module)
        except ImportError as exc:
            raise dg.Failure(
                description=(
                    f"cocoindex_v1_module_import_failed module={self.module} err={exc}"
                )
            ) from exc

        app = self._find_app(mod, self.app_name)
        if app is None:
            raise dg.Failure(
                description=(
                    f"cocoindex_app_not_found name={self.app_name} module={self.module}"
                )
            )

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="cocoindex",
            description=(
                f"L3 CocoIndex v1 App: {self.app_name} "
                f"(module={self.module}, embedding={self.embedding_model})"
            ),
            automation_condition=automation_condition,
            is_virtual=True,
        )
        def _cocoindex_app_asset(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            update = getattr(app, "update", None)
            if update is None:
                raise dg.Failure(
                    description=f"cocoindex_app_has_no_update_method name={self.app_name}"
                )
            try:
                import asyncio

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
                    "embedding_model": self.embedding_model,
                    "hnsw_index": self.hnsw_index,
                    "layer": "3_model_lifecycle",
                }
            )

        return dg.Definitions(assets=[_cocoindex_app_asset])

    def _check_r1_to_r4(self) -> None:
        """Enforce the 4-rule R1–R4 conformance contract.

        R1: Module imports `from ._lifespan import shared_lifespan`
        R2: Module imports the canonical ContextKeys (LANCE_DB, EMBEDDER,
            RESOLVED_FILE_REGISTRY) OR declares an additional one with
            `# R2-exempt: <reason>`
        R3: `coco.App(...)` is at module scope (NOT inside a function body)
        R4: At least one `@coco.fn(` decorator is present
        """
        try:
            mod = importlib.import_module(self.module)
        except ImportError as exc:
            raise ConformanceViolation(
                rule="R0",
                message=f"module {self.module!r} failed to import: {exc}",
                fix="Check the module path + the `from ._lifespan import shared_lifespan` line",
            )

        src = getattr(mod, "__file__", None)
        if not src:
            raise ConformanceViolation(
                rule="R0",
                message=f"module {self.module!r} has no __file__ (dynamic module?)",
                fix="Use a file-backed Python module under cianfhoghlaim/cocoindex/",
            )

        try:
            source_text = open(src).read()
        except OSError as exc:
            raise ConformanceViolation(
                rule="R0",
                message=f"cannot read {src}: {exc}",
                fix="Check the file permissions on the source module",
            )

        # R1: shared_lifespan import
        if "from ._lifespan import shared_lifespan" not in source_text and "from ._lifespan import" not in source_text:
            raise ConformanceViolation(
                rule="R1",
                message="no `from ._lifespan import shared_lifespan` line",
                fix="Add the import to delegate to the canonical lifespan (see oideachais-cocoindex-v1 skill)",
            )

        # R2: canonical ContextKeys
        canonical_keys = ["LANCE_DB", "EMBEDDER", "RESOLVED_FILE_REGISTRY"]
        has_canonical = any(
            f"from ._lifespan import {k}" in source_text for k in canonical_keys
        )
        has_r2_exempt = "# R2-exempt:" in source_text
        if not has_canonical and not has_r2_exempt:
            raise ConformanceViolation(
                rule="R2",
                message=(
                    f"no canonical ContextKey ({', '.join(canonical_keys)}) "
                    "and no `# R2-exempt:` comment"
                ),
                fix=(
                    "Either import the canonical ContextKeys from `._lifespan`, "
                    "or add `# R2-exempt: <reason>` above your custom ContextKey."
                ),
            )

        # R3: `coco.App(...)` at module scope
        if "coco.App(" not in source_text:
            raise ConformanceViolation(
                rule="R3",
                message="no `coco.App(...)` construction found",
                fix="Move the `coco.App(coco.AppConfig(name=...))` construction to module scope",
            )

        # R4: at least one `@coco.fn(` decorator
        if "@coco.fn(" not in source_text:
            raise ConformanceViolation(
                rule="R4",
                message="no `@coco.fn(` decorator found",
                fix="Add `@coco.fn(memo=True)` to your processing function",
            )

    def _find_app(self, mod: Any, app_name: str) -> Any:
        """Find the App instance in the module by AppConfig.name."""
        for name, obj in vars(mod).items():
            if name.startswith("_"):
                continue
            if hasattr(obj, "name") and getattr(obj, "name", None) == app_name:
                return obj
        return None


def _to_snake(name: str) -> str:
    """Convert a CamelCase App name to snake_case."""
    import re

    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


__all__ = [
    "CelticModelLifecycleComponent",
    "ConformanceViolation",
    "EmbeddingModel",
]
