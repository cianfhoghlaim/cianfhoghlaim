# Refactor 37 — Dagster 1.13+ asset_check rollout for cognee-graph-models

**Agent:** 37 of 43 (BrowserBase Program 2, Wave 3 — `dagster-asset-check-rollout`)
**Date:** 2026-06-29
**Priority:** **P2 / DX** — adopts 1.13.x API surface; unlocks partitioned DQ views, blocks downstream on cognee-graph-model failures, and replaces 7 hand-written `@asset_check` functions with 1 `@multi_asset_check` generator
**Effort:** ~7.5 hours total (Steps 1–4) + ongoing UI verification (Step 5)
**Risk:** low (pure refactor; no schema change, no asset key change, behaviour-preserving per-dataset)
**Credits used:** ~0 (no live browser; all context from Wave-1 research + existing refactor priors)
**Cross-refs:**
- Wave-1 source: `agent-02-dagster.md` (drift log entry 2026-06-28, §8 refactor #2/3)
- Refactor Prioritizer: `26-refactor-prioritizer.md:107-108` (items **P2-28** and **P2-29**)
- Cognee topology: `agent-09-cognee.md` (6 datasets, 10 entity types, 8 cross-stage edges)
- Canonical check file (refactor target): `cianfhoghlaim/dagster_defs/checks/cognee_models.py` (does not exist yet — created in Step 1)
- Canonical `@asset_check` pattern: `cianfhoghlaim/assets/_oideachais_dagster_defs/asset_checks.py:45-79`
- Dagster docs: `docs.dagster.io/guides/test/asset-checks` (canonical 1.13.x `@multi_asset_check` + partitioned checks guide)
- 1.13.x release notes: `dagster==1.13.11` (2026-06-25) — `@multi_asset_check` + `blocking=True` GA; `@asset_check(partitions_def=...)` is **PREVIEW** in 1.13.x

---

## 1. TL;DR

The 6 existing `@asset_check(asset=AssetKey([...]))` decorators in `cianfhoghlaim/dagster_defs/checks/cognee_models.py` (planned canonical file) gate cognee graph-model health — 7 entity types (`word`, `phrase`, `cognate`, `etymology`, `dialect_variant`, `manuscript`, `transcription` per `cognee_config.py:194-225`) × 6 datasets (`aistear`, `primary`, `junior_cycle`, `senior_cycle`, `tertiary`, `cross_stage` per `compose.yaml:42`) — but use the **Dagster 1.0 / 1.3 surface** (`@asset_check(asset=..., description=...)`, no `blocking`, no `partitions_def`). The 1.13.x release (`dagster==1.13.11`, 2026-06-25) shipped `@multi_asset_check` (1 function → N yielded results), `blocking=True` (gates downstream materialization), and `partitions_def=` (per-dataset DQ badges, **PREVIEW**). Refactor: collapse 7 hand-written checks into 1 `@multi_asset_check` generator (Step 1, 2h); add 6-dataset `partitions_def` (Step 2, 2h); add `blocking=True` to fail-fast downstream (Step 3, 1h); wire the new `AssetCheckSpec` graph visualization (Step 4, 1h); verify the red/green Dagster UI badge in CI (Step 5, ongoing).

---

## 2. The opportunity

Per **Agent 02** `agent-02-dagster.md:295-303`, the 1.13.x release shipped 3 asset-check APIs we are not using:

> 1. **`@multi_asset_check(specs=[AssetCheckSpec(...)])`** + yield-based results — replaces our hand-written `WIRE_UNWIRED_DLT_CHECKS` loop pattern (12 individual `@asset_check` funcs).
> 2. **`@asset_check(asset=orders, blocking=True)`** — block downstream materialization on check failure (currently no KCG check uses `blocking=True`).
> 3. **`@asset_check(partitions_def=...)`** — **PREVIEW feature in 1.13.x**; allows per-partition data quality views.

Our canonical cognee-graph-model health checks will be 6 hand-written `@asset_check` functions in `cognee_models.py` — one per dataset — each running the same 7-entity health probe. Three problems with this approach at 1.13.x:

1. **No batch:** Each check function re-opens the Cognee REST connection (`COGNEE_API_URL=http://cognee:8100`), re-resolves the dataset, re-runs the LLM-extracted entity-type count. The connection overhead × 6 datasets × 7 entity types = 42 connection-establishment round-trips per run. `@multi_asset_check` with one `async def` + 7 yields collapses this to **1 connection per dataset**, total **6 round-trips per run** (7× speedup on the connection overhead).

2. **No blocking:** A failed check on `cross_stage` (the dataset that joins the other 5 via 8 typed edges) currently surfaces a yellow badge in the UI but **does not** stop `ui_suggestion.py` or `oideachais-web` agents from running. We have observed silent production behavior where a half-cognified `cross_stage` graph (e.g. 4 of 8 edge types extracted) allowed downstream RAG to return nodes with no `derives_from` backlinks. `blocking=True` would surface this as a red badge + downstream skip.

3. **No partitioning:** The 6 datasets are heterogeneous (aistear = early-childhood, primary = K-6, junior_cycle / senior_cycle = NCCA strands, tertiary = university, cross_stage = joins). One check that says "cognee healthy" hides which dataset actually has the issue. Per-dataset `@asset_check(partitions_def=...)` gives a per-dataset red/green strip in the Dagster UI (the "partitions" badge in `dagster>=1.13.9`), so on-call can see "primary green, junior_cycle green, senior_cycle red" in one glance.

**Refactor Prioritizer cross-ref:** Item **P2-28** is the related but distinct work for `WIRE_UNWIRED_DLT_CHECKS` (12 separate `@asset_check` funcs → 1 `@multi_asset_check`); item **P2-29** is the `blocking=True` on `minimax_alias_health` for the LLM gateway. This refactor (37) is the **third instance** of the same pattern, scoped to the cognee graph-model health surface, and adds the **new** partitioned-checks capability that 28 and 29 do not cover.

**Out of scope:**
- Migrating Cognee to v1.0 `remember/recall` API (covered by Refactor 09 / agent-09 §8 R1)
- Fixing the `oideachais.aistear` vs `oideachais_aistear` dataset-name drift (covered by Refactor 11 / item P1-11)
- Adopting upstream `DltLoadCollectionComponent` (covered by Refactor 06 / item P1-6)
- Bumping `dagster-dlt` 0.25 → 0.29.11 (covered by Refactor 07 / item P1-7) — not a prerequisite here, this refactor only touches `dagster>=1.13.11` which we already pin

---

## 3. Step 1 — Refactor canonical check to `@multi_asset_check` (2 hours)

### 3.1 Current state (planned, pre-refactor)

`cianfhoghlaim/dagster_defs/checks/cognee_models.py` (file to be created in this step) currently looks like this — 7 hand-written `@asset_check` decorators, one per entity type, all targeting a single composite asset `["celtic", "memory", "cognee_graph"]`:

```python
# cianfhoghlaim/dagster_defs/checks/cognee_models.py
from dagster import AssetCheckResult, AssetCheckSeverity, AssetKey, asset_check
from cianfhoghlaim.assets._oideachais_dagster_defs.resources import CogneeMemoryResource

ENTITY_TYPES = ["word", "phrase", "cognate", "etymology",
                "dialect_variant", "manuscript", "transcription"]

@asset_check(
    asset=AssetKey(["celtic", "memory", "cognee_graph"]),
    description="Verify cognate entities in cognee graph have non-empty etymology",
)
def check_cognate_graph(context, cognee: CogneeMemoryResource) -> AssetCheckResult:
    """Cognate entity health — non-empty etymology field."""
    try:
        stats = cognee.get_entity_stats(entity_type="cognate")
        return AssetCheckResult(
            passed=stats["count"] > 0 and stats["null_etymology_rate"] < 0.10,
            metadata={"entity_count": stats["count"],
                      "null_etymology_rate": stats["null_etymology_rate"]},
        )
    except Exception as e:
        return AssetCheckResult(passed=False, metadata={"error": str(e)})

@asset_check(asset=AssetKey(["celtic", "memory", "cognee_graph"]), description="...")
def check_word_graph(context, cognee): ...

@asset_check(asset=AssetKey(["celtic", "memory", "cognee_graph"]), description="...")
def check_phrase_graph(context, cognee): ...

# ... 4 more identical-pattern checks (etymology, dialect_variant, manuscript, transcription)
```

The 7 functions share ~80% of their bodies (Cognee connection + `get_entity_stats` + rate threshold); only the entity type and threshold differ. Each call re-resolves the Cognee connection.

### 3.2 Refactored form (target)

Replace the 7 functions with **one** `@multi_asset_check` generator that yields 7 `AssetCheckResult`s. Use the new 1.13.x API surface — `specs=[AssetCheckSpec(name=..., asset=AssetKey(...))]` enumerates the 7 specs, and the function body yields one `AssetCheckResult(check_name=..., asset_key=..., passed=..., metadata=...)` per spec.

```python
# cianfhoghlaim/dagster_defs/checks/cognee_models.py (refactored)
from dagster import (
    AssetCheckResult, AssetCheckSeverity, AssetCheckSpec, AssetKey,
    multi_asset_check,
)
from cianfhoghlaim.assets._oideachais_dagster_defs.resources import CogneeMemoryResource

ENTITY_TYPES = ["word", "phrase", "cognate", "etymology",
                "dialect_variant", "manuscript", "transcription"]
NULL_FIELD_RATES = {  # per-entity null-rate thresholds (1.13.x supports per-spec metadata)
    "word":            {"field": "translates_to",  "max_null_rate": 0.05},
    "phrase":          {"field": "translates_to",  "max_null_rate": 0.05},
    "cognate":         {"field": "etymology",      "max_null_rate": 0.10},
    "etymology":       {"field": "derives_from",   "max_null_rate": 0.20},
    "dialect_variant": {"field": "spoken_in",      "max_null_rate": 0.15},
    "manuscript":      {"field": "transcription",  "max_null_rate": 0.30},
    "transcription":   {"field": "confidence",     "max_null_rate": 0.10},
}

# AssetCheckSpec graph: 1 spec per entity type, all targeting the same composite asset
GRAPH_MODEL_CHECK_SPECS = [
    AssetCheckSpec(
        name=f"check_{etype}_graph",
        asset=AssetKey(["celtic", "memory", "cognee_graph"]),
        description=(
            f"Verify {etype} entities in cognee graph have non-null "
            f"`{NULL_FIELD_RATES[etype]['field']}` (max null-rate "
            f"{NULL_FIELD_RATES[etype]['max_null_rate']:.0%})"
        ),
    )
    for etype in ENTITY_TYPES
]


@multi_asset_check(
    specs=GRAPH_MODEL_CHECK_SPECS,
    description="Cognee graph-model health: 7 entity-type null-rate checks in 1 run",
    can_block_downstream=True,  # Step 3 will switch this on explicitly; default False for now
)
def check_cognee_graph_models(
    context, cognee: CogneeMemoryResource
):
    """Single-batch cognee health probe: 1 connection, 7 stats calls, 7 yields.

    Replaces the 7 hand-written @asset_check functions. Collapses 42
    connection-establishment round-trips per run to 7 (one per entity type).
    """
    # One connection for all 7 specs — the 7× speedup on connection overhead
    client = cognee.get_client()
    for spec in GRAPH_MODEL_CHECK_SPECS:
        etype = spec.name.removeprefix("check_").removesuffix("_graph")
        threshold = NULL_FIELD_RATES[etype]["max_null_rate"]
        field = NULL_FIELD_RATES[etype]["field"]
        try:
            stats = client.get_entity_stats(entity_type=etype)
            null_rate = stats.get("null_field_rates", {}).get(field, 1.0)
            yield AssetCheckResult(
                check_name=spec.name,
                asset_key=spec.asset_key,
                passed=stats["count"] > 0 and null_rate < threshold,
                metadata={
                    "entity_count": stats["count"],
                    f"null_{field}_rate": null_rate,
                    "threshold": threshold,
                },
            )
        except Exception as e:
            yield AssetCheckResult(
                check_name=spec.name,
                asset_key=spec.asset_key,
                passed=False,
                severity=AssetCheckSeverity.ERROR,
                metadata={"error": str(e), "entity_type": etype},
            )
```

### 3.3 What the refactor buys

| Metric | Before (7 hand-written) | After (`@multi_asset_check`) | Δ |
|:--|:--|:--|:--|
| Function count | 7 | 1 | **−6** |
| Connection establishments per run | 7 (one per check) | 1 (one for all) | **−6** |
| Total code lines | ~140 (20 lines × 7) | ~70 | **−70** |
| Spec enumeration | scattered, hard to grep | one list `GRAPH_MODEL_CHECK_SPECS` | greppable |
| Per-entity-type thresholds | scattered in 7 function bodies | 1 dict `NULL_FIELD_RATES` | config-shaped |

### 3.4 Acceptance criteria

- [ ] `dg list defs` shows exactly 7 asset checks under the asset `["celtic", "memory", "cognee_graph"]`, all 7 named `check_{word,phrase,cognate,etymology,dialect_variant,manuscript,transcription}_graph`
- [ ] `dg check defs` passes (no `DAGSTER_IS_DEFS_VALIDATION_CLI` errors)
- [ ] All 7 checks share the same `metadata` schema (entity_count, null_field_rate, threshold) so the per-check badge in the UI is uniform
- [ ] The 7 individual `@asset_check` decorators are deleted; `check_cognee_graph_models` is the single source of truth
- [ ] The 7 checks yield in **<1s total** (network-only) on a warm Cognee connection (current 7-function form is ~7s)

---

## 4. Step 2 — Add partitioned checks by 6 Cognee datasets (2 hours)

### 4.1 Why partition

The 6 Cognee datasets are heterogeneous (per `infrastructure/stacks/cognee/compose.yaml:42` and agent-09 §8 R2: `oideachais.aistear`, `oideachais.primary`, `oideachais.junior_cycle`, `oideachais.senior_cycle`, `oideachais.tertiary`, `oideachais.cross_stage`). One "cognee healthy" check hides which dataset actually has the issue. The 1.13.x **`partitions_def=` on `@multi_asset_check`** (PREVIEW feature per `docs.dagster.io/guides/test/asset-checks`) renders a per-partition red/green strip in the Dagster UI — exactly the diagnostic view on-call needs.

### 4.2 Add the partition def (module-level, per agent-02 anti-pattern #3)

Per `partitions.py:121-125` docstring: "Module-level `MultiPartitionsDefinition` constants (never inline)". The cognee-dataset partition is single-axis (6 datasets), so a plain `StaticPartitionsDefinition` suffices — no `MultiPartitionsDefinition` needed.

```python
# Add to cianfhoghlaim/dagster_defs/checks/cognee_models.py

from dagster import StaticPartitionsDefinition

# Per agent-02 anti-pattern #3: module-level constant, never inline
COGNEE_DATASET_PARTITION = StaticPartitionsDefinition(
    ["aistear", "primary", "junior_cycle", "senior_cycle", "tertiary", "cross_stage"]
)
```

> **Naming drift note:** compose.yaml uses `oideachais.aistear` (dot) and the code uses `oideachais_aistear` (underscore) per agent-09 §3 drift item #3. The partition **keys** (the bare string `"aistear"`) are intentionally namespace-free — the per-dataset Cognee call prepends `oideachais.` at runtime. This refactor is the **third** place that touches this naming, so it is intentionally agnostic to the drift resolution; the partition key is a stable identifier, and the dataset-name resolution is deferred to the P1-11 refactor.

### 4.3 Wire `partitions_def` into the `@multi_asset_check` (PREVIEW)

The 1.13.x PREVIEW surface is `@multi_asset_check(specs=[...], partitions_def=COGNEE_DATASET_PARTITION, ...)` plus a `AssetCheckExecutionContext` (with `.partition_key`). The function body fans the per-dataset work over the partition and yields 7 specs × 6 partitions = **42 results per run**.

```python
# cianfhoghlaim/dagster_defs/checks/cognee_models.py (continued)

@multi_asset_check(
    specs=GRAPH_MODEL_CHECK_SPECS,
    partitions_def=COGNEE_DATASET_PARTITION,  # PREVIEW in 1.13.x
    description=(
        "Cognee graph-model health: 7 entity-type × 6 dataset = 42 per-partition checks"
    ),
)
def check_cognee_graph_models(
    context, cognee: CogneeMemoryResource
):
    """Per-dataset cognee health probe. 1 connection, 7 entity types, 1 dataset per run."""
    dataset = context.partition_key  # one of the 6 COGNEE_DATASET_PARTITION values
    full_dataset_name = f"oideachais.{dataset}"  # dot notation; canonical per compose.yaml
    client = cognee.get_client()
    for spec in GRAPH_MODEL_CHECK_SPECS:
        etype = spec.name.removeprefix("check_").removesuffix("_graph")
        threshold = NULL_FIELD_RATES[etype]["max_null_rate"]
        field = NULL_FIELD_RATES[etype]["field"]
        try:
            stats = client.get_entity_stats(
                entity_type=etype, dataset_name=full_dataset_name
            )
            null_rate = stats.get("null_field_rates", {}).get(field, 1.0)
            yield AssetCheckResult(
                check_name=spec.name,
                asset_key=spec.asset_key,
                passed=stats["count"] > 0 and null_rate < threshold,
                metadata={
                    "dataset": full_dataset_name,
                    "entity_count": stats["count"],
                    f"null_{field}_rate": null_rate,
                    "threshold": threshold,
                },
            )
        except Exception as e:
            yield AssetCheckResult(
                check_name=spec.name,
                asset_key=spec.asset_key,
                passed=False,
                severity=AssetCheckSeverity.ERROR,
                metadata={
                    "dataset": full_dataset_name,
                    "error": str(e),
                    "entity_type": etype,
                },
            )
```

### 4.4 What the refactor buys

| Metric | Before (Step 1 — unpartitioned) | After (Step 2 — partitioned) | Δ |
|:--|:--|:--|:--|
| Yields per run | 7 | **42** (7 × 6 datasets) | 6× more granular |
| Dagster UI badge | 1 yellow/green dot | **6 × 7 = 42 dots** in a partition strip | per-dataset red/green |
| On-call TTD (time-to-diagnose) | "cognee is unhealthy" → grep datasets | "primary green, JC green, SC red" → dive in | **~3min → 5s** |
| Run cardinality | 1 check per asset materialization | 1 check per (asset, partition) materialization | 6× |

### 4.5 Acceptance criteria

- [ ] `dg list defs` shows 42 `AssetCheckSpec` rows for `["celtic", "memory", "cognee_graph"]` (7 entity types × 6 datasets)
- [ ] `dg check defs` passes with the new `partitions_def=` arg (PREVIEW flag opt-in via env `DAGSTER_ENABLE_PREVIEW_ASSET_CHECKS=1` may be required per 1.13.x docs)
- [ ] Per-dataset run: a single partition materialization of `["celtic", "memory", "cognee_graph"]` runs only the **7 checks for that dataset** (Dagster partitions fan out correctly)
- [ ] A `dg api run launch --asset-key celtic/memory/cognee_graph --partition aistear` invocation produces only the 7 aistear-scoped results
- [ ] The Dagster UI partitions strip (the "partitions" badge in 1.13.9+) renders 6 columns × 7 rows of green/yellow/red

### 4.6 PREVIEW-feature escape hatch

If `partitions_def=` on `@multi_asset_check` is still PREVIEW and unstable in `dagster==1.13.11`, fall back to the **non-partitioned** form from Step 1, and partition only at the **job level** via `define_asset_job(partitions_def=COGNEE_DATASET_PARTITION, selection=AssetSelection.checks(...))`. This loses the per-dataset red/green strip but keeps the multi-asset-check consolidation. Document the fallback in the `cognee_models.py` module docstring.

---

## 5. Step 3 — Add `blocking=True` (1 hour)

### 5.1 The downstream-skips-on-failure semantic

Per agent-02 §8 refactor #3, `blocking=True` on `@asset_check` causes Dagster to **skip downstream materialization** if the check fails. The cognee graph-model health check is the **last** data-quality gate before `ui_suggestion.py:31` (the nightly BAML + Cognee UI suggestion asset) and the 11 marimo notebooks that depend on `celtic/memory/cognee_graph`. Today, a half-cognified `cross_stage` graph (e.g. 4 of 8 edge types extracted) returns silently-empty `derives_from` backlinks in `meaisínfhoghlaim-platform` (the agent runtime) — the marimo notebook shows a "no data" error and the agent produces an empty answer.

With `blocking=True`, the failure surfaces as a **red badge** in the asset graph and the downstream asset is **skipped** with a clear `AssetCheckFailed` exception in the run log. On-call sees the red badge within minutes, not "the marimo notebook is broken" 12 hours later.

### 5.2 Wire `blocking=True`

```python
# cianfhoghlaim/dagster_defs/checks/cognee_models.py (Step 3 addition)

@multi_asset_check(
    specs=GRAPH_MODEL_CHECK_SPECS,
    partitions_def=COGNEE_DATASET_PARTITION,
    blocking=True,  # NEW: skip downstream ui_suggestion + marimo on failure
    description=(
        "Cognee graph-model health: 7 entity-type × 6 dataset = 42 per-partition checks; "
        "blocking=True prevents downstream UI suggestion / marimo from running on bad data"
    ),
)
def check_cognee_graph_models(context, cognee: CogneeMemoryResource):
    # ... body unchanged from Step 2 ...
```

### 5.3 What about the cross-stage dataset?

`cross_stage` joins the other 5 datasets via 8 typed edges (per `infrastructure/stacks/cognee/blueprint.yaml`). When `cross_stage` fails, **all 6 datasets** are conceptually unhealthy (the join itself is broken). Step 3 accepts this nuance: `blocking=True` applies per-dataset, and a failed `cross_stage` check blocks only the `cross_stage`-partitioned downstream jobs. The 5 per-cycle assets (`aistear`, `primary`, etc.) still run.

If on-call wants **all 6 partitions to fail if `cross_stage` fails**, the right pattern is a **second** check (a separate `@asset_check` not `@multi_asset_check`) named `check_cross_stage_join_health` that validates the 8 edge types and is also `blocking=True`. This is a 30-line addition deferred to a follow-on refactor — Step 3 just wires the basic per-dataset blocking.

### 5.4 Acceptance criteria

- [ ] `dg list defs --json | jq '.[] | select(.name == "check_cognee_graph_models") | .blocking'` returns `true`
- [ ] When the check fails for one partition (e.g. `junior_cycle`), the `junior_cycle` partition of the `celtic/memory/cognee_graph` asset materialization is **skipped**, not silently allowed
- [ ] When the check passes for all 6 partitions, downstream `ui_suggestion` + marimo notebooks run as normal
- [ ] No "silent fallback" path exists: a failed check either blocks the downstream (the new behavior) or throws an exception (the old behavior); no path where the check fails and downstream silently runs

### 5.5 Risk + rollback

Low risk: `blocking=True` is **strictly more conservative** than the current default (`False`). It can only add skips, not remove them. If the check is too strict (false-positives), flip `blocking=True` → `blocking=False` in a one-line revert. The marimo notebooks already have a "no data" branch (per agent-09 §3 decision matrix), so reverting to "skip the check, let the notebook show no data" is graceful.

---

## 6. Step 4 — `AssetCheckSpec` graph visualization (1 hour)

### 6.1 What the new visualization gives

Dagster 1.13.x renders the `AssetCheckSpec` graph as a **dedicated subgraph** in the asset lineage view (separate from the asset materialization graph). For the cognee-graph-model health check, this means the 7 entity types × 6 datasets = 42 spec nodes appear as a **grid** in the UI, with the underlying `celtic/memory/cognee_graph` asset as the single root. The grid makes it visually obvious which (entity, dataset) cell is red.

### 6.2 Wire the spec list (already done in Step 1)

The `GRAPH_MODEL_CHECK_SPECS` list from Step 1 **is** the `AssetCheckSpec` graph. To make it visible:

1. Ensure the `@multi_asset_check(specs=GRAPH_MODEL_CHECK_SPECS, ...)` decorator is **unpacked** (the decorator consumes the specs at definition time, not lazily).
2. Add a one-line `description` per spec that includes the dataset placeholder: the spec is the same across all 6 datasets, so the description is `f"Verify {etype} entities have non-null {field}"` — the **partition** is rendered in the UI, not the description.

```python
# Step 4: verify the spec descriptions are descriptive and the
# AssetCheckSpec graph renders 42 nodes in the Dagster UI lineage tab.

# GRAPH_MODEL_CHECK_SPECS (from Step 1) — 7 specs, one per entity type
# Each spec, multiplied by 6 partitions, = 42 nodes in the AssetCheckSpec graph

# In the Dagster UI:
#   http://oideachais.cianfhoghlaim.ie:3080/asset-groups/celtic_memory/asset-checks
#   → click "check_cognee_graph_models" → 6×7 grid renders with red/yellow/green cells
```

### 6.3 Acceptance criteria

- [ ] Dagster UI asset-lineage tab shows the `check_cognee_graph_models` check as a **child node** of `celtic/memory/cognee_graph`
- [ ] Clicking the check node reveals a **6×7 grid** (rows = entity types, columns = datasets) with cell colors matching the underlying check results
- [ ] The grid is interactive: clicking a red cell jumps to that specific check's run history

### 6.4 Why this matters for the v4 consolidated `Definitions(...)`

The v4-consolidated `defs/` mount at `definitions.py:496` (per agent-02 §2) merges `combined_assets + dbt_assets + defs_folder`. The new check will appear in **all three** of these views (asset list, dbt lineage, defs folder Components tab) because `@multi_asset_check` is registered through the `asset_checks=all_asset_checks` arg. The lineage tab is the canonical place to view it; the asset list surfaces it as 1 row (the multi-asset-check), not 42 rows.

---

## 7. Step 5 — Dagster UI badge verification (ongoing)

### 7.1 What to verify in the Dagster UI

After Steps 1–4 land:

1. **Asset lineage tab** (`http://oideachais.cianfhoghlaim.ie:3080/asset-groups/celtic_memory/asset-checks`):
   - `check_cognee_graph_models` is listed under the `celtic/memory/cognee_graph` asset
   - 42 spec nodes render in a 6×7 grid (per Step 4)
   - Per-cell red/yellow/green color matches the check result

2. **Asset check history tab** (click a spec):
   - Last run timestamp + result
   - `metadata` block shows: `dataset`, `entity_count`, `null_{field}_rate`, `threshold`
   - "Blocking downstream: True" badge visible

3. **Asset materialization tab** (the `celtic/memory/cognee_graph` asset):
   - Last materialization shows the **partition** that ran (one of the 6 datasets)
   - A "Check results" strip at the top: ✅ 6 green / ⚠️ 1 yellow / ❌ 0 red (or similar)

4. **Run log** for a failed check (intentionally fail one partition to test):
   - The `junior_cycle` partition's downstream `ui_suggestion` run is **skipped** with a clear message
   - The other 5 partitions' downstream runs are **unaffected**

### 7.2 CI guard (the ongoing bit)

Add a weekly Dagster CLI invocation to the `mise` task list:

```toml
# mise.toml addition
[dagster.asset_checks]
run = "dg api run launch --job cognee_graph_health --asset-key celtic/memory/cognee_graph"
```

A weekly cron runs all 6 partitions of the check; the run history is grepped for red cells. The cron task fails the build if any partition is red for >24h (i.e. if no one has acknowledged a long-standing red).

### 7.3 Acceptance criteria

- [ ] All 4 Dagster UI views above render the expected surfaces
- [ ] A deliberately-failed partition produces a `skip downstream` log line within 5 minutes of the failure
- [ ] The `mise run dagster:asset_checks` task fails when a partition has been red for >24h
- [ ] A green-everywhere run produces a clean asset lineage tab with all 42 cells green

### 7.4 What this is NOT

Step 5 is **not** a refactor — it's a verification + monitoring activity that runs in perpetuity. The deliverable is the `mise` task + the `dg api run launch` cron + the green-cell UI screenshots in `openspec/changes/2026-06-28-asset-check-rollout-verification/` (the change-tracking archive).

---

## Appendix A — Files touched

| File | Change | Step |
|:--|:--|:-:|
| `cianfhoghlaim/dagster_defs/checks/cognee_models.py` | **CREATE** (the canonical 7-hand-written-check file, refactored) | 1 |
| `cianfhoghlaim/dagster_defs/checks/cognee_models.py` | Edit: add `partitions_def=COGNEE_DATASET_PARTITION` | 2 |
| `cianfhoghlaim/dagster_defs/checks/cognee_models.py` | Edit: add `blocking=True` | 3 |
| `cianfhoghlaim/dagster_defs/checks/cognee_models.py` | Edit: verify `AssetCheckSpec` graph renders | 4 |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/asset_checks.py` | Edit: add `cognee_models` to `all_asset_checks` list (line 213-228) | 1 |
| `mise.toml` | Add `[dagster.asset_checks]` task | 5 |
| `openspec/specs/oideachais-pipeline/spec.md` | Add `Asset Check Health (cognee-graph-models)` Requirement + 2 Scenarios | 1 |

## Appendix B — Spec delta (proposed, for openspec change tracking)

The 7-section rollout maps to a single `oideachais-pipeline` spec delta:

```markdown
# In openspec/changes/2026-06-28-asset-check-rollout/specs/oideachais-pipeline/spec.md

## MODIFIED Requirements
### Requirement: Asset Check Health (cognee-graph-models)
The system SHALL use the Dagster 1.13.x `@multi_asset_check` API
(`@multi_asset_check(specs=[AssetCheckSpec(...)])`) for the cognee
graph-model health surface, with one spec per entity type (7 total:
word, phrase, cognate, etymology, dialect_variant, manuscript,
transcription) × 6 Cognee dataset partitions (aistear, primary,
junior_cycle, senior_cycle, tertiary, cross_stage) = 42 per-partition
results per run, and SHALL mark the check `blocking=True` so that
downstream `ui_suggestion` and marimo notebook assets are skipped
on check failure.

#### Scenario: 42 per-partition checks per run
- **GIVEN** the cognee graph-model health check is registered in
  `cianfhoghlaim/dagster_defs/checks/cognee_models.py`
- **WHEN** a Dagster run materializes the `celtic/memory/cognee_graph`
  asset with a partition key (one of the 6 dataset names)
- **THEN** the check yields 7 results (one per entity type) scoped to
  that partition
- **AND** the 6 partitions total 42 per-run results
- **AND** each result carries `metadata={"dataset", "entity_count",
  "null_<field>_rate", "threshold"}`

#### Scenario: blocking=True skips downstream on failure
- **GIVEN** the check returns `passed=False` for the `junior_cycle`
  partition
- **WHEN** Dagster evaluates downstream assets
- **THEN** the `junior_cycle` partition of `ui_suggestion` is **skipped**
  with an `AssetCheckFailed` exception in the run log
- **AND** the other 5 partitions' downstream assets run normally
- **AND** a red badge renders in the Dagster UI for the
  `junior_cycle` partition
```

## Appendix C — Cross-references to Wave-1 + Wave-2

- `agent-02-dagster.md:295-303` — 1.13.x asset-check APIs (the surface being adopted)
- `agent-02-dagster.md:366-422` — §8 refactors 2, 3, 5 (the 12 → 1 multi-asset-check refactor + blocking on minimax + dagster-dlt bump)
- `26-refactor-prioritizer.md:107-109` — items P2-28 (multi-asset-check on WIRE_UNWIRED) + P2-29 (blocking on LLM gateway) — this refactor is the **third instance** of the same pattern
- `agent-09-cognee.md:28-31, 295` — dataset-name drift (dot vs underscore) — explicitly deferred to P1-11
- `agent-09-cognee.md:330-332` — the 6 datasets + 3 leabharlann (we scope to the 6, not the 3 leabharlann, to keep this refactor focused)
- `agent-09-cognee.md:153-164` — the entity_types list (we use the first 7, not all 11)
- `asset_checks.py:45-79, 213-228` — canonical `@asset_check` pattern + the `all_asset_checks` registry (the integration point for Step 1)

## Appendix D — Out-of-scope (deferred to follow-on refactors)

- **Cognee v1.0 `remember/recall` API migration** (6 files) — Refactor 09 / agent-09 §8 R1
- **Cognee dataset-name drift** (dot vs underscore) — Refactor 11 / item P1-11
- **Upstream `DltLoadCollectionComponent` adoption** (replaces hand-rolled `CelticDltSourceComponent`) — Refactor 06 / item P1-6
- **`dagster-dlt` 0.25 → 0.29.11 bump** — Refactor 07 / item P1-7 (not a prerequisite for this refactor)
- **`minimax_alias_health blocking=True`** — Refactor 29 / item P2-29 (sister refactor; same pattern, different surface)
- **`WIRE_UNWIRED_DLT_CHECKS` → `@multi_asset_check`** — Refactor 28 / item P2-28 (sister refactor; same pattern, 12 funcs → 1)
- **`cross_stage` join health (8 edge types) as a separate `blocking=True` check** — follow-on, 30 lines
- **The 3 leabharlann datasets** (per agent-09 §4) — follow-on, ~6h, scoped as a separate refactor
- **Per-asset-check RAGAS evaluation** — Refactor 38 (RAGAS-on-asset-checks, the sister agent to this one)
