# 2026-07-24-biep-v2-gov-uk-change-detection-v1

## Why

The existing BIEP v1 has a freshness guarantee for the Ireland dimension via
the **ChangeDetection.io** pattern at `bonneagar/stacks/changedetection/` —
the `gov.ie` education circulars monitor fires whenever a new circular is
published, and the `jrc_circular` Dagster sensor re-runs the BAML extraction
within minutes. This gives the Irish pipeline an "always-fresh" semantic for
the gov.ie RSS feed.

After Changes 1 + 2 ship the **Junior Cycle + England AQA/OCR/Edexcel**
pipelines, those dimensions have **no equivalent freshness guarantee** —
a new AQA specification update, an OCR syllabus revision, or an Edexcel
marking-scheme change would not be picked up until the next scheduled
materialisation. This change closes that gap.

It ships:

- **3 ChangeDetection.io monitors** in `bonneagar/stacks/changedetection/`
  (one per awarding body: AQA, OCR, Edexcel) that watch the public
  specification pages for changes
- **1 Dagster sensor** at
  `orchestration/defs/sensors/england_change_detection_sensor.py` that
  re-runs the BAML extraction on any changed PDF
- **1 DuckLake audit table** `cianfhoghlaim.education.british_isles.england.changes`
  (the audit log of every change detected since the pipeline landed)
- **Per-board Slack/email webhook alerts** via Langfuse (extension to the
  existing `agent-observability` spec)

The Freshness guarantee is now uniform across all 4 dimensions of
BIEP v2 (Leaving Cycle + Junior Cycle + A-Level + GCSE).

## What changes

### 1. Three ChangeDetection.io monitors

`bonneagar/stacks/changedetection/`:

- `aqa_monitor.yaml` — ChangeDetection.io monitor for AQA spec pages
  (`https://www.aqa.org.uk/subjects/<subject>/specifications`)
- `ocr_monitor.yaml` — ChangeDetection.io monitor for OCR spec pages
  (`https://www.ocr.org.uk/qualifications/<subject>/`)
- `edexcel_monitor.yaml` — ChangeDetection.io monitor for Edexcel spec pages
  (`https://qualifications.pearson.com/en/qualifications/edexcel-<subject>.html`)

Each monitor:
- Uses the ChangeDetection.io `web_scraping` mode + CSS selector for the
  spec version + PDF link
- Stores snapshots in the existing `changedetection/changedetection-data`
  volume (no new volume needed)
- Watches every subject × level combination from the Change 2 England scope
  (9 subjects × 2 levels × 2 selectors per board ≈ 108 watched pages total)

### 2. One Dagster sensor

`orchestration/defs/sensors/england_change_detection_sensor.py`:

```python
@asset_sensor(asset_key=AssetKey("eng_aqa_mathematics_ingested"),
              job=england_england_re_extraction_job)
def england_change_detection_sensor(context, asset_event):
    """Re-run the Change 2 England BAML extraction when ChangeDetection.io
    fires for any of the 3 awarding bodies."""
    ...
```

The sensor:

- Subscribes to the 3 ChangeDetection.io webhook endpoints
- Resolves to the per-board DAG asset key (e.g.
  `eng_aqa_mathematics_ingested` for an AQA maths change)
- Triggers the dagster job `england_england_re_extraction_job` which
  re-runs the BAML extraction + the per-path DuckLake landing + the
  RAGAS vote (the full Change 3 ensemble)
- Emits a Langfuse trace event with the change metadata

### 3. One DuckLake audit table

`cianfhoghlaim.education.british_isles.england.changes` — every detected change
since the pipeline landed:

```sql
CREATE TABLE cianfhoghlaim.education.british_isles.england.changes (
    change_id        STRING PRIMARY KEY,
    board            STRING,         -- 'aqa' | 'ocr' | 'edexcel'
    subject          STRING,
    qualification_level STRING,      -- 'gcse' | 'a_level'
    spec_url         STRING,
    old_version      STRING,
    new_version      STRING,
    old_hash         STRING,
    new_hash         STRING,
    detected_at      TIMESTAMP,
    extraction_rerun_id STRING,       -- back-reference to the Dagster run
    extraction_status STRING,         -- 'success' | 'failed' | 'pending'
    ragas_score      DOUBLE,
    PRIMARY KEY (change_id)
);
```

### 4. Per-board Slack/email webhook alerts

Extension to `agent-observability` so every detected change fires a
notification:

- Slack channel `biep-v2-changes` (post to `#kcg-biep-v2`)
- Email to `kcg-curriculum@cianfhoghlaim.ie`
- Both route via the existing Langfuse alerting infrastructure
- Notifications include the change metadata + the RAGAS score delta
  (old canonical vs new canonical)

### 5. Spec deltas

2 spec deltas:

- `openspec/specs/infrastructure-stacks/spec.md` — add 1 new requirement:
  "Requirement: ChangeDetection.io for England awarding bodies" for the 3
  AQA/OCR/Edexcel monitors
- `openspec/specs/upstream-package-monitoring/spec.md` — add 1 new sibling
  requirement: "Requirement: BIEP v2 England change sensor" mirroring the
  existing gov.ie Ireland circular sensor pattern

## Dependencies

```yaml
Blocked by: 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1
            (the sensor re-runs the Change 2 England BAML extraction)
Blocked by (soft): 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1
                   (the sensor wires through the Change 3 ensemble)
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-24-biep-v2-gov-uk-change-detection-v1 --strict` passes
- 3 ChangeDetection.io monitors created + uploaded to the dev vault
- 1 Dagster sensor implemented + tested end-to-end with a synthetic
  ChangeDetection.io webhook payload
- 1 DuckLake audit table created + populated with at least 1 test row
- Slack webhook fires + email alert fires on a test change
- The Change 2 England pipeline still passes regression (the sensor only
  triggers a re-extraction, never a fresh materialisation)
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`infrastructure-stacks`](../../specs/infrastructure-stacks/spec.md) —
  the umbrella spec for the 94 Docker Compose stacks that this change
  extends with the 3 awarding-body ChangeDetection monitors
- [`upstream-package-monitoring`](../../specs/upstream-package-monitoring/spec.md) —
  the upstream-monitoring spec that this change extends with the BIEP v2
  England sibling sensor
- [`british-isles-education-pipeline`](../2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/) —
  the England pipeline that this sensor re-runs
- [`british-isles-education-pipeline`](../2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/) —
  the ensemble pipeline that this sensor wires through
- [`change-detection`](../.agents/skills/change-detection/SKILL.md) —
  the 4-layer change-detection pattern (DLT cursor + Dagster sitemap-hash
  sensor + ChangeDetection.io + Firecrawl monitor)
- [`agent-observability`](../../specs/agent-observability/spec.md) —
  the observability stack (Langfuse + MLflow + RAGAS + Logfire) that the
  webhook alerts route through
- [.agents/skills/change-detection/SKILL.md](../../.agents/skills/change-detection/SKILL.md) —
  the operational skill for wiring ChangeDetection.io
