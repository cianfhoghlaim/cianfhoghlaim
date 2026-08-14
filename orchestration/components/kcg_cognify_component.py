"""Cognify (knowledge-graph) Components for Layer 3.

Three Components that `orchestration/defs/**/defs.yaml` has referenced by
`type:` since the BIEP v3 orchestration change but which were never written —
`dg.load_defs()` failed with `orchestration.components has no attribute
'KCGCognifyComponent'` (and the same for the other two), which aborted the
whole code location:

  KCGCognifyComponent            5 files under 3_model_lifecycle/cognify/
  CognifyIngestSensorsComponent  3_model_lifecycle/cognify/sensors/
  KCGSubjectPilotFactoryComponent  2_materials/lc_extraction/lc_subjects/

Every module, adapter and function these YAML files point at already exists;
only the Component wrappers were missing.

FAIL-LOUDLY CONTRACT
--------------------
The cognify assets call their `source_adapter` for real. The cognee stack has
never been brought up in this deployment, so they WILL fail at execute time
until it is — that is the intended behaviour. They must not return a
metadata-only success, which is the repo's existing false-success pattern
(see the hardcoded row counts in `generic_england_assets.py`). Assets are
always DEFINED regardless of whether the backend is reachable, so the asset
graph stays reproducible across machines; only execution depends on the stack.
"""
# Deliberately NOT `from __future__ import annotations` — Dagster's Resolvable
# derives the YAML schema from real (not postponed-string) type annotations.
import importlib
import logging
import pathlib
from dataclasses import dataclass, field
from typing import Any

import dagster as dg
from dagster.components import Component, ComponentLoadContext, Resolvable

logger = logging.getLogger(__name__)

# orchestration/components/kcg_cognify_component.py -> repo root
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


@dataclass
class KCGCognifyComponent(Component, Resolvable):
    """One cognify stage -> one Dagster asset + one asset check.

    Attributes:
        stage: The pipeline stage slug (e.g. "aistear", "junior_cycle").
        dataset: The cognee dataset this stage writes (e.g.
            "cianfhoghlaim.education.aistear").
        source_adapter: Dotted path to the adapter module that performs the
            cognify call, e.g.
            "scripts.graph_storage.cognify.cognee_integration.aistear_cognify".
            Resolved lazily at execute time, never at defs-build time.
        edge_types: The graph edge types this stage is expected to produce.
        asset_check_kind: The check kind (e.g. "edges_count").
        assertion: Human-readable assertion, e.g. "edges_count >= 1".
        automation_cron: Cron for the AutomationCondition. Default is
            `"manual"` (DEFERRED per the 2026-08-15-dagster-load-path-repair
            change) — assets do NOT auto-trigger in BIEP M1-M4. Operators
            launch them by hand once the cognify stack (cognee + graphiti +
            falkordb + lancedb + memgraph) is up.
        grouping: Documentation label from the YAML; the Dagster group_name
            is derived from `stage` so it stays a valid identifier.
    """

    stage: str
    dataset: str
    source_adapter: str
    edge_types: list[str] = field(default_factory=list)
    asset_check_kind: str = "edges_count"
    assertion: str = "edges_count >= 1"
    # DEFERRED per the 2026-08-15-dagster-load-path-repair change: default
    # to `"manual"` so BIEP M1-M4 do not trigger this asset. Set
    # `automation_cron: "0 3 * * *"` (or any non-manual value) once the
    # cognify stack is on the bringup list.
    automation_cron: str = "manual"
    grouping: str = ""

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        asset_name = f"{self.stage}_cognified"
        group_name = f"3_model_lifecycle_cognify_{self.stage}"

        # DEFERRED: explicit `manual()` automation condition unless the
        # defs.yaml overrides via `automation_cron:`. The per-asset check
        # (fail-loudly contract) still fires on manual launch.
        if self.automation_cron == "manual":
            _automation = dg.AutomationCondition.manual()
        else:
            _automation = dg.AutomationCondition.on_cron(self.automation_cron)

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind="cognee",
            description=(
                f"L3 cognify: {self.stage} -> {self.dataset} "
                f"(edges: {', '.join(self.edge_types) or 'unspecified'})"
            ),
            automation_condition=_automation,
        )
        def _cognify_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            # Imported here, not at module scope: anything under
            # orchestration/defs is imported at defs-build time, so a
            # module-scope import of an adapter that needs cognee would take
            # down the entire code location.
            try:
                adapter = importlib.import_module(self.source_adapter)
            except ImportError as exc:
                raise dg.Failure(
                    description=(
                        f"cognify_adapter_import_failed stage={self.stage} "
                        f"adapter={self.source_adapter} err={exc}"
                    )
                ) from exc

            run = getattr(adapter, "run", None) or getattr(adapter, "main", None)
            if run is None:
                raise dg.Failure(
                    description=(
                        f"cognify_adapter_has_no_entrypoint stage={self.stage} "
                        f"adapter={self.source_adapter}; expected a `run()` or "
                        "`main()` callable"
                    )
                )
            result = run()

            # Report what the adapter actually returned. `edges_written` stays
            # absent rather than defaulting to 0 when the adapter does not
            # report it, so the check below cannot pass on a fabricated count.
            metadata: dict[str, Any] = {
                "stage": self.stage,
                "dataset": self.dataset,
                "edge_types": self.edge_types,
                "adapter": self.source_adapter,
                "layer": "3_model_lifecycle",
            }
            if isinstance(result, dict) and "edges_written" in result:
                metadata["edges_written"] = int(result["edges_written"])
            return dg.MaterializeResult(metadata=metadata)

        @dg.asset_check(
            asset=_cognify_asset,
            name=f"{self.stage}_cognify_{self.asset_check_kind}",
            description=f"{self.assertion} (stage={self.stage})",
        )
        def _cognify_check(context: dg.AssetCheckExecutionContext) -> dg.AssetCheckResult:
            # Reads the materialisation's real metadata. If the asset did not
            # report `edges_written`, this FAILS rather than assuming success.
            record = context.instance.get_latest_materialization_event(
                _cognify_asset.key
            )
            entries = (
                record.asset_materialization.metadata
                if record and record.asset_materialization
                else {}
            )
            if "edges_written" not in entries:
                return dg.AssetCheckResult(
                    passed=False,
                    metadata={
                        "reason": (
                            "adapter reported no `edges_written`; cannot verify "
                            f"{self.assertion!r}"
                        ),
                        "stage": self.stage,
                    },
                )
            edges = int(entries["edges_written"].value)
            return dg.AssetCheckResult(
                passed=edges >= 1,
                metadata={"edges_written": edges, "assertion": self.assertion},
            )

        return dg.Definitions(assets=[_cognify_asset], asset_checks=[_cognify_check])


