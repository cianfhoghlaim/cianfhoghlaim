"""
Backward-compat shim — the legacy northern_ireland law @asset has moved to
dagster.assets.by_domain.law.law_northern_ireland_legislation (per the v3 consolidation
plan, consolidate-cianfhoghlaim-subdirs Phase B.6).

This file is preserved for one release as a re-export shim. Update
your imports to use the canonical by_domain/ path.
"""
from cianfhoghlaim.dagster.assets.by_domain import law_northern_ireland_legislation

__all__ = ["law_northern_ireland_legislation"]
