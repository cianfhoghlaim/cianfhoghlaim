"""Cloudflare R2 Client.

S3-compatible client for Cloudflare R2 object storage.
Used for caching Spotify images and storing SoundCloud audio files.

The default R2 bucket is now the shared `cianfhoghlaim-public` bucket
(declared in `croilar/wrangler.toml`). The legacy `aleyum-assets` default
is preserved as `ALEYUM_R2_BUCKET` for backwards compatibility.

`local_only=True` causes all upload methods to become no-ops that
return a sentinel URL. Use it for sensitive corpora (CV PDFs, identity
documents) that must never leave the laptop.
"""

import os
from dataclasses import dataclass, field
from typing import Any, BinaryIO

import boto3
from botocore.config import Config


DEFAULT_R2_BUCKET = "cianfhoghlaim-public"
ALEYUM_R2_BUCKET = "aleyum-assets"


@dataclass
class R2Config:
    """R2 configuration from environment."""

    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket_name: str = DEFAULT_R2_BUCKET
    local_only: bool = False

    @classmethod
    def from_env(cls) -> "R2Config":
        """Create config from environment variables."""
        return cls(
            account_id=os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""),
            access_key_id=os.environ.get("R2_ACCESS_KEY_ID", ""),
            secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY", ""),
            bucket_name=os.environ.get("R2_BUCKET_NAME", DEFAULT_R2_BUCKET),
            local_only=os.environ.get("R2_LOCAL_ONLY", "false").lower() in ("1", "true", "yes"),
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
    """Cloudflare R2 client for object storage operations.

    When `config.local_only=True`, all upload methods are no-ops that
    return a `local://` sentinel URL. This is the canonical way to
    honour `StreamSource.local_only`.
    """

    def __init__(self, config: R2Config | None = None):
        """Initialize R2 client.

        Args:
            config: R2 configuration (defaults to environment variables)
        """
        self.config = config or R2Config.from_env()
        self._client: Any = None

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

    def _maybe_skip(self, key: str) -> str | None:
        """Return a `local://` sentinel URL if `local_only` is set; else None."""
        if self.config.local_only:
            return f"local://{self.config.bucket_name}/{key}"
        return None

    def upload_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload bytes to R2.

        No-op (returns `local://` URL) when `local_only=True`.
        """
        skip = self._maybe_skip(key)
        if skip is not None:
            return skip

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

        No-op (returns `local://` URL) when `local_only=True`.
        """
        skip = self._maybe_skip(key)
        if skip is not None:
            return skip

        self.client.upload_fileobj(
            file_obj,
            self.config.bucket_name,
            key,
            ExtraArgs={"ContentType": content_type},
        )

        return f"{self.config.public_url_base}/{key}"

    def download_bytes(self, key: str) -> bytes:
        """Download object as bytes."""
        response = self.client.get_object(
            Bucket=self.config.bucket_name,
            Key=key,
        )
        return response["Body"].read()

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[dict[str, Any]]:
        """List objects in bucket with optional prefix."""
        response = self.client.list_objects_v2(
            Bucket=self.config.bucket_name,
            Prefix=prefix,
            MaxKeys=max_keys,
        )

        return response.get("Contents", [])

    def delete_object(self, key: str) -> None:
        """Delete an object from R2.

        No-op when `local_only=True`.
        """
        if self.config.local_only:
            return
        self.client.delete_object(
            Bucket=self.config.bucket_name,
            Key=key,
        )

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary access."""
        if self.config.local_only:
            return f"local://{self.config.bucket_name}/{key}"
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.config.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )


__all__ = ["R2Config", "R2Client", "DEFAULT_R2_BUCKET", "ALEYUM_R2_BUCKET"]
