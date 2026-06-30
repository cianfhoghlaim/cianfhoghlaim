"""
Backward-compat shim — the legacy scotland medicine @assets have moved to
dagster.assets.by_domain.medicine (per the v3 consolidation plan,
consolidate-cianfhoghlaim-subdirs Phase B.6).

This file is preserved for one release as a re-export shim. Update
your imports to use the canonical by_domain/ path.
"""
from cianfhoghlaim.dagster.assets.by_domain import (
    medicine_scotland_nhs_scotland,
)

__all__ = ['medicine_scotland_nhs_scotland']
