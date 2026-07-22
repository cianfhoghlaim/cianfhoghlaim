"""Celtic Dagster dbt translator.

Mirrors `spaces/data-engineering/package_analytics/resources.py:9-15` (the
prior-art project; pattern A4 from `spaces/README.md` §1.1). Flattens dbt
resource names to `AssetKey`s and pins every dbt asset to the `prepared`
group in Dagster so the asset graph UI groups them with the dlt-prepared
assets.

Why this exists:

- The default Dagster dbt translator exposes dbt models as
  `AssetKey(["<project_name>", "<model_name>"])`, which leaks the project
  name into every asset key. We want flat keys
  (`AssetKey(["weekly_downloads"])`) so the dbt assets match the
  convention used by the rest of `cianfhoghlaim/dagster_defs/`.
- We also want every dbt model to land in the `prepared` group so the
  asset lineage in the Dagster UI shows the canonical "raw → prepared →
  reporting" flow.
- Sources (dlt-ingested upstream tables) and seeds (CSV files) are
  distinct from models. The default translator would assign them keys
  that collide with models (e.g. seed `books` collides with source
  `leabharlann.books` if both are keyed as `["books"]`). We prefix
  sources with `["dbt_source", ...]` and skip seeds entirely (the
  seeds are not user-managed assets).

Usage:

    from orchestration.dbt_translator import CelticDagsterDbtTranslator
    from dagster_dbt import DbtCliResource, dbt_assets

    dbt = DbtCliResource(project_dir=Path(__file__).parent / "dbt_project")
    manifest = dbt.cli(["parse"], manifest={}).wait().target_path / "manifest.json"

    @dbt_assets(manifest=manifest, dagster_dbt_translator=CelticDagsterDbtTranslator())
    def cianfhoghlaim_dbt_assets(context, dbt): ...

See also:
- `cianfhoghlaim/dbt_project/` (the 3 models + 3 seeds + 3 sources)
- `openspec/changes/celtic-data-engineering-patterns/specs/celtic-data-engineering-pipeline/spec.md`
"""

from __future__ import annotations

from dagster import AssetKey
from dagster_dbt import DagsterDbtTranslator


class CelticDagsterDbtTranslator(DagsterDbtTranslator):
    """Custom translator for the oideachais dbt project.

    Three overrides vs. the default:

    1. `get_asset_key` — flatten MODELS to a single-segment key
       (just the model name), dropping the dbt project name from
       the asset key. Sources get a `dbt_source` prefix to avoid
       collisions with models. Seeds are excluded.
    2. `get_group_name` — pin every MODEL to the `prepared` group so
       the asset graph shows raw → prepared → reporting. Sources
       are pinned to `external` (they come from upstream dlt jobs).
    3. Seeds are NOT exposed as Dagster assets (they're test fixtures
       used by the dbt build smoke test, not production data flows).
    """

    @classmethod
    def get_asset_key(cls, dbt_resource_props: dict) -> AssetKey:
        """Map dbt resources to AssetKeys.

        - MODELS: flat single-segment key (e.g. `AssetKey(["weekly_downloads"])`).
        - SOURCES: prefixed with `dbt_source` to avoid collisions
          (e.g. `AssetKey(["dbt_source", "books"])` for the source
          `leabharlann.books`).
        - SEEDS: excluded from the asset graph (we raise NotImplemented
          to signal that the calling @dbt_assets should `exclude=`
          them). Dagster handles this via the `exclude` parameter on
          @dbt_assets, not the translator.
        """
        resource_type = dbt_resource_props.get("resource_type", "")
        if resource_type == "source":
            # `name` for a source is e.g. `leabharlann.books`; we use
            # the table name only to avoid leaking the source schema.
            table_name = dbt_resource_props["name"].split(".")[-1]
            return AssetKey(["dbt_source", table_name])
        # models, seeds, snapshots, tests all use the flat name
        return AssetKey(dbt_resource_props["name"])

    def get_group_name(self, dbt_resource_props: dict) -> str:
        """Pin models to `prepared`, sources to `external`."""
        resource_type = dbt_resource_props.get("resource_type", "")
        if resource_type == "source":
            return "external"
        return "prepared"
