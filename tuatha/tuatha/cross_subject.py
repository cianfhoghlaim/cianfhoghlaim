"""tuatha.cross_subject — the cross-subject specialist.

The canonical agent for cross-subject queries (e.g., "How does
the Mathematics syllabus for complex numbers relate to the
Physics syllabus for complex numbers?"). Routes through
multiple subject agents in parallel.
"""
from __future__ import annotations

from typing import Any

from .orchestrator import TuathaOrchestrator


class CrossSubjectSpecialist:
    """The cross-subject specialist.

    Routes cross-subject queries (those that span > 1 NCCA
    subject) to multiple subject agents in parallel and merges
    the responses into a single answer.
    """

    def __init__(self, orchestrator: TuathaOrchestrator | None = None) -> None:
        self._orchestrator = orchestrator or TuathaOrchestrator()

    @property
    def orchestrator(self) -> TuathaOrchestrator:
        return self._orchestrator

    async def cross_subject_query(
        self, subjects: list[str], prompt: str
    ) -> dict[str, Any]:
        """Dispatch a cross-subject query to multiple subject agents.

        Example:
        ```python
        specialist = CrossSubjectSpecialist()
        response = await specialist.cross_subject_query(
            ["mathematics", "physics", "chemistry"],
            "How is the concept of complex numbers used across these subjects?"
        )
        ```
        """
        queries = [
            ("subject", subject, prompt) for subject in subjects
        ]
        responses = await self._orchestrator.dispatch_parallel(queries)
        return {
            "subjects": subjects,
            "prompt": prompt,
            "responses": responses,
        }


# The canonical cross-subject specialist instance.
cross_subject_agent = CrossSubjectSpecialist()


__all__ = ["CrossSubjectSpecialist", "cross_subject_agent"]
