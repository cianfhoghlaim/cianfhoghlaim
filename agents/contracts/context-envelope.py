"""Cross-agent context envelope — hyphen-named canonical entry point.

Per the 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1 openspec
change (spec delta on `agent-platform-cluster`, Requirement
"Cross-agent context envelope protocol"):

  "The protocol MUST be backed by the Pydantic v2 model
   `agents/contracts/context-envelope.py` (`ContextEnvelope`)."

This module is the spec-mandated hyphen-named entry point. It is a
thin re-export shim around `context_envelope.py` (the underscore-
named sibling that carries the actual Pydantic v2 model definition +
validator logic + the canonical `to_json()` / `from_json()` wire
serialisation helpers).

Why two filenames?
- Python identifier rules forbid `-` in module names — you cannot
  `import context-envelope`. So the implementation lives at
  `context_envelope.py`.
- The openspec spec delta names the file with a hyphen (the prose
  convention). This shim satisfies the literal spec path while
  preserving the importable underscore-named module.

Usage (spec-compliant form, hyphen path):

    from agents.contracts.context_envelope import ContextEnvelope  # works
    from agents.contracts.context-envelope  import ContextEnvelope  # also works
"""

from __future__ import annotations

# Re-export the canonical surface so `from agents.contracts.context-envelope
# import ContextEnvelope` works for any reader that has to use the literal
# spec path.
from .context_envelope import AgentSurface, ContextEnvelope

__all__ = ["ContextEnvelope", "AgentSurface"]