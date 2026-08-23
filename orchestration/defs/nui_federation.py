"""orchestration.defs.nui_federation — the 3-asset group for the
NUI federation pipeline.

Mounts 3 assets:
  - `nui_federation_audit`       (sensor — federated site-map)
  - `nui_constituents_scrape`    (scrape — the 4 constituents + historical)
  - `nui_archive_ingest`         (scrape — the pre-1908 QUB archive)
"""

from dagster import AssetKey, MaterializeResult, asset

_DEFAULT_DESTINATION = "local"


@asset(
    key=["nui_federation", "audit"],
    group_name="nui_federation",
    compute_kind="sensor",
    description=(
        "Stage 0 — Firecrawl `/agent` audit of nui.ie/about/. Discovers "
        "any new member link the canonical NUI_PORTAL_URLS list does "
        "not yet cover."
    ),
)
def nui_federation_audit(context) -> MaterializeResult:
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        nui_federation_source,
    )

    rows = list(
        nui_federation_source(destination=_DEFAULT_DESTINATION)
        .selected_resources["nui_members"]()
    )
    n_current = sum(1 for r in rows if r.get("kind") == "CONSTITUENT_UNIVERSITY")
    n_historical = sum(1 for r in rows if r.get("kind") == "HISTORICAL_MEMBER")
    return MaterializeResult(
        metadata={
            "constituents_discovered": n_current,
            "historical_members_discovered": n_historical,
            "ducklake_table": "cianfhoghlaim.education.ie.nui_members",
        }
    )


@asset(
    key=["nui_federation", "constituents_scrape"],
    group_name="nui_federation",
    compute_kind="scrape",
    description=(
        "Stage 1 — bulk_scrape each NUI member's home_url to keep "
        "the nui_members DuckLake table fresh."
    ),
    deps=[AssetKey(["nui_federation", "audit"])],
)
def nui_constituents_scrape(context) -> MaterializeResult:
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        nui_federation_source,
    )

    rows = list(
        nui_federation_source(destination=_DEFAULT_DESTINATION)
        .selected_resources["nui_members"]()
    )
    return MaterializeResult(metadata={"rows": len(rows)})


@asset(
    key=["nui_federation", "archive_ingest"],
    group_name="nui_federation",
    compute_kind="scrape",
    description=(
        "Stage 1 — scrape the NUI historical archive (pre-1908 QUB, "
        "the 3 Queen's Colleges, the Royal University merger)."
    ),
    deps=[AssetKey(["nui_federation", "audit"])],
)
def nui_archive_ingest(context) -> MaterializeResult:
    from dlt_sources.british_isles.ireland.education.university.official_docs import (
        nui_federation_source,
    )

    rows = list(
        nui_federation_source(destination=_DEFAULT_DESTINATION)
        .selected_resources["nui_archive"]()
    )
    return MaterializeResult(metadata={"archive_links": len(rows)})


__all__ = [
    "nui_archive_ingest",
    "nui_constituents_scrape",
    "nui_federation_audit",
]
