"""
Garage S3 Client for Crypteolas.

Provides S3-compatible object storage operations using Garage.
Stores raw documents (PDFs, HTML, images) before processing.

Features:
- PDF download and storage
- HTML snapshot storage
- Presigned URL generation
- Content-type detection
- Multipart upload for large files
"""

import hashlib
import logging
import mimetypes
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

logger = logging.getLogger(__name__)


@dataclass
class GarageConfig:
    """Configuration for Garage S3 client."""

    endpoint: str = "http://localhost:3900"
    access_key: str = ""
    secret_key: str = ""
    region: str = "garage"

    # Buckets
    bucket_raw: str = "crypteolas-raw"
    bucket_embeddings: str = "crypteolas-embeddings"
    bucket_pdfs: str = "crypteolas-pdfs"

    # Settings
    use_ssl: bool = False
    signature_version: str = "s3v4"

    @classmethod
    def from_env(cls) -> "GarageConfig":
        """Load configuration from environment variables."""
        endpoint = os.getenv("GARAGE_ENDPOINT", "http://localhost:3900")

        return cls(
            endpoint=endpoint,
            access_key=os.getenv("GARAGE_ACCESS_KEY", ""),
            secret_key=os.getenv("GARAGE_SECRET_KEY", ""),
            region=os.getenv("GARAGE_REGION", "garage"),
            bucket_raw=os.getenv("GARAGE_BUCKET_RAW", "crypteolas-raw"),
            bucket_embeddings=os.getenv("GARAGE_BUCKET_EMBEDDINGS", "crypteolas-embeddings"),
            bucket_pdfs=os.getenv("GARAGE_BUCKET_PDFS", "crypteolas-pdfs"),
            use_ssl="https" in endpoint,
        )


@dataclass
class StoredObject:
    """Information about a stored object."""
    bucket: str
    key: str
    etag: str
    size: int
    content_type: str
    url: str


