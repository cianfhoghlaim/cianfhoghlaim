"""ResearchGate DLT pipeline.

Public surface:

    from pipelines.researchgate import (
        researchgate_profile_resource,
        run_researchgate_pipeline,
    )
"""

from .source import (
    researchgate_profile_resource,
    run_researchgate_pipeline,
)

__all__ = [
    "researchgate_profile_resource",
    "run_researchgate_pipeline",
]
