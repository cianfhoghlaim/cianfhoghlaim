# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.13",
# ]
# ///
"""07 — Model Registry explorer.

Interactive marimo notebook for browsing the centralized MODEL_REGISTRY
(the 52-entry unified model registry from `centralized-model-registry`).
Filters by family + role + availability + language. Shows the
canonical key, display name, upstream ID, backend, LiteLLM alias,
and notes for each entry.

Companion notebook to `notebooks/00_control_panel.py` (Tab 1).

See also:
- `.agents/skills/centralized-registry/SKILL.md`
- `openspec/specs/centralized-model-registry/spec.md`
- `meaisinfhoghlaim/models/README.md`
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium", app_title="MODEL_REGISTRY Explorer")


@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    import sys

    # The unified MODEL_REGISTRY (52 entries across 7 families).
    # Resilient to import errors (e.g. when ibis is unavailable in dev).
    try:
        from meaisinfhoghlaim.models import (
            MODEL_REGISTRY,
            model_for,
            filter_models,
        )
        _import_ok = True
        _import_error = None
    except Exception as e:  # noqa: BLE001 — dev fallback
        MODEL_REGISTRY = None
        model_for = None
        filter_models = None
        _import_ok = False
        _import_error = e

    return (
        mo,
        pd,
        sys,
        MODEL_REGISTRY,
        model_for,
        filter_models,
        _import_ok,
        _import_error,
    )


@app.cell
def intro(mo, _import_ok, _import_error):
    if not _import_ok:
        mo.md(
            f"""
            # MODEL_REGISTRY Explorer

            **ERROR**: could not import the registry. Reason:

            ```
            {_import_error}
            ```

            Try `uv run python -c "from meaisinfhoghlaim.models import MODEL_REGISTRY; print(MODEL_REGISTRY.summary())"`.
            """
        )
        return

    summary = MODEL_REGISTRY.summary()
    mo.md(
        f"""
        # MODEL_REGISTRY Explorer

        The unified MODEL_REGISTRY has **{summary['total']} entries**
        ({summary['available']} available, {summary['deprecated']} deprecated)
        across **7 families**:

        | Family | Count |
        |:--|--:|
        """
    )
    rows = "\n".join(
        f"| `{fam}` | {count} |"
        for fam, count in sorted(summary["by_family"].items())
    )
    mo.md(f"{rows}\n")
    return


@app.cell
def family_filter(mo, MODEL_REGISTRY):
    """Multi-select widget for the 7 model families."""
    if MODEL_REGISTRY is None:
        return (None,)
    return (
        mo.ui.multiselect(
            options=[
                "ocr_vision", "text_llm", "embedder", "rerank",
                "image_gen", "voice", "translation",
            ],
            value=[
                "ocr_vision", "text_llm", "embedder", "rerank",
                "image_gen", "voice", "translation",
            ],
            label="Model families to display",
        ),
    )


@app.cell
def available_only(mo):
    return (mo.ui.checkbox(value=True, label="Show only available models"),)


@app.cell
def filtered_table(family_filter, available_only, filter_models, pd, MODEL_REGISTRY):
    """Filtered + sorted table of MODEL_REGISTRY entries."""
    if MODEL_REGISTRY is None:
        return (None,)
    entries = []
    for fam in family_filter.value or []:
        for e in filter_models(fam):
            if available_only.value and not e.available:
                continue
            entries.append({
                "key": e.key,
                "family": e.family,
                "role": e.role,
                "display_name": e.display_name,
                "upstream_id": e.upstream_id,
                "backend": e.backend,
                "available": e.available,
                "litellm_alias": e.litellm_alias or "",
                "languages": ",".join(e.languages) if e.languages else "",
                "notes": e.notes[:100] + ("..." if len(e.notes) > 100 else ""),
            })
    df = pd.DataFrame(entries).sort_values(["family", "role", "key"])
    return (df,)


@app.cell
def render_table(filtered_table, mo, family_filter, available_only):
    if filtered_table is None or filtered_table.empty:
        mo.md("No entries match the filters.")
        return
    mo.md(f"## Showing {len(filtered_table)} entries")
    mo.ui.table(filtered_table, selection=None, page_size=50)
    return


@app.cell
def resolve_widget(mo, MODEL_REGISTRY, model_for):
    """Interactive single-model resolver."""
    if MODEL_REGISTRY is None:
        return
    mo.md(
        """
        ## Resolve a single model

        Pick a family + role + optional language, get the canonical
        model key.
        """
    )
    family_select = mo.ui.dropdown(
        options=["ocr_vision", "text_llm", "embedder", "rerank",
                 "image_gen", "voice", "translation"],
        value="text_llm",
        label="Family",
    )
    role_select = mo.ui.text(
        value="default",
        label="Role (e.g. 'default', 'strong', 'irish', 'tts')",
    )
    language_select = mo.ui.text(
        value="",
        label="Language (2-letter code, optional)",
    )
    resolve_button = mo.ui.run_button(label="Resolve")
    return family_select, role_select, language_select, resolve_button


@app.cell
def resolve_result(
    family_select,
    role_select,
    language_select,
    resolve_button,
    model_for,
    mo,
):
    if not resolve_button.value:
        return
    try:
        language = language_select.value or None
        if language:
            result = model_for(family_select.value, role_select.value, language=language)
        else:
            result = model_for(family_select.value, role_select.value)
        mo.md(
            f"""
            **Resolved**: `MODEL_REGISTRY.resolve("{family_select.value}",
            "{role_select.value}", language={language!r})` →
            `{result}`
            """
        )
    except KeyError as e:
        mo.md(f"**KeyError**: {e}")
    return


@app.cell
def footer(mo):
    mo.md(
        """
        ---

        **Reference**: see `.agents/skills/centralized-registry/SKILL.md`
        for the full API documentation, and `meaisinfhoghlaim/models/README.md`
        for the directory overview.

        **Companion**: `notebooks/00_control_panel.py` (the 5-tab control panel
        marimo notebook that reads + writes `deployment-choice.yaml`).

        **Audit**: `mise run lint:registry --strict` to verify no hardcoded
        model strings have bypassed the registry.
        """
    )
    return


if __name__ == "__main__":
    app.run()