"""
destinations_cianfhoghlaim — re-export shim.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec change,
this file is now a re-export shim. The canonical home is
`dlt_sources.common.destinations.ducklake`.

Legacy imports continue to work, but new code SHOULD import from:

    from dlt_sources.common.destinations import named_destinations

This shim is preserved for at least one release cycle per the
dlt_sources LEGACY_ALIASES.md precedent.
"""
from __future__ import annotations

# Re-export from the layer-grouped destinations package.
from dlt_sources.common.destinations.ducklake import *  # noqa: F401,F403
from dlt_sources.common.destinations import named_destinations, DESTINATIONS  # noqa: F401

# === Original file content (preserved for archaeology) ===
# Original path: dlt_sources/common/destinations_cianfhoghlaim.py
# Original line count: 529
# Wave 4: replaced with re-export shim.
#
# The original implementation is preserved in git history at commit
# b8e7e18bd (before Wave 4) — use `git show b8e7e18bd:dlt_sources/common/destinations_cianfhoghlaim.py` to view.
