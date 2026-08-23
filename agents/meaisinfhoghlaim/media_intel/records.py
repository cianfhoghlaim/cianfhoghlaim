"""agents.meaisinfhoghlaim.media_intel.records — the
MediaDescriptor record builder.

Lives in its own module to avoid the circular import
between `__init__.py` and `media_descriptor_agent.py`.

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            design.md § 1 (the 7-axis MediaDescriptor schema)
"""
from __future__ import annotations

import datetime
import uuid
from typing import Any


def make_media_descriptor_record(
    *,
    work: str,
    medium: str,
    language: str,
    source_url: str,
    power_event: dict[str, Any],
    visual_grammar: dict[str, Any],
    palette: dict[str, Any],
    vfx_vocabulary: dict[str, Any],
    narrative_beat: dict[str, Any],
    transferability: dict[str, Any],
    rights_holder: str,
    licence: str,
    derivation_class: str = "description_only",
) -> dict[str, Any]:
    """Build the canonical MediaDescriptor record.

    Per the design.md § 1.4 "no graphics-from-graphics"
    invariant, every record has `shippable: False` enforced.
    Per the design.md § 1.2 the 7 axes are the canonical
    shape.
    """
    return {
        "id": str(uuid.uuid4()),
        "work": work,
        "medium": medium,
        "language": language,
        "source_url": source_url,
        "source_timestamp": datetime.datetime.now(
            tz=datetime.UTC
        ).isoformat(),
        "power_event": power_event,
        "visual_grammar": visual_grammar,
        "palette": palette,
        "vfx_vocabulary": vfx_vocabulary,
        "narrative_beat": narrative_beat,
        "transferability": transferability,
        "provenance": {
            "rights_holder": rights_holder,
            "licence": licence,
            "derivation_class": derivation_class,
            "shippable": False,
            "shippable_art_path": None,
        },
    }
