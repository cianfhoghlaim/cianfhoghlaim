"""
Layer 1 Ingestion Component — the canonical DLT source Component (rewrite of
CelticDltSourceComponent).

Wraps a single DLT source and registers it as a Dagster asset with the
canonical 5-layer group_name "1_ingestion/<domain>/<nation>". This is
the Layer 1 factory that replaces all 200+ hand-written @asset functions
under cianfhoghlaim/dagster/assets/.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.dagster.components.CelticIngestionComponent
    attributes:
      source_id: ie.education.ncca
      domain: curriculum
      nation: ie
      automation: on_cron
      automation_cron: "0 2 * * *"
      state_backed: true
      state_refresh_interval: monthly
"""
from __future__ import annotations

import os
from typing import Any, Literal, Optional

import dagster as dg
from dagster.components import (
    Component,
    ComponentLoadContext,
    DefsStateConfig,
    DefsStateConfigArgs,
    ResolvedDefsStateConfig,
)


AutomationStrategy = Literal["eager", "on_cron", "on_dlt_freshness", "manual"]
StateRefreshInterval = Literal["daily", "weekly", "monthly"]


class CelticIngestionComponent(Component):
    """Layer 1 Ingestion Component.

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
    """

    source_id: str
    domain: str
    nation: str
    automation: AutomationStrategy = "on_cron"
    automation_cron: str = "0 2 * * *"
    state_backed: bool = False
    state_refresh_interval: StateRefreshInterval = "monthly"
    defs_state: ResolvedDefsStateConfig = DefsStateConfigArgs.local_filesystem()

    def _build_automation_condition(self) -> dg.AutomationCondition:
        """Translate the (automation, automation_cron) pair into a
        Dagster 1.13+ AutomationCondition."""
        if self.automation == "eager":
            return dg.AutomationCondition.eager()
        if self.automation == "on_cron":
            return dg.AutomationCondition.cron(self.automation_cron)
        if self.automation == "on_dlt_freshness":
            return dg.AutomationCondition.any_deps_updated()
        # manual: never auto-materialise
        return dg.AutomationCondition.manually()

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        # The state-backed path: re-implement the Component's lifecycle.
        if self.state_backed:
            return self._build_state_backed_defs(context)
        return self._build_default_defs(context)

    def _build_default_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """The non-state-backed path: emit a single @asset with the
        canonical 5-layer group_name."""
        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.destinations import get_dlt_destination
        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.safety import safe_dlt_run
        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
            get_default_factory,
        )

        factory = get_default_factory()
        pipeline_name = f"sf_{self.source_id.replace('.', '_')}"
        dataset_name = self.source_id.replace(".", "_").replace("-", "_")
        group_name = f"1_ingestion/{self.domain}/{self.nation}"
        automation_condition = self._build_automation_condition()

        @dg.asset(
            name=pipeline_name,
            group_name=group_name,
            compute_kind="dlt",
            description=f"L1 Ingestion: {self.source_id} (refresh: {self.state_refresh_interval})",
            automation_condition=automation_condition,
        )
        def _dlt_asset(asset_context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
            dlt = __import__("dlt")
            destination = get_dlt_destination()
            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=destination,
                dataset_name=dataset_name,
                dev_mode=False,
            )
            source_obj = factory.source(self.source_id)()
            load_info = safe_dlt_run(pipeline, source_obj)
            return dg.MaterializeResult(
                metadata={
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
            )

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
        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
            get_default_factory,
        )

        factory = get_default_factory()
        state_path = self.defs_state.path_for_key(self.defs_state_key)
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
        """Fetch the DLT source factory state and write it to the cache
        file as JSON. Called by `dg utils refresh-defs-state`."""
        import json

        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
            get_default_factory,
        )

        factory = get_default_factory()
        # Write the source metadata (URLs, partition keys, etc.) to the
        # cache file. The actual materialisation still uses the live
        # DLT source at build time.
        entry = factory.get(self.source_id)
        state = {
            "source_id": self.source_id,
            "domain": self.domain,
            "nation": self.nation,
            "name": entry.name,
            "refresh_interval": self.state_refresh_interval,
            "fetched_at": __import__("datetime").datetime.utcnow().isoformat(),
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


__all__ = ["CelticIngestionComponent", "StateRefreshInterval", "AutomationStrategy"]
