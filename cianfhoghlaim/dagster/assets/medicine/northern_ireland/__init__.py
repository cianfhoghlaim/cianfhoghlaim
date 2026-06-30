"""
Backward-compat shim — the legacy northern_ireland medicine @assets have moved to
dagster.assets.by_domain.medicine (per the v3 consolidation plan,
consolidate-cianfhoghlaim-subdirs Phase B.6).

This file is preserved for one release as a re-export shim. Update
your imports to use the canonical by_domain/ path.
"""
from cianfhoghlaim.dagster.assets.by_domain import (
    medicine_northern_ireland_nidirect,
)

__all__ = ['medicine_northern_ireland_nidirect']
