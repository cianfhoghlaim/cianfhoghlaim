# Dagster ↔ DLT Integration (`@dlt_assets`)

The `@dlt_assets` decorator from `dagster-dlt` wraps a dlt source
+ pipeline as a set of Dagster assets. This is the canonical
pattern for orchestrating dlt pipelines in Dagster (the KCG
orchestrator).

## Minimal pattern

```python
from dagster_dlt import DagsterDltResource, dlt_assets
import dlt

@dlt.source
def ireland_curriculum_source():
    @dlt.resource(name="primary_outcomes", primary_key=["stage", "curriculum_area", "learning_outcome"])
    def primary_outcomes():
        for outcome in extract_primary_outcomes():
            yield outcome
    return primary_outcomes

@dlt_assets(
    dlt_source=ireland_curriculum_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="ireland_curriculum",
        destination="ducklake",
        dataset_name="cianfhoghlaim.education.ie",
    ),
)
def ireland_curriculum_assets(context, dlt_run_resource: DagsterDltResource):
    yield from dlt_run_resource.run(context=context)
```

## Parallel assets (5 endpoints → 5 parallel assets)

For a REST source with 5 endpoints, use a factory pattern:

```python
from dagster import asset, AssetIn, AssetOut
from dagster_dlt import DagsterDltResource, dlt_assets

@dlt.source
def github_source():
    @dlt.resource(name="repos", primary_key="id")
    def repos():
        yield from fetch_repos()
    @dlt.resource(name="contributors", primary_key=["repo_id", "user_id"])
    def contributors():
        yield from fetch_contributors()
    @dlt.resource(name="issues", primary_key="id")
    def issues():
        yield from fetch_issues()
    @dlt.resource(name="forks", primary_key="id")
    def forks():
        yield from fetch_forks()
    @dlt.resource(name="releases", primary_key="id")
    def releases():
        yield from fetch_releases()
    return repos, contributors, issues, forks, releases

@dlt_assets(
    dlt_source=github_source(),
    dlt_pipeline=dlt.pipeline(pipeline_name="github", destination="ducklake", dataset_name="github"),
)
def github_assets(context, dlt_run_resource: DagsterDltResource):
    yield from dlt_run_resource.run(context=context)
```

The `dlt_assets` decorator yields one Dagster asset per dlt resource
(5 in this case). They are **independent** — they can be
re-materialised in parallel.

## Incremental loading + scheduling

```python
from dagster import schedule, ScheduleEvaluationContext

@dlt_assets(
    dlt_source=github_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="github",
        destination="ducklake",
        dataset_name="github",
    ),
)
def github_assets(context, dlt_run_resource: DagsterDltResource):
    yield from dlt_run_resource.run(context=context)

@schedule(cron_schedule="0 2 * * *", job=define_asset_job("github_assets_job"))
def github_daily_schedule(context: ScheduleEvaluationContext):
    """Run github_assets daily at 02:00 UTC."""
    return RunRequest()
```

## Multiprocess executor (parallelism)

```python
from dagster import multiprocess_executor_config

@job(executor_def=multiprocess_executor_config(max_concurrent=5))
def ireland_curriculum_job():
    ireland_curriculum_assets()
```

The 5 parallel endpoints will run on 5 workers.

## KCG usage

- `orchestration/defs/ireland/curriculum_dlt_assets.py` —
  the 33+ Ireland curriculum assets, each wrapping a dlt source
- `orchestration/defs/leabharlann_assets.py` — 7
  leabharlann assets (4 dlt sources + 3 CocoIndex v1 embedding
  updates)
- The 4-quadrant MultiPartitions by `language + subject` for
  `ireland/curriculum/`

## Reference

- The `dlt_dagster_jaffle.py` reference (400+ lines, the canonical
  dlt + Dagster + jaffle-shop example) was in `docs/dlt/` (deleted
  with the `sync-skills-from-docs` change)
- The `dagster` skill's `references/integrations/dagster-dlt/parallel-github.md`
  for the parallel-asset factory pattern in detail
- The `dagster-dlt` package docs: <https://dagster.io/integrations/dlt>
