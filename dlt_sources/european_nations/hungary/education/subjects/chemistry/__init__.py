"""Re-export the Hungary Chemistry per-subject DLT source."""
from dlt_sources.european_nations.hun.education.subjects.chemistry import (
    hun_chemistry,
    hun_chemistry_source,
)  # noqa: F401

__all__ = ["hun_chemistry", "hun_chemistry_source"]
