"""
Shared helpers split from geospatial/met_office.py

Phase 3D of openspec change.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from typing import Any

try:
    from cianfhoghlaim.dlt.common.http_client import met_office_climate_client, met_office_datahub_client
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


def _fetch_climate_monthly(station_name: str) -> Iterator[dict[str, Any]]:
    """Fetch historic monthly climate data (public)."""
    # Met Office historic climate data is available at:
    # https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/{station}data.txt

    station_slug = station_name.lower().replace(" ", "").replace("-", "")

    factory = _get_climate_factory()
    with factory.create_client() as client:
        try:
            response = client.get(f"/climate/stationdata/{station_slug}data.txt")
            if response.status_code != 200:
                return

            lines = response.text.strip().split("\n")

            # Skip header lines (usually 5-7 lines)
            data_started = False
            for line in lines:
                if line.strip().startswith("yyyy"):
                    data_started = True
                    continue

                if not data_started or not line.strip():
                    continue

                # Parse data line: yyyy mm tmax tmin af rain sun
                parts = line.split()
                if len(parts) < 7:
                    continue

                try:
                    year = int(parts[0])
                    month = int(parts[1])

                    # Handle missing values (marked as ---)
                    def safe_float(val: str) -> float | None:
                        if val.strip("-") == "" or val == "---":
                            return None
                        # Remove any trailing asterisks (provisional data)
                        return float(val.rstrip("*#"))

                    yield {
                        "station_name": station_name,
                        "year": year,
                        "month": month,
                        "max_temp_c": safe_float(parts[2]),
                        "min_temp_c": safe_float(parts[3]),
                        "air_frost_days": safe_float(parts[4]),
                        "rainfall_mm": safe_float(parts[5]),
                        "sunshine_hours": safe_float(parts[6]) if len(parts) > 6 else None,
                    }
                except (ValueError, IndexError):
                    continue

        except Exception:
            pass

def _fetch_observations(
    station_id: str,
    from_date: datetime,
    to_date: datetime,
) -> Iterator[dict[str, Any]]:
    """Fetch observations for a station."""
    factory = _get_datahub_factory()
    with factory.create_client() as client:
        response = client.get(
            "/point/daily",
            params={
                "latitude": "51.5",  # Will be replaced with station lookup
                "longitude": "-0.1",
                "from": from_date.isoformat() + "Z",
                "to": to_date.isoformat() + "Z",
            },
        )

        if response.status_code == 200:
            data = response.json()
            for feature in data.get("features", []):
                props = feature.get("properties", {})
                params = props.get("timeSeries", [])

                for ts in params:
                    yield {
                        "station_id": station_id,
                        "observation_date": ts.get("time"),
                        "max_temp_c": ts.get("maxScreenAirTemp"),
                        "min_temp_c": ts.get("minScreenAirTemp"),
                        "rainfall_mm": ts.get("totalPrecipAmount"),
                        "sunshine_hours": ts.get("totalSunshineDuration"),
                        "wind_speed_knots": ts.get("max10mWindGust"),
                        "humidity_percent": ts.get("screenRelativeHumidity"),
                    }

def _fetch_public_stations() -> list[dict[str, Any]]:
    """Fetch station data from public Met Office files."""
    # Historic climate stations (public data)
    stations = [
        {"station_id": "17", "station_name": "Armagh", "latitude": 54.35, "longitude": -6.65, "country": "Northern Ireland"},
        {"station_id": "23", "station_name": "Ballypatrick Forest", "latitude": 55.18, "longitude": -6.15, "country": "Northern Ireland"},
        {"station_id": "35", "station_name": "Bradford", "latitude": 53.81, "longitude": -1.77, "country": "England"},
        {"station_id": "44", "station_name": "Braemar", "latitude": 57.01, "longitude": -3.40, "country": "Scotland"},
        {"station_id": "56", "station_name": "Cambridge NIAB", "latitude": 52.25, "longitude": 0.10, "country": "England"},
        {"station_id": "62", "station_name": "Cardiff", "latitude": 51.48, "longitude": -3.18, "country": "Wales"},
        {"station_id": "82", "station_name": "Chivenor", "latitude": 51.09, "longitude": -4.15, "country": "England"},
        {"station_id": "99", "station_name": "Durham", "latitude": 54.77, "longitude": -1.58, "country": "England"},
        {"station_id": "113", "station_name": "Eskdalemuir", "latitude": 55.31, "longitude": -3.21, "country": "Scotland"},
        {"station_id": "235", "station_name": "Oxford", "latitude": 51.76, "longitude": -1.26, "country": "England"},
        {"station_id": "238", "station_name": "Paisley", "latitude": 55.85, "longitude": -4.43, "country": "Scotland"},
        {"station_id": "262", "station_name": "Ross-on-Wye", "latitude": 51.91, "longitude": -2.58, "country": "Wales"},
        {"station_id": "282", "station_name": "Sheffield", "latitude": 53.38, "longitude": -1.49, "country": "England"},
        {"station_id": "292", "station_name": "Stornoway", "latitude": 58.21, "longitude": -6.32, "country": "Scotland"},
        {"station_id": "310", "station_name": "Valley", "latitude": 53.25, "longitude": -4.53, "country": "Wales"},
        {"station_id": "351", "station_name": "Whitby", "latitude": 54.48, "longitude": -0.61, "country": "England"},
        {"station_id": "359", "station_name": "Wick", "latitude": 58.45, "longitude": -3.09, "country": "Scotland"},
        {"station_id": "376", "station_name": "Yeovilton", "latitude": 51.00, "longitude": -2.64, "country": "England"},
    ]
    return stations

def _fetch_stations() -> list[dict[str, Any]]:
    """Fetch list of weather stations."""
    factory = _get_datahub_factory()
    with factory.create_client() as client:
        response = client.get("/point/all/sites")

        if response.status_code != 200:
            # Fallback to public station list
            return _fetch_public_stations()

        data = response.json()
        stations = []

        for site in data.get("features", []):
            props = site.get("properties", {})
            coords = site.get("geometry", {}).get("coordinates", [0, 0])

            stations.append({
                "station_id": props.get("id"),
                "station_name": props.get("name"),
                "latitude": coords[1] if len(coords) > 1 else None,
                "longitude": coords[0] if len(coords) > 0 else None,
                "elevation_m": props.get("elevation"),
                "region": props.get("region"),
                "country": props.get("country", "United Kingdom"),
            })

        return stations

def _get_climate_factory():
    """Get HTTP client factory for Met Office public climate data."""
    return met_office_climate_client()

def _get_datahub_factory():
    """Get HTTP client factory for Met Office DataHub API."""
    return met_office_datahub_client()
