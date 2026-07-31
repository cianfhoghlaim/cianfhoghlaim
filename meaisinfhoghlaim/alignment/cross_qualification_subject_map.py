"""Canonical cross-qualification subject map (Plan 3 UC cross-qual).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 3).

The canonical map of (qualification, jurisdiction, subject, board) tuples
to equivalent (qualification, jurisdiction, subject, board) tuples.

LOCKED DECISION (locked 2026-08-15): ships pre-loaded with **30 canonical
pairs** covering the most common cross-qualification comparisons an
Ireland+England operator would query:

  - Chemistry LC <-> A-Level Chemistry (0.95)
  - Chemistry LC <-> GCSE Chemistry (0.80)
  - Coding JC <-> GCSE Computer Science (0.70)
  - Coding JC <-> A-Level Computer Science (0.65)
  - Mathematics LC <-> A-Level Mathematics (0.90)
  - Mathematics LC <-> GCSE Mathematics (0.85)
  - Further Maths LC <-> A-Level Further Maths (1.0 — exact)
  - English LC <-> A-Level English Literature (0.80)
  - English LC <-> GCSE English Language (0.75)
  - Physics LC <-> A-Level Physics (0.92)
  - Biology LC <-> A-Level Biology (0.90)
  - Geography LC <-> A-Level Geography (0.88)
  - History LC <-> A-Level History (0.85)
  - Business LC <-> A-Level Business Studies (0.80)
  - Music LC <-> A-Level Music (0.70)
  - Home Economics LC <-> GCSE Food & Nutrition (0.55)
  - Chemistry A-Level <-> Chemistry GCSE (0.65 — reverse mapping)
  - Physics A-Level <-> Physics GCSE (0.65 — reverse mapping)
  - Biology A-Level <-> Biology GCSE (0.65 — reverse mapping)
  - English Lit A-Level <-> English Lang GCSE (0.55)
  - History A-Level <-> History GCSE (0.60)
  - Geography A-Level <-> Geography GCSE (0.60)
  - Mathematics A-Level <-> GCSE Mathematics (0.75 — reverse mapping)
  - JC Science <-> GCSE Combined Science (0.70)
  - JC English <-> GCSE English Language (0.75)
  - JC Mathematics <-> GCSE Mathematics (0.75)
  - JC Irish <-> GCSE Irish (0.80)
  - JC Geography <-> GCSE Geography (0.65)
  - JC History <-> GCSE History (0.65)
  - JC Business <-> GCSE Business (0.65)

Generalisable: the same primitive + storage pattern works for Scotland
(Nat 5 / Higher / Adv Higher) + Wales (EN/CY) + NI (CCEA) rollouts.

Storage:
  - In-memory: ``_equivalences`` dict keyed by the canonical ``map_id``
  - On disk: ``stedding/education/cross_qualification_subject_map/`` as
    a single JSON file (``equivalences.json``) for the 30 pre-loaded
    entries
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from meaisinfoghlaim.alignment.schema import (
    Board,
    QualificationEquivalence,
    QualificationLevel,
)

logger = logging.getLogger(__name__)


# Canonical on-disk root for the cross-qualification subject map.
CROSS_QUAL_SUBJECT_MAP_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_CROSS_QUAL_SUBJECT_MAP_ROOT",
        "stedding/education/cross_qualification_subject_map",
    )
)


# The 30 pre-loaded equivalences (locked 2026-08-15)
# Format: (qual_a, jur_a, subj_a, board_a, qual_b, jur_b, subj_b, board_b, strength, notes)
_PRE_LOADED: list = [
    # STEM core (Chemistry, Physics, Biology, Maths)
    ("lc", "ireland", "chemistry", "none", "a_level", "england", "chemistry", "none", 0.95, "near-identical curricula"),
    ("lc", "ireland", "chemistry", "none", "gcse", "england", "chemistry", "none", 0.80, "LC is broader"),
    ("a_level", "england", "chemistry", "none", "gcse", "england", "chemistry", "none", 0.65, "reverse mapping"),
    ("lc", "ireland", "physics", "none", "a_level", "england", "physics", "none", 0.92, "near-identical"),
    ("a_level", "england", "physics", "none", "gcse", "england", "physics", "none", 0.65, "reverse mapping"),
    ("lc", "ireland", "biology", "none", "a_level", "england", "biology", "none", 0.90, "near-identical"),
    ("a_level", "england", "biology", "none", "gcse", "england", "biology", "none", 0.65, "reverse mapping"),
    # Mathematics family
    ("lc", "ireland", "mathematics", "none", "a_level", "england", "mathematics", "none", 0.90, "near-identical"),
    ("lc", "ireland", "mathematics", "none", "gcse", "england", "mathematics", "none", 0.85, "high overlap"),
    ("lc", "ireland", "mathematics_further", "none", "a_level", "england", "further_mathematics", "none", 1.00, "exact"),
    ("a_level", "england", "mathematics", "none", "gcse", "england", "mathematics", "none", 0.75, "reverse mapping"),
    # Humanities
    ("lc", "ireland", "english", "none", "a_level", "england", "english_literature", "none", 0.80, "different focus"),
    ("lc", "ireland", "english", "none", "gcse", "england", "english_language", "none", 0.75, "high overlap"),
    ("a_level", "england", "english_literature", "none", "gcse", "england", "english_language", "none", 0.55, "low overlap"),
    ("lc", "ireland", "geography", "none", "a_level", "england", "geography", "none", 0.88, "near-identical"),
    ("a_level", "england", "geography", "none", "gcse", "england", "geography", "none", 0.60, "moderate overlap"),
    ("lc", "ireland", "history", "none", "a_level", "england", "history", "none", 0.85, "high overlap"),
    ("a_level", "england", "history", "none", "gcse", "england", "history", "none", 0.60, "moderate overlap"),
    # Business + practical
    ("lc", "ireland", "business", "none", "a_level", "england", "business_studies", "none", 0.80, "high overlap"),
    ("lc", "ireland", "music", "none", "a_level", "england", "music", "none", 0.70, "practical vs theory"),
    ("lc", "ireland", "home_economics", "none", "gcse", "england", "food_nutrition", "none", 0.55, "partial overlap"),
    # JC (Ireland) <-> GCSE (England) cross-qual
    ("jc", "ireland", "science", "none", "gcse", "england", "combined_science", "none", 0.70, "moderate overlap"),
    ("jc", "ireland", "english", "none", "gcse", "england", "english_language", "none", 0.75, "high overlap"),
    ("jc", "ireland", "mathematics", "none", "gcse", "england", "mathematics", "none", 0.75, "high overlap"),
    ("jc", "ireland", "gaeilge", "none", "gcse", "england", "irish", "none", 0.80, "near-identical"),
    ("jc", "ireland", "geography", "none", "gcse", "england", "geography", "none", 0.65, "moderate overlap"),
    ("jc", "ireland", "history", "none", "gcse", "england", "history", "none", 0.65, "moderate overlap"),
    ("jc", "ireland", "business", "none", "gcse", "england", "business", "none", 0.65, "moderate overlap"),
    # Coding (user-requested specific example)
    ("jc", "ireland", "coding", "none", "gcse", "england", "computer_science", "none", 0.70, "naming differs, content overlaps"),
    ("jc", "ireland", "coding", "none", "a_level", "england", "computer_science", "none", 0.65, "JC is more practical"),
]


class CrossQualificationSubjectMap:
    """The canonical cross-qualification subject map.

    Pre-loaded with 30 equivalences; read-only by default. Use upsert()
    to add new entries (for the Scotland / Wales / NI rollouts).
    """

    def __init__(self, root=None) -> None:
        self.root = (
            Path(root) if root is not None
            else CROSS_QUAL_SUBJECT_MAP_ROOT
        )
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache: dict = {}
        self._load_preloaded()

    def _load_preloaded(self) -> None:
        """Load the 30 pre-loaded equivalences (idempotent)."""
        if self._cache:
            return
        for (qa, ja, sa, ba, qb, jb, sb, bb, strength, notes) in _PRE_LOADED:
            try:
                map_id = f"equiv-{qa}-{sa}-{ja}-{ba}-{qb}-{sb}-{jb}-{bb}"
                equiv = QualificationEquivalence(
                    map_id=map_id,
                    qualification_a=QualificationLevel(qa),
                    jurisdiction_a=ja,
                    subject_a=sa,
                    board_a=Board(ba),
                    qualification_b=QualificationLevel(qb),
                    jurisdiction_b=jb,
                    subject_b=sb,
                    board_b=Board(bb),
                    equivalence_strength=strength,
                    notes=notes,
                )
                self._cache[map_id] = equiv
            except Exception as exc:
                logger.warning(
                    "Failed to load pre-loaded equivalence %s -> %s: %s",
                    (qa, ja, sa), (qb, jb, sb), exc,
                )
        # Try to load additional entries from the on-disk JSON (operator-curated)
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        path = self.root / "equivalences.json"
        if not path.exists():
            return
        try:
            with path.open("r", encoding="utf-8") as f:
                items = json.load(f)
            for d in items:
                try:
                    equiv = QualificationEquivalence.model_validate(d)
                    self._cache[equiv.map_id] = equiv
                except Exception as exc:
                    logger.warning(
                        "Failed to load equivalence %s: %s", d.get("map_id"), exc
                    )
        except Exception:
            logger.exception("Failed to read cross-qual subject map from %s", path)

    def all(self) -> list:
        """Return all equivalences."""
        return list(self._cache.values())

    def get(self, map_id: str):
        """Return a specific equivalence by map_id."""
        return self._cache.get(map_id)

    def upsert(self, equiv: QualificationEquivalence) -> None:
        """Insert or update an equivalence (operator-curated)."""
        self._cache[equiv.map_id] = equiv
        self._save_to_disk()

    def _save_to_disk(self) -> None:
        path = self.root / "equivalences.json"
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(
                    [e.model_dump(mode="json") for e in self._cache.values()],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except Exception:
            logger.exception("Failed to save cross-qual subject map to %s", path)


__all__ = [
    "CROSS_QUAL_SUBJECT_MAP_ROOT",
    "CrossQualificationSubjectMap",
    "QualificationEquivalence",
    "QualificationLevel",
    "Board",
]
