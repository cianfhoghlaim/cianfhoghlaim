---
name: change-detection
description: How the Cianfhoghlaim platform detects upstream changes for `dlt/sources.yaml`. Use when writing a DLT source that needs to re-run on upstream change, wiring a Dagster sensor, or configuring ChangeDetection.io on `arm1-oci`. Covers the 4-layer pattern: DLT incremental cursor + Dagster sitemap-hash sensor + ChangeDetection.io + Firecrawl monitor (the 4th layer, added 2026-06 for blog/changelog-without-sitemap surfaces). Powers BIEP freshness for the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + `gov.ie` education circulars.
---

# Change Detection

## When to use this skill

Use when you need to:

- "Detect when an upstream NCCA / SEC / DES page changes"
- "Wire a DLT source to re-run only when content changes"
- "Add a Dagster sensor that polls a sitemap"
- "Configure ChangeDetection.io on `arm1-oci`"
- "Detect when motherduck / dlthub / lancedb / cocoindex publish a new blog post"
- "Avoid the anti-pattern of polling every source every minute"

## The 4-layer pattern

The Cianfhoghlaim platform detects upstream changes in 4
complementary layers. **All four are running simultaneously**;
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
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Firecrawl monitor (NEW 2026-06)                     │
│  → for blog / changelog / docs surfaces without sitemaps,     │
│    using the Firecrawl LLM-judge to filter meaningful change  │
│    → powers dlt/domains/cross/                  │
│      upstream/blog_post.py + the 3 v1 CocoIndex Apps          │
│      (upstream_blog_monitor, upstream_api_surface,            │
│       cocoindex_v1_conformance). See                          │
│      openspec/changes/upstream-package-monitoring.             │
└─────────────────────────────────────────────────────────────┘
```

## Layer 4 — Firecrawl monitor (NEW 2026-06)

Added by `openspec/changes/upstream-package-monitoring` for blog /
changelog / docs surfaces that don't publish a `sitemap.xml` and
where ChangeDetection.io's HTML diff is too noisy (lots of marketing
copy edits that don't matter). The Firecrawl monitor uses an LLM
judge (`--goal`) to filter meaningful change from noise.

### Canonical recipe

```bash
# Apply a monitor (one-time):
firecrawl monitor apply \
  --page https://motherduck.com/blog/ \
  --goal "Alert on DuckLake / BYOB / Cortex Code changes; ignore marketing noise" \
  --schedule "every 30 minutes" \
  --webhook-url "https://n8n.cianfhoghlaim.ie/webhook/upstream-blog?package=motherduck" \
  --retention-days 90
```

The 4 active monitors (canonical YAML in
`infrastructure/firecrawl/monitors/upstream_packages/`):

| File | Package | Goal focus |
|:--|:--|:--|
| `motherduck_blog.yml` | motherduck | DuckLake releases, BYOB / BYOC hosting, Cortex Code updates |
| `dlthub_blog.yml` | dlthub | Source-context additions, ADE-Bench, Cortex Code integration |
| `lancedb_blog.yml` | lancedb | Lance Format v2.x, Lance Blob V2, multimodal, Namespace |
| `cocoindex_docs.yml` | cocoindex | API-surface changes (coco.App, @coco.fn, FalkorDB connector) |

Each monitor's webhook → n8n workflow
`bonneagar/stacks/n8n/workflows/upstream-blog-monitor.json`
(which validates the payload + writes to
`s3://cianfhoghlaim-upstream-webhooks/<package>/<YYYY-MM-DD>/...jsonl`)
→ DLT incremental source `cianfhoghlaim.dlt.domains.cross.upstream.blog_post`
→ CocoIndex v1 App `upstream_blog_monitor` (BAML `ExtractBlogPostMetadata` +
FalkorDB `BlogPostNode` + `PackageNode` + `PUBLISHED_BY` edges) →
Dagster asset `upstream_blog_monitor_ingest`.

