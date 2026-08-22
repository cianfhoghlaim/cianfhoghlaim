"""baml_src.media — TG4 + Foghlaim Media Classification.

Per the `2026-08-25-tg4-foghlaim-corpus-v1` openspec change.
The 4 BAML functions + 4 Pydantic classes defined at
`baml_src/media/tg4_classification.baml` are imported here for
convenience.
"""
from .tg4_classification import (
    AuditTranscriptQuality,
    ClassifyTg4Episode,
    ExtractSpeakerLineup,
    ExtractWorksheetAnswers,
    Speaker,
    SpeakerLineup,
    SpeakerTurn,
    TranscriptQualityAudit,
    Tg4EpisodeClassification,
    WorksheetAnswers,
    WorksheetQuestion,
)

__all__ = [
    "AuditTranscriptQuality",
    "ClassifyTg4Episode",
    "ExtractSpeakerLineup",
    "ExtractWorksheetAnswers",
    "Speaker",
    "SpeakerLineup",
    "SpeakerTurn",
    "TranscriptQualityAudit",
    "Tg4EpisodeClassification",
    "WorksheetAnswers",
    "WorksheetQuestion",
]