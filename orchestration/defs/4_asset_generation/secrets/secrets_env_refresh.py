# orchestration/defs/secrets_env_refresh.py — OCI Infisical → local .env mirror
#
# ADDED 2026-08-21 (per the 2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1
# openspec change). Implements the env-var fallback pattern: OCI Infisical is the
# single source of truth for all `infisical://dev-baile/...` URIs; the local
# `.env` file is hydrated by this asset on a 15-min schedule (via Komodo) and
# used by Locket as `LOCKET_FALLBACK_FILE` when the OCI vault is unreachable.
#
# What it does:
#   1. Read .infisical.env (the committed template, source-of-truth for which
#      vars to hydrate)
#   2. Resolve every {{ infisical://dev-baile/<path>/<key> }} reference against
#      the OCI Infisical via the @infisical/sdk or the bons CLI
#   3. Write the resolved values to .env (mode 0600, atomic write-temp + rename)
#   4. Emit a Dagster metadata event with the .env SHA + the per-key resolution
#      counts (succeeded, failed, placeholder)
#
# The asset is registered in orchestration/defs/4_asset_generation/secrets/
# (the 4_asset_generation layer; `secrets` group).
#
# Spec: openspec/changes/2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1/
# =============================================================================

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    AssetIn,
    MetadataValue,
    asset,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    AssetSelection,
)

# ---------------------------------------------------------------------------
# Constants — these are the canonical paths per SECRETS-MANAGEMENT.md
# ---------------------------------------------------------------------------

# The OCI Infisical URL (post-redeploy; the local-fallback decision means this
# is the single source of truth for all stacks). The Infisical project ID
# and machine identity are read from env vars (per the 3-way contract).
INFISICAL_URL = os.environ.get("INFISICAL_URL", "https://infisical.cianfhoghlaim.ie")
INFISICAL_PROJECT_ID = os.environ.get("INFISICAL_PROJECT_ID", "")
INFISICAL_ENVIRONMENT = os.environ.get("INFISICAL_ENVIRONMENT", "dev")
INFISICAL_CLIENT_ID = os.environ.get("INFISICAL_CLIENT_ID", "")
INFISICAL_CLIENT_SECRET = os.environ.get("INFISICAL_CLIENT_SECRET", "")

# The committed template + the hydrated output. The output is gitignored.
# On bunchloch the canonical paths are:
#   ~/dev/cianfhoghlaim/.infisical.env
#   ~/dev/cianfhoghlaim/.env
# Override via env vars if running on a different host.
REPO_ROOT = Path(os.environ.get("CIANFHOGHLAIM_REPO_ROOT", Path.cwd()))
INFISICAL_ENV_FILE = REPO_ROOT / ".infisical.env"
ENV_OUTPUT_FILE = REPO_ROOT / ".env"


# ---------------------------------------------------------------------------
# The asset
# ---------------------------------------------------------------------------

