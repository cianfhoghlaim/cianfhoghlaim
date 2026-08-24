"""
cianfhoghlaim.cianfhoghlaim.dlt.british_isles.ireland.law.gov_ie_law — Irish
Government (gov.ie) across ALL ministerial sub-departments.

Source: `https://www.gov.ie/en/` — the umbrella surface covering all
~16 ministerial departments:

- Department of Justice (DoJ)
- Department of Health (DoH)
- Department of Education (DES)
- Department of Business, Enterprise and Innovation (DBEI)
- Department of Environment, Climate and Communications (DECC)
- Department of Agriculture, Food and the Marine (DAFM)
- Department of Tourism, Culture, Arts, Gaeltacht, Sport and Media (DTCAGSM)
- Department of Housing, Local Government and Heritage (DHLGH)
- Department of Public Expenditure and Reform (DPER)
- Department of Rural and Community Development (DRCD)
- Department of Transport (DT)
- Department of Children, Equality, Disability, Integration and Youth (DCEDIY)
- Department of Further and Higher Education, Research, Innovation and Science (DFHERIS)
- Department of Social Protection (DSP)
- Department of Foreign Affairs (DFA)
- Department of Defence (DoD)
- Department of the Taoiseach
- Department of Finance

Covers 1 DLT resource:

- `pages` — press releases + publications + news + organisation pages

Honours `USE_LOCAL_SCRAPES=true` falling back to
`stedding/ingest_queue/gov.ie/`.

This is a superset of the existing `doj.py` source (which covers only
the DoJ sub-tree). The existing `doj` source is kept for backwards
compat; new consumers should use `gov_ie_law_source()` instead.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import structlog

import dlt_sources

logger = structlog.get_logger(__name__)

from dlt_sources.british_isles.ireland.education.curriculum import (  # type: ignore[import-not-found]
    _crawl_source,
)

GOV_IE_BASE = "https://www.gov.ie/en"

# Cover the umbrella surface (organisations + publications + news) plus
# the per-department sub-trees.
GOV_IE_PATHS = [
    "/organisation/*",
    "/en/news/*",
    "/en/publication/*",
    "/en/policy/*",
    "/en/press-release/*",
    # Per-department sub-trees
    "/en/organisation/department-of-justice/*",
    "/en/organisation/department-of-health/*",
    "/en/organisation/department-of-education/*",
    "/en/organisation/department-of-business/*",
    "/en/organisation/department-of-environment/*",
    "/en/organisation/department-of-agriculture/*",
    "/en/organisation/department-of-tourism-culture-arts-gaeltacht-sport-and-media/*",
    "/en/organisation/department-of-housing/*",
    "/en/organisation/department-of-public-expenditure-and-reform/*",
    "/en/organisation/department-of-rural-and-community-development/*",
    "/en/organisation/department-of-transport/*",
    "/en/organisation/department-of-children-equality-disability-integration-and-youth/*",
    "/en/organisation/department-of-further-and-higher-education/*",
    "/en/organisation/department-of-social-protection/*",
    "/en/organisation/department-of-foreign-affairs/*",
    "/en/organisation/department-of-defence/*",
    "/en/organisation/department-of-the-taoiseach/*",
    "/en/organisation/department-of-finance/*",
]


def _crawl_gov_ie_pages(max_pages: int = 800) -> Iterator[dict[str, Any]]:
    """Crawl gov.ie press releases + publications + news across all departments."""
    for page in _crawl_source(
        source_name="gov_ie.pages",
        base_url=GOV_IE_BASE,
        include_paths=GOV_IE_PATHS,
        max_pages=max_pages,
        max_depth=4,
    ):
        page["nation"] = "ie"
        page["domain"] = "law"
        page["entity"] = "gov_ie"
        page["entity_type"] = "press"
        yield page


@dlt.source(name="gov_ie_law")
def gov_ie_law_source(max_pages: int = 800):
    """DLT source for the Irish Government (gov.ie) law corpus.

    Returns 1 resource:

    - `pages` — gov.ie press releases + publications + news across all 16+
                ministerial departments

    Note: This is a superset of the existing `doj` source. New consumers
    should prefer `gov_ie_law_source()`. The `doj` source is kept for
    backwards compat with existing Dagster defs.
    """

    @dlt.resource(
        name="pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pages():
        yield from _crawl_gov_ie_pages(max_pages=max_pages)

    return pages
