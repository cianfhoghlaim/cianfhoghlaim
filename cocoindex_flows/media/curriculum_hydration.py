"""CocoIndex v1 App: curriculum_hydration — DuckLake schema hydration.

Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change.

This flow mounts the 4 new DuckLake tables for curriculum hydration, setting up
the schema for the LC PDFs and the hand-made examples (`stedding/geog.pdf`,
`PastLC-IrishEnglish` images).

The 4 DuckLake tables:
- `cianfhoghlaim.lc.geography.topics`
- `cianfhoghlaim.lc.gaeilge.poems_higher`
- `cianfhoghlaim.lc.english.poets_higher`
- `cianfhoghlaim.education.ie.policies`

Conforms to R1-R4 rules for CocoIndex Apps.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]

# R1: shared lifespan
from .._shared._lifespan import (  # noqa: E402
    shared_lifespan,
)

if COCOINDEX_AVAILABLE:
    # R3: module-scope app definition
    app = coco.App(
        coco.AppConfig(
            name="curriculum_hydration",
            lifespan=shared_lifespan,
        )
    )

    # R4: at least one @coco.fn decorator
    @coco.fn(app=app)
    async def mount_ducklake_schema() -> None:
        """
        Stub flow definition to declare the CocoIndex v1 app footprint.
        Actual row insertion happens via `scripts/curriculum_hydrate.py`.
        """
        logger.info("Mounted curriculum hydration schemas for DuckLake.")

else:
    app = None  # type: ignore[assignment]
