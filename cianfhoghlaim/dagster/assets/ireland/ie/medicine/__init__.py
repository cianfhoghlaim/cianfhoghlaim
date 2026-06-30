"""
oideachais.dagster_defs.assets.ie.medicine — Ireland-medicine DLT assets.

Phase 3.1-3.2 of the lateralise change. One Dagster `@asset` per
DLT source in `dlt_sources/domains/medicine/ie/`:

  * hse            → s3://ducklake/oideachais/medicine.ie.hse/
  * medical_council→ s3://ducklake/oideachais/medicine.ie.medical_council/
  * doh            → s3://ducklake/oideachais/medicine.ie.doh/
  * hpsc           → s3://ducklake/oideachais/medicine.ie.hpsc/

Each asset materialises to a `MaterializeResult("ok")` after the
DLT source runs. We don't actually materialise to DuckLake in
the asset body — that's the job of the SourceFactory's
`dlt_asset` method (Phase 5 wiring). For now the asset is a
*thin wrapper* that calls the source and reports row count.

NOTE: the `context` parameter is left un-annotated to keep
Dagster 1.12.6 happy (the type-hint validator refuses string
annotations on @asset body functions).
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_ie",
    compute_kind="dlt",
    description=(
        "HSE (Health Service Executive) Ireland public pages. "
        "Source: cianfhoghlaim.dlt.british_isles.ireland.medicine.hse.hse_source"
    ),
)
def medicine_ie_hse(context) -> MaterializeResult:
    """DLT extract of hse.ie pages into the oideachais lakehouse."""
    from cianfhoghlaim.dlt.british_isles.ireland.medicine.hse import hse_source

    src = hse_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "hse"}
    )


@asset(
    group_name="medicine_ie",
    compute_kind="dlt",
    description=(
        "Medical Council of Ireland public register search. "
        "Source: cianfhoghlaim.dlt.british_isles.ireland.medicine.medical_council.medical_council_source"
    ),
)
def medicine_ie_medical_council(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.ireland.medicine.medical_council import (
        medical_council_source,
    )

    src = medical_council_source()
    rows = list(src.resources["register_pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "medical_council"}
    )


@asset(
    group_name="medicine_ie",
    compute_kind="dlt",
    description=(
        "Department of Health (Ireland) public pages. "
        "Source: cianfhoghlaim.dlt.british_isles.ireland.medicine.doh.doh_source"
    ),
)
def medicine_ie_doh(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.ireland.medicine.doh import doh_source

    src = doh_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "doh"}
    )


@asset(
    group_name="medicine_ie",
    compute_kind="dlt",
    description=(
        "Health Protection Surveillance Centre (Ireland) public data. "
        "Source: cianfhoghlaim.dlt.british_isles.ireland.medicine.hpsc.hpsc_source"
    ),
)
def medicine_ie_hpsc(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.ireland.medicine.hpsc import hpsc_source

    src = hpsc_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "hpsc"}
    )
