---
title: 'Change Detection'
domain: 'agents'
status: 'stable'
description: 'How the platform detects changes on the public sources in oideachais/sources.yaml. Primary: DLT incremental + sitemap-hash sensors + ChangeDetection.io on arm1-oci. Alternative: firecrawl changeTracking.'
read_when:
  - writing a DLT source that needs to re-run on upstream change
  - wiring a Dagster sensor
  - configuring ChangeDetection.io
truth: sole
updated: '2026-06-13'
ccc_query_hints:
  - change detection dlt incremental sensor
  - changedetection.io
---

# Change Detection

> **Storage mental model reminder:** writes go to DuckLake, reads go to
> MotherDuck, Iceberg is the long-tail catalogue. See
> [`docs/02-data-platform/storage-mental-model.md`](../02-data-platform/storage-mental-model.md).
> **Browser automation fallback ladder:** firecrawl-mcp → sruth-browser → Firecrawl API. See
> [`docs/03-agents/browser-automation.md`](browser-automation.md).

## Primary stack (3 layers)

### 1. DLT `incremental` cursor

Every DLT source uses `dlt.sources.incremental(...)` to track a cursor
field (typically `last_updated` or `act_id`):

```python
@dlt.resource(write_disposition="merge", primary_key="url")
def pages(cursor: dlt.sources.incremental[int] = dlt.sources.incremental("year")):
    for row in _crawl_legislation(cursor.last_value or 1800):
        yield row
```

- **What it does**: tracks the highest-seen value in the destination's
  `_dlt_loads` table. On re-run, the DLT pipeline only fetches rows
  beyond that cursor.
- **Where it lives**: every `oideachais/dlt_sources/domains/**/*.py`
  that touches a paginated API.
- **Doc**: [`docs/02-data-platform/dlt-pipelines.md`](../02-data-platform/dlt-pipelines.md) § Incremental Loading.

### 2. Dagster sitemap-hash sensors

For sources that publish sitemaps, the canonical change-watcher is a
Dagster sensor at `oideachais/dagster_defs/sensors/`:

```python
@dg.sensor(asset_selection=[AssetKey(["ie", "education", "ncca", "pages"])])
def ireland_ncca_sitemap_sensor(context: SensorEvaluationContext):
    response = httpx.get("https://www.ncca.ie/sitemap.xml")
    new_hash = hashlib.sha256(response.content).hexdigest()
    if context.cursor != new_hash:
        context.update_cursor(new_hash)
        return RunRequest(partition_key="...")
    return SkipReason("Sitemap unchanged")
```

- **What it does**: triggers a Dagster run when the sitemap's hash
  changes, which in turn re-runs the DLT source.
- **Where it lives**: `oideachais/dagster_defs/sensors/curriculum_freshness.py`
  + `domain_sensors.py`.

### 3. ChangeDetection.io (deployed)

The canonical change-watcher for the public sources in
`oideachais/sources.yaml` is **ChangeDetection.io**:

- **Deployed on**: `arm1-oci` (the OCI control-plane host).
- **Compose**: `infrastructure/stacks/tools/changedetection/compose.yaml`.
- **Local checkout**: `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/tools/changedetection`.
- **Capabilities**:
  - Watches a list of URLs / sitemaps / CSS selectors.
  - Stores a history of every diff.
  - Sends webhooks (which we can wire to a Dagster run-launcher).

When a source is added to `oideachais/sources.yaml`, register the
same URL in ChangeDetection.io (UI or via the API). The webhook
hits our Dagster run-launcher, which re-materialises the corresponding
asset.

## Alternative: firecrawl `changeTracking` JSON mode

If you don't have ChangeDetection.io wired for a particular source,
you can use firecrawl's `changeTracking` format:

```python
result = firecrawl.scrape(
    url="https://www.ncca.ie/some-page",
    formats=["changeTracking"],
)
# result["changeTracking"] is a structured diff
```

- **What it does**: single-shot diff (no history). Re-run to get a
  new diff.
- **When to use it**: ad-hoc / once-off / when ChangeDetection.io is
  not deployed for the source.
- **Where it lives**: firecrawl-mcp / firecrawl-py. See
  [`docs/03-agents/browser-automation.md`](browser-automation.md).

## Anti-patterns

- **Polling every DLT source every minute**. Use the sitemap-hash
  sensor or ChangeDetection.io to trigger re-runs only on change.
- **Using firecrawl `changeTracking` as the primary mechanism**. It
  doesn't keep history; it costs credits; it has no UI.
- **Re-running DLT sources on a fixed cron without an incremental
  cursor**. You'll re-load rows that haven't changed.

## See also

- [`docs/02-data-platform/dlt-pipelines.md`](../02-data-platform/dlt-pipelines.md) § Incremental Loading
- [`docs/02-data-platform/storage-mental-model.md`](../02-data-platform/storage-mental-model.md) — substrate
- [`docs/03-agents/browser-automation.md`](browser-automation.md) — firecrawl / browserbase
- [`oideachais/dagster_defs/sensors/`](../../oideachais/dagster_defs/sensors/) — sensor implementations
- [`infrastructure/stacks/tools/changedetection/`](../../infrastructure/stacks/tools/changedetection/) — ChangeDetection.io stack
