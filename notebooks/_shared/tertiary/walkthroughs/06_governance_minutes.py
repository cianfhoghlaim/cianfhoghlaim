"""marimo notebook: 06_governance_minutes: UoG governance minutes extraction — UoG tertiary pipeline walkthrough.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.
Pattern mirrors notebooks/ciancheiltis_en_ga_roi.py (dual-mode script,
_intro() markdown cell describing what + how + where the docs live,
_phase_status() cell querying DuckLake).

UoG governance minutes extraction

Reference surfaces:
dlt_sources/.../tertiary/uog/governance_minutes.py + 
cocoindex_flows/.../governance_flow.py + 
governance_minute.baml

Run with:
    uv run marimo edit notebooks/_shared/tertiary/walkthroughs/06_governance_minutes.py
    uv run python notebooks/_shared/tertiary/walkthroughs/06_governance_minutes.py --cli
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
        # 06_governance_minutes: UoG governance minutes extraction

        This notebook walks through **UoG governance minutes extraction** — what it is, how it works, where the docs live, and how to query the live DuckLake data.

        ## Reference surfaces
\n        - dlt_sources/.../tertiary/uog/governance_minutes.py\n        - cocoindex_flows/.../governance_flow.py\n        - governance_minute.baml

        See:
        - `openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/specs/`
        - `openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/specs/cianfhoghlaim-tertiary-pipeline/spec.md`
        - `notebooks/_shared/tertiary/students_union_adk_case_studies.py`
        - `.agents/skills/uoa-tertiary-pipeline/SKILL.md`
        - `baml_src/british_isles/ireland/tertiary/university_extraction.baml`
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

        Walkthrough `06_governance_minutes: UoG governance minutes extraction` — fetched at {datetime.utcnow().isoformat()}.
        """
    )
    return


@app.cell
def _ducklake_query() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from ducklake_helpers import walkthrough_1_data_inlining  # type: ignore

    result = walkthrough_1_data_inlining()
    return (result,)


@app.cell
def _render_result(result) -> None:
    import marimo as mo

    mo.md(f"```json\n{result}\n```")
    return


if __name__ == "__main__":
    app.run()
