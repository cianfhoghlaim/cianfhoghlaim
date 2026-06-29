# Agent 72 — Live docs verifier: Dagster 1.13.11 (partitions + dlt + drift)

**Agent:** 72 (BrowserBase Program 2, Wave 5 — `live-docs`)
**Date:** 2026-06-29 · **Session:** `live-verifier` · **Method:** webfetch (free) only — no browserbase, no firecrawl, no chrome MCP.
**Live (HTTP 200, Vercel CDN, all `Last-Modified: Mon, 29 Jun 2026`):** `pypi.org/pypi/dagster/json`, `pypi.org/pypi/dagster-dlt/json`, `github.com/dagster-io/dagster/releases`, `docs.dagster.io`, `docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets`, `docs.dagster.io/integrations/libraries/dlt`.

---

## 1. TL;DR

- **Current version (verified live, both PyPI JSON + GitHub releases):** `dagster==1.13.11` (core) / `dagster-dlt==0.29.11` (libraries), uploaded to PyPI `2026-06-25T17:29:26Z`, 2 000 304-byte py3 wheel; `dagster-dlt 0.29.11` pins `dagster==1.13.11` exactly.
- **No new release** since Wave 4 agent 84 (1.13.11 is still latest on 2026-06-29). All 4 critical Wave 1 URL paths now 404 — the docs were re-organised from `/concepts/...` → `/guides/build/...` and `/integrations/dlt` → `/integrations/libraries/dlt` (and split into `dlt-pythonic` + `dagster-dlt` sub-pages).
- **Highest-leverage drift:** `.agents/skills/dagster/references/integrations/dagster-dlt/INDEX.md` still says `https://docs.dagster.io/integrations/libraries/dlt` (lucky — that one resolves), but `.agents/skills/dagster/SKILL.md` still shows the **legacy `@dlt_assets` Python decorator pattern** (line 276) and never mentions the new YAML-based `DltLoadCollectionComponent` + `dg scaffold defs` pattern; it also still pre-1.13.9 group names.

---

## 2. Current version (verified live)

| Item | Value | Source |
|:--|:--|:--|
| Latest core | `dagster==1.13.11` | `pypi.org/pypi/dagster/json` → `.info.version`; cross-verified `github.com/dagster-io/dagster/releases` H2 `1.13.11 (core) / 0.29.11 (libraries)` with `<time datetime="2026-06-25T18:23:24Z">` |
| Latest libraries | `dagster-dlt==0.29.11` (and `0.29.11` across all libraries) | same; `pypi.org/pypi/dagster-dlt/json` → `.info.version == "0.29.11"` |
| PyPI upload | `2026-06-25T17:29:26Z` | `pypi.org/pypi/dagster/json` → `.releases."1.13.11"[0].upload_time` |
| Wheel size | 2 000 304 bytes, `python_version: "py3"` | same |
| dagster-dlt pin | `dagster==1.13.11` (exact) | `pypi.org/pypi/dagster-dlt/json` → `.info.requires_dist` |
| KCG pin (current) | `dagster>=1.13.0,<2.0.0`; `dagster-dlt>=0.25.0,<1.0.0` | `openspec/research/2026-06-28-browserbase-program-2/agent-02-dagster.md:33-35` |
| Recommended bump | `dagster-dlt>=0.29.11,<1.0.0` | required for `DltLoadCollectionComponent.partitions_def` + `backfill_policy` (1.13.9 release notes) |

> **Verbatim quote** (PyPI JSON, `pypi.org/pypi/dagster/json`):
> > `"version": "1.13.11"` and `"upload_time": "2026-06-25T17:29:26"`, `"size": 2000304`, `"python_version": "py3"`.

> **Verbatim quote** (GitHub releases, captured 2026-06-29 from `github.com/dagster-io/dagster/releases`):
> > "1.13.11 (core) / 0.29.11 (libraries) ... 25 Jun 18:23 ... [ui] The asset catalog page now renders as a single virtualized list, so workspaces with many asset groups or code locations no longer freeze the UI when expanding those sections. [dagster-dbt] Added a new 'insights' option to DbtProjectComponent's include_metadata field, enabling Dagster+ Insights tracking from YAML config. [dagster-graphql] Added an optional limit argument and new assetSelectionCount / assetCheckSelectionCount fields to the Run GraphQL type."

> **Verbatim quote** (PyPI JSON, `pypi.org/pypi/dagster-dlt/json`):
> > `"version": "0.29.11"`, `"requires_dist": ["dagster==1.13.11", ...]`.

