"""dlt_sources/media/official/departments/wls scrape DLT resource.

Wales non-police / non-defence departments.
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

_WLS_DEPARTMENTS: list[dict[str, str]] = [
    {
        "id": "nhs_wales",
        "title": "NHS Wales (Public Health Wales)",
        "url": "https://phw.nhs.wales/",
        "rights_holder": "NHS Wales",
        "licence": "OGL-3.0",
    },
    {
        "id": "health_wales",
        "title": "Health Education and Improvement Wales (HEIW)",
        "url": "https://heiw.nhs.wales/",
        "rights_holder": "HEIW",
        "licence": "OGL-3.0",
    },
    {
        "id": "welsh_government",
        "title": "Welsh Government",
        "url": "https://www.gov.wales/",
        "rights_holder": "Welsh Government",
        "licence": "OGL-3.0",
    },
]


def _stable_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


@dlt.source(name="wls_departments")
def wls_departments_source(
    use_local_scrapes: bool | None = None,
    write_disposition: str = "merge",
):
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        pass

    @dlt.resource(
        name="wls_departments_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _WLS_DEPARTMENTS:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "wls_departments",
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
    "_WLS_DEPARTMENTS",
    "_stable_hash",
    "wls_departments_source",
]
