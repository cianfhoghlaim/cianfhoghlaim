"""Re-export the North Macedonia Biology per-subject DLT source."""
from cianfhoghlaim.dlt.european_nations.mkd.education.subjects.biology.biology import (
    MKDBiologySource,
    mkd_biology,
    mkd_biology_source,
)  # noqa: F401

__all__ = ["MKDBiologySource", "mkd_biology", "mkd_biology_source"]
