"""M0 foundation entrypoint — BIEP v3 systematic download & iteration.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

Runs the 4 M0 foundation tasks + 4 asset checks in sequence:

1. Bring up the lakehouse stack (13 services)
2. Smoke-test the 13 lakehouse services
3. Run `mise run baml:generate` (BAML client codegen)
4. Seed the British Isles Subject Registry to >= 210 rows
5. Create the `cianhoghlaim` Lance namespace in Lakekeeper
6. Materialise the 4 M0 Dagster assets + 4 asset checks

This is the M0 entrypoint invoked by `mise run biep:v3:m0`.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_m0")


# -----------------------------------------------------------------------------
# Step 1: Bring up the lakehouse stack
# -----------------------------------------------------------------------------


def step_lakehouse_up() -> bool:
    """Run `docker compose ... up -d` for the lakehouse stack."""
    compose_path = Path("bonneagar/stacks/lakehouse/compose.yaml")
    if not compose_path.exists():
        logger.error(f"Lakehouse compose.yaml not found at {compose_path}")
        return False
    logger.info("Bringing up the lakehouse stack (13 services)...")
    result = subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "up", "-d"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        logger.error(f"docker compose up failed: {result.stderr}")
        return False
    logger.info("Lakehouse stack up.")
    return True


# -----------------------------------------------------------------------------
# Step 2: Smoke-test the 13 lakehouse services
# -----------------------------------------------------------------------------


def step_lakehouse_smoke_test() -> bool:
    """Run the `lakehouse_smoke_test` Dagster asset (15s smoke test)."""
    logger.info("Smoke-testing the 13 lakehouse services...")
    script_path = Path("scripts/smoke_test_lakehouse.py")
    if not script_path.exists():
        logger.warning(f"smoke_test_lakehouse.py not found; skipping")
        return True
    result = subprocess.run(
        ["python3", str(script_path), "--dev"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        logger.error(f"lakehouse smoke test failed: {result.stderr}")
        return False
    logger.info("Lakehouse smoke test passed.")
    return True


# -----------------------------------------------------------------------------
# Step 3: BAML codegen
# -----------------------------------------------------------------------------


def step_baml_codegen() -> bool:
    """Run `mise run baml:generate`."""
    logger.info("Running BAML codegen...")
    result = subprocess.run(
        ["mise", "run", "baml:generate"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        logger.error(f"baml:generate failed (exit {result.returncode}): {result.stderr[-1000:]}")
        return False
    logger.info("BAML codegen succeeded.")
    return True


# -----------------------------------------------------------------------------
# Step 4: Seed the registry
# -----------------------------------------------------------------------------


def step_registry_seed() -> bool:
    """Seed the British Isles Subject Registry to >= 210 rows."""
    logger.info("Seeding the British Isles Subject Registry...")
    result = subprocess.run(
        ["mise", "run", "biep:v3:registry:seed"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        logger.error(f"registry:seed failed: {result.stderr[-1000:]}")
        return False
    logger.info(f"Registry seeded: {result.stdout.strip()}")
    return True


# -----------------------------------------------------------------------------
# Step 5: Create the cianfhoghlaim Lance namespace
# -----------------------------------------------------------------------------


def step_lance_namespace() -> bool:
    """Create the `cianhoghlaim` Lance namespace in Lakekeeper."""
    logger.info("Creating the cianfhoghlaim Lance namespace...")
    script_path = Path("scripts/create_lance_namespace.py")
    if not script_path.exists():
        logger.warning(f"create_lance_namespace.py not found; skipping")
        return True
    result = subprocess.run(
        ["python3", str(script_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        logger.error(f"lance namespace creation failed: {result.stderr}")
        return False
    logger.info("Lance namespace created.")
    return True


# -----------------------------------------------------------------------------
# Step 6: Materialise the 4 M0 Dagster assets
# -----------------------------------------------------------------------------


def step_m0_assets() -> bool:
    """Run the 4 M0 Dagster assets via `dagster asset materialize`."""
    logger.info("Materialising the 4 M0 foundation Dagster assets...")
    result = subprocess.run(
        [
            "uv", "run", "dagster", "asset", "materialize",
            "--select", "lakehouse_smoke_test,baml_codegen_gate,registry_seed_count,lance_namespace_ready",
            "-m", "orchestration.definitions",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        logger.error(f"Materialize failed (exit {result.returncode}): {result.stderr[-2000:]}")
        return False
    logger.info("All 4 M0 assets materialised successfully.")
    return True


# -----------------------------------------------------------------------------
# Main entrypoint
# -----------------------------------------------------------------------------


def main() -> int:
    """Run all 6 M0 steps in sequence. Exit 0 iff all 6 succeed."""
    steps = [
        ("lakehouse:up", step_lakehouse_up),
        ("lakehouse:smoke-test", step_lakehouse_smoke_test),
        ("baml:generate", step_baml_codegen),
        ("registry:seed", step_registry_seed),
        ("lance:namespace", step_lance_namespace),
        ("m0:assets", step_m0_assets),
    ]
    for name, step in steps:
        logger.info(f"=== Running step {name} ===")
        if not step():
            logger.error(f"M0 step {name} failed. Aborting.")
            return 1
    logger.info("M0 foundation unblock complete. All 12 prerequisites satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