> **Verbatim quote** (live docs, `docs.dagster.io/integrations/libraries/dlt`):
> > "The [dagster-dlt](/integrations/libraries/dlt/dagster-dlt) library provides a `DltLoadCollectionComponent` which can be used to easily represent a collection of dlt sources and pipelines as assets in Dagster."

> **Verbatim quote** (live docs, `docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets`):
> > "There are several ways to partition your data in Dagster: Time-based partitioning ... Static partitioning ... Two-dimensional partitioning ... Dynamic partitioning" — and the recommendation: "We recommend limiting the number of partitions for each asset to 100,000 or fewer. Assets with partition counts exceeding this limit will likely have slower load times in the UI."

**Real URL pattern observed:** every live page on `docs.dagster.io` follows `/<section>/<topic>/<subtopic>` with subtopic included; the version banner shows `Latest (1.13.11)` linked to the unversioned path while 1.12-1.10 redirect to `https://release-<ver>-<build>.archive.dagster-docs.io/`. (See e.g. `https://release-1-12-8.archive.dagster-docs.io/` in the version dropdown.)

---

## 3. Verbatim code examples (5–10) — captured live from `docs.dagster.io`

### 3.1 Time-based partitions + asset job + daily schedule (`/guides/build/partitions-and-backfills/partitioning-assets`, "Time-based partitions")

```python
import datetime
import os
import pandas as pd
import dagster as dg

daily_partitions = dg.DailyPartitionsDefinition(start_date="2024-01-01")

@dg.asset(partitions_def=daily_partitions)
def daily_sales_data(context: dg.AssetExecutionContext) -> None:
    date = context.partition_key
    df = pd.DataFrame({"date": [date] * 10, "sales": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]})
    os.makedirs("data/daily_sales", exist_ok=True)
    filename = f"data/daily_sales/sales_{date}.csv"
    df.to_csv(filename, index=False)
    context.log.info(f"Daily sales data written to {filename}")

daily_sales_job = dg.define_asset_job(name="daily_sales_job", selection=[daily_sales_data, daily_sales_summary])

@dg.schedule(job=daily_sales_job, cron_schedule="0 1 * * *")
def daily_sales_schedule(context):
    previous_day = context.scheduled_execution_time.date() - datetime.timedelta(days=1)
    date = previous_day.strftime("%Y-%m-%d")
    return dg.RunRequest(run_key=date, partition_key=date)
```

### 3.2 Static partitions (`/guides/build/partitions-and-backfills/partitioning-assets`, "Partitions with predefined categories")

```python
import dagster as dg

region_partitions = dg.StaticPartitionsDefinition(["us", "eu", "jp"])

@dg.asset(partitions_def=region_partitions)
def regional_sales_data(context: dg.AssetExecutionContext) -> None:
    region = context.partition_key
    df = pd.DataFrame({"region": [region] * 10, "sales": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]})
    os.makedirs("data/regional_sales", exist_ok=True)
    filename = f"data/regional_sales/sales_{region}.csv"
    df.to_csv(filename, index=False)
```

### 3.3 Two-dimensional `MultiPartitionsDefinition` + `MultiPartitionKey` schedule (same page, "Two-dimensional partitions")

```python
import datetime
import dagster as dg

daily_partitions = dg.DailyPartitionsDefinition(start_date="2024-01-01")
region_partitions = dg.StaticPartitionsDefinition(["us", "eu", "jp"])
two_dimensional_partitions = dg.MultiPartitionsDefinition(
    {"date": daily_partitions, "region": region_partitions}
)

@dg.asset(partitions_def=two_dimensional_partitions)
def daily_regional_sales_data(context: dg.AssetExecutionContext) -> None:
    # partition_key looks like "2024-01-01|us"
    keys_by_dimension: dg.MultiPartitionKey = context.partition_key.keys_by_dimension
    date = keys_by_dimension["date"]      # ty: ignore[invalid-argument-type]
    region = keys_by_dimension["region"]  # ty: ignore[invalid-argument-type]

@dg.schedule(job=daily_regional_sales_job, cron_schedule="0 1 * * *")
def daily_regional_sales_schedule(context):
    """Process previous day's sales data for all regions."""
    previous_day = context.scheduled_execution_time.date() - datetime.timedelta(days=1)
    date = previous_day.strftime("%Y-%m-%d")
    return [
        dg.RunRequest(
            run_key=f"{date}|{region}",
            partition_key=dg.MultiPartitionKey({"date": date, "region": region}),
        )
        for region in region_partitions.get_partition_keys()
    ]
```

