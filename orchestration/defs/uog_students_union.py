"""orchestration.defs.uog_students_union — the 2-asset group for the
UoG Students' Union pipeline.

Mounts 2 assets:
  - `uog_su_stage0_audit`       (sensor)
  - `uog_su_collect`            (scrape + DuckLake)
"""

from dagster import AssetKey, MaterializeResult, asset

_DEFAULT_DESTINATION = "local"


@asset(
    key=["uog_students_union", "stage0_audit"],
    group_name="uog_students_union",
    compute_kind="sensor",
    description=(
        "Stage 0 — Firecrawl `/agent` audit of `su.universityofgalway.ie`. "
        "Discovers the canonical URLs for the 5 canonical SU documents."
    ),
)
def uog_su_stage0_audit(context) -> MaterializeResult:
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        uog_students_union_source,
    )

    rows = list(
        uog_students_union_source(destination=_DEFAULT_DESTINATION)
        .selected_resources["students_union_documents"]()
    )
    return MaterializeResult(
        metadata={
            "su_documents_seeded": len(rows),
            "ducklake_table": "cianfhoghlaim.education.ie.uog_students_union_documents",
        }
    )


@asset(
    key=["uog_students_union", "collect"],
    group_name="uog_students_union",
    compute_kind="scrape",
    description=(
        "Stage 1 — bulk_scrape the SU policies + class-rep handbooks. "
        "Drops the rows into DuckLake."
    ),
    deps=[AssetKey(["uog_students_union", "stage0_audit"])],
)
def uog_su_collect(context) -> MaterializeResult:
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        uog_students_union_source,
    )

    rows = list(
        uog_students_union_source(destination=_DEFAULT_DESTINATION)
        .selected_resources["students_union_documents"]()
    )
    return MaterializeResult(
        metadata={
            "rows_collected": len(rows),
            "class_rep_handbooks": len(
                list(
                    uog_students_union_source(destination=_DEFAULT_DESTINATION)
                    .selected_resources["class_rep_handbooks"]()
                )
            ),
        }
    )


__all__ = [
    "uog_su_collect",
    "uog_su_stage0_audit",
]