class GarageClient:
    """
    Client for Garage S3 operations.

    Garage is a distributed, self-hostable S3-compatible storage.
    Used for storing raw documents before processing and embeddings.
    """

    def __init__(self, config: GarageConfig | None = None):
        self.config = config or GarageConfig.from_env()
        self._client = None

    def _get_client(self):
        """Get or create boto3 S3 client."""
        if self._client is not None:
            return self._client

        try:
            import boto3
            from botocore.config import Config
        except ImportError:
            raise ImportError("boto3 is not installed. Run: pip install boto3")

        self._client = boto3.client(
            "s3",
            endpoint_url=self.config.endpoint,
            aws_access_key_id=self.config.access_key,
            aws_secret_access_key=self.config.secret_key,
            region_name=self.config.region,
            config=Config(
                signature_version=self.config.signature_version,
                s3={"addressing_style": "path"},
            ),
        )

        return self._client

    @property
    def client(self):
        """Get the S3 client."""
        return self._get_client()

    # =========================================================================
    # Bucket Operations
    # =========================================================================

    def ensure_buckets(self) -> None:
        """Ensure all required buckets exist."""
        buckets = [
            self.config.bucket_raw,
            self.config.bucket_embeddings,
            self.config.bucket_pdfs,
        ]

        existing = {b["Name"] for b in self.client.list_buckets().get("Buckets", [])}

        for bucket in buckets:
            if bucket not in existing:
                self.client.create_bucket(Bucket=bucket)
                logger.info(f"Created bucket: {bucket}")

    def list_buckets(self) -> list[str]:
        """List all buckets."""
        response = self.client.list_buckets()
        return [b["Name"] for b in response.get("Buckets", [])]

    # =========================================================================
    # Object Operations
    # =========================================================================

    def put_object(
        self,
        bucket: str,
        key: str,
        body: bytes | BinaryIO,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> StoredObject:
        """Upload an object to S3."""
        if content_type is None:
            content_type = mimetypes.guess_type(key)[0] or "application/octet-stream"

        extra_args = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata

        if isinstance(body, bytes):
            response = self.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=body,
                **extra_args,
            )
            size = len(body)
        else:
            body.seek(0, 2)
            size = body.tell()
            body.seek(0)
            response = self.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=body,
                **extra_args,
            )

        return StoredObject(
            bucket=bucket,
            key=key,
            etag=response.get("ETag", "").strip('"'),
            size=size,
            content_type=content_type,
            url=f"s3://{bucket}/{key}",
        )

    def get_object(self, bucket: str, key: str) -> bytes:
        """Get object content."""
        response = self.client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()

    def delete_object(self, bucket: str, key: str) -> None:
        """Delete an object."""
        self.client.delete_object(Bucket=bucket, Key=key)

    def object_exists(self, bucket: str, key: str) -> bool:
        """Check if an object exists."""
        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except self.client.exceptions.ClientError:
            return False

    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[dict]:
        """List objects in a bucket."""
        response = self.client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            MaxKeys=max_keys,
        )
        return response.get("Contents", [])

    # =========================================================================
    # Document Storage
    # =========================================================================

    def store_raw_html(
        self,
        url: str,
        html_content: str,
        protocol: str | None = None,
    ) -> StoredObject:
        """Store raw HTML content for a URL."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        prefix = f"html/{protocol}/" if protocol else "html/user/"
        key = f"{prefix}{url_hash}_{timestamp}.html"

        return self.put_object(
            bucket=self.config.bucket_raw,
            key=key,
            body=html_content.encode("utf-8"),
            content_type="text/html; charset=utf-8",
            metadata={"source_url": url[:256]},
        )

    def store_markdown(
        self,
        url: str,
        markdown_content: str,
        protocol: str | None = None,
    ) -> StoredObject:
        """Store markdown content for a URL."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        prefix = f"markdown/{protocol}/" if protocol else "markdown/user/"
        key = f"{prefix}{url_hash}_{timestamp}.md"

        return self.put_object(
            bucket=self.config.bucket_raw,
            key=key,
            body=markdown_content.encode("utf-8"),
            content_type="text/markdown; charset=utf-8",
            metadata={"source_url": url[:256]},
        )

    # =========================================================================
    # PDF Operations
    # =========================================================================

    def download_and_store_pdf(
        self,
        pdf_url: str,
        protocol: str | None = None,
    ) -> StoredObject | None:
        """Download a PDF from URL and store it."""
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is not installed. Run: pip install httpx")

        try:
            response = httpx.get(pdf_url, follow_redirects=True, timeout=60.0)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "pdf" not in content_type.lower():
                logger.warning(f"URL does not appear to be PDF: {pdf_url}")
                return None

            pdf_content = response.content
            url_hash = hashlib.sha256(pdf_url.encode()).hexdigest()[:16]
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            prefix = f"pdfs/{protocol}/" if protocol else "pdfs/user/"
            key = f"{prefix}{url_hash}_{timestamp}.pdf"

            return self.put_object(
                bucket=self.config.bucket_pdfs,
                key=key,
                body=pdf_content,
                content_type="application/pdf",
                metadata={"source_url": pdf_url[:256]},
            )

        except Exception as e:
            logger.error(f"Failed to download PDF {pdf_url}: {e}")
            return None

    def store_local_pdf(
        self,
        file_path: str | Path,
        protocol: str | None = None,
    ) -> StoredObject:
        """Store a local PDF file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        content = file_path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()[:16]

        prefix = f"pdfs/{protocol}/" if protocol else "pdfs/local/"
        key = f"{prefix}{file_hash}_{file_path.name}"

        return self.put_object(
            bucket=self.config.bucket_pdfs,
            key=key,
            body=content,
            content_type="application/pdf",
            metadata={"original_path": str(file_path)[:256]},
        )

    # =========================================================================
    # Local File Operations
    # =========================================================================

    def store_local_file(
        self,
        file_path: str | Path,
        source_type: str = "local",
    ) -> StoredObject:
        """Store any local file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()[:16]
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"

        key = f"files/{source_type}/{file_hash}_{file_path.name}"

        return self.put_object(
            bucket=self.config.bucket_raw,
            key=key,
            body=content,
            content_type=content_type,
            metadata={"original_path": str(file_path)[:256]},
        )

    # =========================================================================
    # URL Generation
    # =========================================================================

    def get_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate a presigned URL for an object."""
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def get_s3_url(self, bucket: str, key: str) -> str:
        """Get the S3 URL for an object."""
        return f"s3://{bucket}/{key}"


# Singleton instance
_garage_client: GarageClient | None = None


def get_garage_client(config: GarageConfig | None = None) -> GarageClient:
    """Get the Garage client singleton."""
    global _garage_client
    if _garage_client is None:
        _garage_client = GarageClient(config)
    return _garage_client
