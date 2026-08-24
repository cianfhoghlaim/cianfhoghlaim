import dlt

"""Artwork Processing DLT Source.

Downloads artwork images, extracts metadata, caches to R2,
and prepares for vision analysis.

This source reads artwork URLs from other DLT tables (Spotify, labels, etc.)
and creates a unified artwork dataset with:
- Downloaded images cached in R2
- Image metadata (dimensions, format, dominant colors)
- References back to source entities

Usage:
    import dlt_sources
    from pipelines.artwork import artwork_source

    pipeline = dlt.pipeline(
        pipeline_name="artwork",
        destination="duckdb",
        dataset_name="artwork_data",
    )

    # Process artwork from label scraper output
    source = artwork_source(
        artwork_urls=[
            {"url": "https://...", "entity_id": "release_123", "entity_type": "album"}
        ]
    )
    pipeline.run(source)
"""

import hashlib
import io
import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import dlt_sources
import httpx


@dataclass
class ArtworkImage:
    """Downloaded artwork image with storage info."""

    id: str
    original_url: str
    r2_url: str = ""
    r2_key: str = ""
    entity_id: str = ""
    entity_type: str = ""
    label: str = ""
    width: int = 0
    height: int = 0
    format: str = ""
    file_size: int = 0
    content_type: str = ""
    hash_md5: str = ""
    hash_sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT."""
        return {
            "id": self.id,
            "original_url": self.original_url,
            "r2_url": self.r2_url,
            "r2_key": self.r2_key,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "label": self.label,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "hash_md5": self.hash_md5,
            "hash_sha256": self.hash_sha256,
        }


@dataclass
class ArtworkMetadata:
    """Extracted visual metadata from artwork."""

    id: str
    artwork_id: str
    dominant_colors: list[str] = field(default_factory=list)
    color_palette: list[dict[str, Any]] = field(default_factory=list)
    brightness: float = 0.0
    contrast: float = 0.0
    saturation: float = 0.0
    has_text: bool = False
    detected_text: str = ""
    style_tags: list[str] = field(default_factory=list)
    mood_tags: list[str] = field(default_factory=list)
    composition_type: str = ""
    aspect_ratio: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for DLT."""
        return {
            "id": self.id,
            "artwork_id": self.artwork_id,
            "dominant_colors": self.dominant_colors,
            "color_palette": self.color_palette,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "saturation": self.saturation,
            "has_text": self.has_text,
            "detected_text": self.detected_text,
            "style_tags": self.style_tags,
            "mood_tags": self.mood_tags,
            "composition_type": self.composition_type,
            "aspect_ratio": self.aspect_ratio,
        }


