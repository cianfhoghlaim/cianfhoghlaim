"""Asset generation data models."""

from enum import StrEnum

from pydantic import BaseModel, Field


class AssetType(StrEnum):
    """Types of game assets."""
    CHARACTER_PORTRAIT = "character_portrait"
    ITEM_ICON = "item_icon"
    CLAN_HERALDRY = "clan_heraldry"
    TERRITORY_TILE = "territory_tile"
    SPELL_EFFECT = "spell_effect"
    CREATURE = "creature"


class CelticStyle(StrEnum):
    """Celtic art styles for generation."""
    LA_TENE = "la_tene"
    OGHAM = "ogham"
    KNOTWORK = "knotwork"
    ZOOMORPHIC = "zoomorphic"
    SPIRAL = "spiral"
    ILLUMINATED = "illuminated"


class GenerationModel(StrEnum):
    """Available generation models."""
    FLUX_DEV = "black-forest-labs/FLUX.1-dev"
    FLUX_SCHNELL = "black-forest-labs/FLUX.1-schnell"
    SDXL_TURBO = "stabilityai/sdxl-turbo"
    QWEN_VL = "Qwen/Qwen2-VL-7B-Instruct"


class ItemRarity(StrEnum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ClanId(StrEnum):
    """Celtic clan identifiers."""
    TUATHA_DE_DANANN = "tuatha_de_danann"
    FIR_BOLG = "fir_bolg"
    FOMORIANS = "fomorians"
    MILESIANS = "milesians"


class AssetRequest(BaseModel):
    """Request for asset generation."""

    asset_type: AssetType
    style: CelticStyle = CelticStyle.KNOTWORK
    model: GenerationModel = GenerationModel.FLUX_SCHNELL

    # Dimensions
    width: int = Field(default=512, ge=256, le=2048)
    height: int = Field(default=512, ge=256, le=2048)

    # Generation parameters
    prompt_override: str | None = None
    negative_prompt: str | None = None
    seed: int | None = None
    steps: int = Field(default=20, ge=1, le=100)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)

    # Asset-specific parameters
    item_name: str | None = None
    item_type: str | None = None
    rarity: ItemRarity = ItemRarity.COMMON
    clan: ClanId | None = None
    power_level: int = Field(default=1, ge=1, le=100)

    # Caching
    cache_key: str | None = None
    use_cache: bool = True

    class Config:
        use_enum_values = True


class AssetResponse(BaseModel):
    """Response from asset generation."""

    success: bool
    asset_id: str

    # Image data
    image_url: str | None = None
    image_base64: str | None = None

    # Metadata
    prompt_used: str
    model_used: str
    generation_time_ms: int

    # Asset details
    asset_type: AssetType
    style: CelticStyle
    width: int
    height: int

    # Storage
    ipfs_cid: str | None = None
    arweave_id: str | None = None

    # Error handling
    error: str | None = None

    class Config:
        use_enum_values = True


class BatchAssetRequest(BaseModel):
    """Batch request for multiple assets."""

    requests: list[AssetRequest]
    priority: int = Field(default=0, ge=0, le=10)
    callback_url: str | None = None

    class Config:
        use_enum_values = True


class BatchAssetResponse(BaseModel):
    """Response from batch asset generation."""

    batch_id: str
    total_requested: int
    completed: int
    failed: int
    results: list[AssetResponse]

    class Config:
        use_enum_values = True
