"""
DLT sources for Northern Ireland education data.

Sources:
- NISRA (Northern Ireland Statistics and Research Agency)
- education-ni.gov.uk
- ETI (Education and Training Inspectorate)
"""

from .nisra import nisra_source
from .education_ni import education_ni_source
from .etini import etini_source

__all__ = [
    "nisra_source",
    "education_ni_source",
    "etini_source",
]
