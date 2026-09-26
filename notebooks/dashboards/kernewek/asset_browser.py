"""marimo notebook: kernewek/asset_browser — the Cornish (kernewek) asset browser.

Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change (Plan 7).
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # Kernewek (Cornish) Asset Browser (Plan 7 of the 2026-10 convergence saga)

        Browse the Cornish asset table (`media.image_gen_chunks_kernewek`)
        populated by `GenerateCornishAsset`.

        ## Reference
        - `baml_src/british_isles/_cross/asset_generation.baml`
        - `cocoindex_flows/media/kernewek/asset_index.py`
        - `scripts/celtic_assets.py`
        """
    )
    return


@app.cell
def _filters() -> None:
    import marimo as mo

    subjects = ["mathematics", "applied_mathematics", "chemistry", "geography",
                "history", "english", "gaeilge", "computer_science"]
    roles = ["default", "fast", "bilingual", "legacy", "diagrams"]

    subject = mo.ui.dropdown(options=["all"] + subjects, value="all", label="Subject")
    role = mo.ui.dropdown(options=["all"] + roles, value="all", label="Role")
    return subject, role


@app.cell
def _browser(subject, role) -> None:
    import marimo as mo

    kw_assets = []
    for s in ["mathematics", "applied_mathematics", "chemistry", "geography", "history"]:
        for r in ["default", "bilingual"]:
            kw_assets.append({
                "asset_id": f"kw-{s}-{r}",
                "subject": s,
                "language": "kw",
                "language_label": "Kernewek",
                "role": r,
                "title": f"Gwrians {s.title()} ({r.title()})",
                "title_en": f"{s.title()} Creation ({r.title()})",
                "palette_hex": ["#1a0e1a", "#d4af37", "#f0e6d2"],
                "stub": True,
            })

    filtered = kw_assets
    if subject.value != "all":
        filtered = [a for a in filtered if a["subject"] == subject.value]
    if role.value != "all":
        filtered = [a for a in filtered if a["role"] == role.value]

    mo.md(
        f"""
        ## Filtered results ({len(filtered)} kernewek assets)

        | ID | Subject | Role | Title | Title (EN) | Stub |
        |:--|:--|:--|:--|:--|:--|
        {chr(10).join(f'| {a["asset_id"]} | {a["subject"]} | {a["role"]} | {a["title"]} | {a["title_en"]} | {a["stub"]} |' for a in filtered)}
        """
    )
    return


@app.cell
def _summary() -> None:
    import marimo as mo

    mo.md(
        """
        ## Summary

        - **Language**: Cornish (Kernewek / kw)
        - **Subjects**: 8
        - **Roles**: 5
        - **Table**: `media.image_gen_chunks_kernewek`
        - **BAML function**: `GenerateCornishAsset(prompt, subject, role)`
        - **Reference**: `openspec/changes/2026-10-07-bilingual-celtic-asset-pipeline-v1/`
        """
    )
    return


if __name__ == "__main__":
    app.run()
