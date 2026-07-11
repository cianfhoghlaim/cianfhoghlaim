# 2026-07-12-british-isles-endpoint-recovery-v1

## Why

The live endpoint probe (recorded in
`docs/agents/british_isles_endpoint_health_audit.md`) found that
**11 of 39 British-Isles canonical endpoints are broken** when hit
with plain HTTP + browser User-Agent:

| Source | Endpoint | Status | Failure mode |
|:--|:--|--:|:--|
| `ncca.py` | `https://ncca.ie` | 403 | WAF (returns 403 even with browser UA + sitemap.xml blocked) |
| `curriculumonline_syllabi.py` | `https://www.curriculumonline.ie` | 403 | Same WAF |
| `sqa/syllabus_source.py` | `https://www.sqa.org.uk/sqa/56983.html` | 404 | URL retired; new finder at `/supporting-others/` |
| `aqa/syllabus_source.py` | `https://www.aqa.org.uk/subjects/gcse` | 404 | Discovery URL retired; use `/search?query=...` |
| `pearson/syllabus_source.py` | `https://qualifications.pearson.com/en/qualifications/edexcel-gcses.html` | 200 | Healthy — but the cache fixture path is stale |
| `wjec/syllabus_source.py` | `https://www.wjec.co.uk` | 200 | Healthy — same caveat as Pearson |
| `ccea/syllabus_source.py` | `https://ccea.org.uk` | 403 | WAF (sitemap.xml 403; robots.txt 200) |
| `courts_ie.py` | `https://www.courts.ie/judgements` | 200 → `/hubs/not-found` | Path retired; new path is `/search/judgements` |
| `gmc.py` | `https://www.gmc-uk.org` | 403 | JS-heavy + WAF |
| `health_social_care.py` | `https://www.gov.im/about-the-government/departments/education-sport-and-culture/` | 403 | Same |
| `isle_of_man.py` | `https://www.gov.im/education` | 403 | Same |

The cross-region expansion work in
[`2026-07-12-british-isles-parity-pipeline-v1`](../2026-07-12-british-isles-parity-pipeline-v1/)
+ the Commonwealth + Canada + Nigeria work in the parallel
follow-on changes MUST NOT propagate the broken pattern. This change
fixes the 11 endpoints + adds the monitoring infrastructure that
detects regressions before they hit CI.

## What changes

### 1. New shared helper `dlt/common/endpoint_recovery.py`

The canonical 3-strategy endpoint-recovery wrapper used by every
fixed source:

1. **Plain HTTP** (`crawl_site` with default backend) for healthy
   endpoints
2. **Firecrawl `stealth` proxy** for WAF-protected endpoints
   (`proxy="stealth"` in `firecrawl_scrape`)
3. **Wayback Machine fallback** (`web.archive.org/web/2024/<url>`)
   for endpoints that 403 even with stealth or that time-out

Every call to `endpoint_recovery.fetch(url)` returns a
`RecoveredPage` dataclass with `status`, `backend_used`,
`content_hash`, `content`, `language`, `wayback_snapshot_url`,
`firecrawl_metadata`. Logs `endpoint_status{status, backend_used}`
structlog event for observability.

### 2. 11 source code edits (no new files, just edits)

- **`dlt/british_isles/ireland/education/ncca.py`**: switch to
  `endpoint_recovery.fetch("https://ncca.ie/en/", strategy="stealth")`;
  add language detection for the `/en/` + `/ga/` URL pair.
- **`dlt/british_isles/ireland/education/curriculumonline_syllabi.py`**: switch
  to `endpoint_recovery.fetch(..., strategy="stealth")`.
- **`dlt/british_isles/scotland/education/sqa/syllabus_source.py`**: switch
  from the hard-coded `/sqa/56983.html` URL to a Firecrawl `map`
  discovery pass that writes the live URL list to
  `stedding/site_scrape_samples/sqa/<lang>/<subject>/urls.json`; the
  resource then reads the URL list from disk when
  `USE_LOCAL_SCRAPES=true`.
- **`dlt/british_isles/england/education/aqa/syllabus_source.py`** +
  **`pearson/syllabus_source.py`** + **`wjec/syllabus_source.py`** +
  **`ccea/syllabus_source.py`**: same Firecrawl `map` discovery
  pattern. Pearson + WJEC use `strategy="auto"` (200 OK); AQA + CCEA
  use `strategy="stealth"`.
- **`dlt/british_isles/ireland/law/courts_ie.py`**: fix the
  `judgements` URL from `/judgements` → `/search/judgements`.
- **`dlt/british_isles/england/medicine/gmc.py`**: switch to
  `strategy="stealth"` + `wait_for=10s`.
- **`dlt/british_isles/isle_of_man/medicine/health_social_care.py`** +
  **`dlt/british_isles/isle_of_man/education/isle_of_man.py`**: switch
  to `strategy="stealth"` + `wait_for=10s`.

### 3. New DuckLake table `oideachais.endpoint_health`

A new endpoint-health monitoring table populated by
`endpoint_recovery.fetch()`. Columns:
`endpoint_url`, `backend_used`, `status_code`, `response_time_ms`,
`content_hash`, `scraped_at`, `language`, `wayback_snapshot_url`.

The Dagster L2 asset `endpoint_health_sink` runs every 6 hours and
emits one row per probed endpoint (the 39 canonical endpoints + any
custom probe set).

### 4. New asset_check pattern

Every fixed source gains an `@asset_check` named
`<source_slug>_endpoint_alive` that asserts the most recent
`endpoint_health` row for the source's canonical URL has
`status_code ∈ (200, 201, 204)`.

### 5. New audit doc `docs/agents/british_isles_endpoint_health_audit.md`

The canonical snapshot of the 39 endpoints (the probe table from
this plan) — committed to the repo so future Drift audits can diff.

### 6. Dagster L2 assets

- **`endpoint_health_sink`** (new) — fires every 6 hours, populates
  the `endpoint_health` table.
- **`endpoint_health_alerts`** (new) — fires every 6 hours,
  posts a Slack alert to `#upstream-endpoints` if any of the 39
  endpoints falls below 200 for 2 consecutive probes.

## Dependencies

```yaml
Blocked by: none
Blocked by (soft): 2026-07-15-pipeline-architecture-clarity-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-12-british-isles-endpoint-recovery-v1 --strict` passes
- All 11 fixed source files AST-parse cleanly
- The new `dlt/common/endpoint_recovery.py` AST-parses cleanly
- `endpoint_recovery.probe_all_39()` returns `status_code=200` for all
  39 canonical endpoints
- `dg check yaml` passes on the new `endpoint_health_sink` +
  `endpoint_health_alerts` L2 defs
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the spec that owns the British Isles DLT + BAML + Dagster + MotherDuck stack
- [`oideachais-pipeline`](../../specs/oideachais-pipeline/spec.md) —
  the parent pipeline
- [`site-crawler`](../../specs/site-crawler/spec.md) —
  the canonical site-scraper primitive
- [`upstream-package-monitoring`](../../specs/upstream-package-monitoring/spec.md) —
  the parallel monitor for the dlthub / firecrawl / motherduck / lancedb / cocoindex upstream packages
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/firecrawl/SKILL.md` — Firecrawl MCP usage
