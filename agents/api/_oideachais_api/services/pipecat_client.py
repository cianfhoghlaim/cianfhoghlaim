"""agents.api._oideachais_api.services.pipecat_client — the Pipecat HTTP bridge.

Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
(Phase 1 §2.4 + Phase 6 wiring). Provides a typed HTTP client for
the Pipecat real-time voice transport.

Requires the Pipecat IaC stack at ``bonneagar/stacks/pipecat/``
(port 8765, env var ``PIPECAT_URL``). When the stack is unreachable
the client raises ``PipecatUnreachable`` which the voice agent
catches and falls back to the Phase 1 stub behaviour.

Reference:
  - https://github.com/pipecat-ai/pipecat — Pipecat docs
  - openspec/changes/2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/
"""

from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

PIPECAT_URL = os.getenv("PIPECAT_URL", "http://pipecat:8765/v1")
PIPECAT_TIMEOUT_SEC = float(os.getenv("PIPECAT_TIMEOUT_SEC", "30"))


class PipecatUnreachable(Exception):
    """Raised when the Pipecat HTTP service is not reachable.

    The voice_agent catches this exception and falls back to the
    Phase 1 stub behaviour (1-second silent WAV). Phase 6 wired
    implementations should NOT swallow this error if they explicitly
    want to know about Pipecat unavailability.
    """

    def __init__(self, url: str, original: Exception | None = None) -> None:
        super().__init__(f"Pipecat unreachable at {url}")
        self.url = url
        self.original = original


@dataclass(frozen=True)
class PipecatAudioRequest:
    """The canonical request to Pipecat.

    Fields:
        audio_b64: base64-encoded audio bytes from the user's microphone.
        session_id: opaque session id (e.g. Convex thread id).
        language: "en" or "ga" — drives ASR/TTS model selection.
        agent: the agent name (e.g. "cianfhoghlaim" or a per-subject agent).
    """

    audio_b64: str
    session_id: str
    language: str = "en"
    agent: str = "cianfhoghlaim"


@dataclass(frozen=True)
class PipecatAudioResponse:
    """The canonical response from Pipecat.

    Fields:
        transcript_in: the ASR transcript (None if ASR fails).
        agent_text: the LLM agent response (None if LLM call fails).
        audio_out_b64: base64-encoded TTS audio bytes (WAV/MP3/Opus).
        tts_provider: which TTS provider was used.
        voice_id: provider-specific voice id.
    """

    transcript_in: str | None
    agent_text: str | None
    audio_out_b64: str
    tts_provider: str
    voice_id: str


def _try_import_httpx():
    """Try to import httpx (the canonical Pipecat client dep).

    Returns None when httpx isn't installed (lightweight container builds
    without the voice transport) so the voice_agent can fall back to the
    Phase 1 stub.
    """
    try:
        import httpx  # type: ignore[import-not-found]
        return httpx
    except ImportError:
        return None


async def call_pipecat_roundtrip(request: PipecatAudioRequest) -> PipecatAudioResponse:
    """Send audio to Pipecat, receive agent + TTS audio response.

    Raises PipecatUnreachable when the service is down or httpx is
    not installed. The voice_agent catches this and falls back to the
    Phase 1 stub behaviour.
    """
    httpx = _try_import_httpx()
    if httpx is None:
        raise PipecatUnreachable(PIPECAT_URL)

    try:
        async with httpx.AsyncClient(timeout=PIPECAT_TIMEOUT_SEC) as client:
            response = await client.post(
                f"{PIPECAT_URL}/audio/roundtrip",
                json={
                    "audio_b64": request.audio_b64,
                    "session_id": request.session_id,
                    "language": request.language,
                    "agent": request.agent,
                },
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
    except Exception as exc:  # noqa: BLE001 — Pipecat unreachable
        logger.warning("pipecat_client.call_pipecat_roundtrip: %s", exc)
        raise PipecatUnreachable(PIPECAT_URL, original=exc) from exc

    return PipecatAudioResponse(
        transcript_in=payload.get("transcript_in"),
        agent_text=payload.get("agent_text"),
        audio_out_b64=payload.get("audio_out_b64", ""),
        tts_provider=payload.get("tts_provider", ""),
        voice_id=payload.get("voice_id", ""),
    )


def b64_audio_from_bytes(audio_bytes: bytes) -> str:
    """Helper for callers — encode raw audio bytes for the request."""
    return base64.b64encode(audio_bytes).decode("ascii")


__all__ = [
    "PIPECAT_URL",
    "PIPECAT_TIMEOUT_SEC",
    "PipecatAudioRequest",
    "PipecatAudioResponse",
    "PipecatUnreachable",
    "call_pipecat_roundtrip",
    "b64_audio_from_bytes",
]


# Suppress unused-import warning for `json` (kept for future structured logging).
_ = json