@dataclass
class CognifyIngestSensorsComponent(Component, Resolvable):
    """Mounts the `@sensor`-decorated functions in `sensors_module`.

    The YAML's `sensors:` list documents each sensor's watch path, interval
    and target dataset. The sensors themselves are already defined in
    `orchestration/defs/3_model_lifecycle/cognify/sensors/cognify_sensors.py`;
    this Component is what actually gets them into `Definitions` — without it
    they were defined but never loaded (the same fate as the 11 modules in
    `orchestration/sensors/`).
    """

    sensors_module: str
    sensors: list[dict[str, Any]] = field(default_factory=list)
    #: Documentation label from the YAML; not used to derive any Dagster name.
    grouping: str = ""

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        try:
            mod = importlib.import_module(self.sensors_module)
        except ImportError as exc:
            raise dg.Failure(
                description=(
                    f"cognify_sensors_module_import_failed "
                    f"module={self.sensors_module} err={exc}"
                )
            ) from exc

        declared = [s["name"] for s in self.sensors if s.get("name")]
        found: list[dg.SensorDefinition] = []
        missing: list[str] = []
        for name in declared:
            obj = getattr(mod, name, None)
            if isinstance(obj, dg.SensorDefinition):
                found.append(obj)
            else:
                missing.append(name)

        if missing:
            # Loud: a sensor the YAML promises but the module does not define
            # is a wiring bug, not something to skip silently.
            raise dg.Failure(
                description=(
                    f"cognify_sensors_missing module={self.sensors_module} "
                    f"missing={missing}"
                )
            )

        # Every sensor targets a `cognee_ingest_<x>_job` by name. None of
        # those jobs existed anywhere in the repo, so mounting the sensors
        # alone made `Definitions.validate_loadable()` raise
        # ("targets job ... which was not found in this repository") — which
        # is why these sensors had never been loaded at all. Build the job
        # each sensor names, from the `cognee_script` the YAML already
        # declares for it.
        jobs = [self._build_ingest_job(spec) for spec in self.sensors]

        # Emit the JOBS only, not the sensors.
        #
        # `cognify_sensors.py` defines the sensors at module scope and now sits
        # in an auto-discovered directory, so `dg.load_defs()` already picks
        # them up; returning them here too raised "Duplicate definition found
        # for agent_definitions_sensor". The jobs, by contrast, exist nowhere
        # else — without them the sensors are unloadable ("targets job ...
        # which was not found in this repository"), which is why this whole
        # sensor set had never loaded.
        #
        # `found` is still computed above so a sensor named in the YAML but
        # missing from the module fails loudly rather than silently.
        logger.info(
            "CognifyIngestSensorsComponent: verified %d sensors in %s; "
            "emitting %d ingest jobs they target",
            len(found), self.sensors_module, len(jobs),
        )
        return dg.Definitions(jobs=jobs)

    def _build_ingest_job(self, spec: dict[str, Any]) -> dg.JobDefinition:
        """One job per sensor, running that sensor's `cognee_script`.

        Named to match the sensor's `job_name`, which is derived from the
        sensor name: `<x>_sensor` -> `cognee_ingest_<x>_job`.
        """
        sensor_name: str = spec["name"]
        stem = sensor_name.removesuffix("_sensor")
        job_name = f"cognee_ingest_{stem}_job"
        script: str = spec.get("cognee_script", f"scripts/cognee_ingest_{stem}.py")
        target_dataset: str = spec.get("target_dataset", stem)
        watch_path: str = spec.get("watch_path", "")

        @dg.op(name=f"run_{job_name}")
        def _run_ingest(context: dg.OpExecutionContext) -> None:
            import subprocess
            import sys

            script_path = _REPO_ROOT / script
            if not script_path.exists():
                raise dg.Failure(
                    description=(
                        f"cognee_ingest_script_missing job={job_name} "
                        f"path={script_path}"
                    )
                )
            context.log.info(
                f"cognee_ingest start job={job_name} script={script} "
                f"dataset={target_dataset} watching={watch_path}"
            )
            # `check=True`: a non-zero exit must fail the run. Cognee has
            # never been brought up in this deployment, so these WILL fail
            # until it is — loudly, which is the point.
            subprocess.run(
                [sys.executable, str(script_path)],
                cwd=_REPO_ROOT,
                check=True,
            )

        @dg.job(name=job_name, description=f"Run {script} -> cognee dataset {target_dataset}")
        def _ingest_job() -> None:
            _run_ingest()

        return _ingest_job


