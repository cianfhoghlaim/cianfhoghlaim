"""
Statistics IE source: met_office_source

Split from geospatial/met_office.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timedelta

import dlt
from dlt.sources import TDataItem

try:
    from shared.http import met_office_climate_client, met_office_datahub_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._met_office_helpers import (
    _fetch_climate_monthly,
    _fetch_observations,
    _fetch_public_stations,
    _fetch_stations,
)


def met_office_source(
    include_historic_climate: bool = True,
    days_back: int = 30,
) -> list:
    """
    UK weather data from Met Office DataHub.

    Args:
        include_historic_climate: Whether to fetch monthly climate summaries
        days_back: Number of days of observations to fetch

    Returns:
        List of DLT resources
    """

    @dlt.resource(
        name="stations",
        primary_key="station_id",
        write_disposition="replace",
    )
    def stations() -> Iterator[TDataItem]:
        """Met Office weather stations."""
        yield from _fetch_stations()

    @dlt.resource(
        name="observations",
        primary_key="id",
        write_disposition="merge",
    )
    def observations() -> Iterator[TDataItem]:
        """Daily weather observations from stations."""
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days_back)

        for station in _fetch_public_stations():
            station_id = station["station_id"]

            for obs in _fetch_observations(station_id, from_date, to_date):
                obs_date = obs.get("observation_date", "")
                yield {
                    "id": f"{station_id}_{obs_date}",
                    **obs,
                }

    @dlt.resource(
        name="climate_monthly",
        primary_key="id",
        write_disposition="replace",
    )
    def climate_monthly() -> Iterator[TDataItem]:
        """Historic monthly climate summaries."""
        if not include_historic_climate:
            return

        # Stations with public historic data
        historic_stations = [
            "Armagh", "Bradford", "Braemar", "Cambridge NIAB",
            "Cardiff", "Durham", "Eskdalemuir", "Oxford",
            "Sheffield", "Stornoway", "Whitby", "Wick",
        ]

        for station_name in historic_stations:
            for record in _fetch_climate_monthly(station_name):
                yield {
                    "id": f"{station_name}_{record['year']}_{record['month']:02d}",
                    **record,
                }

    return [stations, observations, climate_monthly]
