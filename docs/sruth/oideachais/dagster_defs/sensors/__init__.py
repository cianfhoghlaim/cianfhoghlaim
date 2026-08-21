"""
Dagster Sensors for Celtic Education Platform.

Sensor Groups:
- Ireland Curriculum: Unified curriculum freshness (recommended)
- Ireland Domain: Curriculum sitemap, exam papers (legacy)
- UK sensors: DfE, SQA, Wales curriculum
- Celtic sensors: Duchas, Tearma updates
- Geospatial sensors: GeoHive, Met Office
"""

from __future__ import annotations

from .domain_sensors import domain_sensors
from .curriculum_freshness import curriculum_freshness_sensors

# All sensors combined
all_sensors = domain_sensors + curriculum_freshness_sensors

__all__ = [
    "all_sensors",
    "domain_sensors",
    "curriculum_freshness_sensors",
]
