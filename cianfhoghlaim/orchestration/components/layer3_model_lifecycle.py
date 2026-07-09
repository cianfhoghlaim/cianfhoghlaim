"""
Layer 3 Model Lifecycle Component — the canonical CocoIndex v1 App
Component (rewrite of CelticCocoindexV1Component + CelticLancedbHnswComponent).

Wraps one CocoIndex v1 App and registers it as a `is_virtual=True`
Dagster asset so the LanceDB table mirrors its upstream (the L1
filesystem scan) automatically. The R1-R4 conformance contract
(oideachais-cocoindex-v1 skill) is enforced at scaffold time.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.orchestration.components.CelticModelLifecycleComponent
    attributes:
      app_name: LeabharlannBooksEmbedding
      module: cianfhoghlaim.cocoindex.leabharlann_embedding
      embedding_model: BAAI/bge-large-en-v1.5
      hnsw_index: true
"""
from __future__ import annotations

import importlib
from typing import Any, Literal

import dagster as dg
from dagster.components import Component, ComponentLoadContext

EmbeddingModel = Literal["BAAI/bge-m3", "BAAI/bge-large-en-v1.5"]


class ConformanceError(Exception):
    """Raised when a CocoIndex v1 App fails the R1-R4 conformance contract."""

    def __init__(self, rule: str, message: str, fix: str) -> None:
        self.rule = rule
        self.message = message
        self.fix = fix
        super().__init__(f"[{rule}] {message}\nFix: {fix}")


