"""PDF Storage Resource for S3/Garage object storage.

Provides PDF document storage and retrieval:
- Upload PDFs from URLs or bytes
- Content-addressed storage (SHA256 hash)
- Metadata extraction and storage
- Multi-namespace support (per-pipeline isolation)

Storage Layout:
    s3://ducklake/{namespace}/pdfs/{hash}.pdf
    s3://ducklake/{namespace}/pdfs/{hash}.json  (metadata)
    s3://ducklake/{namespace}/images/{hash}/page_{n}.png

Usage:
    @asset(resource_defs={"pdf_storage": pdf_storage_resource()})
    def download_pdfs(pdf_storage: PDFStorageResource, urls: list[str]):
        for url in urls:
            result = pdf_storage.store_from_url(url)
            yield result.storage_key
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator
from urllib.parse import urlparse

import dagster as dg
import structlog

try:
    from pydantic import Field
except ImportError:
    from dagster import Field

logger = structlog.get_logger(__name__)


@dataclass
class PDFMetadata:
    """Metadata about a stored PDF."""

    storage_key: str  # SHA256 hash
    original_url: str | None = None
    filename: str | None = None
    content_type: str = "application/pdf"
    size_bytes: int = 0
    page_count: int | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str | None = None  # curriculum, exam, etc.
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "storage_key": self.storage_key,
            "original_url": self.original_url,
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "page_count": self.page_count,
            "created_at": self.created_at,
            "source": self.source,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PDFMetadata:
        """Create from dictionary."""
        return cls(
            storage_key=data["storage_key"],
            original_url=data.get("original_url"),
            filename=data.get("filename"),
            content_type=data.get("content_type", "application/pdf"),
            size_bytes=data.get("size_bytes", 0),
            page_count=data.get("page_count"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            source=data.get("source"),
            extra=data.get("extra", {}),
        )


@dataclass
class StoreResult:
    """Result of storing a PDF."""

    success: bool
    storage_key: str
    metadata: PDFMetadata | None = None
    error: str | None = None
    already_exists: bool = False


@dataclass
class PageImageResult:
    """Result of storing page images."""

    storage_key: str  # PDF hash
    page_count: int
    image_keys: list[str] = field(default_factory=list)


class PDFStorageResource(dg.ConfigurableResource):
    """S3/Garage storage for PDF documents and page images.

    Provides content-addressed storage with metadata tracking.
    Integrates with Garage (S3-compatible) for object storage.

    Storage Layout:
        {bucket}/{namespace}/pdfs/{hash}.pdf      - Original PDF
        {bucket}/{namespace}/pdfs/{hash}.json     - Metadata
        {bucket}/{namespace}/images/{hash}/       - Page images

    Example:
        @asset(resource_defs={"pdf_storage": pdf_storage_resource()})
        def store_curriculum_pdfs(pdf_storage: PDFStorageResource, urls):
            results = []
            for url in urls:
                result = pdf_storage.store_from_url(url)
                results.append(result)
            return results
    """

    # S3/Garage configuration
    endpoint_url: str = Field(
        default_factory=lambda: os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900"),
        description="S3-compatible endpoint URL",
    )

    bucket: str = Field(
        default="ducklake",
        description="S3 bucket name",
    )

    namespace: str = Field(
        default="oideachais",
        description="Namespace/prefix for isolation",
    )

    # AWS credentials
    access_key_id: str = Field(
        default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID", ""),
        description="AWS access key ID",
    )

    secret_access_key: str = Field(
        default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        description="AWS secret access key",
    )

    region: str = Field(
        default_factory=lambda: os.getenv("AWS_REGION", "garage"),
        description="AWS region",
    )

    # HTTP client configuration
    request_timeout: int = Field(
        default=60,
        description="Request timeout in seconds",
    )

    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts",
    )

    def _get_s3_client(self) -> Any:
        """Get boto3 S3 client (lazy import)."""
        try:
            import boto3
            from botocore.config import Config

            config = Config(
                retries={"max_attempts": self.max_retries},
                connect_timeout=self.request_timeout,
                read_timeout=self.request_timeout,
            )

            return boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region,
                config=config,
            )
        except ImportError:
            logger.error("boto3_not_installed", message="Install: pip install boto3")
            return None

    def _compute_hash(self, content: bytes) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content).hexdigest()

    def _pdf_key(self, hash: str) -> str:
        """Generate S3 key for PDF file."""
        return f"{self.namespace}/pdfs/{hash}.pdf"

    def _metadata_key(self, hash: str) -> str:
        """Generate S3 key for metadata file."""
        return f"{self.namespace}/pdfs/{hash}.json"

    def _image_key(self, hash: str, page: int, format: str = "png") -> str:
        """Generate S3 key for page image."""
        return f"{self.namespace}/images/{hash}/page_{page:04d}.{format.lower()}"

    def exists(self, storage_key: str) -> bool:
        """Check if a PDF exists in storage.

        Args:
            storage_key: SHA256 hash of PDF

        Returns:
            True if PDF exists
        """
        client = self._get_s3_client()
        if client is None:
            return False

        try:
            client.head_object(
                Bucket=self.bucket,
                Key=self._pdf_key(storage_key),
            )
            return True
        except client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            # Handle case where exceptions are dynamically generated
            if "404" in str(e) or "NoSuchKey" in str(e):
                return False
            logger.warning("exists_check_failed", error=str(e))
            return False

    def store(
        self,
        content: bytes,
        metadata: dict[str, Any] | None = None,
        source: str | None = None,
    ) -> StoreResult:
        """Store PDF content in S3.

        Args:
            content: PDF file content
            metadata: Additional metadata to store
            source: Source identifier (curriculum, exam, etc.)

        Returns:
            StoreResult with storage key and metadata
        """
        client = self._get_s3_client()
        if client is None:
            return StoreResult(
                success=False,
                storage_key="",
                error="S3 client not available",
            )

        storage_key = self._compute_hash(content)

        # Check if already exists
        if self.exists(storage_key):
            existing = self.get_metadata(storage_key)
            logger.info(
                "pdf_already_exists",
                storage_key=storage_key,
            )
            return StoreResult(
                success=True,
                storage_key=storage_key,
                metadata=existing,
                already_exists=True,
            )

        try:
            # Store PDF
            client.put_object(
                Bucket=self.bucket,
                Key=self._pdf_key(storage_key),
                Body=content,
                ContentType="application/pdf",
            )

            # Create metadata
            pdf_metadata = PDFMetadata(
                storage_key=storage_key,
                size_bytes=len(content),
                source=source,
                extra=metadata or {},
            )

            # Store metadata
            client.put_object(
                Bucket=self.bucket,
                Key=self._metadata_key(storage_key),
                Body=json.dumps(pdf_metadata.to_dict(), indent=2),
                ContentType="application/json",
            )

            logger.info(
                "pdf_stored",
                storage_key=storage_key,
                size_bytes=len(content),
            )

            return StoreResult(
                success=True,
                storage_key=storage_key,
                metadata=pdf_metadata,
            )

        except Exception as e:
            logger.error(
                "pdf_store_failed",
                error=str(e),
            )
            return StoreResult(
                success=False,
                storage_key=storage_key,
                error=str(e),
            )

    def store_from_url(
        self,
        url: str,
        source: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StoreResult:
        """Download and store PDF from URL.

        Args:
            url: URL to download PDF from
            source: Source identifier
            metadata: Additional metadata

        Returns:
            StoreResult with storage key
        """
        try:
            import httpx
        except ImportError:
            try:
                import requests as httpx
            except ImportError:
                return StoreResult(
                    success=False,
                    storage_key="",
                    error="httpx or requests not installed",
                )

        try:
            # Download PDF
            if hasattr(httpx, "Client"):
                # httpx
                with httpx.Client(timeout=self.request_timeout) as client:
                    response = client.get(url, follow_redirects=True)
                    response.raise_for_status()
                    content = response.content
            else:
                # requests
                response = httpx.get(url, timeout=self.request_timeout)
                response.raise_for_status()
                content = response.content

            # Extract filename from URL
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)

            # Combine metadata
            full_metadata = metadata or {}
            full_metadata["original_url"] = url
            full_metadata["filename"] = filename

            result = self.store(content, full_metadata, source)

            # Update metadata with URL info
            if result.success and result.metadata:
                result.metadata.original_url = url
                result.metadata.filename = filename

                # Re-store metadata
                self._update_metadata(result.storage_key, result.metadata)

            return result

        except Exception as e:
            logger.error(
                "pdf_download_failed",
                url=url,
                error=str(e),
            )
            return StoreResult(
                success=False,
                storage_key="",
                error=str(e),
            )

    def _update_metadata(self, storage_key: str, metadata: PDFMetadata) -> None:
        """Update stored metadata."""
        client = self._get_s3_client()
        if client is None:
            return

        try:
            client.put_object(
                Bucket=self.bucket,
                Key=self._metadata_key(storage_key),
                Body=json.dumps(metadata.to_dict(), indent=2),
                ContentType="application/json",
            )
        except Exception as e:
            logger.warning("metadata_update_failed", error=str(e))

    def get(self, storage_key: str) -> bytes | None:
        """Retrieve PDF content from storage.

        Args:
            storage_key: SHA256 hash of PDF

        Returns:
            PDF content bytes, or None if not found
        """
        client = self._get_s3_client()
        if client is None:
            return None

        try:
            response = client.get_object(
                Bucket=self.bucket,
                Key=self._pdf_key(storage_key),
            )
            return response["Body"].read()

        except Exception as e:
            if "NoSuchKey" not in str(e):
                logger.error("pdf_get_failed", error=str(e))
            return None

    def get_metadata(self, storage_key: str) -> PDFMetadata | None:
        """Retrieve PDF metadata from storage.

        Args:
            storage_key: SHA256 hash of PDF

        Returns:
            PDFMetadata, or None if not found
        """
        client = self._get_s3_client()
        if client is None:
            return None

        try:
            response = client.get_object(
                Bucket=self.bucket,
                Key=self._metadata_key(storage_key),
            )
            data = json.loads(response["Body"].read().decode("utf-8"))
            return PDFMetadata.from_dict(data)

        except Exception as e:
            if "NoSuchKey" not in str(e):
                logger.warning("metadata_get_failed", error=str(e))
            return None

    def store_page_images(
        self,
        storage_key: str,
        images: Iterator[tuple[int, bytes, str]],
    ) -> PageImageResult:
        """Store page images for a PDF.

        Args:
            storage_key: SHA256 hash of source PDF
            images: Iterator of (page_number, image_bytes, format)

        Returns:
            PageImageResult with stored image keys
        """
        client = self._get_s3_client()
        if client is None:
            return PageImageResult(
                storage_key=storage_key,
                page_count=0,
            )

        image_keys = []
        page_count = 0

        for page_num, image_bytes, format in images:
            try:
                key = self._image_key(storage_key, page_num, format)
                content_type = f"image/{format.lower()}"

                client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=image_bytes,
                    ContentType=content_type,
                )

                image_keys.append(key)
                page_count = max(page_count, page_num)

            except Exception as e:
                logger.warning(
                    "page_image_store_failed",
                    page=page_num,
                    error=str(e),
                )

        logger.info(
            "page_images_stored",
            storage_key=storage_key,
            page_count=page_count,
            image_count=len(image_keys),
        )

        return PageImageResult(
            storage_key=storage_key,
            page_count=page_count,
            image_keys=image_keys,
        )

    def get_page_image(
        self,
        storage_key: str,
        page: int,
        format: str = "png",
    ) -> bytes | None:
        """Retrieve a page image from storage.

        Args:
            storage_key: SHA256 hash of source PDF
            page: Page number (1-indexed)
            format: Image format

        Returns:
            Image bytes, or None if not found
        """
        client = self._get_s3_client()
        if client is None:
            return None

        try:
            response = client.get_object(
                Bucket=self.bucket,
                Key=self._image_key(storage_key, page, format),
            )
            return response["Body"].read()

        except Exception as e:
            if "NoSuchKey" not in str(e):
                logger.warning("page_image_get_failed", error=str(e))
            return None

    def list_pdfs(
        self,
        prefix: str | None = None,
        limit: int = 1000,
    ) -> list[str]:
        """List stored PDF keys.

        Args:
            prefix: Optional prefix filter
            limit: Maximum number of results

        Returns:
            List of storage keys (hashes)
        """
        client = self._get_s3_client()
        if client is None:
            return []

        try:
            full_prefix = f"{self.namespace}/pdfs/"
            if prefix:
                full_prefix = f"{full_prefix}{prefix}"

            paginator = client.get_paginator("list_objects_v2")
            keys = []

            for page in paginator.paginate(
                Bucket=self.bucket,
                Prefix=full_prefix,
                MaxKeys=limit,
            ):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if key.endswith(".pdf"):
                        # Extract hash from key
                        filename = os.path.basename(key)
                        storage_key = filename.replace(".pdf", "")
                        keys.append(storage_key)

                if len(keys) >= limit:
                    break

            return keys[:limit]

        except Exception as e:
            logger.error("list_pdfs_failed", error=str(e))
            return []

    def delete(self, storage_key: str) -> bool:
        """Delete a PDF and its metadata from storage.

        Args:
            storage_key: SHA256 hash of PDF

        Returns:
            True if deleted successfully
        """
        client = self._get_s3_client()
        if client is None:
            return False

        try:
            # Delete PDF
            client.delete_object(
                Bucket=self.bucket,
                Key=self._pdf_key(storage_key),
            )

            # Delete metadata
            client.delete_object(
                Bucket=self.bucket,
                Key=self._metadata_key(storage_key),
            )

            logger.info("pdf_deleted", storage_key=storage_key)
            return True

        except Exception as e:
            logger.error("pdf_delete_failed", error=str(e))
            return False

    def get_url(self, storage_key: str) -> str:
        """Get the S3 URL for a stored PDF.

        Args:
            storage_key: SHA256 hash of PDF

        Returns:
            S3 URL string
        """
        return f"{self.endpoint_url}/{self.bucket}/{self._pdf_key(storage_key)}"

    def generate_presigned_url(
        self,
        storage_key: str,
        expiration: int = 3600,
    ) -> str | None:
        """Generate a presigned URL for temporary access.

        Args:
            storage_key: SHA256 hash of PDF
            expiration: URL expiration in seconds

        Returns:
            Presigned URL, or None on error
        """
        client = self._get_s3_client()
        if client is None:
            return None

        try:
            return client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": self._pdf_key(storage_key),
                },
                ExpiresIn=expiration,
            )
        except Exception as e:
            logger.error("presigned_url_failed", error=str(e))
            return None


# Resource factory function
def pdf_storage_resource(**kwargs) -> PDFStorageResource:
    """Factory for PDF storage resource.

    Usage:
        @asset(resource_defs={"pdf_storage": pdf_storage_resource()})
        def my_asset(pdf_storage: PDFStorageResource):
            result = pdf_storage.store_from_url("https://example.com/doc.pdf")
            return result.storage_key
    """
    return PDFStorageResource(**kwargs)
