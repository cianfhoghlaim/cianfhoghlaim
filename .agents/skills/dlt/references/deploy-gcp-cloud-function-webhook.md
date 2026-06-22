# Deploy: GCP Cloud Function as Webhook

Deploy a dlt pipeline as a **webhook-triggered** GCP Cloud Function.
Useful for event-driven ingestion (Slack events, GitHub webhooks,
Stripe webhooks, etc.).

## Pattern

```python
# main.py (Cloud Function entry point)
import dlt
import json
from typing import Any

@dlt.resource(name="webhook_events")
def webhook_events(payload: dict):
    """Yield one row per webhook event."""
    yield {
        "event_type": payload.get("type"),
        "event_id": payload.get("id"),
        "timestamp": payload.get("created_at"),
        "data": json.dumps(payload),
    }

def your_webhook(request):
    """Cloud Function entry point. Receives the webhook POST."""
    payload = request.get_json()
    pipeline = dlt.pipeline(
        pipeline_name="webhook_ingest",
        destination="bigquery",
        dataset_name="webhooks",
    )
    load_info = pipeline.run(webhook_events(payload))
    return f"Loaded {load_info.loads_id}", 200
```

## `requirements.txt`

```
dlt[bigquery]>=1.0.0
google-cloud-functions>=1.0.0
```

## Deploy

```bash
gcloud functions deploy your-webhook \
  --runtime python310 \
  --trigger-http \
  --entry-point your_webhook \
  --set-env-vars DLT_DISABLE_PLUGINS=true \
  --service-account your-sa@project.iam.gserviceaccount.com \
  --memory 512MB \
  --timeout 60s
```

## KCG usage

The KCG stack uses Cloudflare Workers (not GCP Cloud Functions) for
webhook ingestion. The Cloudflare Worker pattern is similar but
uses the Workers Python (`pyodide`) or TypeScript runtime. See the
`tuatha` and `croilar` quadrants for the Workers-based webhook
ingestion.

For GCP, this pattern is a valid alternative if the KCG stack
ever migrates from Cloudflare to GCP.

## Reference

- The `Deploy GCP Cloud Function as a webhook _ dlt Docs.md` (5.5K)
  was in `docs/dlt/` (deleted with the `sync-skills-from-docs`
  change). The same content is in the dltHub docs at
  <https://dlthub.com/docs/dlt-ecosystem/destinations/bigquery>
- The dltHub `dlt-bigquery` destination docs
- The GCP Cloud Functions Python docs: <https://cloud.google.com/functions/docs/concepts/python-runtime>
