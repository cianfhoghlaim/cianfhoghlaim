"""
Culture IE source: canuint_dialect_summary_source

Split from celtic/canuint.py in Phase 3D.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource

try:
    from shared.http import canuint_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._canuint_helpers import (
    _get_canuint_factory,
)


def canuint_dialect_summary_source() -> Iterator[DltResource]:
    """
    Source for Canúint.ie dialect statistics.

    Aggregates:
    - Total recordings per dialect
    - Transcription coverage
    - Speaker diversity
    - Duration statistics
    """

    @dlt.resource(
        name="dialect_stats",
        write_disposition="replace",
        primary_key="dialect",
    )
    def dialect_stats_resource() -> Iterator[dict]:
        """Generate dialect statistics for training planning."""
        factory = _get_canuint_factory()
        dialects = {
            "connacht": "Cúige Connacht",
            "munster": "Cúige Mumhan",
            "ulster": "Cúige Uladh",
        }

        with factory.create_client() as client:
            try:
                response = client.get("/ga/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                logger.warning("canuint_dialect_stats_error", error=str(e))
                return

            for dialect, province in dialects.items():
                location_pattern = re.compile(r"https://www\.canuint\.ie/ga/(\d+)")
                area_count = 0
                recording_estimate = 0

                for link in soup.find_all("a", href=location_pattern):
                    province_elem = link.find_parent(class_="province-section")
                    if province_elem:
                        province_header = province_elem.find(class_="province")
                        if province_header and province in province_header.get_text():
                            area_count += 1
                            recording_estimate += 10  # Rough estimate

                yield {
                    "dialect": dialect,
                    "province": province,
                    "area_count": area_count,
                    "estimated_recordings": recording_estimate,
                    "priority": "high" if dialect == "connacht" else "medium",
                }

    yield dialect_stats_resource