For cocoindex docs (not a blog — a docs surface), the dedicated
`upstream_api_surface` CocoIndex v1 App watches 5 URLs + `llms-full.txt`,
BAML-extracts `ApiChange` records via `ExtractCocoIndexApiChange`, and
writes `ApiChangeNode` + `AFFECTS_APP` edges to the
`upstream_packages_graph` FalkorDB graph. The
`upstream_breaking_change_sensor` (5-min poll) fires Slack alerts to
`#upstream-breaking-changes` when a `change_severity=high` +
`is_breaking=true` change goes unacknowledged.

**Pair this skill with**: the `firecrawl-cli` skill (for the `firecrawl
monitor` CLI recipe) and the `cianfhoghlaim-cocoindex-v1` skill (for the
3 v1 Apps that consume the payloads).

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
sensors in `orchestration/defs/sensors/`:

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
`bonneagar/stacks/changedetection/compose.yaml`.

### Configuration

The `sources.yaml` file at `bonneagar/stacks/changedetection/sources.yaml`
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
- `bonneagar/stacks/changedetection/` — the Layer 3
  Compose stack + `sources.yaml`
- `orchestration/defs/sensors/` — 5 canonical sensor
  implementations
- `dlt/british_isles/ireland/` — 33+ DLT sources (all
  with incremental cursors)

## British-Isles Education pipeline — Layer 2 wiring (post-v4)

The BIEP (`openspec/changes/lc6-biep/`) relies on all 4
change-detection layers for freshness. The canonical Layer 2
sensors live in `orchestration/defs/sensors/`:

| Sensor file | Layer | Trigger | Asset re-materialised |
|:--|:--|:--|:--|
| `ncca_sitemap_sensor.py` | 2 | SHA-256 of `ncca.ie/sitemap.xml` | `lc6_curriculum_syllabus` (6 subjects × 2 langs) |
| `sec_past_paper_sensor.py` | 2 | SHA-256 of `examinations.ie/sitemap.xml` | `lc6_exam_paper_layout` + `lc6_marking_scheme` |
| `gov_ie_circular_sensor.py` | 3 | ChangeDetection.io on `gov.ie/.../circulars/...` | `lc6_government_circulars` (the 7th subject) |
| `cianfhoghlaim_lc6_daily_schedule.py` | 1 + 4 | cron + Dagster schedule at 02:00 UTC | All 42 lc5/lc6 assets |
| `bge_m3_index_rebuild_sensor.py` | 4 | Firecrawl monitor on `huggingface.co/BAAI/bge-m3` | The 24+1 LanceDB tables |

**British-Isles Education pipeline use case:**

- **6 LC subjects** — Mathematics, Chemistry, Geography,
  Gaeilge, English, Computer Science, each monitored by the
  `ncca_sitemap_sensor.py` Layer 2 sensor with SHA-256 hash
  cursor.
- **`gov.ie` circulars** — the `gov_ie_circular_sensor.py`
  Layer 3 sensor (ChangeDetection.io on `arm1-oci`) polls the
  gov.ie circulars pages every hour and re-materialises
  `lc6_government_circulars` (the 7th BIEP subject).
- **2 languages per subject** — the `language` partition
  (`en` / `ga`) is part of the `MultiPartitionsDefinition`, so
  each sensor fans out to 12 re-materialisations per SHA-256
  change (6 subjects × 2 langs).
- **`bge-m3` model freshness** — the
  `bge_m3_index_rebuild_sensor.py` Layer 4 sensor listens to
  the HuggingFace blog + release notes via Firecrawl monitor
  and triggers a LanceDB re-index when the canonical
  `BAAI/bge-m3` embedder bumps a minor version.
- **Dagster `MultiPartitionsDefinition`** — the canonical
  KCG BIEP partition: `(language × subject × level)` for the
  curriculum + `(year)` for the exam-papers partition.

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DLT
  `incremental` cursors (Layer 1) for each BIEP source
- [`.agents/skills/dagster/SKILL.md`](../dagster/SKILL.md) —
  the `@dlt_assets` wrappers + sensor wiring
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the 7 v1 Apps re-materialised by the Layer 2 sensors
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives
- [`.agents/skills/secrets-management/SKILL.md`](../secrets-management/SKILL.md) —
  the `infisical://dev-baile/cianfhoghlaim/FIRECRAWL_API_KEY` +
  `GOV_IE_SCRAPER_TOKEN` secret contract
