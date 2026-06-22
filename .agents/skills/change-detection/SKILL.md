---
name: change-detection
description: How the Cianfhoghlaim platform detects upstream changes for oideachais/sources.yaml. Use when writing a DLT source that needs to re-run on upstream change, wiring a Dagster sensor, or configuring ChangeDetection.io on `arm1-oci`. Covers the 3-layer pattern: DLT incremental cursor + Dagster sitemap-hash sensor + ChangeDetection.io.
---

# Change Detection

## When to use this skill

Use when you need to:

- "Detect when an upstream NCCA / SEC / DES page changes"
- "Wire a DLT source to re-run only when content changes"
- "Add a Dagster sensor that polls a sitemap"
- "Configure ChangeDetection.io on `arm1-oci`"
- "Avoid the anti-pattern of polling every source every minute"

## The 3-layer pattern

The Cianfhoghlaim platform detects upstream changes in 3
complementary layers. **All three are running simultaneously**;
each one is appropriate for a different class of source.

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: DLT `incremental` cursor (per-source, in-pipeline) │
│  → for paginated APIs with a monotonic id / updated_at       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Dagster sitemap-hash sensor (in-Dagster)            │
│  → for sources that publish a sitemap.xml                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: ChangeDetection.io (on arm1-oci, self-hosted)      │
│  → for HTML pages without a sitemap; visual diff             │
└─────────────────────────────────────────────────────────────┘
```

## Layer 1 — DLT `incremental` cursor

Every paginated API source uses `dlt.sources.incremental` so
the source only loads rows newer than the last successful run.
The cursor state is stored in dlt's state file
(`~/.dlt/pipelines/<pipeline_name>/state.json`).

```python
import dlt
from dlt.sources.rest_api import rest_api_source

@dlt.source(name="ireland_curriculum")
def ireland_curriculum_source(
    updated_at=dlt.sources.incremental(
        "updated_at",
        initial_value="2020-01-01T00:00:00Z",
    ),
):
    config = {
        "client": {"base_url": "https://ncca.ie/api/"},
        "resources": [
            {
                "name": "curriculum_pages",
                "endpoint": {
                    "path": "pages",
                    "params": {
                        "updated_since": {
                            "type": "incremental",
                            "cursor_path": "updated_at",
                            "initial_value": "2020-01-01T00:00:00Z",
                        },
                    },
                },
            },
        ],
    }
    return rest_api_source(config)
```

**Conventions:**

- Cursor field is **always** `updated_at` or `last_modified` (UTC
  ISO 8601)
- `initial_value` is the project's `dlt` minimum (e.g.
  `"2020-01-01T00:00:00Z"` for Irish sources)
- For sources without a timestamp, use an incrementing `id`
  cursor instead

## Layer 2 — Dagster sitemap-hash sensor

For sources that publish a `sitemap.xml`, the canonical pattern
is a Dagster sensor that SHA-256-hashes the sitemap and emits a
`RunRequest` only when the hash changes. The project ships 5 such
sensors in `oideachais/dagster_defs/sensors/`:

- `curriculum_freshness_sensor.py`
- `domain_sensors.py`
- `author_archive_sensors.py`
- `cognee_cron_sensor.py`
- `leabharlann_sensors.py`

```python
import hashlib
import requests
from dagster import sensor, SensorEvaluationContext, RunRequest, SkipReason

CURRICULUM_SITEMAP_URL = "https://ncca.ie/sitemap.xml"

@sensor(asset_selection=[AssetKey("ireland_curriculum_pages")])
def curriculum_sitemap_sensor(context: SensorEvaluationContext):
    """Re-run the ireland_curriculum_pages asset when the NCCA sitemap changes."""
    response = requests.get(CURRICULUM_SITEMAP_URL, timeout=30)
    response.raise_for_status()
    current_hash = hashlib.sha256(response.content).hexdigest()

    last_hash = context.cursor or ""
    if current_hash == last_hash:
        return SkipReason(f"NCCA sitemap unchanged (hash {current_hash[:8]})")

    context.update_cursor(current_hash)
    return RunRequest(run_key=current_hash[:16])
