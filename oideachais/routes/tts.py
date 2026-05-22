"""
TTS API Routes.

Endpoints for Irish text-to-speech pronunciation using Chatterbox.
"""

import os

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from ..services.chatterbox import (
    IrishDialect,
    TTSError,
    get_mock_tts_service,
    get_tts_service,
)

router = APIRouter(prefix="/tts", tags=["tts"])

# Use mock service if Chatterbox not available
USE_MOCK = os.getenv("TTS_USE_MOCK", "false").lower() == "true"


class SynthesizeRequest(BaseModel):
    """Request to synthesize text."""

    text: str = Field(..., min_length=1, max_length=500, description="Text to synthesize")
    dialect: IrishDialect = Field(
        default=IrishDialect.STANDARD,
        description="Irish dialect: connacht, munster, ulster, standard",
    )
    language: str = Field(default="ga", description="Language code: ga (Irish), en (English)")


class PronounceRequest(BaseModel):
    """Request to pronounce a word."""

    word: str = Field(..., min_length=1, max_length=100, description="Word to pronounce")
    dialect: IrishDialect = Field(
        default=IrishDialect.STANDARD,
        description="Irish dialect for pronunciation",
    )


def _get_service():
    """Get appropriate TTS service."""
    if USE_MOCK:
        return get_mock_tts_service()
    try:
        return get_tts_service()
    except ImportError:
        # Fallback to mock if Chatterbox not installed
        return get_mock_tts_service()


@router.post("/synthesize")
async def synthesize(request: SynthesizeRequest) -> Response:
    """
    Synthesize text to speech.

    Returns WAV audio (24kHz, mono).

    **Parameters:**
    - text: Text to synthesize (1-500 characters)
    - dialect: Irish dialect (connacht, munster, ulster, standard)
    - language: Language code (ga for Irish, en for English)
    """
    service = _get_service()

    try:
        audio_bytes = await service.synthesize(
            text=request.text,
            dialect=request.dialect,
            language=request.language,
        )

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'inline; filename="pronunciation.wav"',
                "X-Dialect": request.dialect.value,
            },
        )
    except TTSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {e}")


@router.post("/pronounce")
async def pronounce(request: PronounceRequest) -> Response:
    """
    Pronounce a single Irish word.

    Optimized for vocabulary pronunciation.

    **Parameters:**
    - word: Word to pronounce (1-100 characters)
    - dialect: Irish dialect for pronunciation
    """
    service = _get_service()

    try:
        audio_bytes = await service.pronounce(
            word=request.word,
            dialect=request.dialect,
        )

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'inline; filename="{request.word}.wav"',
                "X-Dialect": request.dialect.value,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TTSError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pronunciation failed: {e}")


@router.get("/dialects")
async def list_dialects():
    """
    List available Irish dialects.

    Returns dialect options with descriptions.
    """
    return {
        "dialects": [
            {
                "id": "connacht",
                "name": "Connacht",
                "region": "West (Galway, Mayo, Roscommon)",
                "description": "Western Irish dialect, often considered the 'standard' spoken form",
            },
            {
                "id": "munster",
                "name": "Munster",
                "region": "South (Cork, Kerry, Waterford)",
                "description": "Southern Irish dialect with distinctive vowel sounds",
            },
            {
                "id": "ulster",
                "name": "Ulster",
                "region": "North (Donegal, Belfast area)",
                "description": "Northern Irish dialect with Scottish Gaelic influences",
            },
            {
                "id": "standard",
                "name": "Standard",
                "region": "Official",
                "description": "An Caighdeán Oifigiúil - Official standardized Irish",
            },
        ]
    }


@router.get("/health")
async def health_check():
    """Check TTS service health."""
    try:
        service = _get_service()
        return {
            "status": "healthy",
            "mock": USE_MOCK or isinstance(service, type(get_mock_tts_service())),
            "device": getattr(service, "device", "unknown"),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
