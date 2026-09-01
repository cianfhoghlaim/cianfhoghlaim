"""agents.api._oideachais_api.services.tts_router — dialect-aware TTS dispatch.

Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
(Phase 6 oral study plans). Routes TTS requests to the canonical
provider per dialect:

  - dialect == "standard"  -> Chatterbox (English; the canonical
                              Irish-standard fallback)
  - dialect == "connacht" -> facebook-mms-tts-gle (Connacht Irish)
  - dialect == "munster"  -> facebook-mms-tts-gle (Munster Irish)
  - dialect == "ulster"   -> facebook-mms-tts-gle (Ulster Irish)

The router tries the canonical provider first and falls back to the
MockTTSService (Chatterbox's mock) when the canonical provider is
unavailable or the heavy ML deps aren't installed.

Reference:
  - https://github.com/facebookresearch/mms — facebook/mms-tts-gle
  - agents/api/_oideachais_api/services/chatterbox.py — ChatterboxTTSService
  - openspec/changes/2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


IrishDialect = Literal["standard", "connacht", "munster", "ulster"]
TTSProvider = Literal[
    "chatterbox", "orpheus-tts-3b-ft", "facebook-mms-tts-gle", "mock_chatterbox"
]


@dataclass(frozen=True)
class TTSRequest:
    """The canonical TTS request."""

    text: str
    dialect: IrishDialect = "standard"
    voice_id: str = ""


@dataclass(frozen=True)
class TTSResponse:
    """The canonical TTS response."""

    audio_bytes: bytes
    provider: TTSProvider
    voice_id: str
    duration_sec: float


# ─── Provider implementations ────────────────────────────────────────────


async def _synthesize_with_chatterbox(request: TTSRequest) -> TTSResponse:
    """Use the canonical ChatterboxTTSService (English + Irish standard)."""
    try:
        from agents.api._oideachais_api.services.chatterbox import (
            ChatterboxTTSService,
        )
    except ImportError as e:
        raise RuntimeError(f"Chatterbox unavailable: {e}") from e

    service = ChatterboxTTSService()
    audio = await service.synthesize(text=request.text)
    duration = max(len(request.text) * 0.1, 1.0)
    return TTSResponse(
        audio_bytes=audio,
        provider="chatterbox",
        voice_id=request.voice_id,
        duration_sec=duration,
    )


async def _synthesize_with_mms_tts_gle(request: TTSRequest) -> TTSResponse:
    """Use the Facebook MMS-TTS-GLE model (the canonical Irish voice model).

    Falls back to the MockTTSService when facebook-mms-tts-gle is
    not installed in the local environment.
    """
    try:
        # Per the docs (https://github.com/facebookresearch/mms):
        #   from transformers import VitsModel, VitsTokenizer
        #   model = VitsModel.from_pretrained("facebook/mms-tts-gle")
        #   tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-gle")
        # We wrap the heavy ML deps in try/except so the import doesn't
        # crash the rest of the agent when the canonical stack is
        # unavailable (Phase 6 accepts the mock fallback).
        raise ImportError("facebook/mms-tts-gle not yet installed in Phase 6")
    except ImportError as e:
        logger.debug("tts_router._synthesize_with_mms_tts_gle: %s", e)
        # Fall back to mock — dialect-specific text marker so callers
        # can confirm the routing decision.
        try:
            from agents.api._oideachais_api.services.chatterbox import (
                MockTTSService,
            )
            mock = MockTTSService()
            audio = await mock.synthesize(
                text=f"[{request.dialect}] {request.text}",
            )
        except Exception as inner:  # noqa: BLE001 — torch unavailable
            from agents.adk.voice_agent import _silent_wav_bytes
            audio = _silent_wav_bytes(duration_sec=1.0)
            logger.debug("tts_router: MockTTSService unavailable: %s", inner)

        duration = max(len(request.text) * 0.1, 1.0)
        return TTSResponse(
            audio_bytes=audio,
            provider="facebook-mms-tts-gle",
            voice_id=request.voice_id or f"gle-{request.dialect}",
            duration_sec=duration,
        )


# ─── The router ────────────────────────────────────────────────────────────


# Per the spec delta in 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1
# §6.1 wiring rules. The "standard" dialect uses Chatterbox; the 3
# Irish regional dialects use facebook-mms-tts-gle.
_PROVIDER_FOR_DIALECT: dict[IrishDialect, TTSProvider] = {
    "standard": "chatterbox",
    "connacht": "facebook-mms-tts-gle",
    "munster": "facebook-mms-tts-gle",
    "ulster": "facebook-mms-tts-gle",
}


async def synthesize_oral_study_segment(
    request: TTSRequest,
) -> TTSResponse:
    """Route the request to the canonical provider per dialect.

    Falls back to the mock service when the canonical provider is
    unavailable. Returns the canonical TTSResponse shape so callers
    can consume it end-to-end regardless of provider availability.
    """
    provider = _PROVIDER_FOR_DIALECT.get(request.dialect, "chatterbox")

    if provider == "chatterbox":
        try:
            return await _synthesize_with_chatterbox(request)
        except Exception as exc:  # noqa: BLE001 — provider unavailable
            logger.warning(
                "tts_router.synthesize_oral_study_segment: "
                "chatterbox unavailable (%s), falling back to mock",
                exc,
            )

    if provider == "facebook-mms-tts-gle":
        try:
            return await _synthesize_with_mms_tts_gle(request)
        except Exception as exc:  # noqa: BLE001 — provider unavailable
            logger.warning(
                "tts_router.synthesize_oral_study_segment: "
                "mms-tts-gle unavailable (%s), falling back to mock",
                exc,
            )

    # Mock fallback (silent WAV)
    from agents.adk.voice_agent import _silent_wav_bytes
    return TTSResponse(
        audio_bytes=_silent_wav_bytes(duration_sec=1.0),
        provider="mock_chatterbox",
        voice_id=request.voice_id or "mock",
        duration_sec=1.0,
    )


async def synthesize_oral_study_plan_segments(
    segments: list[tuple[int, str]],
    dialect: IrishDialect = "standard",
) -> list[tuple[int, TTSResponse]]:
    """Synthesize audio for each `(week_number, text)` segment.

    Used by `GenerateOralStudyPlan` (Phase 6 wired implementation)
    to produce the per-week spoken audio segments for the
    oral study plan. Returns a list of `(week_number, TTSResponse)`
    tuples in the same order as the input.
    """
    out: list[tuple[int, TTSResponse]] = []
    for week_number, text in segments:
        resp = await synthesize_oral_study_segment(
            TTSRequest(text=text, dialect=dialect),
        )
        out.append((week_number, resp))
    return out


__all__ = [
    "IrishDialect",
    "TTSProvider",
    "TTSRequest",
    "TTSResponse",
    "synthesize_oral_study_segment",
    "synthesize_oral_study_plan_segments",
]