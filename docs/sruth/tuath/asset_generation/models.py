"""Asset generation data models."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Types of game assets."""

    CHARACTER_PORTRAIT = "character_portrait"
    ITEM_ICON = "item_icon"
    CLAN_HERALDRY = "clan_heraldry"
    TERRITORY_TILE = "territory_tile"
    SPELL_EFFECT = "spell_effect"
    CREATURE = "creature"


class CelticStyle(str, Enum):
    """Celtic art styles for generation."""

    LA_TENE = "la_tene"
    OGHAM = "ogham"
    KNOTWORK = "knotwork"
    ZOOMORPHIC = "zoomorphic"
    SPIRAL = "spiral"
    ILLUMINATED = "illuminated"


class GenerationModel(str, Enum):
    """Available generation models."""

    FLUX_DEV = "black-forest-labs/FLUX.1-dev"
    FLUX_SCHNELL = "black-forest-labs/FLUX.1-schnell"
    SDXL_TURBO = "stabilityai/sdxl-turbo"
    QWEN_VL = "Qwen/Qwen2-VL-7B-Instruct"


class ItemRarity(str, Enum):
    """Item rarity levels."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ClanId(str, Enum):
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
    prompt_override: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    steps: int = Field(default=20, ge=1, le=100)
    guidance_scale: float = Field(default=7.5, ge=1.0, le=20.0)

    # Asset-specific parameters
    item_name: Optional[str] = None
    item_type: Optional[str] = None
    rarity: ItemRarity = ItemRarity.COMMON
    clan: Optional[ClanId] = None
    power_level: int = Field(default=1, ge=1, le=100)

    # Caching
    cache_key: Optional[str] = None
    use_cache: bool = True

    class Config:
        use_enum_values = True


class AssetResponse(BaseModel):
    """Response from asset generation."""

    success: bool
    asset_id: str

    # Image data
    image_url: Optional[str] = None
    image_base64: Optional[str] = None

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
    ipfs_cid: Optional[str] = None
    arweave_id: Optional[str] = None

    # Error handling
    error: Optional[str] = None

    class Config:
        use_enum_values = True


class BatchAssetRequest(BaseModel):
    """Batch request for multiple assets."""

    requests: list[AssetRequest]
    priority: int = Field(default=0, ge=0, le=10)
    callback_url: Optional[str] = None

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
