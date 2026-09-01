"""
Real-time voice agent built on Pipecat.

Bridges:
- ASR:   Whisper-large-v3 / wav2vec2-xlsr-53-irish (via LiteLLM)
- Agent: LiteLLM gateway (root_agent or curriculum_agent)
- TTS:   ABAIR (Irish) / Chatterbox (English) / SAM-Audio (source separation)

Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
(Phase 1 §2.4) + the 2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1
change (Phase 6 oral study plans):

- Phase 1 ships a wired Pipecat client stub that logs the round-trip.
- Phase 6 wires the real Pipecat HTTP client
  (agents.api._oideachais_api.services.pipecat_client.call_pipecat_roundtrip)
  + the dialect-aware TTS router
  (agents.api._oideachais_api.services.tts_router).

Requires: bonneagar/stacks/pipecat/ (port 8765)
Reference: docs/meaisínfhoghlaim/README.md (audio model table)
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

PIPECAT_URL = os.getenv("PIPECAT_URL", "http://pipecat:8765/v1")


def _voice_models_for(language: str) -> tuple[str, str]:
    """Return (asr_model, tts_model) for the given language.

    Resolved via MODEL_REGISTRY (the centralized-model-registry
    openspec change). Falls back to the historical hardcoded
    voice paths when the registry import fails (e.g. optional-dep
    issues at import time).
    """
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        if language == "ga":
            asr_model = MODEL_REGISTRY.resolve("voice", "asr_irish")
            tts_model = MODEL_REGISTRY.resolve("voice", "tts_irish")
        else:
            asr_model = MODEL_REGISTRY.resolve("voice", "asr")
            tts_model = MODEL_REGISTRY.resolve("voice", "tts")
        return asr_model, tts_model
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        if language == "ga":
            return "wav2vec2-irish", "aba-tts"
        return "whisper-large", "chatterbox"


class VoiceAgent:
    """High-level wrapper that abstracts the Pipecat real-time transport.

    Phase 6 (oral study plans) replaces the Phase 1 stub body with
    a real Pipecat HTTP round-trip (agents.api._oideachais_api.services.
    pipecat_client.call_pipecat_roundtrip). Falls back to the Phase 1
    silent-WAV stub when the Pipecat service is unreachable (the
    canonical lightweight-container behaviour).
    """

    def __init__(self, language: str = "en"):
        self.language = language
        self.asr_model, self.tts_model = _voice_models_for(language)

    async def process_audio(self, audio_bytes: bytes, session_id: str) -> dict:
        """Send audio → get agent response → TTS audio back.

        Phase 6 wired implementation: delegates to the canonical Pipecat
        HTTP client. When the service is unreachable (PipecatUnreachable
        exception), falls back to the Phase 1 silent-WAV behaviour so the
        agent works in lightweight container builds.
        """
        import base64

        from agents.api._oideachais_api.services.pipecat_client import (
            PipecatAudioRequest,
            PipecatUnreachable,
            b64_audio_from_bytes,
            call_pipecat_roundtrip,
        )

        audio_b64 = b64_audio_from_bytes(audio_bytes)
        request = PipecatAudioRequest(
            audio_b64=audio_b64,
            session_id=session_id,
            language=self.language,
            agent="cianfhoghlaim",
        )

        tts_provider = "phase6_unreachable"
        try:
            response = await call_pipecat_roundtrip(request)
            return {
                "session_id": session_id,
                "transcript_in": response.transcript_in,
                "agent_text": response.agent_text,
                "audio_out_bytes": base64.b64decode(response.audio_out_b64),
                "audio_out_b64": response.audio_out_b64,
                "tts_provider": response.tts_provider,
                "voice_id": response.voice_id,
                "phase": "phase6_wired",
                "phase_marker": "PHASE_6_WIRED",
            }
        except PipecatUnreachable as exc:
            logger.warning(
                "voice_agent.process_audio: Pipecat unreachable at %s, "
                "falling back to silent WAV",
                exc.url,
            )
            tts_audio_bytes = _silent_wav_bytes(duration_sec=1.0)
            return {
                "session_id": session_id,
                "transcript_in": None,
                "agent_text": None,
                "audio_out_bytes": tts_audio_bytes,
                "audio_out_b64": base64.b64encode(tts_audio_bytes).decode("ascii"),
                "tts_provider": tts_provider,
                "voice_id": "",
                "phase": "phase6_unreachable",
                "phase_marker": "PHASE_6_UNREACHABLE",
            }


def _silent_wav_bytes(duration_sec: float = 1.0, sample_rate: int = 22050) -> bytes:
    """Emit a 1-second silent WAV via the stdlib `wave` module.

    No torch / torchaudio / pydub required — works in any container
    build. Format: PCM 16-bit mono at 22.05 kHz.
    """
    import io

    n_samples = int(duration_sec * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_out:
        wav_out.setnchannels(1)
        wav_out.setsampwidth(2)  # 16-bit
        wav_out.setframerate(sample_rate)
        wav_out.writeframes(b"\x00\x00" * n_samples)
    return buf.getvalue()