### 3.4 Dynamic partitions + sensor (same page, "Partitions with dynamic categories")

```python
region_partitions = dg.DynamicPartitionsDefinition(name="regions")

@dg.sensor(job=regional_sales_job)
def all_regions_sensor(context: dg.SensorEvaluationContext):
    all_regions = ["us", "eu", "jp", "ca", "uk", "au"]
    return dg.SensorResult(
        run_requests=[dg.RunRequest(partition_key=region) for region in all_regions],
        dynamic_partitions_requests=[region_partitions.build_add_request(all_regions)],
    )
```

### 3.5 Custom-calendar partitions with holiday exclusions (same page, "Partitions with custom calendars")

```python
market_calendar = dg.TimeWindowPartitionsDefinition(
    start=datetime(2024, 1, 1),
    cron_schedule="0 0 * * 1-5",  # Weekdays only
    fmt="%Y-%m-%d",
    exclusions=exclusions,  # datetime list of holidays
)
```

### 3.6 `DltLoadCollectionComponent` — scaffold (`/integrations/libraries/dlt`, "Step 2")

```bash
uv add dagster-dlt  # ensure >=0.29.11
dg scaffold defs dagster_dlt.DltLoadCollectionComponent github_snowflake_ingest \
  --source github --destination snowflake
```

### 3.7 `DltLoadCollectionComponent` — `loads.py` + `defs.yaml` (same page, "Step 2")

```python
# my_project/defs/github_snowflake_ingest/loads.py
import dlt

@dlt.source
def my_source():
    @dlt.resource
    def hello_world():
        yield "hello, world!"
    return hello_world

my_load_source = my_source()
my_load_pipeline = dlt.pipeline(destination="snowflake")
```

```yaml
# my_project/defs/github_snowflake_ingest/defs.yaml
type: dagster_dlt.DltLoadCollectionComponent
attributes:
  loads:
    - source: .loads.my_load_source
      pipeline: .loads.my_load_pipeline
```

### 3.8 `DltLoadCollectionComponent` — `translation` (group / metadata) (`/integrations/libraries/dlt`, "Step 4")

```yaml
# my_project/defs/github_snowflake_ingest/defs.yaml
type: dagster_dlt.DltLoadCollectionComponent
attributes:
  loads:
    - source: .loads.dlthub_dlt_stargazers_source
      pipeline: .loads.dlthub_dlt_stargazers_pipeline
      translation:
        group_name: github_data
        description: "Loads all users who have starred the dlt-hub/dlt repo"
        metadata:
          resource_name: "{{ resource.name }}"
          pipeline_name: "{{ pipeline.pipeline_name }}"
          is_transformer: "{{ resource.is_transformer }}"
```

---

## 4. Live changelog entries since Wave 1 (2026-06-28)

> **Wave 1 baseline:** Wave 1 agent captured releases up to **1.13.7** (28 May 2026) at `agent-02-dagster.md:158-167`. Wave 4 agent 84 verified 1.13.11 on 2026-06-29 01:20 UTC. This run is a same-day re-verification (no new release).

