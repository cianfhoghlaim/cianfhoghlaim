"""cianfhoghlaim.dlt — DLT ingestion layer + cross-jurisdiction registry + common helpers.

Post-v7 flattening: this directory IS the canonical location of the
`cianchoghlaim.dlt` Python sub-module. Earlier layouts used a
`dlt/sources/` directory; the canonical entries now live as direct
siblings (`dlt/british_isles/`, `dlt/commonwealth/`, etc.).
"""
# Post-v7: import from the canonical sibling submodules directly.
from dlt_sources import common  # noqa: F401
from dlt_sources import british_isles  # noqa: F401

__all__ = ["common", "british_isles"]
__version__ = "0.4.0"