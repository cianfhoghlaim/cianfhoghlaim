"""dlt_sources/media/official/departments/uk scrape DLT resource.

United Kingdom non-police / non-defence / non-MoD / non-Home-Office
departments. The police + defence + MoD + Home Office + FCDO + MoJ +
DoH surface lives at `dlt_sources/media/official/government/uk/`.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            spec.md § media-intel-acquisition-plan Requirement 5
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import uuid
from collections.abc import Iterator
from typing import Any

import dlt

_UK_DEPARTMENTS: list[dict[str, str]] = [
    {
        "id": "nhs_england",
        "title": "NHS England",
        "url": "https://www.england.nhs.uk/",
        "rights_holder": "NHS England",
        "licence": "OGL-3.0",
    },
    {
        "id": "dwp",
        "title": "Department for Work and Pensions",
        "url": "https://www.gov.uk/government/organisations/department-for-work-and-pensions",
        "rights_holder": "Department for Work and Pensions",
        "licence": "OGL-3.0",
    },
    {
        "id": "transport_uk",
        "title": "Department for Transport",
        "url": "https://www.gov.uk/government/organisations/department-for-transport",
        "rights_holder": "Department for Transport",
        "licence": "OGL-3.0",
    },
    {
        "id": "education_uk",
        "title": "Department for Education (UK)",
        "url": "https://www.gov.uk/government/organisations/department-for-education",
        "rights_holder": "Department for Education",
        "licence": "OGL-3.0",
    },
    {
        "id": "environment_uk",
        "title": "Department for Environment, Food and Rural Affairs",
        "url": "https://www.gov.uk/government/organisations/department-for-environment-food-rural-affairs",
        "rights_holder": "DEFRA",
        "licence": "OGL-3.0",
    },
]


def _stable_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


@dlt.source(name="uk_departments")
def uk_departments_source(
    use_local_scrapes: bool | None = None,
    write_disposition: str = "merge",
):
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        pass

    @dlt.resource(
        name="uk_departments_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _UK_DEPARTMENTS:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "uk_departments",
                "source_url": src["url"],
                "source_timestamp": source_timestamp,
                "rights_holder": src["rights_holder"],
                "licence": src["licence"],
                "provenance": {
                    "rights_holder": src["rights_holder"],
                    "licence": src["licence"],
                    "derivation_class": "fair_use_quote",
                    "shippable": False,
                    "shippable_art_path": None,
                },
            }
            record["_acquisition_id"] = str(uuid.uuid4())
            record["_firecrawl_plan"] = "plan_a_keyless"
            record["_firecrawl_key_present"] = firecrawl_key_present
            record["_content_hash"] = _stable_hash(record)
            yield record

    return pages(),


__all__ = [
    "_UK_DEPARTMENTS",
    "_stable_hash",
    "uk_departments_source",
]
