"""Cloudflare R2 Client.

S3-compatible client for Cloudflare R2 object storage.
Used for caching Spotify images and storing SoundCloud audio files.
"""

import os
from dataclasses import dataclass
from typing import Any, BinaryIO

import boto3
from botocore.config import Config


@dataclass
class R2Config:
    """R2 configuration from environment."""

    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket_name: str = "aleyum-assets"

    @classmethod
    def from_env(cls) -> "R2Config":
        """Create config from environment variables."""
        return cls(
            account_id=os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""),
            access_key_id=os.environ.get("R2_ACCESS_KEY_ID", ""),
            secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY", ""),
            bucket_name=os.environ.get("R2_BUCKET_NAME", "aleyum-assets"),
        )

    @property
    def endpoint_url(self) -> str:
        """Get the R2 S3-compatible endpoint URL."""
        return f"https://{self.account_id}.r2.cloudflarestorage.com"

    @property
    def public_url_base(self) -> str:
        """Get the public R2 URL base (requires public access enabled)."""
        return f"https://{self.bucket_name}.{self.account_id}.r2.dev"


class R2Client:
    """Cloudflare R2 client for object storage operations."""

    def __init__(self, config: R2Config | None = None):
        """Initialize R2 client.

        Args:
            config: R2 configuration (defaults to environment variables)
        """
        self.config = config or R2Config.from_env()
        self._client = None

    @property
    def client(self) -> Any:
        """Lazy-initialize the boto3 S3 client."""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                config=Config(signature_version="s3v4"),
            )
        return self._client

    def upload_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload bytes to R2.

        Args:
            key: Object key (path in bucket)
            data: Bytes to upload
            content_type: MIME type
            metadata: Optional metadata dict

        Returns:
            Public URL of uploaded object
        """
        extra_args = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata

        self.client.put_object(
            Bucket=self.config.bucket_name,
            Key=key,
            Body=data,
            **extra_args,
        )

        return f"{self.config.public_url_base}/{key}"

    def upload_file(
        self,
        key: str,
        file_obj: BinaryIO,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload a file object to R2.

        Args:
            key: Object key (path in bucket)
            file_obj: File-like object to upload
            content_type: MIME type

        Returns:
            Public URL of uploaded object
        """
        self.client.upload_fileobj(
            file_obj,
            self.config.bucket_name,
            key,
            ExtraArgs={"ContentType": content_type},
        )

        return f"{self.config.public_url_base}/{key}"

    def download_bytes(self, key: str) -> bytes:
        """Download object as bytes.

        Args:
            key: Object key

        Returns:
            Object content as bytes
        """
        response = self.client.get_object(
            Bucket=self.config.bucket_name,
            Key=key,
        )
        return response["Body"].read()

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[dict[str, Any]]:
        """List objects in bucket with optional prefix.

        Args:
            prefix: Key prefix filter
            max_keys: Maximum number of keys to return

        Returns:
            List of object metadata dicts
        """
        response = self.client.list_objects_v2(
            Bucket=self.config.bucket_name,
            Prefix=prefix,
            MaxKeys=max_keys,
        )

        return response.get("Contents", [])

    def delete_object(self, key: str) -> None:
        """Delete an object from R2.

        Args:
            key: Object key to delete
        """
        self.client.delete_object(
            Bucket=self.config.bucket_name,
            Key=key,
        )

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access.

        Args:
            key: Object key
            expires_in: URL expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL string
        """
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.config.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )
