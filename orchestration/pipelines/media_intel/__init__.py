"""orchestration.pipelines.media_intel — the per-pipeline Component home (Wave 2).

This module is the canonical home for the per-pipeline Component
that was migrated from `orchestration.defs.media_intel` as part of the
Wave 2 master refactor. It re-exports the original module's
public symbols for backward compatibility; sister repos and
downstream consumers should import from this path going forward.

The corresponding `defs.yaml` file at this directory declares the
canonical `dagster_dlt.DltLoadCollectionComponent` + the Cianfhoghlaim
`translation:` defaults per the `dagster-pipeline-components` spec.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
import warnings

_legacy_mod_path = 'orchestration.defs.media_intel'
_legacy_backup_relpath = 'orchestration/defs/media_intel.legacy.bak'

# Load the original module from the legacy backup file via
# a manual `SourceFileLoader` (because the backup has a
# `.legacy.bak` extension that `spec_from_file_location`
# rejects). This avoids the circular-import problem with the
# live deprecation shim at
# `orchestration.defs.media_intel` (the shim points back to this module,
# so importing from the shim would deadlock).
_legacy_backup_path = None
_candidate = pathlib.Path(__file__).resolve().parent
while _candidate != _candidate.parent:
    _candidate_candidate = _candidate / _legacy_backup_relpath
    if _candidate_candidate.exists():
        _legacy_backup_path = _candidate_candidate
        break
    _candidate = _candidate.parent
if _legacy_backup_path is None:
    raise ImportError(f"Could not locate legacy backup {_legacy_backup_relpath}")
_loader = importlib.machinery.SourceFileLoader(
    'orchestration.defs.media_intel',
    str(_legacy_backup_path),
)
_spec = importlib.util.spec_from_loader(
    'orchestration.defs.media_intel',
    _loader,
)
if _spec is None:
    raise ImportError(f"Could not build module spec for {original_module_path}")
_legacy_mod = importlib.util.module_from_spec(_spec)
sys.modules[_legacy_mod_path] = _legacy_mod
_loader.exec_module(_legacy_mod)

# Re-export every public symbol from the loaded legacy module.
_REEXPORT_SYMBOLS = ['marvel_hickman_comics_l1', 'wheel_of_time_prose_l1', 'avatar_animation_l1', 'gameplay_capture_l1', 'ncca_sec_dfe_sqa_wjec_desc_l1', 'uk_government_l1', 'ie_government_l1', 'crown_dependencies_government_l1', 'uk_departments_l1', 'ie_departments_l1', 'sct_departments_l1', 'wls_departments_l1', 'ni_departments_l1', 'comic_descriptor_l2', 'prose_descriptor_l2', 'animation_descriptor_l2', 'gameplay_descriptor_l2', 'official_document_descriptor_l2', 'media_descriptors_embedding', 'cross_medium_compare_embedding', 'media_intel_explorer_per_medium_notebook', 'media_intel_explorer_cross_medium_notebook', 'media_descriptor_agent_run']
for _sym in _REEXPORT_SYMBOLS:
    globals()[_sym] = getattr(_legacy_mod, _sym)
    del _sym

# Emit the deprecation warning on import (one-time, not per-access).
_DEPRECATION_MSG = (
    f"`{_legacy_mod_path}` is deprecated as of Wave 2 of the master refactor; "
    f"import from `orchestration.pipelines.media_intel` instead. The legacy module will be "
    "removed in a future release."
)
warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)

__all__ = ['marvel_hickman_comics_l1', 'wheel_of_time_prose_l1', 'avatar_animation_l1', 'gameplay_capture_l1', 'ncca_sec_dfe_sqa_wjec_desc_l1', 'uk_government_l1', 'ie_government_l1', 'crown_dependencies_government_l1', 'uk_departments_l1', 'ie_departments_l1', 'sct_departments_l1', 'wls_departments_l1', 'ni_departments_l1', 'comic_descriptor_l2', 'prose_descriptor_l2', 'animation_descriptor_l2', 'gameplay_descriptor_l2', 'official_document_descriptor_l2', 'media_descriptors_embedding', 'cross_medium_compare_embedding', 'media_intel_explorer_per_medium_notebook', 'media_intel_explorer_cross_medium_notebook', 'media_descriptor_agent_run']
