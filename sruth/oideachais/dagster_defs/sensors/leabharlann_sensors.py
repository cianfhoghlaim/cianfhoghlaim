"""
Leabharlann directory-watch sensor.

Polls the 3 leabharlann sources every 60 s and emits a `RunRequest` for
the affected partition when files change.

Polled roots:
- `leabharlann/{gaeilge,aigne}/` (any subdir)
- `leabharlann/zotero/` (top level)
- `stedding/Takeout/` (any subdir, including the no-account-prefix layout)
- `~/Downloads/takeout-*.zip` (new zips)

Reference: openspec/changes/leabharlann-cocoindex-v1/tasks.md Phase 4
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


def _default_leabharlann_root() -> Path:
    return Path(
        os.environ.get(
            "LEABHARLANN_ROOT",
            str(
                Path(__file__).resolve().parents[5]
                / "leabharlann"
            ),
        )
    )


def _default_takeout_root() -> Path:
    return Path(
        os.environ.get(
            "LEABHARLANN_TAKEOUT_ROOT",
            str(
                Path(__file__).resolve().parents[5]
                / "stedding"
                / "Takeout"
            ),
        )
    )


def _walk_modified_files(root: Path, max_depth: int = 8) -> Iterator[Path]:
    """Yield files under `root` whose mtime is within the last 90 s."""
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


@dg.sensor(
    name="leabharlann_directory_sensor",
    minimum_interval_seconds=60,
    description=(
        "Polls the leabharlann books / zotero / takeout roots every 60 s "
        "and emits RunRequests for affected partitions."
    ),
)
def leabharlann_directory_sensor(
    context: dg.SensorEvaluationContext,
) -> dg.SensorResult:
    """
    Directory-watch sensor for the leabharlann assets.
    """
    leabharlann_root = _default_leabharlann_root()
    takeout_root = _default_takeout_root()
    run_requests: list[dg.RunRequest] = []

    # 1. Books — one RunRequest per affected subject (gaeilge / aigne).
    for subject in ("gaeilge", "aigne"):
        subject_dir = leabharlann_root / subject
        for _ in _walk_modified_files(subject_dir):
            run_requests.append(
                dg.RunRequest(
                    run_key=f"leabharlann_books:{subject}:{time.time_ns()}",
                    asset_selection=[
                        dg.AssetKey(["leabharlann_books_raw"]),
                    ],
                    partition_key=subject,
                )
            )
            break  # one RunRequest per subject per tick

    # 2. Zotero — single asset, single RunRequest (any modified file).
    zotero_dir = leabharlann_root / "zotero"
    for _ in _walk_modified_files(zotero_dir):
        run_requests.append(
            dg.RunRequest(
                run_key=f"leabharlann_zotero:{time.time_ns()}",
                asset_selection=[dg.AssetKey(["leabharlann_zotero_raw"])],
                partition_key="batch_1",  # all batches share one source
            )
        )
        break

    # 3. Takeout — one RunRequest per affected account.
    for _ in _walk_modified_files(takeout_root):
        run_requests.append(
            dg.RunRequest(
                run_key=f"leabharlann_takeout:stedding_takeout:{time.time_ns()}",
                asset_selection=[dg.AssetKey(["leabharlann_takeout_v1_raw"])],
                partition_key="stedding_takeout",
            )
        )
        break

    # 4. New zips in ~/Downloads.
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        for zip_path in downloads.glob("takeout-*.zip"):
            try:
                if zip_path.stat().st_mtime >= time.time() - 90:
                    run_requests.append(
                        dg.RunRequest(
                            run_key=f"leabharlann_takeout:zip:{zip_path.stem}",
                            asset_selection=[
                                dg.AssetKey(["leabharlann_takeout_v1_raw"]),
                            ],
                            partition_key=f"zip:{zip_path.stem}",
                        )
                    )
            except (OSError, PermissionError):
                continue

    context.update_cursor(str(time.time()))
    return dg.SensorResult(run_requests=run_requests)


leabharlann_sensors = [leabharlann_directory_sensor]


__all__ = ["leabharlann_directory_sensor", "leabharlann_sensors"]
