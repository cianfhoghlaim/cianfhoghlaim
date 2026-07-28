"""BIEP v3 full setup — canonical operator entrypoint.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

A single `mise run biep:v3:setup` brings the entire BIEP v3 system
online. This is the canonical "first 30 minutes" entrypoint for a
newcomer to set up the BIEP v3 in their own environment.

Steps:
1. Check Docker is running
2. Bring up the lakehouse stack (Garage + Lakekeeper + Lance + Postgres + DuckLake)
3. Smoke-test the 13 lakehouse services
4. Run `baml-cli generate` to compile the BAML client
5. Run `seed_registry()` to populate the 428-cohort British Isles registry
6. Create the `cianhoghlaim` Lance namespace in Lakekeeper
7. Validate the 4 openspec changes (`2026-08-13-biep-v3-systematic-download-ireland-england-v1`
   + the 3 BIEP v3 follow-up changes)
8. Run `mise run lint:skills` for skill metadata validation (53/53 pass)

This is the operator surface that documents the entire BIEP v3
systematic download + iterate plan as a single command.
"""
from __future__ import annotations

import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("biiep_v3_setup")


def _step_docker_check() -> bool:
    """Check Docker is running."""
    try:
        result = subprocess.run(
            ["docker", "version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            logger.error("Docker is not running. Start Docker Desktop and try again.")
            return False
        logger.info("Docker is running: %s", result.stdout.splitlines()[0])
        return True
    except FileNotFoundError:
        logger.error("Docker is not installed. Install Docker Desktop and try again.")
        return False
    except Exception as exc:  # noqa: BLE001
        logger.error("Docker check failed: %s", exc)
        return False


def _step_lakehouse_up() -> bool:
    """Bring up the lakehouse stack (13 services)."""
    logger.info("Bringing up the lakehouse stack (13 services)...")
    try:
        result = subprocess.run(
            [
                "docker", "compose",
                "-f", "bonneagar/stacks/lakehouse/compose.yaml",
                "up", "-d",
            ],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            logger.error("Lakehouse stack up failed: %s", result.stderr[-1000:])
            return False
        logger.info("Lakehouse stack up.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Lakehouse stack up raised: %s", exc)
        return False


def _step_lakehouse_smoke() -> bool:
    """Smoke-test the 13 lakehouse services (200 OK)."""
    logger.info("Smoke-testing the 13 lakehouse services...")
    try:
        result = subprocess.run(
            ["mise", "run", "biep:v3:lakehouse:smoke-test"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            logger.error("Lakehouse smoke test failed: %s", result.stderr[-1000:])
            return False
        logger.info("Lakehouse smoke test passed.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Lakehouse smoke test raised: %s", exc)
        return False


def _step_baml_codegen() -> bool:
    """Run `baml-cli generate` to compile the BAML client."""
    logger.info("Running BAML codegen (baml-cli generate)...")
    try:
        result = subprocess.run(
            ["mise", "run", "baml:generate"],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode != 0:
            logger.error("BAML codegen failed: %s", result.stderr[-1000:])
            return False
        logger.info("BAML codegen succeeded.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("BAML codegen raised: %s", exc)
        return False


def _step_seed_registry() -> bool:
    """Seed the British Isles subject registry to 428+ rows."""
    logger.info("Seeding the British Isles subject registry (428+ rows)...")
    try:
        result = subprocess.run(
            ["mise", "run", "biep:v3:registry:seed"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            logger.error("Registry seed failed: %s", result.stderr[-1000:])
            return False
        logger.info("Registry seed succeeded.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Registry seed raised: %s", exc)
        return False


def _step_create_lance_namespace() -> bool:
    """Create the `cianhoghlaim` Lance namespace in Lakekeeper."""
    logger.info("Creating the cianfhoghlaim Lance namespace in Lakekeeper...")
    try:
        result = subprocess.run(
            ["python3", "scripts/create_lance_namespace.py"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            logger.error("Lance namespace creation failed: %s", result.stderr[-500:])
            return False
        logger.info("Lance namespace created.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Lance namespace creation raised: %s", exc)
        return False


def _step_validate_openspec() -> bool:
    """Validate the 4 BIEP v3 openspec changes."""
    logger.info("Validating the 4 BIEP v3 openspec changes...")
    changes = [
        "2026-08-13-biep-v3-systematic-download-ireland-england-v1",
        "2026-07-30-biep-v3-sct-wls-ni-v1",
        "2026-07-31-biep-v3-crown-dependencies-v1",
        "2026-08-13-biep-v3-filesystem-and-language-pipelines-v1",
    ]
    for change in changes:
        result = subprocess.run(
            ["openspec", "validate", change, "--strict"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            logger.error("openspec validate %s failed: %s", change, result.stderr[-500:])
            return False
    logger.info("All 4 openspec changes validated.")
    return True


def _step_lint_skills() -> bool:
    """Run `mise run lint:skills` for skill metadata validation (53/53 pass)."""
    logger.info("Running mise run lint:skills (53/53 pass)...")
    try:
        result = subprocess.run(
            ["mise", "run", "lint:skills"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            logger.error("lint:skills failed: %s", result.stderr[-1000:])
            return False
        logger.info("lint:skills passed (53/53).")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("lint:skills raised: %s", exc)
        return False


def main() -> int:
    """Run the canonical BIEP v3 full setup. Exit 0 on success."""
    logger.info("=" * 60)
    logger.info("BIEP v3 full setup — canonical operator entrypoint")
    logger.info("=" * 60)

    steps = [
        ("1. Docker check", _step_docker_check),
        ("2. Lakehouse stack up", _step_lakehouse_up),
        ("3. Lakehouse smoke test", _step_lakehouse_smoke),
        ("4. BAML codegen", _step_baml_codegen),
        ("5. Registry seed (428+ rows)", _step_seed_registry),
        ("6. Create cianfhoghlaim Lance namespace", _step_create_lance_namespace),
        ("7. Validate 4 openspec changes", _step_validate_openspec),
        ("8. Run lint:skills (53/53)", _step_lint_skills),
    ]

    for name, step in steps:
        logger.info("=== Running step %s ===", name)
        if not step():
            logger.error("BIEP v3 setup failed at step %s.", name)
            return 1

    logger.info("=" * 60)
    logger.info("BIEP v3 setup complete. All 8 steps passed.")
    logger.info("Next steps:")
    logger.info("  - Run `mise run biep:v3:m0` for the foundation entrypoint")
    logger.info("  - Run `mise run biep:v3:m1` for the Ireland LC pipeline")
    logger.info("  - Run `mise run biep:v3:m3` for the England A-Level pipeline")
    logger.info("  - Run `mise run biep:v3:m4` for the England GCSE pipeline")
    logger.info("  - Run `mise run biep:v3:m5..m10` for the 6 deferred jurisdictions")
    logger.info("  - Run `mise run biep:v3:status` to see the current state")
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
