from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""Cianfhoghlaim Deployment Control Panel — 5-tab marimo.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
Reference: openspec/specs/deployment-control-panel/spec.md

The single marimo control panel that surfaces the
``deployment-choice.yaml`` enablement file as a 5-tab interactive UI.
Each tab reads from and writes to the canonical deployment-choice
via ``notebooks._shared.schema:read_deployment_choice() /
write_deployment_choice()``.

The 5 tabs:

  Tab 1. **Models** — every ``MODEL_REGISTRY`` entry grouped by
    family (ocr_vision / text_llm / embedder / rerank / image_gen
    / voice / translation). Toggle on/off.

  Tab 2. **Pipelines** — every DLT source (from
    ``list_dlt_sources()``) + every CocoIndex App (from
    ``list_cocoindex_apps()``). Toggle on/off.

  Tab 3. **Datasets** — read-only table showing every BIEP DuckDB
    table + LanceDB mount + BAML class (from
    ``schema_introspect_full()``).

  Tab 4. **Stacks** — every Docker Compose stack in
    ``bonneagar/stacks/``. Toggle on/off.

  Tab 5. **Registry** — full ``MODEL_REGISTRY`` view + drift count
    from ``mise run lint:registry``.

Run with:

    marimo edit notebooks/00_control_panel.py

    # Or via the mise task:
    mise run notebook:control-panel
