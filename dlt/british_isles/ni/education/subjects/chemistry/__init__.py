"""Re-export the Northern Ireland chemistry per-subject DLT source."""
from cianfhoghlaim.dlt.british_isles.ni.education.subjects.chemistry import (
    ni_chemistry,
    ni_chemistry_source,
)  # noqa: F401

__all__ = ["ni_chemistry", "ni_chemistry_source"]
