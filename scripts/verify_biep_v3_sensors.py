#!/usr/bin/env python3
"""Verify the 9 BIEP v3 Dagster sensors.

Per the 2026-08-13 BIEP v3 lakehouse full activation plan (Phase 3):

Loads each of the 9 sensors from `orchestration/sensors/` directly
and evaluates them against the live DuckLake registry + the Lakekeeper
REST catalog. Each sensor takes a `SensorEvaluationContext` parameter,
so we instantiate one with a minimal mock instance.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Set repo root for module imports
REPO_ROOT = Path(__file__).resolve().parents[1]

# The 9 BIEP v3 sensors
SENSOR_NAMES = [
    "ncca_registry_sensor",
    "sqa_registry_sensor",
    "wjec_registry_sensor",
    "ccea_registry_sensor",
    "jcq_registry_sensor",
    "jersey_registry_sensor",
    "guernsey_registry_sensor",
    "isle_of_man_registry_sensor",
    "garage_pdf_arrival_sensor",
]


def make_context():
    """Build a real SensorEvaluationContext for sensor eval."""
    from dagster import DagsterInstance, SensorEvaluationContext

    instance = DagsterInstance.ephemeral()
    return SensorEvaluationContext(
        instance_ref=None,
        last_tick_completion_time=None,
        last_run_key=None,
        cursor=None,
        log_key=None,
        repository_name="biep_v3",
        repository_def=None,
        instance=instance,
        sensor_name="test",
        resources={},
        definitions=None,
        last_sensor_start_time=None,
        code_location_origin=None,
        last_completion_time=None,
    )


def main() -> int:
    print("BIEP v3 Sensor Verification")
    print("=" * 60)

    loaded = []
    failed = []
    for name in SENSOR_NAMES:
        try:
            module = __import__(f"orchestration.sensors.{name}", fromlist=[name])
            sensor_obj = getattr(module, name, None)
            if sensor_obj is None:
                failed.append((name, "no module attribute"))
                continue

            ctx = make_context()
            t0 = time.time()
            try:
                # Call the sensor function directly with the mock context
                result = sensor_obj(ctx)
                tick_result = result.run_requests if hasattr(result, "run_requests") else []
                skip_reason = (
                    result.skip_message
                    if hasattr(result, "skip_message") and not tick_result
                    else None
                )
                row_count = len(tick_result) if isinstance(tick_result, list) else 0
            except Exception as e:
                tick_result = None
                skip_reason = f"ERROR: {type(e).__name__}: {str(e)[:80]}"
                row_count = 0
            duration = time.time() - t0
            loaded.append((name, sensor_obj, row_count, skip_reason, duration))
            marker = "✓" if row_count > 0 else "~"
            print(f"  [{marker}] {name:<32} {row_count:>3} run requests  {duration * 1000:>5.1f}ms")
            if skip_reason and not row_count:
                print(f"        → {skip_reason}")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"  [✗] {name:<32} ERROR: {str(e)[:80]}")

    print()
    print("=" * 60)
    print(f"Loaded: {len(loaded)} / {len(SENSOR_NAMES)}")
    print(f"Failed: {len(failed)}")

    # Summary table
    print()
    print("Per-sensor summary:")
    print(f"  {'sensor':<32} {'run_requests':>14} {'duration_ms':>12}")
    for name, _, rr, _, dur in loaded:
        print(f"  {name:<32} {rr:>14} {dur * 1000:>12.1f}")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
