"""
Real-time voice agent built on Pipecat.

Bridges:
- ASR:   Whisper-large-v3 / wav2vec2-xlsr-53-irish (via LiteLLM)
- Agent: LiteLLM gateway (root_agent or curriculum_agent)
- TTS:   ABAIR (Irish) / Chatterbox (English) / SAM-Audio (source separation)

Requires: infrastructure/stacks/engineering/pipecat/ (port 8765)
Reference: docs/meaisínfhoghlaim/README.md (audio model table)
"""
from __future__ import annotations
import os, logging
logger = logging.getLogger(__name__)

PIPECAT_URL = os.getenv("PIPECAT_URL", "http://pipecat:8765/v1")

class VoiceAgent:
    """High-level wrapper that abstracts the Pipecat real-time transport."""
    def __init__(self, language: str = "en"):
        self.language = language
        self.asr_model = "celtic/asr/whisper-large"
        self.tts_model = "celtic/tts/chatterbox"
        if language == "ga":
            self.asr_model = "celtic/asr/wav2vec2-irish"
            self.tts_model = "aba-tts"  # ABAIR Irish TTS

    async def process_audio(self, audio_bytes: bytes, session_id: str) -> dict:
        """Send audio → get agent response → TTS audio back."""
        pass  # TODO: Pipecat SDK integration
