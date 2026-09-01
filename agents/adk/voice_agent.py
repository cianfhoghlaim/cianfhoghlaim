"""
Real-time voice agent built on Pipecat.

Bridges:
- ASR:   Whisper-large-v3 / wav2vec2-xlsr-53-irish (via LiteLLM)
- Agent: LiteLLM gateway (root_agent or curriculum_agent)
- TTS:   ABAIR (Irish) / Chatterbox (English) / SAM-Audio (source separation)

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
    """High-level wrapper that abstracts the Pipecat real-time transport."""
    def __init__(self, language: str = "en"):
        self.language = language
        self.asr_model, self.tts_model = _voice_models_for(language)

    async def process_audio(self, audio_bytes: bytes, session_id: str) -> dict:
        """Send audio → get agent response → TTS audio back.

        Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
        (Phase 1 §2.4): Phase 1 ships a wired Pipecat client stub that
        logs the round-trip; the real TTS round-trip (Chatterbox +
        orpheus-tts-3b-ft + facebook-mms-tts-gle) is delivered in
        Phase 6 (oral study plans).

        The stub returns the canonical response shape so callers can
        consume it end-to-end; the audio bytes field is populated with
        a 1-second silent WAV. Tries `MockTTSService` first (which
        uses torch + torchaudio); falls back to a stdlib-only silent
        WAV generator when torch isn't installed (so the stub works in
        lightweight container builds).
        """
        import base64
        import struct
        import wave

        # Phase 1 stub: round-trip the audio through MockTTSService when
        # torch is available; otherwise emit a 1-second silent WAV via
        # the stdlib `wave` module. The response shape is identical so
        # downstream consumers don't need to branch on the provider.
        tts_audio_bytes = _silent_wav_bytes(duration_sec=1.0)
        tts_provider = "phase1_stdlib_wav"
        try:
            from agents.api._oideachais_api.services.chatterbox import (
                MockTTSService,
            )

            mock = MockTTSService()
            tts_audio_bytes = await mock.synthesize(
                text=f"phase1-stub echo for session {session_id}",
            )
            tts_provider = "mock_chatterbox_phase1_stub"
        except Exception as exc:  # noqa: BLE001 — torch unavailable
            logger.debug(
                "voice_agent.process_audio: MockTTSService unavailable, "
                "falling back to stdlib silent WAV: %s",
                exc,
            )

        logger.info(
            "voice_agent.process_audio phase1_stub session_id=%s "
            "tts_provider=%s audio_out_bytes=%d",
            session_id,
            tts_provider,
            len(tts_audio_bytes),
        )

        return {
            "session_id": session_id,
            "transcript_in": None,  # Phase 6: real Whisper ASR
            "agent_text": None,  # Phase 6: real LLM response
            "audio_out_bytes": tts_audio_bytes,
            "audio_out_b64": base64.b64encode(tts_audio_bytes).decode("ascii"),
            "tts_provider": tts_provider,
            "voice_id": "",
            "phase": "phase1_stub",
            "phase_marker": "PHASE_1_STUB",
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
