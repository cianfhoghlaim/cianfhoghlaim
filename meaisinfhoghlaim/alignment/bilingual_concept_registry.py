"""Bilingual EN<->GA concept pair registry (Plan 2, UC 7).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2).

The canonical EN<->GA concept pair store. 1 row per concept pair.
Combines:
  - The BAML ExtractCrossLinguisticConcept output (auto-curated via BAML)
  - Operator-curated entries (manual additions)
  - Tearma.ie cross-references (via the source_url field)

Schema columns:
  - pair_id (canonical UUID)
  - en_term, ga_term (the canonical term pair)
  - definition_en, definition_ga (definitions in each language)
  - language_pair (default en-ga; also en-cy, en-gd for future expansion)
  - subject_id, stage, topic_id (canonical cohort join keys)
  - confidence (0.0-1.0; BAML extraction fidelity OR operator confidence)
  - source_url (Tearma.ie link for verification)
  - extraction_method (baml, operator_curated, hybrid)
  - created_at, updated_at

Storage:
  - In-memory: _cache dict keyed by (en_term.lower(), ga_term.lower()) tuple
  - On disk: stedding/education/bilingual_concepts/ as JSONL files
    (1 file per (subject, stage); named <subject>__<stage>.jsonl)

Generalisable: same registry works for Wales (EN/CY) + Scotland (EN/GD)
via the language_pair dimension.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from meaisinfoghlaim.alignment.schema import BilingualConcept, LanguagePair

logger = logging.getLogger(__name__)


# Canonical on-disk root for the bilingual concept JSONL files.
BILINGUAL_CONCEPTS_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_BILINGUAL_CONCEPTS_ROOT",
        "stedding/education/bilingual_concepts",
    )
)


class BilingualConceptRegistry:
    """The canonical bilingual concept pair registry."""

    def __init__(self, root=None):
        self.root = Path(root) if root is not None else BILINGUAL_CONCEPTS_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache = {}

    @staticmethod
    def file_name_for(subject_id, stage):
        return f"{subject_id}__{stage}.jsonl"

    def path_for(self, subject_id, stage):
        return self.root / self.file_name_for(subject_id, stage)

    def get(
        self,
        subject_id,
        stage,
        topic_id=None,
        language_pair=None,
    ):
        """Return concept pairs for a (subject, stage) cohort."""
        cache_key = (subject_id, stage)
        if cache_key in self._cache:
            concepts = self._cache[cache_key]
        else:
            path = self.path_for(subject_id, stage)
            concepts = []
            if path.exists():
                concepts = self._read(path)
            self._cache[cache_key] = concepts

        out = []
        for c in concepts:
            if topic_id is not None and c.topic_id != topic_id:
                continue
            if language_pair is not None and c.language_pair != language_pair:
                continue
            out.append(c)
        return out

    def upsert(self, concept, subject_id, stage):
        """Insert or update a concept pair in the registry."""
        path = self.path_for(subject_id, stage)
        existing = self.get(subject_id, stage)
        existing = [c for c in existing if c.pair_id != concept.pair_id]
        existing.append(concept)
        existing.sort(key=lambda c: (c.en_term.lower(), c.ga_term.lower()))
        cache_key = (subject_id, stage)
        self._cache[cache_key] = existing
        with path.open("w", encoding="utf-8") as f:
            for c in existing:
                f.write(c.model_dump_json() + NL)
        logger.info(
            "Upserted bilingual concept %s -> %s at %s",
            concept.en_term, concept.ga_term, path,
        )
        return path

    def upsert_many(self, concepts, subject_id, stage):
        """Upsert many concepts at once. Returns the count upserted."""
        count = 0
        for c in concepts:
            self.upsert(c, subject_id, stage)
            count += 1
        return count

    def all_subjects_stages(self):
        """Return all (subject_id, stage) pairs that have a seeded registry."""
        out = []
        for path in sorted(self.root.glob("*.jsonl")):
            stem = path.stem
            if "__" in stem:
                parts = stem.split("__", 1)
                if len(parts) == 2:
                    out.append((parts[0], parts[1]))
        return out

    def _read(self, path):
        out = []
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    d = json.loads(line)
                    out.append(BilingualConcept.model_validate(d))
        except Exception:
            logger.exception("Failed to read bilingual concept file at %s", path)
        return out


__all__ = [
    "BILINGUAL_CONCEPTS_ROOT",
    "BilingualConcept",
    "BilingualConceptRegistry",
    "LanguagePair",
]
