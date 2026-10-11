"""CocoIndex v1 App: media_power_embedding — cross-media power descriptors.

Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change.

This flow:
1. Receives the `MediaPowerDescriptor` record (from BAML extractions).
2. Enforces the invariant that `provenance.shippable` MUST be `False`.
3. Embeds the design pattern via the shared BAAI/bge-m3 embedder.
4. Mounts the `media.media_power_descriptors` LanceDB table, keyed by
   `(media_class, key)`.

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
            name="media_power_embedding",
            lifespan=shared_lifespan,
        )
    )

    # R4: at least one @coco.fn decorator
    @coco.fn(app=app)
    async def embed_power_descriptor(
        descriptor_dict: dict[str, Any],
        media_class: str,
        media_key: str
    ) -> None:
        """Embeds a MediaPowerDescriptor into LanceDB."""

        # Enforce provenance shippable = False (Invariant guard)
        prov = descriptor_dict.get("provenance", {})
        if prov.get("shippable") is not False:
            logger.warning(
                "media_intel_shippable_violation: Dropping descriptor for %s. "
                "Shippable must be exactly False.", media_key
            )
            return

        # Prepare text representation for the embedder
        text_to_embed = json.dumps({
            "power_event": descriptor_dict.get("power_event"),
            "visual_grammar": descriptor_dict.get("visual_grammar"),
            "palette": descriptor_dict.get("palette"),
            "comparative_lens": descriptor_dict.get("comparative_lens")
        }, sort_keys=True)

        # Retrieve ContextKeys
        embedder = coco.use(EMBEDDER)
        db = coco.use(LANCE_DB)

        # Embed the text
        embedding = await embedder.embed(text_to_embed)

        # Insert into LanceDB
        table = await db.open_table("media.media_power_descriptors", create_if_not_exists=True)

        # We use an append mode; in a full deployment, this might use merge_insert
        # based on (media_class, media_key) keys.
        await table.add([{
            "media_class": media_class,
            "media_key": media_key,
            "descriptor_json": json.dumps(descriptor_dict),
            "embedding": embedding
        }], mode="append")

else:
    app = None  # type: ignore[assignment]
