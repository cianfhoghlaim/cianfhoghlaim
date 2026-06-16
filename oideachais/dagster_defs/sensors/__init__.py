"""
Dagster Sensors for Celtic Education Platform.

Sensor Groups:
- Ireland Curriculum: Unified curriculum freshness (recommended)
- Ireland Domain: Curriculum sitemap, exam papers (legacy)
- UK sensors: DfE, SQA, Wales curriculum
- Celtic sensors: Duchas, Tearma updates
- Geospatial sensors: GeoHive, Met Office
- Author-archive: directory-watch for UoG / Gemini / Takeout
- Leabharlann: directory-watch for books / zotero / takeout v1
"""
from __future__ import annotations

from .author_archive_sensors import author_archive_sensors
from .curriculum_freshness import curriculum_freshness_sensors
from .domain_sensors import domain_sensors
from .leabharlann_sensors import leabharlann_sensors

# All sensors combined
all_sensors = (
    list(domain_sensors)
    + list(curriculum_freshness_sensors)
    + list(author_archive_sensors)
    + list(leabharlann_sensors)
)

__all__ = [
    "all_sensors",
    "domain_sensors",
    "curriculum_freshness_sensors",
    "author_archive_sensors",
    "leabharlann_sensors",
]
