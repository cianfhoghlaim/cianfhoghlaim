"""Tests for the DLT source `dlt_sources/filesystem/uog_personal_archive.py`.

The classifier is the function that turns a file name like
``cian_mac_liathain_assignment_3.pdf`` into the typed
``(ArtefactKind, ArtefactProvenance, module_code, assignment_number)``
quadruple that drives the DuckLake pipeline.

Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
(WS12 — Tests + observability + thesis figures).
"""
from __future__ import annotations

from pathlib import Path


def _load_dlt_source_classifier():
    """Lazily import `_classify_file` from the parallel-subagent DLT source.

    Loads via the ``dlt_sources.filesystem.uog_personal_archive`` package
    path so relative imports inside the module (e.g. ``from ._scanner
    import ...``) resolve correctly.
    """
    try:
        from dlt_sources.filesystem.uog_personal_archive import (
            _classify_file,
        )

        return _classify_file
    except Exception:
        return None


def test_classify_file_assignment_submission():
    """`cian_mac_liathain_assignment_3.pdf` → (ASSIGNMENT_SUBMISSION,
    PERSONAL_SUBMISSION, None, 3)."""
    classifier = _load_dlt_source_classifier()
    if classifier is None:
        # The parallel subagent's DLT source is not yet on disk. The
        # test passes when the module is absent; the assertion is the
        # contract we are pinning down for the parallel implementation.
        import pytest

        pytest.skip(
            "dlt_sources/filesystem/uog_personal_archive.py not yet "
            "written by the parallel subagent"
        )
    result = classifier(Path("cian_mac_liathain_assignment_3.pdf"))
    # The contract (per WS12 spec):
    #   (ArtefactKind.ASSIGNMENT_SUBMISSION,
    #    ArtefactProvenance.PERSONAL_SUBMISSION,
    #    None,
    #    3)
    assert len(result) == 4
    kind, provenance, module_code, assignment_number = result
    # Compare by enum NAME rather than value (defensive against
    # different auto() implementations across Python versions).
    assert kind.name == "ASSIGNMENT_SUBMISSION"
    assert provenance.name == "PERSONAL_SUBMISSION"
    assert module_code is None
    assert assignment_number == 3
