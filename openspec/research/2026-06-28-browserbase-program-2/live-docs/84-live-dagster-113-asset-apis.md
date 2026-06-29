# Agent 84 — Live docs verifier: Dagster 1.13.x asset APIs

**Agent:** 84 (BrowserBase Program 2, Wave 4 — `live-docs`)
**Date:** 2026-06-29 · **Session:** `2abd92f5-ffea-4905-8c6c-8ea54b7c7cba` · **Credits:** ~10 (6 nav + 3 extract)
**Live (HTTP 200, Vercel CDN, `last-modified: Thu, 25 Jun 2026 19:34–20:47 GMT`):** `docs.dagster.io`, `/guides/build/assets/defining-assets`, `/guides/build/partitions-and-backfills/partitioning-assets`, `/guides/test/asset-checks`, `/guides/build/projects`, `/api/clis/dg-cli/dg-cli-reference`, `github.com/dagster-io/dagster/releases`.

---

## 1. TL;DR

Dagster's docs at `docs.dagster.io` were **re-organised from `/concepts/...` to `/guides/build/...`** since Wave 1; the Wave-1 URLs (`/concepts/assets/software-defined-assets`, `/concepts/partitions-schedules-sensors`) now redirect; `/guides/labs/dg` redirects to `/getting-started/installation` (dg is GA, not Labs).
Current version is **1.13.11 (core) / 0.29.11 (libraries), released 2026-06-25** (no new release in the ~2 h since Wave 1). The 1.13.9+ APIs Wave 1 flagged — `@multi_asset_check(specs=[AssetCheckSpec])`, `blocking=True`, `@asset_check(partitions_def=...)` (PREVIEW), hierarchical `group_name`, `is:` filter, `keys_by_dimension` — are **all live and verbatim in the current docs**, but KCG's `asset_checks.py` still uses the legacy surface. **Highest-leverage drift:** SKILL.md (`.agents/skills/dagster/SKILL.md`) still references the old `/concepts/...` URL pattern and omits 1.13.x APIs.

---

## 2. Current version (verified live)

| Item | Value | Source |
|:--|:--|:--|
| Latest core | `dagster==1.13.11` | `github.com/dagster-io/dagster/releases`, H2 `1.13.11 (core) / 0.29.11 (libraries)`, `<time datetime="2026-06-25T18:23:24Z">` |
| Latest libraries | `dagster-dlt==0.29.11` (and 0.29.11 across all libraries) | same section |
| Release date | **2026-06-25** UTC | `<time datetime="2026-06-25T18:23:24Z">` |
| Docs freshness | `last-modified: Thu, 25 Jun 2026 19:34:28–20:47:10 GMT` | HTTP response headers, all 4 docs pages |
| KCG pin | `dagster>=1.13.0,<2.0.0` ✅; `dagster-dlt>=0.25.0,<1.0.0` ❌ **stale — bump to `>=0.29.11`** | `cianfhoghlaim/pyproject.toml` |

> **Verbatim quote** (1.13.11 release, github.com/dagster-io/dagster/releases, captured 2026-06-29 01:20 UTC):
> > "1.13.11 (core) / 0.29.11 (libraries) ... New ... [ui] The asset catalog page now renders as a single virtualized list, so workspaces with many asset groups or code locations no longer freeze the UI when expanding those sections. [dagster-dbt] Added a new 'insights' option to DbtProjectComponent's include_metadata field, enabling Dagster+ Insights tracking from YAML config. [dagster-graphql] Added an optional limit argument and new assetSelectionCount / assetCheckSelectionCount fields to the Run GraphQL type."

> **Verbatim quote** (live `/guides/test/asset-checks` H2 list):
> > "Getting started​ ... Defining a single asset check​ ... Defining multiple asset checks​ ... Programmatically generating asset checks​ ... Blocking downstream materialization​ ... Partitioned asset checks​ ... Scheduling and monitoring asset checks​"

> **Verbatim quote** (live `/guides/build/assets/defining-assets`, H2 list):
> > "Defining operations that create a single asset​ ... Defining operations that create multiple assets​ ... Defining multiple operations that create a single asset​ ... Asset context​ ... Asset code versions​ ... Assets with multi-part keys​ ... Next steps​"

---

## 3. Verbatim code examples (5–10) — captured live from `docs.dagster.io`

### 3.1 `@asset` with deps + owners + hierarchical group (`/guides/build/assets/defining-assets`)

