"""
TTS training and voice cloning for Celtic languages.

Integrates with:
- ABAIR.ie (Irish TTS)
- ElevenLabs (voice cloning)
- Coqui TTS (open-source)
"""

from __future__ import annotations

from dagster import (
    asset,
    AssetExecutionContext,
    Config,
    Output,
    MetadataValue,
)


class TTSConfig(Config):
    """Configuration for TTS training."""
    target_language: str = "ga"
    voice_style: str = "connacht"  # connacht, munster, ulster, donegal
    use_elevenlabs: bool = True
    sample_rate: int = 22050


# Celtic TTS systems
CELTIC_TTS_SYSTEMS = {
    "ga": [
        {
            "name": "ABAIR",
            "url": "https://www.abair.ie",
            "voices": ["connacht_female", "connacht_male", "ulster_female", "munster_male"],
            "quality": "high",
            "type": "neural",
        },
    ],
    "cy": [
        {
            "name": "Welsh TTS",
            "url": "https://techiaith.cymru",
            "voices": ["north_female", "south_male"],
            "quality": "medium",
            "type": "neural",
        },
    ],
    "gd": [
        {
            "name": "Cainnt",
            "url": "https://www.abdn.ac.uk/cainnt",
            "voices": ["lewis_female", "lewis_male"],
            "quality": "medium",
            "type": "hybrid",
        },
    ],
}


@asset(
    group_name="tts_training",
    description="Inventory Celtic TTS systems",
)
def tts_system_inventory(
    context: AssetExecutionContext,
    config: TTSConfig,
) -> Output[list[dict]]:
    """Inventory available TTS systems."""
    systems = []

    if config.target_language in CELTIC_TTS_SYSTEMS:
        for system in CELTIC_TTS_SYSTEMS[config.target_language]:
            systems.append({
                "language": config.target_language,
                **system,
                "status": "available",
            })

    context.log.info(f"Found {len(systems)} TTS systems for {config.target_language}")

    return Output(
        systems,
        metadata={
            "system_count": MetadataValue.int(len(systems)),
            "language": MetadataValue.text(config.target_language),
        },
    )


@asset(
    group_name="tts_training",
    description="Prepare TTS training data",
    deps=[tts_system_inventory],
)
def tts_training_data(
    context: AssetExecutionContext,
    config: TTSConfig,
    collected_celtic_audio: dict,
) -> Output[dict]:
    """Prepare audio data for TTS training."""
    training_data = {
        "language": config.target_language,
        "sample_rate": config.sample_rate,
        "format": "wav",
        "transcriptions": [],
        "total_hours": 0,
        "speakers": [],
    }

    if config.target_language in collected_celtic_audio:
        lang_audio = collected_celtic_audio[config.target_language]
        training_data["total_hours"] = lang_audio.get("total_hours", 0)

    return Output(
        training_data,
        metadata={
            "total_hours": MetadataValue.float(training_data["total_hours"]),
        },
    )


@asset(
    group_name="tts_training",
    description="Create ElevenLabs voice clone",
    deps=[tts_training_data],
)
def elevenlabs_voice_clone(
    context: AssetExecutionContext,
    config: TTSConfig,
    tts_training_data: dict,
) -> Output[dict]:
    """Create voice clone using ElevenLabs."""
    if not config.use_elevenlabs:
        return Output(
            {"status": "skipped", "reason": "ElevenLabs disabled"},
            metadata={"status": MetadataValue.text("skipped")},
        )

    voice_clone = {
        "name": f"celtic-{config.target_language}-{config.voice_style}",
        "language": config.target_language,
        "style": config.voice_style,
        "status": "pending",
        "voice_id": None,
        "sample_audio_url": None,
    }

    context.log.info(f"Would create voice clone: {voice_clone['name']}")

    return Output(
        voice_clone,
        metadata={
            "voice_name": MetadataValue.text(voice_clone["name"]),
        },
    )


# Export assets
tts_training_assets = [
    tts_system_inventory,
    tts_training_data,
    elevenlabs_voice_clone,
]
