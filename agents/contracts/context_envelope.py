"""Cross-agent context envelope protocol.

Defines the canonical handoff envelope that the 3 agent surfaces
(openclaw, openchamber, hermes) use to hand context to each other.

Per the 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1 openspec
change (spec delta on `agent-platform-cluster`):

  "The system MUST provide a typed context-envelope protocol that any
   of the 3 agent surfaces (openclaw + openchamber + hermes) MUST use
   to hand context to any other agent surface."

The Pydantic v2 model `ContextEnvelope` is the single source of truth
for the envelope shape. The 3 handler modules
(openclaw_handler.py, openchamber_handler.py, hermes_handler.py)
implement the per-surface unpacking logic.

Design principles:

1. The envelope is **content-agnostic**. The `context_payload` is a
   `dict[str, Any]` so each surface can put whatever it needs
   (channel metadata, IDE/CLI session state, agent run params).

2. The envelope carries a **trace correlation handle** via
   `parent_trace_id`. Every downstream LLM call inside the receiving
   surface attaches this as a span attribute so the trace correlates
   across surfaces (one span tree spans openclaw → hermes → openchamber).

3. The envelope carries an **`agent_run_id`** for run-level correlation.
   Multiple envelopes from the same logical workflow share the same
   `agent_run_id` (e.g. a multi-step BIEP v3 ingestion that hands off
   3 times).

4. The envelope carries an **`mtls_subject`** so the receiving surface
   can verify the sender's identity. In dev this is a plain string; in
   prod it's the CN of the mTLS client cert.

5. The envelope is **time-bounded** via `expires_at`. Receiving
   surfaces MUST reject envelopes where `expires_at < now()`.

6. The envelope has **`sender` + `recipient`** for routing. A surface
   that receives an envelope not addressed to it MUST return
   `{"status": "rejected", "reason": "wrong_recipient"}`.

7. The envelope is **JSON-serializable** end-to-end (Pydantic v2 with
   `model_dump_json()`). It travels over the wire as a UTF-8 JSON
   string with HTTP Basic auth (the receiving surface's `BRIDGE_TOKEN`
   per the openclaw/openchamber/hermes `.env.example`).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

AgentSurface = Literal["openclaw", "openchamber", "hermes", "ocr-router"]


class ContextEnvelope(BaseModel):
    """Canonical cross-agent context envelope.

    Every handoff from one agent surface to another MUST use this shape.
    Direct HTTP `POST` of an untyped JSON body is forbidden (per spec).
    """

    # --- Routing ---
    sender: AgentSurface = Field(
        ...,
        description="The surface that produced this envelope. One of: openclaw, openchamber, hermes, ocr-router.",
    )
    recipient: AgentSurface = Field(
        ...,
        description="The surface that should receive this envelope. Must match the receiving surface's local config; otherwise the surface returns rejected/wrong_recipient.",
    )

    # --- Correlation ---
    agent_run_id: str = Field(
        default_factory=lambda: f"run_{uuid.uuid4().hex[:12]}",
        description="Run-level correlation id. Multiple envelopes from the same logical workflow share the same id.",
    )
    parent_trace_id: str = Field(
        default="0",
        description="The OpenTelemetry trace id of the sender's parent span. The receiving surface attaches this as a span attribute on every downstream call so the trace correlates across surfaces.",
    )

    # --- Content ---
    context_payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Content-agnostic payload. Each surface decides what to put here (channel metadata, IDE session state, agent run params).",
    )

    # --- Identity ---
    mtls_subject: str = Field(
        default="dev-no-mtls",
        description="The mTLS client cert subject (CN) of the sender. In dev this is a plain string ('dev-no-mtls'); in prod it's the CN of the sender's client cert.",
    )

    # --- Time-bounding ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the sender created the envelope (UTC).",
    )
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=15),
        description="When the envelope expires (UTC). Receiving surfaces MUST reject envelopes where expires_at < now().",
    )

    # --- Optional metadata ---
    description: str | None = Field(
        default=None,
        description="Human-readable description of what the envelope contains. Used for log traces + the Langfuse span metadata.",
    )

    @field_validator("expires_at")
    @classmethod
    def _expires_after_created(cls, v: datetime, info: Any) -> datetime:
        """Reject envelopes that expire before they were created."""
        created = info.data.get("created_at")
        if created is not None and v <= created:
            raise ValueError(f"expires_at ({v}) must be after created_at ({created})")
        return v

    @field_validator("agent_run_id")
    @classmethod
    def _agent_run_id_format(cls, v: str) -> str:
        """Validate the agent_run_id format (must start with `run_`)."""
        if not v.startswith("run_"):
            raise ValueError(f"agent_run_id must start with 'run_'; got {v!r}")
        if len(v) < 8:
            raise ValueError(f"agent_run_id too short: {v!r}")
        return v

    def is_expired(self, now: datetime | None = None) -> bool:
        """Return True if the envelope has expired."""
        now = now or datetime.now(timezone.utc)
        return self.expires_at <= now

    def to_header(self) -> dict[str, str]:
        """Serialize as HTTP headers (for use with `requests` or `httpx`)."""
        return {
            "X-Agent-Sender": self.sender,
            "X-Agent-Recipient": self.recipient,
            "X-Agent-Run-Id": self.agent_run_id,
            "X-Agent-Trace-Id": self.parent_trace_id,
            "X-Agent-Expires-At": self.expires_at.isoformat(),
            "Content-Type": "application/json",
        }

    def to_json(self) -> str:
        """Serialize the envelope to a UTF-8 JSON string.

        The canonical wire format for cross-surface handoff. The recipient
        calls `ContextEnvelope.from_json(json_str)` to rehydrate.

        Example::

            payload = envelope.to_json()
            # → '{"sender":"openclaw","recipient":"hermes",...}'

            # Rehydrate on the receiving surface:
            envelope = ContextEnvelope.from_json(payload)
        """
        # `model_dump_json()` is the Pydantic v2 built-in; we wrap it for
        # the canonical method name.
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str | bytes) -> "ContextEnvelope":
        """Rehydrate an envelope from its JSON wire form.

        Inverse of `to_json()`. Raises `pydantic.ValidationError` if the
        payload is malformed or fails any field-level validator (e.g.
        `expires_at < created_at`).
        """
        if isinstance(json_str, bytes):
            json_str = json_str.decode("utf-8")
        return cls.model_validate_json(json_str)


__all__ = ["ContextEnvelope", "AgentSurface"]