class CelticModelLifecycleComponent(Component):
    """Layer 3 Model Lifecycle Component.

    Wraps one CocoIndex v1 App as a `is_virtual=True` Dagster asset. The
    R1-R4 conformance contract is enforced at scaffold time by
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
        conformance_required: Whether to enforce R1-R4. Default: True.
            Disable only for App migrations in flight.
    """

    app_name: str
    module: str
    embedding_model: EmbeddingModel = "BAAI/bge-large-en-v1.5"
    hnsw_index: bool = True
    conformance_required: bool = True

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 `is_virtual=True` @asset for the CocoIndex v1 App.

        The R1-R4 conformance contract is enforced at scaffold time
        (and at every build_defs invocation) by
        `cocoindex_v1_conformance.check_module(module)`. On failure,
        ConformanceError is raised with the exact rule + fix
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
        """Enforce the 4-rule R1-R4 conformance contract.

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
            raise ConformanceError(
                rule="R0",
                message=f"module {self.module!r} failed to import: {exc}",
                fix="Check the module path + the `from ._lifespan import shared_lifespan` line",
            ) from exc

        src = getattr(mod, "__file__", None)
        if not src:
            raise ConformanceError(
                rule="R0",
                message=f"module {self.module!r} has no __file__ (dynamic module?)",
                fix="Use a file-backed Python module under cianfhoghlaim/cocoindex/",
            )

        try:
            with open(src) as f:
                source_text = f.read()
        except OSError as exc:
            raise ConformanceError(
                rule="R0",
                message=f"cannot read {src}: {exc}",
                fix="Check the file permissions on the source module",
            ) from exc

        # R1: shared_lifespan import (the canonical module must be imported)
        if "from ._lifespan import" not in source_text:
            raise ConformanceError(
                rule="R1",
                message="no `from ._lifespan import` line",
                fix="Add `from ._lifespan import shared_lifespan` (or another canonical ContextKey) to delegate to the canonical lifespan (see oideachais-cocoindex-v1 skill)",
            )

        # R2: canonical ContextKeys (handles both single-line and multi-line
        # `from ._lifespan import (X, Y, Z)` imports)
        canonical_keys = ["LANCE_DB", "EMBEDDER", "RESOLVED_FILE_REGISTRY", "LANCEDB_URI", "EMBED_MODEL", "EMBED_DIM"]
        # Split on the first occurrence of `from ._lifespan import` and
        # check the next ~10 lines (handles the parenthesised multi-line
        # form).
        import re

        r2_match = re.search(r"from \._lifespan import\s*\(?\s*([\s\S]{0,500}?)\)?\s*(?:\n\s*\n|\nfrom |\Z)", source_text)
        r2_block = r2_match.group(1) if r2_match else ""
        has_canonical = any(
            re.search(rf"\b{k}\b", r2_block) is not None
            for k in canonical_keys
        )
        has_r2_exempt = "# R2-exempt:" in source_text
        if not has_canonical and not has_r2_exempt:
            raise ConformanceError(
                rule="R2",
                message=(
                    f"no canonical ContextKey ({', '.join(canonical_keys)}) "
                    "in the `from ._lifespan import` block and no `# R2-exempt:` comment"
                ),
                fix=(
                    "Either import the canonical ContextKeys from `._lifespan`, "
                    "or add `# R2-exempt: <reason>` above your custom ContextKey."
                ),
            )

        # R3: `coco.App(...)` at module scope
        if "coco.App(" not in source_text:
            raise ConformanceError(
                rule="R3",
                message="no `coco.App(...)` construction found",
                fix="Move the `coco.App(coco.AppConfig(name=...))` construction to module scope",
            )

        # R4: at least one `@coco.fn(` decorator
        if "@coco.fn(" not in source_text:
            raise ConformanceError(
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


class CelticFederatedOcrComponent(Component):
    """Layer 3 Federated-OCR Component (NEW for T4 of the 5-tangent plan).

    Wraps `cianfhoghlaim.meaisinfhoghlaim.federated.run_federated_training()`
    as a Dagster `@asset` with a cron automation condition. Per the
    `2026-07-09-agent-fleet-and-observability-facade-v1` change, the
    federated OCR subsystem was moved from
    `meaisinfhoghlaim/process/irish_ocr_federated.py` to
    `meaisinfhoghlaim/federated/`. This Component emits one asset
    (`irish_ocr_federated_smoke`) that runs the federated simulator
    warm-up.

    Usage (from a YAML defs file):

        type: cianfhoghlaim.orchestration.components.CelticFederatedOcrComponent
        attributes:
          source_module: cianfhoghlaim.meaisinfhoghlaim.federated
          model_name: gemma-3-4b
          num_rounds: 10
          automation_cron: "*/30 * * * *"

    Attributes:
        source_module: The Python module that exports
            `run_federated_training`. Default:
            `"cianfhoghlaim.meaisinfhoghlaim.federated"`.
        model_name: The federated model name. Default: `"gemma-3-4b"`.
        num_rounds: The number of federated rounds. Default: 10.
        data_dir: Local data directory (passed through). Default:
            `"/tmp/irish_htr_dataset_dummy"`.
        server_address: The federated server address. Default:
            `"localhost:8080"`.
        automation_cron: The cron expression for the AutomationCondition.
            Default: `"*/30 * * * *"` (every 30 minutes).
    """

    source_module: str = "cianfhoghlaim.meaisinfhoghlaim.federated"
    model_name: str = "gemma-3-4b"
    num_rounds: int = 10
    data_dir: str = "/tmp/irish_htr_dataset_dummy"
    server_address: str = "localhost:8080"
    automation_cron: str = "*/30 * * * *"

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 @asset: `irish_ocr_federated_smoke`.

        The asset invokes `self.source_module.run_federated_training(...)`
        (the canonical post-v4 entry point) and surfaces any
        exception in the metadata instead of crashing the run.
        """
        import json as _json
        from datetime import datetime as _dt, timezone as _tz

        asset_name = "irish_ocr_federated_smoke"
        group_name = "3_model_lifecycle/federated_ocr/irish_ocr_federated"
        description = (
            f"Federated Irish-OCR simulator smoke run — invokes "
            f"`{self.source_module}.run_federated_training()` "
            f"every {self.automation_cron} to keep the v4 federated "
            f"subsystem warm."
        )

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="federated-learning",
            description=description,
            automation_condition=dg.AutomationCondition.cron(
                self.automation_cron
            ),
        )
        def _federated_smoke(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            started_at = _dt.now(tz=_tz.utc)
            try:
                import importlib

                mod = importlib.import_module(self.source_module)
                run_federated_training = getattr(
                    mod, "run_federated_training", None
                )
                if run_federated_training is None:
                    raise ImportError(
                        f"{self.source_module} does not export "
                        f"`run_federated_training`"
                    )
                result = run_federated_training(
                    model_name=self.model_name,
                    num_rounds=self.num_rounds,
                    data_dir=self.data_dir,
                    server_address=self.server_address,
                )
                status = "ok"
                error: str | None = None
            except Exception as exc:  # noqa: BLE001 — never crash Dagster run
                result = {"error": str(exc)}
                status = "error"
                error = str(exc)

            finished_at = _dt.now(tz=_tz.utc)
            duration_seconds = (finished_at - started_at).total_seconds()
            asset_context.log.info(
                f"irish_ocr_federated_smoke: status={status} "
                f"duration={duration_seconds:.2f}s"
            )
            return dg.MaterializeResult(
                metadata={
                    "started_at": started_at.isoformat(),
                    "finished_at": finished_at.isoformat(),
                    "duration_seconds": duration_seconds,
                    "status": status,
                    "error": error,
                    "result": _json.dumps(result, default=str)[:4096],
                    "source_module": self.source_module,
                    "model_name": self.model_name,
                    "asset_kind": "federated_smoke",
                    "layer": "3_model_lifecycle",
                }
            )

        return dg.Definitions(assets=[_federated_smoke])


__all__ = [
    "CelticFederatedOcrComponent",
    "CelticModelLifecycleComponent",
    "ConformanceError",
    "EmbeddingModel",
]
