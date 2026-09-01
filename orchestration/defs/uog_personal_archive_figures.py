"""orchestration.defs.uog_personal_archive_figures — DEPRECATION SHIM.

This module has been moved to `orchestration.pipelines.education.tertiary.uog.personal_archive.figures` as part of
Wave 2 of the 2026-08-24 master refactor (per the canonical
`dagster-pipeline-components` spec).

It re-exports the original `__all__` from the new location for
backward compatibility with downstream consumers that haven't yet
migrated. New code SHOULD import from the canonical destination
path; this shim will be removed in a future release.

Reference: openspec/changes/2026-08-24-master-refactor-v1/specs/dagster-pipeline-components/spec.md
"""
from __future__ import annotations

import warnings

_ORIGINAL_MODULE = 'orchestration.defs.uog_personal_archive_figures'
_DESTINATION_MODULE = 'orchestration.pipelines.education.tertiary.uog.personal_archive.figures'

_DEPRECATION_MSG = (
    f"`{_ORIGINAL_MODULE}` is deprecated as of Wave 2 of the 2026-08-24 master refactor; "
    f"import from `{_DESTINATION_MODULE}` instead. The legacy module will be "
    "removed in a future release."
)
warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)

# Re-export every public symbol from the canonical destination module.
from orchestration.pipelines.education.tertiary.uog.personal_archive.figures import *  # noqa: E402, F401, F403

__all__ = ['FIGURES_DIR', 'uog_personal_archive_thesis_figures']
