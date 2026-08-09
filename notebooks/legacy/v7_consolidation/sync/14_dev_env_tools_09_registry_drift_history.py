# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.13",
# ]
# ///
"""09 — Registry Drift History.

Interactive marimo notebook that surfaces the drift-count history
for the `centralized-model-registry` capability (the
`scripts/registry_audit.py` audit). Companion to notebook 07 (the
MODEL_REGISTRY explorer) + notebook 08 (the live Registry Drift
Watcher).

This notebook does two things:

1. **Current drift** — re-invokes ``scripts/registry_audit.py --json``
   and renders the drift count + the file list. Same as notebook 08
   but with a focus on the historical trend line.
2. **Drift history** — parses every JSON report under
   ``stedding/sync-reports/`` (the canonical sync-reports directory
   written by the 11 sync-loop layers + the
   ``registry_drift_alert_sensor`` materializations) and plots the
   drift-count trend over time.
3. **Dagster event log** — if ``$DAGSTER_HOME/history`` (or the
   default ``.dagster_home/history``) contains a SQLite event log,
   read the ``asset_materialization`` rows for the
   ``registry/drift_alert`` asset key and append them to the
   trend line.

The notebook wraps the centralized registry imports in the same
``try/except`` block as the other 14_dev_env_tools_*.py notebooks so
it can be opened from any working directory.

See also:
- `.agents/skills/centralized-registry/SKILL.md`
- `openspec/specs/centralized-model-registry/spec.md`
- `scripts/registry_audit.py` (the drift detector)
- `orchestration/defs/sync_assets.py:registry_drift_alert`
- `notebooks/14_dev_env_tools_07_model_registry.py` (companion)
- `notebooks/14_dev_env_tools_08_registry_drift_watch.py` (companion)
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium", app_title="Registry Drift History")


# Centralized registries (per the `centralized-model-registry` capability).
# Same try/except block as the rest of the 14_dev_env_tools_*.py notebooks.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0


@app.cell
def header(mo):
    mo.md(
        f"""
        # Registry Drift History

        Trend-line view of the centralized-model-registry drift
        count over time. Combines two data sources:

        1. **`stedding/sync-reports/*.json`** — the canonical
           sync-report directory written by the 11 sync-loop layers.
           Each report carries a `generated_at` timestamp + a
           `ground_truth.models` field that, when compared to
           `MODEL_REGISTRY.summary().total`, surfaces drift.
        2. **Dagster event log** (optional) — the
           `registry/drift_alert` `AssetMaterialization` rows
           recorded by the `registry_drift_alert_sensor` in
           `orchestration/defs/sync_assets.py`.

        The live drift count is re-derived via
        `scripts/registry_audit.py --json` (the canonical drift
        detector, the same call that powers the
        `registry_drift_alert_sensor`).

        **Current registry snapshot** (from `MODEL_REGISTRY.summary()`):

        | Metric | Value |
        |:--|:--|
        | Total entries | **{_REGISTRY_SUMMARY.get('total', 0)}** |
        | Available | **{_REGISTRY_SUMMARY.get('available', 0)}** |
        | Deprecated | **{_REGISTRY_SUMMARY.get('deprecated', 0)}** |
        | Default LLM | `{_DEFAULT_LLM}` |
        | DLT sources | {_DLT_SOURCE_COUNT} |
        | CocoIndex Apps | {_COCO_APP_COUNT} |
        | BAML classes | {_BAML_CLASS_COUNT} |
        """
    )
    return


@app.cell
def current_drift(mo, subprocess, Path, json, datetime, timezone):
    """Re-invoke `scripts/registry_audit.py --json` to get the live drift count."""
    REPO_ROOT = Path(__file__).resolve().parents[1]
    AUDIT_SCRIPT = REPO_ROOT / "scripts" / "registry_audit.py"

    _payload: dict = {"findings": [], "count": 0}
    _error: str | None = None

    if AUDIT_SCRIPT.exists():
        try:
            _proc = subprocess.run(
                ["python3", str(AUDIT_SCRIPT), "--json"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                timeout=120,
            )
            _payload = json.loads(_proc.stdout) if _proc.stdout else _payload
        except Exception as e:  # noqa: BLE001 — dev fallback
            _error = f"audit_failed: {e}"

    _count = _payload.get("count", 0)
    _findings = _payload.get("findings", [])
    _last_check = datetime.now(timezone.utc).isoformat()

    _status = (
        "✅ **0 drift** — `mise run lint:registry` will pass"
        if _count == 0
        else f"⚠️ **{_count} hardcoded model strings** — CI gate fails"
    )
    _error_block = f"\n\n> Audit error: `{_error}`" if _error else ""

    mo.md(
        f"""
        ## Current drift (live)

        | Metric | Value |
        |:--|:--|
        | Drift count | **{_count}** |
        | Last check | `{_last_check}` |
        | Status | {_status} |
        | Audit script | `{AUDIT_SCRIPT.name}` |
        {_error_block}

        {"**Top files:**" if _findings else ""}
        {chr(10).join(f"- `{f.get('file', '?')}:{f.get('lineno', '?')}` — `{f.get('match', '?')}`" for f in _findings[:5]) if _findings else ""}
        """
    )
    return _count, _findings


@app.cell
def drift_history(mo, Path, json):
    """Parse `stedding/sync-reports/*.json` for the drift-count trend.

    The 2 existing files (docs-drift-2026-07-29.json +
    docs-drift-2026-07-30.json) carry `ground_truth.models` + a
    `generated_at` timestamp. We treat any delta between
    `ground_truth.models` and the canonical
    `MODEL_REGISTRY.summary().total` as a proxy for the registry
    drift history.
    """
    REPORTS_DIR = Path("stedding/sync-reports")
    _rows: list[dict] = []
    _parse_error: str | None = None

    if not REPORTS_DIR.is_dir():
        _parse_error = f"`{REPORTS_DIR}/` does not exist — run `mise run sync:all` to generate the first report"
    else:
        for _p in sorted(REPORTS_DIR.glob("*.json")):
            try:
                _d = json.loads(_p.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                continue
            _generated = _d.get("generated_at") or _d.get("checked_at")
            _truth = _d.get("ground_truth") or {}
            _models_truth = _truth.get("models")
            if _generated and _models_truth is not None:
                _rows.append({
                    "file": _p.name,
                    "generated_at": _generated,
                    "ground_truth_models": int(_models_truth),
                    "violations": (_d.get("summary") or {}).get("violations", 0),
                })

    if _parse_error:
        mo.md(f"## Drift history\n\n> {_parse_error}\n")
        return

    if not _rows:
        mo.md(
            "## Drift history\n\n"
            "**No drift-history rows found in `stedding/sync-reports/`.**\n"
            "Run `mise run sync:all` or `mise run lint:drift-docs` to populate."
        )
        return

    _table = "\n".join(
        f"| `{r['file']}` | `{r['generated_at']}` | {r['ground_truth_models']} | {r['violations']} |"
        for r in _rows[-15:]
    )
    _latest_models = _rows[-1]["ground_truth_models"]
    _drift_proxy = max(0, _latest_models - _REGISTRY_SUMMARY.get("total", 0))

    mo.md(
        f"""
        ## Drift history (last {min(15, len(_rows))} of {len(_rows)} sync-reports)

        Proxy: each row reports the `ground_truth.models` field the
        sync loop found. A delta vs the current
        `MODEL_REGISTRY.summary().total` ({_REGISTRY_SUMMARY.get('total', 0)})
        is a drift signal.

        | File | Generated | Models | Violations |
        |:--|:--|--:|--:|
        {_table}

        **Drift proxy (latest vs current):** `{_drift_proxy}` (negative
        values are suppressed to 0).
        """
    )
    return _rows


@app.cell
def dagster_event_log(mo, Path, sqlite3, json, datetime, timezone):
    """Read the Dagster event log (if a local `history` directory exists).

    Dagster stores run history as one SQLite file per run under
    `$DAGSTER_HOME/history/<run_id>/<step_key>.db`. We look for any
    `AssetMaterialization` rows that mention
    `["registry", "drift_alert"]` in their `asset_key` column.
    """
    _candidates = [
        Path("stedding/dagster_home/history"),
        Path("~/.dagster_home/history").expanduser(),
        Path("/tmp/dagster_home/history"),
    ]
    _history_root = next((p for p in _candidates if p.is_dir()), None)

    if not _history_root:
        mo.md(
            """
            ## Dagster event log

            **No Dagster event log found** (looked for
            `stedding/dagster_home/history`, `~/.dagster_home/history`,
            `/tmp/dagster_home/history`). The trend line in the previous
            cell is sourced from `stedding/sync-reports/*.json` only.

            To enable this view, run `mise run dagster:dev` to
            generate the first batch of `AssetMaterialization` rows.
            """
        )
        return

    _rows: list[dict] = []
    for _db_path in _history_root.rglob("*.db"):
        try:
            with sqlite3.connect(str(_db_path)) as _con:
                _cur = _con.execute(
                    """
                    SELECT timestamp, event_json
                    FROM asset_materialization_event_logs
                    WHERE asset_key LIKE '%registry%drift_alert%'
                    ORDER BY timestamp ASC
                    """
                )
                for _ts, _event_json in _cur.fetchall():
                    try:
                        _ev = json.loads(_event_json)
                    except Exception:  # noqa: BLE001
                        continue
                    _metadata = _ev.get("metadata", {})
                    _drift = _metadata.get("drift_count")
                    if _drift is not None:
                        _rows.append({
                            "ts": _ts,
                            "iso": datetime.fromtimestamp(
                                _ts, tz=timezone.utc
                            ).isoformat() if _ts else "?",
                            "drift_count": int(_drift),
                        })
        except Exception:  # noqa: BLE001
            continue

    if not _rows:
        mo.md(
            f"""
            ## Dagster event log

            Looked under `{_history_root}` — **0 `registry/drift_alert`
            materializations found**. The first materialization will
            appear after the next `registry_drift_alert_sensor` tick
            (1-hour cadence per `orchestration/defs/sync_assets.py`).
            """
        )
        return

    _table = "\n".join(
        f"| `{r['iso']}` | {r['drift_count']} |"
        for r in _rows[-15:]
    )
    mo.md(
        f"""
        ## Dagster event log (last {min(15, len(_rows))} of {len(_rows)} materializations)

        Source: `{_history_root}/**/*.db` (the canonical Dagster
        run-history root).

        | Timestamp | Drift count |
        |:--|--:|
        {_table}
        """
    )
    return _rows


@app.cell
def registry_summary(mo):
    mo.md(
        """
        ## 4 canonical artifacts (the centralized registries)

        | Artifact | Path | Purpose |
        |:--|:--|:--|
        | `MODEL_REGISTRY` | `meaisinfhoghlaim/models/model_registry.py` | 52 entries across 7 families. |
        | `schema` introspection | `notebooks/_shared/schema.py` | 5 helpers (`schema_introspect`, `list_dlt_sources`, `list_cocoindex_apps`, `list_baml_classes`, `schema_introspect_full`). |
        | `deployment-choice.yaml` | repo root | The canonical enablement file (models / pipelines / datasets / stacks). |
        | `00_control_panel` notebook | `notebooks/00_control_panel.py` | The 5-tab marimo control panel (the operator's UI). |

        ## Companion notebooks

        - `notebooks/14_dev_env_tools_07_model_registry.py` — the
          MODEL_REGISTRY explorer (52 entries, filter by family +
          role + language).
        - `notebooks/14_dev_env_tools_08_registry_drift_watch.py` —
          the live drift watcher (re-runs `registry_audit.py` on
          every cell re-evaluation).
        - `notebooks/00_control_panel.py` — the 5-tab control
          panel.

        **Audit**: `mise run lint:registry --strict` is the canonical
        CI gate. The `pre-commit` hook in `.pre-commit-config.yaml`
        runs the same audit on every commit.
        """
    )
    return


if __name__ == "__main__":
    app.run()
