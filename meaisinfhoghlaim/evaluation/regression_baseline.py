"""UC 5: RegressionBaseline + RegressionDiff (Plan 3).

Per the 2026-08-15-meaisinfhoghlaim-ireland-england-roadmap (Plan 3, UC 5).

The canonical per-subject regression baseline + diff. Stores golden baseline
content for (subject, stage, board, year) tuples + detects content drift
via SHA256 hash comparison.

Generalisable: same diff works for any (jurisdiction, stage, subject, board)
combination. The store + diff pattern follows the canonical
``golden_baselines.py`` (Plan 1 module 3) shape.

Storage:
  - In-memory: ``_baselines`` dict keyed by ``baseline_id``
  - On disk: ``stedding/education/regression_baselines/`` as JSON files
    (1 per cohort_key; named ``<cohort_key_underscored>.json``)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from meaisinfhoghlaim.alignment.schema import (
    Board,
    QualificationLevel,
    RegressionBaseline,
    RegressionDiff,
)

logger = logging.getLogger(__name__)


# Canonical on-disk root for the regression baseline JSON files.
REGRESSION_BASELINES_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_REGRESSION_BASELINES_ROOT",
        "stedding/education/regression_baselines",
    )
)


class RegressionBaselineStore:
    """The canonical regression baseline store."""

    def __init__(self, root=None) -> None:
        self.root = Path(root) if root is not None else REGRESSION_BASELINES_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self._cache: dict = {}

    @staticmethod
    def _cohort_to_filename(cohort_key: str) -> str:
        """Map cohort_key to canonical filename."""
        return cohort_key.replace("/", "__") + ".json"

    def path_for(self, cohort_key: str) -> Path:
        return self.root / self._cohort_to_filename(cohort_key)

    def _hash_canonical(self, canonical_json: str) -> str:
        """Stable SHA256 hash of the canonical JSON content."""
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def get_latest(self, cohort_key: str) -> RegressionBaseline | None:
        """Return the latest baseline for a cohort_key (or None)."""
        return self._cache.get(cohort_key)

    def get_history(self, cohort_key: str) -> list[RegressionBaseline]:
        """Return the full version history for a cohort_key."""
        path = self.path_for(cohort_key)
        if not path.exists():
            return []
        versions: list = []
        try:
            with path.open("r", encoding="utf-8") as f:
                items = json.load(f)
            for d in items:
                try:
                    versions.append(RegressionBaseline.model_validate(d))
                except Exception:
                    logger.exception("Failed to parse regression baseline at %s", path)
        except Exception:
            logger.exception("Failed to read regression baseline at %s", path)
        return versions

    def save(self, baseline: RegressionBaseline) -> Path:
        """Persist a new baseline (appends to the cohort's history)."""
        import uuid
        if not baseline.baseline_id:
            baseline = baseline.model_copy(update={"baseline_id": str(uuid.uuid4())})
        if not baseline.content_hash:
            baseline = baseline.model_copy(
                update={"content_hash": self._hash_canonical(baseline.canonical_json)}
            )
        # Mark any prior baselines as superseded
        history = self.get_history(baseline.cohort_key)
        superseded: list = []
        for old in history:
            if not old.superseded_by:
                superseded.append(
                    old.model_copy(update={"superseded_by": baseline.baseline_id})
                )
        history = superseded + [baseline]
        path = self.path_for(baseline.cohort_key)
        with path.open("w", encoding="utf-8") as f:
            json.dump(
                [b.model_dump(mode="json") for b in history],
                f,
                indent=2,
                ensure_ascii=False,
            )
        self._cache[baseline.cohort_key] = baseline
        logger.info(
            "Saved regression baseline %s for cohort=%s (hash=%s)",
            baseline.baseline_id, baseline.cohort_key, baseline.content_hash[:12],
        )
        return path


class RegressionDiffer:
    """The canonical regression differ."""

    def __init__(self, store: RegressionBaselineStore | None = None) -> None:
        self.store = store or RegressionBaselineStore()

    def diff(
        self,
        cohort_key: str,
        baseline_old_id: str,
        baseline_new_id: str,
    ) -> RegressionDiff | None:
        """Diff 2 baselines by ID; returns the RegressionDiff."""
        import uuid as _uuid
        from datetime import datetime as _dt
        from datetime import timezone as _tz

        history = {b.baseline_id: b for b in self.store.get_history(cohort_key)}
        old = history.get(baseline_old_id)
        new = history.get(baseline_new_id)
        if old is None or new is None:
            logger.warning(
                "Could not diff: cohort=%s old=%s new=%s (missing baseline)",
                cohort_key, baseline_old_id, baseline_new_id,
            )
            return None

        # Compute the canonical diffs (added / removed / modified topics)
        import json as _json
        try:
            old_topics = set(_json.loads(old.canonical_json).get("topics", []))
        except Exception:
            old_topics = set()
        try:
            new_topics = set(_json.loads(new.canonical_json).get("topics", []))
        except Exception:
            new_topics = set()

        added = sorted(new_topics - old_topics)
        removed = sorted(old_topics - new_topics)
        modified: dict = {}
        for topic in (old_topics & new_topics):
            # In a real impl, we'd deep-diff the topic payload
            # For Plan 3 v1, just mark topics that exist in both as "tracked"
            modified[topic] = {"status": "tracked"}

        return RegressionDiff(
            diff_id=str(_uuid.uuid4()),
            cohort_key=cohort_key,
            baseline_old_id=baseline_old_id,
            baseline_new_id=baseline_new_id,
            content_hash_changed=(old.content_hash != new.content_hash),
            added_topics=added,
            removed_topics=removed,
            modified_concepts_json=_json.dumps(modified),
            duration_ms=0,
        )


__all__ = [
    "REGRESSION_BASELINES_ROOT",
    "RegressionBaselineStore",
    "RegressionDiffer",
    "RegressionBaseline",
    "RegressionDiff",
    "QualificationLevel",
    "Board",
]
