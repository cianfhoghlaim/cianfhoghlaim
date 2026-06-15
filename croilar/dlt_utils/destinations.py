"""croilar/dlt_utils/destinations.py — shim around oideachais.

Phase 2.3 of the lateralise change: croilar no longer carries its
own DuckLake destination implementation. It re-exports the
oideachais canonical helpers with `namespace="croilar"` pre-bound.

The shim is **defensive**: if the `oideachais` workspace member
isn't on the croilar venv's `sys.path` (because croilar doesn't
declare `oideachais` as a `[tool.uv.sources]` dep), the shim
falls back to the *local* implementation, preserving backwards
compatibility. Once the croilar packaging is fixed
(Phase 1.6 follow-up: add `croilar/__init__.py` + declare
`_shared` in pyproject packages), the local fallback can be
removed.

The shim preserves the public surface of the old module
(`NAMESPACE`, `get_dlt_destination`, `get_duckdb_fallback_destination`,
`create_pipeline`) so that:

  * any historical import keeps working
  * the croilar DuckLake data lives under `s3://ducklake/croilar/`
    with Postgres db `ducklake_croilar`
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import dlt

# Backwards-compat: try the oideachais cross-quadrant import first.
try:
    from oideachais.dlt_utils.destinations import with_namespace

    with_namespace("croilar").re_export_into(globals())
except ImportError:
    # Local fallback — pre-Phase-2.3 implementation. Kept so the
    # croilar code-location doesn't break until the packaging is
    # fixed and the cross-quadrant import is wired.
    NAMESPACE = "croilar"

    @dataclass
    class DuckLakeConfig:
        """Minimal DuckLake config for the local fallback path.

        Phase 2.3 of the openspec change: this class is only used
        if the oideachais cross-quadrant import fails. Once croilar
        declares `oideachais` in `[tool.uv.sources]`, this whole
        class can be deleted.
        """

        postgres_host: str = "localhost"
        postgres_port: int = 5433
        postgres_db: str = f"ducklake_{NAMESPACE}"
        postgres_user: str = "lakekeeper"
        postgres_pass: str = "devpassword"
        bucket_url: str = f"s3://ducklake/{NAMESPACE}/"
        endpoint_url: str = "http://localhost:3900"

    def _get_local_config() -> DuckLakeConfig:
        return DuckLakeConfig(
            postgres_host=os.environ.get("DUCKLAKE_POSTGRES_HOST", "localhost"),
            postgres_port=int(os.environ.get("DUCKLAKE_POSTGRES_PORT", "5433")),
            postgres_db=os.environ.get("DUCKLAKE_POSTGRES_DB", f"ducklake_{NAMESPACE}"),
            postgres_user=os.environ.get("DUCKLAKE_POSTGRES_USER", "lakekeeper"),
            postgres_pass=os.environ.get("DUCKLAKE_POSTGRES_PASSWORD", "devpassword"),
            endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900"),
        )

    def get_dlt_destination(use_ducklake: bool | None = None) -> Any:
        from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials

        if use_ducklake is None:
            use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"
        if not use_ducklake:
            return dlt.destinations.duckdb(
                credentials=f"./data/{NAMESPACE}.duckdb"
            )

        cfg = _get_local_config()
        catalog_uri = (
            f"postgresql://{cfg.postgres_user}:{cfg.postgres_pass}"
            f"@{cfg.postgres_host}:{cfg.postgres_port}/{cfg.postgres_db}"
        )
        storage_config = {
            "bucket_url": cfg.bucket_url,
            "credentials": {
                "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
                "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
                "endpoint_url": cfg.endpoint_url,
                "region_name": os.environ.get("AWS_REGION", "garage"),
            },
        }
        credentials = DuckLakeCredentials(
            ducklake_name=NAMESPACE,
            catalog=catalog_uri,
            storage=storage_config,
        )
        return dlt.destinations.ducklake(credentials=credentials)

    def get_duckdb_fallback(
        database_path: str = f"./data/{NAMESPACE}.duckdb",
    ) -> Any:
        return dlt.destinations.duckdb(credentials=database_path)

    # Alias for backwards-compat with the oideachais API surface
    get_duckdb_fallback_destination = get_duckdb_fallback

    def create_pipeline(
        pipeline_name: str = "croilar",
        dataset_name: str = "croilar",
        use_ducklake: bool = True,
        **kwargs: Any,
    ) -> dlt.Pipeline:
        destination = (
            get_dlt_destination(use_ducklake=use_ducklake)
            if use_ducklake
            else get_duckdb_fallback_destination()
        )
        return dlt.pipeline(
            pipeline_name=pipeline_name,
            destination=destination,
            dataset_name=dataset_name,
            **kwargs,
        )
