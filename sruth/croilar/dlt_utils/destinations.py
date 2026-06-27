"""croilar/dlt_utils/destinations.py — thin re-export shim from oideachais.

Phase 2.3 of the lateralise change: croilar no longer carries its
own DuckLake destination implementation. It re-exports the
oideachais canonical helpers with `namespace="croilar"` pre-bound.

The croilar packaging fix (commit `e9e0fc7d2`, "fix(croilar):
close issue #17 — packaging fix for the dagster code-location")
ensures `oideachais` is on the croilar venv's sys.path via
`sruth/croilar/scripts/fix-pth.sh` rewriting the broken
uv-generated .pth to contain `sruth/` (the parent of both
`croilar/` and `oideachais/`). The canonical import therefore
always succeeds.
"""
from sruth.oideachais.dlt_utils.destinations import with_namespace

with_namespace("croilar").re_export_into(globals())