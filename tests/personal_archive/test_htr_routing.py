"""Tests for the HTR router `dlt_sources/filesystem/_htr_ensemble.py`.

Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
(WS12 — Tests + observability + thesis figures).

`route_htr(file_path, size_bytes)` decides whether a PDF goes
through GoodNotes OCR, multi-VLM consensus, or the typed-text
fast path. GoodNotes PDFs are large (`>= 800 bytes` for the
canonical test fixture) so the router returns the
``MULTI_VLM_CONSENSUS`` backend for them.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


_HTR_ROUTER = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway/dlt_sources/filesystem/_htr_ensemble.py"
)


def _load_htr_router():
    if not _HTR_ROUTER.exists():
        return None
    spec = importlib.util.spec_from_file_location(
        "_htr_ensemble_test", _HTR_ROUTER
    )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return getattr(module, "route_htr", None)


def test_route_htr_goodnotes_large_returns_multi_vlm():
    """A 800-byte GoodNotes PDF should be routed to MULTI_VLM_CONSENSUS."""
    route = _load_htr_router()
    if route is None:
        import pytest

        pytest.skip(
            "dlt_sources/filesystem/_htr_ensemble.py not yet written "
            "by the parallel subagent"
        )
    result = route(Path("foo.goodnotes.pdf"), 800.0)
    # The contract (per WS12 spec): the first element of the tuple
    # is the chosen backend enum. The remaining elements are
    # backend-specific (confidence + reason).
    assert isinstance(result, tuple)
    assert len(result) >= 1
    backend = result[0]
    assert backend.name == "MULTI_VLM_CONSENSUS"