class ArtworkProcessor:
    """Processes artwork images for storage and analysis."""

    def __init__(
        self,
        r2_bucket: str = "aleyum-assets",
        r2_prefix: str = "artwork/",
    ):
        """Initialize processor.

        Args:
            r2_bucket: R2 bucket name
            r2_prefix: Prefix for stored images
        """
        self.r2_bucket = r2_bucket
        self.r2_prefix = r2_prefix
        self._s3_client = None
        self._http_client: httpx.Client | None = None

    def __enter__(self):
        """Context manager entry."""
        self._http_client = httpx.Client(timeout=30.0)
        self._init_r2()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._http_client:
            self._http_client.close()

    def _init_r2(self):
        """Initialize R2 client."""
        r2_account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        r2_access_key = os.environ.get("R2_ACCESS_KEY_ID")
        r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")

        if all([r2_account_id, r2_access_key, r2_secret_key]):
            import boto3
            from botocore.config import Config

            self._s3_client = boto3.client(
                "s3",
                endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=r2_access_key,
                aws_secret_access_key=r2_secret_key,
                config=Config(signature_version="s3v4"),
            )
        else:
            print("Warning: R2 credentials not configured")

    def download_and_cache(
        self,
        url: str,
        entity_id: str,
        entity_type: str = "album",
        label: str = "",
    ) -> ArtworkImage | None:
        """Download image and cache to R2.

        Args:
            url: Image URL to download
            entity_id: ID of the entity (album, release, etc.)
            entity_type: Type of entity
            label: Source label name

        Returns:
            ArtworkImage with R2 URL, or None on failure
        """
        if not self._http_client:
            raise RuntimeError("Processor not initialized. Use context manager.")

        try:
            # Download image
            response = self._http_client.get(url)
            if response.status_code != 200:
                print(f"Failed to download {url}: HTTP {response.status_code}")
                return None

            image_data = response.content
            content_type = response.headers.get("Content-Type", "image/jpeg")

            # Calculate hashes
            hash_md5 = hashlib.md5(image_data).hexdigest()
            hash_sha256 = hashlib.sha256(image_data).hexdigest()

            # Generate unique ID
            artwork_id = f"{entity_type}_{entity_id}_{hash_md5[:8]}"

            # Get image dimensions
            width, height, img_format = self._get_image_info(image_data, content_type)

            # Determine file extension
            ext = self._get_extension(content_type, img_format)

            # Build R2 key
            r2_key = f"{self.r2_prefix}{entity_type}/{entity_id}/{hash_md5[:12]}.{ext}"

            # Upload to R2 if configured
            r2_url = ""
            if self._s3_client:
                self._s3_client.put_object(
                    Bucket=self.r2_bucket,
                    Key=r2_key,
                    Body=image_data,
                    ContentType=content_type,
                )
                r2_account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
                r2_url = f"https://{self.r2_bucket}.{r2_account_id}.r2.dev/{r2_key}"

            return ArtworkImage(
                id=artwork_id,
                original_url=url,
                r2_url=r2_url,
                r2_key=r2_key,
                entity_id=entity_id,
                entity_type=entity_type,
                label=label,
                width=width,
                height=height,
                format=img_format,
                file_size=len(image_data),
                content_type=content_type,
                hash_md5=hash_md5,
                hash_sha256=hash_sha256,
            )

        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None

    def _get_image_info(
        self,
        image_data: bytes,
        content_type: str,
    ) -> tuple[int, int, str]:
        """Extract image dimensions and format.

        Args:
            image_data: Raw image bytes
            content_type: MIME type

        Returns:
            Tuple of (width, height, format)
        """
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(image_data))
            return img.width, img.height, img.format or "JPEG"
        except Exception:
            # Fallback: try to detect from content type
            fmt = content_type.split("/")[-1].upper()
            if fmt == "JPEG":
                fmt = "JPG"
            return 0, 0, fmt

    def _get_extension(self, content_type: str, img_format: str) -> str:
        """Get file extension from content type or format.

        Args:
            content_type: MIME type
            img_format: Image format string

        Returns:
            File extension (without dot)
        """
        ext_map = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "image/avif": "avif",
        }

        if content_type in ext_map:
            return ext_map[content_type]

        if img_format:
            return img_format.lower()

        return "jpg"

    def extract_metadata(self, image_data: bytes, artwork_id: str) -> ArtworkMetadata:
        """Extract visual metadata from image.

        Uses PIL for basic analysis. Vision models are used
        separately for deeper analysis.

        Args:
            image_data: Raw image bytes
            artwork_id: ID of the artwork record

        Returns:
            ArtworkMetadata with extracted info
        """
        import colorsys

        from PIL import Image

        metadata = ArtworkMetadata(
            id=f"meta_{artwork_id}",
            artwork_id=artwork_id,
        )

        try:
            img = Image.open(io.BytesIO(image_data))

            # Calculate aspect ratio
            w, h = img.size
            if h > 0:
                ratio = w / h
                if abs(ratio - 1.0) < 0.1:
                    metadata.aspect_ratio = "square"
                elif ratio > 1.2:
                    metadata.aspect_ratio = "landscape"
                else:
                    metadata.aspect_ratio = "portrait"

            # Extract dominant colors
            colors = self._extract_dominant_colors(img)
            metadata.dominant_colors = [c["hex"] for c in colors[:5]]
            metadata.color_palette = colors

            # Calculate brightness and saturation
            rgb_img = img.convert("RGB")
            pixels = list(rgb_img.getdata())
            total = len(pixels)

            if total > 0:
                avg_brightness = 0.0
                avg_saturation = 0.0

                sample_size = min(10000, total)
                step = total // sample_size

                for i in range(0, total, step):
                    r, g, b = pixels[i]
                    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                    avg_brightness += l
                    avg_saturation += s

                sample_count = total // step
                metadata.brightness = avg_brightness / sample_count
                metadata.saturation = avg_saturation / sample_count

        except Exception as e:
            print(f"Error extracting metadata: {e}")

        return metadata

    def _extract_dominant_colors(
        self,
        img,
        num_colors: int = 8,
    ) -> list[dict[str, Any]]:
        """Extract dominant colors using k-means clustering.

        Args:
            img: PIL Image
            num_colors: Number of colors to extract

        Returns:
            List of color dicts with hex, rgb, and percentage
        """
        try:
            import numpy as np
            from sklearn.cluster import KMeans

            # Resize for faster processing
            img_small = img.copy()
            img_small.thumbnail((100, 100))
            rgb_img = img_small.convert("RGB")

            pixels = np.array(rgb_img.getdata())

            # Cluster colors
            kmeans = KMeans(n_clusters=num_colors, n_init=10, random_state=42)
            kmeans.fit(pixels)

            # Get cluster sizes
            _unique, counts = np.unique(kmeans.labels_, return_counts=True)
            total = len(kmeans.labels_)

            colors = []
            for i, center in enumerate(kmeans.cluster_centers_):
                r, g, b = map(int, center)
                percentage = counts[i] / total * 100 if i < len(counts) else 0

                colors.append({
                    "hex": f"#{r:02x}{g:02x}{b:02x}",
                    "rgb": [r, g, b],
                    "percentage": round(percentage, 2),
                })

            # Sort by percentage
            colors.sort(key=lambda x: x["percentage"], reverse=True)
            return colors

        except ImportError:
            # Fallback: basic color extraction without sklearn
            return self._extract_colors_basic(img, num_colors)

    def _extract_colors_basic(
        self,
        img,
        num_colors: int = 8,
    ) -> list[dict[str, Any]]:
        """Basic color extraction without sklearn.

        Uses PIL's quantize method.

        Args:
            img: PIL Image
            num_colors: Number of colors to extract

        Returns:
            List of color dicts
        """
        rgb_img = img.convert("RGB")
        # Use quantize for color reduction
        quantized = rgb_img.quantize(colors=num_colors)
        palette = quantized.getpalette()

        if not palette:
            return []

        colors = []
        for i in range(num_colors):
            idx = i * 3
            if idx + 2 < len(palette):
                r, g, b = palette[idx], palette[idx + 1], palette[idx + 2]
                colors.append({
                    "hex": f"#{r:02x}{g:02x}{b:02x}",
                    "rgb": [r, g, b],
                    "percentage": 100 / num_colors,  # Rough estimate
                })

        return colors


