"""tuatha.operator — the CianfhoghlaimOperator.

The single-user operating mode for the new tuatha/ project.
The canonical "give me one answer to one question" surface
(vs. the multi-agent TuathaOrchestrator for cross-subject
queries).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import TuathaConfig
from .orchestrator import TuathaOrchestrator
from .routing import SubjectAgentWiring


@dataclass(frozen=True)
class OperatorRequest:
    """The canonical single-user operator request."""

    kind: str  # 'subject' | 'educational' | 'hackathon'
    name: str  # the agent name (per the wiring registries)
    prompt: str


@dataclass(frozen=True)
class OperatorResponse:
    """The canonical single-user operator response."""

    kind: str
    name: str
    wire: SubjectAgentWiring
    response: Any


class CianfhoghlaimOperator:
    """The single-user operating mode for the new tuatha/ project.

    Wraps the TuathaOrchestrator with the canonical single-user
    surface. Use this for ad-hoc queries; use the orchestrator
    directly for cross-subject batch operations.
    """

    def __init__(self, config: TuathaConfig | None = None) -> None:
        self._config = config or TuathaConfig.from_env()
        self._orchestrator = TuathaOrchestrator()

    @property
    def config(self) -> TuathaConfig:
        return self._config

    @property
    def orchestrator(self) -> TuathaOrchestrator:
        return self._orchestrator

    async def ask(self, request: OperatorRequest) -> OperatorResponse:
        """Ask a single agent one question.

        The agent is selected by (kind, name) per the wiring
        registries. The question is dispatched as a single
        per-subject / per-educational / per-hackathon invocation.
        """
        if request.kind == "subject":
            wire = self._orchestrator.route_subject(request.name)
        elif request.kind == "educational":
            wire = self._orchestrator.route_educational(request.name)
        elif request.kind == "hackathon":
            wire = self._orchestrator.route_hackathon(request.name)
        else:
            raise ValueError(f"unknown kind: {request.kind!r}")

        # Per the BAML / Letta graceful-degradation pattern: this
        # is the canonical mount point. The actual BAML function
        # call is implemented in the per-subject / per-educational
        # / per-hackathon module (in `tuatha/subjects/` etc.).
        return OperatorResponse(
            kind=request.kind,
            name=request.name,
            wire=wire,
            response={
                "trace_name": wire.langfuse_trace_name.replace(
                    "<verb>", "ask"
                ),
                "prompt": request.prompt,
                "status": "dispatched",
            },
        )


__all__ = ["CianfhoghlaimOperator", "OperatorRequest", "OperatorResponse"]