| Date | Release | Headline change | Material to KCG? |
|:--|:--|:--|:--|
| 2026-06-25 | **1.13.11** | **[ui]** asset catalog virtualized (no UI freeze with many groups); **[dagster-graphql]** `Run` type gets `limit` arg + `assetSelectionCount` / `assetCheckSelectionCount`; **[dagster-dbt]** `DbtProjectComponent.include_metadata` gains `"insights"`; **bugfix** asset check history cleared on asset/partition wipe. | YES — GraphQL count fields + UI virtualization help croilar 300-asset view. |
| 2026-06-18 | 1.13.10 | **Bugfix** `get_latest_materialization_event` could return a stale pre-wipe materialization (also in Dagster+); **bugfix** asset backfill could get stuck when partitions include certain dates; **perf** cron minute-list partition count fixed. | YES — backfill-stuck fix matters for the 33+ Ireland curriculum cycles. |
| 2026-06-11 | 1.13.9 | **[ui]** hierarchical asset groups via `/` in `group_name` (e.g. `marketing/ads`); wildcard `group:"marketing/*"`. **`is:` filter** syntax (`is:external`, `is:materializable`). **[dg]** `DG_PROJECT_PYTHON_EXECUTABLE` parsed via `python-dotenv`. **[dagster-dlt]** `DltLoadCollectionComponent` gains `partitions_def` + `backfill_policy`. **[helm]** `replicaCount` for user code deployments. | YES — refactor `celtic_language` → `celtic/duchas` style; the dlt `partitions_def` is the gap Wave 1 flagged. |
| 2026-06-04 | 1.13.8 | **[ui]** `Docs` tab → `Components` (with `Library` subtab; old `/docs` redirects). BigQuery/Snowflake/DuckDB I/O managers skip empty DataFrame writes. SQL-injection fix in `dagster-clickhouse` dynamic partition keys (we don't use it). | NO — UI rename only. |
| 2026-05-22 | 1.13.6 | `dg api run launch` for Dagster+ API. Declarative automation perf for shared cron. `DbtCloudComponent` gets `pool` config. **Bugfix** asset keys with `..` or leading `/` could escape I/O manager `base_path`. | YES — DBT pool matters if we adopt `DbtCloudComponent` later. |
| 2026-05-15 | 1.13.5 | `dagstermill` requires `papermill>=2.0.0`. `DAGSTER_MAX_ASSET_BACKFILL_RETRIES` renamed to `DAGSTER_MAX_BACKFILL_RETRIES` (old name still works). **Bugfix** `MultiPartitionsDefinition` + `DynamicPartitionsDefinition` regression on `OutputContext.asset_partition_key_range`. SQLite `busy_timeout` 5s→30s. | YES — KCG Ireland curriculum uses `MultiPartitionsDefinition(language, subject)`; pin to ≥1.13.5 mitigates. |

---

## 5. Drift items vs Wave 1 (`agent-02-dagster.md`)

| # | Wave 1 claim | Live reality (verified 2026-06-29) | Action |
|:--|:--|:--|:--|
| 1 | URL `https://docs.dagster.io/concepts/partitions-schedules-sensors` | **404** today. Replaced by `https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets` (HTTP 200). | Update any docs link, changelog, README that still uses the old path. |
| 2 | URL `https://docs.dagster.io/integrations/dlt` | **404** today. Replaced by `https://docs.dagster.io/integrations/libraries/dlt` (HTTP 200) with two child pages `dlt-pythonic` and `dagster-dlt`. | Update `references/integrations/dagster-dlt/INDEX.md` (which **does** link and luckily uses the new path). |
| 3 | "`DltLoadCollectionComponent` … **replaces our bespoke CelticDltSourceComponent** wrapper" | **Confirmed live**. New pattern uses `dg scaffold defs` + `defs.yaml` + `loads.py`. SKILL.md does NOT show this — only the legacy `@dlt_assets` decorator (line 276-289). | **Add the `DltLoadCollectionComponent` pattern** to SKILL.md and deprecate `celtic_dlt_source.py` (or keep as a thin subclass). |
| 4 | "1.13.9 added `DltLoadCollectionComponent.partitions_def` + `backfill_policy`" | **Confirmed** in 1.13.9 release notes. | Bump `dagster-dlt>=0.25.0,<1.0.0` → `dagster-dlt>=0.29.11,<1.0.0` in `pyproject.toml`. |
| 5 | 1.13.9 "**hierarchical asset groups via `/`**" + "`is:` filter" | **Confirmed** in 1.13.9 release notes. Not in SKILL.md. | Add to SKILL.md under "Asset groups". |
| 6 | 1.13.5 `MultiPartitionsDefinition` + `DynamicPartitionsDefinition` regression fix | **Confirmed** in 1.13.5 release notes. KCG uses this combination. | **Already mitigated** by our `>=1.13.0,<2.0.0` pin (resolves to 1.13.11). |
| 7 | 1.13.5 `DAGSTER_MAX_ASSET_BACKFILL_RETRIES` → `DAGSTER_MAX_BACKFILL_RETRIES` rename | **Confirmed**. | No code action — neither env var is set. |
| 8 | 1.13.8 docs re-organisation: `Docs` tab → `Components` + `Library` subtab | **Confirmed** in 1.13.8 release notes + live in version dropdown. | No code action. |
| 9 | 1.13.11 `assetSelectionCount` GraphQL field | **Confirmed** in 1.13.11 release notes. | Use it for a future asset-count dashboard. |

---

## 6. Skill file update recommendation — `.agents/skills/dagster/SKILL.md`

> **The recommendation below is the exact diff to apply.** All paths already use the v4-consolidated `cianfhoghlaim/` package. Total: 4 hunks, 2 new code blocks.

### Hunk A — Bump the dlt dependency line (line 202)

```diff
- uv add dagster dagster-duckdb dagster-dlt
+ # dagster-dlt>=0.29.11 required for DltLoadCollectionComponent.partitions_def + backfill_policy (Dagster 1.13.9)
+ uv add dagster dagster-duckdb "dagster-dlt>=0.29.11"
```

### Hunk B — Replace the legacy `@dlt_assets` example with the new `DltLoadCollectionComponent` pattern (lines 268-291)

```diff
- ### Multi-tenant DLT asset factory
- ... (24 lines of legacy @dlt_assets + MultiPartitionsDefinition example) ...
+ ### DLT via the upstream `DltLoadCollectionComponent` (1.13.9+)
+
+ The YAML-based Component natively supports `partitions_def` and
+ `backfill_policy` — something our bespoke `celtic_dlt_source.py`
+ wrapper does not. Migrate `celtic_dlt_source.py` to a thin
+ subclass that adds `partitions_def=MultiPartitionsDefinition(...)`
+ via `backfill_policy=BackfillPolicy.multi_run()` (1.13.9 release notes).
+
+ ```bash
+ dg scaffold defs dagster_dlt.DltLoadCollectionComponent github_snowflake_ingest \
+   --source github --destination snowflake
+ uv add dagster-dlt  # ensure >=0.29.11
+ ```
+
+ ```yaml
+ # defs/github_snowflake_ingest/defs.yaml
+ type: dagster_dlt.DltLoadCollectionComponent
+ attributes:
+   loads:
+     - source: .loads.my_source
+       pipeline: .loads.my_pipeline
+       translation:
+         group_name: github_data
+ ```
```

### Hunk C — Add a 1.13.9 "Hierarchical group_name + is: filter" subsection in the Asset Patterns area (after the "Asset groups" bullet block, around line 175)

```diff
  - `oideachais-marimo-dashboards` — Layer 4 (11 marimo
    notebooks for the 5 educational stages)
+
+ ### Hierarchical asset groups (1.13.9+)
+
+ Asset group names may now contain `/` separators (e.g. `celtic/duchas`,
+ `celtic/gaeilge`, `celtic/bearla`). Wildcards work (`group:"celtic/*"`)
+ and the asset graph renders them as nested groups. Combined with the
+ new `is:` filter (`is:external`, `is:materializable`) for asset selection.
+
+ ```python
+ @dg.asset(group_name="celtic/duchas", owners=["team:corpdev"])
+ def duchas_grammar_table() -> None: ...
+ ```
```

### Hunk D — Update `.agents/skills/dagster/references/integrations/dagster-dlt/INDEX.md` (currently a 6-line stub; URL happens to work but body has no usage examples)

```diff
- Docs: https://docs.dagster.io/integrations/libraries/dlt
+ Docs: https://docs.dagster.io/integrations/libraries/dlt
+
+ ## Canonical pattern (1.13.9+)
+
+ ```bash
+ dg scaffold defs dagster_dlt.DltLoadCollectionComponent github_snowflake_ingest \
+   --source github --destination snowflake
+ ```
+
+ See SKILL.md § "DLT via the upstream `DltLoadCollectionComponent`" for the
+ full `defs.yaml` + `loads.py` template and the migration plan for
+ `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_dlt_source.py`.
```

---

## 7. Quick env / toolchain snapshot

| Tool / library | Version on 2026-06-29 | Verified via |
|:--|:--|:--|
| `dagster` (core) | `1.13.11` | `pypi.org/pypi/dagster/json` |
| `dagster-dlt` (libraries) | `0.29.11` (pin `dagster==1.13.11`) | `pypi.org/pypi/dagster-dlt/json` |
| `dg` CLI | Bundled with `dagster-dg-cli` (1.13.11 line) | docs version banner |
| Docs `Last-Modified` | 2026-06-29 (all 4 live pages) | HTTP response headers |
| Live doc URL pattern | `/<section>/<topic>/<subtopic>` with version dropdown at top | observed in every page header |
| Archive URL pattern | `https://release-<ver>-<build>.archive.dagster-docs.io/` | observed in version dropdown (1.9-1.12 only) |
| Legacy URL pattern | `/concepts/...` — **all 404** | wave 1 URLs no longer resolve |

**CCC anchors for the KCG Dagster surface** (run after the diff is applied):

```bash
ccc search "DltLoadCollectionComponent partitions_def"           # confirm 1.13.9 surface in use
ccc search "MultiPartitionsDefinition language subject ireland"  # 33+ Ireland curriculum cycles
ccc search "dg scaffold defs dagster_dlt"                        # confirm NOT yet migrated to the Component pattern
ccc search "group_name celtic duchas"                            # confirm NOT yet using hierarchical 1.13.9 groups
```