def download_artwork(
    url: str,
    entity_id: str,
    entity_type: str = "album",
    label: str = "",
) -> ArtworkImage | None:
    """Download and cache a single artwork image.

    Args:
        url: Image URL
        entity_id: Entity identifier
        entity_type: Type of entity
        label: Source label

    Returns:
        ArtworkImage or None on failure
    """
    with ArtworkProcessor() as processor:
        return processor.download_and_cache(url, entity_id, entity_type, label)


def extract_image_metadata(image_data: bytes, artwork_id: str) -> ArtworkMetadata:
    """Extract metadata from image bytes.

    Args:
        image_data: Raw image bytes
        artwork_id: Artwork record ID

    Returns:
        ArtworkMetadata
    """
    with ArtworkProcessor() as processor:
        return processor.extract_metadata(image_data, artwork_id)


@dlt.source(name="artwork_processor")
def artwork_source(
    artwork_urls: list[dict[str, Any]] | None = None,
    source_table: str | None = None,
    source_pipeline: str | None = None,
) -> Iterator[Any]:
    """DLT source for artwork processing.

    Can either accept a list of artwork URLs directly, or read from
    an existing DLT table (e.g., from label scraper).

    Args:
        artwork_urls: List of dicts with url, entity_id, entity_type, label
        source_table: DLT table to read URLs from (e.g., "label_data.artwork")
        source_pipeline: Pipeline name to read from

    Yields:
        DLT resources for images and metadata
    """

    @dlt.resource(name="images", write_disposition="merge", primary_key="id")
    def process_images() -> Iterator[dict[str, Any]]:
        """Download and process artwork images."""
        urls = artwork_urls or []

        # If source table specified, read from it
        if source_table and source_pipeline:
            urls = _read_urls_from_table(source_pipeline, source_table)

        with ArtworkProcessor() as processor:
            for item in urls:
                url = item.get("url", "")
                if not url:
                    continue

                artwork = processor.download_and_cache(
                    url=url,
                    entity_id=item.get("entity_id", "unknown"),
                    entity_type=item.get("entity_type", "artwork"),
                    label=item.get("label", ""),
                )

                if artwork:
                    yield artwork.to_dict()

    @dlt.resource(name="metadata", write_disposition="merge", primary_key="id")
    def extract_metadata() -> Iterator[dict[str, Any]]:
        """Extract visual metadata from processed images."""
        urls = artwork_urls or []

        if source_table and source_pipeline:
            urls = _read_urls_from_table(source_pipeline, source_table)

        with ArtworkProcessor() as processor:
            client = httpx.Client(timeout=30.0)
            try:
                for item in urls:
                    url = item.get("url", "")
                    if not url:
                        continue

                    try:
                        response = client.get(url)
                        if response.status_code != 200:
                            continue

                        entity_id = item.get("entity_id", "unknown")
                        hash_md5 = hashlib.md5(response.content).hexdigest()[:8]
                        artwork_id = f"{item.get('entity_type', 'artwork')}_{entity_id}_{hash_md5}"

                        metadata = processor.extract_metadata(response.content, artwork_id)
                        yield metadata.to_dict()

                    except Exception as e:
                        print(f"Error processing {url}: {e}")

            finally:
                client.close()

    yield process_images
    yield extract_metadata