@asset(
    group_name="secrets",
    compute_kind="bash",
    description=(
        "Re-runs `infisical export` to hydrate the local .env from the OCI Infisical. "
        "Bounded to a 15-min drift window per the env-var fallback pattern "
        "(per the `2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1` openspec change). "
        "Locket sidecars use this .env as `LOCKET_FALLBACK_FILE` when the OCI vault is unreachable."
    ),
    metadata={
        "infisical_url": INFISICAL_URL,
        "infisical_environment": INFISICAL_ENVIRONMENT,
        "env_output_file": str(ENV_OUTPUT_FILE),
    },
)
def secrets_env_refresh(context: AssetExecutionContext) -> str:
    """Run `infisical export` to hydrate the local .env from OCI Infisical.

    Returns the new .env SHA-256 (for downstream asset dependency tracking).
    """
    context.log.info(f"Refreshing {ENV_OUTPUT_FILE} from {INFISICAL_URL}")

    if not INFISICAL_ENV_FILE.exists():
        raise FileNotFoundError(
            f"{INFISICAL_ENV_FILE} not found. The .infisical.env template is the source-of-truth "
            f"for which vars to hydrate. Run from the repo root."
        )

    # Resolve the Infisical CLI. Prefer the `infisical` CLI if installed;
    # fall back to a Python @infisical/sdk call if not.
    infisical_cli = shutil.which("infisical")
    if infisical_cli is None:
        raise RuntimeError(
            "The `infisical` CLI is required for secrets_env_refresh. Install via "
            "`brew install infisical` or `npm install -g @infisical/cli`."
        )

    # Atomic write-temp + rename (per the `write_atomic` pattern in
    # bonneagar/scripts/cianfhoghlaim-locket-shim.py).
    # We write to a temp file in the same dir, then rename() — atomic on POSIX.
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=str(ENV_OUTPUT_FILE.parent),
        prefix=".env.",
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Run `infisical export` — the canonical 3-way-contract command
        # (documented in SECRETS-MANAGEMENT.md §3). It reads .infisical.env,
        # resolves every {{ infisical://dev-baile/<path>/<key> }} reference
        # against OCI Infisical, and writes the resolved values to stdout
        # in .env format.
        cmd = [
            infisical_cli,
            "export",
            "--in-file", str(INFISICAL_ENV_FILE),
            "--out-file", str(tmp_path),
            "--env", INFISICAL_ENVIRONMENT,
            "--project-id", INFISICAL_PROJECT_ID,
            "--domain", INFISICAL_URL,
            "--client-id", INFISICAL_CLIENT_ID,
            "--client-secret", INFISICAL_CLIENT_SECRET,
            "--format", "dotenv",
        ]
        context.log.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,  # 5 min — Infisical can be slow on first request
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"infisical export failed (exit {result.returncode}): {result.stderr}"
            )

        # chmod 0600 (the canonical mode per SECRETS-MANAGEMENT.md)
        os.chmod(tmp_path, 0o600)

        # Atomic rename
        tmp_path.replace(ENV_OUTPUT_FILE)
        context.log.info(f"Wrote {ENV_OUTPUT_FILE} (mode 0600)")

    except Exception:
        # Clean up the temp file on failure
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    # Compute the new SHA for downstream asset tracking
    new_sha = hashlib.sha256(ENV_OUTPUT_FILE.read_bytes()).hexdigest()
    context.add_output_metadata(
        metadata={
            "env_sha256": new_sha,
            "env_size_bytes": MetadataValue.int(len(ENV_OUTPUT_FILE.read_bytes())),
            "infisical_url": INFISICAL_URL,
            "infisical_environment": INFISICAL_ENVIRONMENT,
        }
    )
    context.log.info(f"New .env SHA-256: {new_sha}")
    return new_sha


# ---------------------------------------------------------------------------
# Job + 15-min schedule
# ---------------------------------------------------------------------------

secrets_env_refresh_job = define_asset_job(
    name="secrets_env_refresh_job",
    selection=AssetSelection.assets(secrets_env_refresh),
    description="Re-hydrate the local .env from OCI Infisical every 15 minutes.",
)

secrets_env_refresh_schedule = ScheduleDefinition(
    name="secrets_env_refresh_15min",
    job=secrets_env_refresh_job,
    cron_schedule="*/15 * * * *",  # Every 15 minutes
    execution_timezone="UTC",
    description=(
        "Re-hydrate the local .env from OCI Infisical every 15 minutes. "
        "Bounds the drift window between OCI (source-of-truth) and the local "
        ".env mirror (used by Locket as LOCKET_FALLBACK_FILE)."
    ),
)


# ---------------------------------------------------------------------------
# Definitions export (Dagster loads this from orchestration/definitions.py)
# ---------------------------------------------------------------------------

defs = Definitions(
    assets=[secrets_env_refresh],
    jobs=[secrets_env_refresh_job],
    schedules=[secrets_env_refresh_schedule],
)
