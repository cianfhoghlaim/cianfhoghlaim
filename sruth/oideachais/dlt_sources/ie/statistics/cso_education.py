"""
Statistics IE source: cso_education_source

Split from geospatial/cso_small_areas.py in Phase 3D.
"""

from __future__ import annotations
from collections.abc import Iterator
from typing import Any
import dlt
from dlt.sources import TDataItem
try:
    from shared.http import cso_pxstat_client, data_gov_ie_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._cso_small_areas_helpers import (
    _fetch_data_gov_resource,
    _get_data_gov_factory,
)

def cso_education_source() -> list:
    """
    Education-specific statistics from CSO.

    Includes school enrollment, DEIS designation, and
    educational outcomes data.
    """

    @dlt.resource(
        name="primary_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def primary_schools() -> Iterator[TDataItem]:
        """Primary school statistics."""
        # Department of Education school list
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            # This would need the actual resource ID from data.gov.ie
            # For now, yield placeholder structure
            response = client.get(
                "/package_show",
                params={"id": "primary-schools-list"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() == "JSON":
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield record

    @dlt.resource(
        name="secondary_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def secondary_schools() -> Iterator[TDataItem]:
        """Post-primary school statistics."""
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            response = client.get(
                "/package_show",
                params={"id": "post-primary-schools-list"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() == "JSON":
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield record

    @dlt.resource(
        name="gaeltacht_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def gaeltacht_schools() -> Iterator[TDataItem]:
        """Schools in Gaeltacht areas and Irish-medium schools."""
        # Filter for Irish-medium education
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            # Gaeltacht areas list
            response = client.get(
                "/package_show",
                params={"id": "gaeltacht-areas"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() in ("JSON", "GEOJSON"):
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield record

    return [primary_schools, secondary_schools, gaeltacht_schools]