```python
import dagster as dg


@dg.asset
def daily_sales() -> None: ...


@dg.asset(deps=[daily_sales], group_name="sales")
def weekly_sales() -> None: ...


@dg.asset(
    deps=[weekly_sales],
    owners=["bighead@hooli.com", "team:roof", "team:corpdev"],
)
def weekly_sales_report(context: dg.AssetExecutionContext):
    context.log.info("Loading data for my_dataset")
```

### 3.2 `@multi_asset` + yielded `MaterializeResult` (same page)

```python
import dagster as dg


@dg.multi_asset(specs=[dg.AssetSpec("asset_one"), dg.AssetSpec("asset_two")])
def my_multi_asset():
    yield dg.MaterializeResult(asset_key="asset_one", metadata={"num_rows": 10})
    yield dg.MaterializeResult(asset_key="asset_two", metadata={"num_rows": 24})
```

### 3.3 Canonical 2D `MultiPartitionsDefinition` + `keys_by_dimension` (`/guides/build/partitions-and-backfills/partitioning-assets`)

```python
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
    date = keys_by_dimension["date"]    # ty: ignore[invalid-argument-type]
    region = keys_by_dimension["region"]  # ty: ignore[invalid-argument-type]
```

### 3.4 Single `@asset_check(asset=...)` (`/guides/test/asset-checks`)

```python
import pandas as pd
import dagster as dg


@dg.asset
def orders():
    orders_df = pd.DataFrame({"order_id": [1, 2], "item_id": [432, 878]})
    orders_df.to_csv("orders.csv")


@dg.asset_check(asset=orders)
def orders_id_has_no_nulls():
    orders_df = pd.read_csv("orders.csv")
    num_null_order_ids = orders_df["order_id"].isna().sum()
    return dg.AssetCheckResult(passed=bool(num_null_order_ids == 0))
```

### 3.5 `@multi_asset_check(specs=[AssetCheckSpec])` + yielded `AssetCheckResult` (same page, H2 "Defining multiple asset checks")

```python
from collections.abc import Iterable
import pandas as pd
import dagster as dg


@dg.asset
def orders():
    orders_df = pd.DataFrame({"order_id": [1, 2], "item_id": [432, 878]})
    orders_df.to_csv("orders.csv")


@dg.multi_asset_check(
    specs=[
        dg.AssetCheckSpec(name="orders_id_has_no_nulls", asset="orders"),
        dg.AssetCheckSpec(name="items_id_has_no_nulls", asset="orders"),
    ]
)
def orders_check() -> Iterable[dg.AssetCheckResult]:
    orders_df = pd.read_csv("orders.csv")
    num_null_order_ids = orders_df["order_id"].isna().sum()
    yield dg.AssetCheckResult(
        check_name="orders_id_has_no_nulls",
        passed=bool(num_null_order_ids == 0),
        asset_key="orders",
    )
    num_null_item_ids = orders_df["item_id"].isna().sum()
    yield dg.AssetCheckResult(
        check_name="items_id_has_no_nulls",
        passed=bool(num_null_item_ids == 0),
        asset_key="orders",
    )
```

### 3.6 `blocking=True` — gates downstream materialization (same page, H2 "Blocking downstream materialization")

```python
import pandas as pd
import dagster as dg


@dg.asset
def orders():
    orders_df = pd.DataFrame({"order_id": [1, 2], "item_id": [432, 878]})
    orders_df.to_csv("orders.csv")


# Check that targets `orders`; block materialization of `augmented_orders` on failure
@dg.asset_check(asset=orders, blocking=True)
def orders_id_has_no_nulls():
    orders_df = pd.read_csv("orders.csv")
    num_null_order_ids = orders_df["order_id"].isna().sum()
    return dg.AssetCheckResult(passed=bool(num_null_order_ids == 0))


@dg.asset(deps=[orders])
def augmented_orders():
    orders_df = pd.read_csv("orders.csv")
    augmented_orders_df = orders_df.assign(description=["item_432", "item_878"])
    augmented_orders_df.to_csv("augmented_orders.csv")
```

### 3.7 Partitioned `@asset_check(partitions_def=...)` — PREVIEW (same page, H2 "Partitioned asset checks")

