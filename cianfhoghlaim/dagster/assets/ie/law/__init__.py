"""
oideachais.dagster_defs.assets.ie.law — Ireland-law DLT assets.

Phase 3.1-3.2 of the lateralise change. One Dagster `@asset` per
DLT source in `dlt_sources/domains/law/ie/`:

  * irish_statute_book → s3://ducklake/oideachais/law.ie.isb/
  * doj                → s3://ducklake/oideachais/law.ie.doj/
  * lawreform          → s3://ducklake/oideachais/law.ie.lawreform/

Each asset materialises to a `MaterializeResult("ok")` after the
DLT source runs. See `dagster_defs/assets/ie/medicine/__init__.py`
for the pattern.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="law_ie",
    compute_kind="dlt",
    description=(
        "Irish Statute Book (Acts of the Oireachtas). "
        "Source: dlt_sources.ie.law.irish_statute_book."
        "irish_statute_book_source. Covers all acts between "
        "START_YEAR and END_YEAR (defaults from the source module)."
    ),
)
def law_ie_irish_statute_book(context) -> MaterializeResult:
    from dlt_sources.ie.law.irish_statute_book import (
        irish_statute_book_source,
    )

    src = irish_statute_book_source()
    rows = list(src.resources["acts"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "irish_statute_book"}
    )


@asset(
    group_name="law_ie",
    compute_kind="dlt",
    description=(
        "Department of Justice (Ireland) public pages. "
        "Source: dlt_sources.ie.law.doj.doj_source"
    ),
)
def law_ie_doj(context) -> MaterializeResult:
    from dlt_sources.ie.law.doj import doj_source

    src = doj_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "doj"}
    )


@asset(
    group_name="law_ie",
    compute_kind="dlt",
    description=(
        "Law Reform Commission (Ireland) public pages. "
        "Source: dlt_sources.ie.law.lawreform.lawreform_source"
    ),
)
def law_ie_lawreform(context) -> MaterializeResult:
    from dlt_sources.ie.law.lawreform import lawreform_source

    src = lawreform_source()
    rows = list(src.resources["pages"])
    return MaterializeResult(
        metadata={"row_count": len(rows), "source": "lawreform"}
    )
