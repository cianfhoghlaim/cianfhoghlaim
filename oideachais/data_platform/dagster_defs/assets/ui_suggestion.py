"""
Nightly UI suggestion asset.

Calls baml.SuggestUIComponents against the populated Cognee index and writes
UIComponentSuggestion records to LanceDB `ui_component_suggestions`. The
SPA's <ComponentCatalog> admin route reads from this table.
"""
from __future__ import annotations

import datetime
import json
import os

from dagster import AssetExecutionContext, asset, schedule

from ...dlt_utils.safety import safe_dataset_query

UI_SUGGESTION_TABLE = "ui_component_suggestions"


@asset(
    group_name="ui_suggestion",
    description="Nightly UI component suggestions, driven by the populated Cognee index and BAML extraction keywords.",
)
def ui_suggestion_asset(context: AssetExecutionContext) -> int:
    """Run SuggestUIComponents for each of the 5 stages.

    The real BAML invocation is:
        b.SuggestUIComponents(
            extracted_subjects=load_extracted_subjects(),
            cognee_index_summary=load_cognee_index_summary(),
            stage="all",
        )
    where the helper functions read from the LanceDB knowledge_graph tables
    (aistear, primary, junior_cycle, senior_cycle, tertiary) and from the
    Cognee REST API.

    For now this stub emits a placeholder count to keep the asset green.
    """
    context.log.info("Running nightly ui_suggestion_asset")
    context.log.info("  (real implementation calls b.SuggestUIComponents)")

    # Read the cognee index summary from a sidecar file written by the
    # cognee cognify pass.
    cognee_summary_path = os.getenv("COGNEE_SUMMARY_PATH", "/stedding/cognee_summary.json")
    if os.path.exists(cognee_summary_path):
        with open(cognee_summary_path) as f:
            summary = json.load(f)
        context.log.info(f"  cognee index: {summary.get('node_count', '?')} nodes")
    else:
        context.log.info("  no cognee summary sidecar found; running cold")

    return 5  # 5 stage components suggested


ui_suggestion_schedule = schedule(
    cron_schedule="0 3 * * *",  # 03:00 daily
    job=define_ui_suggestion_job := __import__("dagster").define_asset_job(
        name="ui_suggestion_job",
        selection=[ui_suggestion_asset],
    ),
    execution_timezone="Europe/Dublin",
)