@dataclass
class KCGSubjectPilotFactoryComponent(Component, Resolvable):
    """Expands the 6 LC subjects into assets + checks via an existing factory.

    Delegates to functions that already exist rather than re-implementing
    them: `source_module.source_functions.assets` /`.asset_checks`.
    """

    subjects: list[str]
    source_module: str
    source_functions: dict[str, str] = field(default_factory=dict)
    factory_module: str = ""
    factory_function: str = ""
    automation_cron: str = "0 4 * * *"
    grouping: str = ""

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        try:
            mod = importlib.import_module(self.source_module)
        except ImportError as exc:
            raise dg.Failure(
                description=(
                    f"lc_subject_source_module_import_failed "
                    f"module={self.source_module} err={exc}"
                )
            ) from exc

        assets_fn_name = self.source_functions.get("assets", "get_lc_subject_assets")
        checks_fn_name = self.source_functions.get(
            "asset_checks", "get_lc_subject_asset_checks"
        )
        assets_fn = getattr(mod, assets_fn_name, None)
        checks_fn = getattr(mod, checks_fn_name, None)
        if assets_fn is None or checks_fn is None:
            raise dg.Failure(
                description=(
                    f"lc_subject_factory_functions_missing "
                    f"module={self.source_module} "
                    f"assets={assets_fn_name}:{assets_fn is not None} "
                    f"asset_checks={checks_fn_name}:{checks_fn is not None}"
                )
            )

        # Deliberately does NOT emit the assets, even though it resolved the
        # functions that build them.
        #
        # `lc_subjects_assets.py` binds `LC_SUBJECT_ASSETS` /
        # `LC_SUBJECT_ASSET_CHECKS` at module scope precisely so Dagster's
        # module scan can find them, and that module now sits in an
        # auto-discovered directory. Emitting them here as well produced
        # duplicate keys (`lc_mathematics_pilot_ingested`, ...), which made
        # `Definitions.validate_loadable()` raise.
        #
        # The module-scope bindings are kept as the owner because they work on
        # BOTH load paths — `dg.load_defs()` and the `_defs_walker` fallback —
        # whereas this Component only runs on the former. This build_defs
        # therefore validates the wiring (the functions exist and are
        # callable) and emits nothing.
        n_assets = len(list(assets_fn()))
        n_checks = len(list(checks_fn()))
        logger.info(
            "KCGSubjectPilotFactoryComponent: verified %d assets + %d checks "
            "for %d LC subjects; ownership left to %s's module-scope bindings",
            n_assets, n_checks, len(self.subjects), self.source_module,
        )
        return dg.Definitions()


__all__ = [
    "CognifyIngestSensorsComponent",
    "KCGCognifyComponent",
    "KCGSubjectPilotFactoryComponent",
]
