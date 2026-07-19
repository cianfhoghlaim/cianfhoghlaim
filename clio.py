"""Backward-compat shim — `clio.py` → `cli.py` re-export.

Deprecated: this file exists for one release cycle per the v7
flattening consolidation. Update any external scripts that import
from `cianchoghlaim.clio` to import from `cianchoghlaim.cli` instead.

See `openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1`
for the rename rationale.
"""

# Importing cli re-triggers the canonical source via Python's module
# caching; this shim just re-exports `main` for callers that still
# use the old name.
from cianfhoghlaim.cli import main as _main

# Re-bind so `from cianfhoghlaim.clio import main; main([...])` works
main = _main
__all__ = ["main"]


if __name__ == "__main__":
    import sys

    raise SystemExit(_main(sys.argv[1:]))
