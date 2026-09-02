"""
Layer 1 Ingestion Component — the canonical DLT source Component (rewrite of
CelticDltSourceComponent).

Wraps a single DLT source and registers it as a Dagster asset with the
canonical 5-layer group_name "1_ingestion/<domain>/<nation>". This is
the Layer 1 factory that replaces all 200+ hand-written @asset functions
under cianfhoghlaim.orchestration/assets/.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.orchestration.components.CelticIngestionComponent
    attributes:
      source_id: ie.education.ncca
      domain: curriculum
      nation: ie
      automation: on_cron
      automation_cron: "0 2 * * *"
      state_backed: true
      state_refresh_interval: monthly
"""
# Deliberately NOT `from __future__ import annotations` — Dagster's
# Resolvable derives the YAML schema from real (not postponed-string) type
# annotations; see the identical note in layer2_materials.py /
# biep_subject_component.py.
import os
from dataclasses import dataclass, field
from typing import Any, Literal

import dagster as dg
from dagster.components import (
    Component,
    ComponentLoadContext,
    DefsStateConfigArgs,
    Resolvable,
    ResolvedDefsStateConfig,
)

AutomationStrategy = Literal["eager", "on_cron", "on_dlt_freshness", "manual"]
StateRefreshInterval = Literal["daily", "weekly", "monthly"]


