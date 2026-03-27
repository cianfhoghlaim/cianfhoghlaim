"""Abstract base class for game engine asset exporters."""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Optional, Any
from pydantic import BaseModel, Field

from ..models import AssetType, CelticStyle, AssetResponse


class TargetEngine(str, Enum):
    """Supported game engines for export."""
    GODOT = "godot"
    UNITY = "unity"
    UNREAL = "unreal"
    BABYLON = "babylon"


class TextureFormat(str, Enum):
    """Texture compression formats."""
    PNG = "png"
    WEBP = "webp"
    BC7 = "bc7"      # Desktop (DX11+)
    ASTC = "astc"    # Mobile (iOS/Android)
    ETC2 = "etc2"    # OpenGL ES 3.0
    BASIS = "basis"  # Universal compressed


class MeshFormat(str, Enum):
    """3D mesh formats."""
    GLTF = "gltf"
    GLB = "glb"
    FBX = "fbx"
    OBJ = "obj"


class ExportConfig(BaseModel):
    """Configuration for asset export."""

    # Target engine
    engine: TargetEngine
    output_dir: Path

    # Texture settings
    texture_format: TextureFormat = TextureFormat.PNG
    texture_max_size: int = Field(default=2048, ge=64, le=8192)
    generate_mipmaps: bool = True

    # Mesh settings (for 3D assets)
    mesh_format: MeshFormat = MeshFormat.GLTF
    generate_lod: bool = True
    lod_levels: int = Field(default=3, ge=1, le=5)

    # Metadata
    include_metadata: bool = True
    embed_celtic_style: bool = True

    # Engine-specific overrides
    engine_config: dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class ExportResult(BaseModel):
    """Result of an export operation."""

    success: bool
    engine: TargetEngine
    asset_type: AssetType

    # Generated files
    primary_file: Optional[Path] = None
    additional_files: list[Path] = Field(default_factory=list)

    # Metadata
    export_time_ms: int = 0
    file_sizes: dict[str, int] = Field(default_factory=dict)

    # For engines that need import steps
    import_instructions: Optional[str] = None

    # Error handling
    error: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class BaseExporter(ABC):
    """Abstract base class for game engine exporters.

    Subclasses must implement:
    - export_texture(): Export 2D texture assets
    - export_material(): Export material/shader definitions
    - export_scene(): Export scene files with positioned assets
    - get_file_extension(): Return primary file extension for engine
    """

    def __init__(self, config: ExportConfig):
        self.config = config
        self._ensure_output_dir()

    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Human-readable engine name."""
        ...

    @property
    @abstractmethod
    def engine_version(self) -> str:
        """Target engine version."""
        ...

    @abstractmethod
    def export_texture(
        self,
        asset: AssetResponse,
        image_data: bytes,
        name: str,
    ) -> ExportResult:
        """Export a 2D texture asset.

        Args:
            asset: Asset metadata from generation
            image_data: Raw image bytes (PNG)
            name: Asset name for file naming

        Returns:
            ExportResult with generated file paths
        """
        ...

    @abstractmethod
    def export_material(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> ExportResult:
        """Export a material definition.

        Args:
            name: Material name
            textures: Map of texture slots to file paths
            style: Celtic art style for shader hints
            properties: Material properties (colors, values)

        Returns:
            ExportResult with generated file paths
        """
        ...

    @abstractmethod
    def export_scene(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> ExportResult:
        """Export a scene with positioned assets.

        Args:
            name: Scene name
            assets: List of (asset, transform) tuples

        Returns:
            ExportResult with generated file paths
        """
        ...

    @abstractmethod
    def get_file_extension(self, asset_type: AssetType) -> str:
        """Get the primary file extension for an asset type.

        Args:
            asset_type: Type of asset being exported

        Returns:
            File extension without leading dot
        """
        ...

    def validate_asset(self, asset: AssetResponse) -> list[str]:
        """Validate asset before export.

        Returns list of warnings (empty if valid).
        """
        warnings = []

        if not asset.success:
            warnings.append(f"Asset generation failed: {asset.error}")

        if asset.width > self.config.texture_max_size:
            warnings.append(
                f"Texture width {asset.width} exceeds max {self.config.texture_max_size}"
            )

        if asset.height > self.config.texture_max_size:
            warnings.append(
                f"Texture height {asset.height} exceeds max {self.config.texture_max_size}"
            )

        return warnings

    def generate_metadata(self, asset: AssetResponse) -> dict[str, Any]:
        """Generate metadata dict for embedding in exported assets."""
        return {
            "generator": "cianfhoghlaim-asset-pipeline",
            "asset_id": asset.asset_id,
            "asset_type": asset.asset_type,
            "celtic_style": asset.style,
            "model_used": asset.model_used,
            "prompt": asset.prompt_used,
            "dimensions": {"width": asset.width, "height": asset.height},
            "ipfs_cid": asset.ipfs_cid,
            "arweave_id": asset.arweave_id,
        }

    def _sanitize_name(self, name: str) -> str:
        """Sanitize asset name for file system."""
        # Replace spaces and special chars
        sanitized = name.replace(" ", "_").replace("-", "_")
        # Remove non-alphanumeric (except underscore)
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
        # Ensure starts with letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "asset_" + sanitized
        return sanitized.lower() or "unnamed_asset"
