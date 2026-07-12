"""Spatial joins for the topic-frequency heatmap.

Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md
T6.13 (the topic-heatmap uses GeoParquet + Hilbert sorting).

This module is a thin wrapper around `cianfhoghlaim.tuatha.geospatial.spatial_joins`
for the per-subject topic-frequency data.
"""

from __future__ import annotations

from typing import Any

try:
    from cianfhoghlaim.tuatha.geospatial.spatial_joins import spatial_join_points_in_bbox
    SPATIAL_JOINS_AVAILABLE = True
except ImportError:
    SPATIAL_JOINS_AVAILABLE = False
    spatial_join_points_in_bbox = None


def topic_frequency_spatial_join(
    subject: str,
    language: str = "en",
    bbox: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Spatial join of topic-frequency points within a bounding box.

    Used by the topic-heatmap diagram (per cianfhoghlaim-leaving-cert-portal/
    spec.md Requirement R3 + docs/BROWN_AJAH_THEMING.md Theme 9 — the
    visual RAG).

    The data source is `oideachais.lc.<subject>.topic_frequency` (a
    GeoParquet file written by `geoparquet_writer.py` + Hilbert-sorted by
    `hilbert_indexing.py`).
    """
    if not SPATIAL_JOINS_AVAILABLE:
        return {"error": "Spatial joins not available", "subject": subject}

    # TODO: call spatial_join_points_in_bbox with the topic-frequency GeoParquet
    return {
        "subject": subject,
        "language": language,
        "bbox": bbox,
        "rows": [],
    }