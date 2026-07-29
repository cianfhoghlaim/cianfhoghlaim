"""
Real-time voice agent built on Pipecat.

Bridges:
- ASR:   Whisper-large-v3 / wav2vec2-xlsr-53-irish (via LiteLLM)
- Agent: LiteLLM gateway (root_agent or curriculum_agent)
- TTS:   ABAIR (Irish) / Chatterbox (English) / SAM-Audio (source separation)

Requires: infrastructure/stacks/pipecat/ (port 8765)
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
        """Send audio → get agent response → TTS audio back."""
        pass  # TODO: Pipecat SDK integration
