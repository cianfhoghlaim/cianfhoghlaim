"""
Geospatial Tools for Agno Agents.

Provides location-based education queries:
- School locations and catchment areas
- Gaeltacht areas
- Regional education statistics
- Distance calculations
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from agno.tools import Toolkit


class GeospatialTools(Toolkit):
    """
    Agno toolkit for geospatial education queries.

    Uses GeoParquet indexes for efficient spatial search.
    """

    def __init__(
        self,
        mcp_endpoint: str | None = None,
        default_radius_km: float = 10.0,
    ):
        super().__init__(name="geospatial")
        self.mcp_endpoint = mcp_endpoint or os.getenv(
            "MCP_ENDPOINT", "http://localhost:3000/api/mcp"
        )
        self.default_radius_km = default_radius_km

        # Register tools
        self.register(self.search_schools_near)
        self.register(self.get_gaeltacht_areas)
        self.register(self.get_school_by_roll)
        self.register(self.get_regional_statistics)
        self.register(self.calculate_distance)

    async def _mcp_call(self, method: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Make a call to the MCP endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.mcp_endpoint,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": method,
                        "arguments": arguments,
                    },
                },
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", {})

    def search_schools_near(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        school_type: str | None = None,
        irish_medium: bool | None = None,
        limit: int = 20,
    ) -> str:
        """
        Search for schools near a location.

        Args:
            latitude: Latitude of center point.
            longitude: Longitude of center point.
            radius_km: Search radius in kilometers.
            school_type: Filter by type (primary, secondary, special).
            irish_medium: Filter for Gaelscoileanna.
            limit: Maximum results.

        Returns:
            JSON string with nearby schools.
        """
        import asyncio
        import json

        async def _search():
            arguments = {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km,
                "limit": limit,
            }
            if school_type:
                arguments["school_type"] = school_type
            if irish_medium is not None:
                arguments["irish_medium"] = irish_medium

            return await self._mcp_call("geospatial-schools-near", arguments)

        result = asyncio.get_event_loop().run_until_complete(_search())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_gaeltacht_areas(
        self,
        county: str | None = None,
        include_breac_gaeltacht: bool = True,
    ) -> str:
        """
        Get Gaeltacht area information.

        Args:
            county: Filter by county (e.g., Galway, Donegal, Kerry).
            include_breac_gaeltacht: Include Breac-Ghaeltacht areas.

        Returns:
            JSON string with Gaeltacht areas and statistics.
        """
        import asyncio
        import json

        async def _get():
            arguments = {"include_breac_gaeltacht": include_breac_gaeltacht}
            if county:
                arguments["county"] = county

            return await self._mcp_call("geospatial-gaeltacht", arguments)

        result = asyncio.get_event_loop().run_until_complete(_get())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_school_by_roll(
        self,
        roll_number: str,
    ) -> str:
        """
        Get detailed information about a school by roll number.

        Args:
            roll_number: School roll number (e.g., 19254A).

        Returns:
            JSON string with school details including location.
        """
        import asyncio
        import json

        async def _get():
            arguments = {"roll_number": roll_number}
            return await self._mcp_call("geospatial-school-by-roll", arguments)

        result = asyncio.get_event_loop().run_until_complete(_get())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_regional_statistics(
        self,
        region: str,
        metric: str = "enrollment",
        level: str | None = None,
    ) -> str:
        """
        Get education statistics for a region.

        Args:
            region: Region name (county, province, or 'national').
            metric: Statistic type (enrollment, irish_medium, attainment).
            level: Education level filter.

        Returns:
            JSON string with regional statistics.
        """
        import asyncio
        import json

        async def _get():
            arguments = {"region": region, "metric": metric}
            if level:
                arguments["level"] = level

            return await self._mcp_call("geospatial-statistics", arguments)

        result = asyncio.get_event_loop().run_until_complete(_get())
        return json.dumps(result, indent=2, ensure_ascii=False)

    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> str:
        """
        Calculate distance between two points.

        Uses Haversine formula for great-circle distance.

        Args:
            lat1: Latitude of first point.
            lon1: Longitude of first point.
            lat2: Latitude of second point.
            lon2: Longitude of second point.

        Returns:
            JSON string with distance in kilometers.
        """
        import json
        import math

        # Haversine formula
        R = 6371.0  # Earth's radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return json.dumps(
            {
                "distance_km": round(distance, 2),
                "from": {"latitude": lat1, "longitude": lon1},
                "to": {"latitude": lat2, "longitude": lon2},
            },
            indent=2,
        )
