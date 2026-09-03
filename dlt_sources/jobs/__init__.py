"""`dlt.jobs` — thin sub-package of deployment-manifest `@run.pipeline` jobs.

See module docstring in `government_circulars_job.py` for why this
package exists (it sidesteps the eager-import chain in the legacy
`cianfhoghlaim.dlt.british_isles.ireland.education` package).
"""
from dlt_sources.jobs import government_circulars_job

__all__ = ["government_circulars_job"]