"""

import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium", app_title="Cianfhoghlaim Control Panel")


@app.cell
def imports():
    import marimo as mo
    import sys
    sys.path.insert(0, ".")
    sys.path.insert(0, "notebooks/_shared")

    import pandas as pd
    import yaml
    from pathlib import Path
    from typing import Any

    # The 5 introspection helpers (Phase 0/3)
    import schema as schema_module
    from schema import (
        schema_introspect,
        schema_introspect_full,
        schema_introspect_table,
        list_dlt_sources,
        list_cocoindex_apps,
        list_baml_classes,
        read_deployment_choice,
        write_deployment_choice,
        deployment_choice_path,
    )

    # The unified MODEL_REGISTRY (Phase 0/1)
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for, filter_models

    # The shared lakehouse connection (Phase 3)
    from db import connect_md, LAKEHOUSE_URI_DEFAULT

    return (
        MODEL_REGISTRY,
        connect_md,
        deployment_choice_path,
        filter_models,
        list_baml_classes,
        list_cocoindex_apps,
        list_dlt_sources,
        mo,
        pd,
        read_deployment_choice,
        schema_introspect_full,
        write_deployment_choice,
    )


@app.cell
def intro(mo):
    mo.md(f"""
    # Cianfhoghlaim Deployment Control Panel

    The single source of truth for what models, pipelines, datasets,
    and stacks are currently enabled in this deployment.

    All 5 tabs read from and write to
    `deployment-choice.yaml` at the repo root. The same file is
    shared with the **web UI control panel** (`web/apps/...
    /control-panel/`) and the **CLI** (`scripts/cianfhoghlaim-cli.ts`).

    Use the 5 tabs to:
    1. **Models** — toggle AI/LLM/VLM models on/off
    2. **Pipelines** — toggle DLT sources + CocoIndex Apps on/off
    3. **Datasets** — inspect BIEP DuckDB tables + LanceDB mounts + BAML classes
    4. **Stacks** — toggle Docker Compose stacks on/off
    5. **Registry** — inspect the full `MODEL_REGISTRY` + drift count
    """)
    return


@app.cell
def load_state(MODEL_REGISTRY_entries, read_deployment_choice):
    # Load the current deployment-choice.yaml
    state = read_deployment_choice()
    if not state:
        # First boot — empty. Use MODEL_REGISTRY defaults.
        state = {
            "version": 1,
            "enabled_models": {
                e.key: e.available
                for e in MODEL_REGISTRY_entries()
            },
            "enabled_pipelines": {},
            "enabled_datasets": {},
            "enabled_stacks": {},
            "monitoring": {
                "registry_audit": True,
                "baml_ts_codegen": True,
            },
        }
    return (state,)


@app.cell
def MODEL_REGISTRY_entries():
    # Cache the full MODEL_REGISTRY entries (used by Tab 1 + Tab 5)
    return


@app.cell
def tab_models(filter_models, mo, pd, state, write_deployment_choice):
    """Tab 1: Models — toggle every MODEL_REGISTRY entry on/off."""
    # Group entries by family
    fam_models = filter_models("ocr_vision") + filter_models("text_llm") + \
        filter_models("embedder") + filter_models("rerank") + \
        filter_models("image_gen") + filter_models("voice") + \
        filter_models("translation")

    # Build the marimo table view
    rows = []
    for e in fam_models:
        rows.append({
            "enabled": state.get("enabled_models", {}).get(e.key, True),
            "key": e.key,
            "family": e.family,
            "role": e.role,
            "display_name": e.display_name,
            "upstream_id": e.upstream_id,
            "backend": e.backend,
            "available": e.available,
        })
    df = pd.DataFrame(rows)

    # Build the marimo checkbox grid
    summary = mo.md(
        f"""
        ## Tab 1. Models ({len(fam_models)} entries across 7 families)

        Total enabled: **{sum(state.get('enabled_models', {}).values())}**
        | Total disabled: **{sum(1 for v in state.get('enabled_models', {}).values() if not v)}**
        | Deprecated (always off): **{sum(1 for e in fam_models if not e.available)}**

        Toggle entries via the checkbox grid below; changes write back
        to `deployment-choice.yaml`.
        """
    )

    # Simple checkbox grid (one checkbox per entry, grouped by family)
    family_checkboxes = {}
    for fam in ("ocr_vision", "text_llm", "embedder", "rerank", "image_gen", "voice", "translation"):
        fam_entries = filter_models(fam)
        family_checkboxes[fam] = mo.ui.multiselect(
            options=[e.key for e in fam_entries],
            value=[
                k for k, v in state.get("enabled_models", {}).items()
                if v and k in {e.key for e in fam_entries}
            ],
            label=f"{fam} ({len(fam_entries)} entries)",
        )

    controls = mo.vstack([
        family_checkboxes["ocr_vision"],
        family_checkboxes["text_llm"],
        family_checkboxes["embedder"],
        family_checkboxes["rerank"],
        family_checkboxes["image_gen"],
        family_checkboxes["voice"],
        family_checkboxes["translation"],
    ])

    save_button = mo.ui.button(
        label="Save to deployment-choice.yaml",
        kind="success",
        on_click=lambda _: _save_models(
            family_checkboxes, state, write_deployment_choice,
        ),
    )
    return


@app.cell
def tab_pipelines(
    list_cocoindex_apps,
    list_dlt_sources,
    mo,
    pd,
    state,
    write_deployment_choice,
):
    """Tab 2: Pipelines — toggle DLT sources + CocoIndex Apps."""
    dlt_rows = list_dlt_sources()
    coco_rows = list_cocoindex_apps()

    dlt_df = pd.DataFrame(dlt_rows)
    coco_df = pd.DataFrame(coco_rows)

    summary = mo.md(
        f"""
        ## Tab 2. Pipelines

        - **DLT sources**: {len(dlt_rows)} (across `dlt_sources/`)
        - **CocoIndex Apps**: {len(coco_rows)} (across `cocoindex/`)

        Toggle entries via the multiselects below; changes write back
        to `deployment-choice.yaml`.
        """
    )

    # DLT multiselect
    dlt_names = sorted({r["source_name"] for r in dlt_rows})
    dlt_checkbox = mo.ui.multiselect(
        options=dlt_names,
        value=[
            k for k, v in state.get("enabled_pipelines", {}).items()
            if v and k in set(dlt_names)
        ],
        label=f"Enabled DLT sources ({len(dlt_names)} candidates)",
    )

    # CocoIndex multiselect
    coco_names = sorted({r["app_name"] for r in coco_rows if r["app_name"]})
    coco_checkbox = mo.ui.multiselect(
        options=coco_names,
        value=[
            k for k, v in state.get("enabled_pipelines", {}).items()
            if v and k in set(coco_names)
        ],
        label=f"Enabled CocoIndex Apps ({len(coco_names)} candidates)",
    )

    save_button = mo.ui.button(
        label="Save to deployment-choice.yaml",
        kind="success",
        on_click=lambda _: _save_pipelines(
            dlt_checkbox, coco_checkbox, state, write_deployment_choice,
        ),
    )
    return


@app.cell
def tab_datasets(connect_md, mo, pd, schema_introspect_full):
    """Tab 3: Datasets — read-only introspection of every BIEP table."""
    summary = mo.md(
        """
        ## Tab 3. Datasets (read-only)

        Every BIEP DuckDB table + every LanceDB mount + every BAML
        class. Data populated from `schema_introspect_full()`.

        Note: this tab does NOT modify `deployment-choice.yaml`.
        """
    )

    # Connect to the lakehouse (or fall back to :memory:)
    try:
        conn = connect_md()
    except Exception:
        conn = None

    # Get all introspection rows
    rows = schema_introspect_full(conn)
    if rows:
        df = pd.DataFrame(rows)
    else:
        df = pd.DataFrame([{
            "schema_name": "<no lakehouse connection>",
            "table_name": "(connect to MotherDuck or local DuckLake)",
            "column_name": "",
            "column_type": "",
            "source": "metadata_only",
        }])

    # Source breakdown
    by_source = df["source"].value_counts().to_dict() if "source" in df.columns else {}

    source_summary = mo.md(
        f"""
        ### Source breakdown
        - **DuckDB** (BIEP tables): {by_source.get('duckdb', 0)} columns
        - **LanceDB** (vector mounts): {by_source.get('lance', 0)} columns
        - **BAML** (typed classes): {by_source.get('baml', 0)} columns

        Showing the first 200 rows.
        """
    )
    return


@app.cell
def tab_stacks(mo, state, write_deployment_choice):
    """Tab 4: Stacks — toggle Docker Compose stacks on/off."""
    summary = mo.md(
        """
        ## Tab 4. Stacks

        Toggle Docker Compose stacks in `bonneagar/stacks/*`. The full
        inventory comes from `bonneagar/stacks/INDEX.md` (auto-generated
        by stack-doctor) — only the high-priority stacks are listed
        below.

        For the full list, run: `bun run cianfhoghlaim stacks list`.
        """
    )

    HIGH_PRIORITY_STACKS = [
        "litellm", "langfuse", "mlflow", "cognee", "graphiti",
        "lakehouse", "openclaw", "openchamber", "hermes",
        "dagster", "motherduck", "lancedb", "falkordb", "memgraph",
        "locket", "komodo", "pangolin", "infisical",
    ]

    stack_checkbox = mo.ui.multiselect(
        options=HIGH_PRIORITY_STACKS,
        value=[
            k for k, v in state.get("enabled_stacks", {}).items()
            if v and k in set(HIGH_PRIORITY_STACKS)
        ],
        label=f"High-priority stacks ({len(HIGH_PRIORITY_STACKS)})",
    )

    save_button = mo.ui.button(
        label="Save to deployment-choice.yaml",
        kind="success",
        on_click=lambda _: _save_stacks(
            stack_checkbox, state, write_deployment_choice,
        ),
    )
    return


@app.cell
def tab_registry(MODEL_REGISTRY, filter_models, list_baml_classes, mo, pd):
    """Tab 5: Registry — full MODEL_REGISTRY view + drift warnings +
    memory-doctor surface (added by the 2026-08-15-lakehouse-memory-stack
    change so operators have a one-click link to the 5-backend doctor).
    """
    summary = mo.md(
        """
        ## Tab 5. Registry

        The full `MODEL_REGISTRY` view + drift count (run
        `mise run lint:registry` for the canonical check) + the
        memory-stack doctor shortcut.
        """
    )

    # By family summary
    fam_rows = []
    for fam in ("ocr_vision", "text_llm", "embedder", "rerank",
                "image_gen", "voice", "translation"):
        entries = filter_models(fam)
        available = sum(1 for e in entries if e.available)
        fam_rows.append({
            "family": fam,
            "total": len(entries),
            "available": available,
            "deprecated": len(entries) - available,
        })
    fam_df = pd.DataFrame(fam_rows)

    # Full entry table
    all_entries = list(MODEL_REGISTRY.entries())
    all_df = pd.DataFrame([{
        "key": e.key,
        "family": e.family,
        "role": e.role,
        "display_name": e.display_name,
        "upstream_id": e.upstream_id,
        "backend": e.backend,
        "available": e.available,
        "languages": e.languages or "*",
    } for e in all_entries])

    # BAML count for comparison
    baml_count = len(list_baml_classes())

    # NEW 2026-08-15 — memory doctor card. Surfaces the latest JSON
    # health report emitted by `mise run lakehouse:memory:doctor` so the
    # operator can see the 5-backend status without leaving the control
    # panel.
    import glob
    import json as _json
    import os as _os

    _reports = sorted(
        glob.glob("stedding/memory-health/*.json"),
        key=_os.path.getmtime,
        reverse=True,
    )[:5]
    _report_rows = []
    for _path in _reports:
        try:
            with open(_path) as _f:
                _data = _json.load(_f)
            _ts = _data.get("timestamp", "?")
            _healthy = _data.get("healthy", "?")
            _report_rows.append(
                {"file": _os.path.basename(_path), "timestamp": _ts,
                 "healthy": _healthy}
            )
        except (OSError, _json.JSONDecodeError):
            continue

    memory_doctor_card = mo.md(
        f"""
        ### 🩺 Memory Doctor (NEW 2026-08-15)

        The 5-backend memory stack (cognee + graphiti + lancedb +
        falkordb + memgraph) is wired into the canonical lakehouse via
        the `2026-08-15-lakehouse-memory-stack-deep-integration-v1`
        openspec change. One-click navigation:

        - **Open the notebook**: `marimo edit notebooks/24_lakehouse_memory_doctor.py`
        - **CLI doctor**: `mise run lakehouse:memory:doctor`
        - **Recent health reports** (last 5):
        {''.join(f'  - `{r["file"]}` — {r["timestamp"]} — {r["healthy"]} healthy\\n' for r in _report_rows) if _report_rows else '  - _No reports yet — run `mise run lakehouse:memory:doctor` to generate one_\\n'}

        > The doctor writes JSON reports to `stedding/memory-health/<utc-ts>.json`
        > and is invoked by `deploy:full --phase=7` after the data-stacks
        > come up (see `agent-platform-cluster` spec delta R).
        """
    )

    drift_warning = mo.md(
        f"""
        ### Drift check

        Run `mise run lint:registry --strict` to detect hardcoded
        model strings that bypass `MODEL_REGISTRY`. Audit count
        (informational):

        - **MODEL_REGISTRY entries**: {len(all_entries)} (across 7 families)
        - **BAML classes**: {baml_count} (introspected from `baml_src/`)
        - **Available models**: {sum(1 for e in all_entries if e.available)}
        - **Deprecated models**: {sum(1 for e in all_entries if not e.available)}
        """
    )
    return


@app.cell
def status_footer(deployment_choice_path, mo):
    mo.md(f"""
    ---

    **State file**: `{deployment_choice_path()}`

    Changes persist immediately. The CLI (`bun run cianfhoghlaim
    models list`) and the web UI (`web/apps/...
    /control-panel/`) read the same file.

    For the canonical drift audit, run `mise run lint:registry
    --strict` from the repo root.
    """)
    return


if __name__ == "__main__":
    app.run()
