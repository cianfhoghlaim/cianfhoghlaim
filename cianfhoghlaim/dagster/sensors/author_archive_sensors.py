"""
Author-Archive directory-watch sensor.

Polls the three target roots every 60 s:
- `university_of_galway/` (5 sub-dirs)
- `gemini_deep_research/` (7 domains)
- `Takeout/<account>/` (one per configured account)

For each new or changed file, the sensor emits a `RunRequest` for the
appropriate partition (`author_archive_uog_subdirs`,
`author_archive_gemini_domains`, or `author_archive_accounts`).

The dlt scanner already does its own incremental via SHA-256, so the
sensor is a fire-and-forget hint, not a correctness mechanism.

Reference: openspec/changes/author-archive-gemini-and-uos-ingestion/
            tasks.md Phase 5
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Helpers
# ============================================================================


def _default_uog_root() -> Path:
    return Path(
        os.environ.get(
            "AUTHOR_ARCHIVE_UOG_PATH",
            str(
                Path(__file__).resolve().parents[5]
                / "author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin"
                / "university_of_galway"
            ),
        )
    )


def _default_gemini_root() -> Path:
    return Path(
        os.environ.get(
            "AUTHOR_ARCHIVE_GEMINI_PATH",
            str(
                Path(__file__).resolve().parents[5]
                / "author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin"
                / "gemini_deep_research"
            ),
        )
    )


def _walk_modified_files(root: Path, max_depth: int = 6) -> Iterator[Path]:
    """Yield files under `root` whose mtime is recent (last 90 s)."""
    if not root.exists():
        return
    threshold = time.time() - 90
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            if path.stat().st_mtime >= threshold:
                yield path
        except (OSError, PermissionError):
            continue


# ============================================================================
# Sensor
# ============================================================================


@dg.sensor(
    name="author_archive_directory_sensor",
    minimum_interval_seconds=60,
    description=(
        "Polls the UoG / Gemini / Takeout roots every 60s and emits "
        "RunRequests for partitions whose files have been touched."
    ),
)
def author_archive_directory_sensor(
    context: dg.SensorEvaluationContext,
) -> dg.SensorResult:
    """
    Directory-watch sensor for the author-archive assets.

    Emits one `RunRequest` per affected partition per tick.
    """
    uog_root = _default_uog_root()
    gemini_root = _default_gemini_root()
    run_requests: list[dg.RunRequest] = []

    # UoG — one RunRequest per affected sub-dir.
    for path in _walk_modified_files(uog_root):
        try:
            rel = path.relative_to(uog_root)
        except ValueError:
            continue
        if not rel.parts:
            continue
        subdir = rel.parts[0]
        run_requests.append(
            dg.RunRequest(
                run_key=f"uog:{subdir}:{path.stat().st_mtime_ns}",
                asset_selection=[dg.AssetKey(["author_archive_university_of_galway_raw"])],
                partition_key=subdir,
            )
        )

    # Gemini — one RunRequest per affected domain.
    for path in _walk_modified_files(gemini_root):
        try:
            rel = path.relative_to(gemini_root)
        except ValueError:
            continue
        if not rel.parts:
            continue
        domain = rel.parts[0]
        run_requests.append(
            dg.RunRequest(
                run_key=f"gemini:{domain}:{path.stat().st_mtime_ns}",
                asset_selection=[dg.AssetKey(["author_archive_gemini_deep_research_raw"])],
                partition_key=domain,
            )
        )

    # Takeout — one RunRequest per affected account (filesystem only Phase 1).
    try:
        from cianfhoghlaim.dlt.leabharlann import load_takeout_accounts
    except ImportError:
        load_takeout_accounts = None  # type: ignore[assignment]

    if load_takeout_accounts is not None:
        for account in load_takeout_accounts():
            if not account.takeout_path.exists():
                continue
            for _ in _walk_modified_files(account.takeout_path):
                run_requests.append(
                    dg.RunRequest(
                        run_key=f"takeout:{account.account_label}:{time.time_ns()}",
                        asset_selection=[dg.AssetKey(["author_archive_takeout_raw"])],
                        partition_key=account.account_label,
                    )
                )
                break  # one RunRequest per account per tick

    context.update_cursor(str(time.time()))
    return dg.SensorResult(run_requests=run_requests)


# ============================================================================
# Sensor list export
# ============================================================================


author_archive_sensors = [author_archive_directory_sensor]

__all__ = ["author_archive_directory_sensor", "author_archive_sensors"]
