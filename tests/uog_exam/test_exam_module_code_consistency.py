"""Deterministic eval — exam module code consistency.

The thesis contract: every `UoGExamPaper` row emitted by the BAML
extractor must have a `module_code` matching the regex
`^[A-Z]{2,4}\d{3,4}$`.

This eval is run by CI as part of the marimo "Quality" tab + by a
Dagster asset_check inside the `uog_exam_papers_ocr_extract` asset.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

import pytest

MODULE_CODE_REGEX = re.compile(r"^[A-Z]{2,4}\d{3,4}$")


def test_module_code_regex_accepts_every_case_in_handles():
    """The regex accepts every well-known module-code prefix in the corpus."""
    good_codes = {"CT516", "MA335", "HI451", "ED305", "PS101", "BCT1234", "LW200", "EC301"}
    for code in good_codes:
        assert MODULE_CODE_REGEX.match(code) is not None, code


def test_module_code_regex_rejects_garbage():
    bad_codes = {"", "ct516", "CT51", "CTU123", "CT-516", "C516", "CT516A"}
    for code in bad_codes:
        assert MODULE_CODE_REGEX.match(code) is None, code


def test_eval_runs_against_a_fixture_list():
    """Given 20 well-formed rows, the eval returns 0 failures."""
    rows = [
        type("Row", (), {"module_code": f"CT{c:03d}", "programme_codes": ["MSCAI"]})
        for c in range(500, 520)
    ]
    failures = exam_module_code_consistency(rows)
    assert failures == []


def test_eval_flags_a_single_bad_module_code():
    rows = []
    for c in range(500, 520):
        rows.append(
            type(
                "Row",
                (),
                {"module_code": f"CT{c:03d}", "programme_codes": ["MSCAI"]},
            )
        )
    rows.append(
        type("Row", (), {"module_code": "CT51", "programme_codes": []})
    )  # too short
    failures = exam_module_code_consistency(rows)
    assert "CT51" in failures


# --------------------------------------------------------------------------- #
# The eval function (exported from the baml quality module in production)
# --------------------------------------------------------------------------- #


def exam_module_code_consistency(rows: Iterable) -> list[str]:
    """Return the list of `module_code` values that fail the canonical regex.

    Mirrors the deterministic eval in
    `openspec/changes/2026-08-23-uog-exam-papers-sso-v1/specs/
     cianfhoghlaim-uog-exam-papers/spec.md` (Scenario: BAML round-trip
    preserves the new fields).
    """
    failures: list[str] = []
    for row in rows:
        code = getattr(row, "module_code", None) or ""
        if not MODULE_CODE_REGEX.match(code):
            failures.append(str(code))
    return failures
