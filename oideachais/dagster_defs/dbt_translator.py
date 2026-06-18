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
  convention used by the rest of `oideachais/dagster_defs/`.
- We also want every dbt model to land in the `prepared` group so the
  asset lineage in the Dagster UI shows the canonical "raw → prepared →
  reporting" flow.

Usage:

    from oideachais.dagster_defs.dbt_translator import CelticDagsterDbtTranslator
    from dagster_dbt import DbtCliResource, dbt_assets

    dbt = DbtCliResource(project_dir=Path(__file__).parent / "dbt_project")
    manifest = dbt.cli(["parse"], manifest={}).wait().target_path / "manifest.json"

    @dbt_assets(manifest=manifest, dagster_dbt_translator=CelticDagsterDbtTranslator())
    def oideachais_dbt_assets(context, dbt): ...

See also:
- `oideachais/dbt_project/` (the 3 models)
- `openspec/changes/celtic-data-engineering-patterns/specs/celtic-data-engineering-pipeline/spec.md`
"""

from __future__ import annotations

from dagster import AssetKey
from dagster_dbt import DagsterDbtTranslator


class CelticDagsterDbtTranslator(DagsterDbtTranslator):
    """Custom translator for the oideachais dbt project.

    Two overrides vs. the default:

    1. `get_asset_key` — flatten to a single-segment key (just the model
       name), dropping the dbt project name from the asset key.
    2. `get_group_name` — pin every dbt asset to the `prepared` group so
       the asset graph shows raw → prepared → reporting.
    """

    @classmethod
    def get_asset_key(cls, dbt_resource_props: dict) -> AssetKey:
        """Flatten `dbt_resource_props["name"]` to a single-segment AssetKey.

        The default returns `AssetKey([project_name, resource_type, name])`
        (3 segments). We drop the project name and resource type to keep
        the asset keys aligned with the rest of `oideachais/dagster_defs/`
        which uses single-segment keys.
        """
        return AssetKey(dbt_resource_props["name"])

    def get_group_name(self, dbt_resource_props: dict) -> str:
        """Pin every dbt asset to the `prepared` group.

        This groups them with the dlt-prepared assets in the Dagster UI
        (the `oideachais/dagster_defs/assets/*_prepared.py` modules).
        """
        return "prepared"
