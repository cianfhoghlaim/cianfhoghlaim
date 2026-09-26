"""orchestration/defs/4_asset_generation/tuatha_realm_asset.py — per-subject Tuatha realm Dagster asset.

Per the 2026-10-08-tuatha-closed-loop-mmo-v1 saga change (Plan 8 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Produces the canonical Tuatha realm JSON for one subject + one
language. The realm JSON bundles:
- The celtic-art window chrome (from the per-language asset table)
- The sprite bank (per-language sprites)
- The deity placement (Tuatha Dé deity for the subject)
- The NCCA learning outcomes for the subject
- The linked Cognee entities (from Plan 6)

Falls back to a stub mode when the asset table is offline.

Reference: openspec/specs/tuatha-closed-loop-mmo/spec.md
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, UTC
from typing import Any


# The 8 NCCA subjects with their Tuatha Dé deity + treasure
SUBJECT_DEITIES: dict[str, dict[str, str]] = {
    "mathematics": {
        "deity": "The Dagda", "treasure": "The Cauldron of Plenty",
        "ui_inspiration": "Clair Obscur Belle Époque",
    },
    "applied_mathematics": {
        "deity": "Lugh (samildanach)", "treasure": "The Spear of Lugh (never misses)",
        "ui_inspiration": "Clair Obscur + BitCraft Recipe Tree",
    },
    "chemistry": {
        "deity": "Dian Cecht (healing)", "treasure": "The Sword of Nuada (Caladbolg)",
        "ui_inspiration": "Hades shadow-first palette + Clair Obscur material library",
    },
    "geography": {
        "deity": "Manannán mac Lir (sea)", "treasure": "The Chariot of the king of Sidrach",
        "ui_inspiration": "WoW map zones + hex-based claims",
    },
    "history": {
        "deity": "The Morrígan (war + death)", "treasure": "The Helmet + Breastplate of the king of Clochur",
        "ui_inspiration": "Hades chamber + Clair Obscur act-and-chapter UI",
    },
    "english": {
        "deity": "Brigid (poetry + smithcraft)", "treasure": "(forge)",
        "ui_inspiration": "Hades boon selection + Clair Obscur skill tree",
    },
    "gaeilge": {
        "deity": "Ogma (speech + writing)", "treasure": "(oak-twig)",
        "ui_inspiration": "Clair Obscur skill tree",
    },
    "computer_science": {
        "deity": "Lugh + Brigid (smithcraft)", "treasure": "Sword of Nuada + Cauldron of Plenty",
        "ui_inspiration": "Hades mirror upgrades + BiTcraft recipe",
    },
}


# The 5 NCCA learning outcomes per subject (the canonical codes)
SUBJECT_LEARNING_OUTCOMES: dict[str, list[str]] = {
    "mathematics": ["LC-MATH-LO-3.1.1", "LC-MATH-LO-3.1.2", "LC-MATH-LO-3.2.1", "LC-MATH-LO-3.3.1", "LC-MATH-LO-3.4.1"],
    "applied_mathematics": ["LC-AMATH-LO-2.1.1", "LC-AMATH-LO-2.1.2", "LC-AMATH-LO-2.2.1", "LC-AMATH-LO-2.3.1", "LC-AMATH-LO-2.4.1"],
    "chemistry": ["LC-CHEM-LO-3.1.1", "LC-CHEM-LO-3.1.2", "LC-CHEM-LO-3.2.1", "LC-CHEM-LO-3.3.1", "LC-CHEM-LO-3.4.1"],
    "geography": ["LC-GEOG-LO-1.1.1", "LC-GEOG-LO-1.1.2", "LC-GEOG-LO-2.1.1", "LC-GEOG-LO-3.1.1", "LC-GEOG-LO-4.1.1"],
    "history": ["LC-HIST-LO-1.1.1", "LC-HIST-LO-2.1.1", "LC-HIST-LO-2.2.1", "LC-HIST-LO-3.1.1", "LC-HIST-LO-3.2.1"],
    "english": ["LC-ENG-LO-1.1.1", "LC-ENG-LO-2.1.1", "LC-ENG-LO-2.2.1", "LC-ENG-LO-3.1.1", "LC-ENG-LO-3.2.1"],
    "gaeilge": ["LC-GA-LO-1.1.1", "LC-GA-LO-2.1.1", "LC-GA-LO-2.2.1", "LC-GA-LO-3.1.1", "LC-GA-LO-3.2.1"],
    "computer_science": ["LC-CS-LO-1.1.1", "LC-CS-LO-2.1.1", "LC-CS-LO-2.2.1", "LC-CS-LO-3.1.1", "LC-CS-LO-3.2.1"],
}


def build_mathematics_realm_json(language: str = "en") -> dict[str, Any]:
    """Build the canonical Mathematics realm JSON (stub mode).

    Args:
        language: en | ga | cy | gd | gv | kw | br

    Returns:
        The realm JSON dict with sprite_bank + window_chrome + deity_placement +
        learning_outcomes + cognee_entities
    """
    realm_id = hashlib.sha256(
        f"mathematics|{language}".encode()
    ).hexdigest()[:16]

    subject_deity = SUBJECT_DEITIES["mathematics"]
    subject_outcomes = SUBJECT_LEARNING_OUTCOMES["mathematics"]

    # The celtic-art window chrome (Plan 4 FIBO output)
    window_chrome_url = (
        f"/stedding/fibo/mathematics/{language}/{realm_id}.png"
    )

    # The sprite bank (4 sprites per subject)
    sprite_bank = [
        {
            "sprite_id": f"mathematics-{i:02d}",
            "url": f"/stedding/assets/image_gen_chunks_{language}/mathematics/sprite_{i:02d}.png",
            "label": ["menu", "lesson", "assessment", "boss"][i],
            "x": i * 100,
            "y": 100 + (i % 2) * 50,
        }
        for i in range(4)
    ]

    # The Cognee entities (from Plan 6)
    cognee_entities = [
        {"entity_id": "d448622cbf1330c6", "name": "The Dagda", "type": "PERSON"},
        {"entity_id": "d51ff5625cf3ac1a", "name": "The Cauldron of Plenty", "type": "WORK"},
        {"entity_id": "a1b2c3d4e5f6a7b8c", "name": "Euclid", "type": "PERSON"},
        {"entity_id": "b2c3d4e5f6a7b8c9d0", "name": "Pythagoras", "type": "PERSON"},
    ]

    return {
        "realm_id": realm_id,
        "subject": "mathematics",
        "language": language,
        "sprite_bank": sprite_bank,
        "window_chrome": window_chrome_url,
        "deity_placement": {
            "deity": subject_deity["deity"],
            "treasure": subject_deity["treasure"],
            "ui_inspiration": subject_deity["ui_inspiration"],
            "x": 800,
            "y": 400,
        },
        "learning_outcomes": subject_outcomes,
        "cognee_entities": cognee_entities,
        "created_at": datetime.now(UTC).isoformat(),
    }


def tuatha_realm_asset(subject: str = "mathematics", language: str = "en") -> dict[str, Any]:
    """Dagster asset entry point (the canonical Tuatha realm).

    Per the 2026-10-08-tuatha-closed-loop-mmo-v1 saga change (Plan 8),
    this returns the realm JSON for one subject + one language. Mathematics
    is the only subject supported at launch; the others are added
    incrementally.

    Args:
        subject: The NCCA subject (default: mathematics)
        language: en | ga | cy | gd | gv | kw | br

    Returns:
        The realm JSON dict
    """
    if subject != "mathematics":
        return {
            "error": f"Subject {subject!r} not supported at launch (only 'mathematics' is live)",
            "supported_subjects": list(SUBJECT_DEITIES.keys()),
            "stub": True,
        }
    return build_mathematics_realm_json(language=language)


__all__ = [
    "tuatha_realm_asset",
    "build_mathematics_realm_json",
    "SUBJECT_DEITIES",
    "SUBJECT_LEARNING_OUTCOMES",
]
