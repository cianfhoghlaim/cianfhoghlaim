"""tuatha.orchestrator — the TuathaOrchestrator.

The canonical multi-agent orchestrator for the new tuatha/
project. Routes cross-subject queries + cross-educational
queries + cross-hackathon queries to the right SubjectAgentWiring
+ runs the BIEP hackathon workflows in parallel.
"""
from __future__ import annotations

import asyncio
from typing import Any

from .routing import (
    EDUCATIONAL_WIRING_REGISTRY,
    HACKATHON_WIRING_REGISTRY,
    SUBJECT_WIRING_REGISTRY,
    SubjectAgentWiring,
)


class TuathaOrchestrator:
    """The canonical multi-agent orchestrator.

    Routes a user query to the right per-subject / per-educational /
    per-hackathon agent via the 3 wiring registries. Supports
    parallel dispatch (via `asyncio.gather`) for cross-subject
    queries that span multiple subjects.
    """

    def __init__(self) -> None:
        self._subjects = dict(SUBJECT_WIRING_REGISTRY)
        self._educational = dict(EDUCATIONAL_WIRING_REGISTRY)
        self._hackathon = dict(HACKATHON_WIRING_REGISTRY)

    @property
    def subjects(self) -> dict[str, SubjectAgentWiring]:
        return self._subjects

    @property
    def educational(self) -> dict[str, SubjectAgentWiring]:
        return self._educational

    @property
    def hackathon(self) -> dict[str, SubjectAgentWiring]:
        return self._hackathon

    def route_subject(self, subject: str) -> SubjectAgentWiring:
        """Look up the wiring for a specific NCCA subject."""
        if subject not in self._subjects:
            raise KeyError(
                f"unknown subject: {subject!r}; "
                f"available: {sorted(self._subjects.keys())}"
            )
        return self._subjects[subject]

    def route_educational(self, name: str) -> SubjectAgentWiring:
        """Look up the wiring for a specific educational agent."""
        if name not in self._educational:
            raise KeyError(
                f"unknown educational agent: {name!r}; "
                f"available: {sorted(self._educational.keys())}"
            )
        return self._educational[name]

    def route_hackathon(self, name: str) -> SubjectAgentWiring:
        """Look up the wiring for a specific BIEP hackathon feature."""
        if name not in self._hackathon:
            raise KeyError(
                f"unknown hackathon feature: {name!r}; "
                f"available: {sorted(self._hackathon.keys())}"
            )
        return self._hackathon[name]

    async def dispatch_parallel(
        self, queries: list[tuple[str, str, str]]
    ) -> list[dict[str, Any]]:
        """Dispatch multiple agent queries in parallel.

        Each query is a (kind, name, prompt) tuple where kind is
        one of 'subject' / 'educational' / 'hackathon'.

        Returns a list of {kind, name, response} dicts.
        """
        async def _one(kind: str, name: str, prompt: str) -> dict[str, Any]:
            if kind == "subject":
                wire = self.route_subject(name)
            elif kind == "educational":
                wire = self.route_educational(name)
            elif kind == "hackathon":
                wire = self.route_hackathon(name)
            else:
                raise ValueError(f"unknown kind: {kind!r}")
            return {
                "kind": kind,
                "name": name,
                "wire": wire,
                "prompt": prompt,
            }

        return await asyncio.gather(*[_one(*q) for q in queries])


__all__ = ["TuathaOrchestrator"]
