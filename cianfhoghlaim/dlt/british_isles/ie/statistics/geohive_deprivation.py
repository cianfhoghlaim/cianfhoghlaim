"""
Statistics IE source: geohive_deprivation_source

Split from geospatial/geohive.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from dlt.sources import TDataItem

try:
    from shared.http import (  # noqa: F401
        arcgis_geohive_client,
        cso_pxstat_client,
        data_gov_ie_client,
    )
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._geohive_helpers import (
    _get_data_gov_factory,
)


def geohive_deprivation_source() -> list:
    """
    Pobal HP Deprivation Index data for Small Areas.

    The HP Deprivation Index provides a relative measure of
    deprivation for each Small Area based on Census 2016 data.
    """

    @dlt.resource(
        name="hp_deprivation",
        primary_key="sa_2016",
        write_disposition="replace",
    )
    def hp_deprivation() -> Iterator[TDataItem]:
        """HP Deprivation Index scores by Small Area."""
        # Pobal HP Index endpoint (from data.gov.ie)
        factory = _get_data_gov_factory()
        with factory.create_client() as client:
            response = client.get(
                "/datastore_search",
                params={
                    "resource_id": "hp-deprivation-index-2016",
                    "limit": 32000,  # All Small Areas
                },
            )

            if response.status_code == 200:
                data = response.json()
                for record in data.get("result", {}).get("records", []):
                    yield {
                        "sa_2016": record.get("SA_GUID_2016"),
                        "hp_score": record.get("HP_Score"),
                        "hp_decile": record.get("HP_Decile"),
                        "affluence_deprivation": record.get("Afflu_Depv"),
                        "demographic_growth_decline": record.get("Demo_Grwth_Dec"),
                        "age_dependency": record.get("Age_Dep"),
                        "lone_parent": record.get("Lone_Parent"),
                        "primary_education_only": record.get("Prim_Ed_Only"),
                        "third_level_education": record.get("Third_Level"),
                        "unemployment_rate": record.get("Unemp_Rate"),
                    }

    return [hp_deprivation]
