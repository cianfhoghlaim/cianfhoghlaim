"""Shim for `sruth.shared.agent_os.a2a` — see tuatha/crypteolas/STATUS.md.

The A2A (agent-to-agent) client stub. A real implementation would
negotiate with a remote agent registry over HTTP. This stub is enough
to satisfy imports and to let `agent_os` start without crashing.
"""

from __future__ import annotations

from typing import Any


async def call_agent(
    agent_id: str,
    message: str,
    *,
    timeout: float = 30.0,
    **kwargs: Any,
) -> dict[str, Any]:
    """Stub: call another agent and return a placeholder response."""
    return {
        "agent_id": agent_id,
        "message": message,
        "response": "(stub) A2A call_agent is not yet implemented",
        "timeout": timeout,
    }


__all__ = ["call_agent"]
