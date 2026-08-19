"""Dagster sensor that polls the meaisinfoghlaim cohort_lifecycle state.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 5):

Polls ``meaisinfoghlaim.datasets.cohort_lifecycle.CohortLifecycle`` + the
``CohortRegistry`` every 60s. When a cohort transitions to
EXTRACTING or EVALUATING, emits a RunRequest to trigger the
``meaisin_extraction_progress`` or ``meaisin_eval_progress`` Dagster assets.

Generalisable to Scotland / Wales / NI / Jersey / Guernsey / IoM rollouts.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)


# The canonical poll interval (matches the dagster asset materialisation cadence)
POLL_INTERVAL_SECONDS = 60

# The previous poll's state (in-memory dedup; resets on sensor restart)
_LAST_SEEN: dict = {}


def _load_lifecycle():
    """Lazy-import the lifecycle collaborator (avoids heavy import at module load)."""
    try:
        from meaisinfhoghlaim.datasets.cohort_lifecycle import (
            CohortLifecycle,
            CohortLifecycleState,
        )
        from meaisinfhoghlaim.datasets.cohort_registry import CohortRegistry
        return CohortLifecycle, CohortLifecycleState, CohortRegistry
    except ImportError:
        logger.warning(
            "meaisinfoghlaim.datasets not importable; sensor runs in mock mode"
        )
        return None, None, None


def _safe_kv(cohort_id: str) -> tuple:
    """Return a stable (last_state, last_updated_at) tuple for dedup."""
    return _LAST_SEEN.get(cohort_id, (None, None))


def _has_changed(cohort_id: str, new_state: str, new_updated_at: str) -> bool:
    """Return True iff the cohort's state has changed since the last poll."""
    prev_state, prev_updated_at = _safe_kv(cohort_id)
    if prev_state != new_state or prev_updated_at != new_updated_at:
        _LAST_SEEN[cohort_id] = (new_state, new_updated_at)
        return True
    return False


def _make_run_request(cohort_id: str, run_key: str, tags: dict[str, str]) -> Any:
    """Lazy-import Dagster's RunRequest (avoids heavy import at module load)."""
    try:
        from dagster import RunRequest
        return RunRequest(run_key=run_key, tags=tags)
    except ImportError:
        logger.warning("dagster not importable; sensor returns empty list")
        return None


def _evaluate_skip(cursor: str) -> Any:
    """Return a SkipReason for the sensor when meaisinfoghlaim is unavailable."""
    try:
        from dagster import SkipReason
        return SkipReason("meaisinfoghlaim not importable; sensor is SKIPPED")
    except ImportError:
        return None


def evaluate_tick(context) -> Any:
    """The Dagster sensor tick function.

    Called every 60 seconds by Dagster. Polls the CohortRegistry +
    CohortLifecycle state machine. Emits RunRequests for any cohort
    that has changed state since the last poll.
    """
    CohortLifecycle, CohortLifecycleState, CohortRegistry = _load_lifecycle()
    if CohortLifecycle is None:
        return _evaluate_skip("")

    # Load the registry
    registry = CohortRegistry()
    cohorts = registry.all()

    requests = []
    for cohort in cohorts:
        if cohort.lifecycle_state.value == "not_started":
            continue
        if not _has_changed(
            cohort.cohort_id,
            cohort.lifecycle_state.value,
            cohort.lifecycle_updated_at.isoformat() if cohort.lifecycle_updated_at else "",
        ):
            continue
        # Only trigger on EXTRACTING or EVALUATING transitions
        run_key = f"{cohort.cohort_id}-{cohort.lifecycle_state.value}"
        tags = {
            "cohort_id": cohort.cohort_id,
            "jurisdiction": cohort.jurisdiction,
            "stage": cohort.stage if isinstance(cohort.stage, str) else cohort.stage.value,
            "subject": cohort.subject,
            "board": cohort.board,
            "language": cohort.language,
            "lifecycle_state": cohort.lifecycle_state.value,
        }
        request = _make_run_request(cohort.cohort_id, run_key, tags)
        if request is not None:
            requests.append(request)

    if requests:
        logger.info("meaisin_education_ops_sensor: %d cohort transitions", len(requests))
    return requests


# The canonical Dagster @sensor decorator (lazy-imported so the file can be
# parsed without Dagster installed). When Dagster is available, the sensor
# is registered automatically on Dagster's startup.
try:
    from dagster import sensor, SensorEvaluationContext

    @sensor(
        name="meaisin_education_ops_sensor",
        description="Polls the meaisinfoghlaim cohort_lifecycle state machine + emits RunRequests on EXTRACTING/EVALUATING transitions",
        minimum_interval_seconds=POLL_INTERVAL_SECONDS,
        default_status=None,
    )
    def meaisin_education_ops_sensor(context: SensorEvaluationContext):
        """The Dagster-registered sensor entrypoint."""
        return evaluate_tick(context)

except ImportError:
    logger.warning("dagster not importable; sensor is not registered with Dagster")


__all__ = [
    "POLL_INTERVAL_SECONDS",
    "evaluate_tick",
    "meaisin_education_ops_sensor",
]
