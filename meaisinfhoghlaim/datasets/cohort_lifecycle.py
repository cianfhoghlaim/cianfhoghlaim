"""Per-cohort lifecycle tracker (Plan 4).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 4).

The canonical per-cohort lifecycle state machine:
  not_started -> extracting -> evaluating -> registered -> promoted

State transitions are written to:
  - The CohortRegistry (the canonical per-cohort state)
  - MLflow (per-cohort lifecycle metric logging for the Plan 5 ops
    dashboard)

Generalisable: same state machine for any (jurisdiction, stage, subject,
board) combination. Scotland / Wales / NI rollouts follow the same flow.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from meaisinfoghlaim.alignment.schema import (
    CohortLifecycleState,
    CohortRow,
)
from meaisinfoghlaim.datasets.cohort_registry import CohortRegistry

logger = logging.getLogger(__name__)


# The canonical state transition graph
ALLOWED_TRANSITIONS: dict = {
    CohortLifecycleState.NOT_STARTED: {CohortLifecycleState.EXTRACTING},
    CohortLifecycleState.EXTRACTING: {
        CohortLifecycleState.EVALUATING,
        CohortLifecycleState.NOT_STARTED,  # rollback
    },
    CohortLifecycleState.EVALUATING: {
        CohortLifecycleState.REGISTERED,
        CohortLifecycleState.EXTRACTING,  # re-extract if eval fails
    },
    CohortLifecycleState.REGISTERED: {
        CohortLifecycleState.PROMOTED,
        CohortLifecycleState.EVALUATING,  # rollback
    },
    CohortLifecycleState.PROMOTED: set(),  # terminal state
}


class CohortLifecycle:
    """The canonical per-cohort lifecycle tracker."""

    def __init__(
        self,
        registry: CohortRegistry | None = None,
        mlflow_client: Any | None = None,
    ) -> None:
        self.registry = registry or CohortRegistry()
        self._mlflow_client = mlflow_client
        self._mlflow_available: bool | None = None

    def transition(
        self,
        cohort_id: str,
        new_state: CohortLifecycleState,
    ) -> CohortRow:
        """Transition the cohort to a new state (validated by ALLOWED_TRANSITIONS).

        Args:
            cohort_id: the canonical cohort_id
            new_state: the target CohortLifecycleState

        Returns:
            The updated CohortRow

        Raises:
            ValueError: if the transition is not allowed
            KeyError: if the cohort is not found
        """
        cohort = self.registry.get(cohort_id)
        if cohort is None:
            raise KeyError(f"Cohort {cohort_id!r} not found in registry")

        old_state = cohort.lifecycle_state
        allowed = ALLOWED_TRANSITIONS.get(old_state, set())
        if new_state not in allowed:
            raise ValueError(
                f"Invalid transition: {old_state.value} -> {new_state.value} "
                f"(allowed: {[s.value for s in allowed]})"
            )

        # Apply the transition
        new_cohort = cohort.model_copy(
            update={
                "lifecycle_state": new_state,
                "lifecycle_updated_at": datetime.now(timezone.utc),
            }
        )
        self.registry.upsert(new_cohort)
        logger.info(
            "Cohort %s transitioned %s -> %s",
            cohort_id, old_state.value, new_state.value,
        )

        # Log to MLflow (lazy-loaded)
        self._log_to_mlflow(new_cohort, old_state)

        return new_cohort

    def can_transition(
        self,
        cohort_id: str,
        new_state: CohortLifecycleState,
    ) -> bool:
        """Check if a transition is allowed (without applying it)."""
        cohort = self.registry.get(cohort_id)
        if cohort is None:
            return False
        return new_state in ALLOWED_TRANSITIONS.get(cohort.lifecycle_state, set())

    def _log_to_mlflow(
        self,
        cohort: CohortRow,
        old_state: CohortLifecycleState,
    ) -> None:
        """Log the lifecycle transition to MLflow (lazy-loaded)."""
        if self._mlflow_available is False:
            return
        if self._mlflow_client is None:
            try:
                import mlflow  # type: ignore[import-not-found]
                self._mlflow_client = mlflow
                self._mlflow_available = True
            except ImportError:
                self._mlflow_available = False
                return

        try:
            with mlflow.start_run(run_name=f"lifecycle/{cohort.cohort_id}"):
                mlflow.set_tag("cohort_id", cohort.cohort_id)
                mlflow.set_tag("from_state", old_state.value)
                mlflow.set_tag("to_state", cohort.lifecycle_state.value)
                mlflow.log_metric("lifecycle_transition_count", 1)
        except Exception:
            logger.exception("MLflow log failed for cohort %s lifecycle", cohort.cohort_id)


__all__ = [
    "CohortLifecycle",
    "ALLOWED_TRANSITIONS",
    "CohortLifecycleState",
    "CohortRow",
    "CohortRegistry",
]
