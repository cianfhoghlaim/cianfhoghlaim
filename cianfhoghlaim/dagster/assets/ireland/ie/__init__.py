"""
oideachais.dagster_defs.assets.ie — domain-first Ireland asset sub-tree.

Phase 5 of the openspec change. Replaces the flat
`oideachais.dagster_defs.assets.ireland` address with the new
domain-first `oideachais.dagster_defs.assets.ie.education` package.
"""
from . import education

__all__ = ["education"]
