"""cianfhoghlaim.dlt.cli — CLI entry-point (shim re-exporting cianfhoghlaim.dlt_sources.common.cli).

The earlier `clio.py`-at-root / `dlt/cli.py`-missing layout made
`python -m cianfhoghlaim.dlt.cli` raise `ModuleNotFoundError`. This file
restores the canonical entry-point by re-exporting from the
`dlt/common/cli.py` module (which is where the argparse + DLT_SOURCES
list actually live).
"""
from dlt_sources.common.cli import (
    DLT_SOURCES,
    main,
)

__all__ = ["DLT_SOURCES", "main"]


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
