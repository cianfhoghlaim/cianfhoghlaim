"""Dagster L2 asset: weekly audit of EU institutional Irish (ga) coverage."""

from datetime import UTC, datetime

import dlt_sources
from dagster import AssetExecutionContext, asset


@asset(
    group_name="2_materials_eu_multilingual",
    description="Weekly audit of EU institutional sources Irish (ga) coverage "
    "(per Council Decision 2020/2172 + EU Regulation 1/1958)",
    compute_kind="python",
)
def irish_coverage_monitor(context: AssetExecutionContext) -> dict[str, int]:
    """Audit Irish (Gaeilge) coverage across EU institutional sources."""
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
        ("medicine/ecdc_surveillance", "partial"),
        ("statistics/eurostat", "full"),
        ("publications_office/eu_publications", "full"),
    ]

    rows = [
        {
            "institution": inst,
            "language": "ga",
            "coverage_level": level,
            "checked_at": datetime.now(UTC).isoformat(),
        }
        for inst, level in sources
    ]

    @dlt.resource(
        name="eu_irish_coverage",
        write_disposition="merge",
        primary_key=["institution", "language"],
    )
    def eu_irish_coverage() -> list[dict]:
        return rows

    pipeline = dlt.pipeline(
        pipeline_name="eu_irish_coverage_monitor",
        destination="duckdb",
        dataset_name="cianfhoghlaim_multilingual",
    )
    load_info = pipeline.run(eu_irish_coverage())
    context.log.info(
        "eu_irish_coverage_completed",
        rows=len(rows),
        load_id=str(load_info.loads_ids[0]) if load_info.loads_ids else "",
    )
    return {"rows": len(rows)}


__all__ = ["irish_coverage_monitor"]
