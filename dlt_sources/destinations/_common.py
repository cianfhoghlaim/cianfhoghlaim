"""dlt_sources.destinations._common — shared credential validation + namespace defaults.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (§1.1, §7.1 of the master plan at
`openspec/plans/2026-08-24-master-refactor-plan.md`).

This module is the SINGLE SOURCE OF TRUTH for the per-layer destination
infrastructure. It contains:

- The canonical `DUCKLAKE_NAMESPACE` constant — `"ducklake_cianfhoghlaim"`
  — every DuckLake ATTACH across the platform uses this name.
- The 5 per-quadrant `metadata_schema` strings — `oideachais`, `tuatha`,
  `croilar`, `agents`, `media` — so each quadrant owns its own Postgres
  metadata schema inside the shared `md:cianfhoghlaim` catalog.
- The 6 legacy DuckLake namespace aliases that pre-Wave-1 code paths
  still use, routed to the consolidated namespace.
- The `validate_credentials(env)` helper that asserts every required
  environment variable is present before a destination can be built.

New destination modules SHOULD import from here rather than re-declaring
namespace constants or env-var names. Legacy destinations continue to
work via the shims at:

- `dlt_sources.common.destinations_cianfhoghlaim` (re-export shim)
- `dlt_sources.common.named_destinations` (re-export shim)
- `dlt_sources.common.destinations.*` (re-export shim)
- `dlt_sources.lakehouse.destinations` (re-export shim)
- `dlt_sources.lakehouse.personal_archive_destinations` (re-export shim)
"""
from __future__ import annotations

import os
from typing import Mapping


# ─── The canonical DuckLake namespace (per master plan §1.1) ────────────────

DUCKLAKE_NAMESPACE: str = "ducklake_cianfhoghlaim"
"""The single consolidated DuckLake namespace (replaces the 6 legacy
namespaces per Wave 4 of the master plan).

The Postgres catalog behind this namespace is the canonical Cianfhoghlaim
DuckLake catalog (`md:cianfhoghlaim`). All five per-quadrant
`metadata_schema` values live inside this single catalog.

Reference:
- Master plan §1.1 (single namespace consolidation)
- Wave 4 DuckLake v1.0 hardening change
"""

# ─── The 5 per-quadrant Postgres metadata schemas ───────────────────────────

QUADRANT_METADATA_SCHEMAS: tuple[str, ...] = (
    "oideachais",
    "tuatha",
    "croilar",
    "agents",
    "media",
)
"""The 5 canonical per-quadrant Postgres metadata schemas.

Each quadrant owns its own `metadata_schema` inside the shared
`md:cianfhoghlaim` DuckLake Postgres catalog. This is the
**canonical carve rule** for the multi-repo scaffold (per
`openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/specs/cianfhoghlaim-dlt-sources-multi-repo/spec.md`).
"""

QUADRANT_TO_DUCKLAKE_KEY: Mapping[str, str] = {
    "oideachais": "ducklake_oideachais_quadrant",
    "tuatha": "ducklake_tuatha_quadrant",
    "croilar": "ducklake_croilar_quadrant",
    "agents": "ducklake_agents_quadrant",
    "media": "ducklake_media_quadrant",
}
"""Maps each quadrant name to the canonical `named_destinations()` key
for the per-quadrant destination. Used by `get_ducklake_destination(...)`
when a quadrant is requested via the `metadata_schema` argument.
"""

# ─── Legacy DuckLake namespace aliases ───────────────────────────────────────
# These pre-Wave-4 namespace names were consolidated into
# `ducklake_cianfhoghlaim` per the Wave 4 master plan. They are
# preserved here so the canonical `DESTINATIONS` registry in
# `dlt_sources.destinations.__init__` can route every legacy key to the
# consolidated destination factory.

LEGACY_DUCKLAKE_NAMESPACE_ALIASES: tuple[str, ...] = (
    "ducklake_oideachais",
    "ducklake_educational",
    "ducklake_crypteolas",
    "ducklake_tertiary",
    "ducklake_uog",
    "ducklake_cie",
    "ducklake_oideachais",  # de-duplicated by tuple; preserved for documentation
    "ducklake_tuath",
    "ducklake_meaisinfhoghlaim",
    "ducklake_aleyum",
    "ducklake_croilar",
)
"""The 6 → 10 legacy DuckLake namespace names that pre-Wave-4 code paths
still use. All are routed to `DUCKLAKE_NAMESPACE`
(`"ducklake_cianfhoghlaim"`) via the `DESTINATIONS` registry.
"""

# ─── Environment variable contract ──────────────────────────────────────────

REQUIRED_ENV_VARS: tuple[str, ...] = (
    "CIANFHOGHLAIM_DUCKLAKE_POSTGRES",
    "CIANFHOGHLAIM_DUCKLAKE_S3",
)
"""The 2 environment variables that every destination factory reads
before constructing a destination. `validate_credentials(...)` asserts
these are present unless an explicit override is supplied.

The convention (per `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1`):
- `CIANFHOGHLAIM_DUCKLAKE_POSTGRES` — Postgres catalog URI
- `CIANFHOGHLAIM_DUCKLAKE_S3` — Garage S3 storage path
"""

OPTIONAL_ENV_VARS: tuple[str, ...] = (
    "CIANFHOGHLAIM_DUCKLAKE_BUCKET",
    "DUCKLAKE_POSTGRES_USER",
    "DUCKLAKE_POSTGRES_PASSWORD",
    "DUCKLAKE_BUCKET",
)
"""Optional env vars the destination factories may read for connection
authentication + S3 bucket selection. Missing values fall back to the
defaults declared in each per-layer module (`ducklake.py` /
`motherduck.py` / `filesystem.py` / `iceberg.py`).
"""


def validate_credentials(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    """Validate that every required DuckLake env var is set.

    Args:
        env: Optional explicit env mapping (defaults to `os.environ`).

    Returns:
        The merged env mapping (defaults applied for any unset
        `REQUIRED_ENV_VARS`).

    Raises:
        RuntimeError: If a required env var cannot be resolved either
        via the explicit `env=` argument, the process env, or the
        per-module default. The error message names every missing var.
    """
    src = dict(env) if env is not None else dict(os.environ)
    missing: list[str] = []
    for var in REQUIRED_ENV_VARS:
        if var not in src or not src[var]:
            missing.append(var)
    if missing:
        raise RuntimeError(
            f"validate_credentials: missing required DuckLake env vars: {missing}. "
            f"Set the listed vars (or supply explicit defaults via the per-layer "
            f"destination factory's env= argument) before constructing a destination."
        )
    return src


__all__ = [
    "DUCKLAKE_NAMESPACE",
    "QUADRANT_METADATA_SCHEMAS",
    "QUADRANT_TO_DUCKLAKE_KEY",
    "LEGACY_DUCKLAKE_NAMESPACE_ALIASES",
    "REQUIRED_ENV_VARS",
    "OPTIONAL_ENV_VARS",
    "validate_credentials",
]
