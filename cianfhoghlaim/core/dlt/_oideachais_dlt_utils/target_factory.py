"""
oideachais.dlt_utils.target_factory — multi-target deployment factory.

Stage 4 of ``author-archive-v1``. Defines 3 deployment targets for the
author-archive pipeline:

  1. ``dev``       — local DuckDB (no S3, no Postgres). The default
                     for CI and quick local runs.
  2. ``staging``   — MotherDuck (managed DuckDB in the cloud).
                     Reachable from any container with the
                     ``MOTHERDUCK_TOKEN`` env var.
  3. ``prod``      — Garage S3 + Lakekeeper (DuckLake catalog).
                     The full lakehouse for the production
                     author-archive pipeline.

The factory is invoked from the Dagster assets via
``create_pipeline_for_target(target_name)`` and from the CLI helper
``oideachais/scripts/make_target.sh`` (Stage 4 of the plan).

Usage:

    # In a Dagster asset
    from oideachais.dlt_utils.target_factory import create_pipeline_for_target

    pipeline = create_pipeline_for_target(
        target_name="dev",       # or "staging" / "prod"
        pipeline_name="author_archive_mata",
        dataset_name="author_archive_mata",
    )
    pipeline.run(mata_source())

    # From the CLI
    $ ./oideachais/scripts/make_target.sh dev
    $ ./oideachais/scripts/make_target.sh prod
    $ make_target prod "OIDEACHAIS_USE_PROD=1"

Reference: openspec/changes/author-archive-multi-target/
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Target dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Target:
    """A deployment target for the author-archive pipeline.

    Attributes:
        name: One of ``dev``, ``staging``, ``prod``.
        destination: The DLT destination string (e.g. ``"duckdb"``,
            ``"motherduck"``, ``"ducklake"``).
        dataset_name_prefix: Prefix for the dataset_name (e.g.
            ``"author_archive_dev"`` vs ``"author_archive"``).
        description: Human-readable description of the target.
        requires_secrets: List of env vars the target needs.
        is_production: True for the prod target; affects safety
            guards.
    """

    name: str
    destination: str
    dataset_name_prefix: str
    description: str
    requires_secrets: tuple[str, ...] = field(default_factory=tuple)
    is_production: bool = False


# ---------------------------------------------------------------------------
# The 3 canonical targets
# ---------------------------------------------------------------------------

DEV = Target(
    name="dev",
    destination="duckdb",
    dataset_name_prefix="author_archive_dev",
    description=(
        "Local DuckDB file at ~/.cache/oideachais/author_archive.duckdb. "
        "The default for CI and quick local runs. No external dependencies."
    ),
    requires_secrets=(),
    is_production=False,
)

STAGING = Target(
    name="staging",
    destination="motherduck",
    dataset_name_prefix="author_archive_staging",
    description=(
        "MotherDuck (managed DuckDB in the cloud). For pre-production "
        "validation. Requires MOTHERDUCK_TOKEN."
    ),
    requires_secrets=("MOTHERDUCK_TOKEN",),
    is_production=False,
)

PROD = Target(
    name="prod",
    destination="ducklake",
    dataset_name_prefix="author_archive",
    description=(
        "Garage S3 + Lakekeeper (DuckLake catalog). The full lakehouse. "
        "Requires DUCKLAKE_POSTGRES_*, DUCKLAKE_S3_*, BUCKET, plus "
        "MotherDuck or S3 keys for the LLM-side writes."
    ),
    requires_secrets=(
        "DUCKLAKE_POSTGRES_HOST",
        "DUCKLAKE_POSTGRES_PORT",
        "DUCKLAKE_POSTGRES_DB",
        "DUCKLAKE_POSTGRES_USER",
        "DUCKLAKE_POSTGRES_PASSWORD",
        "BUCKET",
    ),
    is_production=True,
)

ALL_TARGETS: dict[str, Target] = {"dev": DEV, "staging": STAGING, "prod": PROD}


# ---------------------------------------------------------------------------
# Selection + validation
# ---------------------------------------------------------------------------


def get_target(name: str = "dev") -> Target:
    """Return the Target for ``name`` (``"dev"``, ``"staging"``, ``"prod"``).

    The default is ``"dev"`` (local DuckDB). The function also honours
    the ``OIDEACHAIS_TARGET`` env var as a CLI-side override.
    """
    effective = os.environ.get("OIDEACHAIS_TARGET", name).lower()
    if effective not in ALL_TARGETS:
        raise ValueError(
            f"Unknown target {effective!r}. "
            f"Choose one of: {sorted(ALL_TARGETS)}"
        )
    return ALL_TARGETS[effective]


def validate_target_secrets(target: Target) -> None:
    """Raise ``EnvironmentError`` if any required secret is missing.

    Called from the CLI helper before running a DLT pipeline against
    a non-dev target.
    """
    missing = [s for s in target.requires_secrets if not os.environ.get(s)]
    if missing:
        raise OSError(
            f"Target {target.name!r} requires the following env vars: {missing}. "
            f"Source them from Infisical via `locket inject` or set them manually."
        )


# ---------------------------------------------------------------------------
# Pipeline construction
# ---------------------------------------------------------------------------


def create_pipeline_for_target(
    target_name: str = "dev",
    *,
    pipeline_name: str,
    dataset_name: str,
) -> Any:
    """Create a DLT pipeline for the named target.

    Args:
        target_name: One of ``"dev"``, ``"staging"``, ``"prod"``.
        pipeline_name: The DLT pipeline name (used in
            ``~/.dlt/pipelines/{pipeline_name}`` state).
        dataset_name: The dataset/schema name in the target
            warehouse. The target's ``dataset_name_prefix`` is
            prepended automatically (e.g. ``"author_archive_dev"``
            in dev, ``"author_archive"`` in prod).

    Returns:
        A configured ``dlt.Pipeline`` instance ready to ``.run()``.
    """
    target = get_target(target_name)
    full_dataset_name = f"{target.dataset_name_prefix}_{dataset_name}"
    logger.info(
        "create_pipeline_for_target",
        target=target.name,
        destination=target.destination,
        dataset_name=full_dataset_name,
    )

    import dlt

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=target.destination,
        dataset_name=full_dataset_name,
    )


def create_dev_pipeline(*, pipeline_name: str, dataset_name: str) -> Any:
    """Shortcut: create a local-DuckDB pipeline (no env validation)."""
    db_path = Path(
        os.environ.get(
            "OIDEACHAIS_DEV_DB",
            str(Path.home() / ".cache" / "oideachais" / "author_archive.duckdb"),
        )
    )
    db_path.parent.mkdir(parents=True, exist_ok=True)
    import dlt

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=dlt.destinations.duckdb(str(db_path)),
        dataset_name=f"author_archive_dev_{dataset_name}",
    )


def create_staging_pipeline(*, pipeline_name: str, dataset_name: str) -> Any:
    """Shortcut: create a MotherDuck pipeline (requires MOTHERDUCK_TOKEN)."""
    validate_target_secrets(STAGING)
    import dlt

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination="motherduck",
        dataset_name=f"author_archive_staging_{dataset_name}",
    )


def create_prod_pipeline(*, pipeline_name: str, dataset_name: str) -> Any:
    """Shortcut: create a DuckLake (Garage S3 + Lakekeeper) pipeline."""
    validate_target_secrets(PROD)
    return _create_ducklake_pipeline(
        pipeline_name=pipeline_name,
        dataset_name=f"author_archive_{dataset_name}",
    )


def _create_ducklake_pipeline(*, pipeline_name: str, dataset_name: str) -> Any:
    """Build the DuckLake destination with the prod env config.

    Reuses the helpers from ``oideachais.dlt_utils.destinations``.
    """
    import dlt

    from .destinations import _build_local_destination  # type: ignore

    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=_build_local_destination("oideachais"),
        dataset_name=dataset_name,
    )


__all__ = [
    "ALL_TARGETS",
    "DEV",
    "PROD",
    "STAGING",
    "Target",
    "create_dev_pipeline",
    "create_pipeline_for_target",
    "create_prod_pipeline",
    "create_staging_pipeline",
    "get_target",
    "validate_target_secrets",
]
