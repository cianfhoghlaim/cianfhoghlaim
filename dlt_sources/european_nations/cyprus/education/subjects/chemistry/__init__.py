"""Re-export the Cyprus Chemistry per-subject DLT source."""
from dlt_sources.european_nations.cyp.education.subjects.chemistry import (
    cyp_chemistry,
    cyp_chemistry_source,
)  # noqa: F401

__all__ = ["cyp_chemistry", "cyp_chemistry_source"]
