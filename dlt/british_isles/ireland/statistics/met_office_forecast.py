"""
Statistics IE source: met_office_forecast_source

Split from geospatial/met_office.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

import dlt
from dlt.sources import TDataItem

try:
    from cianfhoghlaim.dlt.common.http_client import met_office_climate_client, met_office_datahub_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._met_office_helpers import (
    _get_datahub_factory,
)


def met_office_forecast_source(
    latitude: float = 53.5,
    longitude: float = -7.0,
) -> list:
    """
    Met Office weather forecasts for a location.

    Args:
        latitude: Location latitude
        longitude: Location longitude

    Returns:
        List of DLT resources
    """

    @dlt.resource(
        name="forecast_daily",
        primary_key="id",
        write_disposition="replace",
    )
    def forecast_daily() -> Iterator[TDataItem]:
        """Daily weather forecast."""
        factory = _get_datahub_factory()
        with factory.create_client() as client:
            response = client.get(
                "/point/daily",
                params={
                    "latitude": str(latitude),
                    "longitude": str(longitude),
                },
            )

            if response.status_code == 200:
                data = response.json()
                for feature in data.get("features", []):
                    props = feature.get("properties", {})

                    for ts in props.get("timeSeries", []):
                        forecast_time = ts.get("time", "")
                        yield {
                            "id": f"{latitude}_{longitude}_{forecast_time}",
                            "latitude": latitude,
                            "longitude": longitude,
                            "forecast_time": forecast_time,
                            "max_temp_c": ts.get("dayMaxScreenTemperature"),
                            "min_temp_c": ts.get("nightMinScreenTemperature"),
                            "precipitation_prob": ts.get("dayProbabilityOfPrecipitation"),
                            "weather_code": ts.get("daySignificantWeatherCode"),
                        }

    return [forecast_daily]
