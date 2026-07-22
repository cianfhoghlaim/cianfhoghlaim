"""Re-export the North Macedonia Mathematics per-subject DLT source."""
from dlt_sources.european_nations.mkd.education.subjects.mathematics.mathematics import (
    MKDMathematicsSource,
    mkd_mathematics,
    mkd_mathematics_source,
)  # noqa: F401

__all__ = ["MKDMathematicsSource", "mkd_mathematics", "mkd_mathematics_source"]
