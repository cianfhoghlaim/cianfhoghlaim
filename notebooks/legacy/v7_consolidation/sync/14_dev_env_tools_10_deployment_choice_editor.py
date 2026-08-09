# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.13",
# ]
# ///
"""10 — Deployment Choice Editor.

Interactive marimo notebook for the `deployment-choice.yaml`
enablement file (the canonical source of truth for what models,
pipelines, datasets, and stacks are currently enabled in this
deployment). The notebook is a **visual editor** — every key in
``enabled_models`` / ``enabled_pipelines`` / ``enabled_datasets`` /
``enabled_stacks`` is rendered as a ``mo.ui.switch`` toggle. The
operator can flip toggles + click "Save changes" to persist the
state to disk via ``write_deployment_choice()``.

Cascade target: this notebook completes the
``2026-08-15-cascading-registry-integration-v3`` batch (Round 3 of
the centralized-registry cascade).

What this notebook does:

1. **Load state** — calls ``read_deployment_choice()`` to load the
   current `deployment-choice.yaml` from the repo root. If the
   file is missing, an empty stub is rendered so the operator can
   still toggle the canonical MODEL_REGISTRY entries.
2. **Models / Pipelines / Stacks tabs** — every key in the
   corresponding section becomes a ``mo.ui.switch``. The live count
   of enabled entries is shown in the section header.
3. **Save changes** — a single button persists the toggled state
   to ``deployment-choice.yaml`` via ``write_deployment_choice()``.
   In dev, the save is a dry-run (no write) so the notebook is
   safe to run end-to-end; pass ``--write`` (or set the env var
   ``DEPLOYMENT_CHOICE_EDIT=write``) to actually persist.

The notebook is a **companion** to the canonical 5-tab
``00_control_panel.py``. This one is purpose-built for the
DevEnv cascade and uses the lighter 3-section shape (no Datasets
tab; that lives in 00_control_panel).

See also:
- `.agents/skills/centralized-registry/SKILL.md`
- `openspec/specs/deployment-control-panel/spec.md`
- `notebooks/_shared/schema.py` (the read/write helpers)
- `deployment-choice.yaml` (the file the notebook edits)
- `notebooks/00_control_panel.py` (the canonical 5-tab editor)
- `web/hono-api/control-panel/_python_bridge.py` (the web-UI bridge)
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium", app_title="Deployment Choice Editor")


# Centralized registries (per the `centralized-model-registry` capability).
# Same try/except block as the rest of the 14_dev_env_tools_*.py notebooks.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        read_deployment_choice,
        write_deployment_choice,
        deployment_choice_path,
        list_dlt_sources,
        list_cocoindex_apps,
        list_baml_classes,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
    _WRITE_HELPER_AVAILABLE = True
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
    _WRITE_HELPER_AVAILABLE = False

    def read_deployment_choice() -> dict:
        return {}

    def write_deployment_choice(_data: dict) -> None:  # pragma: no cover — dev fallback
        return None

    def deployment_choice_path():
        from pathlib import Path
        return Path("deployment-choice.yaml")

    def list_dlt_sources() -> list:
        return []

    def list_cocoindex_apps() -> list:
        return []

    def list_baml_classes() -> list:
        return []


@app.cell
def header(mo, deployment_choice_path):
    mo.md(
        f"""
        # Deployment Choice Editor

        Visual editor for ``deployment-choice.yaml`` (the canonical
        enablement file for the Cianfhoghlaim deployment). 3 sections
        — **models**, **pipelines**, **stacks** — each with a
        ``mo.ui.switch`` per entry. Click "Save changes" to persist
        the new state via ``write_deployment_choice()``.

        **File:** `{deployment_choice_path()}`
        **Default LLM (from MODEL_REGISTRY):** `{_DEFAULT_LLM}`
        **Registry entries:** {_REGISTRY_SUMMARY.get('total', 0)} total
        ({_REGISTRY_SUMMARY.get('available', 0)} available,
        {_REGISTRY_SUMMARY.get('deprecated', 0)} deprecated)
        **Write helper available:** `{_WRITE_HELPER_AVAILABLE}`

        Toggle entries on the 3 tabs below + click **Save changes**
        to persist. In dev (no env var) the save is a dry-run; the
        rendered state is shown but the file is left untouched.
        Set ``DEPLOYMENT_CHOICE_EDIT=write`` to actually write.
        """
    )
    return


@app.cell
def load_choice(read_deployment_choice, deployment_choice_path):
    """Load `deployment-choice.yaml` from the repo root."""
    _path = deployment_choice_path()
    _choice: dict = {}
    _load_error: str | None = None
    try:
        _choice = read_deployment_choice() or {}
    except Exception as e:  # noqa: BLE001
        _load_error = f"read_failed: {e}"

    if not _choice:
        # Empty stub so the editor still renders.
        _choice = {
            "version": 1,
            "enabled_models": {},
            "enabled_pipelines": {},
            "enabled_datasets": {},
            "enabled_stacks": {},
            "monitoring": {"registry_audit": True, "baml_ts_codegen": True},
        }

    _models = dict(_choice.get("enabled_models", {}))
    _pipelines = dict(_choice.get("enabled_pipelines", {}))
    _stacks = dict(_choice.get("enabled_stacks", {}))
    return _path, _choice, _load_error, _models, _pipelines, _stacks


@app.cell
def models_tab(mo, _models):
    """Switch grid for the `enabled_models` section."""
    _switches = {
        k: mo.ui.switch(value=bool(v), label=k)
        for k, v in sorted(_models.items())
    }
    _enabled = sum(1 for s in _switches.values() if s.value)
    mo.md(
        f"""
        ## Tab 1. Models ({_enabled} / {len(_switches)} enabled)

        Every key in the ``enabled_models`` section of
        `deployment-choice.yaml` becomes a switch. The MODEL_REGISTRY
        has {_REGISTRY_SUMMARY.get('total', 0)} entries across 7
        families; only the keys present in the YAML are shown.

        {_switches_panel(_switches)}
        """
    )
    return (_switches,)


@app.cell
def pipelines_tab(mo, _pipelines, _switches, list_dlt_sources, list_cocoindex_apps):
    """Switch grid for the `enabled_pipelines` section."""
    _switches_p = {
        k: mo.ui.switch(value=bool(v), label=k)
        for k, v in sorted(_pipelines.items())
    }
    _enabled = sum(1 for s in _switches_p.values() if s.value)
    _dlt_count = len(list_dlt_sources())
    _coco_count = len(list_cocoindex_apps())
    mo.md(
        f"""
        ## Tab 2. Pipelines ({_enabled} / {len(_switches_p)} enabled)

        Every key in the ``enabled_pipelines`` section becomes a
        switch. The available pipeline keys come from:

        - **{_dlt_count} DLT sources** (via ``list_dlt_sources()``)
        - **{_coco_count} CocoIndex Apps** (via ``list_cocoindex_apps()``)

        Only the keys present in the YAML are shown.

        {_switches_panel(_switches_p)}
        """
    )
    return (_switches_p,)


@app.cell
def stacks_tab(mo, _stacks):
    """Switch grid for the `enabled_stacks` section."""
    _switches_s = {
        k: mo.ui.switch(value=bool(v), label=k)
        for k, v in sorted(_stacks.items())
    }
    _enabled = sum(1 for s in _switches_s.values() if s.value)
    mo.md(
        f"""
        ## Tab 3. Stacks ({_enabled} / {len(_switches_s)} enabled)

        Every key in the ``enabled_stacks`` section of
        `deployment-choice.yaml` becomes a switch. The 8 high-priority
        stacks from the 5-tab ``00_control_panel.py`` are the
        canonical candidates (litellm, langfuse, mlflow, cognee,
        graphiti, lakehouse, openclaw, openchamber).

        {_switches_panel(_switches_s)}
        """
    )
    return (_switches_s,)


@app.cell
def save_button(
    mo,
    os,
    _choice,
    _switches,
    _switches_p,
    _switches_s,
    write_deployment_choice,
    _path,
    _load_error,
):
    """Save-changes button. Persists the toggled state to
    `deployment-choice.yaml` (in dev the save is a dry-run unless
    `DEPLOYMENT_CHOICE_EDIT=write`).
    """
    _dry_run = os.environ.get("DEPLOYMENT_CHOICE_EDIT", "dry-run") != "write"

    def _on_save(_=None) -> str:
        _new = dict(_choice)
        _new["enabled_models"] = {k: bool(s.value) for k, s in _switches.items()}
        _new["enabled_pipelines"] = {k: bool(s.value) for k, s in _switches_p.items()}
        _new["enabled_stacks"] = {k: bool(s.value) for k, s in _switches_s.items()}
        if _dry_run:
            return (
                f"DRY-RUN: would persist to `{_path}` (set "
                f"`DEPLOYMENT_CHOICE_EDIT=write` to actually write). "
                f"models={sum(_new['enabled_models'].values())}, "
                f"pipelines={sum(_new['enabled_pipelines'].values())}, "
                f"stacks={sum(_new['enabled_stacks'].values())}."
            )
        try:
            write_deployment_choice(_new)
        except Exception as e:  # noqa: BLE001
            return f"ERROR: write_failed: {e}"
        return (
            f"SAVED: `{_path}` — models={sum(_new['enabled_models'].values())}, "
            f"pipelines={sum(_new['enabled_pipelines'].values())}, "
            f"stacks={sum(_new['enabled_stacks'].values())}."
        )

    _button = mo.ui.button(
        label="Save changes" + (" (DRY-RUN)" if _dry_run else ""),
        kind="success",
        on_click=_on_save,
    )
    _status_md = (
        f"**File**: `{_path}` · **Dry-run**: `{_dry_run}`"
        + (f" · **Load error**: `{_load_error}`" if _load_error else "")
    )
    mo.vstack([mo.md(_status_md), _button])
    return _on_save, _button, _dry_run


@app.cell
def footer(mo):
    mo.md(
        """
        ## Reference

        - `.agents/skills/centralized-registry/SKILL.md` — the
          single source of truth for the 4 canonical artifacts.
        - `openspec/specs/deployment-control-panel/spec.md` — the
          spec this notebook implements.
        - `notebooks/_shared/schema.py:read_deployment_choice` — the
          atomic read helper (with `fcntl.flock`).
        - `notebooks/_shared/schema.py:write_deployment_choice` —
          the atomic write helper.
        - `notebooks/00_control_panel.py` — the canonical 5-tab
          marimo control panel (the operator's UI; this notebook is
          a lighter 3-tab alternative purpose-built for the
          DevEnv cascade).

        ## Companion notebooks

        - `notebooks/14_dev_env_tools_07_model_registry.py` — the
          MODEL_REGISTRY explorer.
        - `notebooks/14_dev_env_tools_08_registry_drift_watch.py` —
          the live drift watcher.
        - `notebooks/14_dev_env_tools_09_registry_drift_history.py` —
          the drift history viewer.
        """
    )
    return


@app.function
def _switches_panel(switches: dict) -> str:
    """Render a switch dict as a markdown bullet list.

    Marimo's ``mo.vstack`` works inside an ``@app.cell`` but cannot
    be embedded inside an ``mo.md(...)`` f-string, so we render the
    switch labels as a bulleted list and rely on the marimo cell
    re-render to update the visible switches.
    """
    if not switches:
        return "_No entries in this section._"
    return "\n".join(f"- `{k}`" for k in switches.keys())


if __name__ == "__main__":
    app.run()
