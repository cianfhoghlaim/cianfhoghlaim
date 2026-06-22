# Deploy: GCP Cloud Functions (scheduled)

Deploy a dlt pipeline as a **scheduled** GCP Cloud Function. Useful
for periodic ingestion (hourly, daily, etc.) without a separate
orchestrator.

## Pattern

```python
# main.py
import dlt

@dlt.source
def my_source():
    @dlt.resource(name="events")
    def events():
        for event in fetch_events():
            yield event
    return events

def scheduled_ingest(event, context):
    """Cloud Function entry point. Triggered by Cloud Scheduler."""
    pipeline = dlt.pipeline(
        pipeline_name="scheduled_ingest",
        destination="bigquery",
        dataset_name="events",
    )
    load_info = pipeline.run(my_source())
    print(f"Loaded {load_info.loads_id}")
```

## Deploy

```bash
gcloud functions deploy scheduled-ingest \
  --runtime python310 \
  --trigger-http \
  --entry-point scheduled_ingest \
  --set-env-vars DLT_DISABLE_PLUGINS=true \
  --service-account your-sa@project.iam.gserviceaccount.com \
  --memory 1GB \
  --timeout 540s  # 9 min (max for Cloud Functions)
```

## Schedule

Create a Cloud Scheduler job that POSTs to the function:

```bash
gcloud scheduler jobs create http daily-ingest \
  --schedule "0 2 * * *" \
  --time-zone "Europe/Dublin" \
  --http-method POST \
  --uri https://europe-west1-PROJECT.cloudfunctions.net/scheduled-ingest \
  --oidc-service-account-email your-sa@project.iam.gserviceaccount.com
```

## KCG usage

The KCG stack uses Dagster for scheduling (the `dagster` skill),
not GCP Cloud Functions + Cloud Scheduler. The Cloud Function
pattern is a valid alternative for small, single-purpose pipelines
that don't need a full orchestrator.

## Reference

- The `Deploy with Google Cloud Functions _ dlt Docs.md` (6.3K) was
  in `docs/dlt/` (deleted with the `sync-skills-from-docs` change)
- The dltHub docs: <https://dlthub.com/docs/dlt-ecosystem/destinations/bigquery>
- The GCP Cloud Functions docs: <https://cloud.google.com/functions/docs>
- The GCP Cloud Scheduler docs: <https://cloud.google.com/scheduler/docs>
