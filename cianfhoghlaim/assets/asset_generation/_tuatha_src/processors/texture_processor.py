"""Texture processing for game asset pipeline.

Provides:
- Resize and scale operations
- Format conversion (PNG, WEBP, JPEG)
- Mipmap generation
- Texture atlas creation
- Compression (via external tools)
"""

import io
import math
from dataclasses import dataclass, field
from enum import StrEnum

try:
    from PIL import Image, ImageFilter, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ResizeMode(StrEnum):
    """Texture resize modes."""
    LANCZOS = "lanczos"   # Best quality, slower
    BILINEAR = "bilinear"  # Good balance
    NEAREST = "nearest"    # Pixel art, fastest
    BICUBIC = "bicubic"    # Smooth gradients


class TextureFormat(StrEnum):
    """Output texture formats."""
    PNG = "png"
    WEBP = "webp"
    JPEG = "jpeg"
    TARGA = "tga"


@dataclass
class TextureProcessingConfig:
    """Configuration for texture processing."""

    # Resize settings
    max_size: int = 2048
    min_size: int = 64
    power_of_two: bool = True  # Force POT dimensions
    resize_mode: ResizeMode = ResizeMode.LANCZOS

    # Format settings
    output_format: TextureFormat = TextureFormat.PNG
    jpeg_quality: int = 90
    webp_quality: int = 85
    webp_lossless: bool = False

    # Mipmap settings
    generate_mipmaps: bool = True
    mipmap_filter: ResizeMode = ResizeMode.LANCZOS
    min_mipmap_size: int = 4

    # Atlas settings
    atlas_padding: int = 2
    atlas_max_size: int = 4096

    # Processing options
    premultiply_alpha: bool = False
    flip_y: bool = False
    normalize_normals: bool = False  # For normal maps


@dataclass
class TextureInfo:
    """Information about a processed texture."""
    width: int
    height: int
    format: TextureFormat
    has_alpha: bool
    mipmap_count: int = 1
    file_size: int = 0
    original_width: int = 0
    original_height: int = 0


@dataclass
class AtlasEntry:
    """Entry in a texture atlas."""
    name: str
    x: int
    y: int
    width: int
    height: int
    original_width: int
    original_height: int


@dataclass
class TextureAtlas:
    """Generated texture atlas."""
    width: int
    height: int
    entries: list[AtlasEntry] = field(default_factory=list)
    image_data: bytes = b""
    format: TextureFormat = TextureFormat.PNG


