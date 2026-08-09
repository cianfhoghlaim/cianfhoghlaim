"""marimo notebook: Knowledge Graph Health (per the 2026-08-10-copilotkit-action-wiring-v1 change).

A marimo notebook surfacing Cognee ingestion timestamps for the
8 canonical datasets backing the 5-stage cognify pipeline:

1. Aistear
2. Primary
3. Junior Cycle
4. Senior Cycle (Leaving Cert)
5. Cross-stage (the 8 EDGE_DEFINITIONS)
6. BAML schemas (sourced from the baml_schemas_sensor)
7. Agent definitions (sourced from the agent_definitions_sensor)
8. Skill metadata (sourced from the skills_sensor)

Each dataset is colour-coded: green (< 24h), yellow (< 7d), red (> 7d).

Run via:
    marimo edit notebooks/28_knowledge_graph_health.py
"""

import marimo

__generated_with = "0.9.32"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Knowledge Graph Health Dashboard

        Real-time ingestion timestamps for the 8 Cognee datasets that
        back the 5-stage cognify pipeline.

        **Color coding:** green (< 24h) → yellow (< 7d) → red (> 7d)

        **Sources:**
        - Aistear / Primary / JC / SC: cognify adapters in `scripts/graph_storage/cognify/cognee_integration/`
        - Cross-stage: `cross_stage_cognify.py` + the 8 `EDGE_DEFINITIONS`
        - BAML schemas: `cognee_ingest_baml_schemas.py` (sensors per C2)
        - Agent definitions: `cognee_ingest_agent_definitions.py` (sensors per C2)
        - Skill metadata: `cognee_ingest_skills.py` (sensors per C2)
        """
    )
    return


@app.cell
def _():
    """Fetch the most recent ingestion timestamp per dataset."""
    import asyncio

    DATASETS = [
        "aistear", "primary", "junior_cycle", "senior_cycle",
        "cross_stage", "baml_schemas", "agent_definitions", "agent_skills",
    ]

    async def _get_timestamps():
        try:
            import cognee  # type: ignore[import-not-found]
        except ImportError:
            return {ds: None for ds in DATASETS}

        results = {}
        for ds in DATASETS:
            try:
                meta = await cognee.get_dataset_metadata(
                    dataset_name=f"cianfhoghlaim.education.{ds}"
                )
                ts = meta.get("last_ingested_at") if meta else None
            except Exception:
                ts = None
            results[ds] = ts
        return results

    timestamps = asyncio.run(_get_timestamps())
    return (timestamps,)


@app.cell
def _(timestamps):
    """Render the 8 datasets as a colour-coded table."""
    from datetime import datetime, UTC

    rows = []
    for ds, ts in timestamps.items():
        if ts is None:
            color = "white"
            label = "no data (cognee not running)"
        else:
            try:
                age_hours = (
                    datetime.now(UTC) - datetime.fromisoformat(ts)
                ).total_seconds() / 3600
                if age_hours < 24:
                    color = "green"
                elif age_hours < 168:  # 7d
                    color = "yellow"
                else:
                    color = "red"
                label = f"{ts} ({age_hours:.0f}h ago)"
            except Exception:
                color = "white"
                label = f"{ts} (unparseable)"
        rows.append({"color": color, "dataset": ds, "last_ingested": label})

    return (rows,)


@app.cell
def _(rows):
    import marimo as mo
    mo.ui.table(data=rows, label="Knowledge Graph Datasets")
    return


if __name__ == "__main__":
    app.run()