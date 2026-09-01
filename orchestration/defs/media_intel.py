"""orchestration.defs.media_intel — DEPRECATION SHIM.

This module has been moved to `orchestration.pipelines.media_intel` as part of
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

_ORIGINAL_MODULE = 'orchestration.defs.media_intel'
_DESTINATION_MODULE = 'orchestration.pipelines.media_intel'

_DEPRECATION_MSG = (
    f"`{_ORIGINAL_MODULE}` is deprecated as of Wave 2 of the 2026-08-24 master refactor; "
    f"import from `{_DESTINATION_MODULE}` instead. The legacy module will be "
    "removed in a future release."
)
warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)

# Re-export every public symbol from the canonical destination module.
from orchestration.pipelines.media_intel import *  # noqa: E402, F401, F403

__all__ = ['marvel_hickman_comics_l1', 'wheel_of_time_prose_l1', 'avatar_animation_l1', 'gameplay_capture_l1', 'ncca_sec_dfe_sqa_wjec_desc_l1', 'uk_government_l1', 'ie_government_l1', 'crown_dependencies_government_l1', 'uk_departments_l1', 'ie_departments_l1', 'sct_departments_l1', 'wls_departments_l1', 'ni_departments_l1', 'comic_descriptor_l2', 'prose_descriptor_l2', 'animation_descriptor_l2', 'gameplay_descriptor_l2', 'official_document_descriptor_l2', 'media_descriptors_embedding', 'cross_medium_compare_embedding', 'media_intel_explorer_per_medium_notebook', 'media_intel_explorer_cross_medium_notebook', 'media_descriptor_agent_run']
