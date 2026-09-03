# DLT + Dagster: Parallel GitHub Reference

The `docs/dagster/integrations/dlt_github/` example (deleted with
the `sync-skills-from-docs` change) is the closest analogue to
KCG's `ireland/curriculum/` ingestion pattern: 5 parallel REST
endpoints, each as its own Dagster asset, with incremental loading
and a daily schedule.

## The factory pattern

```python
# defs/assets_parallel.py
from dagster import asset, AssetExecutionContext, Output
from dagster_dlt import DagsterDltResource, dlt_assets
import dlt

@dlt.source
def github_source():
    @dlt.resource(name="repos", primary_key="id", write_disposition="merge")
    def repos():
        yield from fetch_repos()
    @dlt.resource(name="contributors", primary_key=["repo_id", "user_id"], write_disposition="merge")
    def contributors():
        yield from fetch_contributors()
    @dlt.resource(name="issues", primary_key="id", write_disposition="merge")
    def issues():
        yield from fetch_issues()
    @dlt.resource(name="forks", primary_key="id", write_disposition="merge")
    def forks():
        yield from fetch_forks()
    @dlt.resource(name="releases", primary_key="id", write_disposition="merge")
    def releases():
        yield from fetch_releases()
    return repos, contributors, issues, forks, releases

@dlt_assets(
    dlt_source=github_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="github",
        destination="ducklake",
        dataset_name="github",
    ),
)
def github_assets(context: AssetExecutionContext, dlt_run_resource: DagsterDltResource):
    yield from dlt_run_resource.run(context=context)
```

This yields 5 independent assets. They run in parallel via the
`multiprocess_executor` config:

```python
# defs/dagster_pipeline.py
from dagster import job, multiprocess_executor_config, define_asset_job

github_assets_job = define_asset_job(
    name="github_assets_job",
    selection=AssetSelection.assets(*github_assets),
    executor_def=multiprocess_executor_config(max_concurrent=5),
)
```

## Incremental loading with `apply_hints`

For each resource, `apply_hints` configures the incremental cursor
(field + initial value):

```python
@dlt.resource(name="issues", primary_key="id", write_disposition="merge")
def issues():
    # dlt tracks the latest `updated_at` value and only loads newer rows
    yield from fetch_issues()
```

The Dagster asset automatically reflects the dlt incremental state.

## Daily schedule

```python
from dagster import schedule, ScheduleEvaluationContext

@schedule(cron_schedule="0 2 * * *", job=github_assets_job)
def github_daily(context: ScheduleEvaluationContext):
    return RunRequest()
```

## KCG usage

- The `ireland/curriculum/` assets (33+ sources) use this exact
  pattern
- The `orchestration/defs/ireland/curriculum_dlt_assets.py`
  module defines the `MultiPartitionsDefinition` by
  `language + subject`
- The `cianfhoghlaim-pipeline` spec mandates this MultiPartitions
  scheme

## Reference

- The full `dlt_github/` example (multiple files, the canonical
  DLT + Dagster reference) was in
  `docs/dagster/integrations/dlt_github/` (deleted with the
  `sync-skills-from-docs` change)
- The `dlt` skill's `references/dagster-dlt-assets.md` for the
  full `@dlt_assets` pattern
- The `cianfhoghlaim-pipeline` openspec spec for the partition scheme
