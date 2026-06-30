"""
Layer 4 Asset Generation Component — the canonical marimo / TanStack
Start / oRPC / Hono route Component (NEW for the 5-layer rewrite).

Wraps one dashboard / page / route as a Dagster asset that triggers
re-materialisation on upstream changes. This is the Layer 4 factory
that replaces the 11 marimo notebook materialisation assets and the
TanStack Start page generation assets.

    Usage (from a YAML defs file):

    type: cianfhoghlaim.dagster.components.CelticAssetGenerationComponent
    attributes:
      dashboard_kind: marimo
      dashboard_path: notebooks/dashboards/education/mathematics.py
      upstream_assets:
        - 3_model_lifecycle/cocoindex_v1/leabharlann_books
      refresh_on: ["0 6 * * *"]
      slug: primary_curriculum
"""
from __future__ import annotations

import os
from typing import Literal

import dagster as dg
from dagster.components import Component, ComponentLoadContext

DashboardKind = Literal["marimo", "tanstack_page", "orpc_route", "hono_route"]


class CelticAssetGenerationComponent(Component):
    """Layer 4 Asset Generation Component.

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
            marimo notebook, or "web/apps/oideachais-web/src/routes/
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
    upstream_assets: list[str] = []  # noqa: RUF012 — Dagster Component mutable default
    refresh_on: list[str] = ["0 6 * * *"]  # noqa: RUF012 — Dagster Component mutable default
    slug: str = ""

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 1 @asset that re-runs the dashboard/page on upstream
        changes + cron schedules."""
        slug = self.slug or os.path.splitext(os.path.basename(self.dashboard_path))[0]
        group_name = f"4_asset_generation/{self.dashboard_kind}/{slug}"
        asset_name = f"{self.dashboard_kind}_{slug}"
        deps = [dg.AssetDep(key) for key in self.upstream_assets]

        # Compose multiple cron expressions into a single
        # AutomationCondition (OR'd).
        cron_conditions = [
            dg.AutomationCondition.cron(expr) for expr in self.refresh_on
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
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            asset_context.log.info(
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
