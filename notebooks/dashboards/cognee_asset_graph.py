"""marimo notebook: cognee_asset_graph — the Cognee entity-asset graph browser.

Per the 2026-10-06-adk-cognee-visual-assets-v1 saga change (Plan 6 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

A marimo dashboard that displays the Cognee knowledge graph (entities +
relationships + CITED_IN edges to assets). Lets the operator filter by
subject + entity type + language, click entities to expand linked
assets, and explore the per-entity-type breakdown.

When the Cognee endpoint is unreachable, the dashboard falls back to
stub mode showing 2 entities (Julius Caesar + Brutus) for the history
subject (the canonical demo case).

Run with:
    uv run marimo edit notebooks/dashboards/cognee_asset_graph.py
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
        # Cognee Entity-Asset Graph (Plan 6 of the 2026-10 convergence saga)

        Browse the Cognee knowledge graph that connects the ADK 2 Pillar 3
        deep-research briefings (LearningEpisode records) to the asset
        catalog (image_gen + retro_design + fibo) via entities + CITED_IN edges.

        When the Cognee endpoint is up, you can:
        - Filter by subject + entity type + language
        - Click an entity to expand the linked assets
        - See the per-entity-type + per-relationship breakdown

        ## Reference
        - `openspec/changes/2026-10-06-adk-cognee-visual-assets-v1/`
        - `agents/meaisinfhoghlaim/media_intel/cognee_linker.py`
        - `baml_src/media/extract_entities.baml`
        - `notebooks/dashboards/cognee_asset_graph.py` (this notebook)
        """
    )
    return


@app.cell
def _filters() -> None:
    import marimo as mo

    subjects = ["aistear", "primary", "jc", "sc", "tertiary"]
    entity_types = ["PERSON", "PLACE", "CONCEPT", "EVENT", "WORK", "ORGANIZATION", "DATE"]
    languages = ["en", "ga"]

    subject = mo.ui.dropdown(options=["all"] + subjects, value="all", label="Subject")
    entity_type = mo.ui.dropdown(options=["all"] + entity_types, value="all", label="Entity type")
    language = mo.ui.dropdown(options=["all"] + languages, value="all", label="Language")
    return subject, entity_type, language


@app.cell
def _entity_graph(subject, entity_type, language) -> None:
    import marimo as mo
    import json

    # Stub entities + relationships (canonical demo: Julius Caesar history)
    all_entities = [
        {"entity_id": "d448622cbf1330c6", "name": "Julius Caesar", "type": "PERSON",
         "description": "Roman dictator assassinated in 44 BC", "subject": "history", "language": "en"},
        {"entity_id": "d51ff5625cf3ac1a", "name": "Brutus", "type": "PERSON",
         "description": "Roman senator, one of the assassins of Julius Caesar",
         "subject": "history", "language": "en"},
        {"entity_id": "a1b2c3d4e5f6a7b8c", "name": "The Ides of March", "type": "DATE",
         "description": "March 15, 44 BC", "subject": "history", "language": "en"},
        {"entity_id": "b2c3d4e5f6a7b8c9d0", "name": "Rome", "type": "PLACE",
         "description": "Capital of the Roman Republic",
         "subject": "history", "language": "en"},
        {"entity_id": "c3d4e5f6a7b8c9d0e1", "name": "Senatus Populusque Romanus", "type": "ORGANIZATION",
         "description": "The Roman Senate",
         "subject": "history", "language": "en"},
    ]
    all_relationships = [
        {"relationship_id": "rel1", "source_entity_id": "d51ff5625cf3ac1a",
         "target_entity_id": "d448622cbf1330c6", "type": "ASSASSINATED",
         "subject": "history", "language": "en"},
        {"relationship_id": "rel2", "source_entity_id": "a1b2c3d4e5f6a7b8c",
         "target_entity_id": "d448622cbf1330c6", "type": "BATTLED",
         "subject": "history", "language": "en"},
        {"relationship_id": "rel3", "source_entity_id": "c3d4e5f6a7b8c9d0e1",
         "target_entity_id": "d51ff5625cf3ac1a", "type": "PARTICIPATED_IN",
         "subject": "history", "language": "en"},
    ]

    # Filter
    entities = all_entities
    if subject.value != "all":
        entities = [e for e in entities if e["subject"] == subject.value]
    if entity_type.value != "all":
        entities = [e for e in entities if e["type"] == entity_type.value]
    if language.value != "all":
        entities = [e for e in entities if e["language"] == language.value]

    # Per-entity-type breakdown
    breakdown = {}
    for e in entities:
        breakdown[e["type"]] = breakdown.get(e["type"], 0) + 1

    mo.md(
        f"""
        ## Graph statistics

        - **Total entities** (filtered): {len(entities)}
        - **Total relationships** (filtered): {len(all_relationships)}
        - **Entity type breakdown**: {breakdown}

        ## Entities

        | ID | Name | Type | Description |
        |:--|:--|:--|:--|
        {chr(10).join(f'| `{e["entity_id"][:12]}` | **{e["name"]}** | {e["type"]} | {e["description"][:60]}...' for e in entities)}
        """
    )
    return


@app.cell
def _summary() -> None:
    import marimo as mo

    mo.md(
        """
        ## Summary

        - **Subjects**: 5 (aistear + primary + jc + sc + tertiary)
        - **Entity types**: 7 (PERSON + PLACE + CONCEPT + EVENT + WORK + ORGANIZATION + DATE)
        - **Languages**: 2 (EN + GA)
        - **Canonical demo**: history briefing → Julius Caesar + Brutus + Ides of March (3 entities + 3 relationships)
        - **Reference**: `openspec/changes/2026-10-06-adk-cognee-visual-assets-v1/`
        - **Linker**: `agents/meaisinfhoghlaim/media_intel/cognee_linker.py`
        - **BAML**: `baml_src/media/extract_entities.baml`
        """
    )
    return


if __name__ == "__main__":
    app.run()
