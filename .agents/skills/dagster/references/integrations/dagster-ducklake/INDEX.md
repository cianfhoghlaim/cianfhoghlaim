# DuckLake Integration (the canonical KCG lakehouse sink)

The `dagster-ducklake` integration is the canonical way to wire
DuckLake (Postgres metadata catalog + S3-compatible object store)
into a Dagster asset. KCG uses DuckLake as the production lakehouse
sink (the `cianfhoghlaim/storage/ducklake_client.py` module is the
canonical client).

## Resource configuration

```python
from dagster_ducklake import DuckLakeResource
from dagster import EnvVar

ducklake = DuckLakeResource(
    catalog=EnvVar("DUCKLAKE_CATALOG_URL"),  # e.g. postgres://...
    storage_url=EnvVar("DUCKLAKE_STORAGE_URL"),  # e.g. s3://ducklake/
    aws_access_key_id=EnvVar("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=EnvVar("AWS_SECRET_ACCESS_KEY"),
)
```

## Asset pattern

```python
from dagster import asset, AssetExecutionContext
from dagster_ducklake import DuckLakeResource

@asset
def ireland_primary_curriculum(
    context: AssetExecutionContext,
    ducklake: DuckLakeResource,
) -> None:
    """Materialise the Ireland primary curriculum to DuckLake."""
    # Run dlt pipeline, write to DuckLake
    pipeline = dlt.pipeline(
        pipeline_name="ireland_primary",
        destination=ducklake.get_dlt_destination(),
        dataset_name="oideachais.education.ie",
    )
    load_info = pipeline.run(primary_outcomes_source())
    context.add_output_metadata({
        "rows_loaded": load_info.loads_ids[0] if load_info.loads_ids else 0,
        "dataset_name": "oideachais.education.ie",
    })
```

## Multi-domain schema

DuckLake creates schemas of the form `oideachais.{domain}.{nation}`.
The `oideachais-pipeline` spec mandates this convention:

```python
# Ireland education
load_info = pipeline.run(curriculum_source(), dataset_name="oideachais.education.ie")

# Northern Ireland medicine
load_info = pipeline.run(hse_source(), dataset_name="oideachais.medicine.ni")

# Scotland site analysis
load_info = pipeline.run(site_analysis_source(), dataset_name="oideachais.site_analysis.sct")
```

## KCG usage

- `cianfhoghlaim/storage/ducklake_client.py` — the canonical DuckLake
  client (Postgres catalog + Garage S3 object store)
- `oideachais-pipeline` spec — the single `md:oideachais` (MotherDuck)
  database + single `ducklake:oideachais` (Garage S3) catalog
- `cianfhoghlaim/orchestration/defs/` — the 21+ asset modules that
  write to DuckLake via the resource above

## Reference

- The full `dagster-ducklake` reference (66 lines, with the canonical
  `DuckLakeResource` config) was in
  `docs/dagster/integrations/dagster-ducklake/README.md` (deleted
  with the `sync-skills-from-docs` change). The same content is in
  the upstream [dagster-ducklake](https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-ducklake)
  package
- The `ducklake` skill for upstream DuckLake patterns
- The `oideachais-pipeline` openspec spec for the multi-domain
  schema convention