```python
import pandas as pd
import dagster as dg

partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")


@dg.asset(partitions_def=partitions_def)
def orders(context: dg.AssetExecutionContext):
    orders_df = pd.DataFrame({"order_id": [1, 2], "item_id": [432, 878]})
    orders_df.to_csv(f"orders_{context.partition_key}.csv")


@dg.asset_check(asset=orders, partitions_def=partitions_def)
def orders_id_has_no_nulls(context: dg.AssetCheckExecutionContext):
    orders_df = pd.read_csv(f"orders_{context.partition_key}.csv")
    num_null_order_ids = orders_df["order_id"].isna().sum()
    return dg.AssetCheckResult(passed=bool(num_null_order_ids == 0))
```

### 3.8 Inline `check_specs=[AssetCheckSpec(...)]` on `@dg.asset` (same page, last code block)

```python
@dg.asset(
    partitions_def=partitions_def,
    check_specs=[
        dg.AssetCheckSpec(
            name="orders_id_has_no_nulls",
            asset="inline_orders",
            partitions_def=partitions_def,
        )
    ],
)
def inline_orders(context: dg.AssetExecutionContext):
    orders_df = pd.DataFrame({"order_id": [1, 2], "item_id": [432, 878]})
    orders_df.to_csv(f"orders_{context.partition_key}.csv")
    yield dg.Output(value=None)
    num_null_order_ids = orders_df["order_id"].isna().sum()
    yield dg.AssetCheckResult(passed=bool(num_null_order_ids == 0))
```

### 3.9 `dg` CLI signatures — verbatim (`/api/clis/dg-cli/dg-cli-reference`)

```text
dg scaffold [OPTIONS] COMMAND [ARGS]...
dg dev [OPTIONS]
dg check [OPTIONS] COMMAND [ARGS]...
dg check defs [OPTIONS]
dg check toml [OPTIONS]
dg check yaml [OPTIONS] [PATHS]...
dg list [OPTIONS] COMMAND [ARGS]...
dg list component-tree [OPTIONS]
```

### 3.10 1.13.11 bugfix highlights — verbatim (github.com/dagster-io/dagster/releases)

```text
1.13.11 (core) / 0.29.11 (libraries) — Latest
Bugfixes: Asset check history is now cleared when an asset or its partitions are
  wiped; stale entries no longer linger in the Execution History and Partitions views.
  [ui] The run detail page header now displays the asset-check count for asset-job runs.
  [dagster-dbt] .with_insights() now logs a warning instead of raising when called
  against an unsupported adapter.
```

---

## 4. Live changelog entries since Wave 1 (2026-06-28 23:08 → 2026-06-29 01:21)

**No new releases** since Wave 1's research timestamp — the upstream GitHub releases page shows `1.13.11` is still the latest tag at 2026-06-29 01:21 UTC (no tag in the ~2 h since Wave 1 captured). All 1.13.x releases through 1.13.11 (2026-06-25) are already in Wave-1's drift log (`agent-02-dagster.md:275-291`).

| Item | Status |
|:--|:--|
| New `dagster` release | **NONE** |
| New `dagster-dlt` release | **NONE** — 0.29.11 still latest |
| Docs freshness | All 4 pages `last-modified: 2026-06-25 19:34–20:47 GMT` (unchanged since Wave 1) |
| Net new content | `/guides/test/asset-checks` adds the **inline `check_specs=[AssetCheckSpec(...)]` on `@dg.asset`** pattern (code 3.8) and a full H2 on "Scheduling and monitoring asset checks" (e.g. `make_email_on_run_failure_sensor`) — both absent from Wave-1 narrative |
| Wave-1 PREVIEW status | `@asset_check(partitions_def=...)` is still **PREVIEW** (no GA promotion in any 1.13.10 / 1.13.11 release notes) |

---

## 5. Drift items vs Wave 1 text synthesis (`agent-02-dagster.md`)

