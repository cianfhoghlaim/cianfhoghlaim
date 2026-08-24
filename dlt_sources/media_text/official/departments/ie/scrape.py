"""dlt_sources/media/official/departments/ie scrape DLT resource.

Éire non-police / non-defence departments. The police + defence +
DoD + DoJ + DFA + Oireachtas + President surface lives at
`dlt_sources/media/official/government/ie/`.
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

_IE_DEPARTMENTS: list[dict[str, str]] = [
    {
        "id": "doh_ie",
        "title": "Department of Health (Ireland)",
        "url": "https://www.gov.ie/en/department-of-health/",
        "rights_holder": "Department of Health (Ireland)",
        "licence": "PSI",
    },
    {
        "id": "doedu_ie",
        "title": "Department of Education (Ireland)",
        "url": "https://www.gov.ie/en/department-of-education/",
        "rights_holder": "Department of Education (Ireland)",
        "licence": "PSI",
    },
    {
        "id": "hse",
        "title": "Health Service Executive (HSE)",
        "url": "https://www.hse.ie/",
        "rights_holder": "Health Service Executive",
        "licence": "PSI",
    },
]


def _stable_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


@dlt.source(name="ie_departments")
def ie_departments_source(
    use_local_scrapes: bool | None = None,
    write_disposition: str = "merge",
):
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        pass

    @dlt.resource(
        name="ie_departments_pages",
        write_disposition=write_disposition,
        primary_key=("id", "source_url", "source_timestamp"),
    )
    def pages() -> Iterator[dict[str, Any]]:
        firecrawl_key_present = bool(os.environ.get("FIRECRAWL_API_KEY"))
        for src in _IE_DEPARTMENTS:
            source_timestamp = datetime.datetime.now(
                tz=datetime.UTC
            ).isoformat()
            record = {
                "id": src["id"],
                "title": src["title"],
                "jurisdiction": "ie_departments",
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
    "_IE_DEPARTMENTS",
    "_stable_hash",
    "ie_departments_source",
]
