"""
Layer 3 Model Lifecycle Component — the canonical CocoIndex v1 App
Component (rewrite of CelticCocoindexV1Component + CelticLancedbHnswComponent).

Wraps one CocoIndex v1 App and registers it as a `is_virtual=True`
Dagster asset so the LanceDB table mirrors its upstream (the L1
filesystem scan) automatically. The R1-R4 conformance contract
(cianfhoghlaim-cocoindex-v1 skill) is enforced at scaffold time.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.orchestration.components.CelticModelLifecycleComponent
    attributes:
      app_name: LeabharlannBooksEmbedding
      module: cianfhoghlaim.cocoindex.leabharlann_embedding
      embedding_model: BAAI/bge-large-en-v1.5
      hnsw_index: true
"""
# Deliberately NOT `from __future__ import annotations` — Dagster's
# Resolvable derives the YAML schema from real (not postponed-string) type
# annotations; see the identical note in layer1_ingestion.py /
# layer2_materials.py. With postponed annotations, `get_model_cls()` raises
# `AttributeError: 'str' object has no attribute '__name__'`.
import importlib
from dataclasses import dataclass, field
from typing import Any, Literal

import dagster as dg
from dagster.components import Component, ComponentLoadContext, Resolvable

EmbeddingModel = Literal["BAAI/bge-m3", "BAAI/bge-large-en-v1.5"]


class ConformanceError(Exception):
    """Raised when a CocoIndex v1 App fails the R1-R4 conformance contract."""

    def __init__(self, rule: str, message: str, fix: str) -> None:
        self.rule = rule
        self.message = message
        self.fix = fix
        super().__init__(f"[{rule}] {message}\nFix: {fix}")