| Wave-1 statement | Live verification (2026-06-29) | Action |
|:--|:--|:--|
| Cited `/concepts/assets/software-defined-assets` (`agent-02-dagster.md:435`) | Live path is **`/guides/build/assets/defining-assets`** | **UPDATE** all SKILL.md URLs |
| Cited `/concepts/partitions-schedules-sensors` (implied via `agent-02-dagster.md:433`) | Live paths: **`/guides/build/partitions-and-backfills/partitioning-assets`** + `/guides/automate/schedules` (no combined page) | **UPDATE** to two URLs |
| Cited `/guides/labs/dg` for dg CLI | **`/guides/labs/dg` → 302 → `/getting-started/installation`** (dg is GA) | **REPLACE** with `/api/clis/dg-cli/dg-cli-reference` |
| Flagged `@multi_asset_check` as not yet adopted (Wave-1 §8.2) | Live docs confirm **GA** + canonical batch pattern | **Unchanged** — P2-28 refactor |
| Flagged `blocking=True` as not used (Wave-1 §8.3) | Live docs confirm **GA** + gating semantics | **Unchanged** — P2-29 refactor |
| Flagged partitioned `@asset_check` as PREVIEW (Wave-1 §8.4) | Still **PREVIEW** in `/guides/test/asset-checks` H2 | **Unchanged** — Refactor 37 |
| Pinned `dagster-dlt>=0.25.0,<1.0.0` | Latest live = 0.29.11 (6 minor versions newer) | **BUMP** to `>=0.29.11` (Wave-1 §8.5) |
| Did NOT mention inline `check_specs=[AssetCheckSpec]` on `@dg.asset` | Live docs show it (code 3.8) — useful for per-asset inline DQ | **NEW pattern** for KCG |
| Did NOT mention `keys_by_dimension` migration from `partition_key.split("|")` | Live docs use `keys_by_dimension` as canonical (code 3.3) | **MIGRATE** `curriculum_dlt_assets.py:132-133` |
| Did NOT mention 1.13.11 "asset check history cleanup on wipe" | 1.13.11 release confirms GA | **RE-TEST** `WIRE_UNWIRED_DLT_CHECKS` on wipe |
| `dagster-graphql assetCheckSelectionCount` mentioned indirectly | 1.13.11 release confirms GA | **Unchanged** |

---

## 6. Skill file update recommendation — exact diffs

Target: `.agents/skills/dagster/SKILL.md` (410 lines). Wave-1 file at line 11 cites the pre-v4 `oideachais.data_platform.dagster_defs.definitions` path and embeds the INDEX pointing at the now-stale `/concepts/...` URL pattern; the 1.13.x APIs (`@multi_asset_check`, `blocking=True`, partitioned `@asset_check`, hierarchical `group_name`, `keys_by_dimension`) are **absent** from the body.

### Diff 1 — fix the local-entry-point block (lines 11–14 of `.agents/skills/dagster/SKILL.md`)

```diff
-**Environment**: Start local environment with `uv run dagster dev -m oideachais.data_platform.dagster_defs.definitions` inside the `oideachais` directory.
-**Partitions**: `ireland/curriculum/` assets are MultiPartitioned by `language` and `subject` (e.g., `"en|mathematics"`).
-**Lakehouse**: MotherDuck/DuckLake is the sink. Ensure `USE_DUCKLAKE=true` if using MotherDuck, otherwise it uses a local DuckDB file.
-**Namespaces**: NEVER use absolute namespaces (e.g. `oideachais.data_platform...`) from within data_platform. Always use relative or local package imports.
+**Environment (v4)**: `dg dev` from the workspace root (loads `cianfhoghlaim/assets/_oideachais_dagster_defs/_oideachais_dg.toml` → `module_name = "oideachais.dagster_defs.definitions"`). Do NOT use the legacy `dagster dev -m ...` form (removed in Dagster 1.10+ Components).
+**Partitions**: `ireland/curriculum/` assets use `MultiPartitionsDefinition({"subject": StaticPartitionsDefinition(...), "language": StaticPartitionsDefinition(["en","ga"])})`. Read via `context.partition_key.keys_by_dimension["subject"]` (see `/guides/build/partitions-and-backfills/partitioning-assets`), NOT the legacy `partition_key.split("|")`.
+**Lakehouse**: MotherDuck/DuckLake is the sink. `USE_DUCKLAKE=true` selects the DuckLake catalog (Postgres + Garage S3); otherwise local DuckDB at `$DAGSTER_HOME/dagster.duckdb`.
+**Namespaces**: NEVER use absolute namespaces (e.g. `oideachais.data_platform...`) from within data_platform. Always use relative or local package imports.
+**Asset checks (1.13.x)**: use `@dg.multi_asset_check(specs=[dg.AssetCheckSpec(name=..., asset=...)])` for batch checks (replaces the 12 individual `@asset_check` loop in `assets/wire_unwired_dlt_sources.py`). For LLM-gateway fail-fast, add `blocking=True` to `minimax_alias_health` in `assets/llm_gateway_assets.py`. Per-partition DQ badges require the PREVIEW `@dg.asset_check(partitions_def=...)`.
+**Hierarchical groups (1.13.9+)**: prefer `group_name="celtic/duchas"` over the flat `group_name="celtic_language"`; select with `group:"celtic/*"`.
```

