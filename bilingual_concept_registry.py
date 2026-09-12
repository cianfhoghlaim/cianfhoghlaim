"""Bilingual EN<->GA concept pair registry (Plan 2, UC 7).

Per the 2026-08-15-meaisinfhoghlaim-ireland-england-roadmap (Plan 2).

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

ciancheiltis writer (PR0.6 — 2026-09-06-ciancheiltis-v1):
  The ciancheiltis umbrella project emits bilingual pairs into a
  SEPARATE file pattern under the same root:
      stedding/education/bilingual_concepts/ciancheiltis_<phase>__<theme>.jsonl
  (one file per (phase, theme) — the ciancheiltis 10-theme catalog T1-T10).
  The ciancheiltis writer is OPT-IN: enable via
      BILINGUAL_CONCEPT_REGISTRY_CIANCHEILTIS=1
  in the environment, OR pass `enable_ciancheiltis_writer=True` to
  `write_ciancheiltis_pair()`. Disabled by default so the existing
  Ireland (en-ga) JSONL files are never accidentally overwritten.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from meaisinfhoghlaim.alignment.schema import BilingualConcept, LanguagePair

logger = logging.getLogger(__name__)


# Canonical on-disk root for the bilingual concept JSONL files.
BILINGUAL_CONCEPTS_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_BILINGUAL_CONCEPTS_ROOT",
        "stedding/education/bilingual_concepts",
    )
)


# Canonical source-value that identifies a row as a ciancheiltis-paired row.
# Per the 2026-09-06 spec §Requirement Cross-pipeline integration with
# cianfhoghlaim: the BilingualTopicEdge table gains a `source` dimension
# and ciancheiltis-paired rows MUST set `source = "ciancheiltis"`.
CIANCHEILTIS_SOURCE_TAG = "ciancheiltis"


# Canonical file-naming convention for the ciancheiltis writer path.
# Distinct from the existing Ireland (en-ga) writer which uses
# `<subject>__<stage>.jsonl`. The ciancheiltis writer uses
# `ciancheiltis_<phase>__<theme>.jsonl` so the two surface can never
# collide and a `--filter source=ciancheiltis` query on the bilingual
# concept table is unambiguous.
CIANCHEILTIS_FILE_PATTERN = "ciancheiltis_{phase}__{theme}.jsonl"


# Env-var gate for the ciancheiltis writer (the canonical opt-in flag).
BILINGUAL_CONCEPT_REGISTRY_CIANCHEILTIS_ENV = "BILINGUAL_CONCEPT_REGISTRY_CIANCHEILTIS"


class BilingualConceptRegistry:
    """The canonical bilingual concept pair registry.

    Reads + writes JSONL files from
    stedding/education/bilingual_concepts/. 1 file per (subject, stage)
    pair (named <subject>__<stage>.jsonl). In-memory cache avoids
    re-reading on every query.
    """

    def __init__(self, root=None) -> None:
        self.root = Path(root) if root is not None else BILINGUAL_CONCEPTS_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache = {}

    @staticmethod
    def file_name_for(subject_id, stage):
        """Canonical filename for a (subject, stage) pair."""
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
                f.write(c.model_dump_json() + "\n")
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


# ---------------------------------------------------------------------------
# ciancheiltis writer path (PR0.6 — 2026-09-06-ciancheiltis-v1)
# ---------------------------------------------------------------------------
# The ciancheiltis umbrella emits bilingual pairs into a SEPARATE file
# pattern under the same root. The writer is OPT-IN — by default the
# existing Ireland (en-ga) JSONL files are NEVER overwritten.


def _ciancheiltis_writer_enabled(
    enable_ciancheiltis_writer: bool | None,
) -> bool:
    """Resolve the opt-in gate: env var OR explicit param enables the writer."""
    if enable_ciancheiltis_writer is True:
        return True
    if os.environ.get(BILINGUAL_CONCEPT_REGISTRY_CIANCHEILTIS_ENV) == "1":
        return True
    return False


def ciancheiltis_path_for(phase: str, theme: str, root: Path | None = None) -> Path:
    """Canonical on-disk path for a (phase, theme) ciancheiltis file."""
    base = Path(root) if root is not None else BILINGUAL_CONCEPTS_ROOT
    return base / CIANCHEILTIS_FILE_PATTERN.format(phase=phase, theme=theme)


def write_ciancheiltis_pair(
    row: dict[str, Any],
    phase: str,
    theme: str,
    *,
    enable_ciancheiltis_writer: bool | None = None,
    root: Path | None = None,
) -> Path | None:
    """Write a single ciancheiltis bilingual-pair row to disk.

    The writer is OPT-IN. Enable via either:
      - the `BILINGUAL_CONCEPT_REGISTRY_CIANCHEILTIS=1` env var, OR
      - passing `enable_ciancheiltis_writer=True`.

    The function refuses to write rows whose `source` column !=
    `CIANCHEILTIS_SOURCE_TAG` ("ciancheiltis") and logs a warning.
    Returns the on-disk path on success, None when the writer is
    disabled or the row is rejected.

    Per the 2026-09-06 spec §Requirement Cross-pipeline integration with
    cianfhoghlaim: the on-disk path is
        stedding/education/bilingual_concepts/ciancheiltis_<phase>__<theme>.jsonl
    which is distinct from the existing Ireland (en-ga) writer path
    (`<subject>__<stage>.jsonl`).
    """
    if not _ciancheiltis_writer_enabled(enable_ciancheiltis_writer):
        logger.warning(
            "ciancheiltis_writer_disabled phase=%s theme=%s hint='set %s=1 or pass enable_ciancheiltis_writer=True'",
            phase,
            theme,
            BILINGUAL_CONCEPT_REGISTRY_CIANCHEILTIS_ENV,
        )
        return None

    if not isinstance(row, dict):
        logger.warning(
            "ciancheiltis_writer_rejected_non_dict phase=%s theme=%s row_type=%s",
            phase,
            theme,
            type(row).__name__,
        )
        return None

    source = row.get("source")
    if source != CIANCHEILTIS_SOURCE_TAG:
        logger.warning(
            "ciancheiltis_writer_rejected_wrong_source phase=%s theme=%s source=%s expected=%s",
            phase,
            theme,
            source,
            CIANCHEILTIS_SOURCE_TAG,
        )
        return None

    path = ciancheiltis_path_for(phase=phase, theme=theme, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    logger.info(
        "ciancheiltis_pair_written phase=%s theme=%s path=%s pair_id=%s",
        phase,
        theme,
        str(path),
        row.get("pair_id"),
    )
    return path


def load_ciancheiltis_pairs(
    phase: str,
    theme: str,
    *,
    root: Path | None = None,
) -> list[dict[str, Any]]:
    """Read the ciancheiltis bilingual-pair JSONL file for a (phase, theme).

    Returns a list of raw row dicts (NOT BilingualConcept objects — the
    ciancheiltis schema is deliberately narrower than the Ireland
    education schema, so we keep the round-trip as dicts). Returns an
    empty list when the file does not exist or fails to parse.

    Per the 2026-09-06 spec §Requirement Cross-pipeline integration with
    cianfhoghlaim: this reader backs the
    `bilingual_coverage_audit.py` gate (≥ 0.95 threshold) for the
    ciancheiltis source dimension.
    """
    path = ciancheiltis_path_for(phase=phase, theme=theme, root=root)
    out: list[dict[str, Any]] = []
    if not path.exists():
        return out
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    logger.exception(
                        "load_ciancheiltis_pairs_invalid_json",
                        path=str(path),
                    )
                    continue
                if isinstance(d, dict):
                    out.append(d)
    except Exception:
        logger.exception(
            "load_ciancheiltis_pairs_failed",
            path=str(path),
        )
    return out


__all__ = [
    "BILINGUAL_CONCEPTS_ROOT",
    "BilingualConcept",
    "BilingualConceptRegistry",
    "CIANCHEILTIS_FILE_PATTERN",
    "CIANCHEILTIS_SOURCE_TAG",
    "BILINGUAL_CONCEPT_REGISTRY_CIANCHEILTIS_ENV",
    "LanguagePair",
    "ciancheiltis_path_for",
    "write_ciancheiltis_pair",
    "load_ciancheiltis_pairs",
]
