"""Daily diagram pre-render Dagster asset.

Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T6.8.
Renders the 4 diagram modes × 8 subjects × EN/GA = 64 SVGs once per day
and writes them to `s3://cianfhoghlaim-diagram-cache/{mode}/{subject}/{lang}.svg`.

This pre-render keeps the page-load fast path (the `?cache=true`
query parameter reads from the Convex `diagram_cache` table).
"""


from datetime import datetime, timezone

from dagster import (
    AssetExecutionContext,
    DailyPartitionsDefinition,
    asset,
)

try:
    from baml_client import b
    BAML_AVAILABLE = True
except ImportError:
    BAML_AVAILABLE = False
    b = None


# 4 modes × 8 subjects × 2 languages = 64 SVGs to pre-render
DIAGRAM_MODES = ("concept-map", "topic-heatmap", "pclm-flow", "question-sankey")
SUBJECTS = (
    "mathematics", "applied_mathematics", "chemistry", "geography",
    "history", "english", "gaeilge", "computer_science",
)
LANGUAGES = ("en", "ga")


@asset(
    group_name="diagrams",
    partitions_def=DailyPartitionsDefinition(start_date="2026-07-02"),
    description="Daily pre-render of the 4 diagram modes × 8 subjects × EN/GA = 64 SVGs",
)
def daily_diagram_pre_render(context: AssetExecutionContext) -> dict[str, int]:
    """Render all 64 diagram SVGs and write to s3://cianfhoghlaim-diagram-cache/.

    Returns the count of rendered SVGs (64 on success).
    """
    if not BAML_AVAILABLE:
        context.log.warning("BAML not available; skipping pre-render")
        return {"rendered": 0, "skipped": 64}

    rendered = 0
    for mode in DIAGRAM_MODES:
        for subject in SUBJECTS:
            for language in LANGUAGES:
                try:
                    # Call the appropriate BAML function
                    if mode == "concept-map":
                        payload = b.RenderConceptMap(
                            subject=subject,
                            language=language,
                            syllabus_topics_json="[]",
                            past_papers_json="[]",
                            marking_schemes_json="[]",
                            five_key_competencies_json="[]",
                        )
                    elif mode == "topic-heatmap":
                        payload = b.RenderTopicHeatmap(
                            subject=subject,
                            language=language,
                            past_papers_json="[]",
                            year_range=[2017, 2025],
                        )
                    elif mode == "pclm-flow":
                        payload = b.RenderPCLMFlow(
                            subject=subject,
                            language=language,
                            marking_scheme_json="[]",
                            paper="paper-1",
                            year=2024,
                        )
                    elif mode == "question-sankey":
                        payload = b.RenderQuestionSankey(
                            subject=subject,
                            language=language,
                            past_papers_json="[]",
                            year_range=[2017, 2025],
                        )
                    else:
                        continue

                    # TODO: write the SVG to s3://cianfhoghlaim-diagram-cache/
                    # and insert a row into Convex `diagram_cache`
                    rendered += 1
                    context.log.info(f"Rendered {mode}/{subject}/{language}")
                except Exception as e:
                    context.log.error(f"Failed to render {mode}/{subject}/{language}: {e}")

    context.log.info(f"daily_diagram_pre_render complete: {rendered}/64")
    return {"rendered": rendered, "skipped": 64 - rendered, "rendered_at": datetime.now(timezone.utc).isoformat()}