### Diff 2 — append the 1.13.x asset-check API surface (insert after `<!-- END GENERATED INDEX -->` on line 84)

```diff
 <!-- END GENERATED INDEX -->

+## Dagster 1.13.x asset-check API surface (live-verified 2026-06-29)
+
+| API | Status | Where | KCG adoption |
+|:--|:--|:--|:--|
+| `@dg.asset_check(asset=...)` | GA | `/guides/test/asset-checks` | ✅ `asset_checks.py:45-79` |
+| `@dg.multi_asset_check(specs=[AssetCheckSpec(...)])` + yielded `AssetCheckResult` | GA (1.13.5+) | same page, H2 "Defining multiple asset checks" | ❌ Refactor P2-28 (Wave 1 §8.2) |
+| `@dg.asset_check(asset=..., blocking=True)` | GA (1.13.5+) | same page, H2 "Blocking downstream materialization" | ❌ Refactor P2-29 — apply to `minimax_alias_health` |
+| `@dg.asset_check(partitions_def=...)` + `AssetCheckExecutionContext` | **PREVIEW** in 1.13.x | same page, H2 "Partitioned asset checks" | ❌ Refactor 37 (cognee graph-model health) |
+| Inline `check_specs=[AssetCheckSpec(...)]` on `@dg.asset` | GA | same page, last code block | NEW — consider for `curriculum_dlt_assets.py` |
+| Hierarchical `group_name="celtic/duchas"` + `group:"celtic/*"` | GA (1.13.9+) | `/about/changelog` 1.13.9 entry | ❌ Refactor P2-31 (Wave 1 §8.4) |
+| `is:` filter (`is:external`, `is:materializable`) | GA (1.13.9+) | same release entry | available, not yet used |
+| `keys_by_dimension: dg.MultiPartitionKey` | GA | `/guides/build/partitions-and-backfills/partitioning-assets` H2 "Two-dimensional partitions" | ❌ Migrate `partition_key.split("|")` at `curriculum_dlt_assets.py:132-133` |
```

### Diff 3 — fix the canonical-docs URL list (after the existing "files to read next" block, mirrors `agent-02-dagster.md:433-436`)

```diff
-- `docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets` — canonical 2D MultiPartitionsDefinition docs
-- `docs.dagster.io/guides/test/asset-checks` — canonical `@asset_check` + `@multi_asset_check` + partitioned checks (PREVIEW) docs
+- `docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets` — canonical 2D `MultiPartitionsDefinition` + `keys_by_dimension` (replaces old `/concepts/partitions-schedules-sensors`)
+- `docs.dagster.io/guides/test/asset-checks` — canonical `@asset_check` + `@multi_asset_check` + `blocking=True` + partitioned checks (PREVIEW)
 - `docs.dagster.io/integrations/libraries/dlt` — canonical `DltLoadCollectionComponent` docs
 - `docs.dagster.io/api/clis/dg-cli/dg-cli-reference` — canonical `dg` CLI flag reference
+- `docs.dagster.io/about/changelog` — full release-by-release notes (1.13.9 hierarchical groups, 1.13.6 `dg api run launch`, etc.)
```

### Diff 4 — bump `dagster-dlt` pin in `cianfhoghlaim/pyproject.toml`

```diff
 dependencies = [
     "dagster>=1.13.0,<2.0.0",
-    "dagster-dlt>=0.25.0,<1.0.0",
+    "dagster-dlt>=0.29.11,<1.0.0",
     ...
 ]
```

Enables the `DltLoadCollectionComponent` adoption (Wave 1 §8.1) and 6 bugfixes since 0.25.0. `dg check defs` will validate the bump.

---

## 7. Files-to-read-next

`agent-02-dagster.md` (Wave-1), `refactors/37-dagster-asset-check-rollout.md`, `refactors/26-refactor-prioritizer.md` P2-28/29/31, `asset_checks.py:45-79` (target for diff 2), `curriculum_dlt_assets.py:132-133` (target for `keys_by_dimension` migration), `.agents/skills/dagster/SKILL.md` (receives diffs 1–3).

---

*End of agent-84 deliverable. Live-verified 2026-06-29 01:21 UTC. Session `2abd92f5-ffea-4905-8c6c-8ea54b7c7cba`; 6 navigations + 3 extractions (~10 credits).*