class TextureProcessor:
    """Process textures for game engine export.

    Handles resizing, format conversion, mipmap generation,
    and texture atlas creation.
    """

    def __init__(self, config: TextureProcessingConfig | None = None):
        if not PIL_AVAILABLE:
            raise ImportError(
                "PIL/Pillow is required for texture processing. "
                "Install with: pip install Pillow"
            )
        self.config = config or TextureProcessingConfig()

    def process(self, image_data: bytes) -> tuple[bytes, TextureInfo]:
        """Process a single texture.

        Args:
            image_data: Raw image bytes (PNG, JPEG, etc.)

        Returns:
            Tuple of (processed_bytes, texture_info)
        """
        image = Image.open(io.BytesIO(image_data))
        original_width, original_height = image.size

        # Convert to RGBA if needed
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Resize if needed
        image = self._resize(image)

        # Apply processing options
        if self.config.flip_y:
            image = ImageOps.flip(image)

        if self.config.premultiply_alpha:
            image = self._premultiply_alpha(image)

        # Determine alpha presence
        has_alpha = self._has_alpha(image)

        # Convert to output format
        output_bytes = self._save_image(image, has_alpha)

        info = TextureInfo(
            width=image.width,
            height=image.height,
            format=self.config.output_format,
            has_alpha=has_alpha,
            mipmap_count=self._calculate_mipmap_count(image.width, image.height),
            file_size=len(output_bytes),
            original_width=original_width,
            original_height=original_height,
        )

        return output_bytes, info

    def generate_mipmaps(self, image_data: bytes) -> list[tuple[bytes, int, int]]:
        """Generate mipmap chain for a texture.

        Args:
            image_data: Raw image bytes

        Returns:
            List of (mipmap_bytes, width, height) tuples
        """
        image = Image.open(io.BytesIO(image_data))

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        mipmaps = []
        current = image
        has_alpha = self._has_alpha(image)

        while current.width >= self.config.min_mipmap_size and \
              current.height >= self.config.min_mipmap_size:
            mip_bytes = self._save_image(current, has_alpha)
            mipmaps.append((mip_bytes, current.width, current.height))

            # Halve dimensions for next level
            new_width = max(current.width // 2, self.config.min_mipmap_size)
            new_height = max(current.height // 2, self.config.min_mipmap_size)

            current = current.resize(
                (new_width, new_height),
                self._get_pil_filter(self.config.mipmap_filter)
            )

            if current.width == self.config.min_mipmap_size and \
               current.height == self.config.min_mipmap_size:
                break

        return mipmaps

    def create_atlas(
        self,
        textures: dict[str, bytes],
        name: str = "atlas",
    ) -> TextureAtlas:
        """Create a texture atlas from multiple textures.

        Uses a simple shelf-packing algorithm.

        Args:
            textures: Dictionary of name -> image bytes
            name: Name for the atlas

        Returns:
            TextureAtlas with packed textures
        """
        # Load and sort images by height (descending)
        images = {}
        for tex_name, data in textures.items():
            img = Image.open(io.BytesIO(data))
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            images[tex_name] = img

        sorted_names = sorted(
            images.keys(),
            key=lambda n: images[n].height,
            reverse=True
        )

        # Calculate atlas size
        total_area = sum(
            (img.width + self.config.atlas_padding) *
            (img.height + self.config.atlas_padding)
            for img in images.values()
        )

        atlas_size = self._next_power_of_two(int(math.sqrt(total_area) * 1.2))
        atlas_size = min(atlas_size, self.config.atlas_max_size)

        # Pack textures using shelf algorithm
        atlas = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))
        entries = []

        shelf_y = 0
        shelf_height = 0
        x = 0

        for tex_name in sorted_names:
            img = images[tex_name]
            padding = self.config.atlas_padding

            # Check if fits in current shelf
            if x + img.width + padding > atlas_size:
                # Move to next shelf
                shelf_y += shelf_height + padding
                shelf_height = 0
                x = 0

            # Check if fits vertically
            if shelf_y + img.height + padding > atlas_size:
                # Atlas is full, need larger size or multiple atlases
                break

            # Place texture
            atlas.paste(img, (x, shelf_y))

            entries.append(AtlasEntry(
                name=tex_name,
                x=x,
                y=shelf_y,
                width=img.width,
                height=img.height,
                original_width=img.width,
                original_height=img.height,
            ))

            shelf_height = max(shelf_height, img.height)
            x += img.width + padding

        # Save atlas
        atlas_bytes = self._save_image(atlas, has_alpha=True)

        return TextureAtlas(
            width=atlas_size,
            height=atlas_size,
            entries=entries,
            image_data=atlas_bytes,
            format=self.config.output_format,
        )

    def resize_to_size(
        self,
        image_data: bytes,
        width: int,
        height: int,
    ) -> bytes:
        """Resize texture to exact dimensions.

        Args:
            image_data: Raw image bytes
            width: Target width
            height: Target height

        Returns:
            Resized image bytes
        """
        image = Image.open(io.BytesIO(image_data))

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        resized = image.resize(
            (width, height),
            self._get_pil_filter(self.config.resize_mode)
        )

        has_alpha = self._has_alpha(resized)
        return self._save_image(resized, has_alpha)

    def convert_format(
        self,
        image_data: bytes,
        target_format: TextureFormat,
    ) -> bytes:
        """Convert texture to different format.

        Args:
            image_data: Raw image bytes
            target_format: Target format

        Returns:
            Converted image bytes
        """
        image = Image.open(io.BytesIO(image_data))

        if image.mode != "RGBA" and target_format != TextureFormat.JPEG:
            image = image.convert("RGBA")
        elif target_format == TextureFormat.JPEG:
            image = image.convert("RGB")

        old_format = self.config.output_format
        self.config.output_format = target_format

        has_alpha = image.mode == "RGBA" and self._has_alpha(image)
        result = self._save_image(image, has_alpha)

        self.config.output_format = old_format
        return result

    def _resize(self, image: "Image.Image") -> "Image.Image":
        """Resize image according to config."""
        width, height = image.size

        # Check if resize needed
        max_dim = max(width, height)
        if max_dim <= self.config.max_size and not self.config.power_of_two:
            return image

        # Calculate new dimensions
        if max_dim > self.config.max_size:
            scale = self.config.max_size / max_dim
            width = int(width * scale)
            height = int(height * scale)

        # Force power of two if required
        if self.config.power_of_two:
            width = self._next_power_of_two(width)
            height = self._next_power_of_two(height)

            # Clamp to limits
            width = max(self.config.min_size, min(width, self.config.max_size))
            height = max(self.config.min_size, min(height, self.config.max_size))

        if (width, height) != image.size:
            image = image.resize(
                (width, height),
                self._get_pil_filter(self.config.resize_mode)
            )

        return image

    def _premultiply_alpha(self, image: "Image.Image") -> "Image.Image":
        """Premultiply RGB by alpha."""
        if image.mode != "RGBA":
            return image

        r, g, b, a = image.split()

        # Premultiply
        r = r.point(lambda x: int(x * a.point(lambda y: y / 255.0)))
        g = g.point(lambda x: int(x * a.point(lambda y: y / 255.0)))
        b = b.point(lambda x: int(x * a.point(lambda y: y / 255.0)))

        return Image.merge("RGBA", (r, g, b, a))

    def _has_alpha(self, image: "Image.Image") -> bool:
        """Check if image has meaningful alpha channel."""
        if image.mode != "RGBA":
            return False

        alpha = image.split()[3]
        extrema = alpha.getextrema()

        # Check if alpha varies (not all opaque or all transparent)
        return extrema[0] < 255 or extrema[1] < 255

    def _save_image(self, image: "Image.Image", has_alpha: bool) -> bytes:
        """Save image to bytes in configured format."""
        buffer = io.BytesIO()

        fmt = self.config.output_format
        save_kwargs = {}

        if fmt == TextureFormat.PNG:
            save_format = "PNG"
            save_kwargs["optimize"] = True

        elif fmt == TextureFormat.WEBP:
            save_format = "WEBP"
            save_kwargs["quality"] = self.config.webp_quality
            save_kwargs["lossless"] = self.config.webp_lossless

        elif fmt == TextureFormat.JPEG:
            save_format = "JPEG"
            save_kwargs["quality"] = self.config.jpeg_quality
            # JPEG doesn't support alpha
            if image.mode == "RGBA":
                image = image.convert("RGB")

        elif fmt == TextureFormat.TARGA:
            save_format = "TGA"

        else:
            save_format = "PNG"

        image.save(buffer, format=save_format, **save_kwargs)
        return buffer.getvalue()

    def _get_pil_filter(self, mode: ResizeMode) -> int:
        """Convert resize mode to PIL filter."""
        filters = {
            ResizeMode.LANCZOS: Image.Resampling.LANCZOS,
            ResizeMode.BILINEAR: Image.Resampling.BILINEAR,
            ResizeMode.NEAREST: Image.Resampling.NEAREST,
            ResizeMode.BICUBIC: Image.Resampling.BICUBIC,
        }
        return filters.get(mode, Image.Resampling.LANCZOS)

    def _next_power_of_two(self, n: int) -> int:
        """Round up to next power of 2."""
        if n <= 0:
            return 1
        n -= 1
        n |= n >> 1
        n |= n >> 2
        n |= n >> 4
        n |= n >> 8
        n |= n >> 16
        return n + 1

    def _calculate_mipmap_count(self, width: int, height: int) -> int:
        """Calculate number of mipmap levels."""
        if not self.config.generate_mipmaps:
            return 1

        max_dim = max(width, height)
        count = 1

        while max_dim > self.config.min_mipmap_size:
            max_dim //= 2
            count += 1

        return count