```

**Conventions:**

- The sensor returns `SkipReason` (not `None`) when the hash
  matches — Dagster UI shows the skip reason so you can see WHY
  the sensor did not fire
- The cursor is the full SHA-256 hash (64 hex chars)
- The `run_key` is the first 16 chars of the hash (for dedup)
- A polling cadence of 60s is the default; reduce to 300s for
  low-traffic sources

## Layer 3 — ChangeDetection.io (on `arm1-oci`)

For HTML pages without a sitemap (or when a visual diff matters),
the project runs the [ChangeDetection.io](https://changedetection.io)
container on `arm1-oci`. The Compose file is at
`infrastructure/stacks/tools/changedetection/compose.yaml`.

### Configuration

The `sources.yaml` file at `infrastructure/stacks/tools/changedetection/sources.yaml`
pairs each watched URL with the Dagster job that runs when the
URL changes:

```yaml
- name: "NCCA — primary curriculum (mathematics)"
  url: "https://ncca.ie/en/primary/curriculum-area/mathematics"
  check_interval: 3600  # 1 hour
  dagster_job: "ireland_curriculum_mathematics"
  dagster_asset: "ireland_curriculum_pages"
```

### Webhook

ChangeDetection.io posts a JSON payload to a webhook
(`/api/change-detected`) when a source changes. The Dagster
run-launcher accepts the payload, looks up the matching asset
in `sources.yaml`, and emits a `RunRequest` for the affected
partition:

```python
from dagster import webserver, job, RunRequest
import yaml

@webserver(path="/api/change-detected")
def change_detected_webhook(context, payload: dict):
    sources = yaml.safe_load(open(SOURCES_YAML))
    for src in sources:
        if src["url"] == payload["url"]:
            return RunRequest(run_key=payload["uuid"], asset_selection=[src["dagster_asset"]])
    return {"status": "no-match"}
```

## The `sources.yaml` pairing rule

Each ChangeDetection.io entry MUST declare its corresponding
Dagster asset. This is the only invariant:

```yaml
- name: <human-readable>
  url: <full URL>
  check_interval: <seconds, min 300>
  dagster_job: <job name>
  dagster_asset: <asset key>
```

If the URL is shared by multiple assets, list them all and the
webhook fans out the `RunRequest` to each.

## Anti-patterns

- **Polling every DLT source every minute** — wastes API credits
  and warms up rate-limited sources. Use Layer 1 (incremental
  cursor) or Layer 2 (sitemap sensor) instead.
- **ChangeDetection.io as the only mechanism** — fine for
  one-off URLs, but for 100+ sources the UI becomes
  unmanageable. Use Layer 2 for the bulk, Layer 3 for the
  outliers.
- **DLT fixed-cron without an incremental cursor** — the source
  re-loads everything every run. Costs API credits, wastes
  DuckLake writes, and risks duplicates.
- **firecrawl `changeTracking` JSON mode as the primary
  mechanism** — has no history, costs credits per check, and
  silently misses any content that isn't in the structured
  output schema.
- **Polling at sub-minute intervals** — even for fast-moving
  sources, 60s is the floor. Below that, switch to a webhook
  (the upstream pushes).

## Cross-references

- `.agents/skills/dlt/SKILL.md` — the dlt skill (Layer 1 lives
  here)
- `.agents/skills/dagster/SKILL.md` — the Dagster skill
  (Layer 2 sensors live here)
- `infrastructure/stacks/tools/changedetection/` — the Layer 3
  Compose stack + `sources.yaml`
- `oideachais/dagster_defs/sensors/` — 5 canonical sensor
  implementations
- `oideachais/dlt_sources/ireland/` — 33+ DLT sources (all
  with incremental cursors)
