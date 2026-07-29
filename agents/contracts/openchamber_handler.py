"""openchamber handler — receive a ContextEnvelope from openclaw or hermes.

The handler unpacks the envelope and returns a `dict` with the unpacked
context_payload, ready for the openchamber IDE/CLI session to consume.

Per the 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1 openspec
change (spec delta on `agent-platform-cluster`, Requirement
"Cross-agent context envelope protocol"):

  "openchamber_handler.py ... MUST implement a function
   `receive_envelope(envelope: ContextEnvelope) -> dict[str, Any]`
   that unpacks the envelope into the surface's local context."

Usage:

    from agents.contracts.context_envelope import ContextEnvelope
    from agents.contracts.openchamber_handler import receive_envelope

    envelope = ContextEnvelope(...)
    result = receive_envelope(envelope)
    if result["status"] == "received":
        # feed result["context"] into the IDE/CLI session state
        ...
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from .context_envelope import AgentSurface, ContextEnvelope

logger = logging.getLogger(__name__)

EXPECTED_RECIPIENT: AgentSurface = "openchamber"


def receive_envelope(envelope: ContextEnvelope) -> dict[str, Any]:
    """Receive a cross-agent envelope on the openchamber surface.

    Returns a dict with the unpacked context_payload, ready for the
    openchamber IDE/CLI session to consume. The dict has these keys:

    - `status`: "received" | "rejected" | "expired"
    - `recipient`: "openchamber" (always)
    - `agent_run_id`: the envelope's run id (for correlation)
    - `parent_trace_id`: the envelope's trace id (for Langfuse correlation)
    - `context`: the unpacked context_payload (only if status == "received")
    - `reason`: human-readable reason (only if status != "received")
    """
    # 1. Wrong-recipient check
    if envelope.recipient != EXPECTED_RECIPIENT:
        logger.warning(
            "openchamber: envelope addressed to %r, not openchamber; rejecting",
            envelope.recipient,
        )
        return {
            "status": "rejected",
            "recipient": EXPECTED_RECIPIENT,
            "agent_run_id": envelope.agent_run_id,
            "parent_trace_id": envelope.parent_trace_id,
            "reason": f"wrong_recipient: envelope.addressed_to={envelope.recipient}",
        }

    # 2. Expiry check
    if envelope.is_expired(datetime.now(timezone.utc)):
        logger.warning(
            "openchamber: envelope %s expired at %s; rejecting",
            envelope.agent_run_id,
            envelope.expires_at.isoformat(),
        )
        return {
            "status": "expired",
            "recipient": EXPECTED_RECIPIENT,
            "agent_run_id": envelope.agent_run_id,
            "parent_trace_id": envelope.parent_trace_id,
            "reason": f"expired_at={envelope.expires_at.isoformat()}",
        }

    # 3. Unpack the context_payload
    #    The openchamber IDE/CLI expects these keys (session-state hydration).
    context = dict(envelope.context_payload)
    context.setdefault("source_surface", envelope.sender)
    context.setdefault("trace_id", envelope.parent_trace_id)
    context.setdefault("run_id", envelope.agent_run_id)
    context.setdefault("workspace", "/")  # default workspace root

    logger.info(
        "openchamber: received envelope run_id=%s from sender=%s",
        envelope.agent_run_id,
        envelope.sender,
    )

    return {
        "status": "received",
        "recipient": EXPECTED_RECIPIENT,
        "agent_run_id": envelope.agent_run_id,
        "parent_trace_id": envelope.parent_trace_id,
        "context": context,
    }


__all__ = ["receive_envelope", "EXPECTED_RECIPIENT"]