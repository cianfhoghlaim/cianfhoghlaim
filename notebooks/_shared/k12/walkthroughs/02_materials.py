"""marimo notebook: 02_materials: L2 Materials — BAML extractions for aistear + primary + jc + sc — K-12 teacher + student pipeline walkthrough.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pattern mirrors notebooks/ciancheiltis_en_ga_roi.py (dual-mode script,
_intro() markdown cell describing what + how + where the docs live,
_phase_status() cell querying DuckLake).

L2 Materials — BAML extractions for aistear + primary + jc + sc

Reference surfaces:
baml_src/british_isles/ireland/education/{aistear,primary,junior_cycle,senior_cycle}.baml + 
orchestration/defs/2_materials/primary_jc/

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/02_materials.py
    uv run python notebooks/_shared/k12/walkthroughs/02_materials.py --cli
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
        # 02_materials: L2 Materials — BAML extractions for aistear + primary + jc + sc

        This notebook walks through **L2 Materials — BAML extractions for aistear + primary + jc + sc** — what it is, how it works, where the docs live, and how to query the live DuckLake data.

        ## Reference surfaces
\n        - baml_src/british_isles/ireland/education/{aistear,primary,junior_cycle,senior_cycle}.baml\n        - orchestration/defs/2_materials/primary_jc/

        See:
        - `openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/specs/`
        - `openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/specs/cianfhoghlaim-tertiary-pipeline/spec.md`
        - `.agents/skills/uoa-tertiary-pipeline/SKILL.md`
        - `baml_src/british_isles/ireland/education/stages/aistear.baml`
        - `cocoindex_flows/british_isles/ireland/education/_shared.py`
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo
    from datetime import datetime

    mo.md(
        f"""
        ## Phase status (live DuckLake query)

        Walkthrough `02_materials: L2 Materials — BAML extractions for aistear + primary + jc + sc` — fetched at {datetime.utcnow().isoformat()}.
        """
    )
    return


@app.cell
def _ducklake_query() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from ducklake_helpers import walkthrough_k12_demo  # type: ignore

    result = walkthrough_k12_demo()
    return (result,)


@app.cell
def _render_result(result) -> None:
    import marimo as mo

    mo.md(f"```json\n{result}\n```")
    return


if __name__ == "__main__":
    app.run()
