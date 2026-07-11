"""Re-export the Wales chemistry per-subject DLT source."""
from cianfhoghlaim.dlt.british_isles.wls.education.subjects.chemistry import (
    wls_chemistry,
    wls_chemistry_source,
)  # noqa: F401

__all__ = ["wls_chemistry", "wls_chemistry_source"]
