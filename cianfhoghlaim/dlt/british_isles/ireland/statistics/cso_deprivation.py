"""
Statistics IE source: cso_deprivation_source

Split from geospatial/cso_small_areas.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from dlt.sources import TDataItem

try:
    from cianfhoghlaim.dlt.common.http_client import cso_pxstat_client, data_gov_ie_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._cso_small_areas_helpers import (
    _fetch_data_gov_resource,
    _get_data_gov_factory,
)


def cso_deprivation_source() -> list:
    """
    Deprivation indices for Irish Small Areas.

    Includes Pobal HP Deprivation Index and related measures.
    """

    @dlt.resource(
        name="hp_deprivation_2022",
        primary_key="sa_2022",
        write_disposition="replace",
    )
    def hp_deprivation() -> Iterator[TDataItem]:
        """
        Pobal HP Deprivation Index 2022.

        The HP Index measures relative affluence and deprivation
        based on demographic, social, and economic indicators.
        """
        # Pobal HP Index data from data.gov.ie
        # Resource ID needs to be updated when 2022 data is published
        yield from _fetch_data_gov_resource("hp-deprivation-index-2022")

    @dlt.resource(
        name="deis_schools",
        primary_key="roll_number",
        write_disposition="replace",
    )
    def deis_schools() -> Iterator[TDataItem]:
        """
        DEIS (Delivering Equality of Opportunity in Schools) designated schools.

        DEIS provides additional resources to schools serving
        disadvantaged communities.
        """
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            response = client.get(
                "/package_show",
                params={"id": "deis-schools"},
            )

            if response.status_code == 200:
                data = response.json()
                resources = data.get("result", {}).get("resources", [])

                for resource in resources:
                    if resource.get("format", "").upper() == "JSON":
                        for record in _fetch_data_gov_resource(resource["id"]):
                            yield {
                                "roll_number": record.get("Roll_Number", record.get("roll_number")),
                                "school_name": record.get("School_Name", record.get("school_name")),
                                "deis_band": record.get("DEIS_Band", record.get("deis_band")),
                                "county": record.get("County", record.get("county")),
                                "school_type": record.get("School_Type", record.get("school_type")),
                            }

    return [hp_deprivation, deis_schools]
