"""Re-export the Greece Chemistry per-subject DLT source."""
from dlt_sources.european_nations.grc.education.subjects.chemistry import (
    grc_chemistry,
    grc_chemistry_source,
)  # noqa: F401

__all__ = ["grc_chemistry", "grc_chemistry_source"]