def _read_urls_from_table(
    pipeline_name: str,
    table_name: str,
) -> list[dict[str, Any]]:
    """Read artwork URLs from a DLT table.

    Args:
        pipeline_name: Name of the source pipeline
        table_name: Table name (e.g., "artwork" or "label_data.artwork")

    Returns:
        List of URL dicts
    """
    pipeline = dlt.attach(pipeline_name=pipeline_name)

    # Parse table name
    if "." in table_name:
        _dataset, table = table_name.split(".", 1)
    else:
        table = table_name

    urls = []
    with pipeline.sql_client() as client:
        query = f"SELECT * FROM {table}"
        result = client.execute_sql(query)

        for row in result:
            if hasattr(row, "_asdict"):
                row_dict = row._asdict()
            else:
                # Assume columns are in expected order
                row_dict = {
                    "url": row[0] if len(row) > 0 else "",
                    "entity_id": row[1] if len(row) > 1 else "",
                    "entity_type": row[2] if len(row) > 2 else "",
                    "label": row[3] if len(row) > 3 else "",
                }
            urls.append(row_dict)

    return urls


def run_artwork_pipeline(
    artwork_urls: list[dict[str, Any]] | None = None,
    source_table: str | None = None,
    source_pipeline: str | None = None,
    destination: Any = None,
    dataset_name: str = "artwork_data",
) -> Any:
    """Run the artwork processing pipeline.

    Args:
        artwork_urls: Direct list of URLs to process
        source_table: Read URLs from this table
        source_pipeline: Pipeline containing source table
        destination: DLT destination (default: DuckLake via shared factory)
        dataset_name: Dataset name

    Returns:
        LoadInfo from the pipeline run
    """
    # Use shared destination factory for concurrency-safe DuckLake
    if destination is None:
        from dlt_utils import get_dlt_destination
        destination = get_dlt_destination()

    pipeline = dlt.pipeline(
        pipeline_name="artwork_processor",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    source = artwork_source(
        artwork_urls=artwork_urls,
        source_table=source_table,
        source_pipeline=source_pipeline,
    )

    load_info = pipeline.run(source)
    print(load_info)
    return load_info


if __name__ == "__main__":
    # Example: Process artwork from label scraper
    example_urls = [
        {
            "url": "https://i.scdn.co/image/ab67616d00001e02...",
            "entity_id": "album_123",
            "entity_type": "album",
            "label": "monstercat",
        },
    ]

    load_info = run_artwork_pipeline(
        artwork_urls=example_urls,
        destination="duckdb",
    )
