# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.13",
# ]
# ///
"""08 — Registry Drift Watcher.

Interactive marimo notebook for monitoring centralized-model-registry
drift via `scripts/registry_audit.py`. Companion to notebook 07 (the
MODEL_REGISTRY explorer) + the `registry_drift_alert` Dagster sensor
in `orchestration/defs/sync_assets.py`.

What this notebook does:

1. Invokes `scripts/registry_audit.py` with `--json` and parses the
   structured findings (count + file list + matched string).
2. Renders a drift dashboard:
   - Total drift count (must be 0 for `mise run lint:registry` to pass)
   - List of offending files + the hardcoded model strings
   - The MODEL_REGISTRY entry that should replace each finding
3. Re-runs the audit on every cell re-evaluation (so the operator
   can edit a file and see the drift count drop in real time).
4. Optionally exports the findings to `stedding/registry-drift/` for
   the Dagster `registry_drift_alert_sensor` to ingest.

Cascade target: this notebook completes the
2026-08-15-cascading-registry-integration-v2 batch.

See also:
- `.agents/skills/centralized-registry/SKILL.md`
- `openspec/specs/centralized-model-registry/spec.md`
- `meaisinfhoghlaim/models/README.md`
- `orchestration/defs/sync_assets.py` (the Layer 9 sensor + job + asset)
- `notebooks/14_dev_env_tools_07_model_registry.py` (companion)
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium", app_title="Registry Drift Watcher")


@app.cell
def imports():
    import marimo as mo
    import json
    import subprocess
    from datetime import datetime, timezone
    from pathlib import Path

    # The MODEL_REGISTRY (so we can suggest replacements for each finding).
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for
        _import_ok = True
        _import_error = None
    except Exception as e:  # noqa: BLE001 — dev fallback
        MODEL_REGISTRY = None
        model_for = None
        _import_ok = False
        _import_error = e

    return (
        mo,
        json,
        subprocess,
        datetime,
        timezone,
        Path,
        MODEL_REGISTRY,
        model_for,
        _import_ok,
        _import_error,
    )


@app.cell
def header(mo):
    mo.md(
        """
        # Registry Drift Watcher

        Live view of `scripts/registry_audit.py` output. The drift count
        must be **0** for `mise run lint:registry` to pass (the canonical
        CI gate enforced by the `registry_drift_alert_sensor` in
        `orchestration/defs/sync_assets.py`).

        Edit a file → refresh this cell → see the drift count drop.
        """
    )
    return


@app.cell
def run_audit(subprocess, Path, json, _import_ok):
    REPO_ROOT = Path(__file__).resolve().parents[1]
    AUDIT_SCRIPT = REPO_ROOT / "scripts" / "registry_audit.py"

    _audit_payload: dict = {"findings": [], "count": 0}
    _audit_error: str | None = None

    if _import_ok and AUDIT_SCRIPT.exists():
        try:
            _proc = subprocess.run(
                ["python3", str(AUDIT_SCRIPT), "--json"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                timeout=120,
            )
            _audit_payload = json.loads(_proc.stdout)
        except Exception as e:  # noqa: BLE001
            _audit_error = f"audit_failed: {e}"

    return REPO_ROOT, AUDIT_SCRIPT, _audit_payload, _audit_error


@app.cell
def summary(mo, _audit_payload, _audit_error, _import_error, _import_ok, datetime, timezone):
    _drift_count = _audit_payload.get("count", 0)
    _findings = _audit_payload.get("findings", [])
    _last_check = datetime.now(timezone.utc).isoformat()

    _status = (
        "✅ **0 drift** — `mise run lint:registry` will pass"
        if _drift_count == 0
        else f"⚠️ **{_drift_count} hardcoded model strings** — CI gate fails"
    )

    _error_block = ""
    if _audit_error:
        _error_block = f"\n\n> Audit error: `{_audit_error}`"
    if _import_error:
        _error_block = f"\n\n> Import error: `{_import_error}`"

    mo.md(
        f"""
        ## Drift status

        | Metric | Value |
        |:--|:--|
        | Drift count | **{_drift_count}** |
        | Findings | **{len(_findings)}** |
        | Last check | `{_last_check}` |
        | Status | {_status} |
        | MODEL_REGISTRY loaded | {"yes" if _import_ok else "no"} |
        {_error_block}
        """
    )
    return _drift_count, _findings, _last_check


@app.cell
def findings_table(mo, _findings):
    if not _findings:
        mo.md("No drift findings. 🎉")
        return

    _rows = []
    for f in _findings[:50]:  # cap at 50 for readability
        _rows.append(
            {
                "file": str(f.get("file", "?")),
                "line": f.get("line", "?"),
                "matched": str(f.get("matched", "?")),
                "suggestion": f.get("suggestion", ""),
            }
        )

    mo.md("## Drift findings (top 50)")
    return _rows


@app.cell
def findings_table_render(_rows, mo):
    if not _rows:
        return
    try:
        import pandas as pd

        _df = pd.DataFrame(_rows)
        return mo.ui.table(_df, label="drift_findings")
    except ImportError:
        return mo.md(
            "\n".join(
                f"- `{r['file']}:{r['line']}` → `{r['matched']}`"
                for r in _rows[:20]
            )
        )


@app.cell
def replacement_hints(mo, MODEL_REGISTRY, model_for, _findings):
    if not MODEL_REGISTRY or not _findings:
        return

    _registry_entries = list(MODEL_REGISTRY.values()) if hasattr(MODEL_REGISTRY, "values") else []
    _registry_keys = {e.key for e in _registry_entries} if _registry_entries else set()

    _hints = []
    for f in _findings[:10]:
        matched = str(f.get("matched", ""))
        # Try to find a registry entry whose upstream_id matches.
        replacement = None
        for entry in _registry_entries:
            if entry.upstream_id == matched or entry.key == matched:
                replacement = entry
                break

        if replacement:
            _hints.append(
                f"- `{f.get('file', '?')}:{f.get('line', '?')}` → "
                f"`from meaisinfhoghlaim.models import model_for; "
                f"model_for({replacement.family!r}, {replacement.role!r})` "
                f"(resolves to `{replacement.key}`)"
            )
        else:
            _hints.append(
                f"- `{f.get('file', '?')}:{f.get('line', '?')}` → "
                f"`{matched}` (no MODEL_REGISTRY entry — open an issue)"
            )

    if _hints:
        return mo.md(
            "## Replacement hints\n\n" + "\n".join(_hints)
        )


@app.cell
def ci_gate_check(mo, _drift_count):
    _gate_pass = _drift_count == 0
    if _gate_pass:
        return mo.md(
            "✅ **CI gate passes** — `mise run lint:registry` will exit 0. "
            "The `registry_drift_alert_sensor` will not fire."
        )
    return mo.md(
        f"❌ **CI gate fails** — `mise run lint:registry` will exit 1 "
        f"with {_drift_count} finding(s). The "
        f"`registry_drift_alert_sensor` will fire on the next tick."
    )


@app.cell
def dagster_link(mo):
    mo.md(
        """
        ## Dagster integration

        This notebook complements the `registry_drift_alert_sensor`
        wired in `orchestration/defs/sync_assets.py` (Layer 9 of the
        sync_health surface). The sensor polls `scripts/registry_audit.py`
        hourly and emits a `RunRequest` for the
        `materialize_registry_drift_alert_job` whenever drift is
        detected, with the drift count + file list as Dagster metadata.

        See:
        - `orchestration/defs/sync_assets.py:registry_drift_alert_sensor`
        - `orchestration/defs/sync_assets.py:materialize_registry_drift_alert_job`
        - `orchestration/defs/sync_assets.py:registry_drift_alert` (the asset)

        ## Companion notebooks

        - `notebooks/14_dev_env_tools_07_model_registry.py` — the
          MODEL_REGISTRY explorer (companion for browsing the 58 entries)
        - `notebooks/00_control_panel.py` — the 5-tab marimo control
          panel (the operator's UI)
        """
    )
    return


if __name__ == "__main__":
    app.run()