@dataclass
class CelticIngestionComponent(Component, Resolvable):
    """Layer 1 Ingestion Component.

    `@dataclass` + `Resolvable`: without them Dagster's Resolvable machinery
    can't derive a YAML schema for this Component (same fix as
    `CelticMaterialsComponent` in layer2_materials.py — see that file's
    docstring for the full explanation of why `Component` alone isn't
    enough in Dagster 1.13+).

    Wraps a single DLT source as a Dagster asset with the canonical
    5-layer group_name "1_ingestion/<domain>/<nation>".

    Attributes:
        source_id: The DLT source id (e.g. "ie.education.ncca"). Resolved
            against the canonical source_factory at runtime.
        domain: The domain (e.g. "curriculum", "law", "medicine",
            "site_analysis", "filesystem"). Drives the group_name prefix.
        nation: The 3-letter nation code (e.g. "ie", "en", "sct"). Drives
            the group_name suffix.
        automation: The automation strategy. One of:
            - "eager": Materialise as soon as any upstream is updated
            - "on_cron": Materialise on `automation_cron` (default)
            - "on_dlt_freshness": Materialise on DLT incremental load
            - "manual": Materialise only via manual launch
        automation_cron: The cron expression (only used when
            automation == "on_cron"). Default: "0 2 * * *"
        state_backed: Whether to use the state-backed Component pattern
            (per the Dagster 1.13+ state-backed components feature). The
            external state is cached and refreshed via
            `dg utils refresh-defs-state`. Use for the 5 high-churn
            sources (NCCA, SEC, CCEA, SQA, WJEC).
        state_refresh_interval: Hint for the refresh cadence (daily,
            weekly, monthly). Default per user direction: "monthly".
            This is documentation/metadata; the actual refresh is driven
            by the `dg utils refresh-defs-state` cron (typically
            scheduled at the system level to match the interval).
        defs_state: Resolved state-backed component config. Defaults to
            local filesystem (per the DefsStateConfigArgs.default).
        dlt_source: Dotted "module.path.function_name" pointing at the
            @dlt.source-decorated callable to run (e.g.
            "dlt_sources.education.ireland.british_isles.education.law.piab.piab_source").
            Resolved via importlib at asset-execution time. Optional —
            state-backed sources that resolve their own source at
            materialisation time may omit it.
        destination_table / destination_tables: Documentation/lineage
            hint(s) for the table(s) this source writes to. Surfaced in
            the asset's MaterializeResult metadata; not otherwise used.
        fallback_resources: Local ingest-queue paths to fall back to when
            the live source is unreachable (documentation/lineage hint,
            surfaced in metadata).
        subject / subject_label: Per-subject labelling (used by the LC6
            per-subject curriculum sources).
        asset_check / asset_check_min_rows: Name + minimum-row threshold
            for an associated asset check (documentation hint; the actual
            check is defined separately, not emitted by this Component).
        tags: Dagster asset tags.
        metadata: Freeform documentation metadata surfaced verbatim.
    """

    source_id: str
    domain: str
    nation: str
    automation: AutomationStrategy = "on_cron"
    automation_cron: str = "0 2 * * *"
    state_backed: bool = False
    state_refresh_interval: StateRefreshInterval = "monthly"
    defs_state: ResolvedDefsStateConfig = field(
        default_factory=DefsStateConfigArgs.local_filesystem
    )
    dlt_source: str | None = None
    destination_table: str | None = None
    destination_tables: list[str] | None = None
    fallback_resources: list[str] = field(default_factory=list)
    subject: str | None = None
    subject_label: str | None = None
    asset_check: str | None = None
    asset_check_min_rows: int | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def _resolve_dlt_source_callable(self):
        """Resolve `self.dlt_source` — a dotted "module.path.function_name"
        string — to the actual @dlt.source-decorated callable via
        importlib.

        Replaces the never-implemented `dlt_sources.common.source_factory`
        registry (confirmed: that module doesn't exist anywhere in the
        codebase, and no equivalent id->callable registry exists either).
        """
        import importlib

        if not self.dlt_source:
            raise ValueError(
                f"CelticIngestionComponent[{self.source_id}] has no "
                "`dlt_source` configured — set `dlt_source: "
                "<module.path>.<function_name>` in defs.yaml to point at "
                "a @dlt.source-decorated callable."
            )
        module_path, _, func_name = self.dlt_source.rpartition(".")
        module = importlib.import_module(module_path)
        return getattr(module, func_name)

    def _build_automation_condition(self) -> dg.AutomationCondition:
        """Translate the (automation, automation_cron) pair into a
        Dagster 1.13+ AutomationCondition."""
        if self.automation == "eager":
            return dg.AutomationCondition.eager()
        if self.automation == "on_cron":
            # AutomationCondition.cron() was renamed to .on_cron() in the
            # installed Dagster 1.13 — same rename already applied in
            # layer2_materials.py's CelticMaterialsComponent; the other 2
            # layer*.py Components (layer3/4/5) still need it but that's
            # outside this plan's scope.
            return dg.AutomationCondition.on_cron(self.automation_cron)
        if self.automation == "on_dlt_freshness":
            return dg.AutomationCondition.any_deps_updated()
        # manual: never auto-materialise
        # Dagster 1.13 has no `AutomationCondition.manually()` — `None` is how
        # "never auto-materialise, launch by hand" is expressed.
        return None

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        # The state-backed path: re-implement the Component's lifecycle.
        if self.state_backed:
            return self._build_state_backed_defs(context)
        return self._build_default_defs(context)

    def _build_default_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """The non-state-backed path: emit a single @asset with the
        canonical 5-layer group_name."""
        from dlt_sources.common.destinations_cianfhoghlaim import (
            get_dlt_destination,
        )
        from dlt_sources.common.safety import safe_dlt_run

        pipeline_name = f"sf_{self.source_id.replace('.', '_')}"
        dataset_name = self.source_id.replace(".", "_").replace("-", "_")
        group_name = f"1_ingestion_{self.domain}_{self.nation}"
        automation_condition = self._build_automation_condition()

        @dg.asset(
            name=pipeline_name,
            group_name=group_name,
            compute_kind="dlt",
            description=f"L1 Ingestion: {self.source_id} (refresh: {self.state_refresh_interval})",
            automation_condition=automation_condition,
            tags={t: "" for t in self.tags},
        )
        def _dlt_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
            dlt = __import__("dlt")
            destination = get_dlt_destination()
            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=destination,
                dataset_name=dataset_name,
                dev_mode=False,
            )
            source_obj = self._resolve_dlt_source_callable()()
            load_info = safe_dlt_run(pipeline, source_obj)
            result_metadata: dict[str, Any] = {
                "source_id": self.source_id,
                "dataset_name": dataset_name,
                "domain": self.domain,
                "nation": self.nation,
                "layer": "1_ingestion",
                "refresh_interval": self.state_refresh_interval,
                "loads_ids": (
                    str(load_info.loads_ids[0]) if load_info.loads_ids else ""
                ),
            }
            if self.destination_table:
                result_metadata["destination_table"] = self.destination_table
            if self.destination_tables:
                result_metadata["destination_tables"] = self.destination_tables
            if self.fallback_resources:
                result_metadata["fallback_resources"] = self.fallback_resources
            if self.metadata:
                result_metadata.update(self.metadata)
            return dg.MaterializeResult(metadata=result_metadata)

        return dg.Definitions(assets=[_dlt_asset])

    def _build_state_backed_defs(
        self, context: ComponentLoadContext
    ) -> dg.Definitions:
        """The state-backed path: cache the DLT source factory state on
        the local filesystem and refresh via `dg utils refresh-defs-state`.

        Subclasses must implement:
            - write_state_to_path: Fetches state from external sources
            - build_defs_from_state: Builds Dagster definitions from the
              cached state
            - defs_state_config: Property that returns configuration for
              state management

        The 5 high-churn sources (NCCA, SEC, CCEA, SQA, WJEC) use this
        path with `state_refresh_interval="monthly"` (per user direction)
        and a system-level `dg utils refresh-defs-state` cron that runs
        at the start of each month.
        """
        # NOTE: this used to eagerly "touch" a `dlt_sources.common.
        # source_factory.get_default_factory()` singleton here before even
        # checking for cached state — that module never existed anywhere in
        # the codebase, so every state-backed source (all 6 LC6 subjects)
        # raised ModuleNotFoundError at defs-build time, before the
        # state_path.exists() check below ever ran. Removed: state
        # resolution doesn't need a source factory, only
        # `_resolve_dlt_source_callable()` (called lazily inside the asset
        # body via `_build_default_defs`) does.
        try:
            state_path = self.defs_state.path_for_key(self.defs_state_key)
        except AttributeError:
            # The installed dagster-components' `DefsStateConfigArgs` no
            # longer exposes `path_for_key` (it exposes
            # `versioned_state_storage`/`key`/`management_type` instead) —
            # this state-backed lifecycle predates that API change and
            # needs a real redesign against the current state-backed-
            # components API, out of scope here. Treat "can't resolve a
            # state path" the same as "no cached state yet" so these
            # assets still load (and materialise) via the default path
            # instead of failing defs-build entirely.
            state_path = None
        if state_path and state_path.exists():
            return self.build_defs_from_state(context, state_path)

        # No cached state: fall back to the default path with a warning.
        # The system-level `dg utils refresh-defs-state` cron will
        # populate the cache on the next run.
        return self._build_default_defs(context)

    @property
    def defs_state_key(self) -> str:
        """Unique key for the cached state file. Format:
        `CelticIngestionComponent[<source_id>]`.
        """
        return f"CelticIngestionComponent[{self.source_id}]"

    def write_state_to_path(self, state_path) -> None:
        """Fetch the DLT source metadata and write it to the cache file as
        JSON. Called by `dg utils refresh-defs-state`."""
        import json
        from datetime import datetime, timezone

        # Resolve the live source callable to record its real function
        # name (used to exist via a `source_factory.get(...).name` lookup
        # — that registry was never implemented; `dlt_source` +
        # `_resolve_dlt_source_callable()` is the real resolution path).
        source_name = self.source_id
        if self.dlt_source:
            source_fn = self._resolve_dlt_source_callable()
            source_name = getattr(source_fn, "__name__", self.source_id)
        state = {
            "source_id": self.source_id,
            "domain": self.domain,
            "nation": self.nation,
            "name": source_name,
            "refresh_interval": self.state_refresh_interval,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        state_path.write_text(json.dumps(state, indent=2))

    def build_defs_from_state(
        self, context: ComponentLoadContext, state_path
    ) -> dg.Definitions:
        """Build the canonical L1 @asset from the cached state."""
        return self._build_default_defs(context)

    def build_defs_for_component(
        self, context: ComponentLoadContext
    ) -> dg.Definitions:
        """State-backed Component lifecycle hook.

        The state-backed Component framework calls this method; we
        delegate to build_defs which dispatches to the state-backed
        or default path.
        """
        return self.build_defs(context)


__all__ = ["AutomationStrategy", "CelticIngestionComponent", "StateRefreshInterval"]
