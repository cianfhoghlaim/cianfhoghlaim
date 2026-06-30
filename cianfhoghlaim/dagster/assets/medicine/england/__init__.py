"""
oideachais.dagster_defs.assets.medicine.en — England-medicine DLT assets.

Phase 3.3 of the lateralise change. 3 England-medicine DLT
sources wired as Dagster assets:

  * nhs_england → NHS England (national service commissioner)
  * gmc         → General Medical Council (UK register)
  * nice        → National Institute for Health & Care Excellence
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="medicine_en",
    compute_kind="dlt",
    description="NHS England public pages.",
)
def medicine_en_nhs_england(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.medicine.nhs_england import (
        nhs_england_source,
    )

    src = nhs_england_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nhs_england"}
    )


@asset(
    group_name="medicine_en",
    compute_kind="dlt",
    description="General Medical Council (UK medical register).",
)
def medicine_en_gmc(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.medicine.gmc import gmc_source

    src = gmc_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "gmc"}
    )


@asset(
    group_name="medicine_en",
    compute_kind="dlt",
    description="NICE (National Institute for Health & Care Excellence) guidelines.",
)
def medicine_en_nice(context) -> MaterializeResult:
    from cianfhoghlaim.dlt.british_isles.england.medicine.nice import nice_source

    src = nice_source()
    rows = list(src.resources["guidelines_pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "nice"}
    )