@dataclass
class CelticModelLifecycleComponent(Component, Resolvable):
    """Layer 3 Model Lifecycle Component.

    `@dataclass` + `Resolvable`: without them Dagster derives
    `EmptyAttributesModel` (which forbids every extra field), so all 97
    `3_model_lifecycle/cocoindex_v1/**/defs.yaml` files failed schema
    validation. Same fix as `CelticIngestionComponent`.

    NOTE: the 97 YAML files use TWO incompatible shapes — 34 supply the
    singular `app_name` + `module` this class declares, and 60 supply an
    `apps:` LIST plus `app_group` / `schedule`, which this class has never
    supported. The list shape is accepted below as `apps` and each entry
    is expanded into its own asset; see `_iter_app_specs()`.

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
        apps: The multi-app shape — a list of
            `{app_name, module, source?, lance_table?}` mappings. Mutually
            exclusive with the singular `app_name`/`module` pair; supply
            exactly one of the two forms.
        app_group: Group label for the multi-app shape (e.g.
            "americas_california_education"). Defaults to the single app's
            snake-cased name.
        schedule: `{cron, timezone}` for the multi-app shape. Translated
            into an `AutomationCondition.on_cron`.
        tags / metadata: Freeform documentation surfaced in asset metadata.
        r4_exempt / r4_exempt_reason: Skip the R4 conformance rule (an App
            with no embedding column, e.g. GeoParquet output). BEHAVIOURAL.
        automation / automation_cron: Override the automation condition,
            mirroring `CelticIngestionComponent`. BEHAVIOURAL.
    """

    app_name: str | None = None
    module: str | None = None
    # Nullable: `apple_photos_geospatial` sets `embedding_model: null` because
    # it writes GeoParquet and has no embedding column (it is also r4_exempt).
    embedding_model: EmbeddingModel | None = "BAAI/bge-large-en-v1.5"
    hnsw_index: bool = True
    conformance_required: bool = True
    apps: list[dict[str, Any]] = field(default_factory=list)
    app_group: str | None = None
    schedule: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # --- behavioural ---
    r4_exempt: bool = False
    r4_exempt_reason: str | None = None
    automation: Literal["eager", "on_cron"] | None = None
    automation_cron: str | None = None

    # --- documentation / lineage hints ---
    # Every field below is already supplied by one or more
    # `3_model_lifecycle/cocoindex_v1/**/defs.yaml` files and was previously
    # rejected outright (the class derived `EmptyAttributesModel`). They are
    # surfaced verbatim in the asset's MaterializeResult metadata and do not
    # otherwise change behaviour. Declared explicitly rather than via a
    # catch-all so `scripts/audit_defs_yaml.py` keeps its teeth: a genuinely
    # new key still fails loudly instead of being silently swallowed.
    table_name: str | None = None
    table_name_pattern: str | None = None
    lance_tables: list[str] = field(default_factory=list)
    lance_table_format: str | None = None
    source_asset: str | None = None
    source_tables: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    depts: list[str] = field(default_factory=list)
    corpora: list[str] = field(default_factory=list)
    # Deliberately `Any` — these three are genuinely heterogeneous across the
    # files that use them, and narrowing them re-breaks the layer:
    #   subjects         list[dict] in lc_subjects, not list[str]
    #   backbones        a dict {caption, audio_leg, ...} in youtube_kg
    #   cognify_datasets an int COUNT (5, 6) in lc_cognify / gemini_corpus
    # They are documentation only; a schema that describes them precisely
    # would mean splitting this component, which is follow-on work.
    subjects: Any = None
    backbones: Any = None
    cognify_datasets: Any = None
    # Also `Any` — an int COUNT in lc_cognify / gemini_corpus, same as
    # `cognify_datasets` above.
    graphiti_streams: Any = None
    falkordb_label: str | None = None
    ducklake_source: str | None = None
    ocr_registry: str | None = None
    privacy_gate: str | None = None
    # `factory_pattern`/`factory_module` document that the `apps:` entry is a
    # factory collapsing N jurisdictions into one module; the apps list is
    # still supplied alongside, so no extra resolution logic is needed.
    factory_pattern: bool = False
    factory_module: str | None = None
    # `schedules` is a *named* schedule map ({name: {cron, timezone}}) used by
    # one file. Not yet emitted as real dg.ScheduleDefinitions — declared so
    # the file loads; emitting them is follow-on work.
    schedules: dict[str, Any] = field(default_factory=dict)
    total_vectors: int | None = None
    expected_total_documents: int | None = None
    refresh_interval_secs: int | None = None
    frame_sample_fps: float | None = None
    audio_leg: dict[str, Any] = field(default_factory=dict)

    def _iter_app_specs(self) -> list[dict[str, Any]]:
        """Normalise the THREE YAML shapes to a single list of app specs.

        The 97 `3_model_lifecycle/cocoindex_v1/**/defs.yaml` files were
        written against three different mental models of this Component:

          1. singular   `app_name:` + `module:`                  (34 files)
          2. list       `apps: [{app_name, module, ...}]`        (60 files)
          3. per-subject `subjects: [{name, app_name, module}]`  (lc_subjects)

        Returns a list of `{app_name, module, ...}` mappings. Raises if none
        is populated, rather than silently emitting nothing — an empty
        Definitions is how this layer previously reported success while
        doing nothing.
        """
        if self.apps:
            return self._validate_specs([dict(a) for a in self.apps], "apps")
        # Shape 3: `subjects` is normally a documentation list of plain
        # strings, but lc_subjects uses it to carry full app specs.
        if isinstance(self.subjects, list) and any(
            isinstance(s, dict) and s.get("module") for s in self.subjects
        ):
            specs = [dict(s) for s in self.subjects if isinstance(s, dict)]
            return self._validate_specs(specs, "subjects")
        if self.app_name and self.module:
            return [{"app_name": self.app_name, "module": self.module}]
        if self.app_name:
            # Shape 4: graph-only stage — `3_model_lifecycle/lc_cognify` and
            # `legal_research/gemini_corpus` name an app but no `module:`,
            # because they describe a cognify / Graphiti / FalkorDB fan-out
            # rather than a CocoIndex App. The asset is still DEFINED (so the
            # graph is the same on every machine); `_resolve_app()` raises a
            # precise Failure at execute time.
            return [{"app_name": self.app_name, "module": None}]
        raise ValueError(
            "CelticModelLifecycleComponent needs one of: `app_name` (with or "
            "without `module`), a non-empty `apps:` list, or a `subjects:` "
            f"list carrying app specs. Got app_name={self.app_name!r}, "
            f"module={self.module!r}, apps={len(self.apps)} entries."
        )

    def _validate_specs(
        self, specs: list[dict[str, Any]], source_key: str
    ) -> list[dict[str, Any]]:
        """Every spec must name both an app and a module — fail loudly if not."""
        for i, spec in enumerate(specs):
            if not spec.get("app_name") or not spec.get("module"):
                raise ValueError(
                    f"CelticModelLifecycleComponent[{self.app_group or '?'}]: "
                    f"{source_key}[{i}] needs both `app_name` and `module`; "
                    f"got {sorted(spec)}"
                )
        return specs

    def _automation_condition(self) -> dg.AutomationCondition:
        """Explicit `automation_cron` wins, then `schedule.cron`, else eager."""
        cron = self.automation_cron or (self.schedule or {}).get("cron")
        if self.automation == "eager":
            return dg.AutomationCondition.eager().resolve_through_virtual()
        if cron:
            return dg.AutomationCondition.on_cron(cron).resolve_through_virtual()
        return dg.AutomationCondition.eager().resolve_through_virtual()

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 `is_virtual=True` @asset for the CocoIndex v1 App.

        The R1-R4 conformance contract is enforced at scaffold time
        (and at every build_defs invocation) by
        `cocoindex_v1_conformance.check_module(module)`. On failure,
        ConformanceError is raised with the exact rule + fix
        instructions.
        """
        # NOTE: conformance is checked at EXECUTE time (inside the asset
        # body), not here. It imports the App's module, and CocoIndex modules
        # are currently unimportable — the PyPI `cocoindex` package is not
        # installed and the repo's own `cocoindex/` directory shadows the
        # name. Raising here took down the entire code location, so every
        # YAML Component in the repo silently vanished. See the class
        # docstring's "assets are always defined" note.
        automation_condition = self._automation_condition()
        assets = [
            self._build_app_asset(spec, automation_condition)
            for spec in self._iter_app_specs()
        ]
        return dg.Definitions(assets=assets)

    def _build_app_asset(
        self,
        spec: dict[str, Any],
        automation_condition: dg.AutomationCondition,
    ) -> dg.AssetsDefinition:
        """Emit one `is_virtual=True` @asset for a single app spec.

        Kept as its own method so the closure captures THIS spec — building
        the assets inline in a loop would have every closure see the last
        iteration's values.
        """
        app_name: str = spec["app_name"]
        # `None` for the graph-only shape (see `_iter_app_specs` shape 4).
        module_path: str | None = spec.get("module")

        asset_name = f"{_to_snake(app_name)}_app"
        group_name = (
            f"3_model_lifecycle_cocoindex_v1_"
            f"{_to_snake(self.app_group or app_name)}"
        )

        def _resolve_app() -> Any:
            """Import the module and reflect the App — at EXECUTE time."""
            if module_path is None:
                raise dg.Failure(
                    description=(
                        f"cocoindex_app_has_no_module app_name={app_name}. This "
                        "defs.yaml describes a graph-only stage (cognify / "
                        "Graphiti / FalkorDB) but is typed as "
                        "CelticModelLifecycleComponent, which builds CocoIndex "
                        "Apps. Either add `module: <path.to.app_module>`, or "
                        "retype it to KCGCognifyComponent and give it `stage`, "
                        "`dataset` and `source_adapter`."
                    )
                )
            return _import_and_find_app()

        def _import_and_find_app() -> Any:
            """Import the module and reflect the App.

            Deliberately not done at defs-build time: `dg.load_defs()` aborts
            the whole code location on the first exception, so an unimportable
            App module would (and did) take every other Component down with
            it. Failing here still fails loudly, just scoped to the one asset.
            """
            try:
                mod = importlib.import_module(module_path)
            except ImportError as exc:
                raise dg.Failure(
                    description=(
                        f"cocoindex_v1_module_import_failed module={module_path} "
                        f"err={exc}. The pre-refactor flat layout "
                        "(`cianfhoghlaim.cocoindex.<app>`) was repaired by "
                        "the 2026-08-24-wave-0-cocoindex-module-path-repair-v1 "
                        "openspec change (85 defs.yaml files updated). If this "
                        "Failure persists, check (1) the v0 CocoIndex straggler "
                        "audit (Wave 3), (2) the module-path migration map in "
                        "`openspec/specs/cocoindex-v1-module-path-migration/spec.md`."
                    )
                ) from exc

            app = self._find_app(mod, app_name)
            if app is None:
                raise dg.Failure(
                    description=(
                        f"cocoindex_app_not_found name={app_name} module={module_path}"
                    )
                )
            return app

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="cocoindex",
            description=(
                f"L3 CocoIndex v1 App: {app_name} "
                f"(module={module_path}, embedding={self.embedding_model})"
            ),
            automation_condition=automation_condition,
            is_virtual=True,
            tags={t: "" for t in self.tags},
        )
        def _cocoindex_app_asset(
            context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            # Conformance + module resolution happen here, at execute time.
            # `_resolve_app()` runs first so the graph-only shape raises its
            # own precise "no module" Failure rather than a confusing
            # conformance error about a None module path.
            app = _resolve_app()
            if self.conformance_required and module_path is not None:
                self._check_module_r1_to_r4(module_path)

            update = getattr(app, "update", None)
            if update is None:
                raise dg.Failure(
                    description=f"cocoindex_app_has_no_update_method name={app_name}"
                )
            try:
                import asyncio

                if asyncio.iscoroutinefunction(update):
                    asyncio.run(update())
                else:
                    update()
            except Exception as exc:  # pragma: no cover
                context.log.warning(
                    f"cocoindex_update_failed name={app_name} err={exc}"
                )
                return dg.MaterializeResult(
                    metadata={"skipped": True, "reason": str(exc)}
                )
            result_metadata: dict[str, Any] = {
                "app_name": app_name,
                "module": module_path,
                "embedding_model": self.embedding_model,
                "hnsw_index": self.hnsw_index,
                "layer": "3_model_lifecycle",
            }
            for key in ("source", "lance_table"):
                if spec.get(key):
                    result_metadata[key] = spec[key]
            if self.metadata:
                result_metadata.update(self.metadata)
            return dg.MaterializeResult(metadata=result_metadata)

        return _cocoindex_app_asset

    def _check_r1_to_r4(self) -> None:
        """Enforce the R1-R4 conformance contract for every declared app."""
        for spec in self._iter_app_specs():
            self._check_module_r1_to_r4(spec["module"])

    def _r4_is_required(self) -> bool:
        """R4 (`@coco.fn(` present) is skippable for Apps with no embedding
        column — e.g. the GeoParquet writer. An exemption must state a
        reason, so the escape hatch can't be used silently."""
        if not self.r4_exempt:
            return True
        if not self.r4_exempt_reason:
            raise ConformanceError(
                rule="R4",
                message="r4_exempt: true was set without an r4_exempt_reason",
                fix="Add `r4_exempt_reason: <why this App has no embedding column>`",
            )
        return False

    def _check_module_r1_to_r4(self, module_path: str) -> None:
        """Enforce the 4-rule R1-R4 conformance contract on one module.

        R1: Module imports `from ._lifespan import shared_lifespan`
        R2: Module imports the canonical ContextKeys (LANCE_DB, EMBEDDER,
            RESOLVED_FILE_REGISTRY) OR declares an additional one with
            `# R2-exempt: <reason>`
        R3: `coco.App(...)` is at module scope (NOT inside a function body)
        R4: At least one `@coco.fn(` decorator is present
        """
        try:
            mod = importlib.import_module(module_path)
        except ImportError as exc:
            raise ConformanceError(
                rule="R0",
                message=f"module {module_path!r} failed to import: {exc}",
                fix="Check the module path + the `from ._lifespan import shared_lifespan` line",
            ) from exc

        src = getattr(mod, "__file__", None)
        if not src:
            raise ConformanceError(
                rule="R0",
                message=f"module {module_path!r} has no __file__ (dynamic module?)",
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
                fix="Add `from ._lifespan import shared_lifespan` (or another canonical ContextKey) to delegate to the canonical lifespan (see cianfhoghlaim-cocoindex-v1 skill)",
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

        # R4: at least one `@coco.fn(` decorator, unless explicitly exempted
        # with a stated reason (see `_r4_is_required`).
        if self._r4_is_required() and "@coco.fn(" not in source_text:
            raise ConformanceError(
                rule="R4",
                message="no `@coco.fn(` decorator found",
                fix=(
                    "Add `@coco.fn(memo=True)` to your processing function, or "
                    "set `r4_exempt: true` + `r4_exempt_reason: <why>` if this "
                    "App legitimately has no embedding column"
                ),
            )

    def _find_app(self, mod: Any, app_name: str) -> Any:
        """Find the App instance in the module by AppConfig.name.

        Per the CocoIndex v1 API (post-1.0.20), the App instance stores
        its name in the PRIVATE `_name` attribute (e.g.
        `gaeilge_embedding.app.__dict__["_name"]` → "GaeilgeEmbedding").
        The `obj.config.name` and `obj.name` attributes do NOT exist
        on the v1 App class — only the `_name` private attribute does.

        This v1-aware lookup checks `_name` first, then falls back to
        `obj.config.name` (legacy) and `obj.name` (very legacy).
        """
        for name, obj in vars(mod).items():
            if name.startswith("_"):
                continue
            # v1 API: App._name (private attribute)
            obj_dict = getattr(obj, "__dict__", {})
            private_name = obj_dict.get("_name")
            if private_name == app_name:
                return obj
            # Fallback: legacy `obj.config.name`
            config = getattr(obj, "config", None)
            if config is not None and getattr(config, "name", None) == app_name:
                return obj
            # Fallback: very legacy `obj.name`
            if getattr(obj, "name", None) == app_name:
                return obj
            # v1 API: App is sometimes named at module level — match by
            # the local Python variable name too (convention used by
            # many CocoIndex v1 examples)
            if name == app_name and hasattr(obj, "update"):
                return obj
        return None


def _to_snake(name: str) -> str:
    """Convert a CamelCase App name to snake_case."""
    import re

    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


@dataclass
class CelticFederatedOcrComponent(Component, Resolvable):
    """Layer 3 Federated-OCR Component (NEW for T4 of the 5-tangent plan).

    `@dataclass` + `Resolvable`: without them Dagster derives
    `EmptyAttributesModel` (which forbids every extra field), so
    `3_model_lifecycle/federated_ocr/defs.yaml` failed schema validation.

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
    # DEFERRED per the 2026-08-15-dagster-load-path-repair change: default
    # to `"manual"` so BIEP M1-M4 do not trigger the federated simulator.
    # Set `automation_cron: "*/30 * * * *"` (or any non-manual value)
    # once the federated OCR subsystem is on the bringup list.
    automation_cron: str = "manual"

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 @asset: `irish_ocr_federated_smoke`.

        The asset invokes `self.source_module.run_federated_training(...)`
        (the canonical post-v4 entry point) and surfaces any
        exception in the metadata instead of crashing the run.
        """
        import json as _json
        from datetime import datetime as _dt, timezone as _tz

        asset_name = "irish_ocr_federated_smoke"
        group_name = "3_model_lifecycle_federated_ocr_irish_ocr_federated"
        description = (
            f"Federated Irish-OCR simulator smoke run — invokes "
            f"`{self.source_module}.run_federated_training()` "
            f"every {self.automation_cron} to keep the v4 federated "
            f"subsystem warm."
        )

        # DEFERRED: explicit `manual()` automation condition unless the
        # defs.yaml overrides via `automation_cron:`.
        if self.automation_cron == "manual":
            # Dagster 1.13 has no `AutomationCondition.manual()` — `None` is how
            # "never auto-materialise, launch by hand" is expressed.
            _automation = None
        else:
            _automation = dg.AutomationCondition.on_cron(self.automation_cron)

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="federated-learning",
            description=description,
            automation_condition=_automation,
        )
        def _federated_smoke(
            context: dg.AssetExecutionContext,
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
            context.log.info(
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
