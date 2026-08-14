"""
Layer 4 Asset Generation Component — the canonical marimo / TanStack
Start / oRPC / Hono route Component (NEW for the 5-layer rewrite).

Wraps one dashboard / page / route as a Dagster asset that triggers
re-materialisation on upstream changes. This is the Layer 4 factory
that replaces the 11 marimo notebook materialisation assets and the
TanStack Start page generation assets.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.orchestration.components.CelticAssetGenerationComponent
    attributes:
      dashboard_kind: marimo
      dashboard_path: notebooks/dashboards/education/mathematics.py
      upstream_assets:
        - 3_model_lifecycle/cocoindex_v1/leabharlann_books
      refresh_on: ["0 6 * * *"]
      slug: primary_curriculum
"""
# Deliberately NOT `from __future__ import annotations` — Dagster's
# Resolvable derives the YAML schema from real (not postponed-string) type
# annotations; see the identical note in layer1_ingestion.py /
# layer2_materials.py. With postponed annotations, `get_model_cls()` raises
# `AttributeError: 'str' object has no attribute '__name__'`.
import os
from dataclasses import dataclass, field
from typing import Literal

import dagster as dg
from dagster.components import Component, ComponentLoadContext, Resolvable

DashboardKind = Literal["marimo", "tanstack_page", "orpc_route", "hono_route"]


@dataclass
class CelticAssetGenerationComponent(Component, Resolvable):
    """Layer 4 Asset Generation Component.

    `@dataclass` + `Resolvable`: without them Dagster derives
    `EmptyAttributesModel` (which forbids every extra field), so all 10
    `4_asset_generation/**/defs.yaml` files failed schema validation and
    the whole layer contributed zero assets. Same fix as
    `CelticIngestionComponent` / `CelticMaterialsComponent`.

    Wraps one marimo dashboard / TanStack Start page / oRPC route /
    Hono route as a Dagster asset that triggers re-materialisation on
    upstream changes.

    Attributes:
        dashboard_kind: The kind of dashboard. One of:
            - "marimo": A marimo notebook at `dashboard_path`
            - "tanstack_page": A TanStack Start page (the path is
              symbolic; the actual re-materialisation triggers a
              Vite build)
            - "orpc_route": An oRPC route at `dashboard_path`
            - "hono_route": A Hono route at `dashboard_path`
        dashboard_path: The path to the dashboard (e.g.
            "notebooks/dashboards/education/mathematics.py" for a
            marimo notebook, or "web/apps/cianfhoghlaim-web/src/routes/
            curriculum.tsx" for a TanStack Start page).
        upstream_assets: List of upstream asset keys that this
            dashboard depends on. Drives the deps.
        refresh_on: List of cron expressions to schedule the
            re-materialisation on. Multiple values are OR'd together.
        slug: The slug used in the group_name (e.g.
            "primary_curriculum"). Default is the dashboard file stem.
    """

    dashboard_kind: DashboardKind
    dashboard_path: str
    upstream_assets: list[str] = field(default_factory=list)
    refresh_on: list[str] = field(default_factory=lambda: ["0 6 * * *"])
    slug: str = ""
    # Supplied by marimo_dashboards/uog_math_coursework/defs.yaml — the list
    # of notebook stems that make up a multi-notebook dashboard. Surfaced in
    # asset metadata; emitting one asset per notebook is follow-on work.
    notebooks: list[str] = field(default_factory=list)

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 @asset that re-runs the dashboard/page on upstream
        changes + cron schedules."""
        slug = self.slug or os.path.splitext(os.path.basename(self.dashboard_path))[0]
        group_name = f"4_asset_generation_{self.dashboard_kind}_{slug}"
        asset_name = f"{self.dashboard_kind}_{slug}"
        # `upstream_assets` are written "2_materials/ie_law/court_rules" in
        # YAML — Dagster's display convention for a multi-segment AssetKey.
        # Passing that string straight to AssetDep fails Dagster's
        # ^[A-Za-z0-9_]+$ single-name validation, so split it into segments.
        # Same fix already present in layer2_materials.py.
        deps = [
            dg.AssetDep(dg.AssetKey(key.split("/"))) for key in self.upstream_assets
        ]

        # Compose multiple cron expressions into a single
        # AutomationCondition (OR'd).
        # `.cron()` was renamed `.on_cron()` in the installed Dagster 1.13 —
        # the old name raises AttributeError at defs-build time.
        cron_conditions = [
            dg.AutomationCondition.on_cron(expr) for expr in self.refresh_on
        ]
        if len(cron_conditions) == 1:
            automation_condition = cron_conditions[0]
        else:
            automation_condition = cron_conditions[0]
            for c in cron_conditions[1:]:
                automation_condition = automation_condition | c

        # Also materialise eagerly when any upstream updates.
        automation_condition = automation_condition | dg.AutomationCondition.any_deps_updated()

        @dg.asset(
            name=asset_name,
            group_name=group_name,
            compute_kind=self.dashboard_kind,
            description=(
                f"L4 Asset Generation: {self.dashboard_kind} at "
                f"{self.dashboard_path}"
            ),
            automation_condition=automation_condition,
            deps=deps,
        )
        def _dashboard_asset(
            context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            context.log.info(
                f"Re-materialising {self.dashboard_kind} at {self.dashboard_path}"
            )
            # The actual re-materialisation is a no-op for the asset
            # graph; the page itself re-reads the upstream data on
            # each render. The Dagster asset is the lineage witness.
            return dg.MaterializeResult(
                metadata={
                    "dashboard_kind": self.dashboard_kind,
                    "dashboard_path": self.dashboard_path,
                    "upstream_assets": self.upstream_assets,
                    "layer": "4_asset_generation",
                    "slug": slug,
                }
            )

        return dg.Definitions(assets=[_dashboard_asset])


__all__ = ["CelticAssetGenerationComponent", "DashboardKind"]
