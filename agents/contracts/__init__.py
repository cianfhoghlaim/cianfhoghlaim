"""Cross-agent context envelope protocol.

Per the 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1 openspec
change (spec delta on `agent-platform-cluster`, Requirement
"Cross-agent context envelope protocol"):

  "The system MUST provide a typed context-envelope protocol that any
   of the 3 agent surfaces (openclaw + openchamber + hermes) MUST use
   to hand context to any other agent surface. The protocol MUST be
   backed by the Pydantic v2 model `agents/contracts/context-envelope.py`
   (`ContextEnvelope`)."

Public surface:

- `ContextEnvelope` — the Pydantic v2 model (defined in
  `context_envelope.py`; the spec-mandated hyphen path
  `context-envelope.py` is a thin re-export shim around it)
- `receive_envelope` (in 3 sibling modules: `openclaw_handler.py`,
  `openchamber_handler.py`, `hermes_handler.py`) — the per-surface
  unpack function
- `AgentSurface` — the Literal type enumerating the 4 known surfaces

The convention is: every cross-surface handoff is a `POST` to the
recipient's surface URL with `Authorization: Basic <BRIDGE_TOKEN>`
and a JSON body of `ContextEnvelope.to_json()` (the canonical
`model_dump_json()` wrapper). The recipient calls
`ContextEnvelope.from_json(body_str)` to rehydrate, then
`receive_envelope(envelope)` to either accept (returns
`{"status": "received", ...}`) or reject (`{"status": "rejected" | "expired", ...}`).
"""

from __future__ import annotations

from .context_envelope import AgentSurface, ContextEnvelope
from .hermes_handler import receive_envelope as hermes_receive
from .openchamber_handler import receive_envelope as openchamber_receive
from .openclaw_handler import receive_envelope as openclaw_receive

__all__ = [
    "AgentSurface",
    "ContextEnvelope",
    "openclaw_receive",
    "openchamber_receive",
    "hermes_receive",
]