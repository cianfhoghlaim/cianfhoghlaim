"""CocoIndex v1 App: wheel_of_time_embedding — per-chapter WoT power schemas.

Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change.

This flow:
1. Receives the `WotChapterSchema` record (from BAML extractions).
2. Enforces the invariant that `provenance.shippable` MUST be `False`.
3. Embeds the per-chapter power events + summary via the shared BAAI/bge-m3 embedder.
4. Mounts the `media.wheel_of_time_chapters` LanceDB table, keyed by
   `(book_index, chapter_number)`.

Conforms to R1-R4 rules for CocoIndex Apps.
"""
from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Lazy cocoindex + lancedb imports
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]

# R1: shared lifespan + canonical ContextKeys
from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

if COCOINDEX_AVAILABLE:
    # R3: module-scope app definition
    app = coco.App(
        coco.AppConfig(
            name="wheel_of_time_embedding",
            lifespan=shared_lifespan,
        )
    )

    # R4: at least one @coco.fn decorator
    @coco.fn(app=app)
    async def embed_wot_chapter(
        chapter_dict: dict[str, Any]
    ) -> None:
        """Embeds a WotChapterSchema into LanceDB."""

        # Enforce provenance shippable = False (Invariant guard)
        prov = chapter_dict.get("provenance", {})
        if prov.get("shippable") is not False:
            logger.warning(
                "media_intel_shippable_violation: Dropping WoT chapter %s-%s. "
                "Shippable must be exactly False.",
                chapter_dict.get("book_index"), chapter_dict.get("chapter_number")
            )
            return

        book_index = chapter_dict.get("book_index", 0)
        chapter_number = chapter_dict.get("chapter_number", 0)

        # Prepare text representation for the embedder
        text_to_embed = json.dumps({
            "summary": chapter_dict.get("summary"),
            "power_events": chapter_dict.get("power_events"),
            "characters": chapter_dict.get("characters"),
        }, sort_keys=True)

        # Retrieve ContextKeys
        embedder = coco.use(EMBEDDER)
        db = coco.use(LANCE_DB)

        # Embed the text
        embedding = await embedder.embed(text_to_embed)

        # Insert into LanceDB
        table = await db.open_table("media.wheel_of_time_chapters", create_if_not_exists=True)

        await table.add([{
            "book_index": book_index,
            "chapter_number": chapter_number,
            "chapter_json": json.dumps(chapter_dict),
            "embedding": embedding
        }], mode="append")

else:
    app = None  # type: ignore[assignment]
