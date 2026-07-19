"""cianfhoghlaim.dlt — DLT ingestion layer + cross-jurisdiction registry + common helpers.

Post-v7 flattening: this directory IS the canonical location of the
`cianfhoghlaim.dlt` Python sub-module. Earlier layouts used a
`dlt/sources/` directory; the canonical entries now live as direct
siblings (`dlt/british_isles/`, `dlt/commonwealth/`, etc.).
"""
# Post-v7: import from the canonical sibling submodules directly.
# The pre-v7 layout had `cianchoghlaim/dlt/__init__.py` re-exporting these,
# but the v7 flattening removed the cianchoghlaim/ subdirectory.
from dlt import common  # noqa: F401
from dlt import british_isles  # noqa: F401

__all__ = ["common", "british_isles"]
__version__ = "0.4.0"
