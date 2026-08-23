"""Shared fixtures for the UoG exam-papers test suite."""

from __future__ import annotations

import hashlib
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pytest

# --------------------------------------------------------------------------- #
# Make `sruth_browser` importable in this repo's flat layout.
#
# `sruth_browser` lives at `bonneagar/stacks/browser/sruth_browser/`. At
# production runtime it is installed as a separate package (the
# sruth-browser Docker stack) and the Python interpreter is rooted at
# that stack's directory. In the standalone repo-test environment we
# only have the cianfhoghlaim repo root on `sys.path`, so we inject the
# path here at conftest import time. This is a no-op in production.
# --------------------------------------------------------------------------- #

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRUTH_BROWSER_ROOT = (
    _REPO_ROOT / "bonneagar" / "stacks" / "browser"
)
if (
    _SRUTH_BROWSER_ROOT.is_dir()
    and str(_SRUTH_BROWSER_ROOT) not in sys.path
):
    sys.path.insert(0, str(_SRUTH_BROWSER_ROOT))


# --------------------------------------------------------------------------- #
# Fixture-only OOG env (default behaviour for every test in this package).
# --------------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def _uog_fixture_only_env(monkeypatch):
    """Mark every test as fixture-mode by default.

    Tests that need real credentials can either:
      - set env vars in-test via `monkeypatch.setenv(...)`, OR
      - apply the `@pytest.mark.opt_in` marker and the runtime check
        in `tests/uog_exam/conftest.py::opt_in_only()` will guard them.
    """
    monkeypatch.setenv("OOG_STUDENT_ID", "fixture-only")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "fixture-only")
    # Make sure no Infisical env vars leak in from the host shell.
    for var in (
        "INFISICAL_TOKEN",
        "INFISICAL_URL",
        "INFISICAL_PROJECT",
        "INFISICAL_ENV",
        "OP_SERVICE_ACCOUNT_TOKEN",
    ):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def uog_fixture_modules() -> list[str]:
    """The 4 v1 fixture module codes."""
    return ["CT516", "CT511", "MA335", "ED305"]


@pytest.fixture
def uog_sample_exam_paper() -> dict[str, Any]:
    """One representative `UoGExamMaterial` for round-trip tests."""
    return {
        "module_code": "CT516",
        "module_title": "Deep Learning",
        "programme_codes": ["MSCAI"],
        "school_slug": "computer-science",
        "academic_year": 2023,
        "sitting": "AUTUMN",
        "material_type": "paper",
        "paper_format": "PDF_UPLOAD",
        "language": "en",
        "source_url": "https://exams.universityofgalway.ie/CT516/2023/AUT.pdf",
        "title": "CT516 — Deep Learning — Autumn 2023",
        "content_hash": hashlib.sha256(b"fixture-ct516-2023-aut").hexdigest()[:16],
        "downloaded_at": "2026-08-23T00:00:00Z",
        "bytes": 0,
    }


@pytest.fixture
def uog_fake_pdf(tmp_path: Path) -> Path:
    """Write a 1-byte PDF to a tmp path so file-existence tests pass."""
    target = tmp_path / "CT516_2023_autumn_paper.pdf"
    target.write_bytes(b"%PDF-1.4\n%fake for tests\n%%EOF\n")
    return target


# --------------------------------------------------------------------------- #
# `opt_in` marker — tests that touch real credentials
# --------------------------------------------------------------------------- #


def pytest_collection_modifyitems(config, items: Iterable[pytest.Item]) -> None:
    """Skip any opt-in test unless `OOG_RUN_OPT_IN=1`."""
    import os

    if os.environ.get("OOG_RUN_OPT_IN") == "1":
        return
    skip_opt_in = pytest.mark.skip(
        reason=(
            "Marked @pytest.mark.opt_in — set OOG_RUN_OPT_IN=1 to run with "
            "real credentials (requires OOG_STUDENT_ID + OOG_STUDENT_PASSWORD)."
        )
    )
    for item in items:
        if "opt_in" in item.keywords:
            item.add_marker(skip_opt_in)
