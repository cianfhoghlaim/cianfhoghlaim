"""Dagster L2 asset: weekly audit of EU institutional English coverage."""
from __future__ import annotations

from datetime import UTC, datetime

import dlt
from dagster import AssetExecutionContext, asset


@asset(
    group_name="2_materials_eu_multilingual",
    description="Weekly audit of EU institutional sources English (en) coverage",
    compute_kind="python",
)
def english_coverage_monitor(context: AssetExecutionContext) -> dict[str, int]:
    """Audit English coverage across EU institutional sources."""
    sources = [
        ("eur_lex/regulations", "full"),
        ("eur_lex/directives", "full"),
        ("eur_lex/decisions", "full"),
        ("eur_lex/treaties", "full"),
        ("eur_lex/cjeu_case_law", "full"),
        ("education/eurydice", "full"),
        ("education/cedefop", "full"),
        ("education/school_education_gateway", "full"),
        ("medicine/ema_medicines_register", "full"),
        ("medicine/ecdc_surveillance", "full"),
        ("statistics/eurostat", "full"),
        ("publications_office/eu_publications", "full"),
    ]

    rows = [
        {
            "institution": inst,
            "language": "en",
            "coverage_level": level,
            "checked_at": datetime.now(UTC).isoformat(),
        }
        for inst, level in sources
    ]

    @dlt.resource(
        name="eu_english_coverage",
        write_disposition="merge",
        primary_key=["institution", "language"],
    )
    def eu_english_coverage() -> list[dict]:
        return rows

    pipeline = dlt.pipeline(
        pipeline_name="eu_english_coverage_monitor",
        destination="duckdb",
        dataset_name="cianfhoghlaim_multilingual",
    )
    load_info = pipeline.run(eu_english_coverage())
    context.log.info(
        "eu_english_coverage_completed",
        rows=len(rows),
        load_id=str(load_info.loads_ids[0]) if load_info.loads_ids else "",
    )
    return {"rows": len(rows)}


__all__ = ["english_coverage_monitor"]
